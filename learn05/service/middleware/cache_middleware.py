# -*- coding: utf-8 -*-
"""
缓存中间件

本模块提供API响应缓存、智能缓存策略和缓存管理功能。
"""

import json
import hashlib
import logging
from typing import Callable, Optional, Dict, Any, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import JSONResponse
import asyncio
from datetime import datetime, timedelta

# 尝试导入缓存管理器
try:
    from ..utils.cache_manager import CacheManager
    from ..config.cache_config import CacheConfig, CacheKeyGenerator
except ImportError:
    # 开发阶段的模拟实现
    class CacheManager:
        async def get(self, key: str) -> Optional[Any]:
            return None
        
        async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
            return True
        
        async def delete(self, key: str) -> bool:
            return True
        
        async def clear_pattern(self, pattern: str) -> int:
            return 0
    
    class CacheConfig:
        def __init__(self):
            self.enabled = True
            self.default_ttl = 300
            self.max_size = 1000
    
    class CacheKeyGenerator:
        @staticmethod
        def api_cache_key(method: str, path: str, query_params: dict, user_id: Optional[str] = None) -> str:
            return f"api:{method}:{path}:{hash(str(query_params))}:{user_id or 'anonymous'}"

logger = logging.getLogger(__name__)
cache_logger = logging.getLogger("cache")


class CacheMiddleware(BaseHTTPMiddleware):
    """API响应缓存中间件"""
    
    def __init__(
        self, 
        app: ASGIApp,
        cache_manager: Optional[CacheManager] = None,
        cache_config: Optional[CacheConfig] = None,
        cacheable_methods: List[str] = None,
        cacheable_paths: List[str] = None,
        exclude_paths: List[str] = None,
        cache_headers: bool = True
    ):
        super().__init__(app)
        self.cache_manager = cache_manager or CacheManager()
        self.cache_config = cache_config or CacheConfig()
        self.cacheable_methods = cacheable_methods or ["GET"]
        self.cacheable_paths = cacheable_paths or []
        self.exclude_paths = exclude_paths or [
            "/api/v1/auth/",
            "/api/v1/system/health",
            "/docs",
            "/openapi.json"
        ]
        self.cache_headers = cache_headers
        self.key_generator = CacheKeyGenerator()
        
        # 缓存统计
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "total_requests": 0
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否启用缓存
        if not self.cache_config.enabled:
            return await call_next(request)
        
        # 检查是否可缓存
        if not self._is_cacheable(request):
            return await call_next(request)
        
        self.cache_stats["total_requests"] += 1
        
        # 生成缓存键
        cache_key = self._generate_cache_key(request)
        
        try:
            # 尝试从缓存获取响应
            cached_response = await self.cache_manager.get(cache_key)
            if cached_response:
                self.cache_stats["hits"] += 1
                cache_logger.debug(f"缓存命中: {cache_key}")
                return self._create_response_from_cache(cached_response, request)
            
            # 缓存未命中，处理请求
            self.cache_stats["misses"] += 1
            response = await call_next(request)
            
            # 缓存响应（异步）
            if self._should_cache_response(response):
                asyncio.create_task(self._cache_response(cache_key, response, request))
            
            # 添加缓存头信息
            if self.cache_headers:
                response.headers["X-Cache-Status"] = "MISS"
                response.headers["X-Cache-Key"] = cache_key
            
            return response
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            cache_logger.error(f"缓存操作失败: {e}")
            # 缓存失败时继续正常处理请求
            return await call_next(request)
    
    def _is_cacheable(self, request: Request) -> bool:
        """检查请求是否可缓存"""
        # 检查HTTP方法
        if request.method not in self.cacheable_methods:
            return False
        
        # 检查排除路径
        path = request.url.path
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return False
        
        # 检查包含路径（如果指定）
        if self.cacheable_paths:
            for cacheable_path in self.cacheable_paths:
                if path.startswith(cacheable_path):
                    return True
            return False
        
        # 检查认证头（避免缓存需要认证的请求）
        if "authorization" in request.headers:
            # 只缓存公开API或特定的认证API
            if not any(path.startswith(p) for p in ["/api/v1/public/", "/api/v1/grades/statistics"]):
                return False
        
        return True
    
    def _generate_cache_key(self, request: Request) -> str:
        """生成缓存键"""
        # 获取用户ID（如果有）
        user_id = getattr(request.state, "user_id", None)
        
        # 生成基础缓存键
        cache_key = self.key_generator.api_cache_key(
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            user_id=user_id
        )
        
        return cache_key
    
    def _should_cache_response(self, response: Response) -> bool:
        """检查响应是否应该缓存"""
        # 只缓存成功响应
        if response.status_code >= 400:
            return False
        
        # 检查Cache-Control头
        cache_control = response.headers.get("cache-control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False
        
        return True
    
    async def _cache_response(self, cache_key: str, response: Response, request: Request):
        """缓存响应（异步）"""
        try:
            # 读取响应体
            if hasattr(response, 'body'):
                body = response.body
            else:
                # 对于StreamingResponse等，需要特殊处理
                return
            
            # 构建缓存数据
            cache_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body.decode() if isinstance(body, bytes) else body,
                "content_type": response.headers.get("content-type", "application/json"),
                "cached_at": datetime.now().isoformat(),
                "request_path": request.url.path
            }
            
            # 计算TTL
            ttl = self._calculate_ttl(request, response)
            
            # 存储到缓存
            await self.cache_manager.set(cache_key, cache_data, ttl)
            cache_logger.debug(f"响应已缓存: {cache_key}, TTL: {ttl}s")
            
        except Exception as e:
            cache_logger.error(f"缓存响应失败: {e}")
    
    def _calculate_ttl(self, request: Request, response: Response) -> int:
        """计算缓存TTL"""
        # 检查响应头中的缓存指令
        cache_control = response.headers.get("cache-control", "")
        if "max-age=" in cache_control:
            try:
                max_age = int(cache_control.split("max-age=")[1].split(",")[0])
                return min(max_age, self.cache_config.default_ttl)
            except (ValueError, IndexError):
                pass
        
        # 根据路径类型设置不同的TTL
        path = request.url.path
        if "/statistics" in path or "/analytics" in path:
            return 600  # 统计数据缓存10分钟
        elif "/grades" in path:
            return 300  # 成绩数据缓存5分钟
        elif "/public" in path:
            return 3600  # 公开数据缓存1小时
        else:
            return self.cache_config.default_ttl
    
    def _create_response_from_cache(self, cached_data: Dict[str, Any], request: Request) -> Response:
        """从缓存数据创建响应"""
        try:
            # 创建响应
            if cached_data["content_type"].startswith("application/json"):
                # JSON响应
                try:
                    content = json.loads(cached_data["body"]) if isinstance(cached_data["body"], str) else cached_data["body"]
                    response = JSONResponse(
                        content=content,
                        status_code=cached_data["status_code"]
                    )
                except json.JSONDecodeError:
                    response = Response(
                        content=cached_data["body"],
                        status_code=cached_data["status_code"],
                        media_type=cached_data["content_type"]
                    )
            else:
                # 其他类型响应
                response = Response(
                    content=cached_data["body"],
                    status_code=cached_data["status_code"],
                    media_type=cached_data["content_type"]
                )
            
            # 添加原始头信息（排除一些不应该缓存的头）
            exclude_headers = {"date", "server", "x-request-id", "x-process-time"}
            for key, value in cached_data["headers"].items():
                if key.lower() not in exclude_headers:
                    response.headers[key] = value
            
            # 添加缓存头信息
            if self.cache_headers:
                response.headers["X-Cache-Status"] = "HIT"
                response.headers["X-Cached-At"] = cached_data["cached_at"]
                response.headers["X-Cache-Age"] = str(
                    int((datetime.now() - datetime.fromisoformat(cached_data["cached_at"])).total_seconds())
                )
            
            return response
            
        except Exception as e:
            cache_logger.error(f"从缓存创建响应失败: {e}")
            # 返回一个错误响应，触发重新请求
            raise
    
    async def invalidate_cache(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        try:
            count = await self.cache_manager.clear_pattern(pattern)
            cache_logger.info(f"清除缓存: {pattern}, 数量: {count}")
            return count
        except Exception as e:
            cache_logger.error(f"清除缓存失败: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total = self.cache_stats["total_requests"]
        if total == 0:
            return self.cache_stats.copy()
        
        stats = self.cache_stats.copy()
        stats["hit_rate"] = stats["hits"] / total * 100
        stats["miss_rate"] = stats["misses"] / total * 100
        stats["error_rate"] = stats["errors"] / total * 100
        
        return stats


class SmartCacheMiddleware(CacheMiddleware):
    """智能缓存中间件 - 支持更高级的缓存策略"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_warming_enabled = kwargs.get("cache_warming_enabled", False)
        self.adaptive_ttl_enabled = kwargs.get("adaptive_ttl_enabled", True)
        self.request_frequency = {}  # 请求频率统计
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求频率
        if self.adaptive_ttl_enabled:
            self._record_request_frequency(request)
        
        return await super().dispatch(request, call_next)
    
    def _record_request_frequency(self, request: Request):
        """记录请求频率"""
        path = request.url.path
        current_time = datetime.now()
        
        if path not in self.request_frequency:
            self.request_frequency[path] = []
        
        # 添加当前请求时间
        self.request_frequency[path].append(current_time)
        
        # 清理1小时前的记录
        cutoff_time = current_time - timedelta(hours=1)
        self.request_frequency[path] = [
            t for t in self.request_frequency[path] if t > cutoff_time
        ]
    
    def _calculate_ttl(self, request: Request, response: Response) -> int:
        """智能计算缓存TTL"""
        base_ttl = super()._calculate_ttl(request, response)
        
        if not self.adaptive_ttl_enabled:
            return base_ttl
        
        # 根据请求频率调整TTL
        path = request.url.path
        frequency = len(self.request_frequency.get(path, []))
        
        if frequency > 100:  # 高频请求
            return min(base_ttl * 2, 3600)  # 最多1小时
        elif frequency > 50:  # 中频请求
            return base_ttl
        else:  # 低频请求
            return max(base_ttl // 2, 60)  # 最少1分钟


def setup_cache_middleware(app, cache_manager: CacheManager, config: dict = None):
    """设置缓存中间件"""
    config = config or {}
    cache_config = config.get("cache", {})
    
    # 选择中间件类型
    middleware_class = SmartCacheMiddleware if cache_config.get("smart_cache", True) else CacheMiddleware
    
    app.add_middleware(
        middleware_class,
        cache_manager=cache_manager,
        cacheable_methods=cache_config.get("cacheable_methods", ["GET"]),
        cacheable_paths=cache_config.get("cacheable_paths", []),
        exclude_paths=cache_config.get("exclude_paths", []),
        cache_headers=cache_config.get("cache_headers", True),
        cache_warming_enabled=cache_config.get("cache_warming_enabled", False),
        adaptive_ttl_enabled=cache_config.get("adaptive_ttl_enabled", True)
    )
    
    logger.info("缓存中间件设置完成")