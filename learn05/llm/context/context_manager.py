# -*- coding: utf-8 -*-
"""
上下文管理器
负责管理对话上下文和会话状态
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum

class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class ContextType(Enum):
    """上下文类型"""
    TEACHING = "teaching"  # 教学相关
    LEARNING = "learning"  # 学习相关
    TUTORING = "tutoring"  # 辅导相关
    CLASSROOM = "classroom"  # 课堂相关
    GENERAL = "general"  # 通用

@dataclass
class Message:
    """消息对象"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'message_id': self.message_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建"""
        return cls(
            role=MessageRole(data['role']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {}),
            message_id=data.get('message_id', str(uuid.uuid4()))
        )

@dataclass
class ConversationContext:
    """对话上下文"""
    session_id: str
    context_type: ContextType
    messages: List[Message] = field(default_factory=list)
    system_prompt: Optional[str] = None
    user_info: Dict[str, Any] = field(default_factory=dict)
    context_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    max_messages: int = 50
    
    def add_message(self, role: MessageRole, content: str, metadata: Dict[str, Any] = None):
        """添加消息"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        # 限制消息数量
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """获取最近的消息"""
        return self.messages[-count:] if count > 0 else self.messages
    
    def get_messages_by_role(self, role: MessageRole) -> List[Message]:
        """按角色获取消息"""
        return [msg for msg in self.messages if msg.role == role]
    
    def get_conversation_summary(self) -> str:
        """获取对话摘要"""
        if not self.messages:
            return "暂无对话内容"
        
        user_messages = self.get_messages_by_role(MessageRole.USER)
        assistant_messages = self.get_messages_by_role(MessageRole.ASSISTANT)
        
        return f"对话轮数: {len(user_messages)}, 最后更新: {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def clear_messages(self):
        """清空消息"""
        self.messages.clear()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'context_type': self.context_type.value,
            'messages': [msg.to_dict() for msg in self.messages],
            'system_prompt': self.system_prompt,
            'user_info': self.user_info,
            'context_data': self.context_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'max_messages': self.max_messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """从字典创建"""
        context = cls(
            session_id=data['session_id'],
            context_type=ContextType(data['context_type']),
            system_prompt=data.get('system_prompt'),
            user_info=data.get('user_info', {}),
            context_data=data.get('context_data', {}),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            max_messages=data.get('max_messages', 50)
        )
        
        # 恢复消息
        for msg_data in data.get('messages', []):
            context.messages.append(Message.from_dict(msg_data))
        
        return context

class ContextManager:
    """上下文管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.contexts: Dict[str, ConversationContext] = {}
        self.default_max_messages = self.config.get('default_max_messages', 50)
        self.context_timeout = timedelta(hours=self.config.get('context_timeout_hours', 24))
        self.auto_cleanup = self.config.get('auto_cleanup', True)
        
        # 初始化策略
        self.strategy = None
        strategy_name = self.config.get('strategy', 'sliding_window')
        self._initialize_strategy(strategy_name)
    
    def _initialize_strategy(self, strategy_name: str):
        """初始化上下文策略"""
        from .context_strategies import (
            SlidingWindowStrategy,
            TokenLimitStrategy,
            SemanticCompressionStrategy
        )
        
        strategy_config = self.config.get('strategy_config', {})
        
        if strategy_name == 'sliding_window':
            self.strategy = SlidingWindowStrategy(**strategy_config)
        elif strategy_name == 'token_limit':
            self.strategy = TokenLimitStrategy(**strategy_config)
        elif strategy_name == 'semantic_compression':
            self.strategy = SemanticCompressionStrategy(**strategy_config)
        else:
            # 默认使用滑动窗口策略
            self.strategy = SlidingWindowStrategy(window_size=10)
    
    def create_context(self, 
                      session_id: str, 
                      context_type: ContextType,
                      system_prompt: Optional[str] = None,
                      user_info: Dict[str, Any] = None) -> ConversationContext:
        """创建新的对话上下文"""
        context = ConversationContext(
            session_id=session_id,
            context_type=context_type,
            system_prompt=system_prompt,
            user_info=user_info or {},
            max_messages=self.default_max_messages
        )
        
        # 添加系统提示词
        if system_prompt:
            context.add_message(MessageRole.SYSTEM, system_prompt)
        
        self.contexts[session_id] = context
        return context
    
    def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """获取对话上下文"""
        context = self.contexts.get(session_id)
        
        if context and self.auto_cleanup:
            # 检查是否超时
            if datetime.now() - context.updated_at > self.context_timeout:
                self.remove_context(session_id)
                return None
        
        return context
    
    def update_context(self, session_id: str, **kwargs) -> bool:
        """更新上下文信息"""
        context = self.get_context(session_id)
        if not context:
            return False
        
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        context.updated_at = datetime.now()
        return True
    
    def add_message(self, 
                   session_id: str, 
                   role: MessageRole, 
                   content: str,
                   metadata: Dict[str, Any] = None) -> bool:
        """添加消息到上下文"""
        context = self.get_context(session_id)
        if not context:
            return False
        
        context.add_message(role, content, metadata)
        
        # 应用上下文策略
        if self.strategy:
            context.messages = self.strategy.apply(context.messages)
        
        return True
    
    def get_conversation_history(self, 
                               session_id: str, 
                               count: int = 10,
                               include_system: bool = False) -> List[Dict[str, str]]:
        """获取对话历史"""
        context = self.get_context(session_id)
        if not context:
            return []
        
        messages = context.get_recent_messages(count)
        
        if not include_system:
            messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        return [{
            'role': msg.role.value,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        } for msg in messages]
    
    def get_context_for_llm(self, session_id: str) -> List[Dict[str, str]]:
        """获取适用于LLM的上下文格式"""
        context = self.get_context(session_id)
        if not context:
            return []
        
        # 应用策略获取优化后的消息
        messages = context.messages
        if self.strategy:
            messages = self.strategy.apply(messages)
        
        return [{
            'role': msg.role.value,
            'content': msg.content
        } for msg in messages]
    
    def remove_context(self, session_id: str) -> bool:
        """删除上下文"""
        if session_id in self.contexts:
            del self.contexts[session_id]
            return True
        return False
    
    def clear_context_messages(self, session_id: str) -> bool:
        """清空上下文消息"""
        context = self.get_context(session_id)
        if not context:
            return False
        
        context.clear_messages()
        return True
    
    def list_active_sessions(self) -> List[str]:
        """列出活跃的会话"""
        if not self.auto_cleanup:
            return list(self.contexts.keys())
        
        active_sessions = []
        current_time = datetime.now()
        
        for session_id, context in self.contexts.items():
            if current_time - context.updated_at <= self.context_timeout:
                active_sessions.append(session_id)
        
        return active_sessions
    
    def cleanup_expired_contexts(self) -> int:
        """清理过期的上下文"""
        if not self.auto_cleanup:
            return 0
        
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, context in self.contexts.items():
            if current_time - context.updated_at > self.context_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.contexts[session_id]
        
        return len(expired_sessions)
    
    def get_context_statistics(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        total_contexts = len(self.contexts)
        active_contexts = len(self.list_active_sessions())
        
        context_types = {}
        total_messages = 0
        
        for context in self.contexts.values():
            context_type = context.context_type.value
            context_types[context_type] = context_types.get(context_type, 0) + 1
            total_messages += len(context.messages)
        
        return {
            'total_contexts': total_contexts,
            'active_contexts': active_contexts,
            'context_types': context_types,
            'total_messages': total_messages,
            'average_messages_per_context': total_messages / total_contexts if total_contexts > 0 else 0
        }
    
    def export_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """导出上下文数据"""
        context = self.get_context(session_id)
        if not context:
            return None
        
        return context.to_dict()
    
    def import_context(self, context_data: Dict[str, Any]) -> bool:
        """导入上下文数据"""
        try:
            context = ConversationContext.from_dict(context_data)
            self.contexts[context.session_id] = context
            return True
        except Exception as e:
            print(f"Error importing context: {e}")
            return False
    
    def save_contexts_to_file(self, file_path: str):
        """保存上下文到文件"""
        data = {
            'export_time': datetime.now().isoformat(),
            'contexts': {}
        }
        
        for session_id, context in self.contexts.items():
            data['contexts'][session_id] = context.to_dict()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_contexts_from_file(self, file_path: str) -> int:
        """从文件加载上下文"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            loaded_count = 0
            for session_id, context_data in data.get('contexts', {}).items():
                if self.import_context(context_data):
                    loaded_count += 1
            
            return loaded_count
        except Exception as e:
            print(f"Error loading contexts: {e}")
            return 0