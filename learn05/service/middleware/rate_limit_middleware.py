# -*- coding: utf-8 -*-
"""
限流中间件

本模块提供API访问频率限制、防护和流量控制功能。
"""

import time
import logging
import hashlib
from typing import Callable, Dict, Any, Optional, List, Tuple
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import JSONResponse
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

# 尝试导入Redis缓存
try:
    from ..utils.cache_manager import CacheManager
except ImportError:
    # 开发阶段的模拟实现
    class CacheManager:
        def __init__(self):
            self._data = {}
        
        async def get(self, key: str) -> Optional[Any]:
            return self._data.get(key)
        
        async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
            self._data[key] = value
            return True
        
        async def incr(self, key: str, amount: int = 1) -> int:
            current = self._data.get(key, 0)
            self._data[key] = current + amount
            return self._data[key]
        
        async def expire(self, key: str, ttl: int) -> bool:
            return True

logger = logging.getLogger(__name__)
rate_limit_logger = logging.getLogger("rate_limit")


class RateLimitRule:
    """限流规则"""
    
    def __init__(
        self,
        requests: int,
        window: int,
        burst: Optional[int] = None,
        key_func: Optional[Callable] = None,
        scope: str = "global"
    ):
        self.requests = requests  # 允许的请求数
        self.window = window  # 时间窗口（秒）
        self.burst = burst or requests  # 突发请求数
        self.key_func = key_func  # 自定义键生成函数
        self.scope = scope  # 限流范围：global, ip, user, endpoint
    
    def generate_key(self, request: Request) -> str:
        """生成限流键"""
        if self.key_func:
            return self.key_func(request)
        
        if self.scope == "ip":
            return f"rate_limit:ip:{self._get_client_ip(request)}"
        elif self.scope == "user":
            user_id = getattr(request.state, "user_id", "anonymous")
            return f"rate_limit:user:{user_id}"
        elif self.scope == "endpoint":
            return f"rate_limit:endpoint:{request.method}:{request.url.path}"
        else:  # global
            return "rate_limit:global"
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity  # 桶容量
        self.tokens = capacity  # 当前令牌数
        self.refill_rate = refill_rate  # 令牌补充速率（每秒）
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """消费令牌"""
        async with self.lock:
            now = time.time()
            # 补充令牌
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            
            # 检查是否有足够令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """获取等待时间"""
        if self.tokens >= tokens:
            return 0
        return (tokens - self.tokens) / self.refill_rate


class SlidingWindowCounter:
    """滑动窗口计数器"""
    
    def __init__(self, window_size: int, bucket_count: int = 10):
        self.window_size = window_size
        self.bucket_count = bucket_count
        self.bucket_size = window_size / bucket_count
        self.buckets = deque(maxlen=bucket_count)
        self.last_update = time.time()
    
    def add_request(self, timestamp: Optional[float] = None) -> int:
        """添加请求并返回当前窗口内的请求数"""
        if timestamp is None:
            timestamp = time.time()
        
        self._update_buckets(timestamp)
        
        # 添加到当前桶
        if self.buckets:
            self.buckets[-1][1] += 1
        else:
            bucket_start = int(timestamp / self.bucket_size) * self.bucket_size
            self.buckets.append([bucket_start, 1])
        
        return self.get_request_count()
    
    def get_request_count(self) -> int:
        """获取当前窗口内的请求数"""
        return sum(bucket[1] for bucket in self.buckets)
    
    def _update_buckets(self, timestamp: float):
        """更新桶"""
        current_bucket = int(timestamp / self.bucket_size) * self.bucket_size
        window_start = timestamp - self.window_size
        
        # 移除过期的桶
        while self.buckets and self.buckets[0][0] < window_start:
            self.buckets.popleft()
        
        # 添加新桶（如果需要）
        if not self.buckets or self.buckets[-1][0] < current_bucket:
            # 填充中间的空桶
            if self.buckets:
                last_bucket = self.buckets[-1][0]
                bucket = last_bucket + self.bucket_size
                while bucket <= current_bucket:
                    if bucket >= window_start:
                        self.buckets.append([bucket, 0])
                    bucket += self.bucket_size
            else:
                self.buckets.append([current_bucket, 0])


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(
        self,
        app: ASGIApp,
        cache_manager: Optional[CacheManager] = None,
        default_rules: Optional[List[RateLimitRule]] = None,
        algorithm: str = "sliding_window",  # token_bucket, sliding_window, fixed_window
        enable_burst: bool = True,
        whitelist_ips: Optional[List[str]] = None,
        blacklist_ips: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.cache_manager = cache_manager or CacheManager()
        self.algorithm = algorithm
        self.enable_burst = enable_burst
        self.whitelist_ips = set(whitelist_ips or [])
        self.blacklist_ips = set(blacklist_ips or [])
        
        # 默认限流规则
        self.default_rules = default_rules or [
            RateLimitRule(requests=100, window=60, scope="ip"),  # 每分钟100次/IP
            RateLimitRule(requests=1000, window=3600, scope="user"),  # 每小时1000次/用户
            RateLimitRule(requests=10000, window=3600, scope="global"),  # 每小时10000次全局
        ]
        
        # 路径特定规则
        self.path_rules = {
            "/api/v1/auth/login": [RateLimitRule(requests=5, window=300, scope="ip")],  # 登录限制
            "/api/v1/ai/": [RateLimitRule(requests=20, window=60, scope="user")],  # AI接口限制
            "/api/v1/grades/import": [RateLimitRule(requests=3, window=3600, scope="user")],  # 导入限制
        }
        
        # 内存存储（用于令牌桶和滑动窗口）
        self.token_buckets = {}
        self.sliding_windows = {}
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "blocked_by_rule": defaultdict(int),
            "blocked_by_ip": defaultdict(int)
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        self.stats["total_requests"] += 1
        
        # 检查IP黑白名单
        client_ip = self._get_client_ip(request)
        
        if client_ip in self.blacklist_ips:
            self.stats["blocked_requests"] += 1
            self.stats["blocked_by_ip"][client_ip] += 1
            rate_limit_logger.warning(f"IP黑名单阻止请求: {client_ip}")
            return self._create_rate_limit_response("IP blocked", 403)
        
        if client_ip in self.whitelist_ips:
            # 白名单IP跳过限流
            return await call_next(request)
        
        # 获取适用的限流规则
        rules = self._get_applicable_rules(request)
        
        # 检查每个规则
        for rule in rules:
            is_allowed, wait_time = await self._check_rate_limit(request, rule)
            if not is_allowed:
                self.stats["blocked_requests"] += 1
                self.stats["blocked_by_rule"][f"{rule.scope}:{rule.requests}/{rule.window}"] += 1
                
                rate_limit_logger.warning(
                    f"限流阻止请求: IP={client_ip}, Rule={rule.scope}:{rule.requests}/{rule.window}, "
                    f"Path={request.url.path}, Wait={wait_time:.2f}s"
                )
                
                return self._create_rate_limit_response(
                    f"Rate limit exceeded. Try again in {wait_time:.0f} seconds.",
                    429,
                    wait_time
                )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加限流头信息
        self._add_rate_limit_headers(response, request, rules)
        
        return response
    
    def _get_applicable_rules(self, request: Request) -> List[RateLimitRule]:
        """获取适用的限流规则"""
        rules = self.default_rules.copy()
        
        # 检查路径特定规则
        path = request.url.path
        for pattern, path_rules in self.path_rules.items():
            if path.startswith(pattern):
                rules.extend(path_rules)
        
        return rules
    
    async def _check_rate_limit(self, request: Request, rule: RateLimitRule) -> Tuple[bool, float]:
        """检查限流规则"""
        key = rule.generate_key(request)
        
        if self.algorithm == "token_bucket":
            return await self._check_token_bucket(key, rule)
        elif self.algorithm == "sliding_window":
            return await self._check_sliding_window(key, rule)
        else:  # fixed_window
            return await self._check_fixed_window(key, rule)
    
    async def _check_token_bucket(self, key: str, rule: RateLimitRule) -> Tuple[bool, float]:
        """令牌桶算法检查"""
        if key not in self.token_buckets:
            self.token_buckets[key] = TokenBucket(
                capacity=rule.burst,
                refill_rate=rule.requests / rule.window
            )
        
        bucket = self.token_buckets[key]
        is_allowed = await bucket.consume(1)
        wait_time = bucket.get_wait_time(1) if not is_allowed else 0
        
        return is_allowed, wait_time
    
    async def _check_sliding_window(self, key: str, rule: RateLimitRule) -> Tuple[bool, float]:
        """滑动窗口算法检查"""
        if key not in self.sliding_windows:
            self.sliding_windows[key] = SlidingWindowCounter(rule.window)
        
        window = self.sliding_windows[key]
        current_count = window.add_request()
        
        is_allowed = current_count <= rule.requests
        wait_time = rule.window if not is_allowed else 0
        
        return is_allowed, wait_time
    
    async def _check_fixed_window(self, key: str, rule: RateLimitRule) -> Tuple[bool, float]:
        """固定窗口算法检查"""
        now = int(time.time())
        window_start = (now // rule.window) * rule.window
        cache_key = f"{key}:{window_start}"
        
        try:
            current_count = await self.cache_manager.get(cache_key) or 0
            
            if current_count >= rule.requests:
                # 计算等待时间
                wait_time = window_start + rule.window - now
                return False, wait_time
            
            # 增加计数
            new_count = await self.cache_manager.incr(cache_key, 1)
            if new_count == 1:
                # 设置过期时间
                await self.cache_manager.expire(cache_key, rule.window)
            
            return True, 0
            
        except Exception as e:
            logger.error(f"固定窗口限流检查失败: {e}")
            # 出错时允许请求通过
            return True, 0
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _create_rate_limit_response(self, message: str, status_code: int, retry_after: float = 0) -> Response:
        """创建限流响应"""
        headers = {}
        if retry_after > 0:
            headers["Retry-After"] = str(int(retry_after))
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": "Rate limit exceeded",
                "message": message,
                "retry_after": int(retry_after) if retry_after > 0 else None
            },
            headers=headers
        )
    
    def _add_rate_limit_headers(self, response: Response, request: Request, rules: List[RateLimitRule]):
        """添加限流头信息"""
        # 添加主要限流信息（取最严格的规则）
        if rules:
            main_rule = min(rules, key=lambda r: r.requests / r.window)
            key = main_rule.generate_key(request)
            
            # 获取当前使用情况
            if self.algorithm == "token_bucket" and key in self.token_buckets:
                bucket = self.token_buckets[key]
                remaining = int(bucket.tokens)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
            elif self.algorithm == "sliding_window" and key in self.sliding_windows:
                window = self.sliding_windows[key]
                used = window.get_request_count()
                remaining = max(0, main_rule.requests - used)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
            
            response.headers["X-RateLimit-Limit"] = str(main_rule.requests)
            response.headers["X-RateLimit-Window"] = str(main_rule.window)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取限流统计信息"""
        total = self.stats["total_requests"]
        if total == 0:
            return self.stats
        
        stats = dict(self.stats)
        stats["block_rate"] = stats["blocked_requests"] / total * 100
        stats["success_rate"] = (total - stats["blocked_requests"]) / total * 100
        
        return stats
    
    async def reset_limits(self, scope: str = "all"):
        """重置限流计数"""
        if scope == "all" or scope == "token_bucket":
            self.token_buckets.clear()
        
        if scope == "all" or scope == "sliding_window":
            self.sliding_windows.clear()
        
        if scope == "all" or scope == "cache":
            # 清除Redis中的限流数据
            try:
                await self.cache_manager.clear_pattern("rate_limit:*")
            except Exception as e:
                logger.error(f"清除限流缓存失败: {e}")
        
        logger.info(f"限流计数已重置: {scope}")


def setup_rate_limit_middleware(app, cache_manager: CacheManager, config: dict = None):
    """设置限流中间件"""
    config = config or {}
    rate_limit_config = config.get("rate_limit", {})
    
    # 构建默认规则
    default_rules = []
    for rule_config in rate_limit_config.get("default_rules", []):
        default_rules.append(RateLimitRule(
            requests=rule_config["requests"],
            window=rule_config["window"],
            burst=rule_config.get("burst"),
            scope=rule_config.get("scope", "global")
        ))
    
    app.add_middleware(
        RateLimitMiddleware,
        cache_manager=cache_manager,
        default_rules=default_rules,
        algorithm=rate_limit_config.get("algorithm", "sliding_window"),
        enable_burst=rate_limit_config.get("enable_burst", True),
        whitelist_ips=rate_limit_config.get("whitelist_ips", []),
        blacklist_ips=rate_limit_config.get("blacklist_ips", [])
    )
    
    logger.info("限流中间件设置完成")