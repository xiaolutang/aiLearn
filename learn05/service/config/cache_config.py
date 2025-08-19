# -*- coding: utf-8 -*-
"""
缓存配置和管理

本模块提供Redis缓存配置、缓存策略和性能优化功能。
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """缓存类型枚举"""
    MEMORY = "memory"
    REDIS = "redis"
    HYBRID = "hybrid"  # 内存+Redis混合缓存


class CacheStrategy(Enum):
    """缓存策略枚举"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    TTL = "ttl"  # 基于时间过期
    WRITE_THROUGH = "write_through"  # 写穿透
    WRITE_BACK = "write_back"  # 写回


@dataclass
class CacheConfig:
    """缓存配置类"""
    
    # 基础配置
    enabled: bool = True
    cache_type: CacheType = CacheType.REDIS
    strategy: CacheStrategy = CacheStrategy.LRU
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    redis_ssl_cert_reqs: str = "required"
    
    # 连接池配置
    redis_max_connections: int = 50
    redis_connection_timeout: int = 5
    redis_socket_timeout: int = 5
    redis_socket_keepalive: bool = True
    redis_socket_keepalive_options: Dict[str, int] = None
    
    # 缓存策略配置
    default_ttl: int = 3600  # 默认1小时过期
    max_memory_size: int = 1000  # 内存缓存最大条目数
    key_prefix: str = "ai_tutor:"
    
    # 性能配置
    enable_compression: bool = True
    compression_threshold: int = 1024  # 超过1KB启用压缩
    enable_serialization: bool = True
    serialization_format: str = "pickle"  # pickle, json, msgpack
    
    # 集群配置
    enable_cluster: bool = False
    cluster_nodes: list = None
    cluster_skip_full_coverage_check: bool = False
    
    # 监控配置
    enable_metrics: bool = True
    metrics_prefix: str = "cache_"
    
    def __post_init__(self):
        """初始化后处理"""
        if self.socket_keepalive_options is None:
            self.socket_keepalive_options = {}
        
        if self.cluster_nodes is None:
            self.cluster_nodes = []
        
        # 从环境变量读取配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        self.enabled = os.getenv("CACHE_ENABLED", str(self.enabled)).lower() == "true"
        
        cache_type_str = os.getenv("CACHE_TYPE", self.cache_type.value)
        try:
            self.cache_type = CacheType(cache_type_str)
        except ValueError:
            logger.warning(f"无效的缓存类型: {cache_type_str}, 使用默认值: {self.cache_type.value}")
        
        self.redis_url = os.getenv("REDIS_URL", self.redis_url)
        self.redis_host = os.getenv("REDIS_HOST", self.redis_host)
        self.redis_port = int(os.getenv("REDIS_PORT", str(self.redis_port)))
        self.redis_db = int(os.getenv("REDIS_DB", str(self.redis_db)))
        self.redis_password = os.getenv("REDIS_PASSWORD", self.redis_password)
        
        self.default_ttl = int(os.getenv("CACHE_DEFAULT_TTL", str(self.default_ttl)))
        self.max_memory_size = int(os.getenv("CACHE_MAX_MEMORY_SIZE", str(self.max_memory_size)))
        self.key_prefix = os.getenv("CACHE_KEY_PREFIX", self.key_prefix)
        
        self.enable_compression = os.getenv("CACHE_COMPRESSION", str(self.enable_compression)).lower() == "true"
        self.compression_threshold = int(os.getenv("CACHE_COMPRESSION_THRESHOLD", str(self.compression_threshold)))


class PerformanceConfig:
    """性能优化配置类"""
    
    def __init__(self):
        # API性能配置
        self.enable_async = True
        self.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        # 数据库性能配置
        self.db_pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.db_max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.db_pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.db_pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        self.db_pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
        
        # 查询优化配置
        self.enable_query_cache = os.getenv("ENABLE_QUERY_CACHE", "true").lower() == "true"
        self.query_cache_ttl = int(os.getenv("QUERY_CACHE_TTL", "300"))  # 5分钟
        self.max_page_size = int(os.getenv("MAX_PAGE_SIZE", "100"))
        
        # AI服务性能配置
        self.ai_request_timeout = int(os.getenv("AI_REQUEST_TIMEOUT", "60"))
        self.ai_max_retries = int(os.getenv("AI_MAX_RETRIES", "3"))
        self.ai_retry_delay = float(os.getenv("AI_RETRY_DELAY", "1.0"))
        self.ai_enable_cache = os.getenv("AI_ENABLE_CACHE", "true").lower() == "true"
        self.ai_cache_ttl = int(os.getenv("AI_CACHE_TTL", "1800"))  # 30分钟
        
        # 响应压缩配置
        self.enable_gzip = os.getenv("ENABLE_GZIP", "true").lower() == "true"
        self.gzip_min_size = int(os.getenv("GZIP_MIN_SIZE", "1024"))
        
        # 限流配置
        self.enable_rate_limit = os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true"
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        self.rate_limit_burst = int(os.getenv("RATE_LIMIT_BURST", "10"))


class CacheKeyGenerator:
    """缓存键生成器"""
    
    def __init__(self, prefix: str = "ai_tutor:"):
        self.prefix = prefix
    
    def generate_key(self, namespace: str, identifier: Union[str, int], *args) -> str:
        """生成缓存键"""
        key_parts = [self.prefix, namespace, str(identifier)]
        if args:
            key_parts.extend(str(arg) for arg in args)
        return ":".join(key_parts)
    
    def user_key(self, user_id: int, action: str = "") -> str:
        """生成用户相关缓存键"""
        return self.generate_key("user", user_id, action) if action else self.generate_key("user", user_id)
    
    def grade_key(self, student_id: int, subject: str = "", exam_id: str = "") -> str:
        """生成成绩相关缓存键"""
        return self.generate_key("grade", student_id, subject, exam_id)
    
    def ai_session_key(self, session_id: str) -> str:
        """生成AI会话缓存键"""
        return self.generate_key("ai_session", session_id)
    
    def ai_response_key(self, prompt_hash: str, model: str = "") -> str:
        """生成AI响应缓存键"""
        return self.generate_key("ai_response", prompt_hash, model)
    
    def analytics_key(self, analysis_type: str, target_id: int, time_range: str = "") -> str:
        """生成分析数据缓存键"""
        return self.generate_key("analytics", analysis_type, target_id, time_range)


# 缓存配置实例
cache_config = CacheConfig()
performance_config = PerformanceConfig()
key_generator = CacheKeyGenerator(cache_config.key_prefix)


def get_cache_config() -> CacheConfig:
    """获取缓存配置"""
    return cache_config


def get_performance_config() -> PerformanceConfig:
    """获取性能配置"""
    return performance_config


def get_key_generator() -> CacheKeyGenerator:
    """获取缓存键生成器"""
    return key_generator


# 缓存装饰器配置
CACHE_DECORATORS = {
    "user_profile": {"ttl": 1800, "key_pattern": "user:{user_id}:profile"},
    "grade_list": {"ttl": 600, "key_pattern": "grade:{student_id}:list"},
    "class_statistics": {"ttl": 3600, "key_pattern": "stats:class:{class_id}"},
    "ai_analysis": {"ttl": 1800, "key_pattern": "ai:analysis:{hash}"},
    "teaching_resources": {"ttl": 7200, "key_pattern": "resource:{type}:{id}"},
}


def get_cache_decorator_config(decorator_name: str) -> Dict[str, Any]:
    """获取缓存装饰器配置"""
    return CACHE_DECORATORS.get(decorator_name, {"ttl": cache_config.default_ttl})