#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM监控和指标收集模块
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json

from .unified_interface import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """请求指标"""
    timestamp: float
    provider: LLMProvider
    model: str
    success: bool
    latency: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class ProviderStats:
    """提供商统计"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    total_tokens: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_request_time: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def average_latency(self) -> float:
        """平均延迟"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency / self.successful_requests
    
    @property
    def tokens_per_second(self) -> float:
        """每秒处理的Token数"""
        if self.total_latency == 0:
            return 0.0
        return self.total_tokens / self.total_latency


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_history: int = 10000, window_size: int = 3600):
        self.max_history = max_history
        self.window_size = window_size  # 时间窗口大小（秒）
        
        # 指标存储
        self.metrics_history: deque = deque(maxlen=max_history)
        self.provider_stats: Dict[LLMProvider, ProviderStats] = defaultdict(ProviderStats)
        self.model_stats: Dict[str, ProviderStats] = defaultdict(ProviderStats)
        
        # 实时指标
        self.current_window_metrics: deque = deque()
        
        # 线程锁
        self._lock = threading.RLock()
        
        # 启动清理线程
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_metrics, daemon=True)
        self._cleanup_thread.start()
    
    def record_request(self, metrics: RequestMetrics):
        """记录请求指标"""
        with self._lock:
            # 添加到历史记录
            self.metrics_history.append(metrics)
            self.current_window_metrics.append(metrics)
            
            # 更新提供商统计
            provider_stat = self.provider_stats[metrics.provider]
            self._update_stats(provider_stat, metrics)
            
            # 更新模型统计
            model_stat = self.model_stats[metrics.model]
            self._update_stats(model_stat, metrics)
            
            logger.debug(f"记录请求指标: {metrics.provider.value}, 成功: {metrics.success}, 延迟: {metrics.latency:.2f}s")
    
    def _update_stats(self, stats: ProviderStats, metrics: RequestMetrics):
        """更新统计数据"""
        stats.total_requests += 1
        stats.last_request_time = metrics.timestamp
        
        if metrics.success:
            stats.successful_requests += 1
            stats.total_latency += metrics.latency
            stats.total_tokens += metrics.total_tokens
            stats.total_prompt_tokens += metrics.prompt_tokens
            stats.total_completion_tokens += metrics.completion_tokens
        else:
            stats.failed_requests += 1
            if metrics.error_type:
                stats.error_counts[metrics.error_type] += 1
    
    def get_provider_stats(self, provider: LLMProvider) -> ProviderStats:
        """获取提供商统计"""
        with self._lock:
            return self.provider_stats[provider]
    
    def get_model_stats(self, model: str) -> ProviderStats:
        """获取模型统计"""
        with self._lock:
            return self.model_stats[model]
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """获取总体统计"""
        with self._lock:
            total_requests = sum(stats.total_requests for stats in self.provider_stats.values())
            total_successful = sum(stats.successful_requests for stats in self.provider_stats.values())
            total_failed = sum(stats.failed_requests for stats in self.provider_stats.values())
            total_latency = sum(stats.total_latency for stats in self.provider_stats.values())
            total_tokens = sum(stats.total_tokens for stats in self.provider_stats.values())
            
            return {
                'total_requests': total_requests,
                'successful_requests': total_successful,
                'failed_requests': total_failed,
                'success_rate': total_successful / total_requests if total_requests > 0 else 0.0,
                'average_latency': total_latency / total_successful if total_successful > 0 else 0.0,
                'total_tokens': total_tokens,
                'tokens_per_second': total_tokens / total_latency if total_latency > 0 else 0.0,
                'providers': {
                    provider.value: {
                        'total_requests': stats.total_requests,
                        'success_rate': stats.success_rate,
                        'average_latency': stats.average_latency,
                        'total_tokens': stats.total_tokens,
                        'tokens_per_second': stats.tokens_per_second,
                        'error_counts': dict(stats.error_counts)
                    }
                    for provider, stats in self.provider_stats.items()
                }
            }
    
    def get_window_stats(self, window_seconds: int = 300) -> Dict[str, Any]:
        """获取时间窗口内的统计"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        with self._lock:
            # 过滤时间窗口内的指标
            window_metrics = [m for m in self.current_window_metrics if m.timestamp >= cutoff_time]
            
            if not window_metrics:
                return {
                    'window_seconds': window_seconds,
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'success_rate': 0.0,
                    'average_latency': 0.0,
                    'requests_per_second': 0.0,
                    'tokens_per_second': 0.0
                }
            
            total_requests = len(window_metrics)
            successful_requests = sum(1 for m in window_metrics if m.success)
            failed_requests = total_requests - successful_requests
            total_latency = sum(m.latency for m in window_metrics if m.success)
            total_tokens = sum(m.total_tokens for m in window_metrics if m.success)
            
            return {
                'window_seconds': window_seconds,
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': successful_requests / total_requests if total_requests > 0 else 0.0,
                'average_latency': total_latency / successful_requests if successful_requests > 0 else 0.0,
                'requests_per_second': total_requests / window_seconds,
                'tokens_per_second': total_tokens / window_seconds if window_seconds > 0 else 0.0
            }
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """获取错误分析"""
        with self._lock:
            all_errors = defaultdict(int)
            provider_errors = defaultdict(lambda: defaultdict(int))
            
            for provider, stats in self.provider_stats.items():
                for error_type, count in stats.error_counts.items():
                    all_errors[error_type] += count
                    provider_errors[provider.value][error_type] = count
            
            return {
                'total_errors': dict(all_errors),
                'provider_errors': {k: dict(v) for k, v in provider_errors.items()}
            }
    
    def _cleanup_old_metrics(self):
        """清理旧的指标数据"""
        while True:
            try:
                time.sleep(60)  # 每分钟清理一次
                current_time = time.time()
                cutoff_time = current_time - self.window_size
                
                with self._lock:
                    # 清理当前窗口指标
                    while (self.current_window_metrics and 
                           self.current_window_metrics[0].timestamp < cutoff_time):
                        self.current_window_metrics.popleft()
                
            except Exception as e:
                logger.error(f"清理指标数据时出错: {e}")
    
    def export_metrics(self, format_type: str = 'json') -> str:
        """导出指标数据"""
        stats = self.get_overall_stats()
        window_stats = self.get_window_stats()
        error_analysis = self.get_error_analysis()
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_stats': stats,
            'window_stats': window_stats,
            'error_analysis': error_analysis
        }
        
        if format_type == 'json':
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的导出格式: {format_type}")
    
    def reset_stats(self):
        """重置统计数据"""
        with self._lock:
            self.metrics_history.clear()
            self.current_window_metrics.clear()
            self.provider_stats.clear()
            self.model_stats.clear()
            logger.info("指标统计已重置")


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, slow_request_threshold: float = 5.0):
        self.slow_request_threshold = slow_request_threshold
        self.metrics_collector = MetricsCollector()
        
        # 性能警报
        self.alerts: List[Dict[str, Any]] = []
        self.max_alerts = 100
    
    def record_request(self, provider: LLMProvider, model: str, 
                      response: LLMResponse, latency: float, 
                      request_id: Optional[str] = None):
        """记录请求性能"""
        metrics = RequestMetrics(
            timestamp=time.time(),
            provider=provider,
            model=model,
            success=response.success,
            latency=latency,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            error_type=response.error_type if not response.success else None,
            error_message=response.error_message if not response.success else None,
            request_id=request_id
        )
        
        self.metrics_collector.record_request(metrics)
        
        # 检查慢请求
        if response.success and latency > self.slow_request_threshold:
            self._add_alert({
                'type': 'slow_request',
                'timestamp': time.time(),
                'provider': provider.value,
                'model': model,
                'latency': latency,
                'threshold': self.slow_request_threshold,
                'request_id': request_id
            })
        
        # 检查失败请求
        if not response.success:
            self._add_alert({
                'type': 'request_failed',
                'timestamp': time.time(),
                'provider': provider.value,
                'model': model,
                'error_type': response.error_type,
                'error_message': response.error_message,
                'request_id': request_id
            })
    
    def _add_alert(self, alert: Dict[str, Any]):
        """添加警报"""
        self.alerts.append(alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop(0)
        
        logger.warning(f"性能警报: {alert}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        window_stats = self.metrics_collector.get_window_stats(300)  # 5分钟窗口
        overall_stats = self.metrics_collector.get_overall_stats()
        
        # 计算健康分数
        health_score = 100.0
        
        # 成功率影响
        success_rate = window_stats.get('success_rate', 0.0)
        if success_rate < 0.95:
            health_score -= (0.95 - success_rate) * 100
        
        # 平均延迟影响
        avg_latency = window_stats.get('average_latency', 0.0)
        if avg_latency > self.slow_request_threshold:
            health_score -= min(50, (avg_latency - self.slow_request_threshold) * 10)
        
        # 确保健康分数在0-100之间
        health_score = max(0.0, min(100.0, health_score))
        
        # 确定健康状态
        if health_score >= 90:
            status = 'healthy'
        elif health_score >= 70:
            status = 'warning'
        else:
            status = 'critical'
        
        return {
            'status': status,
            'health_score': health_score,
            'window_stats': window_stats,
            'recent_alerts': self.alerts[-10:],  # 最近10个警报
            'provider_status': {
                provider.value: {
                    'success_rate': stats.success_rate,
                    'average_latency': stats.average_latency,
                    'total_requests': stats.total_requests,
                    'last_request_time': stats.last_request_time
                }
                for provider, stats in self.metrics_collector.provider_stats.items()
            }
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'health_status': self.get_health_status(),
            'overall_stats': self.metrics_collector.get_overall_stats(),
            'window_stats': {
                '5min': self.metrics_collector.get_window_stats(300),
                '15min': self.metrics_collector.get_window_stats(900),
                '1hour': self.metrics_collector.get_window_stats(3600)
            },
            'error_analysis': self.metrics_collector.get_error_analysis(),
            'alerts_summary': {
                'total_alerts': len(self.alerts),
                'recent_alerts': self.alerts[-20:]
            }
        }


# 全局监控器实例
_global_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def record_llm_request(provider: LLMProvider, model: str, 
                      response_time: float, success: bool,
                      response: Optional[LLMResponse] = None,
                      request_id: Optional[str] = None):
    """记录LLM请求（便捷函数）"""
    monitor = get_performance_monitor()
    if response:
        monitor.record_request(provider, model, response, response_time, request_id)
    else:
        # 创建一个简单的响应对象用于记录
        from .unified_interface import LLMResponse, LLMUsage
        dummy_response = LLMResponse(
            content="",
            model=model,
            provider=provider,
            usage=LLMUsage(),
            latency=response_time,
            success=success
        )
        monitor.record_request(provider, model, dummy_response, response_time, request_id)