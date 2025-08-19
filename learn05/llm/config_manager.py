
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

from typing import Dict, Any

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置"""
        self._config[key] = value
