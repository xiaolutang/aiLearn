# -*- coding: utf-8 -*-
"""
API v1 路由模块

本模块提供API v1版本的路由配置和管理。
"""

from fastapi import APIRouter
from api.v1.auth import router as auth_router
from api.v1.users import router as users_router
from api.v1.grades import router as grades_router
from api.v1.tutoring import router as tutoring_router
from api.v1.analytics import router as analytics_router
from api.v1.system import router as system_router
from api.v1.ai import router as ai_router
from api.v1.homework import router as homework_router
from api.v1.teaching_prep import router as teaching_prep_router
from api.v1.classroom import router as classroom_router
from api.v1.dashboard import router as dashboard_router
from api.v1.experiment import router as experiment_router
from api.v1.classroom_ai import router as classroom_ai_router
from api.v1.ai_service_integration import router as ai_service_router

# 创建v1路由器
api_v1_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_v1_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["认证"]
)

api_v1_router.include_router(
    users_router,
    prefix="/users",
    tags=["用户管理"]
)

api_v1_router.include_router(
    grades_router,
    prefix="/grades",
    tags=["成绩管理"]
)

api_v1_router.include_router(
    tutoring_router,
    prefix="/tutoring",
    tags=["辅导方案"]
)

api_v1_router.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["数据分析"]
)

api_v1_router.include_router(
    system_router,
    prefix="/system",
    tags=["系统管理"]
)

api_v1_router.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI服务"]
)

api_v1_router.include_router(
    homework_router,
    prefix="/homework",
    tags=["作业批改"]
)

api_v1_router.include_router(
    teaching_prep_router,
    prefix="/prepare",
    tags=["备课助手"]
)

api_v1_router.include_router(
    classroom_router,
    prefix="/classroom",
    tags=["课堂管理"]
)

api_v1_router.include_router(
    experiment_router,
    prefix="/experiment",
    tags=["实验设计"]
)

api_v1_router.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["工作台"]
)

api_v1_router.include_router(
    classroom_ai_router,
    prefix="/classroom",
    tags=["课堂AI助手"]
)

api_v1_router.include_router(
    ai_service_router,
    prefix="/ai-service",
    tags=["AI服务集成"]
)

__all__ = ["api_v1_router"]