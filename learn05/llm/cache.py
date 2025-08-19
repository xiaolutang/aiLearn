
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存模块
"""

from typing import Any, Optional

class LLMCache:
    """LLM缓存类"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        self._cache[key] = value
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
