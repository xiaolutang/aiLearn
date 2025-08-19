# -*- coding: utf-8 -*-
"""
中间件模块

本模块提供完整的中间件集成，包括性能监控、缓存、限流、压缩等功能。
"""

import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI

# 导入所有中间件
from .performance import (
    PerformanceMonitoringMiddleware,
    RequestLoggingMiddleware,
    CORSMiddleware,
    setup_middleware as setup_performance_middleware
)
from .cache_middleware import (
    CacheMiddleware,
    SmartCacheMiddleware,
    setup_cache_middleware
)
from .rate_limit_middleware import (
    RateLimitMiddleware,
    setup_rate_limit_middleware
)
from .compression_middleware import (
    CompressionMiddleware,
    ContentOptimizationMiddleware,
    setup_compression_middleware
)

# 尝试导入缓存管理器
try:
    from ..utils.cache_manager import CacheManager
    from ..config.cache_config import CacheConfig, PerformanceConfig
except ImportError:
    # 开发阶段的模拟实现
    class CacheManager:
        async def get(self, key: str) -> Optional[Any]:
            return None
        
        async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
            return True
    
    class CacheConfig:
        def __init__(self):
            self.enabled = True
            self.default_ttl = 300
    
    class PerformanceConfig:
        def __init__(self):
            self.enable_compression = True
            self.enable_caching = True
            self.enable_rate_limiting = True

logger = logging.getLogger(__name__)


class MiddlewareManager:
    """中间件管理器"""
    
    def __init__(self):
        self.cache_manager = None
        self.performance_middleware = None
        self.cache_middleware = None
        self.rate_limit_middleware = None
        self.compression_middleware = None
        self.is_initialized = False
    
    async def initialize(self, config: Dict[str, Any] = None):
        """初始化中间件管理器"""
        if self.is_initialized:
            return
        
        config = config or {}
        
        # 初始化缓存管理器
        cache_config = CacheConfig()
        self.cache_manager = CacheManager()
        
        logger.info("中间件管理器初始化完成")
        self.is_initialized = True
    
    def setup_all_middleware(self, app: FastAPI, config: Dict[str, Any] = None):
        """设置所有中间件"""
        config = config or {}
        performance_config = PerformanceConfig()
        
        # 中间件添加顺序很重要，按照请求处理的逆序添加
        
        # 1. 压缩中间件（最后处理响应）
        if performance_config.enable_compression:
            setup_compression_middleware(app, config)
            logger.info("✓ 压缩中间件已启用")
        
        # 2. 缓存中间件
        if performance_config.enable_caching and self.cache_manager:
            setup_cache_middleware(app, self.cache_manager, config)
            logger.info("✓ 缓存中间件已启用")
        
        # 3. 限流中间件
        if performance_config.enable_rate_limiting and self.cache_manager:
            setup_rate_limit_middleware(app, self.cache_manager, config)
            logger.info("✓ 限流中间件已启用")
        
        # 4. 性能监控中间件（最先处理请求）
        setup_performance_middleware(app, config)
        logger.info("✓ 性能监控中间件已启用")
        
        logger.info("所有中间件设置完成")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        stats = {
            "middleware_status": {
                "initialized": self.is_initialized,
                "cache_manager": self.cache_manager is not None,
                "performance_middleware": self.performance_middleware is not None,
                "cache_middleware": self.cache_middleware is not None,
                "rate_limit_middleware": self.rate_limit_middleware is not None,
                "compression_middleware": self.compression_middleware is not None
            }
        }
        
        # 收集各中间件的统计信息
        if self.performance_middleware:
            stats["performance"] = self.performance_middleware.get_stats()
        
        if self.cache_middleware:
            stats["cache"] = self.cache_middleware.get_cache_stats()
        
        if self.rate_limit_middleware:
            stats["rate_limit"] = self.rate_limit_middleware.get_stats()
        
        if self.compression_middleware:
            stats["compression"] = self.compression_middleware.get_compression_stats()
        
        return stats
    
    async def clear_all_caches(self):
        """清除所有缓存"""
        if self.cache_manager:
            try:
                await self.cache_manager.clear_pattern("*")
                logger.info("所有缓存已清除")
            except Exception as e:
                logger.error(f"清除缓存失败: {e}")
        
        if self.cache_middleware:
            await self.cache_middleware.invalidate_cache("*")
        
        if self.rate_limit_middleware:
            await self.rate_limit_middleware.reset_limits()


# 全局中间件管理器实例
middleware_manager = MiddlewareManager()


def setup_middleware(app: FastAPI, config: Dict[str, Any] = None):
    """设置所有中间件的便捷函数"""
    config = config or {}
    
    # 初始化中间件管理器
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 如果事件循环正在运行，创建任务
        asyncio.create_task(middleware_manager.initialize(config))
    else:
        # 如果事件循环未运行，直接运行
        loop.run_until_complete(middleware_manager.initialize(config))
    
    # 设置所有中间件
    middleware_manager.setup_all_middleware(app, config)
    
    return middleware_manager


def get_middleware_manager() -> MiddlewareManager:
    """获取中间件管理器实例"""
    return middleware_manager


# 导出主要类和函数
__all__ = [
    "MiddlewareManager",
    "middleware_manager",
    "setup_middleware",
    "get_middleware_manager",
    "PerformanceMonitoringMiddleware",
    "CacheMiddleware",
    "SmartCacheMiddleware",
    "RateLimitMiddleware",
    "CompressionMiddleware",
    "ContentOptimizationMiddleware"
]