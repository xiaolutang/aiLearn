# -*- coding: utf-8 -*-
"""
异常类导出模块

从middleware.exception_handler导出常用的异常类，方便其他模块使用。
"""

from middleware.exception_handler import (
    CustomException,
    BusinessException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    LLMException,
    FileProcessingException,
    ValidationException,
    raise_not_found,
    raise_unauthorized,
    raise_forbidden,
    raise_business_error,
    raise_llm_error,
    raise_file_error
)

__all__ = [
    'CustomException',
    'BusinessException',
    'AuthenticationException',
    'AuthorizationException',
    'ResourceNotFoundException',
    'LLMException',
    'FileProcessingException',
    'ValidationException',
    'raise_not_found',
    'raise_unauthorized',
    'raise_forbidden',
    'raise_business_error',
    'raise_llm_error',
    'raise_file_error'
]