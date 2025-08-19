#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM配置管理模块
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """LLM提供商配置"""
    name: str
    api_key: str
    base_url: str = ""
    default_model: str = ""
    timeout: int = 30
    max_retries: int = 3
    requests_per_minute: int = 60
    tokens_per_minute: int = 90000
    enabled: bool = True
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    cache_type: str = "memory"  # memory, redis
    ttl: int = 3600  # 缓存过期时间（秒）
    max_size: int = 1000  # 内存缓存最大条目数
    redis_url: str = "redis://localhost:6379/0"
    key_prefix: str = "llm_cache:"


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0  # 基础延迟（秒）
    max_delay: float = 60.0  # 最大延迟（秒）
    exponential_base: float = 2.0  # 指数退避基数
    jitter: bool = True  # 是否添加随机抖动
    retry_on_timeout: bool = True
    retry_on_rate_limit: bool = True
    retry_on_server_error: bool = True


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    enabled: bool = True
    failure_threshold: int = 5  # 失败阈值
    recovery_timeout: int = 60  # 恢复超时（秒）
    expected_exception: tuple = ()  # 预期异常类型


@dataclass
class MonitoringConfig:
    """监控配置"""
    enabled: bool = True
    metrics_enabled: bool = True
    logging_enabled: bool = True
    log_level: str = "INFO"
    metrics_export_interval: int = 60  # 指标导出间隔（秒）
    slow_request_threshold: float = 5.0  # 慢请求阈值（秒）


@dataclass
class LLMConfig:
    """LLM总配置"""
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    primary_provider: str = "tongyi"
    fallback_providers: List[str] = field(default_factory=lambda: ["openai"])
    cache: CacheConfig = field(default_factory=CacheConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    concurrent_requests: int = 10  # 并发请求数限制
    request_timeout: int = 30  # 请求超时（秒）


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.environ.get('LLM_CONFIG_FILE')
        self._config: Optional[LLMConfig] = None
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        # 首先从文件加载
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self._config = self._parse_config(config_data)
                logger.info(f"从文件加载配置: {self.config_file}")
                return
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
        
        # 从环境变量加载
        self._config = self._load_from_env()
        logger.info("从环境变量加载配置")
    
    def _parse_config(self, config_data: Dict[str, Any]) -> LLMConfig:
        """解析配置数据"""
        # 解析提供商配置
        providers = {}
        for name, provider_data in config_data.get('providers', {}).items():
            providers[name] = ProviderConfig(
                name=name,
                api_key=provider_data.get('api_key', ''),
                base_url=provider_data.get('base_url', ''),
                default_model=provider_data.get('default_model', ''),
                timeout=provider_data.get('timeout', 30),
                max_retries=provider_data.get('max_retries', 3),
                requests_per_minute=provider_data.get('requests_per_minute', 60),
                tokens_per_minute=provider_data.get('tokens_per_minute', 90000),
                enabled=provider_data.get('enabled', True),
                extra_params=provider_data.get('extra_params', {})
            )
        
        # 解析缓存配置
        cache_data = config_data.get('cache', {})
        cache_config = CacheConfig(
            enabled=cache_data.get('enabled', True),
            cache_type=cache_data.get('cache_type', 'memory'),
            ttl=cache_data.get('ttl', 3600),
            max_size=cache_data.get('max_size', 1000),
            redis_url=cache_data.get('redis_url', 'redis://localhost:6379/0'),
            key_prefix=cache_data.get('key_prefix', 'llm_cache:')
        )
        
        # 解析重试配置
        retry_data = config_data.get('retry', {})
        retry_config = RetryConfig(
            max_retries=retry_data.get('max_retries', 3),
            base_delay=retry_data.get('base_delay', 1.0),
            max_delay=retry_data.get('max_delay', 60.0),
            exponential_base=retry_data.get('exponential_base', 2.0),
            jitter=retry_data.get('jitter', True),
            retry_on_timeout=retry_data.get('retry_on_timeout', True),
            retry_on_rate_limit=retry_data.get('retry_on_rate_limit', True),
            retry_on_server_error=retry_data.get('retry_on_server_error', True)
        )
        
        # 解析熔断器配置
        cb_data = config_data.get('circuit_breaker', {})
        circuit_breaker_config = CircuitBreakerConfig(
            enabled=cb_data.get('enabled', True),
            failure_threshold=cb_data.get('failure_threshold', 5),
            recovery_timeout=cb_data.get('recovery_timeout', 60)
        )
        
        # 解析监控配置
        monitoring_data = config_data.get('monitoring', {})
        monitoring_config = MonitoringConfig(
            enabled=monitoring_data.get('enabled', True),
            metrics_enabled=monitoring_data.get('metrics_enabled', True),
            logging_enabled=monitoring_data.get('logging_enabled', True),
            log_level=monitoring_data.get('log_level', 'INFO'),
            metrics_export_interval=monitoring_data.get('metrics_export_interval', 60),
            slow_request_threshold=monitoring_data.get('slow_request_threshold', 5.0)
        )
        
        return LLMConfig(
            providers=providers,
            primary_provider=config_data.get('primary_provider', 'tongyi'),
            fallback_providers=config_data.get('fallback_providers', ['openai']),
            cache=cache_config,
            retry=retry_config,
            circuit_breaker=circuit_breaker_config,
            monitoring=monitoring_config,
            concurrent_requests=config_data.get('concurrent_requests', 10),
            request_timeout=config_data.get('request_timeout', 30)
        )
    
    def _load_from_env(self) -> LLMConfig:
        """从环境变量加载配置"""
        # 提供商配置
        providers = {}
        
        # OpenAI配置
        if os.environ.get('OPENAI_API_KEY'):
            providers['openai'] = ProviderConfig(
                name='openai',
                api_key=os.environ.get('OPENAI_API_KEY'),
                base_url=os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
                default_model=os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                timeout=int(os.environ.get('OPENAI_TIMEOUT', '30')),
                max_retries=int(os.environ.get('OPENAI_MAX_RETRIES', '3')),
                requests_per_minute=int(os.environ.get('OPENAI_REQUESTS_PER_MINUTE', '60')),
                tokens_per_minute=int(os.environ.get('OPENAI_TOKENS_PER_MINUTE', '90000')),
                enabled=os.environ.get('OPENAI_ENABLED', 'true').lower() == 'true'
            )
        
        # 通义千问配置
        if os.environ.get('TONGYI_API_KEY'):
            providers['tongyi'] = ProviderConfig(
                name='tongyi',
                api_key=os.environ.get('TONGYI_API_KEY'),
                base_url=os.environ.get('TONGYI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
                default_model=os.environ.get('TONGYI_MODEL', 'qwen-plus'),
                timeout=int(os.environ.get('TONGYI_TIMEOUT', '30')),
                max_retries=int(os.environ.get('TONGYI_MAX_RETRIES', '3')),
                requests_per_minute=int(os.environ.get('TONGYI_REQUESTS_PER_MINUTE', '60')),
                tokens_per_minute=int(os.environ.get('TONGYI_TOKENS_PER_MINUTE', '150000')),
                enabled=os.environ.get('TONGYI_ENABLED', 'true').lower() == 'true'
            )
        
        # 缓存配置
        cache_config = CacheConfig(
            enabled=os.environ.get('LLM_CACHE_ENABLED', 'true').lower() == 'true',
            cache_type=os.environ.get('LLM_CACHE_TYPE', 'memory'),
            ttl=int(os.environ.get('LLM_CACHE_TTL', '3600')),
            max_size=int(os.environ.get('LLM_CACHE_MAX_SIZE', '1000')),
            redis_url=os.environ.get('LLM_CACHE_REDIS_URL', 'redis://localhost:6379/0'),
            key_prefix=os.environ.get('LLM_CACHE_KEY_PREFIX', 'llm_cache:')
        )
        
        # 重试配置
        retry_config = RetryConfig(
            max_retries=int(os.environ.get('LLM_MAX_RETRIES', '3')),
            base_delay=float(os.environ.get('LLM_RETRY_BASE_DELAY', '1.0')),
            max_delay=float(os.environ.get('LLM_RETRY_MAX_DELAY', '60.0')),
            exponential_base=float(os.environ.get('LLM_RETRY_EXPONENTIAL_BASE', '2.0')),
            jitter=os.environ.get('LLM_RETRY_JITTER', 'true').lower() == 'true'
        )
        
        # 熔断器配置
        circuit_breaker_config = CircuitBreakerConfig(
            enabled=os.environ.get('LLM_CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true',
            failure_threshold=int(os.environ.get('LLM_CIRCUIT_BREAKER_FAILURE_THRESHOLD', '5')),
            recovery_timeout=int(os.environ.get('LLM_CIRCUIT_BREAKER_RECOVERY_TIMEOUT', '60'))
        )
        
        # 监控配置
        monitoring_config = MonitoringConfig(
            enabled=os.environ.get('LLM_MONITORING_ENABLED', 'true').lower() == 'true',
            metrics_enabled=os.environ.get('LLM_METRICS_ENABLED', 'true').lower() == 'true',
            logging_enabled=os.environ.get('LLM_LOGGING_ENABLED', 'true').lower() == 'true',
            log_level=os.environ.get('LLM_LOG_LEVEL', 'INFO'),
            metrics_export_interval=int(os.environ.get('LLM_METRICS_EXPORT_INTERVAL', '60')),
            slow_request_threshold=float(os.environ.get('LLM_SLOW_REQUEST_THRESHOLD', '5.0'))
        )
        
        # 主配置
        primary_provider = os.environ.get('PRIMARY_LLM_PROVIDER', 'tongyi')
        fallback_providers = os.environ.get('FALLBACK_LLM_PROVIDERS', 'openai').split(',')
        
        return LLMConfig(
            providers=providers,
            primary_provider=primary_provider,
            fallback_providers=[p.strip() for p in fallback_providers if p.strip()],
            cache=cache_config,
            retry=retry_config,
            circuit_breaker=circuit_breaker_config,
            monitoring=monitoring_config,
            concurrent_requests=int(os.environ.get('LLM_CONCURRENT_REQUESTS', '10')),
            request_timeout=int(os.environ.get('LLM_REQUEST_TIMEOUT', '30'))
        )
    
    def get_config(self) -> LLMConfig:
        """获取配置"""
        if self._config is None:
            self._load_config()
        return self._config
    
    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """获取提供商配置"""
        config = self.get_config()
        return config.providers.get(provider_name)
    
    def reload_config(self):
        """重新加载配置"""
        self._config = None
        self._load_config()
        logger.info("配置已重新加载")
    
    def save_config(self, config_file: Optional[str] = None):
        """保存配置到文件"""
        if not self._config:
            return
        
        file_path = config_file or self.config_file
        if not file_path:
            raise ValueError("未指定配置文件路径")
        
        # 转换为字典
        config_dict = {
            'providers': {
                name: {
                    'api_key': provider.api_key,
                    'base_url': provider.base_url,
                    'default_model': provider.default_model,
                    'timeout': provider.timeout,
                    'max_retries': provider.max_retries,
                    'requests_per_minute': provider.requests_per_minute,
                    'tokens_per_minute': provider.tokens_per_minute,
                    'enabled': provider.enabled,
                    'extra_params': provider.extra_params
                }
                for name, provider in self._config.providers.items()
            },
            'primary_provider': self._config.primary_provider,
            'fallback_providers': self._config.fallback_providers,
            'cache': {
                'enabled': self._config.cache.enabled,
                'cache_type': self._config.cache.cache_type,
                'ttl': self._config.cache.ttl,
                'max_size': self._config.cache.max_size,
                'redis_url': self._config.cache.redis_url,
                'key_prefix': self._config.cache.key_prefix
            },
            'retry': {
                'max_retries': self._config.retry.max_retries,
                'base_delay': self._config.retry.base_delay,
                'max_delay': self._config.retry.max_delay,
                'exponential_base': self._config.retry.exponential_base,
                'jitter': self._config.retry.jitter,
                'retry_on_timeout': self._config.retry.retry_on_timeout,
                'retry_on_rate_limit': self._config.retry.retry_on_rate_limit,
                'retry_on_server_error': self._config.retry.retry_on_server_error
            },
            'circuit_breaker': {
                'enabled': self._config.circuit_breaker.enabled,
                'failure_threshold': self._config.circuit_breaker.failure_threshold,
                'recovery_timeout': self._config.circuit_breaker.recovery_timeout
            },
            'monitoring': {
                'enabled': self._config.monitoring.enabled,
                'metrics_enabled': self._config.monitoring.metrics_enabled,
                'logging_enabled': self._config.monitoring.logging_enabled,
                'log_level': self._config.monitoring.log_level,
                'metrics_export_interval': self._config.monitoring.metrics_export_interval,
                'slow_request_threshold': self._config.monitoring.slow_request_threshold
            },
            'concurrent_requests': self._config.concurrent_requests,
            'request_timeout': self._config.request_timeout
        }
        
        # 保存到文件
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已保存到: {file_path}")


# 全局配置管理器实例
_config_manager = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_llm_config() -> LLMConfig:
    """获取LLM配置"""
    return get_config_manager().get_config()


def get_provider_config(provider_name: str) -> Optional[ProviderConfig]:
    """获取提供商配置"""
    return get_config_manager().get_provider_config(provider_name)