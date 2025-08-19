# -*- coding: utf-8 -*-
"""
全局异常处理中间件

本模块提供统一的异常处理机制，确保所有异常都能被正确捕获和处理。
"""

import logging
import traceback
import uuid
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

from models.response import (
    ResponseBuilder, CommonResponses, DetailedErrorResponse, 
    ValidationError as CustomValidationError, ErrorCode, get_http_status
)
from config import get_config

settings = get_config()

# 配置日志
logger = logging.getLogger(__name__)


class CustomException(Exception):
    """自定义业务异常"""
    
    def __init__(self, message: str, error_code: str = ErrorCode.INTERNAL_ERROR, 
                 status_code: int = 500, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class BusinessException(CustomException):
    """业务逻辑异常"""
    
    def __init__(self, message: str, error_code: str = ErrorCode.INVALID_REQUEST, details: dict = None):
        super().__init__(message, error_code, 400, details)


class AuthenticationException(CustomException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, ErrorCode.UNAUTHORIZED, 401)


class AuthorizationException(CustomException):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, ErrorCode.FORBIDDEN, 403)


class ResourceNotFoundException(CustomException):
    """资源未找到异常"""
    
    def __init__(self, resource: str = "资源"):
        message = f"{resource}不存在"
        super().__init__(message, ErrorCode.NOT_FOUND, 404)


class LLMException(CustomException):
    """大模型服务异常"""
    
    def __init__(self, message: str = "AI服务暂时不可用", error_code: str = ErrorCode.LLM_API_ERROR):
        status_code = 503 if error_code == ErrorCode.LLM_API_ERROR else 504
        super().__init__(message, error_code, status_code)


class FileProcessingException(CustomException):
    """文件处理异常"""
    
    def __init__(self, message: str, error_code: str = ErrorCode.FILE_UPLOAD_ERROR):
        super().__init__(message, error_code, 400)


class ValidationException(CustomException):
    """参数验证异常"""
    
    def __init__(self, message: str, error_code: str = ErrorCode.INVALID_REQUEST, details: dict = None):
        super().__init__(message, error_code, 400, details)


def generate_request_id() -> str:
    """生成请求ID"""
    return str(uuid.uuid4())


def log_exception(request: Request, exc: Exception, request_id: str):
    """记录异常日志"""
    logger.error(
        f"Request ID: {request_id} | "
        f"Method: {request.method} | "
        f"URL: {request.url} | "
        f"Exception: {type(exc).__name__} | "
        f"Message: {str(exc)}",
        exc_info=True
    )


async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    """自定义异常处理器"""
    request_id = generate_request_id()
    log_exception(request, exc, request_id)
    
    response = ResponseBuilder.error(
        message=exc.message,
        error_code=exc.error_code,
        data=exc.details if exc.details else None,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode='json')
    )


async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]) -> JSONResponse:
    """HTTP异常处理器"""
    request_id = generate_request_id()
    log_exception(request, exc, request_id)
    
    # 映射HTTP状态码到错误代码
    error_code_mapping = {
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        400: ErrorCode.INVALID_REQUEST,
    }
    
    error_code = error_code_mapping.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    
    response = ResponseBuilder.error(
        message=exc.detail if hasattr(exc, 'detail') else str(exc),
        error_code=error_code,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode='json')
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求验证异常处理器"""
    request_id = generate_request_id()
    log_exception(request, exc, request_id)
    
    # 转换验证错误格式
    validation_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append(
            CustomValidationError(
                field=field,
                message=error["msg"],
                value=error.get("input")
            )
        )
    
    response = ResponseBuilder.validation_error(
        errors=validation_errors,
        message="请求参数验证失败",
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=400,
        content=response.model_dump(mode='json')
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """SQLAlchemy异常处理器"""
    request_id = generate_request_id()
    log_exception(request, exc, request_id)
    
    # 处理不同类型的数据库异常
    if isinstance(exc, IntegrityError):
        message = "数据完整性约束违反"
        error_code = ErrorCode.INVALID_REQUEST
        status_code = 400
    else:
        message = "数据库操作失败"
        error_code = ErrorCode.INTERNAL_ERROR
        status_code = 500
    
    response = ResponseBuilder.error(
        message=message,
        error_code=error_code,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(mode='json')
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    request_id = generate_request_id()
    log_exception(request, exc, request_id)
    
    # 在开发环境中包含堆栈跟踪
    stack_trace = None
    if hasattr(settings, 'DEBUG') and settings.DEBUG:
        stack_trace = traceback.format_exc()
    
    response = DetailedErrorResponse(
        success=False,
        message="内部服务器错误",
        error_code=ErrorCode.INTERNAL_ERROR,
        request_id=request_id,
        stack_trace=stack_trace
    )
    
    return JSONResponse(
        status_code=500,
        content=response.model_dump(exclude_none=True, mode='json')
    )


def setup_exception_handlers(app):
    """设置异常处理器"""
    
    # 自定义异常
    app.add_exception_handler(CustomException, custom_exception_handler)
    
    # HTTP异常
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # 验证异常
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 数据库异常
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # 全局异常
    app.add_exception_handler(Exception, global_exception_handler)
    
    logger.info("异常处理器设置完成")


# 异常工具函数
def raise_not_found(resource: str = "资源"):
    """抛出资源未找到异常"""
    raise ResourceNotFoundException(resource)


def raise_unauthorized(message: str = "未授权访问"):
    """抛出未授权异常"""
    raise AuthenticationException(message)


def raise_forbidden(message: str = "权限不足"):
    """抛出权限不足异常"""
    raise AuthorizationException(message)


def raise_business_error(message: str, error_code: str = ErrorCode.INVALID_REQUEST, details: dict = None):
    """抛出业务异常"""
    raise BusinessException(message, error_code, details)


def raise_llm_error(message: str = "AI服务暂时不可用", error_code: str = ErrorCode.LLM_API_ERROR):
    """抛出大模型异常"""
    raise LLMException(message, error_code)


def raise_file_error(message: str, error_code: str = ErrorCode.FILE_UPLOAD_ERROR):
    """抛出文件处理异常"""
    raise FileProcessingException(message, error_code)