# -*- coding: utf-8 -*-
"""
智能教学助手后端服务主入口
"""

# 首先加载环境变量
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ai_teaching_assistant")

# 导入配置和API路由
from config import get_config, Config
from api import get_api_router

# 创建配置实例
config = get_config()

# 定义应用生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器
    
    Args:
        app: FastAPI应用实例
        
    Yields:
        None
    """
    logger.info("智能教学助手后端服务启动中...")
    
    # 确保上传目录存在
    upload_dir = Path("uploads")  # 使用默认上传目录
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 应用启动前的初始化操作
    try:
        # 初始化数据库连接
        logger.info(f"数据库连接初始化: {config.SQLALCHEMY_DATABASE_URL}")
        # 这里可以添加数据库迁移、预加载数据等操作
    except Exception as e:
        logger.error(f"应用初始化失败: {e}")
        raise
    
    yield
    
    # 应用关闭前的清理操作
    logger.info("智能教学助手后端服务关闭中...")
    # 这里可以添加关闭数据库连接、清理资源等操作
    

# 创建FastAPI应用
app = FastAPI(
    title="智能教学助手",
    description="提供高效成绩录入与分析、班级及年级成绩综合分析、学生个性化成绩分析及练题指导、辅导方案生成等功能。",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI文档
    redoc_url="/redoc"  # ReDoc文档
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求响应时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加请求处理时间到响应头
    
    Args:
        request: HTTP请求
        call_next: 下一个中间件或路由处理函数
        
    Returns:
        Response: HTTP响应
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录请求日志
    logger.info(
        f"{request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s"
    )
    
    return response

# 添加全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器
    
    Args:
        request: HTTP请求
        exc: 异常实例
        
    Returns:
        JSONResponse: 异常响应
    """
    logger.error(f"请求处理异常: {exc}", exc_info=True)
    
    # 为HTTPException保持原始状态码和详情
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error": str(exc)}
        )
    
    # 其他异常返回500状态码
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误", "error": str(exc)}
    )

# 挂载静态文件目录
static_dir = getattr(config, 'STATIC_DIR', None)
if static_dir and os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 挂载上传文件目录（用于测试和开发）
if config.UPLOAD_FOLDER and os.path.exists(config.UPLOAD_FOLDER):
    app.mount("/uploads", StaticFiles(directory=config.UPLOAD_FOLDER), name="uploads")

# 注册API路由
api_router = get_api_router()
app.include_router(api_router, prefix="/api", tags=["API"])

# 根路径路由
@app.get("/")
async def root():
    """根路径路由
    
    Returns:
        Dict[str, str]: 欢迎信息
    """
    return {
        "message": "欢迎使用智能教学助手后端服务",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康检查路由
@app.get("/health")
async def health_check():
    """健康检查路由
    
    Returns:
        Dict[str, str]: 健康状态
    """
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0.0"
    }

# 启动服务（仅当直接运行此文件时）
if __name__ == "__main__":
    # 使用硬编码的默认值或直接从配置中获取
    host = "127.0.0.1"
    port = 8000
    reload = True
    workers = 1
    
    logger.info(f"启动FastAPI服务: http://{host}:{port}")
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers
    )