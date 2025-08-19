#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手AI服务配置文件
包含各种AI服务的配置参数
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class ModelProvider(Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    QWEN = "qwen"
    CLAUDE = "claude"
    GEMINI = "gemini"

class ServiceMode(Enum):
    """服务模式枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class ModelConfig:
    """模型配置"""
    provider: ModelProvider
    model_name: str
    api_key: str
    base_url: str = None
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30

@dataclass
class ServiceConfig:
    """服务配置"""
    service_name: str
    enabled: bool = True
    max_concurrent_requests: int = 10
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 缓存时间（秒）
    retry_attempts: int = 3
    retry_delay: float = 1.0

class AIServiceConfig:
    """AI服务配置管理器"""
    
    def __init__(self, mode: ServiceMode = ServiceMode.DEVELOPMENT):
        self.mode = mode
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        # 基础配置
        self.debug = self.mode == ServiceMode.DEVELOPMENT
        self.log_level = "DEBUG" if self.debug else "INFO"
        
        # API配置
        self.api_config = {
            "host": os.getenv("AI_SERVICE_HOST", "0.0.0.0"),
            "port": int(os.getenv("AI_SERVICE_PORT", "8000")),
            "reload": self.debug,
            "workers": 1 if self.debug else 4
        }
        
        # 模型配置
        self.model_configs = {
            ModelProvider.OPENAI: ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url=os.getenv("OPENAI_BASE_URL"),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            ),
            ModelProvider.QWEN: ModelConfig(
                provider=ModelProvider.QWEN,
                model_name=os.getenv("QWEN_MODEL", "qwen-max"),
                api_key=os.getenv("QWEN_API_KEY", ""),
                base_url=os.getenv("QWEN_BASE_URL"),
                max_tokens=int(os.getenv("QWEN_MAX_TOKENS", "2000")),
                temperature=float(os.getenv("QWEN_TEMPERATURE", "0.7"))
            )
        }
        
        # 服务配置
        self.service_configs = {
            "lesson_prep": ServiceConfig(
                service_name="备课助手服务",
                enabled=True,
                max_concurrent_requests=int(os.getenv("LESSON_PREP_MAX_REQUESTS", "10")),
                cache_enabled=True,
                cache_ttl=int(os.getenv("LESSON_PREP_CACHE_TTL", "3600"))
            ),
            "classroom_ai": ServiceConfig(
                service_name="课堂AI助手服务",
                enabled=True,
                max_concurrent_requests=int(os.getenv("CLASSROOM_AI_MAX_REQUESTS", "15")),
                cache_enabled=True,
                cache_ttl=int(os.getenv("CLASSROOM_AI_CACHE_TTL", "1800"))
            ),
            "grade_management": ServiceConfig(
                service_name="成绩管理服务",
                enabled=True,
                max_concurrent_requests=int(os.getenv("GRADE_MGMT_MAX_REQUESTS", "20")),
                cache_enabled=True,
                cache_ttl=int(os.getenv("GRADE_MGMT_CACHE_TTL", "7200"))
            )
        }
        
        # 提示词配置
        self.prompt_configs = {
            "material_analysis": {
                "system_prompt": "你是一位资深的教育专家，擅长分析教学材料。请根据提供的教材内容，进行深入的教学分析。",
                "max_length": 1500,
                "include_examples": True
            },
            "lesson_planning": {
                "system_prompt": "你是一位经验丰富的教师，擅长制定详细的教学计划。请根据教学目标和学生情况，设计合理的教学环节。",
                "max_length": 2000,
                "include_timeline": True
            },
            "student_analysis": {
                "system_prompt": "你是一位教育心理学专家，擅长分析学生的学习情况和特点。请基于学生数据进行深入分析。",
                "max_length": 1200,
                "include_recommendations": True
            },
            "real_time_learning": {
                "system_prompt": "你是一位课堂观察专家，能够实时分析学生的学习状态和课堂互动情况。",
                "max_length": 1000,
                "real_time_mode": True
            },
            "experiment_design": {
                "system_prompt": "你是一位实验教学专家，擅长设计安全、有效的教学实验。请根据教学目标设计实验方案。",
                "max_length": 1800,
                "safety_first": True
            },
            "grade_analysis": {
                "system_prompt": "你是一位数据分析专家，擅长分析学生成绩数据，发现学习规律和问题。",
                "max_length": 1500,
                "statistical_analysis": True
            },
            "personalized_guidance": {
                "system_prompt": "你是一位个性化教育专家，能够根据学生特点提供针对性的学习指导建议。",
                "max_length": 1200,
                "personalization_level": "high"
            }
        }
        
        # 缓存配置
        self.cache_config = {
            "enabled": True,
            "backend": os.getenv("CACHE_BACKEND", "memory"),  # memory, redis
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            "default_ttl": int(os.getenv("CACHE_DEFAULT_TTL", "3600")),
            "max_size": int(os.getenv("CACHE_MAX_SIZE", "1000"))
        }
        
        # 日志配置
        self.logging_config = {
            "level": self.log_level,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file_path": os.getenv("LOG_FILE_PATH", "logs/ai_service.log"),
            "max_file_size": int(os.getenv("LOG_MAX_FILE_SIZE", "10485760")),  # 10MB
            "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5"))
        }
        
        # 安全配置
        self.security_config = {
            "api_key_required": os.getenv("API_KEY_REQUIRED", "false").lower() == "true",
            "allowed_origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
            "rate_limit": {
                "enabled": True,
                "requests_per_minute": int(os.getenv("RATE_LIMIT_RPM", "60")),
                "requests_per_hour": int(os.getenv("RATE_LIMIT_RPH", "1000"))
            }
        }
        
        # 监控配置
        self.monitoring_config = {
            "metrics_enabled": True,
            "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
            "performance_tracking": True,
            "error_tracking": True
        }
    
    def get_model_config(self, provider: ModelProvider) -> ModelConfig:
        """获取模型配置"""
        return self.model_configs.get(provider)
    
    def get_service_config(self, service_name: str) -> ServiceConfig:
        """获取服务配置"""
        return self.service_configs.get(service_name)
    
    def get_prompt_config(self, prompt_type: str) -> Dict[str, Any]:
        """获取提示词配置"""
        return self.prompt_configs.get(prompt_type, {})
    
    def is_service_enabled(self, service_name: str) -> bool:
        """检查服务是否启用"""
        config = self.get_service_config(service_name)
        return config.enabled if config else False
    
    def get_primary_model_provider(self) -> ModelProvider:
        """获取主要模型提供商"""
        # 优先级：OpenAI > Qwen > 其他
        for provider in [ModelProvider.OPENAI, ModelProvider.QWEN]:
            config = self.get_model_config(provider)
            if config and config.api_key:
                return provider
        return ModelProvider.OPENAI  # 默认返回OpenAI
    
    def validate_config(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 检查模型配置
        primary_provider = self.get_primary_model_provider()
        primary_config = self.get_model_config(primary_provider)
        if not primary_config or not primary_config.api_key:
            errors.append(f"主要模型提供商 {primary_provider.value} 的API密钥未配置")
        
        # 检查服务配置
        for service_name, config in self.service_configs.items():
            if config.enabled and config.max_concurrent_requests <= 0:
                errors.append(f"服务 {service_name} 的最大并发请求数配置无效")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "mode": self.mode.value,
            "debug": self.debug,
            "api_config": self.api_config,
            "cache_config": self.cache_config,
            "logging_config": self.logging_config,
            "security_config": self.security_config,
            "monitoring_config": self.monitoring_config,
            "services": {name: {
                "name": config.service_name,
                "enabled": config.enabled,
                "max_concurrent_requests": config.max_concurrent_requests,
                "cache_enabled": config.cache_enabled,
                "cache_ttl": config.cache_ttl
            } for name, config in self.service_configs.items()}
        }

# 全局配置实例
config = AIServiceConfig()

# 配置验证
config_errors = config.validate_config()
if config_errors:
    print("配置验证警告:")
    for error in config_errors:
        print(f"  - {error}")