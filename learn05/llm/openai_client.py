# -*- coding: utf-8 -*-
"""
OpenAI大模型客户端实现
提供与OpenAI API的交互功能
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Union
import requests

from llm.base import LLMInterface, LLMRateLimiter, LLMRetryHandler
from config.core_config import get_llm_config, get_rate_limit_config, get_retry_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIRateLimiter(LLMRateLimiter):
    """OpenAI速率限制器实现"""
    
    def __init__(self, rate_limit_config: Optional[Dict[str, int]] = None):
        # 使用传入的配置或从全局配置获取
        self.rate_limit = rate_limit_config or get_rate_limit_config()
        
        # 最近调用记录，每个记录包含时间和使用的tokens
        self.recent_calls = []
    
    def check_rate_limit(self) -> None:
        """检查速率限制，如果超过限制则等待"""
        current_time = time.time()
        
        # 清理过期的调用记录（60秒前的记录）
        self.recent_calls = [call for call in self.recent_calls if call["time"] > current_time - 60]
        
        # 检查请求数量
        if len(self.recent_calls) >= self.rate_limit["requests_per_minute"]:
            wait_time = 60 - (current_time - self.recent_calls[0]["time"])
            logger.warning(f"OpenAI API速率限制，等待{wait_time:.2f}秒")
            time.sleep(wait_time)
    
    def record_request(self, tokens_used: int = 0) -> None:
        """记录请求信息"""
        self.recent_calls.append({
            "time": time.time(),
            "tokens_used": tokens_used
        })


class OpenAIRetryHandler(LLMRetryHandler):
    """OpenAI重试处理器实现"""
    
    def __init__(self, retry_config: Optional[Dict[str, Union[int, float]]] = None):
        # 使用传入的配置或从全局配置获取
        self.retry_config = retry_config or get_retry_config()
    
    def retry_request(self, func, *args, **kwargs) -> Any:
        """带重试机制的请求"""
        retries = 0
        delay = self.retry_config["retry_delay"]
        
        while retries < self.retry_config["max_retries"]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                
                # 检查是否需要重试
                if not self.handle_error(e):
                    raise
                
                logger.error(f"请求失败: {e}, 第{retries}次重试")
                
                if retries >= self.retry_config["max_retries"]:
                    raise
                
                time.sleep(delay)
                delay *= self.retry_config["backoff_factor"]
    
    def handle_error(self, error: Exception) -> bool:
        """处理错误，判断是否需要重试"""
        # 对于API超时、服务不可用等错误进行重试
        if isinstance(error, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
            return True
        
        # 对于速率限制错误进行重试
        if isinstance(error, requests.exceptions.HTTPError):
            if error.response.status_code in [429, 503]:  # 429: Too Many Requests, 503: Service Unavailable
                return True
        
        # 其他错误不重试
        return False


class OpenAIClient(LLMInterface):
    """OpenAI大模型客户端实现"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # 获取全局配置
        config = get_llm_config()
        
        # 使用传入的参数或从配置中获取
        self.api_key = api_key or config["api_key"]
        self.base_url = base_url or config["base_url"] or "https://api.openai.com/v1"
        
        if not self.api_key:
            logger.warning("OpenAI API密钥未设置")
        
        # 设置请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 初始化速率限制器和重试处理器
        self.rate_limiter = OpenAIRateLimiter()
        self.retry_handler = OpenAIRetryHandler()
    
    def generate(self, prompt: str, model: str = "gpt-3.5-turbo", **kwargs) -> str:
        """生成文本响应"""
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, model=model, **kwargs)
        
        # 提取响应内容
        if isinstance(response, dict) and "choices" in response:
            return response["choices"][0]["message"]["content"]
        
        # 如果响应是直接的字符串，直接返回
        if isinstance(response, str):
            return response
        
        # 默认返回空字符串
        return ""
    
    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", **kwargs) -> Dict[str, Any]:
        """进行对话"""
        # 检查速率限制
        self.rate_limiter.check_rate_limit()
        
        # 构造请求数据
        data = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        # 定义请求函数
        def make_request():
            url = f"{self.base_url}/chat/completions"
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        
        # 使用重试处理器发送请求
        result = self.retry_handler.retry_request(make_request)
        
        # 记录请求信息
        if "usage" in result and "total_tokens" in result["usage"]:
            self.rate_limiter.record_request(result["usage"]["total_tokens"])
        else:
            self.rate_limiter.record_request()
        
        return result
    
    def embedding(self, text: str, model: str = "text-embedding-ada-002", **kwargs) -> List[float]:
        """获取文本嵌入向量"""
        # 检查速率限制
        self.rate_limiter.check_rate_limit()
        
        # 构造请求数据
        data = {
            "model": model,
            "input": text,
            **kwargs
        }
        
        # 定义请求函数
        def make_request():
            url = f"{self.base_url}/embeddings"
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        
        # 使用重试处理器发送请求
        result = self.retry_handler.retry_request(make_request)
        
        # 记录请求信息
        if "usage" in result and "total_tokens" in result["usage"]:
            self.rate_limiter.record_request(result["usage"]["total_tokens"])
        else:
            self.rate_limiter.record_request()
        
        # 提取嵌入向量
        if isinstance(result, dict) and "data" in result and result["data"]:
            return result["data"][0]["embedding"]
        
        # 默认返回空列表
        return []
    
    def batch_generate(self, prompts: List[str], model: str = "gpt-3.5-turbo", **kwargs) -> List[str]:
        """批量生成文本响应"""
        results = []
        
        for prompt in prompts:
            # 为每个提示生成响应
            result = self.generate(prompt, model=model, **kwargs)
            results.append(result)
        
        return results