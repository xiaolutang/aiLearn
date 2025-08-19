# -*- coding: utf-8 -*-
"""
性能监控模块
实现系统性能和API性能监控功能
"""

import time
import psutil
import threading
import statistics
from typing import Any, Dict, List, Optional, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import logging
import json
import functools

# 配置日志
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"  # 计数器
    GAUGE = "gauge"      # 仪表
    HISTOGRAM = "histogram"  # 直方图
    TIMER = "timer"      # 计时器

@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    metric_type: MetricType
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels,
            'unit': self.unit,
            'description': self.description
        }

@dataclass
class MonitorConfig:
    """监控配置"""
    collection_interval: float = 1.0  # 收集间隔（秒）
    retention_period: int = 3600  # 保留时间（秒）
    max_metrics: int = 10000  # 最大指标数量
    enable_system_metrics: bool = True
    enable_api_metrics: bool = True
    enable_custom_metrics: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=dict)

class MetricCollector(ABC):
    """指标收集器抽象基类"""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self._metrics: deque = deque(maxlen=config.max_metrics)
        self._lock = threading.RLock()
    
    @abstractmethod
    def collect(self) -> List[PerformanceMetric]:
        """收集指标"""
        pass
    
    def add_metric(self, metric: PerformanceMetric):
        """添加指标"""
        with self._lock:
            self._metrics.append(metric)
    
    def get_metrics(self, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   metric_names: Optional[List[str]] = None) -> List[PerformanceMetric]:
        """获取指标"""
        with self._lock:
            metrics = list(self._metrics)
        
        # 时间过滤
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        # 名称过滤
        if metric_names:
            metrics = [m for m in metrics if m.name in metric_names]
        
        return metrics
    
    def clear_old_metrics(self):
        """清理旧指标"""
        cutoff_time = datetime.now() - timedelta(seconds=self.config.retention_period)
        
        with self._lock:
            # 转换为列表以便修改
            metrics_list = list(self._metrics)
            # 过滤掉旧指标
            filtered_metrics = [m for m in metrics_list if m.timestamp >= cutoff_time]
            # 重新创建deque
            self._metrics.clear()
            self._metrics.extend(filtered_metrics)

class SystemMetricsCollector(MetricCollector):
    """系统指标收集器"""
    
    def collect(self) -> List[PerformanceMetric]:
        """收集系统指标"""
        metrics = []
        timestamp = datetime.now()
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics.append(PerformanceMetric(
                name="system_cpu_usage",
                metric_type=MetricType.GAUGE,
                value=cpu_percent,
                timestamp=timestamp,
                unit="percent",
                description="CPU使用率"
            ))
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            metrics.append(PerformanceMetric(
                name="system_memory_usage",
                metric_type=MetricType.GAUGE,
                value=memory.percent,
                timestamp=timestamp,
                unit="percent",
                description="内存使用率"
            ))
            
            metrics.append(PerformanceMetric(
                name="system_memory_available",
                metric_type=MetricType.GAUGE,
                value=memory.available,
                timestamp=timestamp,
                unit="bytes",
                description="可用内存"
            ))
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            metrics.append(PerformanceMetric(
                name="system_disk_usage",
                metric_type=MetricType.GAUGE,
                value=(disk.used / disk.total) * 100,
                timestamp=timestamp,
                unit="percent",
                description="磁盘使用率"
            ))
            
            # 网络IO
            net_io = psutil.net_io_counters()
            metrics.append(PerformanceMetric(
                name="system_network_bytes_sent",
                metric_type=MetricType.COUNTER,
                value=net_io.bytes_sent,
                timestamp=timestamp,
                unit="bytes",
                description="网络发送字节数"
            ))
            
            metrics.append(PerformanceMetric(
                name="system_network_bytes_recv",
                metric_type=MetricType.COUNTER,
                value=net_io.bytes_recv,
                timestamp=timestamp,
                unit="bytes",
                description="网络接收字节数"
            ))
            
            # 进程数量
            process_count = len(psutil.pids())
            metrics.append(PerformanceMetric(
                name="system_process_count",
                metric_type=MetricType.GAUGE,
                value=process_count,
                timestamp=timestamp,
                unit="count",
                description="系统进程数量"
            ))
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
        
        return metrics

class APIMetricsCollector(MetricCollector):
    """API指标收集器"""
    
    def __init__(self, config: MonitorConfig):
        super().__init__(config)
        self._request_counts = defaultdict(int)
        self._response_times = defaultdict(list)
        self._error_counts = defaultdict(int)
        self._active_requests = defaultdict(int)
    
    def record_request(self, endpoint: str, method: str = "GET"):
        """记录请求"""
        key = f"{method}:{endpoint}"
        self._request_counts[key] += 1
        self._active_requests[key] += 1
        
        # 添加请求计数指标
        self.add_metric(PerformanceMetric(
            name="api_request_count",
            metric_type=MetricType.COUNTER,
            value=self._request_counts[key],
            timestamp=datetime.now(),
            labels={"endpoint": endpoint, "method": method},
            description="API请求计数"
        ))
    
    def record_response(self, endpoint: str, method: str, response_time: float, status_code: int):
        """记录响应"""
        key = f"{method}:{endpoint}"
        self._response_times[key].append(response_time)
        self._active_requests[key] = max(0, self._active_requests[key] - 1)
        
        # 记录错误
        if status_code >= 400:
            self._error_counts[key] += 1
        
        timestamp = datetime.now()
        
        # 添加响应时间指标
        self.add_metric(PerformanceMetric(
            name="api_response_time",
            metric_type=MetricType.TIMER,
            value=response_time,
            timestamp=timestamp,
            labels={"endpoint": endpoint, "method": method, "status": str(status_code)},
            unit="seconds",
            description="API响应时间"
        ))
        
        # 添加错误率指标
        if status_code >= 400:
            self.add_metric(PerformanceMetric(
                name="api_error_count",
                metric_type=MetricType.COUNTER,
                value=self._error_counts[key],
                timestamp=timestamp,
                labels={"endpoint": endpoint, "method": method, "status": str(status_code)},
                description="API错误计数"
            ))
    
    def collect(self) -> List[PerformanceMetric]:
        """收集API指标"""
        metrics = []
        timestamp = datetime.now()
        
        # 活跃请求数
        for key, count in self._active_requests.items():
            method, endpoint = key.split(':', 1)
            metrics.append(PerformanceMetric(
                name="api_active_requests",
                metric_type=MetricType.GAUGE,
                value=count,
                timestamp=timestamp,
                labels={"endpoint": endpoint, "method": method},
                description="活跃API请求数"
            ))
        
        # 平均响应时间
        for key, times in self._response_times.items():
            if times:
                method, endpoint = key.split(':', 1)
                avg_time = statistics.mean(times)
                metrics.append(PerformanceMetric(
                    name="api_avg_response_time",
                    metric_type=MetricType.GAUGE,
                    value=avg_time,
                    timestamp=timestamp,
                    labels={"endpoint": endpoint, "method": method},
                    unit="seconds",
                    description="API平均响应时间"
                ))
        
        return metrics
    
    def get_endpoint_statistics(self, endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """获取端点统计信息"""
        key = f"{method}:{endpoint}"
        
        response_times = self._response_times.get(key, [])
        
        stats = {
            'request_count': self._request_counts.get(key, 0),
            'error_count': self._error_counts.get(key, 0),
            'active_requests': self._active_requests.get(key, 0),
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'error_rate': 0
        }
        
        if stats['request_count'] > 0:
            stats['error_rate'] = stats['error_count'] / stats['request_count'] * 100
        
        return stats

class CustomMetricsCollector(MetricCollector):
    """自定义指标收集器"""
    
    def __init__(self, config: MonitorConfig):
        super().__init__(config)
        self._custom_metrics = {}
    
    def add_custom_metric(self, name: str, value: Union[int, float], 
                         metric_type: MetricType = MetricType.GAUGE,
                         labels: Optional[Dict[str, str]] = None,
                         unit: str = "", description: str = ""):
        """添加自定义指标"""
        metric = PerformanceMetric(
            name=name,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {},
            unit=unit,
            description=description
        )
        
        self.add_metric(metric)
        self._custom_metrics[name] = metric
    
    def increment_counter(self, name: str, value: Union[int, float] = 1,
                         labels: Optional[Dict[str, str]] = None):
        """递增计数器"""
        current_metric = self._custom_metrics.get(name)
        if current_metric and current_metric.metric_type == MetricType.COUNTER:
            new_value = current_metric.value + value
        else:
            new_value = value
        
        self.add_custom_metric(name, new_value, MetricType.COUNTER, labels)
    
    def set_gauge(self, name: str, value: Union[int, float],
                  labels: Optional[Dict[str, str]] = None):
        """设置仪表值"""
        self.add_custom_metric(name, value, MetricType.GAUGE, labels)
    
    def record_histogram(self, name: str, value: Union[int, float],
                        labels: Optional[Dict[str, str]] = None):
        """记录直方图值"""
        self.add_custom_metric(name, value, MetricType.HISTOGRAM, labels)
    
    def collect(self) -> List[PerformanceMetric]:
        """收集自定义指标"""
        return list(self._custom_metrics.values())

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig()
        self._collectors: List[MetricCollector] = []
        self._running = False
        self._monitor_thread = None
        self._lock = threading.RLock()
        
        # 初始化收集器
        if self.config.enable_system_metrics:
            self._collectors.append(SystemMetricsCollector(self.config))
        
        if self.config.enable_api_metrics:
            self.api_collector = APIMetricsCollector(self.config)
            self._collectors.append(self.api_collector)
        
        if self.config.enable_custom_metrics:
            self.custom_collector = CustomMetricsCollector(self.config)
            self._collectors.append(self.custom_collector)
    
    def start(self):
        """启动监控"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        
        logger.info("性能监控已启动")
    
    def stop(self):
        """停止监控"""
        self._running = False
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        logger.info("性能监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                # 收集所有指标
                for collector in self._collectors:
                    metrics = collector.collect()
                    for metric in metrics:
                        collector.add_metric(metric)
                
                # 清理旧指标
                for collector in self._collectors:
                    collector.clear_old_metrics()
                
                # 检查告警阈值
                self._check_alerts()
                
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
            
            time.sleep(self.config.collection_interval)
    
    def _check_alerts(self):
        """检查告警阈值"""
        if not self.config.alert_thresholds:
            return
        
        for collector in self._collectors:
            recent_metrics = collector.get_metrics(
                start_time=datetime.now() - timedelta(seconds=60)
            )
            
            for metric in recent_metrics:
                threshold = self.config.alert_thresholds.get(metric.name)
                if threshold and metric.value > threshold:
                    logger.warning(
                        f"告警: {metric.name} = {metric.value} 超过阈值 {threshold}"
                    )
    
    def get_metrics(self, 
                   metric_names: Optional[List[str]] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[PerformanceMetric]:
        """获取指标"""
        all_metrics = []
        
        for collector in self._collectors:
            metrics = collector.get_metrics(start_time, end_time, metric_names)
            all_metrics.extend(metrics)
        
        return all_metrics
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        recent_time = datetime.now() - timedelta(minutes=5)
        system_metrics = self.get_metrics(
            metric_names=[
                "system_cpu_usage", "system_memory_usage", 
                "system_disk_usage", "system_process_count"
            ],
            start_time=recent_time
        )
        
        stats = {}
        for metric in system_metrics:
            if metric.name not in stats:
                stats[metric.name] = []
            stats[metric.name].append(metric.value)
        
        # 计算平均值
        for name, values in stats.items():
            if values:
                stats[name] = {
                    'current': values[-1],
                    'average': statistics.mean(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return stats
    
    def get_api_stats(self) -> Dict[str, Any]:
        """获取API统计信息"""
        if not hasattr(self, 'api_collector'):
            return {}
        
        # 获取所有端点的统计信息
        endpoints_stats = {}
        
        # 从指标中提取端点信息
        api_metrics = self.get_metrics(
            metric_names=["api_request_count", "api_response_time", "api_error_count"]
        )
        
        endpoints = set()
        for metric in api_metrics:
            if 'endpoint' in metric.labels:
                endpoint = metric.labels['endpoint']
                method = metric.labels.get('method', 'GET')
                endpoints.add((endpoint, method))
        
        for endpoint, method in endpoints:
            endpoints_stats[f"{method}:{endpoint}"] = self.api_collector.get_endpoint_statistics(endpoint, method)
        
        return endpoints_stats
    
    def export_metrics(self, format_type: str = "json") -> str:
        """导出指标"""
        metrics = self.get_metrics()
        
        if format_type.lower() == "json":
            metrics_data = [metric.to_dict() for metric in metrics]
            return json.dumps(metrics_data, indent=2, ensure_ascii=False)
        
        elif format_type.lower() == "prometheus":
            # Prometheus格式
            lines = []
            for metric in metrics:
                labels_str = ""
                if metric.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                
                lines.append(f"{metric.name}{labels_str} {metric.value}")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"不支持的格式: {format_type}")
    
    def add_custom_metric(self, name: str, value: Union[int, float], 
                         metric_type: MetricType = MetricType.GAUGE,
                         labels: Optional[Dict[str, str]] = None,
                         unit: str = "", description: str = ""):
        """添加自定义指标"""
        if hasattr(self, 'custom_collector'):
            self.custom_collector.add_custom_metric(
                name, value, metric_type, labels, unit, description
            )
    
    def record_api_request(self, endpoint: str, method: str = "GET"):
        """记录API请求"""
        if hasattr(self, 'api_collector'):
            self.api_collector.record_request(endpoint, method)
    
    def record_api_response(self, endpoint: str, method: str, response_time: float, status_code: int):
        """记录API响应"""
        if hasattr(self, 'api_collector'):
            self.api_collector.record_response(endpoint, method, response_time, status_code)

class SystemMonitor:
    """系统监控器（简化版）"""
    
    @staticmethod
    def get_cpu_usage() -> float:
        """获取CPU使用率"""
        return psutil.cpu_percent(interval=0.1)
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }
    
    @staticmethod
    def get_disk_usage(path: str = '/') -> Dict[str, float]:
        """获取磁盘使用情况"""
        disk = psutil.disk_usage(path)
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': (disk.used / disk.total) * 100
        }
    
    @staticmethod
    def get_network_io() -> Dict[str, int]:
        """获取网络IO"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }

class APIMonitor:
    """API监控器（装饰器版）"""
    
    def __init__(self, monitor: Optional[PerformanceMonitor] = None):
        self.monitor = monitor
    
    def __call__(self, endpoint: str, method: str = "GET"):
        """API监控装饰器"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                # 记录请求
                if self.monitor:
                    self.monitor.record_api_request(endpoint, method)
                
                try:
                    result = func(*args, **kwargs)
                    status_code = 200
                    return result
                    
                except Exception as e:
                    status_code = 500
                    raise e
                    
                finally:
                    # 记录响应
                    response_time = time.time() - start_time
                    if self.monitor:
                        self.monitor.record_api_response(endpoint, method, response_time, status_code)
            
            return wrapper
        return decorator

# 全局监控实例
_global_monitor = None

def get_global_monitor() -> PerformanceMonitor:
    """获取全局监控器"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
        _global_monitor.start()
    return _global_monitor

def set_global_monitor(monitor: PerformanceMonitor):
    """设置全局监控器"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.stop()
    _global_monitor = monitor

# 便捷装饰器
def monitor_api(endpoint: str, method: str = "GET"):
    """API监控装饰器（使用全局监控器）"""
    return APIMonitor(get_global_monitor())(endpoint, method)

def monitor_performance(metric_name: str, metric_type: MetricType = MetricType.TIMER):
    """性能监控装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                monitor = get_global_monitor()
                monitor.add_custom_metric(
                    metric_name, execution_time, metric_type,
                    labels={'function': func.__name__},
                    unit='seconds'
                )
        
        return wrapper
    return decorator