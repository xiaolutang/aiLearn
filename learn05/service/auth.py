#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证模块
提供用户认证和授权功能
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db, get_user_by_username

# JWT配置
SECRET_KEY = "your-secret-key-here"  # 在生产环境中应使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2密码流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    """将明文密码哈希化"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配"""
    import hashlib
    
    # 首先尝试SHA256验证（项目中使用的格式）
    sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    if sha256_hash == hashed_password:
        return True
    
    # 如果SHA256不匹配，再尝试bcrypt验证（向后兼容）
    if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False
    
    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """从JWT令牌中获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 优先使用user_id字段，如果没有则尝试从sub字段解析
        user_id = payload.get("user_id")
        if user_id is None:
            user_id_str: str = payload.get("sub")
            if user_id_str is None:
                raise credentials_exception
            
            try:
                user_id = int(user_id_str)
            except ValueError:
                raise credentials_exception
        
        # 直接使用SQLAlchemy查询获取用户
        from .database import User
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception


def get_current_active_user(current_user = Depends(get_current_user)):
    """获取当前活跃的用户"""
    # 这里可以添加额外的活跃状态检查逻辑
    return current_user


def verify_token_role(token: str, required_role: Union[str, list]) -> bool:
    """验证令牌的角色是否符合要求"""
    payload = decode_token(token)
    user_role = payload.get("role")
    
    if isinstance(required_role, str):
        required_roles = [required_role]
    else:
        required_roles = required_role
    
    return user_role in required_roles


def role_required(required_role: Union[str, list]):
    """角色验证依赖项"""
    def role_checker(current_user = Depends(get_current_active_user)):
        if isinstance(required_role, str):
            required_roles = [required_role]
        else:
            required_roles = required_role
        
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return current_user
    return role_checker


def authenticate_user(db: Session, username: str, password: str):
    """用户认证"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# 预定义的角色权限
ROLES = {
    "admin": ["admin", "teacher", "student", "parent"],
    "teacher": ["teacher", "student", "parent"],
    "student": ["student"],
    "parent": ["parent"]
}


def check_permission(current_user_role: str, target_role: str) -> bool:
    """检查用户是否有访问目标角色资源的权限"""
    if current_user_role not in ROLES:
        return False
    return target_role in ROLES[current_user_role]


def get_user_role(token: str) -> str:
    """从JWT令牌中获取用户角色"""
    payload = decode_token(token)
    user_role = payload.get("role")
    return user_role