# -*- coding: utf-8 -*-
"""
统一API响应格式模型

本模块定义了标准化的API响应格式，确保所有接口返回一致的数据结构。
"""

from typing import Optional, Any, Dict, List, Union, Generic, TypeVar
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

T = TypeVar('T')

class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class ErrorCode(str, Enum):
    """错误代码枚举"""
    # 通用错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    
    # 业务错误
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    DUPLICATE_USER = "DUPLICATE_USER"
    GRADE_NOT_FOUND = "GRADE_NOT_FOUND"
    INVALID_GRADE_DATA = "INVALID_GRADE_DATA"
    CLASS_NOT_FOUND = "CLASS_NOT_FOUND"
    STUDENT_NOT_FOUND = "STUDENT_NOT_FOUND"
    
    # 大模型相关错误
    LLM_API_ERROR = "LLM_API_ERROR"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_QUOTA_EXCEEDED = "LLM_QUOTA_EXCEEDED"
    
    # 文件处理错误
    FILE_UPLOAD_ERROR = "FILE_UPLOAD_ERROR"
    FILE_FORMAT_ERROR = "FILE_FORMAT_ERROR"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"


class APIResponse(BaseModel, Generic[T]):
    """标准API响应格式"""
    
    success: bool = Field(description="请求是否成功")
    message: str = Field(description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    
    items: List[T] = Field(description="数据列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")
    
    @classmethod
    def create(cls, items: List[Any], total: int, page: int, page_size: int):
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class ValidationError(BaseModel):
    """验证错误详情"""
    
    field: str = Field(description="字段名")
    message: str = Field(description="错误消息")
    value: Optional[Any] = Field(default=None, description="错误值")


class DetailedErrorResponse(APIResponse):
    """详细错误响应格式"""
    
    errors: Optional[List[ValidationError]] = Field(default=None, description="详细错误列表")
    stack_trace: Optional[str] = Field(default=None, description="堆栈跟踪（仅开发环境）")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 响应构建器
class ResponseBuilder:
    """响应构建器"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", request_id: str = None) -> APIResponse:
        """构建成功响应"""
        return APIResponse(
            success=True,
            message=message,
            data=data,
            request_id=request_id
        )
    
    @staticmethod
    def error(message: str, error_code: str = None, data: Any = None, request_id: str = None) -> APIResponse:
        """构建错误响应"""
        return APIResponse(
            success=False,
            message=message,
            error_code=error_code or ErrorCode.INTERNAL_ERROR,
            data=data,
            request_id=request_id
        )
    
    @staticmethod
    def validation_error(errors: List[ValidationError], message: str = "数据验证失败", request_id: str = None) -> DetailedErrorResponse:
        """构建验证错误响应"""
        return DetailedErrorResponse(
            success=False,
            message=message,
            error_code=ErrorCode.INVALID_REQUEST,
            errors=errors,
            request_id=request_id
        )
    
    @staticmethod
    def paginated(items: List[Any], total: int, page: int, page_size: int, 
                 message: str = "查询成功", request_id: str = None) -> APIResponse:
        """构建分页响应"""
        paginated_data = PaginatedResponse.create(items, total, page, page_size)
        return APIResponse(
            success=True,
            message=message,
            data=paginated_data.dict(),
            request_id=request_id
        )


# 常用响应
class CommonResponses:
    """常用响应模板"""
    
    @staticmethod
    def unauthorized(message: str = "未授权访问") -> APIResponse:
        return ResponseBuilder.error(message, ErrorCode.UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message: str = "权限不足") -> APIResponse:
        return ResponseBuilder.error(message, ErrorCode.FORBIDDEN)
    
    @staticmethod
    def not_found(resource: str = "资源") -> APIResponse:
        return ResponseBuilder.error(f"{resource}不存在", ErrorCode.NOT_FOUND)
    
    @staticmethod
    def invalid_request(message: str = "请求参数无效") -> APIResponse:
        return ResponseBuilder.error(message, ErrorCode.INVALID_REQUEST)
    
    @staticmethod
    def internal_error(message: str = "内部服务器错误") -> APIResponse:
        return ResponseBuilder.error(message, ErrorCode.INTERNAL_ERROR)
    
    @staticmethod
    def llm_error(message: str = "AI服务暂时不可用") -> APIResponse:
        return ResponseBuilder.error(message, ErrorCode.LLM_API_ERROR)


# HTTP状态码映射
HTTP_STATUS_MAPPING = {
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.INVALID_REQUEST: 400,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.LLM_API_ERROR: 503,
    ErrorCode.LLM_TIMEOUT: 504,
    ErrorCode.FILE_UPLOAD_ERROR: 400,
    ErrorCode.FILE_FORMAT_ERROR: 400,
    ErrorCode.FILE_SIZE_EXCEEDED: 413,
}


def get_http_status(error_code: str) -> int:
    """根据错误代码获取HTTP状态码"""
    return HTTP_STATUS_MAPPING.get(error_code, 500)