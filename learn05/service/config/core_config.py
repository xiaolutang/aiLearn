# -*- coding: utf-8 -*-
"""
核心配置文件
统一管理各种配置信息
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """应用配置类"""
    
    def __init__(self):
        # 基础路径设置
        self.BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.SERVICE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # 数据库配置
        self.DB_PATH = os.getenv('DB_PATH', str(self.BASE_DIR / 'student_database.db'))
        self.SQLALCHEMY_DATABASE_URL = f"sqlite:///{self.DB_PATH}"
        
        # FastAPI 配置
        self.FASTAPI_HOST = os.getenv('FASTAPI_HOST', '127.0.0.1')
        self.FASTAPI_PORT = int(os.getenv('FASTAPI_PORT', '8000'))
        self.FASTAPI_DEBUG = os.getenv('FASTAPI_DEBUG', 'True').lower() == 'true'
        
        # 日志配置
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', str(self.BASE_DIR / 'app.log'))
        
        # 认证配置
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
        self.ALGORITHM = os.getenv('ALGORITHM', 'HS256')
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
        
        # JWT配置对象
        self.jwt = type('JWT', (), {
            'secret_key': self.SECRET_KEY,
            'algorithm': self.ALGORITHM,
            'access_token_expire_minutes': self.ACCESS_TOKEN_EXPIRE_MINUTES
        })()
        
        # 大模型配置
        self.LLM_CONFIG = {
            "model": os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
            "api_key": os.getenv('LLM_API_KEY', os.getenv('OPENAI_API_KEY')),
            "temperature": float(os.getenv('LLM_TEMPERATURE', '0.1')),
            "base_url": os.getenv('LLM_BASE_URL')
        }
        
        # 速率限制配置
        self.RATE_LIMIT = {
            "requests_per_minute": int(os.getenv('RATE_LIMIT_RPM', '60')),
            "tokens_per_minute": int(os.getenv('RATE_LIMIT_TPM', '150000'))
        }
        
        # CORS配置
        self.CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost,http://localhost:8080').split(',')
        
        # 上传文件夹配置
        self.UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(self.BASE_DIR / '../uploads'))
        
        # 其他配置可以继续添加在这里
        
        # 重试配置
        self.RETRY_CONFIG = {
            "max_retries": int(os.getenv('RETRY_MAX', '3')),
            "retry_delay": int(os.getenv('RETRY_DELAY', '1')),
            "backoff_factor": float(os.getenv('RETRY_BACKOFF', '2'))
        }
        
    def get_db_url(self) -> str:
        """获取数据库URL"""
        return self.SQLALCHEMY_DATABASE_URL
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取大模型配置"""
        return self.LLM_CONFIG
    
    def get_fastapi_config(self) -> Dict[str, Any]:
        """获取FastAPI配置"""
        return {
            "host": self.FASTAPI_HOST,
            "port": self.FASTAPI_PORT,
            "debug": self.FASTAPI_DEBUG
        }


# 创建全局配置实例
global_config = Config()


# 导出常用配置
def get_config() -> Config:
    """获取全局配置实例"""
    return global_config


def get_db_url() -> str:
    """获取数据库URL"""
    return global_config.get_db_url()


def get_llm_config() -> Dict[str, Any]:
    """获取大模型配置"""
    return global_config.get_llm_config()


def get_rate_limit_config() -> Dict[str, Any]:
    """获取速率限制配置"""
    return global_config.RATE_LIMIT


def get_retry_config() -> Dict[str, Any]:
    """获取重试配置"""
    return {
        "max_retries": 3,
        "backoff_factor": 1.0,
        "retry_on_timeout": True,
        "retry_on_rate_limit": True
    }