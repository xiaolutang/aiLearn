# -*- coding: utf-8 -*-
"""
性能优化配置模块

本模块定义了系统性能优化相关的配置参数，包括缓存、限流、压缩、
数据库连接池、异步处理等配置。
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class CacheType(str, Enum):
    """缓存类型枚举"""
    REDIS = "redis"
    MEMORY = "memory"
    HYBRID = "hybrid"


class CompressionType(str, Enum):
    """压缩类型枚举"""
    GZIP = "gzip"
    BROTLI = "brotli"
    DEFLATE = "deflate"


class RateLimitAlgorithm(str, Enum):
    """限流算法枚举"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RedisConfig:
    """Redis配置"""
    url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    password: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_PASSWORD"))
    
    # 连接池配置
    max_connections: int = field(default_factory=lambda: int(os.getenv("REDIS_MAX_CONNECTIONS", "50")))
    retry_on_timeout: bool = field(default_factory=lambda: os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true")
    socket_timeout: float = field(default_factory=lambda: float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0")))
    socket_connect_timeout: float = field(default_factory=lambda: float(os.getenv("REDIS_CONNECT_TIMEOUT", "5.0")))
    
    # 集群配置
    cluster_enabled: bool = field(default_factory=lambda: os.getenv("REDIS_CLUSTER_ENABLED", "false").lower() == "true")
    cluster_nodes: List[str] = field(default_factory=lambda: os.getenv("REDIS_CLUSTER_NODES", "").split(",") if os.getenv("REDIS_CLUSTER_NODES") else [])


@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = field(default_factory=lambda: os.getenv("CACHE_ENABLED", "true").lower() == "true")
    cache_type: CacheType = field(default_factory=lambda: CacheType(os.getenv("CACHE_TYPE", "redis")))
    default_ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_DEFAULT_TTL", "300")))
    max_size: int = field(default_factory=lambda: int(os.getenv("CACHE_MAX_SIZE", "10000")))
    
    # Redis配置
    redis: RedisConfig = field(default_factory=RedisConfig)
    
    # 缓存键配置
    key_prefix: str = field(default_factory=lambda: os.getenv("CACHE_KEY_PREFIX", "ailearn:"))
    key_separator: str = field(default_factory=lambda: os.getenv("CACHE_KEY_SEPARATOR", ":"))
    
    # 序列化配置
    serialization_format: str = field(default_factory=lambda: os.getenv("CACHE_SERIALIZATION", "json"))  # json, msgpack, pickle
    compression_enabled: bool = field(default_factory=lambda: os.getenv("CACHE_COMPRESSION", "false").lower() == "true")
    compression_threshold: int = field(default_factory=lambda: int(os.getenv("CACHE_COMPRESSION_THRESHOLD", "1024")))
    
    # API缓存配置
    api_cache_enabled: bool = field(default_factory=lambda: os.getenv("API_CACHE_ENABLED", "true").lower() == "true")
    api_cache_ttl: int = field(default_factory=lambda: int(os.getenv("API_CACHE_TTL", "300")))
    api_cache_exclude_paths: List[str] = field(default_factory=lambda: os.getenv("API_CACHE_EXCLUDE_PATHS", "/health,/docs,/redoc").split(","))
    
    # 查询缓存配置
    query_cache_enabled: bool = field(default_factory=lambda: os.getenv("QUERY_CACHE_ENABLED", "true").lower() == "true")
    query_cache_ttl: int = field(default_factory=lambda: int(os.getenv("QUERY_CACHE_TTL", "600")))


@dataclass
class RateLimitConfig:
    """限流配置"""
    enabled: bool = field(default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true")
    algorithm: RateLimitAlgorithm = field(default_factory=lambda: RateLimitAlgorithm(os.getenv("RATE_LIMIT_ALGORITHM", "token_bucket")))
    
    # 默认限流规则
    default_rate: str = field(default_factory=lambda: os.getenv("RATE_LIMIT_DEFAULT", "100/minute"))
    burst_rate: str = field(default_factory=lambda: os.getenv("RATE_LIMIT_BURST", "200/minute"))
    
    # IP白名单和黑名单
    ip_whitelist: List[str] = field(default_factory=lambda: os.getenv("RATE_LIMIT_IP_WHITELIST", "").split(",") if os.getenv("RATE_LIMIT_IP_WHITELIST") else [])
    ip_blacklist: List[str] = field(default_factory=lambda: os.getenv("RATE_LIMIT_IP_BLACKLIST", "").split(",") if os.getenv("RATE_LIMIT_IP_BLACKLIST") else [])
    
    # 路径特定规则
    path_rules: Dict[str, str] = field(default_factory=lambda: {
        "/api/v1/auth/login": os.getenv("RATE_LIMIT_LOGIN", "10/minute"),
        "/api/v1/grades/import": os.getenv("RATE_LIMIT_IMPORT", "5/minute"),
        "/api/v1/ai/chat": os.getenv("RATE_LIMIT_AI_CHAT", "30/minute"),
        "/api/v1/analytics": os.getenv("RATE_LIMIT_ANALYTICS", "50/minute")
    })
    
    # 用户特定规则
    user_rules: Dict[str, str] = field(default_factory=lambda: {
        "admin": os.getenv("RATE_LIMIT_ADMIN", "1000/minute"),
        "teacher": os.getenv("RATE_LIMIT_TEACHER", "500/minute"),
        "student": os.getenv("RATE_LIMIT_STUDENT", "100/minute")
    })
    
    # 存储配置
    storage_type: str = field(default_factory=lambda: os.getenv("RATE_LIMIT_STORAGE", "redis"))  # redis, memory
    key_prefix: str = field(default_factory=lambda: os.getenv("RATE_LIMIT_KEY_PREFIX", "ratelimit:"))


@dataclass
class CompressionConfig:
    """压缩配置"""
    enabled: bool = field(default_factory=lambda: os.getenv("COMPRESSION_ENABLED", "true").lower() == "true")
    
    # 压缩算法
    gzip_enabled: bool = field(default_factory=lambda: os.getenv("COMPRESSION_GZIP", "true").lower() == "true")
    brotli_enabled: bool = field(default_factory=lambda: os.getenv("COMPRESSION_BROTLI", "true").lower() == "true")
    deflate_enabled: bool = field(default_factory=lambda: os.getenv("COMPRESSION_DEFLATE", "false").lower() == "true")
    
    # 压缩参数
    min_size: int = field(default_factory=lambda: int(os.getenv("COMPRESSION_MIN_SIZE", "1024")))
    gzip_level: int = field(default_factory=lambda: int(os.getenv("COMPRESSION_GZIP_LEVEL", "6")))
    brotli_quality: int = field(default_factory=lambda: int(os.getenv("COMPRESSION_BROTLI_QUALITY", "4")))
    
    # 内容类型过滤
    include_content_types: List[str] = field(default_factory=lambda: [
        "application/json",
        "application/javascript",
        "text/css",
        "text/html",
        "text/plain",
        "text/xml",
        "application/xml"
    ])
    
    exclude_content_types: List[str] = field(default_factory=lambda: [
        "image/*",
        "video/*",
        "audio/*",
        "application/zip",
        "application/gzip"
    ])


@dataclass
class DatabasePerformanceConfig:
    """数据库性能配置"""
    # 连接池配置
    pool_size: int = field(default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "20")))
    max_overflow: int = field(default_factory=lambda: int(os.getenv("DB_MAX_OVERFLOW", "30")))
    pool_timeout: int = field(default_factory=lambda: int(os.getenv("DB_POOL_TIMEOUT", "30")))
    pool_recycle: int = field(default_factory=lambda: int(os.getenv("DB_POOL_RECYCLE", "3600")))
    pool_pre_ping: bool = field(default_factory=lambda: os.getenv("DB_POOL_PRE_PING", "true").lower() == "true")
    
    # 查询配置
    query_timeout: int = field(default_factory=lambda: int(os.getenv("DB_QUERY_TIMEOUT", "30")))
    slow_query_threshold: float = field(default_factory=lambda: float(os.getenv("DB_SLOW_QUERY_THRESHOLD", "1.0")))
    
    # 批量操作配置
    batch_size: int = field(default_factory=lambda: int(os.getenv("DB_BATCH_SIZE", "1000")))
    bulk_insert_chunk_size: int = field(default_factory=lambda: int(os.getenv("DB_BULK_INSERT_CHUNK_SIZE", "500")))
    
    # 读写分离配置
    read_replica_enabled: bool = field(default_factory=lambda: os.getenv("DB_READ_REPLICA_ENABLED", "false").lower() == "true")
    read_replica_url: Optional[str] = field(default_factory=lambda: os.getenv("DB_READ_REPLICA_URL"))


@dataclass
class AsyncConfig:
    """异步处理配置"""
    # 异步任务配置
    max_workers: int = field(default_factory=lambda: int(os.getenv("ASYNC_MAX_WORKERS", "10")))
    task_timeout: int = field(default_factory=lambda: int(os.getenv("ASYNC_TASK_TIMEOUT", "300")))
    
    # 并发控制
    max_concurrent_requests: int = field(default_factory=lambda: int(os.getenv("ASYNC_MAX_CONCURRENT", "100")))
    semaphore_limit: int = field(default_factory=lambda: int(os.getenv("ASYNC_SEMAPHORE_LIMIT", "50")))
    
    # HTTP客户端配置
    http_timeout: int = field(default_factory=lambda: int(os.getenv("HTTP_TIMEOUT", "30")))
    http_max_connections: int = field(default_factory=lambda: int(os.getenv("HTTP_MAX_CONNECTIONS", "100")))
    http_max_keepalive_connections: int = field(default_factory=lambda: int(os.getenv("HTTP_MAX_KEEPALIVE", "20")))


@dataclass
class AIServiceConfig:
    """AI服务性能配置"""
    # 缓存配置
    cache_enabled: bool = field(default_factory=lambda: os.getenv("AI_CACHE_ENABLED", "true").lower() == "true")
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("AI_CACHE_TTL", "3600")))
    
    # 重试配置
    max_retries: int = field(default_factory=lambda: int(os.getenv("AI_MAX_RETRIES", "3")))
    retry_delay: float = field(default_factory=lambda: float(os.getenv("AI_RETRY_DELAY", "1.0")))
    retry_backoff: float = field(default_factory=lambda: float(os.getenv("AI_RETRY_BACKOFF", "2.0")))
    
    # 超时配置
    request_timeout: int = field(default_factory=lambda: int(os.getenv("AI_REQUEST_TIMEOUT", "60")))
    connect_timeout: int = field(default_factory=lambda: int(os.getenv("AI_CONNECT_TIMEOUT", "10")))
    
    # 并发控制
    max_concurrent_requests: int = field(default_factory=lambda: int(os.getenv("AI_MAX_CONCURRENT", "10")))
    
    # 熔断器配置
    circuit_breaker_enabled: bool = field(default_factory=lambda: os.getenv("AI_CIRCUIT_BREAKER", "true").lower() == "true")
    failure_threshold: int = field(default_factory=lambda: int(os.getenv("AI_FAILURE_THRESHOLD", "5")))
    recovery_timeout: int = field(default_factory=lambda: int(os.getenv("AI_RECOVERY_TIMEOUT", "60")))


@dataclass
class MonitoringConfig:
    """监控配置"""
    # 性能监控
    performance_monitoring: bool = field(default_factory=lambda: os.getenv("MONITORING_PERFORMANCE", "true").lower() == "true")
    request_logging: bool = field(default_factory=lambda: os.getenv("MONITORING_REQUEST_LOGGING", "true").lower() == "true")
    
    # 指标收集
    metrics_enabled: bool = field(default_factory=lambda: os.getenv("MONITORING_METRICS", "true").lower() == "true")
    metrics_endpoint: str = field(default_factory=lambda: os.getenv("MONITORING_METRICS_ENDPOINT", "/metrics"))
    
    # 健康检查
    health_check_enabled: bool = field(default_factory=lambda: os.getenv("MONITORING_HEALTH_CHECK", "true").lower() == "true")
    health_check_interval: int = field(default_factory=lambda: int(os.getenv("MONITORING_HEALTH_INTERVAL", "30")))
    
    # 日志配置
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "json"))  # json, text
    log_file_enabled: bool = field(default_factory=lambda: os.getenv("LOG_FILE_ENABLED", "false").lower() == "true")
    log_file_path: str = field(default_factory=lambda: os.getenv("LOG_FILE_PATH", "logs/app.log"))


@dataclass
class PerformanceConfig:
    """性能优化总配置"""
    # 子配置模块
    cache: CacheConfig = field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    compression: CompressionConfig = field(default_factory=CompressionConfig)
    database: DatabasePerformanceConfig = field(default_factory=DatabasePerformanceConfig)
    async_config: AsyncConfig = field(default_factory=AsyncConfig)
    ai_service: AIServiceConfig = field(default_factory=AIServiceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # 全局开关
    optimization_enabled: bool = field(default_factory=lambda: os.getenv("PERFORMANCE_OPTIMIZATION", "true").lower() == "true")
    debug_mode: bool = field(default_factory=lambda: os.getenv("DEBUG_MODE", "false").lower() == "true")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "cache": self.cache.__dict__,
            "rate_limit": self.rate_limit.__dict__,
            "compression": self.compression.__dict__,
            "database": self.database.__dict__,
            "async": self.async_config.__dict__,
            "ai_service": self.ai_service.__dict__,
            "monitoring": self.monitoring.__dict__,
            "optimization_enabled": self.optimization_enabled,
            "debug_mode": self.debug_mode
        }
    
    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        redis_config = self.cache.redis
        if redis_config.url:
            return redis_config.url
        
        auth = f":{redis_config.password}@" if redis_config.password else ""
        return f"redis://{auth}{redis_config.host}:{redis_config.port}/{redis_config.db}"
    
    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否启用"""
        if not self.optimization_enabled:
            return False
        
        feature_map = {
            "cache": self.cache.enabled,
            "rate_limit": self.rate_limit.enabled,
            "compression": self.compression.enabled,
            "monitoring": self.monitoring.performance_monitoring,
            "ai_cache": self.ai_service.cache_enabled,
            "circuit_breaker": self.ai_service.circuit_breaker_enabled
        }
        
        return feature_map.get(feature, False)


# 全局配置实例
performance_config = PerformanceConfig()


def get_performance_config() -> PerformanceConfig:
    """获取性能配置实例"""
    return performance_config


def reload_config():
    """重新加载配置"""
    global performance_config
    performance_config = PerformanceConfig()
    return performance_config