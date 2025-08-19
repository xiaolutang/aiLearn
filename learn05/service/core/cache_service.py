# -*- coding: utf-8 -*-
"""
缓存服务模块

本模块实现了Redis缓存管理功能，包括AI响应缓存、用户会话缓存等。
"""

import json
import pickle
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import asyncio

try:
    import redis.asyncio as redis
except ImportError:
    import redis
    redis.asyncio = redis

from .ai_service import AIResponse, AIProvider

logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 0):
        self.redis_url = redis_url
        self.db = db
        self.redis_client = None
        self.connection_pool = None
        self.is_connected = False
        
        # 缓存键前缀
        self.prefixes = {
            "ai": "ai:",
            "user": "user:",
            "session": "session:",
            "homework": "homework:",
            "analytics": "analytics:",
            "temp": "temp:"
        }
        
        # 默认TTL设置（秒）
        self.default_ttl = {
            "ai": 3600,  # AI响应缓存1小时
            "user": 1800,  # 用户信息缓存30分钟
            "session": 7200,  # 会话缓存2小时
            "homework": 86400,  # 作业缓存1天
            "analytics": 1800,  # 分析结果缓存30分钟
            "temp": 300  # 临时缓存5分钟
        }
    
    async def connect(self):
        """连接Redis"""
        try:
            self.connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                db=self.db,
                decode_responses=True,
                max_connections=20
            )
            self.redis_client = redis.Redis(connection_pool=self.connection_pool)
            
            # 测试连接
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
        if self.connection_pool:
            await self.connection_pool.disconnect()
        self.is_connected = False
        logger.info("Redis connection closed")
    
    def _get_key(self, category: str, key: str) -> str:
        """生成缓存键"""
        prefix = self.prefixes.get(category, "")
        return f"{prefix}{key}"
    
    async def _ensure_connected(self):
        """确保Redis连接"""
        if not self.is_connected:
            await self.connect()
    
    async def set(self, category: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            await self._ensure_connected()
            
            cache_key = self._get_key(category, key)
            
            # 序列化值
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            elif isinstance(value, (str, int, float, bool)):
                serialized_value = str(value)
            else:
                # 对于复杂对象使用pickle
                serialized_value = pickle.dumps(value).hex()
                cache_key += ":pickle"
            
            # 设置TTL
            if ttl is None:
                ttl = self.default_ttl.get(category, 3600)
            
            await self.redis_client.setex(cache_key, ttl, serialized_value)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def get(self, category: str, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            await self._ensure_connected()
            
            cache_key = self._get_key(category, key)
            
            # 尝试获取普通缓存
            value = await self.redis_client.get(cache_key)
            if value is not None:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            
            # 尝试获取pickle缓存
            pickle_key = cache_key + ":pickle"
            pickle_value = await self.redis_client.get(pickle_key)
            if pickle_value is not None:
                return pickle.loads(bytes.fromhex(pickle_value))
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    async def delete(self, category: str, key: str) -> bool:
        """删除缓存"""
        try:
            await self._ensure_connected()
            
            cache_key = self._get_key(category, key)
            pickle_key = cache_key + ":pickle"
            
            # 删除两种可能的键
            result1 = await self.redis_client.delete(cache_key)
            result2 = await self.redis_client.delete(pickle_key)
            
            return (result1 + result2) > 0
            
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    async def exists(self, category: str, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            await self._ensure_connected()
            
            cache_key = self._get_key(category, key)
            pickle_key = cache_key + ":pickle"
            
            exists1 = await self.redis_client.exists(cache_key)
            exists2 = await self.redis_client.exists(pickle_key)
            
            return exists1 or exists2
            
        except Exception as e:
            logger.error(f"Cache exists error: {str(e)}")
            return False
    
    async def expire(self, category: str, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        try:
            await self._ensure_connected()
            
            cache_key = self._get_key(category, key)
            return await self.redis_client.expire(cache_key, ttl)
            
        except Exception as e:
            logger.error(f"Cache expire error: {str(e)}")
            return False
    
    async def clear_category(self, category: str) -> int:
        """清空某个分类的所有缓存"""
        try:
            await self._ensure_connected()
            
            prefix = self.prefixes.get(category, "")
            pattern = f"{prefix}*"
            
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear category error: {str(e)}")
            return 0
    
    # AI缓存专用方法
    async def get_ai_cache(self, key: str) -> Optional[AIResponse]:
        """获取AI响应缓存"""
        cached_data = await self.get("ai", key)
        if cached_data:
            try:
                return AIResponse(
                    success=cached_data["success"],
                    content=cached_data["content"],
                    provider=AIProvider(cached_data["provider"]),
                    model=cached_data["model"],
                    usage=cached_data.get("usage"),
                    error=cached_data.get("error"),
                    response_time=cached_data.get("response_time"),
                    cached=True,
                    metadata=cached_data.get("metadata")
                )
            except Exception as e:
                logger.error(f"Failed to deserialize AI response: {str(e)}")
        return None
    
    async def set_ai_cache(self, key: str, response: AIResponse, ttl: int = 3600) -> bool:
        """设置AI响应缓存"""
        cache_data = {
            "success": response.success,
            "content": response.content,
            "provider": response.provider.value,
            "model": response.model,
            "usage": response.usage,
            "error": response.error,
            "response_time": response.response_time,
            "metadata": response.metadata,
            "cached_at": datetime.now().isoformat()
        }
        return await self.set("ai", key, cache_data, ttl)
    
    # 用户会话缓存
    async def set_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 7200) -> bool:
        """设置用户会话缓存"""
        session_data["last_activity"] = datetime.now().isoformat()
        return await self.set("session", user_id, session_data, ttl)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户会话缓存"""
        return await self.get("session", user_id)
    
    async def update_user_activity(self, user_id: str) -> bool:
        """更新用户活动时间"""
        session_data = await self.get_user_session(user_id)
        if session_data:
            session_data["last_activity"] = datetime.now().isoformat()
            return await self.set_user_session(user_id, session_data)
        return False
    
    # 作业缓存
    async def cache_homework_result(self, submission_id: str, result: Dict[str, Any], ttl: int = 86400) -> bool:
        """缓存作业批改结果"""
        return await self.set("homework", submission_id, result, ttl)
    
    async def get_homework_result(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """获取作业批改结果缓存"""
        return await self.get("homework", submission_id)
    
    # 分析结果缓存
    async def cache_analytics_result(self, analysis_key: str, result: Dict[str, Any], ttl: int = 1800) -> bool:
        """缓存分析结果"""
        return await self.set("analytics", analysis_key, result, ttl)
    
    async def get_analytics_result(self, analysis_key: str) -> Optional[Dict[str, Any]]:
        """获取分析结果缓存"""
        return await self.get("analytics", analysis_key)
    
    # 批量操作
    async def mget(self, category: str, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存"""
        results = {}
        for key in keys:
            value = await self.get(category, key)
            if value is not None:
                results[key] = value
        return results
    
    async def mset(self, category: str, data: Dict[str, Any], ttl: Optional[int] = None) -> int:
        """批量设置缓存"""
        success_count = 0
        for key, value in data.items():
            if await self.set(category, key, value, ttl):
                success_count += 1
        return success_count
    
    # 统计信息
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            await self._ensure_connected()
            
            info = await self.redis_client.info()
            stats = {
                "connected": self.is_connected,
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
            
            # 计算命中率
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            if hits + misses > 0:
                stats["hit_rate"] = round((hits / (hits + misses)) * 100, 2)
            else:
                stats["hit_rate"] = 0
            
            # 获取各分类的键数量
            category_counts = {}
            for category, prefix in self.prefixes.items():
                keys = await self.redis_client.keys(f"{prefix}*")
                category_counts[category] = len(keys)
            
            stats["category_counts"] = category_counts
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {"connected": False, "error": str(e)}
    
    # 健康检查
    async def health_check(self) -> Dict[str, Any]:
        """缓存健康检查"""
        try:
            await self._ensure_connected()
            
            # 测试基本操作
            test_key = "health_check"
            test_value = {"timestamp": datetime.now().isoformat()}
            
            # 写入测试
            write_success = await self.set("temp", test_key, test_value, 60)
            
            # 读取测试
            read_value = await self.get("temp", test_key)
            read_success = read_value is not None
            
            # 删除测试
            delete_success = await self.delete("temp", test_key)
            
            return {
                "status": "healthy" if all([write_success, read_success, delete_success]) else "unhealthy",
                "connected": self.is_connected,
                "operations": {
                    "write": write_success,
                    "read": read_success,
                    "delete": delete_success
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # 清理过期缓存
    async def cleanup_expired(self) -> Dict[str, int]:
        """清理过期缓存（Redis会自动处理，这里主要用于统计）"""
        try:
            await self._ensure_connected()
            
            cleanup_stats = {}
            
            for category, prefix in self.prefixes.items():
                keys = await self.redis_client.keys(f"{prefix}*")
                expired_count = 0
                
                for key in keys:
                    ttl = await self.redis_client.ttl(key)
                    if ttl == -2:  # 键已过期
                        expired_count += 1
                
                cleanup_stats[category] = {
                    "total_keys": len(keys),
                    "expired_keys": expired_count
                }
            
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Cleanup expired error: {str(e)}")
            return {}

# 全局缓存管理器实例
cache_manager = None

def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager()
    return cache_manager

async def init_cache(redis_url: str = "redis://localhost:6379", db: int = 0):
    """初始化缓存"""
    global cache_manager
    cache_manager = CacheManager(redis_url, db)
    await cache_manager.connect()
    return cache_manager

async def close_cache():
    """关闭缓存连接"""
    global cache_manager
    if cache_manager:
        await cache_manager.disconnect()
        cache_manager = None