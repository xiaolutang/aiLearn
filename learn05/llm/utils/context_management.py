# -*- coding: utf-8 -*-
"""
上下文管理工具模块
提供对话上下文的有效管理功能，提高交互连贯性
"""

import logging
from typing import Dict, List, Optional, Any, Union
import time
from collections import deque

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextManager:
    """对话上下文管理器
    负责管理和维护对话的上下文信息，支持会话历史的追踪和管理
    """
    
    def __init__(self, max_history_length: int = 10, context_ttl: int = 3600):
        """初始化上下文管理器
        
        Args:
            max_history_length: 最大历史消息数量
            context_ttl: 上下文的生存时间(秒)
        """
        self.max_history_length = max_history_length
        self.context_ttl = context_ttl
        self.contexts = {}
    
    def create_context(self, session_id: str) -> None:
        """创建新的对话上下文
        
        Args:
            session_id: 会话ID
        """
        if session_id not in self.contexts:
            self.contexts[session_id] = {
                'messages': deque(maxlen=self.max_history_length),
                'created_at': time.time(),
                'last_accessed': time.time()
            }
            logger.info(f"创建新的对话上下文: {session_id}")
        else:
            logger.warning(f"会话上下文已存在: {session_id}")
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """添加消息到对话上下文
        
        Args:
            session_id: 会话ID
            role: 消息角色(如'user'或'assistant')
            content: 消息内容
        """
        if session_id not in self.contexts:
            self.create_context(session_id)
        
        self.contexts[session_id]['messages'].append({
            'role': role,
            'content': content,
            'timestamp': time.time()
        })
        self.contexts[session_id]['last_accessed'] = time.time()
        logger.debug(f"添加消息到上下文: {session_id}, 角色: {role}")
    
    def get_context(self, session_id: str, include_system: bool = True, include_timestamp: bool = False) -> List[Dict[str, str]]:
        """获取对话上下文
        
        Args:
            session_id: 会话ID
            include_system: 是否包含系统提示词
            include_timestamp: 是否包含时间戳
            
        Returns:
            List[Dict[str, str]]: 上下文消息列表
        """
        if session_id not in self.contexts:
            self.create_context(session_id)
            return []
        
        # 更新最后访问时间
        self.contexts[session_id]['last_accessed'] = time.time()
        
        # 转换消息格式
        messages = []
        for msg in self.contexts[session_id]['messages']:
            message = {
                'role': msg['role'],
                'content': msg['content']
            }
            if include_timestamp:
                message['timestamp'] = msg['timestamp']
            messages.append(message)
        
        # 检查上下文是否过期
        self._cleanup_expired_contexts()
        
        logger.debug(f"获取对话上下文: {session_id}, 消息数量: {len(messages)}")
        return messages
    
    def clear_context(self, session_id: str) -> None:
        """清除对话上下文
        
        Args:
            session_id: 会话ID
        """
        if session_id in self.contexts:
            del self.contexts[session_id]
            logger.info(f"清除对话上下文: {session_id}")
    
    def reset_context(self, session_id: str) -> None:
        """重置对话上下文(清空历史消息但保留上下文对象)
        
        Args:
            session_id: 会话ID
        """
        if session_id in self.contexts:
            self.contexts[session_id]['messages'] = deque(maxlen=self.max_history_length)
            self.contexts[session_id]['last_accessed'] = time.time()
            logger.info(f"重置对话上下文: {session_id}")
        else:
            self.create_context(session_id)
    
    def _cleanup_expired_contexts(self) -> None:
        """清理过期的对话上下文
        """
        current_time = time.time()
        expired_sessions = []
        
        for session_id, context in self.contexts.items():
            if current_time - context['last_accessed'] > self.context_ttl:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.clear_context(session_id)
            logger.info(f"清理过期对话上下文: {session_id}")
    
    def get_context_summary(self, session_id: str, llm_client) -> str:
        """获取对话上下文摘要
        
        Args:
            session_id: 会话ID
            llm_client: 大模型客户端
            
        Returns:
            str: 上下文摘要
        """
        if session_id not in self.contexts:
            return "无对话历史"
        
        messages = self.get_context(session_id)
        if not messages:
            return "无对话历史"
        
        # 构造提示词让大模型生成摘要
        prompt = f"""
        请为以下对话生成一个简明的摘要，突出关键信息和讨论要点:
        {chr(10).join([f"{msg['role']}: {msg['content']}" for msg in messages])}
        
        摘要应简洁明了，不超过100字。
        """
        
        try:
            summary = llm_client.generate(prompt)
            logger.info(f"生成对话上下文摘要: {session_id}")
            return summary
        except Exception as e:
            logger.error(f"生成对话上下文摘要失败: {e}")
            return "生成摘要失败"
    
    def get_active_sessions(self) -> List[str]:
        """获取所有活跃的会话ID
        
        Returns:
            List[str]: 活跃会话ID列表
        """
        self._cleanup_expired_contexts()
        return list(self.contexts.keys())


class ContextAwareLLMWrapper:
    """上下文感知的大模型包装器
    结合上下文管理器，提供更智能的大模型调用接口
    """
    
    def __init__(self, llm_client, context_manager: ContextManager = None):
        """初始化上下文感知的大模型包装器
        
        Args:
            llm_client: 大模型客户端
            context_manager: 上下文管理器(可选，默认创建新的)
        """
        self.llm_client = llm_client
        self.context_manager = context_manager or ContextManager()
    
    def generate_with_context(self, session_id: str, user_message: str, system_prompt: str = None) -> str:
        """结合上下文生成响应
        
        Args:
            session_id: 会话ID
            user_message: 用户消息
            system_prompt: 系统提示词(可选)
            
        Returns:
            str: 生成的响应
        """
        # 添加用户消息到上下文
        self.context_manager.add_message(session_id, 'user', user_message)
        
        # 获取完整上下文
        context_messages = self.context_manager.get_context(session_id)
        
        # 构造完整消息列表，包含系统提示词(如果有)
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.extend(context_messages)
        
        # 调用大模型生成响应
        try:
            response = self.llm_client.generate_chat_completion(messages)
            
            # 添加响应到上下文
            self.context_manager.add_message(session_id, 'assistant', response)
            
            return response
        except Exception as e:
            logger.error(f"生成响应失败: {e}")
            raise
    
    def clear_session(self, session_id: str) -> None:
        """清除指定会话的上下文
        
        Args:
            session_id: 会话ID
        """
        self.context_manager.clear_context(session_id)
    
    def reset_session(self, session_id: str) -> None:
        """重置指定会话的上下文
        
        Args:
            session_id: 会话ID
        """
        self.context_manager.reset_context(session_id)
    
    def summarize_session(self, session_id: str) -> str:
        """生成会话摘要
        
        Args:
            session_id: 会话ID
            
        Returns:
            str: 会话摘要
        """
        return self.context_manager.get_context_summary(session_id, self.llm_client)


# 创建全局上下文管理器实例
_global_context_manager = ContextManager()

def get_context_manager() -> ContextManager:
    """获取全局上下文管理器实例
    
    Returns:
        ContextManager: 上下文管理器实例
    """
    return _global_context_manager


def create_context_aware_llm_wrapper(llm_client) -> ContextAwareLLMWrapper:
    """创建上下文感知的大模型包装器
    
    Args:
        llm_client: 大模型客户端
        
    Returns:
        ContextAwareLLMWrapper: 上下文感知的大模型包装器
    """
    return ContextAwareLLMWrapper(llm_client, get_context_manager())

def get_conversation_summary(conversation_history):
    """获取对话摘要"""
    if not conversation_history:
        return "无对话历史"
    
    # 简单的摘要生成
    total_messages = len(conversation_history)
    if total_messages <= 3:
        return f"包含{total_messages}条消息的简短对话"
    else:
        return f"包含{total_messages}条消息的对话，最近讨论了相关主题"
