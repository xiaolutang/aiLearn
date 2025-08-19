# -*- coding: utf-8 -*-
"""
核心服务层

本模块包含智能教学助手的核心业务逻辑和服务组件。
"""

from .ai_service import AIServiceManager
from .homework_service import HomeworkGradingService
from .teaching_service import TeachingService
from .teaching_prep_service import TeachingPrepService
from .classroom_ai_service import ClassroomAIService
from .analytics_service import AnalyticsService
from .cache_service import CacheManager
from .task_service import TaskManager

__all__ = [
    "AIServiceManager",
    "HomeworkGradingService", 
    "TeachingService",
    "TeachingPrepService",
    "ClassroomAIService",
    "AnalyticsService",
    "CacheManager",
    "TaskManager"
]