# -*- coding: utf-8 -*-
"""
缓存管理模块
实现多种缓存策略和缓存管理功能
"""

import time
import json
import hashlib
import threading
from typing import Any, Dict, List, Optional, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
import pickle
import logging

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """缓存配置"""
    max_size: int = 1000
    ttl_seconds: int = 3600  # 1小时
    cleanup_interval: int = 300  # 5分钟
    enable_compression: bool = False
    enable_encryption: bool = False
    persistence_file: Optional[str] = None
    redis_url: Optional[str] = None
    redis_db: int = 0

@dataclass
class CacheItem:
    """缓存项"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    
    def __post_init__(self):
        if isinstance(self.value, (str, bytes)):
            self.size_bytes = len(self.value)
        else:
            try:
                self.size_bytes = len(pickle.dumps(self.value))
            except:
                self.size_bytes = 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl_seconds is None:
            return False
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry_time
    
    def access(self):
        """记录访问"""
        self.accessed_at = datetime.now()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'access_count': self.access_count,
            'ttl_seconds': self.ttl_seconds,
            'size_bytes': self.size_bytes
        }

class CacheStrategy(ABC):
    """缓存策略抽象基类"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._lock = threading.RLock()
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """获取缓存大小"""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """获取所有键"""
        pass
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        if isinstance(key, str):
            return hashlib.md5(key.encode('utf-8')).hexdigest()
        return str(key)
    
    def _serialize_value(self, value: Any) -> bytes:
        """序列化值"""
        try:
            return pickle.dumps(value)
        except Exception as e:
            logger.error(f"序列化失败: {e}")
            return b''
    
    def _deserialize_value(self, data: bytes) -> Any:
        """反序列化值"""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"反序列化失败: {e}")
            return None

class MemoryCache(CacheStrategy):
    """内存缓存策略"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache: Dict[str, CacheItem] = {}
        self._last_cleanup = time.time()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            self._cleanup_if_needed()
            
            cache_key = self._generate_key(key)
            item = self._cache.get(cache_key)
            
            if item is None:
                return None
            
            if item.is_expired():
                del self._cache[cache_key]
                return None
            
            item.access()
            return item.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                ttl = ttl or self.config.ttl_seconds
                
                item = CacheItem(
                    key=cache_key,
                    value=value,
                    created_at=datetime.now(),
                    accessed_at=datetime.now(),
                    ttl_seconds=ttl
                )
                
                # 检查缓存大小限制
                if len(self._cache) >= self.config.max_size:
                    self._evict_items()
                
                self._cache[cache_key] = item
                return True
                
            except Exception as e:
                logger.error(f"设置缓存失败: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            cache_key = self._generate_key(key)
            if cache_key in self._cache:
                del self._cache[cache_key]
                return True
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            return True
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        with self._lock:
            cache_key = self._generate_key(key)
            item = self._cache.get(cache_key)
            
            if item is None:
                return False
            
            if item.is_expired():
                del self._cache[cache_key]
                return False
            
            return True
    
    def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> List[str]:
        """获取所有键"""
        with self._lock:
            return list(self._cache.keys())
    
    def _cleanup_if_needed(self):
        """按需清理过期项"""
        current_time = time.time()
        if current_time - self._last_cleanup > self.config.cleanup_interval:
            self._cleanup_expired()
            self._last_cleanup = current_time
    
    def _cleanup_expired(self):
        """清理过期项"""
        expired_keys = []
        for key, item in self._cache.items():
            if item.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")
    
    def _evict_items(self):
        """驱逐缓存项（LRU策略）"""
        if not self._cache:
            return
        
        # 按访问时间排序，删除最久未访问的项
        sorted_items = sorted(
            self._cache.items(),
            key=lambda x: x[1].accessed_at
        )
        
        # 删除最旧的25%项目
        evict_count = max(1, len(sorted_items) // 4)
        for i in range(evict_count):
            key, _ = sorted_items[i]
            del self._cache[key]
        
        logger.info(f"驱逐了 {evict_count} 个缓存项")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_size = sum(item.size_bytes for item in self._cache.values())
            total_accesses = sum(item.access_count for item in self._cache.values())
            
            return {
                'total_items': len(self._cache),
                'total_size_bytes': total_size,
                'total_accesses': total_accesses,
                'max_size': self.config.max_size,
                'hit_rate': 0.0  # 需要额外跟踪命中率
            }

class LRUCache(CacheStrategy):
    """LRU缓存策略"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache: OrderedDict[str, CacheItem] = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            cache_key = self._generate_key(key)
            
            if cache_key not in self._cache:
                return None
            
            item = self._cache[cache_key]
            
            if item.is_expired():
                del self._cache[cache_key]
                return None
            
            # 移动到末尾（最近使用）
            self._cache.move_to_end(cache_key)
            item.access()
            
            return item.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                ttl = ttl or self.config.ttl_seconds
                
                item = CacheItem(
                    key=cache_key,
                    value=value,
                    created_at=datetime.now(),
                    accessed_at=datetime.now(),
                    ttl_seconds=ttl
                )
                
                # 如果键已存在，更新并移动到末尾
                if cache_key in self._cache:
                    self._cache[cache_key] = item
                    self._cache.move_to_end(cache_key)
                else:
                    # 检查大小限制
                    if len(self._cache) >= self.config.max_size:
                        # 删除最久未使用的项（第一个）
                        self._cache.popitem(last=False)
                    
                    self._cache[cache_key] = item
                
                return True
                
            except Exception as e:
                logger.error(f"设置LRU缓存失败: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            cache_key = self._generate_key(key)
            if cache_key in self._cache:
                del self._cache[cache_key]
                return True
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            return True
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        with self._lock:
            cache_key = self._generate_key(key)
            item = self._cache.get(cache_key)
            
            if item is None:
                return False
            
            if item.is_expired():
                del self._cache[cache_key]
                return False
            
            return True
    
    def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> List[str]:
        """获取所有键"""
        with self._lock:
            return list(self._cache.keys())

class TTLCache(CacheStrategy):
    """TTL缓存策略"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache: Dict[str, CacheItem] = {}
        self._expiry_times: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            cache_key = self._generate_key(key)
            
            if cache_key not in self._cache:
                return None
            
            # 检查是否过期
            if self._is_expired(cache_key):
                self._remove_expired_item(cache_key)
                return None
            
            item = self._cache[cache_key]
            item.access()
            
            return item.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                ttl = ttl or self.config.ttl_seconds
                
                item = CacheItem(
                    key=cache_key,
                    value=value,
                    created_at=datetime.now(),
                    accessed_at=datetime.now(),
                    ttl_seconds=ttl
                )
                
                # 设置过期时间
                expiry_time = datetime.now() + timedelta(seconds=ttl)
                
                self._cache[cache_key] = item
                self._expiry_times[cache_key] = expiry_time
                
                # 清理过期项
                self._cleanup_expired()
                
                return True
                
            except Exception as e:
                logger.error(f"设置TTL缓存失败: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            cache_key = self._generate_key(key)
            if cache_key in self._cache:
                self._remove_expired_item(cache_key)
                return True
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._expiry_times.clear()
            return True
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        with self._lock:
            cache_key = self._generate_key(key)
            
            if cache_key not in self._cache:
                return False
            
            if self._is_expired(cache_key):
                self._remove_expired_item(cache_key)
                return False
            
            return True
    
    def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> List[str]:
        """获取所有键"""
        with self._lock:
            return list(self._cache.keys())
    
    def _is_expired(self, cache_key: str) -> bool:
        """检查是否过期"""
        expiry_time = self._expiry_times.get(cache_key)
        if expiry_time is None:
            return True
        
        return datetime.now() > expiry_time
    
    def _remove_expired_item(self, cache_key: str):
        """移除过期项"""
        self._cache.pop(cache_key, None)
        self._expiry_times.pop(cache_key, None)
    
    def _cleanup_expired(self):
        """清理所有过期项"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, expiry_time in self._expiry_times.items():
            if current_time > expiry_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_expired_item(key)

class RedisCache(CacheStrategy):
    """Redis缓存策略"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._redis = None
        self._connect_redis()
    
    def _connect_redis(self):
        """连接Redis"""
        try:
            import redis
            
            if self.config.redis_url:
                self._redis = redis.from_url(
                    self.config.redis_url,
                    db=self.config.redis_db,
                    decode_responses=False
                )
            else:
                self._redis = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=self.config.redis_db,
                    decode_responses=False
                )
            
            # 测试连接
            self._redis.ping()
            logger.info("Redis连接成功")
            
        except ImportError:
            logger.error("Redis库未安装，请安装: pip install redis")
            raise
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            cache_key = self._generate_key(key)
            data = self._redis.get(cache_key)
            
            if data is None:
                return None
            
            return self._deserialize_value(data)
            
        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            cache_key = self._generate_key(key)
            data = self._serialize_value(value)
            ttl = ttl or self.config.ttl_seconds
            
            return self._redis.setex(cache_key, ttl, data)
            
        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        try:
            cache_key = self._generate_key(key)
            return bool(self._redis.delete(cache_key))
            
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            return self._redis.flushdb()
            
        except Exception as e:
            logger.error(f"Redis清空失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            cache_key = self._generate_key(key)
            return bool(self._redis.exists(cache_key))
            
        except Exception as e:
            logger.error(f"Redis检查存在失败: {e}")
            return False
    
    def size(self) -> int:
        """获取缓存大小"""
        try:
            return self._redis.dbsize()
            
        except Exception as e:
            logger.error(f"Redis获取大小失败: {e}")
            return 0
    
    def keys(self) -> List[str]:
        """获取所有键"""
        try:
            return [key.decode('utf-8') for key in self._redis.keys()]
            
        except Exception as e:
            logger.error(f"Redis获取键失败: {e}")
            return []

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, strategy: str = 'memory', config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.strategy = self._create_strategy(strategy)
        self._hit_count = 0
        self._miss_count = 0
        self._lock = threading.RLock()
    
    def _create_strategy(self, strategy_name: str) -> CacheStrategy:
        """创建缓存策略"""
        strategies = {
            'memory': MemoryCache,
            'lru': LRUCache,
            'ttl': TTLCache,
            'redis': RedisCache
        }
        
        if strategy_name not in strategies:
            raise ValueError(f"不支持的缓存策略: {strategy_name}")
        
        return strategies[strategy_name](self.config)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            value = self.strategy.get(key)
            
            if value is not None:
                self._hit_count += 1
            else:
                self._miss_count += 1
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        return self.strategy.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        return self.strategy.delete(key)
    
    def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            self._hit_count = 0
            self._miss_count = 0
            return self.strategy.clear()
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self.strategy.exists(key)
    
    def size(self) -> int:
        """获取缓存大小"""
        return self.strategy.size()
    
    def keys(self) -> List[str]:
        """获取所有键"""
        return self.strategy.keys()
    
    def get_hit_rate(self) -> float:
        """获取命中率"""
        with self._lock:
            total = self._hit_count + self._miss_count
            if total == 0:
                return 0.0
            return self._hit_count / total
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            stats = {
                'hit_count': self._hit_count,
                'miss_count': self._miss_count,
                'hit_rate': self.get_hit_rate(),
                'cache_size': self.size(),
                'max_size': self.config.max_size
            }
            
            # 如果策略支持，添加详细统计
            if hasattr(self.strategy, 'get_statistics'):
                strategy_stats = self.strategy.get_statistics()
                stats.update(strategy_stats)
            
            return stats
    
    def reset_statistics(self):
        """重置统计信息"""
        with self._lock:
            self._hit_count = 0
            self._miss_count = 0
    
    def cache_decorator(self, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
        """缓存装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
                
                # 尝试从缓存获取
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # 执行函数并缓存结果
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator

# 全局缓存实例
_global_cache_manager = None

def get_global_cache() -> CacheManager:
    """获取全局缓存管理器"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager

def set_global_cache(cache_manager: CacheManager):
    """设置全局缓存管理器"""
    global _global_cache_manager
    _global_cache_manager = cache_manager

# 便捷装饰器
def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """缓存装饰器（使用全局缓存）"""
    return get_global_cache().cache_decorator(ttl, key_func)