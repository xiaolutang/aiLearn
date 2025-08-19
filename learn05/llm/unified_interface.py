#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一LLM接口模块
提供标准化的大模型接口定义和响应格式
"""

import asyncio
import time
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, AsyncIterator, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """LLM提供商枚举"""
    TONGYI = "tongyi"
    OPENAI = "openai"
    CLAUDE = "claude"
    LOCAL = "local"


class LLMErrorType(Enum):
    """LLM错误类型枚举"""
    NETWORK_ERROR = "network_error"
    AUTH_ERROR = "auth_error"
    RATE_LIMIT = "rate_limit"
    QUOTA_EXCEEDED = "quota_exceeded"
    MODEL_ERROR = "model_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class LLMUsage:
    """LLM使用量统计"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def to_dict(self) -> Dict[str, int]:
        return asdict(self)


@dataclass
class LLMResponse:
    """统一的LLM响应格式"""
    content: str
    model: str
    provider: LLMProvider
    usage: LLMUsage
    latency: float
    success: bool
    request_id: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[LLMErrorType] = None
    metadata: Optional[Dict[str, Any]] = None
    cached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['provider'] = self.provider.value if self.provider else None
        result['error_type'] = self.error_type.value if self.error_type else None
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMResponse':
        if 'provider' in data and data['provider']:
            data['provider'] = LLMProvider(data['provider'])
        if 'error_type' in data and data['error_type']:
            data['error_type'] = LLMErrorType(data['error_type'])
        if 'usage' in data and isinstance(data['usage'], dict):
            data['usage'] = LLMUsage(**data['usage'])
        return cls(**data)


@dataclass
class LLMRequest:
    """LLM请求数据结构"""
    prompt: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[Union[str, List[str]]] = None
    stream: bool = False
    metadata: Optional[Dict[str, Any]] = None
    
    def get_cache_key(self) -> str:
        """生成缓存键"""
        cache_data = {
            'prompt': self.prompt,
            'messages': self.messages,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'stop': self.stop
        }
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(cache_str.encode('utf-8')).hexdigest()


class LLMException(Exception):
    """LLM异常基类"""
    
    def __init__(self, message: str, error_type: LLMErrorType = LLMErrorType.UNKNOWN, 
                 provider: Optional[LLMProvider] = None, model: Optional[str] = None):
        super().__init__(message)
        self.error_type = error_type
        self.provider = provider
        self.model = model
        self.timestamp = time.time()


class LLMNetworkException(LLMException):
    """网络异常"""
    def __init__(self, message: str, provider: Optional[LLMProvider] = None):
        super().__init__(message, LLMErrorType.NETWORK_ERROR, provider)


class LLMAuthenticationException(LLMException):
    """认证异常"""
    def __init__(self, message: str, provider: Optional[LLMProvider] = None):
        super().__init__(message, LLMErrorType.AUTH_ERROR, provider)


class LLMRateLimitException(LLMException):
    """速率限制异常"""
    def __init__(self, message: str, provider: Optional[LLMProvider] = None, 
                 retry_after: Optional[int] = None):
        super().__init__(message, LLMErrorType.RATE_LIMIT, provider)
        self.retry_after = retry_after


class LLMQuotaExceededException(LLMException):
    """配额超限异常"""
    def __init__(self, message: str, provider: Optional[LLMProvider] = None):
        super().__init__(message, LLMErrorType.QUOTA_EXCEEDED, provider)


class LLMModelException(LLMException):
    """模型异常"""
    def __init__(self, message: str, provider: Optional[LLMProvider] = None, 
                 model: Optional[str] = None):
        super().__init__(message, LLMErrorType.MODEL_ERROR, provider, model)


class LLMTimeoutException(LLMException):
    """超时异常"""
    def __init__(self, message: str, provider: Optional[LLMProvider] = None):
        super().__init__(message, LLMErrorType.TIMEOUT, provider)


class LLMServiceUnavailableException(LLMException):
    """服务不可用异常"""
    def __init__(self, message: str, provider: Optional[LLMProvider] = None):
        super().__init__(message, LLMErrorType.UNKNOWN, provider)


class LLMValidationException(LLMException):
    """验证错误异常"""
    def __init__(self, message: str, provider: Optional[LLMProvider] = None):
        super().__init__(message, LLMErrorType.UNKNOWN, provider)


class UnifiedLLMInterface(ABC):
    """统一的LLM接口抽象类"""
    
    def __init__(self, provider: LLMProvider, config: Optional[Dict[str, Any]] = None):
        self.provider = provider
        self.config = config or {}
        self.default_model = self.config.get('default_model', '')
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """生成文本响应"""
        pass
    
    @abstractmethod
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """进行对话"""
        pass
    
    @abstractmethod
    async def stream_generate(self, request: LLMRequest) -> AsyncIterator[str]:
        """流式生成文本"""
        pass
    
    @abstractmethod
    async def stream_chat(self, request: LLMRequest) -> AsyncIterator[str]:
        """流式对话"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass
    
    def get_provider(self) -> LLMProvider:
        """获取提供商"""
        return self.provider
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config.copy()
    
    def update_config(self, config: Dict[str, Any]):
        """更新配置"""
        self.config.update(config)
        
    def _create_error_response(self, request: LLMRequest, error: Exception, 
                              latency: float = 0.0) -> LLMResponse:
        """创建错误响应"""
        error_type = LLMErrorType.UNKNOWN
        if isinstance(error, LLMException):
            error_type = error.error_type
        
        return LLMResponse(
            content="",
            model=request.model or self.default_model,
            provider=self.provider,
            usage=LLMUsage(),
            latency=latency,
            success=False,
            error=str(error),
            error_type=error_type
        )
    
    def _create_success_response(self, content: str, model: str, usage: LLMUsage,
                               latency: float, request_id: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None,
                               cached: bool = False) -> LLMResponse:
        """创建成功响应"""
        return LLMResponse(
            content=content,
            model=model,
            provider=self.provider,
            usage=usage,
            latency=latency,
            success=True,
            request_id=request_id,
            metadata=metadata,
            cached=cached
        )


class LLMMetrics:
    """LLM指标收集器"""
    
    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency = 0.0
        self.total_tokens = 0
        self.error_types = {}
        self.provider_stats = {}
        
    def record_request(self, response: LLMResponse):
        """记录请求指标"""
        self.request_count += 1
        self.total_latency += response.latency
        self.total_tokens += response.usage.total_tokens
        
        provider_name = response.provider.value
        if provider_name not in self.provider_stats:
            self.provider_stats[provider_name] = {
                'requests': 0, 'successes': 0, 'errors': 0, 
                'latency': 0.0, 'tokens': 0
            }
        
        stats = self.provider_stats[provider_name]
        stats['requests'] += 1
        stats['latency'] += response.latency
        stats['tokens'] += response.usage.total_tokens
        
        if response.success:
            self.success_count += 1
            stats['successes'] += 1
        else:
            self.error_count += 1
            stats['errors'] += 1
            
            if response.error_type:
                error_type = response.error_type.value
                self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        avg_latency = self.total_latency / self.request_count if self.request_count > 0 else 0
        success_rate = self.success_count / self.request_count if self.request_count > 0 else 0
        
        return {
            'total_requests': self.request_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': success_rate,
            'average_latency': avg_latency,
            'total_tokens': self.total_tokens,
            'error_types': self.error_types,
            'provider_stats': self.provider_stats
        }
    
    def reset(self):
        """重置统计信息"""
        self.__init__()


# 全局指标收集器
global_metrics = LLMMetrics()