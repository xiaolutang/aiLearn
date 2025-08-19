#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手 - 配置文件
存储应用程序的配置信息
"""

import os
from datetime import timedelta

class Config:
    """基础配置类"""
    # 应用程序名称
    APP_NAME = "智能教学助手"
    APP_VERSION = "1.0.0"
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///./student_database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT认证配置
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key-here-change-it-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or "./uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # LLM服务配置 - 简化为内部服务对接
    LLM_SERVICE_CONFIG = {
        "base_url": os.environ.get("LLM_SERVICE_URL") or "http://localhost:8000",
        "timeout": int(os.environ.get("LLM_SERVICE_TIMEOUT") or "30"),
        "retry_times": int(os.environ.get("LLM_SERVICE_RETRY") or "3"),
        "health_check_interval": int(os.environ.get("LLM_HEALTH_CHECK_INTERVAL") or "60")
    }
    
    # 缓存配置
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 日志配置
    LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 限流配置
    RATE_LIMIT_DEFAULT = "100/hour"
    
    # 安全配置
    CORS_ORIGINS = ["*"]  # 生产环境中应该设置为具体的域名
    
    # 调试模式
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """开发环境配置"""
    # 开发环境使用SQLite数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or "sqlite:///./student_database.db"
    
    # 开发环境启用调试模式
    DEBUG = True
    TESTING = True
    
    # 开发环境中的日志级别
    LOG_LEVEL = "DEBUG"

class TestingConfig(Config):
    """测试环境配置"""
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    
    # 测试环境启用测试模式
    TESTING = True
    
    # 测试环境禁用CSRF保护
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    # 生产环境使用MySQL或PostgreSQL数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "mysql+pymysql://username:password@localhost/intelligent_teaching_assistant"
    
    # 生产环境禁用调试模式
    DEBUG = False
    TESTING = False
    
    # 生产环境中的日志级别
    LOG_LEVEL = "INFO"
    
    # 生产环境中的CORS配置
    CORS_ORIGINS = ["https://your-frontend-domain.com"]
    
    # 生产环境中的JWT配置
    SECRET_KEY = os.environ.get("SECRET_KEY")  # 生产环境中必须设置环境变量
    
    # 生产环境中的大模型配置
    LLM_API_KEY = os.environ.get("LLM_API_KEY")  # 生产环境中必须设置环境变量
    ALIBABA_CLOUD_API_KEY = os.environ.get("ALIBABA_CLOUD_API_KEY")  # 生产环境中必须设置环境变量
    ALIBABA_CLOUD_API_SECRET = os.environ.get("ALIBABA_CLOUD_API_SECRET")  # 生产环境中必须设置环境变量

# 根据环境变量选择配置类
def get_config():
    """根据环境变量获取配置类"""
    env = os.environ.get("ENVIRONMENT", "development")
    if env.lower() == "production":
        return ProductionConfig()
    elif env.lower() == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

# 创建配置实例
config = get_config()

# 创建上传文件夹
if not os.path.exists(config.UPLOAD_FOLDER):
    os.makedirs(config.UPLOAD_FOLDER)