# -*- coding: utf-8 -*-
"""
优化管理器模块
整合缓存、并发处理和性能监控功能
"""

import time
import asyncio
import threading
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import functools

from .cache_manager import CacheManager, CacheConfig
from .concurrent_processor import ConcurrentProcessor, ThreadPoolProcessor, AsyncProcessor, ProcessingConfig
from .performance_monitor import PerformanceMonitor, MonitorConfig, MetricType

# 配置日志
logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """优化策略"""
    PERFORMANCE = "performance"  # 性能优先
    MEMORY = "memory"           # 内存优先
    BALANCED = "balanced"       # 平衡模式
    CUSTOM = "custom"           # 自定义

@dataclass
class OptimizationConfig:
    """优化配置"""
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    
    # 缓存配置
    cache_config: Optional[CacheConfig] = None
    enable_cache: bool = True
    cache_ttl: int = 3600  # 默认缓存1小时
    
    # 并发配置
    processing_config: Optional[ProcessingConfig] = None
    enable_concurrent: bool = True
    max_workers: int = 4
    
    # 监控配置
    monitor_config: Optional[MonitorConfig] = None
    enable_monitoring: bool = True
    
    # 性能阈值
    max_response_time: float = 5.0  # 最大响应时间（秒）
    max_memory_usage: float = 80.0  # 最大内存使用率（%）
    max_cpu_usage: float = 80.0     # 最大CPU使用率（%）
    
    # 自动优化
    enable_auto_optimization: bool = True
    optimization_interval: int = 300  # 优化检查间隔（秒）
    
    def __post_init__(self):
        """初始化后处理"""
        if self.cache_config is None:
            self.cache_config = CacheConfig()
        
        if self.processing_config is None:
            self.processing_config = ProcessingConfig(
                max_workers=self.max_workers
            )
        
        if self.monitor_config is None:
            self.monitor_config = MonitorConfig()

class OptimizationRule(ABC):
    """优化规则抽象基类"""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
        self.enabled = True
    
    @abstractmethod
    def should_apply(self, context: Dict[str, Any]) -> bool:
        """判断是否应该应用此规则"""
        pass
    
    @abstractmethod
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用优化规则"""
        pass
    
    def get_description(self) -> str:
        """获取规则描述"""
        return f"优化规则: {self.name}"

class CacheOptimizationRule(OptimizationRule):
    """缓存优化规则"""
    
    def __init__(self):
        super().__init__("缓存优化", priority=1)
    
    def should_apply(self, context: Dict[str, Any]) -> bool:
        """判断是否需要缓存优化"""
        cache_hit_rate = context.get('cache_hit_rate', 0)
        response_time = context.get('avg_response_time', 0)
        
        # 缓存命中率低或响应时间长时应用缓存优化
        return cache_hit_rate < 0.7 or response_time > 2.0
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用缓存优化"""
        optimizations = []
        
        cache_hit_rate = context.get('cache_hit_rate', 0)
        if cache_hit_rate < 0.5:
            optimizations.append("增加缓存TTL时间")
            optimizations.append("扩大缓存容量")
        
        response_time = context.get('avg_response_time', 0)
        if response_time > 3.0:
            optimizations.append("启用预加载缓存")
            optimizations.append("优化缓存键策略")
        
        return {
            'rule': self.name,
            'optimizations': optimizations,
            'estimated_improvement': '20-40%'
        }

class ConcurrencyOptimizationRule(OptimizationRule):
    """并发优化规则"""
    
    def __init__(self):
        super().__init__("并发优化", priority=2)
    
    def should_apply(self, context: Dict[str, Any]) -> bool:
        """判断是否需要并发优化"""
        cpu_usage = context.get('cpu_usage', 0)
        active_requests = context.get('active_requests', 0)
        queue_length = context.get('queue_length', 0)
        
        # CPU使用率低但有排队请求时，或队列过长时应用并发优化
        return (cpu_usage < 50 and active_requests > 0) or queue_length > 10
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用并发优化"""
        optimizations = []
        
        cpu_usage = context.get('cpu_usage', 0)
        current_workers = context.get('current_workers', 1)
        
        if cpu_usage < 30 and current_workers < 8:
            optimizations.append(f"增加工作线程数到 {min(current_workers * 2, 8)}")
        
        queue_length = context.get('queue_length', 0)
        if queue_length > 20:
            optimizations.append("启用异步处理模式")
            optimizations.append("实现请求批处理")
        
        return {
            'rule': self.name,
            'optimizations': optimizations,
            'estimated_improvement': '30-50%'
        }

class MemoryOptimizationRule(OptimizationRule):
    """内存优化规则"""
    
    def __init__(self):
        super().__init__("内存优化", priority=3)
    
    def should_apply(self, context: Dict[str, Any]) -> bool:
        """判断是否需要内存优化"""
        memory_usage = context.get('memory_usage', 0)
        cache_size = context.get('cache_size', 0)
        
        # 内存使用率高时应用内存优化
        return memory_usage > 75 or cache_size > 1000000  # 1MB
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用内存优化"""
        optimizations = []
        
        memory_usage = context.get('memory_usage', 0)
        if memory_usage > 85:
            optimizations.append("清理过期缓存")
            optimizations.append("减少缓存容量")
            optimizations.append("启用内存压缩")
        
        cache_size = context.get('cache_size', 0)
        if cache_size > 2000000:  # 2MB
            optimizations.append("实现缓存分层")
            optimizations.append("优化数据序列化")
        
        return {
            'rule': self.name,
            'optimizations': optimizations,
            'estimated_improvement': '15-30%'
        }

class OptimizationManager:
    """优化管理器"""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        
        # 初始化组件
        self.cache_manager = None
        self.processor = None
        self.monitor = None
        
        if self.config.enable_cache:
            self.cache_manager = CacheManager(self.config.cache_config)
        
        if self.config.enable_concurrent:
            self.processor = ThreadPoolProcessor(self.config.processing_config)
        
        if self.config.enable_monitoring:
            self.monitor = PerformanceMonitor(self.config.monitor_config)
            self.monitor.start()
        
        # 优化规则
        self.rules: List[OptimizationRule] = [
            CacheOptimizationRule(),
            ConcurrencyOptimizationRule(),
            MemoryOptimizationRule()
        ]
        
        # 自动优化
        self._auto_optimization_enabled = self.config.enable_auto_optimization
        self._optimization_thread = None
        self._running = False
        
        if self._auto_optimization_enabled:
            self.start_auto_optimization()
    
    def start_auto_optimization(self):
        """启动自动优化"""
        if self._running:
            return
        
        self._running = True
        self._optimization_thread = threading.Thread(target=self._auto_optimization_loop)
        self._optimization_thread.daemon = True
        self._optimization_thread.start()
        
        logger.info("自动优化已启动")
    
    def stop_auto_optimization(self):
        """停止自动优化"""
        self._running = False
        
        if self._optimization_thread:
            self._optimization_thread.join(timeout=5.0)
        
        logger.info("自动优化已停止")
    
    def _auto_optimization_loop(self):
        """自动优化循环"""
        while self._running:
            try:
                # 收集系统状态
                context = self._collect_optimization_context()
                
                # 应用优化规则
                optimizations = self.analyze_and_optimize(context)
                
                if optimizations:
                    logger.info(f"自动优化建议: {optimizations}")
                    
                    # 应用自动优化
                    self._apply_auto_optimizations(optimizations)
                
            except Exception as e:
                logger.error(f"自动优化错误: {e}")
            
            time.sleep(self.config.optimization_interval)
    
    def _collect_optimization_context(self) -> Dict[str, Any]:
        """收集优化上下文信息"""
        context = {}
        
        # 缓存信息
        if self.cache_manager:
            cache_stats = self.cache_manager.get_stats()
            context.update({
                'cache_hit_rate': cache_stats.get('hit_rate', 0),
                'cache_size': cache_stats.get('size', 0),
                'cache_memory_usage': cache_stats.get('memory_usage', 0)
            })
        
        # 处理器信息
        if self.processor:
            processor_stats = self.processor.get_stats()
            context.update({
                'active_requests': processor_stats.get('active_tasks', 0),
                'queue_length': processor_stats.get('pending_tasks', 0),
                'current_workers': processor_stats.get('worker_count', 1)
            })
        
        # 系统监控信息
        if self.monitor:
            system_stats = self.monitor.get_system_stats()
            api_stats = self.monitor.get_api_stats()
            
            # 系统指标
            cpu_stats = system_stats.get('system_cpu_usage', {})
            memory_stats = system_stats.get('system_memory_usage', {})
            
            if isinstance(cpu_stats, dict):
                context['cpu_usage'] = cpu_stats.get('current', 0)
            if isinstance(memory_stats, dict):
                context['memory_usage'] = memory_stats.get('current', 0)
            
            # API指标
            if api_stats:
                response_times = []
                for endpoint_stats in api_stats.values():
                    if 'avg_response_time' in endpoint_stats:
                        response_times.append(endpoint_stats['avg_response_time'])
                
                if response_times:
                    context['avg_response_time'] = sum(response_times) / len(response_times)
        
        return context
    
    def analyze_and_optimize(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析并生成优化建议"""
        optimizations = []
        
        # 按优先级排序规则
        sorted_rules = sorted(self.rules, key=lambda r: r.priority)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            try:
                if rule.should_apply(context):
                    optimization = rule.apply(context)
                    optimizations.append(optimization)
                    
                    logger.info(f"应用优化规则: {rule.name}")
                    
            except Exception as e:
                logger.error(f"优化规则 {rule.name} 执行失败: {e}")
        
        return optimizations
    
    def _apply_auto_optimizations(self, optimizations: List[Dict[str, Any]]):
        """应用自动优化"""
        for optimization in optimizations:
            rule_name = optimization.get('rule')
            optimizations_list = optimization.get('optimizations', [])
            
            for opt in optimizations_list:
                try:
                    self._execute_optimization(opt)
                except Exception as e:
                    logger.error(f"执行优化 '{opt}' 失败: {e}")
    
    def _execute_optimization(self, optimization: str):
        """执行具体的优化操作"""
        if "增加缓存TTL" in optimization and self.cache_manager:
            # 动态调整缓存TTL
            current_ttl = self.config.cache_ttl
            new_ttl = min(current_ttl * 1.5, 7200)  # 最大2小时
            self.config.cache_ttl = int(new_ttl)
            logger.info(f"缓存TTL调整为: {new_ttl}秒")
        
        elif "清理过期缓存" in optimization and self.cache_manager:
            # 清理缓存
            self.cache_manager.clear()
            logger.info("已清理过期缓存")
        
        elif "增加工作线程" in optimization and self.processor:
            # 动态调整线程数（这里只是示例，实际实现可能需要重新创建处理器）
            logger.info(f"建议增加工作线程数: {optimization}")
        
        else:
            logger.info(f"优化建议: {optimization}")
    
    def add_optimization_rule(self, rule: OptimizationRule):
        """添加优化规则"""
        self.rules.append(rule)
        logger.info(f"添加优化规则: {rule.name}")
    
    def remove_optimization_rule(self, rule_name: str):
        """移除优化规则"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        logger.info(f"移除优化规则: {rule_name}")
    
    def enable_rule(self, rule_name: str):
        """启用优化规则"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info(f"启用优化规则: {rule_name}")
                break
    
    def disable_rule(self, rule_name: str):
        """禁用优化规则"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info(f"禁用优化规则: {rule_name}")
                break
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        context = self._collect_optimization_context()
        optimizations = self.analyze_and_optimize(context)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_context': context,
            'optimization_suggestions': optimizations,
            'active_rules': [r.name for r in self.rules if r.enabled],
            'performance_summary': self._generate_performance_summary(context)
        }
        
        return report
    
    def _generate_performance_summary(self, context: Dict[str, Any]) -> Dict[str, str]:
        """生成性能摘要"""
        summary = {}
        
        # CPU状态
        cpu_usage = context.get('cpu_usage', 0)
        if cpu_usage > 80:
            summary['cpu'] = "高负载"
        elif cpu_usage > 50:
            summary['cpu'] = "中等负载"
        else:
            summary['cpu'] = "低负载"
        
        # 内存状态
        memory_usage = context.get('memory_usage', 0)
        if memory_usage > 80:
            summary['memory'] = "内存紧张"
        elif memory_usage > 60:
            summary['memory'] = "内存适中"
        else:
            summary['memory'] = "内存充足"
        
        # 缓存状态
        cache_hit_rate = context.get('cache_hit_rate', 0)
        if cache_hit_rate > 0.8:
            summary['cache'] = "缓存效果良好"
        elif cache_hit_rate > 0.5:
            summary['cache'] = "缓存效果一般"
        else:
            summary['cache'] = "缓存效果较差"
        
        # 响应时间状态
        avg_response_time = context.get('avg_response_time', 0)
        if avg_response_time > 3.0:
            summary['response_time'] = "响应较慢"
        elif avg_response_time > 1.0:
            summary['response_time'] = "响应正常"
        else:
            summary['response_time'] = "响应快速"
        
        return summary
    
    def optimize_function(self, 
                         cache_key: Optional[str] = None,
                         cache_ttl: Optional[int] = None,
                         enable_concurrent: bool = False,
                         monitor_performance: bool = True):
        """函数优化装饰器"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                if cache_key and self.cache_manager:
                    key = f"{cache_key}:{hash(str(args) + str(kwargs))}"
                    
                    # 尝试从缓存获取
                    cached_result = self.cache_manager.get(key)
                    if cached_result is not None:
                        return cached_result
                
                # 性能监控
                start_time = time.time() if monitor_performance else None
                
                try:
                    # 执行函数
                    if enable_concurrent and self.processor:
                        # 并发执行
                        future = self.processor.submit(func, *args, **kwargs)
                        result = future.result()
                    else:
                        # 同步执行
                        result = func(*args, **kwargs)
                    
                    # 缓存结果
                    if cache_key and self.cache_manager:
                        ttl = cache_ttl or self.config.cache_ttl
                        self.cache_manager.set(key, result, ttl)
                    
                    return result
                    
                finally:
                    # 记录性能指标
                    if monitor_performance and start_time and self.monitor:
                        execution_time = time.time() - start_time
                        self.monitor.add_custom_metric(
                            f"function_execution_time",
                            execution_time,
                            MetricType.TIMER,
                            labels={'function': func.__name__},
                            unit='seconds'
                        )
            
            return wrapper
        return decorator
    
    def get_cache_manager(self) -> Optional[CacheManager]:
        """获取缓存管理器"""
        return self.cache_manager
    
    def get_processor(self) -> Optional[ConcurrentProcessor]:
        """获取并发处理器"""
        return self.processor
    
    def get_monitor(self) -> Optional[PerformanceMonitor]:
        """获取性能监控器"""
        return self.monitor
    
    def shutdown(self):
        """关闭优化管理器"""
        self.stop_auto_optimization()
        
        if self.processor:
            self.processor.shutdown()
        
        if self.monitor:
            self.monitor.stop()
        
        logger.info("优化管理器已关闭")

# 全局优化管理器实例
_global_optimization_manager = None

def get_global_optimization_manager() -> OptimizationManager:
    """获取全局优化管理器"""
    global _global_optimization_manager
    if _global_optimization_manager is None:
        _global_optimization_manager = OptimizationManager()
    return _global_optimization_manager

def set_global_optimization_manager(manager: OptimizationManager):
    """设置全局优化管理器"""
    global _global_optimization_manager
    if _global_optimization_manager:
        _global_optimization_manager.shutdown()
    _global_optimization_manager = manager

# 便捷装饰器
def optimize(cache_key: Optional[str] = None,
            cache_ttl: Optional[int] = None,
            enable_concurrent: bool = False,
            monitor_performance: bool = True):
    """优化装饰器（使用全局优化管理器）"""
    manager = get_global_optimization_manager()
    return manager.optimize_function(cache_key, cache_ttl, enable_concurrent, monitor_performance)

def cached(key: str, ttl: int = 3600):
    """缓存装饰器"""
    return optimize(cache_key=key, cache_ttl=ttl)

def concurrent(func):
    """并发装饰器"""
    return optimize(enable_concurrent=True)(func)

def monitored(func):
    """监控装饰器"""
    return optimize(monitor_performance=True)(func)