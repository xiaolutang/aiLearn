# -*- coding: utf-8 -*-
"""
AI服务管理模块

本模块实现了多AI提供商的统一接入、降级处理和缓存机制。
"""

import asyncio
import json
import hashlib
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union
import aiohttp
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """AI提供商枚举"""
    OPENAI = "openai"
    CLAUDE = "claude"
    WENXIN = "wenxin"
    QIANFAN = "qianfan"
    ZHIPU = "zhipu"

@dataclass
class AIRequest:
    """AI请求数据类"""
    provider: AIProvider
    model: str
    messages: List[Dict[str, str]]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    system_prompt: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AIResponse:
    """AI响应数据类"""
    success: bool
    content: str
    provider: AIProvider
    model: str
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None
    response_time: Optional[float] = None
    cached: bool = False
    metadata: Optional[Dict[str, Any]] = None

class AIServiceInterface(ABC):
    """AI服务接口"""
    
    @abstractmethod
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        """聊天完成接口"""
        pass
    
    @abstractmethod
    async def image_analysis(self, image_url: str, prompt: str) -> AIResponse:
        """图像分析接口"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass

class OpenAIService(AIServiceInterface):
    """OpenAI服务实现"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        self.models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    async def _get_session(self):
        """获取HTTP会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        """OpenAI聊天完成"""
        start_time = datetime.now()
        
        try:
            session = await self._get_session()
            
            # 构建请求数据
            payload = {
                "model": request.model,
                "messages": request.messages,
                "temperature": request.temperature,
                "stream": request.stream
            }
            
            if request.max_tokens:
                payload["max_tokens"] = request.max_tokens
            
            if request.system_prompt:
                payload["messages"].insert(0, {
                    "role": "system",
                    "content": request.system_prompt
                })
            
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    return AIResponse(
                        success=True,
                        content=data["choices"][0]["message"]["content"],
                        provider=AIProvider.OPENAI,
                        model=request.model,
                        usage=data.get("usage"),
                        response_time=response_time
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error: {response.status} - {error_text}")
                    return AIResponse(
                        success=False,
                        content="",
                        provider=AIProvider.OPENAI,
                        model=request.model,
                        error=f"API error: {response.status}"
                    )
        
        except Exception as e:
            logger.error(f"OpenAI service error: {str(e)}")
            return AIResponse(
                success=False,
                content="",
                provider=AIProvider.OPENAI,
                model=request.model,
                error=str(e)
            )
    
    async def image_analysis(self, image_url: str, prompt: str) -> AIResponse:
        """OpenAI图像分析"""
        try:
            session = await self._get_session()
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return AIResponse(
                        success=True,
                        content=data["choices"][0]["message"]["content"],
                        provider=AIProvider.OPENAI,
                        model="gpt-4-vision-preview"
                    )
                else:
                    return AIResponse(
                        success=False,
                        content="",
                        provider=AIProvider.OPENAI,
                        model="gpt-4-vision-preview",
                        error=f"API error: {response.status}"
                    )
        
        except Exception as e:
            return AIResponse(
                success=False,
                content="",
                provider=AIProvider.OPENAI,
                model="gpt-4-vision-preview",
                error=str(e)
            )
    
    def get_available_models(self) -> List[str]:
        """获取可用模型"""
        return self.models
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/models") as response:
                return response.status == 200
        except:
            return False
    
    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()

class ClaudeService(AIServiceInterface):
    """Claude服务实现（模拟）"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.models = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        """Claude聊天完成（模拟实现）"""
        # 这里应该实现真实的Claude API调用
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        return AIResponse(
            success=True,
            content="这是Claude的模拟响应",
            provider=AIProvider.CLAUDE,
            model=request.model,
            response_time=0.1
        )
    
    async def image_analysis(self, image_url: str, prompt: str) -> AIResponse:
        """Claude图像分析（模拟实现）"""
        await asyncio.sleep(0.1)
        
        return AIResponse(
            success=True,
            content="这是Claude的图像分析模拟响应",
            provider=AIProvider.CLAUDE,
            model="claude-3-opus"
        )
    
    def get_available_models(self) -> List[str]:
        return self.models
    
    async def health_check(self) -> bool:
        return True

class AIServiceManager:
    """AI服务管理器"""
    
    def __init__(self, cache_manager=None):
        self.services: Dict[AIProvider, AIServiceInterface] = {}
        self.fallback_order = [AIProvider.OPENAI, AIProvider.CLAUDE]
        self.cache_manager = cache_manager
        self.request_stats = {}
        self.circuit_breaker = {}
    
    def register_service(self, provider: AIProvider, service: AIServiceInterface):
        """注册AI服务"""
        self.services[provider] = service
        self.circuit_breaker[provider] = {
            "failures": 0,
            "last_failure": None,
            "is_open": False
        }
        logger.info(f"Registered AI service: {provider.value}")
    
    def _generate_cache_key(self, request: AIRequest) -> str:
        """生成缓存键"""
        content = json.dumps({
            "provider": request.provider.value,
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "system_prompt": request.system_prompt
        }, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _get_cached_response(self, cache_key: str) -> Optional[AIResponse]:
        """获取缓存响应"""
        if not self.cache_manager:
            return None
        
        try:
            cached_data = await self.cache_manager.get_ai_cache(cache_key)
            if cached_data:
                cached_data.cached = True
                return cached_data
        except Exception as e:
            logger.warning(f"Cache get error: {str(e)}")
        
        return None
    
    async def _set_cached_response(self, cache_key: str, response: AIResponse):
        """设置缓存响应"""
        if not self.cache_manager or not response.success:
            return
        
        try:
            await self.cache_manager.set_ai_cache(cache_key, response, ttl=3600)
        except Exception as e:
            logger.warning(f"Cache set error: {str(e)}")
    
    def _is_circuit_open(self, provider: AIProvider) -> bool:
        """检查熔断器状态"""
        breaker = self.circuit_breaker.get(provider)
        if not breaker or not breaker["is_open"]:
            return False
        
        # 检查是否应该重置熔断器
        if breaker["last_failure"]:
            time_since_failure = datetime.now() - breaker["last_failure"]
            if time_since_failure > timedelta(minutes=5):  # 5分钟后重试
                breaker["is_open"] = False
                breaker["failures"] = 0
                return False
        
        return True
    
    def _record_failure(self, provider: AIProvider):
        """记录失败"""
        breaker = self.circuit_breaker.get(provider)
        if breaker:
            breaker["failures"] += 1
            breaker["last_failure"] = datetime.now()
            
            # 连续失败3次后开启熔断器
            if breaker["failures"] >= 3:
                breaker["is_open"] = True
                logger.warning(f"Circuit breaker opened for {provider.value}")
    
    def _record_success(self, provider: AIProvider):
        """记录成功"""
        breaker = self.circuit_breaker.get(provider)
        if breaker:
            breaker["failures"] = 0
            breaker["is_open"] = False
    
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        """聊天完成（单一提供商）"""
        # 检查缓存
        cache_key = self._generate_cache_key(request)
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # 检查熔断器
        if self._is_circuit_open(request.provider):
            return AIResponse(
                success=False,
                content="",
                provider=request.provider,
                model=request.model,
                error="Service temporarily unavailable (circuit breaker open)"
            )
        
        # 调用服务
        service = self.services.get(request.provider)
        if not service:
            return AIResponse(
                success=False,
                content="",
                provider=request.provider,
                model=request.model,
                error=f"Service not available: {request.provider.value}"
            )
        
        try:
            response = await service.chat_completion(request)
            
            if response.success:
                self._record_success(request.provider)
                await self._set_cached_response(cache_key, response)
            else:
                self._record_failure(request.provider)
            
            return response
        
        except Exception as e:
            self._record_failure(request.provider)
            logger.error(f"AI service error: {str(e)}")
            return AIResponse(
                success=False,
                content="",
                provider=request.provider,
                model=request.model,
                error=str(e)
            )
    
    async def chat_completion_with_fallback(self, request: AIRequest) -> AIResponse:
        """带降级的聊天完成"""
        # 首先尝试指定的提供商
        response = await self.chat_completion(request)
        if response.success:
            return response
        
        # 如果失败，尝试降级到其他提供商
        for fallback_provider in self.fallback_order:
            if fallback_provider == request.provider:
                continue
            
            if fallback_provider not in self.services:
                continue
            
            if self._is_circuit_open(fallback_provider):
                continue
            
            logger.info(f"Falling back to {fallback_provider.value}")
            
            fallback_request = AIRequest(
                provider=fallback_provider,
                model=self.services[fallback_provider].get_available_models()[0],
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system_prompt=request.system_prompt,
                user_id=request.user_id,
                session_id=request.session_id
            )
            
            fallback_response = await self.chat_completion(fallback_request)
            if fallback_response.success:
                return fallback_response
        
        # 所有提供商都失败
        return AIResponse(
            success=False,
            content="",
            provider=request.provider,
            model=request.model,
            error="All AI services are currently unavailable"
        )
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {}
        
        for provider, service in self.services.items():
            try:
                health = await service.health_check()
                breaker = self.circuit_breaker.get(provider, {})
                
                status[provider.value] = {
                    "healthy": health,
                    "circuit_open": breaker.get("is_open", False),
                    "failures": breaker.get("failures", 0),
                    "models": service.get_available_models()
                }
            except Exception as e:
                status[provider.value] = {
                    "healthy": False,
                    "error": str(e)
                }
        
        return status
    
    async def close_all(self):
        """关闭所有服务"""
        for service in self.services.values():
            if hasattr(service, 'close'):
                await service.close()