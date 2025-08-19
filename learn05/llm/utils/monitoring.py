#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手AI服务监控模块
提供性能监控、日志记录、健康检查等功能
"""

import time
import logging
import asyncio
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from functools import wraps
from contextlib import asynccontextmanager

@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    timestamp: datetime
    service_name: str
    operation: str
    duration: float
    success: bool
    error_message: Optional[str] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

@dataclass
class SystemMetrics:
    """系统指标数据结构"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_usage: float
    active_connections: int
    request_queue_size: int

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.performance_metrics: deque = deque(maxlen=max_metrics)
        self.system_metrics: deque = deque(maxlen=max_metrics)
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        
    def add_performance_metric(self, metric: PerformanceMetrics):
        """添加性能指标"""
        self.performance_metrics.append(metric)
        
        # 更新统计信息
        key = f"{metric.service_name}.{metric.operation}"
        self.request_counts[key] += 1
        self.response_times[key].append(metric.duration)
        
        if not metric.success:
            self.error_counts[key] += 1
        
        # 保持响应时间列表大小
        if len(self.response_times[key]) > 1000:
            self.response_times[key] = self.response_times[key][-1000:]
    
    def add_system_metric(self, metric: SystemMetrics):
        """添加系统指标"""
        self.system_metrics.append(metric)
    
    def get_performance_summary(self, service_name: str = None, 
                              time_window: timedelta = None) -> Dict[str, Any]:
        """获取性能摘要"""
        now = datetime.now()
        cutoff_time = now - time_window if time_window else None
        
        filtered_metrics = [
            m for m in self.performance_metrics
            if (not service_name or m.service_name == service_name) and
               (not cutoff_time or m.timestamp >= cutoff_time)
        ]
        
        if not filtered_metrics:
            return {"message": "No metrics found"}
        
        # 计算统计信息
        total_requests = len(filtered_metrics)
        successful_requests = sum(1 for m in filtered_metrics if m.success)
        failed_requests = total_requests - successful_requests
        
        durations = [m.duration for m in filtered_metrics]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # 按操作分组统计
        operation_stats = defaultdict(lambda: {
            'count': 0, 'success': 0, 'failed': 0, 'avg_duration': 0
        })
        
        for metric in filtered_metrics:
            op_stats = operation_stats[metric.operation]
            op_stats['count'] += 1
            if metric.success:
                op_stats['success'] += 1
            else:
                op_stats['failed'] += 1
        
        # 计算平均响应时间
        for operation, stats in operation_stats.items():
            op_durations = [m.duration for m in filtered_metrics if m.operation == operation]
            stats['avg_duration'] = sum(op_durations) / len(op_durations) if op_durations else 0
        
        return {
            "time_window": str(time_window) if time_window else "all_time",
            "service_name": service_name or "all_services",
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "avg_response_time": avg_duration,
            "max_response_time": max_duration,
            "min_response_time": min_duration,
            "operation_stats": dict(operation_stats)
        }
    
    def get_system_summary(self, time_window: timedelta = None) -> Dict[str, Any]:
        """获取系统摘要"""
        now = datetime.now()
        cutoff_time = now - time_window if time_window else None
        
        filtered_metrics = [
            m for m in self.system_metrics
            if not cutoff_time or m.timestamp >= cutoff_time
        ]
        
        if not filtered_metrics:
            return {"message": "No system metrics found"}
        
        latest_metric = filtered_metrics[-1]
        
        cpu_values = [m.cpu_percent for m in filtered_metrics]
        memory_values = [m.memory_percent for m in filtered_metrics]
        
        return {
            "time_window": str(time_window) if time_window else "all_time",
            "current_cpu_percent": latest_metric.cpu_percent,
            "current_memory_percent": latest_metric.memory_percent,
            "current_memory_available_mb": latest_metric.memory_available // (1024 * 1024),
            "current_disk_usage": latest_metric.disk_usage,
            "avg_cpu_percent": sum(cpu_values) / len(cpu_values),
            "max_cpu_percent": max(cpu_values),
            "avg_memory_percent": sum(memory_values) / len(memory_values),
            "max_memory_percent": max(memory_values),
            "active_connections": latest_metric.active_connections,
            "request_queue_size": latest_metric.request_queue_size
        }

class AIServiceMonitor:
    """AI服务监控器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_collector = MetricsCollector()
        self.logger = self._setup_logger()
        self.is_monitoring = False
        self.monitor_task = None
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("ai_service_monitor")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 文件处理器
            file_handler = logging.FileHandler("logs/ai_service_monitor.log")
            file_handler.setLevel(logging.DEBUG)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        
        return logger
    
    def start_monitoring(self, interval: int = 30):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
        self.logger.info(f"AI服务监控已启动，监控间隔: {interval}秒")
    
    async def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("AI服务监控已停止")
    
    async def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.is_monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"监控循环出错: {str(e)}")
                await asyncio.sleep(interval)
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            # 获取系统资源使用情况
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 获取网络连接数（简化版）
            connections = len(psutil.net_connections())
            
            metric = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available=memory.available,
                disk_usage=disk.percent,
                active_connections=connections,
                request_queue_size=0  # 需要从应用层获取
            )
            
            self.metrics_collector.add_system_metric(metric)
            
            # 检查资源使用警告
            if cpu_percent > 80:
                self.logger.warning(f"CPU使用率过高: {cpu_percent}%")
            if memory.percent > 85:
                self.logger.warning(f"内存使用率过高: {memory.percent}%")
            if disk.percent > 90:
                self.logger.warning(f"磁盘使用率过高: {disk.percent}%")
                
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {str(e)}")
    
    def record_performance(self, service_name: str, operation: str, 
                          duration: float, success: bool, 
                          error_message: str = None, **kwargs):
        """记录性能指标"""
        metric = PerformanceMetrics(
            timestamp=datetime.now(),
            service_name=service_name,
            operation=operation,
            duration=duration,
            success=success,
            error_message=error_message,
            **kwargs
        )
        
        self.metrics_collector.add_performance_metric(metric)
        
        # 记录日志
        if success:
            self.logger.info(
                f"[{service_name}] {operation} 成功 - 耗时: {duration:.3f}s"
            )
        else:
            self.logger.error(
                f"[{service_name}] {operation} 失败 - 耗时: {duration:.3f}s - 错误: {error_message}"
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        try:
            # 获取最近的系统指标
            system_summary = self.metrics_collector.get_system_summary(
                time_window=timedelta(minutes=5)
            )
            
            # 获取最近的性能指标
            performance_summary = self.metrics_collector.get_performance_summary(
                time_window=timedelta(minutes=5)
            )
            
            # 判断健康状态
            is_healthy = True
            issues = []
            
            if isinstance(system_summary, dict) and "current_cpu_percent" in system_summary:
                if system_summary["current_cpu_percent"] > 90:
                    is_healthy = False
                    issues.append("CPU使用率过高")
                
                if system_summary["current_memory_percent"] > 90:
                    is_healthy = False
                    issues.append("内存使用率过高")
            
            if isinstance(performance_summary, dict) and "success_rate" in performance_summary:
                if performance_summary["success_rate"] < 0.95:
                    is_healthy = False
                    issues.append("成功率过低")
                
                if performance_summary["avg_response_time"] > 5.0:
                    is_healthy = False
                    issues.append("响应时间过长")
            
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "issues": issues,
                "system_metrics": system_summary,
                "performance_metrics": performance_summary
            }
            
        except Exception as e:
            self.logger.error(f"获取健康状态失败: {str(e)}")
            return {
                "status": "unknown",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def export_metrics(self, format_type: str = "json") -> str:
        """导出指标数据"""
        try:
            data = {
                "export_time": datetime.now().isoformat(),
                "performance_metrics": [
                    asdict(m) for m in list(self.metrics_collector.performance_metrics)
                ],
                "system_metrics": [
                    asdict(m) for m in list(self.metrics_collector.system_metrics)
                ]
            }
            
            if format_type.lower() == "json":
                return json.dumps(data, default=str, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
                
        except Exception as e:
            self.logger.error(f"导出指标数据失败: {str(e)}")
            return f"{{\"error\": \"{str(e)}\"}}"

def performance_monitor(service_name: str, operation: str = None):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation or func.__name__
            success = True
            error_msg = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                duration = time.time() - start_time
                # 这里需要访问全局监控器实例
                # 在实际使用中，可以通过依赖注入或全局变量获取
                pass
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation or func.__name__
            success = True
            error_msg = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                duration = time.time() - start_time
                # 记录性能指标
                pass
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

@asynccontextmanager
async def monitor_operation(monitor: AIServiceMonitor, service_name: str, operation: str):
    """操作监控上下文管理器"""
    start_time = time.time()
    success = True
    error_msg = None
    
    try:
        yield
    except Exception as e:
        success = False
        error_msg = str(e)
        raise
    finally:
        duration = time.time() - start_time
        monitor.record_performance(
            service_name=service_name,
            operation=operation,
            duration=duration,
            success=success,
            error_message=error_msg
        )

# 全局监控器实例
global_monitor = AIServiceMonitor()