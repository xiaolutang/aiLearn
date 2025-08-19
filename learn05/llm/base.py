# -*- coding: utf-8 -*-
"""
大模型基础接口模块
定义大模型客户端的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union


class LLMInterface(ABC):
    """大模型接口抽象类"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本响应
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数
            
        Returns:
            str: 生成的文本响应
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """进行对话
        
        Args:
            messages: 对话消息列表，每个消息包含role和content
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 对话响应结果
        """
        pass
    
    @abstractmethod
    def embedding(self, text: str, **kwargs) -> List[float]:
        """获取文本嵌入向量
        
        Args:
            text: 输入文本
            **kwargs: 其他参数
            
        Returns:
            List[float]: 嵌入向量
        """
        pass
    
    @abstractmethod
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """批量生成文本响应
        
        Args:
            prompts: 提示文本列表
            **kwargs: 其他参数
            
        Returns:
            List[str]: 生成的文本响应列表
        """
        pass


class LLMRateLimiter(ABC):
    """大模型速率限制器抽象类"""
    
    @abstractmethod
    def check_rate_limit(self) -> None:
        """检查速率限制，如果超过限制则等待"""
        pass
    
    @abstractmethod
    def record_request(self, tokens_used: int = 0) -> None:
        """记录请求信息
        
        Args:
            tokens_used: 使用的token数量
        """
        pass


class LLMRetryHandler(ABC):
    """大模型重试处理器抽象类"""
    
    @abstractmethod
    def retry_request(self, func, *args, **kwargs) -> Any:
        """带重试机制的请求
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Any: 函数执行结果
        """
        pass
    
    @abstractmethod
    def handle_error(self, error: Exception) -> bool:
        """处理错误
        
        Args:
            error: 异常对象
            
        Returns:
            bool: 是否需要重试
        """
        pass