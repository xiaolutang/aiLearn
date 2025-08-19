# -*- coding: utf-8 -*-
"""
压缩中间件

本模块提供HTTP响应压缩、内容优化和传输加速功能。
"""

import gzip
import zlib
import logging
from typing import Callable, List, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import StreamingResponse
import asyncio
from io import BytesIO
import json

# 尝试导入brotli，如果不存在则设置为None
try:
    import brotli
except ImportError:
    brotli = None

logger = logging.getLogger(__name__)
compression_logger = logging.getLogger("compression")


class CompressionMiddleware(BaseHTTPMiddleware):
    """响应压缩中间件"""
    
    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 500,
        compression_level: int = 6,
        compressible_types: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        enable_brotli: bool = True,
        enable_gzip: bool = True,
        enable_deflate: bool = True,
        auto_vary: bool = True
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.enable_brotli = enable_brotli
        self.enable_gzip = enable_gzip
        self.enable_deflate = enable_deflate
        self.auto_vary = auto_vary
        
        # 可压缩的MIME类型
        self.compressible_types = compressible_types or [
            "text/html",
            "text/css",
            "text/javascript",
            "text/plain",
            "text/xml",
            "application/json",
            "application/javascript",
            "application/xml",
            "application/rss+xml",
            "application/atom+xml",
            "application/x-javascript",
            "application/x-font-ttf",
            "application/vnd.ms-fontobject",
            "font/opentype",
            "image/svg+xml",
            "image/x-icon",
            "application/octet-stream"  # 用于API响应
        ]
        
        # 排除路径
        self.exclude_paths = exclude_paths or [
            "/api/v1/system/health",
            "/metrics",
            "/static/images/",
            "/static/videos/"
        ]
        
        # 压缩统计
        self.stats = {
            "total_responses": 0,
            "compressed_responses": 0,
            "total_bytes_before": 0,
            "total_bytes_after": 0,
            "compression_by_type": {
                "gzip": 0,
                "brotli": 0,
                "deflate": 0
            }
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否需要跳过压缩
        if self._should_skip_compression(request):
            return await call_next(request)
        
        # 处理请求
        response = await call_next(request)
        
        self.stats["total_responses"] += 1
        
        # 检查是否可以压缩响应
        if not self._can_compress_response(request, response):
            return response
        
        # 获取响应内容
        content = await self._get_response_content(response)
        if not content or len(content) < self.minimum_size:
            return response
        
        # 选择压缩算法
        compression_type = self._select_compression_type(request)
        if not compression_type:
            return response
        
        # 压缩内容
        compressed_content = self._compress_content(content, compression_type)
        if not compressed_content or len(compressed_content) >= len(content):
            # 压缩后更大，不使用压缩
            return response
        
        # 更新统计
        self.stats["compressed_responses"] += 1
        self.stats["total_bytes_before"] += len(content)
        self.stats["total_bytes_after"] += len(compressed_content)
        self.stats["compression_by_type"][compression_type] += 1
        
        # 创建压缩响应
        compressed_response = self._create_compressed_response(
            response, compressed_content, compression_type
        )
        
        compression_logger.debug(
            f"响应已压缩: {compression_type}, "
            f"原始大小: {len(content)}, "
            f"压缩后: {len(compressed_content)}, "
            f"压缩率: {(1 - len(compressed_content) / len(content)) * 100:.1f}%"
        )
        
        return compressed_response
    
    def _should_skip_compression(self, request: Request) -> bool:
        """检查是否应该跳过压缩"""
        # 检查排除路径
        path = request.url.path
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        
        # 检查Accept-Encoding头
        accept_encoding = request.headers.get("accept-encoding", "")
        if not accept_encoding:
            return True
        
        # 检查是否支持任何压缩算法
        supported_encodings = ["gzip", "br", "deflate"]
        if not any(encoding in accept_encoding.lower() for encoding in supported_encodings):
            return True
        
        return False
    
    def _can_compress_response(self, request: Request, response: Response) -> bool:
        """检查响应是否可以压缩"""
        # 检查状态码
        if response.status_code < 200 or response.status_code >= 300:
            return False
        
        # 检查是否已经压缩
        if "content-encoding" in response.headers:
            return False
        
        # 检查Content-Type
        content_type = response.headers.get("content-type", "")
        if content_type:
            # 提取主要MIME类型
            main_type = content_type.split(";")[0].strip().lower()
            if main_type not in self.compressible_types:
                return False
        
        # 检查Cache-Control
        cache_control = response.headers.get("cache-control", "")
        if "no-transform" in cache_control.lower():
            return False
        
        return True
    
    async def _get_response_content(self, response: Response) -> Optional[bytes]:
        """获取响应内容"""
        try:
            if hasattr(response, 'body'):
                content = response.body
                if isinstance(content, str):
                    return content.encode('utf-8')
                elif isinstance(content, bytes):
                    return content
            
            # 对于StreamingResponse等，暂时不支持压缩
            return None
            
        except Exception as e:
            compression_logger.error(f"获取响应内容失败: {e}")
            return None
    
    def _select_compression_type(self, request: Request) -> Optional[str]:
        """选择压缩算法"""
        accept_encoding = request.headers.get("accept-encoding", "").lower()
        
        # 按优先级选择压缩算法
        if self.enable_brotli and "br" in accept_encoding and brotli is not None:
            return "brotli"
        elif self.enable_gzip and "gzip" in accept_encoding:
            return "gzip"
        elif self.enable_deflate and "deflate" in accept_encoding:
            return "deflate"
        
        return None
    
    def _compress_content(self, content: bytes, compression_type: str) -> Optional[bytes]:
        """压缩内容"""
        try:
            if compression_type == "gzip":
                return gzip.compress(content, compresslevel=self.compression_level)
            elif compression_type == "brotli":
                if brotli is None:
                    # 如果brotli不可用，回退到gzip
                    return gzip.compress(content, compresslevel=self.compression_level)
                return brotli.compress(content, quality=self.compression_level)
            elif compression_type == "deflate":
                return zlib.compress(content, level=self.compression_level)
            else:
                return None
                
        except Exception as e:
            compression_logger.error(f"压缩内容失败: {compression_type}, {e}")
            return None
    
    def _create_compressed_response(
        self, 
        original_response: Response, 
        compressed_content: bytes, 
        compression_type: str
    ) -> Response:
        """创建压缩响应"""
        # 创建新响应
        response = Response(
            content=compressed_content,
            status_code=original_response.status_code,
            media_type=original_response.media_type
        )
        
        # 复制原始头信息
        for key, value in original_response.headers.items():
            if key.lower() not in ["content-length", "content-encoding"]:
                response.headers[key] = value
        
        # 设置压缩头信息
        if compression_type == "brotli":
            response.headers["content-encoding"] = "br"
        else:
            response.headers["content-encoding"] = compression_type
        
        response.headers["content-length"] = str(len(compressed_content))
        
        # 添加Vary头
        if self.auto_vary:
            vary_header = response.headers.get("vary", "")
            if "accept-encoding" not in vary_header.lower():
                if vary_header:
                    response.headers["vary"] = f"{vary_header}, Accept-Encoding"
                else:
                    response.headers["vary"] = "Accept-Encoding"
        
        return response
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """获取压缩统计信息"""
        total_responses = self.stats["total_responses"]
        compressed_responses = self.stats["compressed_responses"]
        total_before = self.stats["total_bytes_before"]
        total_after = self.stats["total_bytes_after"]
        
        stats = self.stats.copy()
        
        if total_responses > 0:
            stats["compression_rate"] = compressed_responses / total_responses * 100
        else:
            stats["compression_rate"] = 0
        
        if total_before > 0:
            stats["size_reduction_rate"] = (1 - total_after / total_before) * 100
            stats["average_compression_ratio"] = total_after / total_before
        else:
            stats["size_reduction_rate"] = 0
            stats["average_compression_ratio"] = 1
        
        stats["bytes_saved"] = total_before - total_after
        
        return stats


class ContentOptimizationMiddleware(BaseHTTPMiddleware):
    """内容优化中间件"""
    
    def __init__(
        self,
        app: ASGIApp,
        minify_json: bool = True,
        remove_whitespace: bool = True,
        optimize_images: bool = False,
        enable_etag: bool = True
    ):
        super().__init__(app)
        self.minify_json = minify_json
        self.remove_whitespace = remove_whitespace
        self.optimize_images = optimize_images
        self.enable_etag = enable_etag
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 优化响应内容
        if self._should_optimize(response):
            optimized_response = await self._optimize_response(response)
            if optimized_response:
                response = optimized_response
        
        # 添加ETag
        if self.enable_etag and self._should_add_etag(response):
            self._add_etag(response)
        
        return response
    
    def _should_optimize(self, response: Response) -> bool:
        """检查是否应该优化响应"""
        if response.status_code < 200 or response.status_code >= 300:
            return False
        
        content_type = response.headers.get("content-type", "")
        return any(ct in content_type for ct in [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript"
        ])
    
    async def _optimize_response(self, response: Response) -> Optional[Response]:
        """优化响应内容"""
        try:
            if not hasattr(response, 'body'):
                return None
            
            content = response.body
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            content_type = response.headers.get("content-type", "")
            
            # JSON优化
            if "application/json" in content_type and self.minify_json:
                try:
                    # 解析并重新序列化JSON（去除空格）
                    json_data = json.loads(content)
                    optimized_content = json.dumps(json_data, separators=(',', ':'), ensure_ascii=False)
                    
                    # 创建优化后的响应
                    optimized_response = Response(
                        content=optimized_content,
                        status_code=response.status_code,
                        media_type=response.media_type
                    )
                    
                    # 复制头信息
                    for key, value in response.headers.items():
                        if key.lower() != "content-length":
                            optimized_response.headers[key] = value
                    
                    optimized_response.headers["content-length"] = str(len(optimized_content.encode('utf-8')))
                    
                    return optimized_response
                    
                except json.JSONDecodeError:
                    pass
            
            # HTML/CSS/JS优化
            elif self.remove_whitespace and any(ct in content_type for ct in ["text/html", "text/css", "text/javascript"]):
                # 简单的空白字符优化
                import re
                optimized_content = re.sub(r'\s+', ' ', content).strip()
                
                if len(optimized_content) < len(content):
                    optimized_response = Response(
                        content=optimized_content,
                        status_code=response.status_code,
                        media_type=response.media_type
                    )
                    
                    for key, value in response.headers.items():
                        if key.lower() != "content-length":
                            optimized_response.headers[key] = value
                    
                    optimized_response.headers["content-length"] = str(len(optimized_content.encode('utf-8')))
                    
                    return optimized_response
            
            return None
            
        except Exception as e:
            logger.error(f"内容优化失败: {e}")
            return None
    
    def _should_add_etag(self, response: Response) -> bool:
        """检查是否应该添加ETag"""
        # 检查是否已有ETag
        if "etag" in response.headers:
            return False
        
        # 检查状态码
        if response.status_code != 200:
            return False
        
        # 检查内容类型
        content_type = response.headers.get("content-type", "")
        return any(ct in content_type for ct in [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript"
        ])
    
    def _add_etag(self, response: Response):
        """添加ETag头"""
        try:
            if hasattr(response, 'body'):
                content = response.body
                if isinstance(content, str):
                    content = content.encode('utf-8')
                
                # 生成ETag
                import hashlib
                etag = hashlib.md5(content).hexdigest()
                response.headers["etag"] = f'"{etag}"'
                
        except Exception as e:
            logger.error(f"添加ETag失败: {e}")


def setup_compression_middleware(app, config: dict = None):
    """设置压缩中间件"""
    config = config or {}
    compression_config = config.get("compression", {})
    optimization_config = config.get("optimization", {})
    
    # 内容优化中间件
    app.add_middleware(
        ContentOptimizationMiddleware,
        minify_json=optimization_config.get("minify_json", True),
        remove_whitespace=optimization_config.get("remove_whitespace", True),
        optimize_images=optimization_config.get("optimize_images", False),
        enable_etag=optimization_config.get("enable_etag", True)
    )
    
    # 压缩中间件
    app.add_middleware(
        CompressionMiddleware,
        minimum_size=compression_config.get("minimum_size", 500),
        compression_level=compression_config.get("compression_level", 6),
        compressible_types=compression_config.get("compressible_types"),
        exclude_paths=compression_config.get("exclude_paths"),
        enable_brotli=compression_config.get("enable_brotli", True),
        enable_gzip=compression_config.get("enable_gzip", True),
        enable_deflate=compression_config.get("enable_deflate", True),
        auto_vary=compression_config.get("auto_vary", True)
    )
    
    logger.info("压缩和优化中间件设置完成")