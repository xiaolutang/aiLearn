#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM工厂类 - 统一管理和创建LLM客户端
"""

import os
import logging
from typing import Dict, Any, Optional, Type
from enum import Enum

from unified_interface import UnifiedLLMInterface, LLMProvider
from providers import OpenAILLMClient, TongyiLLMClient
from unified_client import UnifiedLLMClient

# 兼容旧接口
try:
    from service.llm.base import LLMInterface
    from service.llm_integration import llm_router
except ImportError:
    LLMInterface = None
    llm_router = None

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM工厂类"""
    
    # 注册的LLM客户端类
    _clients: Dict[LLMProvider, Type[UnifiedLLMInterface]] = {
        LLMProvider.OPENAI: OpenAILLMClient,
        LLMProvider.TONGYI: TongyiLLMClient,
    }
    
    def __init__(self):
        """初始化LLM工厂"""
        self._default_provider = LLMProvider.TONGYI
        self._client_cache = {}
    
    # 默认配置
    _default_configs = {
        LLMProvider.OPENAI: {
            'timeout': 30,
            'max_retries': 3,
            'requests_per_minute': 60,
            'tokens_per_minute': 90000,
        },
        LLMProvider.TONGYI: {
            'timeout': 30,
            'max_retries': 3,
            'requests_per_minute': 60,
            'tokens_per_minute': 150000,
        }
    }
    
    @classmethod
    def create_client(cls, provider: LLMProvider, 
                     config: Optional[Dict[str, Any]] = None) -> UnifiedLLMInterface:
        """创建LLM客户端
        
        Args:
            provider: LLM提供商
            config: 配置参数
            
        Returns:
            LLM客户端实例
            
        Raises:
            ValueError: 不支持的提供商
        """
        if provider not in cls._clients:
            raise ValueError(f"不支持的LLM提供商: {provider}")
        
        # 合并默认配置
        final_config = cls._default_configs.get(provider, {}).copy()
        if config:
            final_config.update(config)
        
        client_class = cls._clients[provider]
        
        try:
            return client_class(final_config)
        except Exception as e:
            logger.error(f"创建{provider.value}客户端失败: {e}")
            raise
    
    @classmethod
    def create_unified_client(cls, 
                            primary_provider: LLMProvider,
                            fallback_providers: Optional[list] = None,
                            config: Optional[Dict[str, Any]] = None) -> UnifiedLLMClient:
        """创建统一LLM客户端（支持降级）
        
        Args:
            primary_provider: 主要提供商
            fallback_providers: 降级提供商列表
            config: 配置参数
            
        Returns:
            统一LLM客户端实例
        """
        # 创建主要客户端
        primary_client = cls.create_client(primary_provider, config)
        
        # 创建降级客户端
        fallback_clients = []
        if fallback_providers:
            for provider in fallback_providers:
                try:
                    fallback_client = cls.create_client(provider, config)
                    fallback_clients.append(fallback_client)
                except Exception as e:
                    logger.warning(f"创建降级客户端{provider.value}失败: {e}")
        
        return UnifiedLLMClient(
            primary_client=primary_client,
            fallback_clients=fallback_clients,
            config=config or {}
        )
    
    def get_client(self, provider: Optional[LLMProvider] = None, 
                   config: Optional[Dict[str, Any]] = None) -> UnifiedLLMInterface:
        """获取LLM客户端实例
        
        Args:
            provider: LLM提供商，默认使用TONGYI
            config: 配置参数
            
        Returns:
            LLM客户端实例
        """
        if provider is None:
            provider = self._default_provider
        
        # 使用缓存避免重复创建
        cache_key = f"{provider.value}_{hash(str(config))}"
        if cache_key in self._client_cache:
            return self._client_cache[cache_key]
        
        client = self.create_client(provider, config)
        self._client_cache[cache_key] = client
        return client
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的提供商列表"""
        return list(cls._clients.keys())
    
    @classmethod
    def register_client(cls, provider: LLMProvider, 
                       client_class: Type[UnifiedLLMInterface]):
        """注册新的LLM客户端
        
        Args:
            provider: LLM提供商
            client_class: 客户端类
        """
        cls._clients[provider] = client_class
        logger.info(f"注册LLM客户端: {provider.value}")
    
    @classmethod
    def set_default_config(cls, provider: LLMProvider, config: Dict[str, Any]):
        """设置默认配置
        
        Args:
            provider: LLM提供商
            config: 配置参数
        """
        cls._default_configs[provider] = config
        logger.info(f"设置{provider.value}默认配置")


def get_llm_client(provider: str = None, config: Dict[str, Any] = None) -> UnifiedLLMInterface:
    """获取LLM客户端的便捷函数
    
    Args:
        provider: 提供商名称（openai, tongyi等）
        config: 配置参数
        
    Returns:
        LLM客户端实例
    """
    # 兼容旧接口
    if provider is None and llm_router is not None:
        logger.warning("使用旧的LLM路由器，建议升级到新的统一接口")
        return llm_router
    
    # 从环境变量或配置中获取默认提供商
    if not provider:
        provider = os.environ.get('DEFAULT_LLM_PROVIDER', 'tongyi')
    
    # 转换为枚举
    provider_map = {
        'openai': LLMProvider.OPENAI,
        'tongyi': LLMProvider.TONGYI,
        'qianwen': LLMProvider.TONGYI,  # 别名
    }
    
    provider_enum = provider_map.get(provider.lower())
    if not provider_enum:
        raise ValueError(f"不支持的提供商: {provider}")
    
    return LLMFactory.create_client(provider_enum, config)


def get_unified_llm_client(config: Dict[str, Any] = None) -> UnifiedLLMClient:
    """获取统一LLM客户端的便捷函数
    
    Args:
        config: 配置参数
        
    Returns:
        统一LLM客户端实例
    """
    # 默认配置：通义千问为主，OpenAI为备用
    primary_provider = LLMProvider.TONGYI
    fallback_providers = [LLMProvider.OPENAI]
    
    # 从配置中读取提供商设置
    if config:
        primary = config.get('primary_provider')
        if primary:
            provider_map = {
                'openai': LLMProvider.OPENAI,
                'tongyi': LLMProvider.TONGYI,
            }
            primary_provider = provider_map.get(primary.lower(), primary_provider)
        
        fallbacks = config.get('fallback_providers', [])
        if fallbacks:
            fallback_providers = []
            for fb in fallbacks:
                provider_map = {
                    'openai': LLMProvider.OPENAI,
                    'tongyi': LLMProvider.TONGYI,
                }
                fb_provider = provider_map.get(fb.lower())
                if fb_provider:
                    fallback_providers.append(fb_provider)
    
    return LLMFactory.create_unified_client(
        primary_provider=primary_provider,
        fallback_providers=fallback_providers,
        config=config
    )


# 全局客户端实例（单例模式）
_global_client = None


def get_global_llm_client() -> UnifiedLLMClient:
    """获取全局LLM客户端实例
    
    Returns:
        全局LLM客户端实例
    """
    global _global_client
    
    if _global_client is None:
        # 从环境变量读取配置
        config = {
            'cache_enabled': os.environ.get('LLM_CACHE_ENABLED', 'true').lower() == 'true',
            'cache_ttl': int(os.environ.get('LLM_CACHE_TTL', '3600')),
            'max_retries': int(os.environ.get('LLM_MAX_RETRIES', '3')),
            'circuit_breaker_enabled': os.environ.get('LLM_CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true',
            'primary_provider': os.environ.get('PRIMARY_LLM_PROVIDER', 'tongyi'),
            'fallback_providers': os.environ.get('FALLBACK_LLM_PROVIDERS', 'openai').split(',')
        }
        
        _global_client = get_unified_llm_client(config)
        logger.info("初始化全局LLM客户端")
    
    return _global_client


def reset_global_client():
    """重置全局客户端（用于测试）"""
    global _global_client
    _global_client = None