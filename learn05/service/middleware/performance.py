# -*- coding: utf-8 -*-
"""
性能监控中间件

本模块提供API性能监控、请求日志记录和性能分析功能。
"""

import time
import logging
import uuid
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)
performance_logger = logging.getLogger("performance")
access_logger = logging.getLogger("access")


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.request_stats = {
            "total_requests": 0,
            "slow_requests": 0,
            "error_requests": 0,
            "avg_response_time": 0.0
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        await self._log_request_start(request, request_id)
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 添加性能头信息
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            # 记录请求完成信息
            await self._log_request_end(request, response, process_time, request_id)
            
            # 更新统计信息
            self._update_stats(process_time, response.status_code)
            
            return response
            
        except Exception as exc:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录异常
            await self._log_request_error(request, exc, process_time, request_id)
            
            # 更新错误统计
            self._update_stats(process_time, 500, is_error=True)
            
            # 重新抛出异常
            raise exc
    
    async def _log_request_start(self, request: Request, request_id: str):
        """记录请求开始"""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        access_logger.info(
            f"REQUEST_START | ID: {request_id} | "
            f"Method: {request.method} | "
            f"URL: {request.url} | "
            f"IP: {client_ip} | "
            f"User-Agent: {user_agent}"
        )
    
    async def _log_request_end(self, request: Request, response: Response, 
                              process_time: float, request_id: str):
        """记录请求完成"""
        client_ip = self._get_client_ip(request)
        
        # 判断是否为慢请求
        is_slow = process_time > self.slow_request_threshold
        log_level = logging.WARNING if is_slow else logging.INFO
        
        access_logger.log(
            log_level,
            f"REQUEST_END | ID: {request_id} | "
            f"Method: {request.method} | "
            f"URL: {request.url} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.3f}s | "
            f"IP: {client_ip} | "
            f"Slow: {is_slow}"
        )
        
        # 记录性能数据
        if is_slow:
            performance_logger.warning(
                f"SLOW_REQUEST | ID: {request_id} | "
                f"URL: {request.url} | "
                f"Time: {process_time:.3f}s"
            )
    
    async def _log_request_error(self, request: Request, exc: Exception, 
                                process_time: float, request_id: str):
        """记录请求错误"""
        client_ip = self._get_client_ip(request)
        
        access_logger.error(
            f"REQUEST_ERROR | ID: {request_id} | "
            f"Method: {request.method} | "
            f"URL: {request.url} | "
            f"Time: {process_time:.3f}s | "
            f"IP: {client_ip} | "
            f"Error: {type(exc).__name__} | "
            f"Message: {str(exc)}"
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 返回直接连接的IP
        return request.client.host if request.client else "unknown"
    
    def _update_stats(self, process_time: float, status_code: int, is_error: bool = False):
        """更新统计信息"""
        self.request_stats["total_requests"] += 1
        
        if is_error or status_code >= 400:
            self.request_stats["error_requests"] += 1
        
        if process_time > self.slow_request_threshold:
            self.request_stats["slow_requests"] += 1
        
        # 更新平均响应时间
        total = self.request_stats["total_requests"]
        current_avg = self.request_stats["avg_response_time"]
        self.request_stats["avg_response_time"] = (
            (current_avg * (total - 1) + process_time) / total
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = self.request_stats["total_requests"]
        if total == 0:
            return self.request_stats.copy()
        
        stats = self.request_stats.copy()
        stats["slow_request_rate"] = stats["slow_requests"] / total * 100
        stats["error_rate"] = stats["error_requests"] / total * 100
        stats["success_rate"] = (total - stats["error_requests"]) / total * 100
        
        return stats


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    def __init__(self, app: ASGIApp, log_request_body: bool = False, 
                 log_response_body: bool = False, max_body_size: int = 1024):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求详情
        await self._log_request_details(request)
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应详情
        await self._log_response_details(request, response)
        
        return response
    
    async def _log_request_details(self, request: Request):
        """记录请求详情"""
        request_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": request.path_params,
            "client": {
                "host": request.client.host if request.client else None,
                "port": request.client.port if request.client else None
            }
        }
        
        # 记录请求体（如果启用）
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    # 尝试解析JSON
                    try:
                        request_data["body"] = json.loads(body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_data["body"] = body.decode("utf-8", errors="ignore")[:self.max_body_size]
                else:
                    request_data["body"] = f"<Body too large: {len(body)} bytes>"
            except Exception as e:
                request_data["body_error"] = str(e)
        
        logger.debug(f"REQUEST_DETAILS: {json.dumps(request_data, ensure_ascii=False)}")
    
    async def _log_response_details(self, request: Request, response: Response):
        """记录响应详情"""
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "request_id": getattr(request.state, "request_id", None)
        }
        
        # 记录响应体（如果启用且状态码表示错误）
        if self.log_response_body and (response.status_code >= 400 or logger.isEnabledFor(logging.DEBUG)):
            try:
                # 注意：这里不能直接读取响应体，因为它可能已经被消费
                # 在实际应用中，可能需要使用StreamingResponse或其他方法
                pass
            except Exception as e:
                response_data["body_error"] = str(e)
        
        logger.debug(f"RESPONSE_DETAILS: {json.dumps(response_data, ensure_ascii=False)}")


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS中间件"""
    
    def __init__(self, app: ASGIApp, allow_origins: list = None, 
                 allow_methods: list = None, allow_headers: list = None,
                 allow_credentials: bool = True):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]
        self.allow_credentials = allow_credentials
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 处理预检请求
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)
        
        # 添加CORS头
        origin = request.headers.get("origin")
        if origin and ("*" in self.allow_origins or origin in self.allow_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in self.allow_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response


def setup_middleware(app, config: dict = None):
    """设置中间件"""
    config = config or {}
    
    # 性能监控中间件
    performance_config = config.get("performance", {})
    app.add_middleware(
        PerformanceMonitoringMiddleware,
        slow_request_threshold=performance_config.get("slow_request_threshold", 1.0)
    )
    
    # 请求日志中间件
    logging_config = config.get("logging", {})
    app.add_middleware(
        RequestLoggingMiddleware,
        log_request_body=logging_config.get("log_request_body", False),
        log_response_body=logging_config.get("log_response_body", False),
        max_body_size=logging_config.get("max_body_size", 1024)
    )
    
    # CORS中间件
    cors_config = config.get("cors", {})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.get("allow_origins", ["*"]),
        allow_methods=cors_config.get("allow_methods", ["GET", "POST", "PUT", "DELETE", "OPTIONS"]),
        allow_headers=cors_config.get("allow_headers", ["*"]),
        allow_credentials=cors_config.get("allow_credentials", True)
    )
    
    logger.info("中间件设置完成")


# 性能统计端点
def get_performance_stats(performance_middleware: PerformanceMonitoringMiddleware) -> dict:
    """获取性能统计信息"""
    return performance_middleware.get_stats()