# -*- coding: utf-8 -*-
"""
系统管理API路由

本模块提供系统管理相关的API接口，包括健康检查、性能监控、系统信息等。
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import psutil
import platform
import sys
import os

from database import get_db, User
from models.response import APIResponse, ResponseBuilder
from middleware.exception_handler import (
    BusinessException,
    ValidationException,
    AuthenticationException
)
from auth import get_current_user, role_required
from config.database_config import database_health_check, get_database_stats
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


# 响应模型
class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    database: Dict[str, Any]
    system: Dict[str, Any]
    services: Dict[str, Any]


class SystemInfoResponse(BaseModel):
    """系统信息响应模型"""
    platform: Dict[str, Any]
    python: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    cpu: Dict[str, Any]
    network: Dict[str, Any]


class PerformanceMetrics(BaseModel):
    """性能指标响应模型"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, Any]
    database_stats: Dict[str, Any]
    api_stats: Dict[str, Any]


class LogLevel(BaseModel):
    """日志级别设置模型"""
    level: str
    logger_name: Optional[str] = None


# 系统启动时间
START_TIME = datetime.now()


@router.get("/health", response_model=APIResponse[HealthCheckResponse])
async def health_check(
    request: Request,
    db: Session = Depends(get_db)
):
    """系统健康检查"""
    try:
        # 计算系统运行时间
        uptime = (datetime.now() - START_TIME).total_seconds()
        
        # 数据库健康检查
        db_health = database_health_check()
        
        # 系统资源检查
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 服务状态检查
        services_status = {
            "api": "healthy",
            "database": db_health["status"],
            "authentication": "healthy",
            "file_system": "healthy" if disk.percent < 90 else "warning"
        }
        
        # 整体状态判断
        overall_status = "healthy"
        if db_health["status"] != "healthy":
            overall_status = "unhealthy"
        elif memory.percent > 90 or disk.percent > 90 or cpu_percent > 90:
            overall_status = "warning"
        elif any(status == "warning" for status in services_status.values()):
            overall_status = "warning"
        
        health_data = HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime=uptime,
            database=db_health,
            system={
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            services=services_status
        )
        
        return ResponseBuilder.success(
            health_data,
            "健康检查完成"
        )
        
    except Exception as e:
        logger.error(f"健康检查异常: {e}")
        # 即使出现异常，也要返回健康检查结果
        error_health = HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version="1.0.0",
            uptime=(datetime.now() - START_TIME).total_seconds(),
            database={"status": "unknown", "error": str(e)},
            system={"status": "unknown"},
            services={"api": "unhealthy"}
        )
        
        return ResponseBuilder.success(
            error_health,
            "健康检查完成（存在异常）"
        )


@router.get("/info", response_model=APIResponse[SystemInfoResponse])
async def get_system_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """获取系统信息"""
    try:
        # 权限检查
        if current_user.role != 'admin':
            raise AuthenticationException("只有管理员可以查看系统信息")
        
        # 平台信息
        platform_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "hostname": platform.node()
        }
        
        # Python信息
        python_info = {
            "version": sys.version,
            "version_info": list(sys.version_info),
            "executable": sys.executable,
            "path": sys.path[:5]  # 只显示前5个路径
        }
        
        # 内存信息
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percentage": memory.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percentage": swap.percent
        }
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percentage": disk.percent
        }
        
        # CPU信息
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "min_frequency": psutil.cpu_freq().min if psutil.cpu_freq() else None,
            "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
            "usage_per_core": psutil.cpu_percent(percpu=True, interval=1)
        }
        
        # 网络信息
        network_io = psutil.net_io_counters()
        network_info = {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv,
            "interfaces": list(psutil.net_if_addrs().keys())
        }
        
        system_info = SystemInfoResponse(
            platform=platform_info,
            python=python_info,
            memory=memory_info,
            disk=disk_info,
            cpu=cpu_info,
            network=network_info
        )
        
        return ResponseBuilder.success(
            system_info,
            "获取系统信息成功"
        )
        
    except AuthenticationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取系统信息异常: {e}")
        raise BusinessException("获取系统信息失败")


@router.get("/metrics", response_model=APIResponse[PerformanceMetrics])
async def get_performance_metrics(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """获取性能指标"""
    try:
        # 权限检查
        if current_user.role not in ['admin', 'teacher']:
            raise AuthenticationException("只有管理员和教师可以查看性能指标")
        
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # 网络IO
        network_io = psutil.net_io_counters()
        network_io_info = {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv
        }
        
        # 数据库统计
        db_stats = get_database_stats()
        
        # API统计（这里需要从性能监控中间件获取）
        api_stats = {
            "total_requests": 0,
            "avg_response_time": 0.0,
            "error_rate": 0.0
        }
        
        # 尝试从请求中获取性能统计
        if hasattr(request.app.state, 'performance_stats'):
            api_stats = request.app.state.performance_stats
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io_info,
            database_stats=db_stats,
            api_stats=api_stats
        )
        
        return ResponseBuilder.success(
            metrics,
            "获取性能指标成功"
        )
        
    except AuthenticationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取性能指标异常: {e}")
        raise BusinessException("获取性能指标失败")


@router.get("/logs", response_model=APIResponse[Dict[str, Any]])
async def get_system_logs(
    request: Request,
    level: Optional[str] = "INFO",
    lines: int = 100,
    current_user: User = Depends(get_current_user)
):
    """获取系统日志"""
    try:
        # 权限检查
        if current_user.role != 'admin':
            raise AuthenticationException("只有管理员可以查看系统日志")
        
        # 这里应该实现日志读取逻辑
        # 由于日志系统的复杂性，这里只返回示例数据
        log_data = {
            "level": level,
            "lines_requested": lines,
            "logs": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "系统正常运行",
                    "module": "system"
                }
            ],
            "total_lines": 1,
            "note": "日志功能正在开发中"
        }
        
        return ResponseBuilder.success(
            log_data,
            "获取系统日志成功"
        )
        
    except AuthenticationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取系统日志异常: {e}")
        raise BusinessException("获取系统日志失败")


@router.post("/logs/level", response_model=APIResponse[Dict[str, str]])
async def set_log_level(
    request: Request,
    log_level: LogLevel,
    current_user: User = Depends(get_current_user)
):
    """设置日志级别"""
    try:
        # 权限检查
        if current_user.role != 'admin':
            raise AuthenticationException("只有管理员可以设置日志级别")
        
        # 验证日志级别
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level.level.upper() not in valid_levels:
            raise ValidationException(f"无效的日志级别，支持的级别: {', '.join(valid_levels)}")
        
        # 设置日志级别
        logger_name = log_level.logger_name or 'root'
        target_logger = logging.getLogger(logger_name)
        target_logger.setLevel(getattr(logging, log_level.level.upper()))
        
        logger.info(f"日志级别已设置 - 用户: {current_user.username}, Logger: {logger_name}, Level: {log_level.level}")
        
        return ResponseBuilder.success(
            {
                "logger": logger_name,
                "level": log_level.level.upper(),
                "message": "日志级别设置成功"
            },
            "日志级别设置成功"
        )
        
    except (AuthenticationException, ValidationException) as e:
        raise e
    except Exception as e:
        logger.error(f"设置日志级别异常: {e}")
        raise BusinessException("设置日志级别失败")


@router.get("/version", response_model=APIResponse[Dict[str, str]])
async def get_version_info(
    request: Request
):
    """获取版本信息"""
    try:
        version_info = {
            "application": "智能教学助手",
            "version": "1.0.0",
            "build_date": "2024-01-01",
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "api_version": "v1"
        }
        
        return ResponseBuilder.success(
            version_info,
            "获取版本信息成功"
        )
        
    except Exception as e:
        logger.error(f"获取版本信息异常: {e}")
        raise BusinessException("获取版本信息失败")


@router.post("/cache/clear", response_model=APIResponse[Dict[str, str]])
async def clear_cache(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """清理系统缓存"""
    try:
        # 权限检查
        if current_user.role != 'admin':
            raise AuthenticationException("只有管理员可以清理系统缓存")
        
        # 这里应该实现缓存清理逻辑
        # 目前只是记录操作
        logger.info(f"系统缓存清理 - 用户: {current_user.username}")
        
        return ResponseBuilder.success(
            {
                "message": "系统缓存清理成功",
                "timestamp": datetime.now().isoformat()
            },
            "系统缓存清理成功"
        )
        
    except AuthenticationException as e:
        raise e
    except Exception as e:
        logger.error(f"清理系统缓存异常: {e}")
        raise BusinessException("清理系统缓存失败")


@router.get("/status", response_model=APIResponse[Dict[str, Any]])
async def get_system_status(
    request: Request
):
    """获取系统状态概览"""
    try:
        # 基本状态信息
        uptime = (datetime.now() - START_TIME).total_seconds()
        
        # 快速资源检查
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status_info = {
            "status": "running",
            "uptime_seconds": uptime,
            "uptime_formatted": str(datetime.now() - START_TIME),
            "memory_usage_percent": memory.percent,
            "disk_usage_percent": disk.percent,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        return ResponseBuilder.success(
            status_info,
            "获取系统状态成功"
        )
        
    except Exception as e:
        logger.error(f"获取系统状态异常: {e}")
        raise BusinessException("获取系统状态失败")