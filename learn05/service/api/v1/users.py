# -*- coding: utf-8 -*-
"""
用户管理API路由

本模块提供用户管理相关的API接口。
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db, User
from models.response import APIResponse, ResponseBuilder, PaginatedResponse
from middleware.exception_handler import BusinessException, AuthenticationException
from auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


@router.get("/", response_model=APIResponse[PaginatedResponse[UserResponse]])
async def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    try:
        # 权限检查
        if current_user.role != 'admin':
            raise ValidationException("只有管理员可以查看用户列表")
        
        # 构建查询
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # 分页
        total = query.count()
        users = query.offset((page - 1) * page_size).limit(page_size).all()
        
        user_responses = [UserResponse.from_orm(user) for user in users]
        paginated_response = PaginatedResponse(
            items=user_responses,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
        
        return ResponseBuilder.success(paginated_response, "获取用户列表成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取用户列表异常: {e}")
        raise BusinessException("获取用户列表失败")


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    try:
        # 权限检查：只能查看自己或管理员查看所有
        if current_user.role != 'admin' and current_user.id != user_id:
            raise ValidationException("无权查看此用户信息")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValidationException("用户不存在")
        
        return ResponseBuilder.success(UserResponse.from_orm(user), "获取用户信息成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取用户信息异常: {e}")
        raise BusinessException("获取用户信息失败")