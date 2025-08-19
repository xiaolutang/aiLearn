#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一LLM客户端管理器
提供缓存、重试、降级等高级功能
"""

import asyncio
import json
import time
import random
from typing import Dict, List, Optional, Any, AsyncIterator, Callable
from dataclasses import asdict
import logging
from contextlib import asynccontextmanager

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from unified_interface import (
    UnifiedLLMInterface, LLMRequest, LLMResponse, LLMProvider,
    LLMException, LLMRateLimitException, LLMNetworkException, LLMTimeoutException,
    global_metrics
)

logger = logging.getLogger(__name__)


class LLMCache:
    """LLM缓存管理器"""
    
    def __init__(self, redis_client=None, ttl: int = 3600, enabled: bool = True):
        self.redis_client = redis_client
        self.ttl = ttl
        self.enabled = enabled
        self.memory_cache = {}  # 内存缓存作为备选
        self.max_memory_cache_size = 1000
        
    async def get_cached_response(self, cache_key: str) -> Optional[LLMResponse]:
        """获取缓存的响应"""
        if not self.enabled:
            return None
            
        try:
            # 优先使用Redis缓存
            if self.redis_client:
                cached_data = await self.redis_client.get(f"llm_cache:{cache_key}")
                if cached_data:
                    data = json.loads(cached_data)
                    response = LLMResponse.from_dict(data)
                    response.cached = True
                    return response
            
            # 备选内存缓存
            if cache_key in self.memory_cache:
                cache_item = self.memory_cache[cache_key]
                if time.time() - cache_item['timestamp'] < self.ttl:
                    response = LLMResponse.from_dict(cache_item['data'])
                    response.cached = True
                    return response
                else:
                    del self.memory_cache[cache_key]
                    
        except Exception as e:
            logger.warning(f"缓存获取失败: {e}")
            
        return None
    
    async def cache_response(self, cache_key: str, response: LLMResponse):
        """缓存响应"""
        if not self.enabled or not response.success:
            return
            
        try:
            response_data = response.to_dict()
            
            # 使用Redis缓存
            if self.redis_client:
                await self.redis_client.setex(
                    f"llm_cache:{cache_key}",
                    self.ttl,
                    json.dumps(response_data, ensure_ascii=False)
                )
            
            # 内存缓存
            if len(self.memory_cache) >= self.max_memory_cache_size:
                # 删除最旧的缓存项
                oldest_key = min(self.memory_cache.keys(), 
                               key=lambda k: self.memory_cache[k]['timestamp'])
                del self.memory_cache[oldest_key]
            
            self.memory_cache[cache_key] = {
                'data': response_data,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.warning(f"缓存存储失败: {e}")
    
    async def clear_cache(self, pattern: str = "*"):
        """清理缓存"""
        try:
            if self.redis_client:
                keys = await self.redis_client.keys(f"llm_cache:{pattern}")
                if keys:
                    await self.redis_client.delete(*keys)
            
            if pattern == "*":
                self.memory_cache.clear()
            else:
                # 简单的模式匹配
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    
        except Exception as e:
            logger.warning(f"缓存清理失败: {e}")


class RetryManager:
    """重试管理器"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """执行带重试的函数"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # 判断是否应该重试
                if not self._should_retry(e, attempt):
                    break
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(f"第{attempt + 1}次尝试失败，{delay}秒后重试: {e}")
                    await asyncio.sleep(delay)
        
        # 所有重试都失败了
        raise last_exception
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False
        
        # 网络错误和超时错误可以重试
        if isinstance(exception, (LLMNetworkException, LLMTimeoutException)):
            return True
        
        # 速率限制错误可以重试
        if isinstance(exception, LLMRateLimitException):
            return True
        
        # 其他LLM异常不重试
        if isinstance(exception, LLMException):
            return False
        
        # 其他异常可以重试
        return True
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间（指数退避 + 随机抖动）"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        # 添加随机抖动（±25%）
        jitter = delay * 0.25 * (2 * random.random() - 1)
        delay += jitter
        
        return max(0, delay)


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过熔断器调用函数"""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise Exception("熔断器开启，服务不可用")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'


class FallbackManager:
    """降级管理器"""
    
    def __init__(self, fallback_providers: List[LLMProvider] = None,
                 fallback_models: Dict[LLMProvider, List[str]] = None):
        self.fallback_providers = fallback_providers or []
        self.fallback_models = fallback_models or {}
        
    def get_fallback_options(self, original_provider: LLMProvider, 
                           original_model: str) -> List[tuple]:
        """获取降级选项"""
        options = []
        
        # 同提供商的其他模型
        if original_provider in self.fallback_models:
            for model in self.fallback_models[original_provider]:
                if model != original_model:
                    options.append((original_provider, model))
        
        # 其他提供商
        for provider in self.fallback_providers:
            if provider != original_provider:
                if provider in self.fallback_models:
                    for model in self.fallback_models[provider]:
                        options.append((provider, model))
                else:
                    options.append((provider, None))  # 使用默认模型
        
        return options


class UnifiedLLMClient:
    """统一LLM客户端管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.clients: Dict[LLMProvider, UnifiedLLMInterface] = {}
        self.cache = LLMCache(
            ttl=self.config.get('cache_ttl', 3600),
            enabled=self.config.get('cache_enabled', True)
        )
        self.retry_manager = RetryManager(
            max_retries=self.config.get('max_retries', 3)
        )
        self.circuit_breakers: Dict[LLMProvider, CircuitBreaker] = {}
        self.fallback_manager = FallbackManager(
            fallback_providers=self.config.get('fallback_providers', []),
            fallback_models=self.config.get('fallback_models', {})
        )
        self.default_provider = LLMProvider(self.config.get('default_provider', 'tongyi'))
        
        # 并发控制
        self.semaphore = asyncio.Semaphore(self.config.get('max_concurrent_requests', 10))
        
    def register_client(self, provider: LLMProvider, client: UnifiedLLMInterface):
        """注册LLM客户端"""
        self.clients[provider] = client
        self.circuit_breakers[provider] = CircuitBreaker(
            failure_threshold=self.config.get('circuit_breaker_threshold', 5),
            recovery_timeout=self.config.get('circuit_breaker_timeout', 60)
        )
        logger.info(f"注册LLM客户端: {provider.value}")
    
    def get_client(self, provider: Optional[LLMProvider] = None) -> UnifiedLLMInterface:
        """获取LLM客户端"""
        provider = provider or self.default_provider
        if provider not in self.clients:
            raise ValueError(f"未注册的LLM提供商: {provider.value}")
        return self.clients[provider]
    
    @asynccontextmanager
    async def _acquire_semaphore(self):
        """获取信号量"""
        await self.semaphore.acquire()
        try:
            yield
        finally:
            self.semaphore.release()
    
    async def generate(self, request: LLMRequest, 
                      provider: Optional[LLMProvider] = None) -> LLMResponse:
        """生成文本响应"""
        async with self._acquire_semaphore():
            return await self._execute_with_fallback('generate', request, provider)
    
    async def chat(self, request: LLMRequest,
                  provider: Optional[LLMProvider] = None) -> LLMResponse:
        """进行对话"""
        async with self._acquire_semaphore():
            return await self._execute_with_fallback('chat', request, provider)
    
    async def stream_generate(self, request: LLMRequest,
                            provider: Optional[LLMProvider] = None) -> AsyncIterator[str]:
        """流式生成文本"""
        async with self._acquire_semaphore():
            client = self.get_client(provider)
            async for chunk in client.stream_generate(request):
                yield chunk
    
    async def stream_chat(self, request: LLMRequest,
                        provider: Optional[LLMProvider] = None) -> AsyncIterator[str]:
        """流式对话"""
        async with self._acquire_semaphore():
            client = self.get_client(provider)
            async for chunk in client.stream_chat(request):
                yield chunk
    
    async def _execute_with_fallback(self, method: str, request: LLMRequest,
                                   provider: Optional[LLMProvider] = None) -> LLMResponse:
        """执行带降级的请求"""
        provider = provider or self.default_provider
        original_model = request.model
        
        # 检查缓存
        if method in ['generate', 'chat']:
            cache_key = request.get_cache_key()
            cached_response = await self.cache.get_cached_response(cache_key)
            if cached_response:
                global_metrics.record_request(cached_response)
                return cached_response
        
        # 尝试主要选项
        try:
            response = await self._execute_single_request(method, request, provider)
            
            # 缓存成功的响应
            if response.success and method in ['generate', 'chat']:
                await self.cache.cache_response(cache_key, response)
            
            global_metrics.record_request(response)
            return response
            
        except Exception as e:
            logger.warning(f"主要请求失败: {e}")
            
            # 尝试降级选项
            fallback_options = self.fallback_manager.get_fallback_options(provider, original_model)
            
            for fallback_provider, fallback_model in fallback_options:
                try:
                    fallback_request = LLMRequest(**asdict(request))
                    if fallback_model:
                        fallback_request.model = fallback_model
                    
                    response = await self._execute_single_request(
                        method, fallback_request, fallback_provider
                    )
                    
                    if response.success:
                        logger.info(f"降级成功: {fallback_provider.value}/{fallback_model}")
                        global_metrics.record_request(response)
                        return response
                        
                except Exception as fallback_error:
                    logger.warning(f"降级失败 {fallback_provider.value}: {fallback_error}")
                    continue
            
            # 所有选项都失败了
            error_response = LLMResponse(
                content="",
                model=original_model or "",
                provider=provider,
                usage=LLMUsage(),
                latency=0.0,
                success=False,
                error=f"所有LLM选项都失败: {str(e)}"
            )
            global_metrics.record_request(error_response)
            return error_response
    
    async def _execute_single_request(self, method: str, request: LLMRequest,
                                    provider: LLMProvider) -> LLMResponse:
        """执行单个请求"""
        client = self.get_client(provider)
        circuit_breaker = self.circuit_breakers[provider]
        
        async def _call_method():
            if method == 'generate':
                return await client.generate(request)
            elif method == 'chat':
                return await client.chat(request)
            else:
                raise ValueError(f"不支持的方法: {method}")
        
        # 通过熔断器和重试管理器执行
        return await circuit_breaker.call(
            self.retry_manager.execute_with_retry,
            _call_method
        )
    
    async def health_check(self) -> Dict[LLMProvider, bool]:
        """健康检查"""
        results = {}
        for provider, client in self.clients.items():
            try:
                results[provider] = await client.health_check()
            except Exception as e:
                logger.error(f"健康检查失败 {provider.value}: {e}")
                results[provider] = False
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return global_metrics.get_stats()
    
    def reset_metrics(self):
        """重置指标"""
        global_metrics.reset()
    
    async def clear_cache(self, pattern: str = "*"):
        """清理缓存"""
        await self.cache.clear_cache(pattern)