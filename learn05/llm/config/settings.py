#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置模块
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class ServiceMode(Enum):
    """服务模式枚举"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class LLMSettings:
    """LLM设置类"""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMSettings':
        """从字典创建"""
        return cls(
            model=data.get("model", "gpt-3.5-turbo"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 1000),
            api_key=data.get("api_key"),
            base_url=data.get("base_url"),
            timeout=data.get("timeout", 30)
        )

DEFAULT_SETTINGS = {
    "llm": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000
    },
    "database": {
        "host": "localhost",
        "port": 3306,
        "name": "test_db"
    },
    "cache": {
        "enabled": True,
        "ttl": 3600
    }
}

ENVIRONMENT_SETTINGS = {
    "development": DEFAULT_SETTINGS,
    "production": DEFAULT_SETTINGS,
    "testing": DEFAULT_SETTINGS
}

def load_environment_config(env: str = "development"):
    """加载环境配置"""
    return ENVIRONMENT_SETTINGS.get(env, DEFAULT_SETTINGS)

def validate_config(config: dict) -> bool:
    """验证配置"""
    required_keys = ["llm", "database", "cache"]
    return all(key in config for key in required_keys)
