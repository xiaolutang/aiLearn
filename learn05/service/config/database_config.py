# -*- coding: utf-8 -*-
"""
数据库配置和连接池管理

本模块提供数据库连接配置、连接池管理和性能优化功能。
"""

import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        # 基础配置
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./intelligent_tutor.db")
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        self.echo_pool = os.getenv("DB_ECHO_POOL", "false").lower() == "true"
        
        # 连接池配置
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1小时
        self.pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
        
        # 性能配置
        self.connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
        self.query_timeout = int(os.getenv("DB_QUERY_TIMEOUT", "30"))
        self.isolation_level = os.getenv("DB_ISOLATION_LEVEL", "READ_COMMITTED")
        
        # SQLite特定配置
        self.sqlite_pragma = {
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "cache_size": "-64000",  # 64MB缓存
            "temp_store": "MEMORY",
            "mmap_size": "268435456",  # 256MB内存映射
            "foreign_keys": "ON"
        }
        
        # MySQL/PostgreSQL特定配置
        self.mysql_charset = "utf8mb4"
        self.mysql_collation = "utf8mb4_unicode_ci"
    
    def get_engine_config(self) -> Dict[str, Any]:
        """获取引擎配置"""
        config = {
            "echo": self.echo,
            "echo_pool": self.echo_pool,
            "pool_pre_ping": self.pool_pre_ping,
            "pool_recycle": self.pool_recycle,
        }
        
        # 根据数据库类型配置连接池
        if self.database_url.startswith("sqlite"):
            config.update({
                "poolclass": StaticPool,
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": self.connect_timeout
                }
            })
        else:
            config.update({
                "poolclass": QueuePool,
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow,
                "pool_timeout": self.pool_timeout,
            })
            
            # MySQL特定配置
            if "mysql" in self.database_url:
                config["connect_args"] = {
                    "charset": self.mysql_charset,
                    "connect_timeout": self.connect_timeout,
                    "read_timeout": self.query_timeout,
                    "write_timeout": self.query_timeout,
                }
            
            # PostgreSQL特定配置
            elif "postgresql" in self.database_url:
                config["connect_args"] = {
                    "connect_timeout": self.connect_timeout,
                    "command_timeout": self.query_timeout,
                }
        
        return config


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "slow_queries": 0,
            "total_queries": 0,
            "avg_query_time": 0.0
        }
    
    def initialize(self):
        """初始化数据库连接"""
        try:
            # 创建引擎
            engine_config = self.config.get_engine_config()
            self.engine = create_engine(self.config.database_url, **engine_config)
            
            # 设置事件监听器
            self._setup_event_listeners()
            
            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # SQLite特定优化
            if self.config.database_url.startswith("sqlite"):
                self._setup_sqlite_pragmas()
            
            logger.info(f"数据库连接初始化成功: {self.config.database_url}")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    def _setup_event_listeners(self):
        """设置事件监听器"""
        @event.listens_for(self.engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            self._connection_stats["total_connections"] += 1
            self._connection_stats["active_connections"] += 1
            logger.debug(f"数据库连接建立: {connection_record}")
        
        @event.listens_for(self.engine, "close")
        def on_close(dbapi_connection, connection_record):
            self._connection_stats["active_connections"] -= 1
            logger.debug(f"数据库连接关闭: {connection_record}")
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
            self._connection_stats["total_queries"] += 1
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time
            
            # 更新平均查询时间
            total_queries = self._connection_stats["total_queries"]
            current_avg = self._connection_stats["avg_query_time"]
            self._connection_stats["avg_query_time"] = (
                (current_avg * (total_queries - 1) + total_time) / total_queries
            )
            
            # 记录慢查询
            if total_time > 1.0:  # 超过1秒的查询
                self._connection_stats["slow_queries"] += 1
                logger.warning(
                    f"慢查询检测 - 执行时间: {total_time:.3f}s\n"
                    f"SQL: {statement[:200]}..."
                )
        
        @event.listens_for(self.engine, "handle_error")
        def handle_error(exception_context):
            self._connection_stats["failed_connections"] += 1
            logger.error(f"数据库错误: {exception_context.original_exception}")
    
    def _setup_sqlite_pragmas(self):
        """设置SQLite优化参数"""
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            for pragma, value in self.config.sqlite_pragma.items():
                cursor.execute(f"PRAGMA {pragma}={value}")
            cursor.close()
            logger.debug("SQLite PRAGMA设置完成")
    
    @contextmanager
    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self.SessionLocal:
            raise RuntimeError("数据库未初始化")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            session.close()
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        stats = self._connection_stats.copy()
        
        # 添加连接池信息
        if self.engine and hasattr(self.engine.pool, 'size'):
            stats.update({
                "pool_size": self.engine.pool.size(),
                "checked_in": self.engine.pool.checkedin(),
                "checked_out": self.engine.pool.checkedout(),
                "overflow": self.engine.pool.overflow(),
                "invalid": self.engine.pool.invalid()
            })
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        try:
            with self.get_session() as session:
                # 执行简单查询测试连接
                result = session.execute("SELECT 1")
                result.fetchone()
                
                return {
                    "status": "healthy",
                    "database_url": self.config.database_url.split("@")[-1] if "@" in self.config.database_url else self.config.database_url,
                    "connection_stats": self.get_connection_stats(),
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db() -> Session:
    """获取数据库会话（依赖注入用）"""
    with db_manager.get_session() as session:
        yield session


def init_database():
    """初始化数据库"""
    db_manager.initialize()


def get_database_stats() -> Dict[str, Any]:
    """获取数据库统计信息"""
    return db_manager.get_connection_stats()


def database_health_check() -> Dict[str, Any]:
    """数据库健康检查"""
    return db_manager.health_check()


def close_database():
    """关闭数据库连接"""
    db_manager.close()