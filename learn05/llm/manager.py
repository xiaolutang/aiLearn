#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM管理器 - 统一的LLM服务管理接口
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator, Union
from contextlib import asynccontextmanager

from .unified_interface import (
    LLMProvider, LLMRequest, LLMResponse, 
    LLMException, LLMRateLimitException,
    LLMQuotaExceededException, LLMServiceUnavailableException
)
from .unified_client import UnifiedLLMClient
from .factory import LLMFactory
from .config import get_llm_config
from .monitoring import get_performance_monitor, record_llm_request

logger = logging.getLogger(__name__)


class LLMManager:
    """LLM管理器 - 提供统一的LLM服务管理"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_llm_config()
        self.factory = LLMFactory()
        self.monitor = get_performance_monitor()
        
        # 客户端缓存
        self._clients: Dict[str, UnifiedLLMClient] = {}
        
        # 检查是否为测试模式（传入了自定义配置）
        self._test_mode = config is not None
        
        # 初始化默认客户端（测试模式下跳过）
        if not self._test_mode:
            self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化客户端"""
        try:
            # 创建统一客户端（支持降级）
            self._unified_client = self.factory.create_unified_client(
                primary_provider=LLMProvider.TONGYI,
                fallback_providers=[LLMProvider.OPENAI]
            )
            
            # 创建单独的客户端
            for provider in [LLMProvider.TONGYI, LLMProvider.OPENAI]:
                try:
                    client = self.factory.create_client(provider)
                    self._clients[provider.value] = client
                    logger.info(f"初始化{provider.value}客户端成功")
                except Exception as e:
                    logger.warning(f"初始化{provider.value}客户端失败: {e}")
            
            logger.info("LLM管理器初始化完成")
            
        except Exception as e:
            logger.error(f"LLM管理器初始化失败: {e}")
            raise
    
    async def generate(self, 
                      prompt: str,
                      model: Optional[str] = None,
                      provider: Optional[LLMProvider] = None,
                      **kwargs) -> LLMResponse:
        """生成文本
        
        Args:
            prompt: 输入提示词
            model: 模型名称
            provider: 指定提供商，如果不指定则使用统一客户端（支持降级）
            **kwargs: 其他参数
        
        Returns:
            LLMResponse: 生成结果
        """
        start_time = time.time()
        request_id = kwargs.get('request_id', f"req_{int(time.time() * 1000)}")
        
        try:
            # 构建请求
            request = LLMRequest(
                prompt=prompt,
                model=model or self.config.default_model,
                **kwargs
            )
            
            # 选择客户端
            if provider:
                client = self._get_client(provider)
                actual_provider = provider
            else:
                client = self._unified_client
                actual_provider = LLMProvider.TONGYI  # 默认主提供商
            
            # 调用生成
            response = await client.generate(request)
            
            # 记录指标
            latency = time.time() - start_time
            record_llm_request(
                provider=actual_provider,
                model=request.model,
                response=response,
                latency=latency,
                request_id=request_id
            )
            
            return response
            
        except Exception as e:
            # 记录失败指标
            latency = time.time() - start_time
            error_response = LLMResponse(
                success=False,
                content="",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            record_llm_request(
                provider=actual_provider if 'actual_provider' in locals() else LLMProvider.TONGYI,
                model=model or self.config.default_model,
                response=error_response,
                latency=latency,
                request_id=request_id
            )
            
            logger.error(f"生成文本失败 (request_id: {request_id}): {e}")
            raise
    
    async def chat(self,
                  messages: List[Dict[str, str]],
                  model: Optional[str] = None,
                  provider: Optional[LLMProvider] = None,
                  **kwargs) -> LLMResponse:
        """对话生成
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            provider: 指定提供商
            **kwargs: 其他参数
        
        Returns:
            LLMResponse: 生成结果
        """
        start_time = time.time()
        request_id = kwargs.get('request_id', f"chat_{int(time.time() * 1000)}")
        
        try:
            # 构建请求
            request = LLMRequest(
                messages=messages,
                model=model or self.config.default_model,
                **kwargs
            )
            
            # 选择客户端
            if provider:
                client = self._get_client(provider)
                actual_provider = provider
            else:
                client = self._unified_client
                actual_provider = LLMProvider.TONGYI
            
            # 调用对话
            response = await client.chat(request)
            
            # 记录指标
            latency = time.time() - start_time
            record_llm_request(
                provider=actual_provider,
                model=request.model,
                response=response,
                latency=latency,
                request_id=request_id
            )
            
            return response
            
        except Exception as e:
            # 记录失败指标
            latency = time.time() - start_time
            error_response = LLMResponse(
                success=False,
                content="",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            record_llm_request(
                provider=actual_provider if 'actual_provider' in locals() else LLMProvider.TONGYI,
                model=model or self.config.default_model,
                response=error_response,
                latency=latency,
                request_id=request_id
            )
            
            logger.error(f"对话生成失败 (request_id: {request_id}): {e}")
            raise
    
    async def stream_generate(self,
                             prompt: str,
                             model: Optional[str] = None,
                             provider: Optional[LLMProvider] = None,
                             **kwargs) -> AsyncGenerator[str, None]:
        """流式生成文本
        
        Args:
            prompt: 输入提示词
            model: 模型名称
            provider: 指定提供商
            **kwargs: 其他参数
        
        Yields:
            str: 生成的文本片段
        """
        start_time = time.time()
        request_id = kwargs.get('request_id', f"stream_{int(time.time() * 1000)}")
        
        try:
            # 构建请求
            request = LLMRequest(
                prompt=prompt,
                model=model or self.config.default_model,
                stream=True,
                **kwargs
            )
            
            # 选择客户端
            if provider:
                client = self._get_client(provider)
                actual_provider = provider
            else:
                client = self._unified_client
                actual_provider = LLMProvider.TONGYI
            
            # 流式生成
            full_content = ""
            async for chunk in client.stream_generate(request):
                full_content += chunk
                yield chunk
            
            # 记录成功指标
            latency = time.time() - start_time
            success_response = LLMResponse(
                success=True,
                content=full_content
            )
            
            record_llm_request(
                provider=actual_provider,
                model=request.model,
                response=success_response,
                latency=latency,
                request_id=request_id
            )
            
        except Exception as e:
            # 记录失败指标
            latency = time.time() - start_time
            error_response = LLMResponse(
                success=False,
                content="",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            record_llm_request(
                provider=actual_provider if 'actual_provider' in locals() else LLMProvider.TONGYI,
                model=model or self.config.default_model,
                response=error_response,
                latency=latency,
                request_id=request_id
            )
            
            logger.error(f"流式生成失败 (request_id: {request_id}): {e}")
            raise
    
    async def stream_chat(self,
                         messages: List[Dict[str, str]],
                         model: Optional[str] = None,
                         provider: Optional[LLMProvider] = None,
                         **kwargs) -> AsyncGenerator[str, None]:
        """流式对话生成
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            provider: 指定提供商
            **kwargs: 其他参数
        
        Yields:
            str: 生成的文本片段
        """
        start_time = time.time()
        request_id = kwargs.get('request_id', f"stream_chat_{int(time.time() * 1000)}")
        
        try:
            # 构建请求
            request = LLMRequest(
                messages=messages,
                model=model or self.config.default_model,
                stream=True,
                **kwargs
            )
            
            # 选择客户端
            if provider:
                client = self._get_client(provider)
                actual_provider = provider
            else:
                client = self._unified_client
                actual_provider = LLMProvider.TONGYI
            
            # 流式对话
            full_content = ""
            async for chunk in client.stream_chat(request):
                full_content += chunk
                yield chunk
            
            # 记录成功指标
            latency = time.time() - start_time
            success_response = LLMResponse(
                success=True,
                content=full_content
            )
            
            record_llm_request(
                provider=actual_provider,
                model=request.model,
                response=success_response,
                latency=latency,
                request_id=request_id
            )
            
        except Exception as e:
            # 记录失败指标
            latency = time.time() - start_time
            error_response = LLMResponse(
                success=False,
                content="",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            record_llm_request(
                provider=actual_provider if 'actual_provider' in locals() else LLMProvider.TONGYI,
                model=model or self.config.default_model,
                response=error_response,
                latency=latency,
                request_id=request_id
            )
            
            logger.error(f"流式对话失败 (request_id: {request_id}): {e}")
            raise
    
    def _get_client(self, provider: LLMProvider) -> UnifiedLLMClient:
        """获取指定提供商的客户端"""
        client = self._clients.get(provider.value)
        if not client:
            raise LLMServiceUnavailableException(f"提供商 {provider.value} 不可用")
        return client
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = self.monitor.get_health_status()
        
        # 检查各个提供商的健康状态
        provider_health = {}
        for provider_name, client in self._clients.items():
            try:
                is_healthy = await client.health_check()
                provider_health[provider_name] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'available': True
                }
            except Exception as e:
                provider_health[provider_name] = {
                    'status': 'error',
                    'available': False,
                    'error': str(e)
                }
        
        return {
            'overall_health': health_status,
            'provider_health': provider_health,
            'timestamp': time.time()
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return self.monitor.get_performance_report()
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        return list(self._clients.keys())
    
    def get_available_models(self, provider: Optional[LLMProvider] = None) -> Dict[str, List[str]]:
        """获取可用的模型列表"""
        if provider:
            # 返回指定提供商的模型
            provider_config = self.config.providers.get(provider.value, {})
            return {provider.value: provider_config.get('available_models', [])}
        else:
            # 返回所有提供商的模型
            models = {}
            for provider_name, config in self.config.providers.items():
                models[provider_name] = config.get('available_models', [])
            return models
    
    async def close(self):
        """关闭管理器"""
        try:
            # 关闭所有客户端
            for client in self._clients.values():
                if hasattr(client, 'close'):
                    await client.close()
            
            if hasattr(self._unified_client, 'close'):
                await self._unified_client.close()
            
            logger.info("LLM管理器已关闭")
            
        except Exception as e:
            logger.error(f"关闭LLM管理器时出错: {e}")
    
    @asynccontextmanager
    async def session(self):
        """会话上下文管理器"""
        try:
            yield self
        finally:
            # 可以在这里添加会话清理逻辑
            pass


# 全局管理器实例
_global_manager = None


def get_llm_manager() -> LLMManager:
    """获取全局LLM管理器"""
    global _global_manager
    if _global_manager is None:
        _global_manager = LLMManager()
    return _global_manager


async def generate_text(prompt: str, 
                       model: Optional[str] = None,
                       provider: Optional[LLMProvider] = None,
                       **kwargs) -> LLMResponse:
    """生成文本（便捷函数）"""
    manager = get_llm_manager()
    return await manager.generate(prompt, model, provider, **kwargs)


async def chat_completion(messages: List[Dict[str, str]],
                         model: Optional[str] = None,
                         provider: Optional[LLMProvider] = None,
                         **kwargs) -> LLMResponse:
    """对话完成（便捷函数）"""
    manager = get_llm_manager()
    return await manager.chat(messages, model, provider, **kwargs)


async def stream_text(prompt: str,
                     model: Optional[str] = None,
                     provider: Optional[LLMProvider] = None,
                     **kwargs) -> AsyncGenerator[str, None]:
    """流式生成文本（便捷函数）"""
    manager = get_llm_manager()
    async for chunk in manager.stream_generate(prompt, model, provider, **kwargs):
        yield chunk


async def stream_chat_completion(messages: List[Dict[str, str]],
                                model: Optional[str] = None,
                                provider: Optional[LLMProvider] = None,
                                **kwargs) -> AsyncGenerator[str, None]:
    """流式对话完成（便捷函数）"""
    manager = get_llm_manager()
    async for chunk in manager.stream_chat(messages, model, provider, **kwargs):
        yield chunk