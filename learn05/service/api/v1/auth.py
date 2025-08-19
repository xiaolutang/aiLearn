# -*- coding: utf-8 -*-
"""
认证API路由

本模块提供用户认证相关的API接口。
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime, timedelta

from database import get_db
from models.response import APIResponse, ResponseBuilder
from middleware.exception_handler import (
    AuthenticationException,
    BusinessException,
    ValidationException,
    raise_unauthorized
)
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from database import User
from pydantic import BaseModel, EmailStr, validator
import re

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter()


# 请求模型
class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str
    remember_me: bool = False
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('用户名不能为空')
        if len(v) < 3 or len(v) > 50:
            raise ValueError('用户名长度必须在3-50个字符之间')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('密码长度不能少于6个字符')
        return v


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str
    password: str
    confirm_password: str
    email: EmailStr
    role: str = "teacher"
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('用户名不能为空')
        if len(v) < 3 or len(v) > 50:
            raise ValueError('用户名长度必须在3-50个字符之间')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('密码长度不能少于6个字符')
        if len(v) > 128:
            raise ValueError('密码长度不能超过128个字符')
        # 密码强度检查
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('确认密码与密码不匹配')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['teacher', 'student', 'admin']
        if v not in allowed_roles:
            raise ValueError(f'角色必须是以下之一: {", ".join(allowed_roles)}')
        return v


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    current_password: str
    new_password: str
    confirm_new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('新密码长度不能少于6个字符')
        if len(v) > 128:
            raise ValueError('新密码长度不能超过128个字符')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('新密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('新密码必须包含至少一个数字')
        return v
    
    @validator('confirm_new_password')
    def validate_confirm_new_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('确认新密码与新密码不匹配')
        return v


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str


# 响应模型
class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    user_info: dict


class UserInfo(BaseModel):
    """用户信息响应模型"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """用户登录"""
    try:
        # 记录登录尝试
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"登录尝试 - 用户: {login_data.username}, IP: {client_ip}")
        
        # 验证用户凭据
        user = authenticate_user(db, login_data.username, login_data.password)
        if not user:
            logger.warning(f"登录失败 - 用户: {login_data.username}, IP: {client_ip}")
            raise AuthenticationException("用户名或密码错误")
        
        if not user.is_active:
            logger.warning(f"登录失败 - 用户已禁用: {login_data.username}, IP: {client_ip}")
            raise AuthenticationException("账户已被禁用")
        
        # 计算令牌过期时间
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        if login_data.remember_me:
            expires_delta = timedelta(days=30)  # 记住我：30天
        
        # 创建访问令牌
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role},
            expires_delta=expires_delta
        )
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        db.commit()
        
        # 构建响应
        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email or "",
            "full_name": user.username,  # 使用username作为full_name
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        response_data = LoginResponse(
            access_token=access_token,
            expires_in=int(expires_delta.total_seconds()),
            user_info=user_info
        )
        
        logger.info(f"登录成功 - 用户: {login_data.username}, IP: {client_ip}")
        return ResponseBuilder.success(response_data, "登录成功")
        
    except AuthenticationException as e:
        raise e
    except BusinessException as e:
        raise e
    except Exception as e:
        logger.error(f"登录异常: {e}")
        raise BusinessException("登录服务暂时不可用")


@router.post("/register", response_model=APIResponse[UserInfo])
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """用户注册"""
    try:
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"注册尝试 - 用户: {register_data.username}, IP: {client_ip}")
        
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(
            (User.username == register_data.username) | 
            (User.email == register_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == register_data.username:
                raise ValidationException("用户名已存在")
            else:
                raise ValidationException("邮箱已被注册")
        
        # 创建新用户
        hashed_password = hash_password(register_data.password)
        new_user = User(
            username=register_data.username,
            email=register_data.email,
            password=hashed_password,
            role=register_data.role,
            is_active=True,
            created_at=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"注册成功 - 用户: {register_data.username}, ID: {new_user.id}, IP: {client_ip}")
        
        return ResponseBuilder.success(
            UserInfo.from_orm(new_user),
            "注册成功"
        )
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"注册异常: {e}")
        raise BusinessException("注册服务暂时不可用")


@router.get("/me", response_model=APIResponse[UserInfo])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    try:
        return ResponseBuilder.success(
            UserInfo.from_orm(current_user),
            "获取用户信息成功"
        )
    except Exception as e:
        logger.error(f"获取用户信息异常: {e}")
        raise BusinessException("获取用户信息失败")


@router.post("/change-password", response_model=APIResponse[dict])
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    try:
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"修改密码尝试 - 用户: {current_user.username}, IP: {client_ip}")
        
        # 验证当前密码
        if not authenticate_user(db, current_user.username, password_data.current_password):
            raise AuthenticationException("当前密码错误")
        
        # 检查新密码是否与当前密码相同
        if password_data.current_password == password_data.new_password:
            raise ValidationException("新密码不能与当前密码相同")
        
        # 更新密码
        current_user.hashed_password = hash_password(password_data.new_password)
        db.commit()
        
        logger.info(f"密码修改成功 - 用户: {current_user.username}, IP: {client_ip}")
        
        return ResponseBuilder.success(
            {"message": "密码修改成功"},
            "密码修改成功"
        )
        
    except (ValidationException, AuthenticationException) as e:
        raise e
    except Exception as e:
        logger.error(f"修改密码异常: {e}")
        raise BusinessException("修改密码服务暂时不可用")


@router.post("/logout", response_model=APIResponse[dict])
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    try:
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"用户登出 - 用户: {current_user.username}, IP: {client_ip}")
        
        # 在实际应用中，这里可以将令牌加入黑名单
        # 目前只是记录登出事件
        
        return ResponseBuilder.success(
            {"message": "登出成功"},
            "登出成功"
        )
        
    except Exception as e:
        logger.error(f"登出异常: {e}")
        raise BusinessException("登出服务暂时不可用")


@router.post("/verify-token", response_model=APIResponse[dict])
async def verify_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """验证令牌"""
    try:
        token_data = verify_token(credentials.credentials)
        
        return ResponseBuilder.success(
            {
                "valid": True,
                "user_id": token_data.get("user_id"),
                "username": token_data.get("sub"),
                "role": token_data.get("role"),
                "exp": token_data.get("exp")
            },
            "令牌验证成功"
        )
        
    except AuthenticationException as e:
        return ResponseBuilder.success(
            {"valid": False, "error": str(e)},
            "令牌验证失败"
        )
    except Exception as e:
        logger.error(f"令牌验证异常: {e}")
        raise BusinessException("令牌验证服务暂时不可用")