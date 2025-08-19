# -*- coding: utf-8 -*-
"""
用户模型模块
定义用户相关的数据结构
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, EmailStr, validator
import datetime
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="电子邮箱", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    full_name: str = Field(..., min_length=2, max_length=100, description="全名")
    role: str = Field("student", description="用户角色", pattern=r"^(admin|teacher|student|parent)$")
    is_active: bool = Field(True, description="是否活跃")
    school_id: Optional[str] = Field(None, description="学校ID")
    department_id: Optional[str] = Field(None, description="部门ID")
    profile_picture: Optional[str] = Field(None, description="头像URL")
    phone_number: Optional[str] = Field(None, description="手机号码")
    address: Optional[str] = Field(None, max_length=200, description="地址")
    date_of_birth: Optional[datetime.date] = Field(None, description="出生日期")
    join_date: Optional[datetime.date] = Field(datetime.date.today(), description="加入日期")
    phone_number: Optional[str] = Field(None, description="电话号码")
    profile_picture: Optional[str] = Field(None, description="头像URL")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """验证电话号码格式"""
        if v and not v.replace('-', '').replace(' ', '').isdigit():
            raise ValueError("电话号码格式不正确")
        return v


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=8, description="密码")
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError("密码长度至少为8位")
        # 可以添加更多密码强度验证规则
        # if not any(char.isupper() for char in v):
        #     raise ValueError("密码必须包含至少一个大写字母")
        # if not any(char.islower() for char in v):
        #     raise ValueError("密码必须包含至少一个小写字母")
        # if not any(char.isdigit() for char in v):
        #     raise ValueError("密码必须包含至少一个数字")
        return v


class UserUpdate(UserBase):
    """用户更新模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="全名")
    password: Optional[str] = Field(None, min_length=8, description="密码")


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="用户ID")
    hashed_password: str = Field(..., description="加密密码")
    is_active: bool = Field(True, description="是否激活")
    is_verified: bool = Field(False, description="是否验证")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    last_login: Optional[datetime.datetime] = Field(None, description="最后登录时间")
    
    class Config:
        """配置类"""
        orm_mode = True


class UserResponse(UserBase):
    """用户响应模型"""
    id: str = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否激活")
    is_verified: bool = Field(..., description="是否验证")
    created_at: datetime.datetime = Field(..., description="创建时间")
    last_login: Optional[datetime.datetime] = Field(None, description="最后登录时间")


class Token(BaseModel):
    """令牌模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = Field(None, description="用户名")
    scopes: List[str] = Field([], description="权限范围")


class UserSettings(BaseModel):
    """用户设置模型"""
    user_id: str = Field(..., description="用户ID")
    theme: str = Field("light", description="主题", pattern=r"^(light|dark|system)$")
    language: str = Field("zh-CN", description="语言")
    notifications: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email": True,
            "sms": False,
            "push": True
        }, 
        description="通知设置"
    )
    timezone: str = Field("Asia/Shanghai", description="时区")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")


class UserProfile(BaseModel):
    """用户个人资料模型"""
    user_id: str = Field(..., description="用户ID")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    education: Optional[str] = Field(None, description="教育背景")
    work_experience: Optional[str] = Field(None, description="工作经历")
    interests: List[str] = Field(default_factory=list, description="兴趣爱好")
    social_links: Dict[str, str] = Field(default_factory=dict, description="社交链接")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")


class PaginatedUsers(BaseModel):
    """分页用户列表模型"""
    users: List[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总用户数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


# 用户角色权限定义
ROLE_PERMISSIONS = {
    "admin": [
        "manage_users",
        "manage_classes",
        "manage_subjects",
        "view_all_grades",
        "edit_all_grades",
        "generate_reports",
        "system_settings"
    ],
    "teacher": [
        "manage_own_classes",
        "view_own_classes_grades",
        "edit_own_classes_grades",
        "generate_class_reports",
        "view_student_profiles",
        "create_coaching_plans"
    ],
    "student": [
        "view_own_grades",
        "view_own_performance",
        "view_recommended_practice",
        "view_coaching_plans"
    ],
    "parent": [
        "view_child_grades",
        "view_child_performance",
        "view_child_coaching_plans"
    ]
}


def get_user_permissions(role: str) -> List[str]:
    """获取用户角色的权限列表
    
    Args:
        role: 用户角色
        
    Returns:
        List[str]: 权限列表
    """
    return ROLE_PERMISSIONS.get(role, [])


def user_has_permission(user_role: str, permission: str) -> bool:
    """检查用户是否有特定权限
    
    Args:
        user_role: 用户角色
        permission: 权限名称
        
    Returns:
        bool: 是否有权限
    """
    permissions = get_user_permissions(user_role)
    return permission in permissions