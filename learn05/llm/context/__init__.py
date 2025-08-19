# -*- coding: utf-8 -*-
"""
上下文管理模块
支持多轮对话和会话状态保持
"""

from .context_manager import ContextManager, ConversationContext
from .session_manager import SessionManager, SessionInfo
from .memory_store import MemoryStore, MemoryType
from .context_strategies import (
    ContextStrategy,
    SlidingWindowStrategy,
    TokenLimitStrategy,
    SemanticCompressionStrategy
)

__all__ = [
    'ContextManager',
    'ConversationContext',
    'SessionManager',
    'SessionInfo',
    'MemoryStore',
    'MemoryType',
    'ContextStrategy',
    'SlidingWindowStrategy',
    'TokenLimitStrategy',
    'SemanticCompressionStrategy'
]

__version__ = '1.0.0'
__author__ = 'AI Teaching Assistant Team'
__description__ = '智能教学助手上下文管理系统'

# 便捷函数
def create_context_manager(config: dict = None) -> ContextManager:
    """创建上下文管理器实例"""
    return ContextManager(config)

def create_session_manager(config: dict = None) -> SessionManager:
    """创建会话管理器实例"""
    return SessionManager(config)

def get_available_strategies() -> list:
    """获取可用的上下文策略"""
    return [
        'sliding_window',
        'token_limit',
        'semantic_compression'
    ]

def get_strategy_descriptions() -> dict:
    """获取策略描述"""
    return {
        'sliding_window': '滑动窗口策略：保持最近N轮对话',
        'token_limit': 'Token限制策略：基于Token数量限制上下文长度',
        'semantic_compression': '语义压缩策略：基于语义相似度压缩历史对话'
    }