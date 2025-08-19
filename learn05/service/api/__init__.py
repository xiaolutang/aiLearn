# -*- coding: utf-8 -*-
"""
API接口模块
提供所有HTTP接口定义
"""

from fastapi import APIRouter

# 导入各个API模块
def get_api_router():
    """获取API路由器实例，整合所有API路由
    
    Returns:
        APIRouter: 包含所有API路由的路由器实例
    """
    # 创建主API路由器
    api_router = APIRouter(prefix="/api", tags=["API"])
    
    # 导入并注册用户API路由
    from .user_api import router as user_router
    api_router.include_router(user_router, prefix="/users", tags=["Users"])
    
    # 导入并注册成绩API路由
    from .grade_api import router as grade_router
    api_router.include_router(grade_router, prefix="/grades", tags=["Grades"])
    
    # 导入并注册班级API路由
    from .class_api import router as class_router
    api_router.include_router(class_router, prefix="/classes", tags=["Classes"])
    
    return api_router