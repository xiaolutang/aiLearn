# -*- coding: utf-8 -*-
"""
会话管理器
负责管理用户会话和会话信息
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum

class SessionStatus(Enum):
    """会话状态"""
    ACTIVE = "active"  # 活跃
    IDLE = "idle"  # 空闲
    EXPIRED = "expired"  # 过期
    TERMINATED = "terminated"  # 已终止

class UserRole(Enum):
    """用户角色"""
    STUDENT = "student"  # 学生
    TEACHER = "teacher"  # 教师
    ADMIN = "admin"  # 管理员
    GUEST = "guest"  # 访客

@dataclass
class SessionInfo:
    """会话信息"""
    session_id: str
    user_id: str
    user_role: UserRole
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    user_info: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)
    context_types: Set[str] = field(default_factory=set)
    activity_count: int = 0
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def update_activity(self):
        """更新活动时间"""
        self.last_activity = datetime.now()
        self.activity_count += 1
        if self.status == SessionStatus.IDLE:
            self.status = SessionStatus.ACTIVE
    
    def is_expired(self, timeout: timedelta) -> bool:
        """检查是否过期"""
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        return datetime.now() - self.last_activity > timeout
    
    def get_duration(self) -> timedelta:
        """获取会话持续时间"""
        return self.last_activity - self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user_role': self.user_role.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'user_info': self.user_info,
            'session_data': self.session_data,
            'context_types': list(self.context_types),
            'activity_count': self.activity_count,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionInfo':
        """从字典创建"""
        session = cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            user_role=UserRole(data['user_role']),
            status=SessionStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            last_activity=datetime.fromisoformat(data['last_activity']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            user_info=data.get('user_info', {}),
            session_data=data.get('session_data', {}),
            activity_count=data.get('activity_count', 0),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent')
        )
        session.context_types = set(data.get('context_types', []))
        return session

class SessionManager:
    """会话管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sessions: Dict[str, SessionInfo] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        
        # 配置参数
        self.session_timeout = timedelta(hours=self.config.get('session_timeout_hours', 24))
        self.max_sessions_per_user = self.config.get('max_sessions_per_user', 5)
        self.auto_cleanup = self.config.get('auto_cleanup', True)
        self.cleanup_interval = timedelta(minutes=self.config.get('cleanup_interval_minutes', 30))
        
        # 统计信息
        self.total_sessions_created = 0
        self.last_cleanup = datetime.now()
    
    def create_session(self, 
                      user_id: str,
                      user_role: UserRole,
                      user_info: Dict[str, Any] = None,
                      session_duration: Optional[timedelta] = None,
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None) -> str:
        """创建新会话"""
        # 检查用户会话数量限制
        if self._check_user_session_limit(user_id):
            self._cleanup_user_sessions(user_id)
        
        session_id = str(uuid.uuid4())
        expires_at = None
        if session_duration:
            expires_at = datetime.now() + session_duration
        
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            user_info=user_info or {},
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session
        
        # 更新用户会话映射
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        
        self.total_sessions_created += 1
        
        # 自动清理
        if self.auto_cleanup:
            self._auto_cleanup()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """获取会话信息"""
        session = self.sessions.get(session_id)
        
        if session:
            # 检查会话是否过期
            if session.is_expired(self.session_timeout):
                session.status = SessionStatus.EXPIRED
                return session
            
            # 更新活动时间
            session.update_activity()
        
        return session
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """更新会话信息"""
        session = self.get_session(session_id)
        if not session or session.status in [SessionStatus.EXPIRED, SessionStatus.TERMINATED]:
            return False
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.update_activity()
        return True
    
    def terminate_session(self, session_id: str) -> bool:
        """终止会话"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.status = SessionStatus.TERMINATED
        
        # 从用户会话映射中移除
        if session.user_id in self.user_sessions:
            self.user_sessions[session.user_id].discard(session_id)
            if not self.user_sessions[session.user_id]:
                del self.user_sessions[session.user_id]
        
        return True
    
    def remove_session(self, session_id: str) -> bool:
        """删除会话"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # 从用户会话映射中移除
        if session.user_id in self.user_sessions:
            self.user_sessions[session.user_id].discard(session_id)
            if not self.user_sessions[session.user_id]:
                del self.user_sessions[session.user_id]
        
        # 删除会话
        del self.sessions[session_id]
        return True
    
    def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """获取用户的所有会话"""
        if user_id not in self.user_sessions:
            return []
        
        sessions = []
        for session_id in self.user_sessions[user_id]:
            session = self.sessions.get(session_id)
            if session:
                sessions.append(session)
        
        return sessions
    
    def get_active_sessions(self) -> List[SessionInfo]:
        """获取所有活跃会话"""
        active_sessions = []
        
        for session in self.sessions.values():
            if not session.is_expired(self.session_timeout) and session.status == SessionStatus.ACTIVE:
                active_sessions.append(session)
        
        return active_sessions
    
    def add_context_type(self, session_id: str, context_type: str) -> bool:
        """为会话添加上下文类型"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.context_types.add(context_type)
        return True
    
    def remove_context_type(self, session_id: str, context_type: str) -> bool:
        """从会话中移除上下文类型"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.context_types.discard(context_type)
        return True
    
    def validate_session(self, session_id: str, user_id: str = None) -> bool:
        """验证会话有效性"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # 检查用户ID匹配
        if user_id and session.user_id != user_id:
            return False
        
        # 检查会话状态
        if session.status in [SessionStatus.EXPIRED, SessionStatus.TERMINATED]:
            return False
        
        return True
    
    def extend_session(self, session_id: str, duration: timedelta) -> bool:
        """延长会话时间"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        if session.expires_at:
            session.expires_at += duration
        else:
            session.expires_at = datetime.now() + duration
        
        return True
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """获取会话统计信息"""
        total_sessions = len(self.sessions)
        active_sessions = len(self.get_active_sessions())
        
        # 按状态统计
        status_counts = {}
        for session in self.sessions.values():
            status = session.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 按用户角色统计
        role_counts = {}
        for session in self.sessions.values():
            role = session.user_role.value
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # 计算平均会话时长
        total_duration = timedelta()
        for session in self.sessions.values():
            total_duration += session.get_duration()
        
        avg_duration = total_duration / total_sessions if total_sessions > 0 else timedelta()
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_users': len(self.user_sessions),
            'status_distribution': status_counts,
            'role_distribution': role_counts,
            'average_session_duration': str(avg_duration),
            'total_sessions_created': self.total_sessions_created
        }
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.is_expired(self.session_timeout):
                session.status = SessionStatus.EXPIRED
                expired_sessions.append(session_id)
        
        # 删除过期会话
        for session_id in expired_sessions:
            self.remove_session(session_id)
        
        self.last_cleanup = datetime.now()
        return len(expired_sessions)
    
    def _check_user_session_limit(self, user_id: str) -> bool:
        """检查用户会话数量是否超限"""
        if user_id not in self.user_sessions:
            return False
        
        return len(self.user_sessions[user_id]) >= self.max_sessions_per_user
    
    def _cleanup_user_sessions(self, user_id: str):
        """清理用户的旧会话"""
        if user_id not in self.user_sessions:
            return
        
        user_session_ids = list(self.user_sessions[user_id])
        sessions_with_time = []
        
        for session_id in user_session_ids:
            session = self.sessions.get(session_id)
            if session:
                sessions_with_time.append((session_id, session.last_activity))
        
        # 按最后活动时间排序，保留最新的
        sessions_with_time.sort(key=lambda x: x[1], reverse=True)
        
        # 删除多余的会话
        sessions_to_keep = self.max_sessions_per_user - 1
        for session_id, _ in sessions_with_time[sessions_to_keep:]:
            self.remove_session(session_id)
    
    def _auto_cleanup(self):
        """自动清理"""
        if datetime.now() - self.last_cleanup > self.cleanup_interval:
            self.cleanup_expired_sessions()
    
    def export_sessions(self, file_path: str):
        """导出会话数据"""
        data = {
            'export_time': datetime.now().isoformat(),
            'sessions': {},
            'statistics': self.get_session_statistics()
        }
        
        for session_id, session in self.sessions.items():
            data['sessions'][session_id] = session.to_dict()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def import_sessions(self, file_path: str) -> int:
        """导入会话数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for session_id, session_data in data.get('sessions', {}).items():
                try:
                    session = SessionInfo.from_dict(session_data)
                    self.sessions[session_id] = session
                    
                    # 更新用户会话映射
                    if session.user_id not in self.user_sessions:
                        self.user_sessions[session.user_id] = set()
                    self.user_sessions[session.user_id].add(session_id)
                    
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing session {session_id}: {e}")
            
            return imported_count
        except Exception as e:
            print(f"Error importing sessions: {e}")
            return 0
    
    def get_session_by_user_and_context(self, user_id: str, context_type: str) -> Optional[SessionInfo]:
        """根据用户ID和上下文类型获取会话"""
        user_sessions = self.get_user_sessions(user_id)
        
        for session in user_sessions:
            if (context_type in session.context_types and 
                session.status == SessionStatus.ACTIVE and
                not session.is_expired(self.session_timeout)):
                return session
        
        return None
    
    def refresh_session(self, session_id: str) -> bool:
        """刷新会话活动时间"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.update_activity()
        return True