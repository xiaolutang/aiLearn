# -*- coding: utf-8 -*-
"""
智能教学助手主应用

本模块是智能教学助手的主应用入口，负责初始化FastAPI应用、
配置中间件、注册路由和管理应用生命周期。
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime
from sqlalchemy.orm import Session

# 导入数据库相关
from database import get_db as _get_db, Base, User, engine
from user_management import init_system_roles, init_system_admin

# 导入新的API路由
from api.v1 import api_v1_router
from llm_api import router as llm_router

# 导入中间件和异常处理
from middleware.exception_handler import setup_exception_handlers
from middleware import setup_middleware, get_middleware_manager
from models.response import APIResponse, ResponseBuilder

# 导入原有路由（保持兼容性）
# from .auth import router as auth_router  # auth router已在api.v1中定义
# from .grade_management import router as grade_router  # grade router已在api.v1中定义
# from .tutoring_service import router as tutoring_router  # tutoring router已在api.v1中定义
# from .analytics import router as analytics_router  # analytics router已在api.v1中定义

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库会话依赖
def get_db():
    """获取数据库会话"""
    yield from _get_db()

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("智能教学助手服务启动中...")
    
    try:
        # 初始化数据库
        db = next(get_db())
        Base.metadata.create_all(bind=engine)
        
        # 初始化系统角色和管理员
        init_system_roles(db)
        init_system_admin("admin", "admin123", "admin@example.com", "系统管理员", db)
        
        logger.info("数据库初始化完成")
        logger.info("智能教学助手服务启动完成！")
        
    except Exception as e:
        logger.error(f"服务启动时出错: {str(e)}")
    
    yield
    
    # 关闭时清理
    logger.info("智能教学助手服务关闭中...")

# FastAPI应用初始化
app = FastAPI(
    title="智能教学助手",
    description="高效成绩录入与分析、班级及年级成绩综合分析、学生个性化成绩分析及练题指导、辅导方案生成等功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 设置异常处理
setup_exception_handlers(app)

# 设置所有中间件（包括CORS、性能监控、缓存、限流、压缩等）
setup_middleware(app, {
    "cors": {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"]
    },
    "performance": {
        "enable_monitoring": True,
        "enable_logging": True
    },
    "cache": {
        "enable_api_cache": True,
        "default_ttl": 300
    },
    "rate_limit": {
        "default_rate": "100/minute",
        "enable_ip_whitelist": True
    },
    "compression": {
        "enable_gzip": True,
        "enable_brotli": True,
        "min_size": 1024
    }
})

# 注册API路由
app.include_router(api_v1_router)
app.include_router(llm_router)

# 保持向后兼容的路由（已迁移到api.v1）
# app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
# app.include_router(grade_router, prefix="/api/grades", tags=["成绩管理"])
# app.include_router(tutoring_router, prefix="/api/tutoring", tags=["辅导服务"])
# app.include_router(sql_agent_router, prefix="/api/sql-agent", tags=["SQL智能助手"])

# 系统基础路由
@app.get("/")
def root():
    """系统根路径"""
    return ResponseBuilder.success(
        message="智能教学助手服务运行中",
        data={"version": "1.0.0"}
    )

@app.get("/health")
def health_check():
    """系统健康检查"""
    return ResponseBuilder.success(
        message="系统运行正常",
        data={
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/api/info")
def api_info():
    """获取API信息"""
    return {
        "name": "智能教学助手API",
        "version": "1.0.0",
        "description": "提供成绩管理、数据分析、AI辅导等功能",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "api_v1": "/api/v1",
            "llm": "/llm",
            "performance": "/api/performance"
        }
    }

@app.get("/api/performance")
def get_performance_stats():
    """获取系统性能统计信息"""
    try:
        middleware_manager = get_middleware_manager()
        stats = middleware_manager.get_performance_stats()
        
        return ResponseBuilder.success(
            data=stats,
            message="性能统计信息获取成功"
        )
    except Exception as e:
        logger.error(f"获取性能统计失败: {e}")
        return ResponseBuilder.error(
            message="获取性能统计失败",
            error_code="PERFORMANCE_STATS_ERROR"
        )

@app.post("/api/performance/clear-cache")
def clear_all_caches():
    """清除所有缓存"""
    try:
        middleware_manager = get_middleware_manager()
        import asyncio
        
        # 创建异步任务清除缓存
        async def clear_cache_task():
            await middleware_manager.clear_all_caches()
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(clear_cache_task())
        else:
            loop.run_until_complete(clear_cache_task())
        
        return ResponseBuilder.success(
            message="所有缓存已清除"
        )
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return ResponseBuilder.error(
            message="清除缓存失败",
            error_code="CACHE_CLEAR_ERROR"
        )

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)