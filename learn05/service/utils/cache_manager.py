# -*- coding: utf-8 -*-
"""
缓存管理器

提供统一的缓存接口，支持Redis和内存缓存，包含性能优化功能。
"""

import json
import pickle
import gzip
import hashlib
import logging
import asyncio
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
from contextlib import asynccontextmanager

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False
    msgpack = None

from ..config.cache_config import CacheConfig, CacheType, get_cache_config, get_key_generator

logger = logging.getLogger(__name__)


class CacheMetrics:
    """缓存指标收集器"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0
        self.total_time = 0.0
        self.start_time = datetime.now()
    
    def record_hit(self, duration: float = 0.0):
        """记录缓存命中"""
        self.hits += 1
        self.total_time += duration
    
    def record_miss(self, duration: float = 0.0):
        """记录缓存未命中"""
        self.misses += 1
        self.total_time += duration
    
    def record_set(self, duration: float = 0.0):
        """记录缓存设置"""
        self.sets += 1
        self.total_time += duration
    
    def record_delete(self, duration: float = 0.0):
        """记录缓存删除"""
        self.deletes += 1
        self.total_time += duration
    
    def record_error(self):
        """记录缓存错误"""
        self.errors += 1
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def avg_response_time(self) -> float:
        """平均响应时间"""
        total_ops = self.hits + self.misses + self.sets + self.deletes
        return self.total_time / total_ops if total_ops > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "hit_rate": self.hit_rate,
            "avg_response_time": self.avg_response_time,
            "uptime_seconds": uptime
        }


class Serializer:
    """序列化器"""
    
    def __init__(self, format_type: str = "pickle", enable_compression: bool = True, compression_threshold: int = 1024):
        self.format_type = format_type
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold
    
    def serialize(self, data: Any) -> bytes:
        """序列化数据"""
        try:
            if self.format_type == "json":
                serialized = json.dumps(data, default=str).encode('utf-8')
            elif self.format_type == "msgpack" and MSGPACK_AVAILABLE:
                serialized = msgpack.packb(data)
            else:  # pickle
                serialized = pickle.dumps(data)
            
            # 压缩处理
            if self.enable_compression and len(serialized) > self.compression_threshold:
                serialized = gzip.compress(serialized)
                # 添加压缩标记
                serialized = b'\x01' + serialized
            else:
                # 添加未压缩标记
                serialized = b'\x00' + serialized
            
            return serialized
        
        except Exception as e:
            logger.error(f"序列化失败: {e}")
            raise
    
    def deserialize(self, data: bytes) -> Any:
        """反序列化数据"""
        try:
            if not data:
                return None
            
            # 检查压缩标记
            is_compressed = data[0] == 1
            data = data[1:]
            
            # 解压缩
            if is_compressed:
                data = gzip.decompress(data)
            
            # 反序列化
            if self.format_type == "json":
                return json.loads(data.decode('utf-8'))
            elif self.format_type == "msgpack" and MSGPACK_AVAILABLE:
                return msgpack.unpackb(data)
            else:  # pickle
                return pickle.loads(data)
        
        except Exception as e:
            logger.error(f"反序列化失败: {e}")
            return None


class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, datetime] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # 检查过期时间
        if entry['expires_at'] and datetime.now() > entry['expires_at']:
            await self.delete(key)
            return None
        
        # 更新访问时间
        self._access_times[key] = datetime.now()
        return entry['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            # 检查容量限制
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()
            
            ttl = ttl or self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
            
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            self._access_times[key] = datetime.now()
            
            return True
        
        except Exception as e:
            logger.error(f"内存缓存设置失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]
        return True
    
    async def clear(self) -> bool:
        """清空缓存"""
        self._cache.clear()
        self._access_times.clear()
        return True
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return key in self._cache
    
    async def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)
    
    async def _evict_lru(self):
        """LRU淘汰策略"""
        if not self._access_times:
            return
        
        # 找到最久未访问的键
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        await self.delete(lru_key)


class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._redis: Optional[redis.Redis] = None
        self.serializer = Serializer(
            config.serialization_format,
            config.enable_compression,
            config.compression_threshold
        )
    
    async def connect(self):
        """连接Redis"""
        if not REDIS_AVAILABLE:
            raise ImportError("Redis库未安装，请安装: pip install redis")
        
        try:
            if self.config.enable_cluster:
                from redis.asyncio.cluster import RedisCluster
                self._redis = RedisCluster(
                    startup_nodes=self.config.cluster_nodes,
                    skip_full_coverage_check=self.config.cluster_skip_full_coverage_check,
                    decode_responses=False
                )
            else:
                self._redis = redis.from_url(
                    self.config.redis_url,
                    max_connections=self.config.redis_max_connections,
                    socket_timeout=self.config.redis_socket_timeout,
                    socket_connect_timeout=self.config.redis_connection_timeout,
                    socket_keepalive=self.config.redis_socket_keepalive,
                    socket_keepalive_options=self.config.redis_socket_keepalive_options,
                    decode_responses=False
                )
            
            # 测试连接
            await self._redis.ping()
            logger.info("Redis连接成功")
        
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开Redis连接"""
        if self._redis:
            await self._redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            if not self._redis:
                await self.connect()
            
            data = await self._redis.get(key)
            if data is None:
                return None
            
            return self.serializer.deserialize(data)
        
        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            if not self._redis:
                await self.connect()
            
            data = self.serializer.serialize(value)
            ttl = ttl or self.config.default_ttl
            
            if ttl > 0:
                return await self._redis.setex(key, ttl, data)
            else:
                return await self._redis.set(key, data)
        
        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            if not self._redis:
                await self.connect()
            
            return bool(await self._redis.delete(key))
        
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        try:
            if not self._redis:
                await self.connect()
            
            return await self._redis.flushdb()
        
        except Exception as e:
            logger.error(f"Redis清空失败: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            if not self._redis:
                await self.connect()
            
            return bool(await self._redis.exists(key))
        
        except Exception as e:
            logger.error(f"Redis检查存在失败: {e}")
            return False
    
    async def size(self) -> int:
        """获取缓存大小"""
        try:
            if not self._redis:
                await self.connect()
            
            return await self._redis.dbsize()
        
        except Exception as e:
            logger.error(f"Redis获取大小失败: {e}")
            return 0
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的键"""
        try:
            if not self._redis:
                await self.connect()
            
            keys = await self._redis.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        
        except Exception as e:
            logger.error(f"Redis获取键失败: {e}")
            return []


class CacheManager:
    """统一缓存管理器"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or get_cache_config()
        self.key_generator = get_key_generator()
        self.metrics = CacheMetrics()
        
        # 初始化缓存后端
        if self.config.cache_type == CacheType.REDIS:
            self._cache = RedisCache(self.config)
        elif self.config.cache_type == CacheType.MEMORY:
            self._cache = MemoryCache(self.config.max_memory_size, self.config.default_ttl)
        else:  # HYBRID
            self._memory_cache = MemoryCache(self.config.max_memory_size // 2, self.config.default_ttl)
            self._redis_cache = RedisCache(self.config)
            self._cache = self._redis_cache  # 默认使用Redis
    
    async def initialize(self):
        """初始化缓存管理器"""
        if isinstance(self._cache, RedisCache):
            await self._cache.connect()
        
        if hasattr(self, '_redis_cache'):
            await self._redis_cache.connect()
    
    async def close(self):
        """关闭缓存管理器"""
        if isinstance(self._cache, RedisCache):
            await self._cache.disconnect()
        
        if hasattr(self, '_redis_cache'):
            await self._redis_cache.disconnect()
    
    @asynccontextmanager
    async def _measure_time(self, operation: str):
        """测量操作时间"""
        start_time = asyncio.get_event_loop().time()
        try:
            yield
        finally:
            duration = asyncio.get_event_loop().time() - start_time
            if operation == "get":
                self.metrics.record_hit(duration)
            elif operation == "set":
                self.metrics.record_set(duration)
            elif operation == "delete":
                self.metrics.record_delete(duration)
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.config.enabled:
            return None
        
        try:
            async with self._measure_time("get"):
                # 混合缓存策略：先查内存，再查Redis
                if self.config.cache_type == CacheType.HYBRID:
                    value = await self._memory_cache.get(key)
                    if value is not None:
                        return value
                    
                    value = await self._redis_cache.get(key)
                    if value is not None:
                        # 回写到内存缓存
                        await self._memory_cache.set(key, value, self.config.default_ttl // 2)
                    return value
                else:
                    return await self._cache.get(key)
        
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            self.metrics.record_error()
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.config.enabled:
            return False
        
        try:
            async with self._measure_time("set"):
                if self.config.cache_type == CacheType.HYBRID:
                    # 同时写入内存和Redis
                    memory_result = await self._memory_cache.set(key, value, ttl)
                    redis_result = await self._redis_cache.set(key, value, ttl)
                    return memory_result and redis_result
                else:
                    return await self._cache.set(key, value, ttl)
        
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
            self.metrics.record_error()
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if not self.config.enabled:
            return False
        
        try:
            async with self._measure_time("delete"):
                if self.config.cache_type == CacheType.HYBRID:
                    memory_result = await self._memory_cache.delete(key)
                    redis_result = await self._redis_cache.delete(key)
                    return memory_result or redis_result
                else:
                    return await self._cache.delete(key)
        
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
            self.metrics.record_error()
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        if not self.config.enabled:
            return False
        
        try:
            if self.config.cache_type == CacheType.HYBRID:
                memory_result = await self._memory_cache.clear()
                redis_result = await self._redis_cache.clear()
                return memory_result and redis_result
            else:
                return await self._cache.clear()
        
        except Exception as e:
            logger.error(f"缓存清空失败: {e}")
            self.metrics.record_error()
            return False
    
    async def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """获取缓存值，如果不存在则调用函数并缓存结果"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # 调用函数获取值
        if asyncio.iscoroutinefunction(func):
            value = await func(*args, **kwargs)
        else:
            value = func(*args, **kwargs)
        
        # 缓存结果
        if value is not None:
            await self.set(key, value, ttl)
        
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return self.metrics.get_stats()
    
    def generate_hash_key(self, *args, **kwargs) -> str:
        """生成哈希键"""
        content = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(content.encode()).hexdigest()


# 全局缓存管理器实例
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()
    return _cache_manager


def cache_result(ttl: int = 3600, key_pattern: Optional[str] = None):
    """缓存结果装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_manager = await get_cache_manager()
            
            # 生成缓存键
            if key_pattern:
                # 使用模式生成键
                key = key_pattern.format(*args, **kwargs)
            else:
                # 使用函数名和参数哈希生成键
                hash_key = cache_manager.generate_hash_key(*args, **kwargs)
                key = f"{func.__name__}:{hash_key}"
            
            return await cache_manager.get_or_set(key, func, ttl, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 对于同步函数，需要在异步上下文中运行
            return asyncio.create_task(async_wrapper(*args, **kwargs))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator