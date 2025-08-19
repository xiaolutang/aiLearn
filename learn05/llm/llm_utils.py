
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM工具模块
"""

from typing import Dict, Any, List, Optional
import json
import time

def format_prompt(template: str, **kwargs) -> str:
    """格式化提示词模板"""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"模板参数缺失: {e}")

def validate_response(response: Dict[str, Any]) -> bool:
    """验证响应格式"""
    required_fields = ["content", "status"]
    return all(field in response for field in required_fields)

def parse_json_response(response_text: str) -> Dict[str, Any]:
    """解析JSON响应"""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "raw_text": response_text}

def calculate_tokens(text: str) -> int:
    """估算token数量"""
    # 简单估算：中文字符按2个token计算，英文单词按1个token计算
    chinese_chars = len([c for c in text if '一' <= c <= '鿿'])
    english_words = len(text.split()) - chinese_chars
    return chinese_chars * 2 + english_words

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """带退避的重试装饰器"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
    return wrapper

class TokenCounter:
    """Token计数器"""
    
    def __init__(self):
        self.total_tokens = 0
        self.request_count = 0
    
    def add_tokens(self, count: int):
        """添加token数量"""
        self.total_tokens += count
        self.request_count += 1
    
    def get_average(self) -> float:
        """获取平均token数"""
        return self.total_tokens / self.request_count if self.request_count > 0 else 0
    
    def reset(self):
        """重置计数器"""
        self.total_tokens = 0
        self.request_count = 0


def format_messages(messages):
    """格式化消息列表"""
    if not messages:
        return []
    
    formatted = []
    for msg in messages:
        if isinstance(msg, dict):
            formatted.append(msg)
        elif isinstance(msg, str):
            formatted.append({"role": "user", "content": msg})
        else:
            formatted.append({"role": "user", "content": str(msg)})
    
    return formatted

def extract_content(response):
    """从响应中提取内容"""
    if isinstance(response, dict):
        return response.get("content", response.get("message", str(response)))
    return str(response)

def handle_api_error(error):
    """处理API错误"""
    error_info = {
        "type": type(error).__name__,
        "message": str(error),
        "timestamp": time.time()
    }
    return error_info

def handle_llm_error(error):
    """处理LLM错误"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": time.time(),
        "retry_suggested": True
    }
    return error_info
