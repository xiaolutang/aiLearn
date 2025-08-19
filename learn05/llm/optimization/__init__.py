# -*- coding: utf-8 -*-
"""
性能优化模块
提供缓存、并发处理、性能监控等优化功能

作者: AI Assistant
版本: 1.0.0
创建时间: 2024-01-01
"""

from .cache_manager import (
    CacheManager,
    CacheConfig,
    CacheStrategy,
    LRUCache,
    TTLCache,
    RedisCache,
    MemoryCache
)

from .concurrent_processor import (
    ConcurrentProcessor,
    TaskResult,
    TaskStatus,
    ProcessingConfig,
    ThreadPoolProcessor,
    AsyncProcessor
)

from .performance_monitor import (
    PerformanceMonitor,
    MetricType,
    PerformanceMetric,
    MonitorConfig,
    SystemMonitor,
    APIMonitor
)

from .optimization_manager import (
    OptimizationManager,
    OptimizationConfig,
    OptimizationStrategy
)

__all__ = [
    # 缓存管理
    'CacheManager',
    'CacheConfig', 
    'CacheStrategy',
    'LRUCache',
    'TTLCache',
    'RedisCache',
    'MemoryCache',
    
    # 并发处理
    'ConcurrentProcessor',
    'TaskResult',
    'TaskStatus',
    'ProcessingConfig',
    'ThreadPoolProcessor',
    'AsyncProcessor',
    
    # 性能监控
    'PerformanceMonitor',
    'MetricType',
    'PerformanceMetric',
    'MonitorConfig',
    'SystemMonitor',
    'APIMonitor',
    
    # 优化管理
    'OptimizationManager',
    'OptimizationConfig',
    'OptimizationStrategy'
]

# 便捷函数
def create_cache_manager(strategy: str = 'memory', **kwargs) -> CacheManager:
    """创建缓存管理器"""
    return CacheManager(strategy=strategy, **kwargs)

def create_concurrent_processor(max_workers: int = 4, **kwargs) -> ConcurrentProcessor:
    """创建并发处理器"""
    return ConcurrentProcessor(max_workers=max_workers, **kwargs)

def create_performance_monitor(**kwargs) -> PerformanceMonitor:
    """创建性能监控器"""
    return PerformanceMonitor(**kwargs)

def create_optimization_manager(**kwargs) -> OptimizationManager:
    """创建优化管理器"""
    return OptimizationManager(**kwargs)

# 版本信息
__version__ = '1.0.0'
__author__ = 'AI Assistant'
__description__ = '智能教学助手LLM性能优化模块'