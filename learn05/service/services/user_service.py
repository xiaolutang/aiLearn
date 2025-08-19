# -*- coding: utf-8 -*-
"""
用户服务模块
提供用户相关的业务逻辑
"""

import logging
from typing import Dict, List, Optional, Any, Union
import datetime
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt

from models.user import (
    UserCreate, UserUpdate, UserInDB, UserResponse, 
    Token, TokenData, UserSettings, UserProfile,
    PaginatedUsers, get_user_permissions, user_has_permission
)
from config.core_config import get_config
from database import DatabaseManager
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取配置
config = get_config()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

# OAuth2密码流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password: str) -> str:
    """获取密码哈希值
    
    Args:
        password: 原始密码
        
    Returns:
        str: 密码哈希值
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否正确
    """
    try:
        # 首先尝试bcrypt验证
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # 如果bcrypt验证失败，尝试SHA-256验证（兼容旧数据）
        import hashlib
        sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return sha256_hash == hashed_password


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """创建访问令牌
    
    Args:
        data: 令牌数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class UserService:
    """用户服务类"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """初始化用户服务
        
        Args:
            db_manager: 数据库管理器实例(可选，默认创建新的)
        """
        self.db_manager = db_manager or DatabaseManager(config.SQLALCHEMY_DATABASE_URL)
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """创建新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            UserResponse: 创建的用户响应
        """
        logger.info(f"创建新用户: {user_data.username}")
        
        # 检查用户名是否已存在
        existing_user = self.get_user_by_username(user_data.username)
        if existing_user:
            raise ValueError(f"用户名 '{user_data.username}' 已存在")
        
        # 检查邮箱是否已存在
        existing_email = self.get_user_by_email(user_data.email)
        if existing_email:
            raise ValueError(f"邮箱 '{user_data.email}' 已被使用")
        
        # 创建用户数据
        hashed_password = get_password_hash(user_data.password)
        user_in_db = UserInDB(
            **user_data.dict(exclude={"password"}),
            hashed_password=hashed_password
        )
        
        # 保存到数据库
        result = self.db_manager.execute_query(
            """
            INSERT INTO users (id, username, email, full_name, role, phone_number, 
            profile_picture, hashed_password, is_active, is_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_in_db.id,
                user_in_db.username,
                user_in_db.email,
                user_in_db.full_name,
                user_in_db.role,
                user_in_db.phone_number,
                user_in_db.profile_picture,
                user_in_db.hashed_password,
                user_in_db.is_active,
                user_in_db.is_verified,
                user_in_db.created_at,
                user_in_db.updated_at
            )
        )
        
        if result is None:
            raise Exception("创建用户失败")
        
        # 创建默认用户设置和个人资料
        self._create_default_settings(user_in_db.id)
        self._create_default_profile(user_in_db.id)
        
        # 返回用户响应
        return UserResponse(
            id=user_in_db.id,
            username=user_in_db.username,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            role=user_in_db.role,
            phone_number=user_in_db.phone_number,
            profile_picture=user_in_db.profile_picture,
            is_active=user_in_db.is_active,
            is_verified=user_in_db.is_verified,
            created_at=user_in_db.created_at,
            last_login=user_in_db.last_login
        )
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """通过ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[UserInDB]: 用户对象，如果不存在则返回None
        """
        logger.debug(f"通过ID获取用户: {user_id}")
        
        result = self.db_manager.execute_query(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not result or len(result) == 0:
            return None
        
        user_data = result[0]
        # 根据实际数据库结构映射字段
        # users表字段: id, username, password, role, related_id, email, phone_number, created_at, updated_at, is_active
        return UserInDB(
            id=str(user_data[0]),  # 转换为字符串
            username=user_data[1],
            hashed_password=user_data[2],  # password字段
            role=user_data[3],
            email=user_data[5] if len(user_data) > 5 and user_data[5] else "user@example.com",
            phone_number=user_data[6] if len(user_data) > 6 else None,
            created_at=user_data[7] if len(user_data) > 7 else datetime.datetime.now(),
            updated_at=user_data[8] if len(user_data) > 8 else datetime.datetime.now(),
            is_active=user_data[9] if len(user_data) > 9 else True,
            full_name=user_data[1],  # 使用用户名作为全名的默认值
            profile_picture=None,  # 数据库中没有此字段
            is_verified=True,  # 默认值
            last_login=None  # 数据库中没有此字段
        )
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """通过用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[UserInDB]: 用户对象，如果不存在则返回None
        """
        logger.debug(f"通过用户名获取用户: {username}")
        
        result = self.db_manager.execute_query(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        
        if not result or len(result) == 0:
            return None
        
        user_data = result[0]
        # 根据实际数据库结构映射字段
        # users表字段: id, username, password, role, related_id, email, phone_number, created_at, updated_at, is_active
        return UserInDB(
            id=str(user_data[0]),  # 转换为字符串
            username=user_data[1],
            hashed_password=user_data[2],  # password字段
            role=user_data[3],
            email=user_data[5] if len(user_data) > 5 and user_data[5] else "user@example.com",
            phone_number=user_data[6] if len(user_data) > 6 else None,
            created_at=user_data[7] if len(user_data) > 7 else datetime.datetime.now(),
            updated_at=user_data[8] if len(user_data) > 8 else datetime.datetime.now(),
            is_active=user_data[9] if len(user_data) > 9 else True,
            full_name=user_data[1],  # 使用用户名作为全名的默认值
            profile_picture=None,  # 数据库中没有此字段
            is_verified=True,  # 默认值
            last_login=None  # 数据库中没有此字段
        )
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """通过邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            Optional[UserInDB]: 用户对象，如果不存在则返回None
        """
        logger.debug(f"通过邮箱获取用户: {email}")
        
        result = self.db_manager.execute_query(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        
        if not result or len(result) == 0:
            return None
        
        user_data = result[0]
        return UserInDB(
            id=user_data[0],
            username=user_data[1],
            email=user_data[2],
            full_name=user_data[3],
            role=user_data[4],
            phone_number=user_data[5],
            profile_picture=user_data[6],
            hashed_password=user_data[7],
            is_active=user_data[8],
            is_verified=user_data[9],
            created_at=user_data[10],
            updated_at=user_data[11],
            last_login=user_data[12]
        )
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 用户更新数据
            
        Returns:
            UserResponse: 更新后的用户响应
        """
        logger.info(f"更新用户信息: {user_id}")
        
        # 检查用户是否存在
        existing_user = self.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError(f"用户不存在: {user_id}")
        
        # 检查用户名是否已被其他用户使用
        if user_data.username and user_data.username != existing_user.username:
            other_user = self.get_user_by_username(user_data.username)
            if other_user:
                raise ValueError(f"用户名 '{user_data.username}' 已被使用")
        
        # 检查邮箱是否已被其他用户使用
        if user_data.email and user_data.email != existing_user.email:
            other_user = self.get_user_by_email(user_data.email)
            if other_user:
                raise ValueError(f"邮箱 '{user_data.email}' 已被使用")
        
        # 构建更新字段和参数
        update_fields = []
        params = []
        
        if user_data.username is not None:
            update_fields.append("username = ?")
            params.append(user_data.username)
        
        if user_data.email is not None:
            update_fields.append("email = ?")
            params.append(user_data.email)
        
        if user_data.full_name is not None:
            update_fields.append("full_name = ?")
            params.append(user_data.full_name)
        
        if user_data.role is not None:
            update_fields.append("role = ?")
            params.append(user_data.role)
        
        if user_data.phone_number is not None:
            update_fields.append("phone_number = ?")
            params.append(user_data.phone_number)
        
        if user_data.profile_picture is not None:
            update_fields.append("profile_picture = ?")
            params.append(user_data.profile_picture)
        
        if user_data.password is not None:
            update_fields.append("hashed_password = ?")
            params.append(get_password_hash(user_data.password))
        
        # 添加更新时间和用户ID
        update_fields.append("updated_at = ?")
        params.append(datetime.datetime.now())
        params.append(user_id)
        
        # 执行更新
        if update_fields:
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            self.db_manager.execute_query(query, tuple(params))
        
        # 返回更新后的用户信息
        updated_user = self.get_user_by_id(user_id)
        if not updated_user:
            raise Exception("更新用户失败")
        
        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            full_name=updated_user.full_name,
            role=updated_user.role,
            phone_number=updated_user.phone_number,
            profile_picture=updated_user.profile_picture,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否删除成功
        """
        logger.info(f"删除用户: {user_id}")
        
        # 检查用户是否存在
        existing_user = self.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError(f"用户不存在: {user_id}")
        
        # 执行删除
        result = self.db_manager.execute_query(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )
        
        return result is not None
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[UserInDB]: 用户对象，如果验证失败则返回None
        """
        logger.info(f"验证用户: {username}")
        
        user = self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        # 更新最后登录时间
        self.update_last_login(user.id)
        
        return user
    
    def update_last_login(self, user_id: str) -> None:
        """更新用户最后登录时间
        
        Args:
            user_id: 用户ID
        """
        logger.debug(f"更新用户最后登录时间: {user_id}")
        
        # 由于数据库中没有last_login字段，只更新updated_at字段
        self.db_manager.execute_query(
            "UPDATE users SET updated_at = ? WHERE id = ?",
            (datetime.datetime.now(), user_id)
        )
    
    def get_users(self, page: int = 1, limit: int = 10, **filters) -> PaginatedUsers:
        """获取用户列表
        
        Args:
            page: 当前页码
            limit: 每页数量
            **filters: 过滤条件
            
        Returns:
            PaginatedUsers: 分页用户列表
        """
        logger.info(f"获取用户列表: 页码={page}, 每页数量={limit}, 过滤条件={filters}")
        
        # 构建查询条件
        query_parts = ["SELECT * FROM users WHERE 1=1"]
        params = []
        
        # 添加过滤条件
        if "role" in filters:
            query_parts.append("AND role = ?")
            params.append(filters["role"])
        
        if "is_active" in filters:
            query_parts.append("AND is_active = ?")
            params.append(filters["is_active"])
        
        if "search" in filters:
            search_term = f"%{filters['search']}%"
            query_parts.append("AND (username LIKE ? OR full_name LIKE ? OR email LIKE ?)")
            params.extend([search_term, search_term, search_term])
        
        # 添加分页
        offset = (page - 1) * limit
        query_parts.append("LIMIT ? OFFSET ?")
        params.extend([limit, offset])
        
        # 执行查询
        query = " ".join(query_parts)
        results = self.db_manager.execute_query(query, tuple(params))
        
        # 构建用户列表
        users = []
        for user_data in results:
            user = UserInDB(
                id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                full_name=user_data[3],
                role=user_data[4],
                phone_number=user_data[5],
                profile_picture=user_data[6],
                hashed_password=user_data[7],
                is_active=user_data[8],
                is_verified=user_data[9],
                created_at=user_data[10],
                updated_at=user_data[11],
                last_login=user_data[12]
            )
            users.append(UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                phone_number=user.phone_number,
                profile_picture=user.profile_picture,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                last_login=user.last_login
            ))
        
        # 获取总数
        total_query = "SELECT COUNT(*) FROM users WHERE 1=1"
        if len(query_parts) > 1:
            total_query += " " + " ".join(query_parts[1:-1])  # 不包含LIMIT和OFFSET
        total_result = self.db_manager.execute_query(total_query, tuple(params[:-2]))  # 不包含LIMIT和OFFSET参数
        total = total_result[0][0] if total_result else 0
        
        # 计算总页数
        total_pages = (total + limit - 1) // limit
        
        return PaginatedUsers(
            users=users,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    def _create_default_settings(self, user_id: str) -> None:
        """创建默认用户设置
        
        Args:
            user_id: 用户ID
        """
        settings = UserSettings(user_id=user_id)
        
        self.db_manager.execute_query(
            """
            INSERT INTO user_settings (user_id, theme, language, notifications, timezone, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                settings.user_id,
                settings.theme,
                settings.language,
                str(settings.notifications),  # 存储为JSON字符串
                settings.timezone,
                settings.updated_at
            )
        )
    
    def _create_default_profile(self, user_id: str) -> None:
        """创建默认用户个人资料
        
        Args:
            user_id: 用户ID
        """
        profile = UserProfile(user_id=user_id)
        
        self.db_manager.execute_query(
            """
            INSERT INTO user_profiles (user_id, bio, education, work_experience, interests, social_links, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile.user_id,
                profile.bio,
                profile.education,
                profile.work_experience,
                str(profile.interests),  # 存储为JSON字符串
                str(profile.social_links),  # 存储为JSON字符串
                profile.updated_at
            )
        )


# 创建全局用户服务实例
_global_user_service = UserService()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    获取当前认证的用户
    作为FastAPI依赖项，用于保护需要认证的端点
    
    Args:
        token: 认证令牌
        
    Returns:
        UserResponse: 当前用户信息
        
    Raises:
        HTTPException: 当令牌无效或用户不存在时
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # 获取用户服务实例
    user_service = get_user_service()
    
    # 查询用户信息
    user = user_service.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


def get_user_service() -> UserService:
    """
    获取全局用户服务实例
    
    Returns:
        UserService: 用户服务实例
    """
    return _global_user_service