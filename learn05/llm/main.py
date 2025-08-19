#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手AI服务主启动文件
"""

import os
import sys
import asyncio
import uvicorn
import logging
from pathlib import Path

# 加载环境变量
try:
    from dotenv import load_dotenv
    # 加载当前目录的.env文件
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"已加载环境变量文件: {env_path}")
    else:
        print(f"环境变量文件不存在: {env_path}")
except ImportError:
    print("警告: python-dotenv未安装，无法自动加载.env文件")

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import get_llm_config
from config.settings import ServiceMode
from utils import global_monitor
from api.ai_service_api import app

def setup_logging():
    """设置日志"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    # 创建logs目录
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                logs_dir / "ai_service.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("日志系统初始化完成")
    return logger

def validate_environment():
    """验证环境配置"""
    logger = logging.getLogger(__name__)
    
    # 检查必要的目录
    required_dirs = ["logs", "cache"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        logger.info(f"确保目录存在: {dir_path}")
    
    logger.info("环境验证完成")

async def startup_event():
    """应用启动事件"""
    logger = logging.getLogger(__name__)
    logger.info("智能教学助手AI服务启动中...")
    
    # 启动监控
    if config.monitoring_config["metrics_enabled"]:
        global_monitor.start_monitoring(
            interval=config.monitoring_config["health_check_interval"]
        )
        logger.info("性能监控已启动")
    
    # 预热服务
    try:
        from services.lesson_prep_service import LessonPrepService
        from services.classroom_ai_service import ClassroomAIService
        from services.grade_management_service import GradeManagementService
        from factory import LLMFactory
        
        llm_factory = LLMFactory()
        
        # 初始化服务（预热）
        lesson_prep = LessonPrepService(llm_factory)
        classroom_ai = ClassroomAIService(llm_factory)
        grade_mgmt = GradeManagementService(llm_factory)
        
        logger.info("AI服务模块预热完成")
        
    except Exception as e:
        logger.error(f"服务预热失败: {str(e)}")
    
    logger.info("智能教学助手AI服务启动完成")

async def shutdown_event():
    """应用关闭事件"""
    logger = logging.getLogger(__name__)
    logger.info("智能教学助手AI服务关闭中...")
    
    # 停止监控
    await global_monitor.stop_monitoring()
    logger.info("性能监控已停止")
    
    logger.info("智能教学助手AI服务已关闭")

def create_app():
    """创建应用实例"""
    # 添加启动和关闭事件
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)
    
    return app

def main():
    """主函数"""
    # 设置日志
    logger = setup_logging()
    logger.info("智能教学助手AI服务初始化")
    
    # 验证环境
    validate_environment()
    
    # 获取配置
    config = get_llm_config()
    
    # 显示配置信息
    logger.info(f"运行模式: development")
    logger.info(f"API地址: http://localhost:8000")
    logger.info(f"调试模式: True")
    
    # 创建应用
    app_instance = create_app()
    
    # 启动服务器
    try:
        uvicorn.run(
            "api.ai_service_api:app",
            host="localhost",
            port=8000,
            reload=True,
            workers=1,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()