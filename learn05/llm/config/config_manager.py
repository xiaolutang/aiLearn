#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
"""

from typing import Dict, Any, Optional
import json
import os

class ConfigManager:
    """配置管理器"""
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.config = {}
        if config_file and os.path.exists(config_file):
            self.load_config()
    
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}
    
    def get_config(self, key: str = None, default=None):
        """获取配置值"""
        if key is None:
            return self.config
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value

class LLMConfig:
    """LLM配置"""
    def __init__(self, api_key: str = "", model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

class DatabaseConfig:
    """数据库配置"""
    def __init__(self, host: str = "localhost", port: int = 3306, database: str = "test"):
        self.host = host
        self.port = port
        self.database = database

class CacheConfig:
    """缓存配置"""
    def __init__(self, enabled: bool = True, ttl: int = 3600):
        self.enabled = enabled
        self.ttl = ttl

class AgentConfig:
    """智能体配置"""
    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout
