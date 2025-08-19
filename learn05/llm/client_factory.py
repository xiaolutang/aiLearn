
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM客户端工厂模块
"""

from typing import Optional, Dict, Any
from llm.base import LLMInterface

class LLMClientFactory:
    """LLM客户端工厂类"""
    
    @staticmethod
    def create_client(provider: str = "openai", **kwargs) -> LLMInterface:
        """创建LLM客户端"""
        if provider == "openai":
            from llm.openai_client import OpenAIClient
            return OpenAIClient(**kwargs)
        else:
            raise ValueError(f"不支持的提供商: {provider}")
