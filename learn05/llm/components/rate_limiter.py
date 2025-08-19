# -*- coding: utf-8 -*-
"""
速率限制器组件
提供对大模型API调用的速率控制功能
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
import threading
from abc import ABC, abstractmethod
from collections import deque

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter(ABC):
    """速率限制器抽象基类"""
    
    @abstractmethod
    def acquire(self) -> bool:
        """尝试获取调用令牌
        
        Returns:
            bool: 是否成功获取令牌
        """
        pass
    
    @abstractmethod
    def wait(self) -> None:
        """等待直到可以获取令牌
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """重置速率限制器
        """
        pass


class TokenBucketRateLimiter(RateLimiter):
    """令牌桶算法的速率限制器实现"""
    
    def __init__(self, rate: float, capacity: int):
        """初始化令牌桶速率限制器
        
        Args:
            rate: 令牌生成速率(个/秒)
            capacity: 令牌桶容量
        """
        self.rate = rate  # 令牌生成速率
        self.capacity = capacity  # 令牌桶容量
        self.tokens = capacity  # 当前可用令牌数
        self.last_refill_time = time.time()  # 上次填充时间
        self.lock = threading.RLock()  # 可重入锁
    
    def _refill(self) -> None:
        """填充令牌桶
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_refill_time
        
        # 计算新增令牌数
        new_tokens = elapsed_time * self.rate
        if new_tokens > 0:
            # 更新令牌数和最后填充时间
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill_time = current_time
    
    def acquire(self) -> bool:
        """尝试获取调用令牌
        
        Returns:
            bool: 是否成功获取令牌
        """
        with self.lock:
            # 先填充令牌
            self._refill()
            
            # 检查是否有足够的令牌
            if self.tokens >= 1:
                # 消耗一个令牌
                self.tokens -= 1
                return True
            else:
                # 没有足够的令牌
                return False
    
    def wait(self) -> None:
        """等待直到可以获取令牌
        """
        with self.lock:
            # 先填充令牌
            self._refill()
            
            # 检查是否有足够的令牌
            if self.tokens >= 1:
                # 消耗一个令牌
                self.tokens -= 1
                return
            
            # 计算需要等待的时间
            time_needed = (1 - self.tokens) / self.rate
            logger.debug(f"速率限制: 需要等待 {time_needed:.2f} 秒")
        
        # 在锁外等待，避免阻塞其他线程
        time.sleep(time_needed)
        
        # 再次尝试获取令牌
        self.wait()
    
    def reset(self) -> None:
        """重置速率限制器
        """
        with self.lock:
            self.tokens = self.capacity
            self.last_refill_time = time.time()
            logger.info(f"重置速率限制器: 令牌桶已充满")


class WindowRateLimiter(RateLimiter):
    """滑动窗口算法的速率限制器实现"""
    
    def __init__(self, window_size: int, max_requests: int):
        """初始化滑动窗口速率限制器
        
        Args:
            window_size: 窗口大小(秒)
            max_requests: 窗口内最大请求数
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.request_times = deque()  # 请求时间队列
        self.lock = threading.RLock()  # 可重入锁
    
    def _clean_old_requests(self) -> None:
        """清理过期的请求记录
        """
        current_time = time.time()
        # 计算窗口的起始时间
        window_start = current_time - self.window_size
        
        # 移除所有过期的请求记录
        while self.request_times and self.request_times[0] < window_start:
            self.request_times.popleft()
    
    def acquire(self) -> bool:
        """尝试获取调用令牌
        
        Returns:
            bool: 是否成功获取令牌
        """
        with self.lock:
            # 清理过期请求
            self._clean_old_requests()
            
            # 检查请求数是否超过限制
            if len(self.request_times) < self.max_requests:
                # 记录新请求时间
                self.request_times.append(time.time())
                return True
            else:
                # 请求数超过限制
                return False
    
    def wait(self) -> None:
        """等待直到可以获取令牌
        """
        with self.lock:
            # 清理过期请求
            self._clean_old_requests()
            
            # 检查是否可以立即获取令牌
            if len(self.request_times) < self.max_requests:
                # 记录新请求时间
                self.request_times.append(time.time())
                return
            
            # 计算需要等待的时间
            # 获取队列中最早的请求时间
            earliest_request_time = self.request_times[0]
            # 计算该请求何时会过期
            time_needed = earliest_request_time + self.window_size - time.time()
            # 确保等待时间不为负数
            time_needed = max(0, time_needed)
            
            logger.debug(f"速率限制: 需要等待 {time_needed:.2f} 秒")
        
        # 在锁外等待，避免阻塞其他线程
        time.sleep(time_needed)
        
        # 再次尝试获取令牌
        self.wait()
    
    def reset(self) -> None:
        """重置速率限制器
        """
        with self.lock:
            self.request_times.clear()
            logger.info(f"重置速率限制器: 请求记录已清空")


class RateLimiterFactory:
    """速率限制器工厂类
    用于创建不同类型的速率限制器
    """
    
    @staticmethod
    def create_token_bucket(rate: float, capacity: int) -> TokenBucketRateLimiter:
        """创建令牌桶速率限制器
        
        Args:
            rate: 令牌生成速率(个/秒)
            capacity: 令牌桶容量
            
        Returns:
            TokenBucketRateLimiter: 令牌桶速率限制器实例
        """
        logger.info(f"创建令牌桶速率限制器: 速率={rate}/秒, 容量={capacity}")
        return TokenBucketRateLimiter(rate, capacity)
    
    @staticmethod
    def create_window(window_size: int, max_requests: int) -> WindowRateLimiter:
        """创建滑动窗口速率限制器
        
        Args:
            window_size: 窗口大小(秒)
            max_requests: 窗口内最大请求数
            
        Returns:
            WindowRateLimiter: 滑动窗口速率限制器实例
        """
        logger.info(f"创建滑动窗口速率限制器: 窗口大小={window_size}秒, 最大请求数={max_requests}")
        return WindowRateLimiter(window_size, max_requests)


class MultiLevelRateLimiter:
    """多级速率限制器
    支持同时应用多种速率限制策略
    """
    
    def __init__(self, limiters: List[RateLimiter]):
        """初始化多级速率限制器
        
        Args:
            limiters: 速率限制器列表
        """
        self.limiters = limiters
    
    def acquire(self) -> bool:
        """尝试获取所有速率限制器的调用令牌
        
        Returns:
            bool: 是否成功获取所有令牌
        """
        return all(limiter.acquire() for limiter in self.limiters)
    
    def wait(self) -> None:
        """等待直到可以获取所有令牌
        """
        # 依次等待每个速率限制器
        for limiter in self.limiters:
            limiter.wait()
    
    def reset(self) -> None:
        """重置所有速率限制器
        """
        for limiter in self.limiters:
            limiter.reset()


# 预定义的速率限制器配置
PRESET_RATE_LIMITERS = {
    'openai_free_tier': {
        'type': 'token_bucket',
        'rate': 3,
        'capacity': 20
    },
    'openai_paid_tier': {
        'type': 'token_bucket',
        'rate': 30,
        'capacity': 60
    },
    'tongyi_light': {
        'type': 'window',
        'window_size': 60,
        'max_requests': 60
    },
    'tongyi_pro': {
        'type': 'window',
        'window_size': 60,
        'max_requests': 300
    }
}


def get_preset_rate_limiter(preset_name: str) -> RateLimiter:
    """获取预定义的速率限制器
    
    Args:
        preset_name: 预定义配置名称
        
    Returns:
        RateLimiter: 速率限制器实例
    """
    if preset_name not in PRESET_RATE_LIMITERS:
        raise ValueError(f"未知的预定义速率限制器配置: {preset_name}")
    
    config = PRESET_RATE_LIMITERS[preset_name]
    factory = RateLimiterFactory()
    
    if config['type'] == 'token_bucket':
        return factory.create_token_bucket(config['rate'], config['capacity'])
    elif config['type'] == 'window':
        return factory.create_window(config['window_size'], config['max_requests'])
    else:
        raise ValueError(f"不支持的速率限制器类型: {config['type']}")