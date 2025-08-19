# -*- coding: utf-8 -*-
"""
重试处理器组件
提供对大模型API调用失败的重试处理功能
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar
from abc import ABC, abstractmethod
import functools
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryHandler(ABC):
    """重试处理器抽象基类"""
    
    @abstractmethod
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """判断是否应该重试
        
        Args:
            attempt: 当前尝试次数
            exception: 异常对象
            
        Returns:
            bool: 是否应该重试
        """
        pass
    
    @abstractmethod
    def wait_time(self, attempt: int) -> float:
        """计算等待时间
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            float: 等待时间(秒)
        """
        pass
    
    def retry(self, func: Callable[..., T], *args, **kwargs) -> T:
        """执行函数并在需要时重试
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 关键字参数
            
        Returns:
            T: 函数返回值
        """
        attempt = 0
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if self.should_retry(attempt, e):
                    wait_time = self.wait_time(attempt)
                    logger.info(f"尝试 {attempt} 失败: {e}, 等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"重试次数已达上限，操作失败: {e}")
                    raise


class ExponentialBackoffRetryHandler(RetryHandler):
    """指数退避重试策略的实现"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 30.0, jitter: bool = True):
        """初始化指数退避重试处理器
        
        Args:
            max_attempts: 最大尝试次数
            base_delay: 基础延迟时间(秒)
            max_delay: 最大延迟时间(秒)
            jitter: 是否添加随机抖动
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        # 默认重试的状态码和异常类型
        self.retriable_status_codes = {
            429,  # Too Many Requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504   # Gateway Timeout
        }
        self.retriable_exceptions = (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError
        )
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """判断是否应该重试
        
        Args:
            attempt: 当前尝试次数
            exception: 异常对象
            
        Returns:
            bool: 是否应该重试
        """
        # 检查是否超过最大尝试次数
        if attempt > self.max_attempts:
            return False
        
        # 检查异常类型是否在可重试列表中
        if isinstance(exception, self.retriable_exceptions):
            # 对于HTTP错误，检查状态码
            if isinstance(exception, requests.exceptions.HTTPError) and hasattr(exception, 'response'):
                return exception.response.status_code in self.retriable_status_codes
            return True
        
        # 检查是否是特定于大模型API的可重试错误
        if hasattr(exception, 'error_type'):
            return exception.error_type in ('rate_limit', 'server_error', 'timeout')
        
        # 对于其他异常，默认不重试
        return False
    
    def wait_time(self, attempt: int) -> float:
        """计算等待时间(指数退避算法)
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            float: 等待时间(秒)
        """
        # 基础等待时间 = 基础延迟 * (2^(尝试次数-1))
        wait_time = self.base_delay * (2 ** (attempt - 1))
        
        # 限制最大等待时间
        wait_time = min(wait_time, self.max_delay)
        
        # 添加随机抖动(±10%)
        if self.jitter:
            jitter_factor = random.uniform(0.9, 1.1)
            wait_time *= jitter_factor
        
        return wait_time


class FixedIntervalRetryHandler(RetryHandler):
    """固定间隔重试策略的实现"""
    
    def __init__(self, max_attempts: int = 3, delay: float = 2.0):
        """初始化固定间隔重试处理器
        
        Args:
            max_attempts: 最大尝试次数
            delay: 固定延迟时间(秒)
        """
        self.max_attempts = max_attempts
        self.delay = delay
        # 默认使用与指数退避相同的可重试条件
        self.retriable_status_codes = {
            429, 500, 502, 503, 504
        }
        self.retriable_exceptions = (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError
        )
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """判断是否应该重试
        
        Args:
            attempt: 当前尝试次数
            exception: 异常对象
            
        Returns:
            bool: 是否应该重试
        """
        # 检查是否超过最大尝试次数
        if attempt > self.max_attempts:
            return False
        
        # 检查异常类型是否在可重试列表中
        if isinstance(exception, self.retriable_exceptions):
            # 对于HTTP错误，检查状态码
            if isinstance(exception, requests.exceptions.HTTPError) and hasattr(exception, 'response'):
                return exception.response.status_code in self.retriable_status_codes
            return True
        
        # 检查是否是特定于大模型API的可重试错误
        if hasattr(exception, 'error_type'):
            return exception.error_type in ('rate_limit', 'server_error', 'timeout')
        
        # 对于其他异常，默认不重试
        return False
    
    def wait_time(self, attempt: int) -> float:
        """计算等待时间(固定间隔)
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            float: 等待时间(秒)
        """
        return self.delay


class RandomIntervalRetryHandler(RetryHandler):
    """随机间隔重试策略的实现"""
    
    def __init__(self, max_attempts: int = 3, min_delay: float = 1.0, max_delay: float = 5.0):
        """初始化随机间隔重试处理器
        
        Args:
            max_attempts: 最大尝试次数
            min_delay: 最小延迟时间(秒)
            max_delay: 最大延迟时间(秒)
        """
        self.max_attempts = max_attempts
        self.min_delay = min_delay
        self.max_delay = max_delay
        # 默认使用与指数退避相同的可重试条件
        self.retriable_status_codes = {
            429, 500, 502, 503, 504
        }
        self.retriable_exceptions = (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError
        )
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """判断是否应该重试
        
        Args:
            attempt: 当前尝试次数
            exception: 异常对象
            
        Returns:
            bool: 是否应该重试
        """
        # 检查是否超过最大尝试次数
        if attempt > self.max_attempts:
            return False
        
        # 检查异常类型是否在可重试列表中
        if isinstance(exception, self.retriable_exceptions):
            # 对于HTTP错误，检查状态码
            if isinstance(exception, requests.exceptions.HTTPError) and hasattr(exception, 'response'):
                return exception.response.status_code in self.retriable_status_codes
            return True
        
        # 检查是否是特定于大模型API的可重试错误
        if hasattr(exception, 'error_type'):
            return exception.error_type in ('rate_limit', 'server_error', 'timeout')
        
        # 对于其他异常，默认不重试
        return False
    
    def wait_time(self, attempt: int) -> float:
        """计算等待时间(随机间隔)
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            float: 等待时间(秒)
        """
        return random.uniform(self.min_delay, self.max_delay)


class RetryHandlerFactory:
    """重试处理器工厂类
    用于创建不同类型的重试处理器
    """
    
    @staticmethod
    def create_exponential_backoff(max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 30.0, jitter: bool = True) -> ExponentialBackoffRetryHandler:
        """创建指数退避重试处理器
        
        Args:
            max_attempts: 最大尝试次数
            base_delay: 基础延迟时间(秒)
            max_delay: 最大延迟时间(秒)
            jitter: 是否添加随机抖动
            
        Returns:
            ExponentialBackoffRetryHandler: 指数退避重试处理器实例
        """
        logger.info(f"创建指数退避重试处理器: 最大尝试次数={max_attempts}, 基础延迟={base_delay}秒, 最大延迟={max_delay}秒, 抖动={jitter}")
        return ExponentialBackoffRetryHandler(max_attempts, base_delay, max_delay, jitter)
    
    @staticmethod
    def create_fixed_interval(max_attempts: int = 3, delay: float = 2.0) -> FixedIntervalRetryHandler:
        """创建固定间隔重试处理器
        
        Args:
            max_attempts: 最大尝试次数
            delay: 固定延迟时间(秒)
            
        Returns:
            FixedIntervalRetryHandler: 固定间隔重试处理器实例
        """
        logger.info(f"创建固定间隔重试处理器: 最大尝试次数={max_attempts}, 固定延迟={delay}秒")
        return FixedIntervalRetryHandler(max_attempts, delay)
    
    @staticmethod
    def create_random_interval(max_attempts: int = 3, min_delay: float = 1.0, max_delay: float = 5.0) -> RandomIntervalRetryHandler:
        """创建随机间隔重试处理器
        
        Args:
            max_attempts: 最大尝试次数
            min_delay: 最小延迟时间(秒)
            max_delay: 最大延迟时间(秒)
            
        Returns:
            RandomIntervalRetryHandler: 随机间隔重试处理器实例
        """
        logger.info(f"创建随机间隔重试处理器: 最大尝试次数={max_attempts}, 最小延迟={min_delay}秒, 最大延迟={max_delay}秒")
        return RandomIntervalRetryHandler(max_attempts, min_delay, max_delay)


def retry_decorator(retry_handler: RetryHandler = None):
    """重试装饰器
    
    Args:
        retry_handler: 重试处理器实例(可选，默认创建指数退避重试处理器)
        
    Returns:
        Callable: 装饰后的函数
    """
    if retry_handler is None:
        # 创建默认的指数退避重试处理器
        retry_handler = RetryHandlerFactory.create_exponential_backoff()
        
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return retry_handler.retry(func, *args, **kwargs)
        return wrapper
    
    return decorator


# 预定义的重试处理器配置
PRESET_RETRY_HANDLERS = {
    'default': {
        'type': 'exponential',
        'max_attempts': 3,
        'base_delay': 1.0,
        'max_delay': 30.0,
        'jitter': True
    },
    'aggressive': {
        'type': 'exponential',
        'max_attempts': 5,
        'base_delay': 0.5,
        'max_delay': 20.0,
        'jitter': True
    },
    'conservative': {
        'type': 'fixed',
        'max_attempts': 2,
        'delay': 3.0
    },
    'random': {
        'type': 'random',
        'max_attempts': 4,
        'min_delay': 1.0,
        'max_delay': 10.0
    }
}


def get_preset_retry_handler(preset_name: str) -> RetryHandler:
    """获取预定义的重试处理器
    
    Args:
        preset_name: 预定义配置名称
        
    Returns:
        RetryHandler: 重试处理器实例
    """
    if preset_name not in PRESET_RETRY_HANDLERS:
        raise ValueError(f"未知的预定义重试处理器配置: {preset_name}")
    
    config = PRESET_RETRY_HANDLERS[preset_name]
    factory = RetryHandlerFactory()
    
    if config['type'] == 'exponential':
        return factory.create_exponential_backoff(
            config['max_attempts'],
            config['base_delay'],
            config['max_delay'],
            config['jitter']
        )
    elif config['type'] == 'fixed':
        return factory.create_fixed_interval(
            config['max_attempts'],
            config['delay']
        )
    elif config['type'] == 'random':
        return factory.create_random_interval(
            config['max_attempts'],
            config['min_delay'],
            config['max_delay']
        )
    else:
        raise ValueError(f"不支持的重试处理器类型: {config['type']}")