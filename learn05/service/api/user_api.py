# -*- coding: utf-8 -*-
"""
用户API接口
提供用户相关的HTTP接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import List, Optional
import datetime
import os
from pathlib import Path

from models.user import (
    UserCreate, UserUpdate, UserResponse, Token, TokenData, 
    UserSettings, UserProfile, PaginatedUsers
)
from services.user_service import get_user_service, UserService, create_access_token
from config.core_config import get_config

# 创建路由器
router = APIRouter()

# 配置
config = get_config()

# OAuth2密码持有者令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
):
    """获取当前登录用户
    
    Args:
        token: OAuth2令牌
        user_service: 用户服务实例
        
    Returns:
        UserInDB: 当前登录用户
        
    Raises:
        HTTPException: 令牌无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.jwt.secret_key, algorithms=[config.jwt.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=Token, tags=["认证"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """\获取访问令牌
    
    Args:
        form_data: OAuth2密码请求表单
        user_service: 用户服务实例
        
    Returns:
        Token: 访问令牌和令牌类型
        
    Raises:
        HTTPException: 认证失败
    """
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = datetime.timedelta(minutes=config.jwt.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["用户管理"])
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """创建新用户
    
    Args:
        user_data: 用户创建数据
        user_service: 用户服务实例
        
    Returns:
        UserResponse: 创建的用户信息
        
    Raises:
        HTTPException: 创建失败
    """
    try:
        return user_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me", response_model=UserResponse, tags=["用户管理"])
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """获取当前登录用户信息
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        UserResponse: 当前登录用户信息
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        phone_number=current_user.phone_number,
        profile_picture=current_user.profile_picture,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.get("/", response_model=PaginatedUsers, tags=["用户管理"])
async def get_users(
    page: int = 1,
    limit: int = 10,
    role: Optional[str] = None,
    search: Optional[str] = None,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """获取用户列表
    
    Args:
        page: 当前页码
        limit: 每页数量
        role: 用户角色过滤
        search: 搜索关键词
        user_service: 用户服务实例
        current_user: 当前登录用户
        
    Returns:
        PaginatedUsers: 分页用户列表
    """
    # 构建过滤条件
    filters = {}
    if role:
        filters["role"] = role
    if search:
        filters["search"] = search
    
    return user_service.get_users(page=page, limit=limit, **filters)


@router.get("/{user_id}", response_model=UserResponse, tags=["用户管理"])
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """获取单个用户信息
    
    Args:
        user_id: 用户ID
        user_service: 用户服务实例
        current_user: 当前登录用户
        
    Returns:
        UserResponse: 用户信息
        
    Raises:
        HTTPException: 用户不存在
    """
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    return UserResponse(
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
    )


@router.put("/{user_id}", response_model=UserResponse, tags=["用户管理"])
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """更新用户信息
    
    Args:
        user_id: 用户ID
        user_data: 用户更新数据
        user_service: 用户服务实例
        current_user: 当前登录用户
        
    Returns:
        UserResponse: 更新后的用户信息
        
    Raises:
        HTTPException: 更新失败或用户不存在
    """
    # 检查权限（只能更新自己或管理员可以更新任何用户）
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限更新该用户")
    
    try:
        return user_service.update_user(user_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["用户管理"])
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """删除用户
    
    Args:
        user_id: 用户ID
        user_service: 用户服务实例
        current_user: 当前登录用户
        
    Returns:
        None
        
    Raises:
        HTTPException: 删除失败或用户不存在
    """
    # 检查权限（只能删除自己或管理员可以删除任何用户）
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限删除该用户")
    
    try:
        result = user_service.delete_user(user_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除用户失败")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/me/profile-picture", response_model=UserResponse, tags=["用户管理"])
async def upload_profile_picture(
    file: UploadFile = File(...),
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """上传用户头像
    
    Args:
        file: 头像文件
        user_service: 用户服务实例
        current_user: 当前登录用户
        
    Returns:
        UserResponse: 更新后的用户信息
        
    Raises:
        HTTPException: 上传失败
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只支持JPG、PNG和GIF格式的图片")
    
    # 验证文件大小（限制为5MB）
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size and file.size > max_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小不能超过5MB")
    
    try:
        # 创建上传目录
        upload_dir = Path(config.fastapi.upload_dir) / "profile_pictures"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        file_extension = Path(file.filename).suffix
        file_name = f"{current_user.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
        file_path = upload_dir / file_name
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # 更新用户信息
        user_update = UserUpdate(profile_picture=str(file_path))
        updated_user = user_service.update_user(current_user.id, user_update)
        
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传头像失败: {str(e)}")


@router.get("/me/settings", response_model=UserSettings, tags=["用户管理"])
async def get_user_settings(
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """获取用户设置
    
    Args:
        user_service: 用户服务实例
        current_user: 当前登录用户
        
    Returns:
        UserSettings: 用户设置信息
        
    Raises:
        HTTPException: 获取失败
    """
    try:
        # 查询用户设置
        result = user_service.db_manager.execute_query(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (current_user.id,)
        )
        
        if not result or len(result) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户设置不存在")
        
        settings_data = result[0]
        return UserSettings(
            user_id=settings_data[0],
            theme=settings_data[1],
            language=settings_data[2],
            notifications=eval(settings_data[3]),  # 从字符串解析为字典
            timezone=settings_data[4],
            updated_at=settings_data[5]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/me/settings", response_model=UserSettings, tags=["用户管理"])
async def update_user_settings(
    settings_data: UserSettings,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """更新用户设置
    
    Args:
        settings_data: 用户设置数据
        user_service: 用户服务实例
        current_user: 当前登录用户
        
    Returns:
        UserSettings: 更新后的用户设置
        
    Raises:
        HTTPException: 更新失败
    """
    try:
        # 验证用户ID
        if settings_data.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有权限更新该用户设置")
        
        # 更新用户设置
        result = user_service.db_manager.execute_query(
            """
            UPDATE user_settings SET theme = ?, language = ?, notifications = ?, 
            timezone = ?, updated_at = ? WHERE user_id = ?
            """,
            (
                settings_data.theme,
                settings_data.language,
                str(settings_data.notifications),  # 保存为字符串
                settings_data.timezone,
                datetime.datetime.now(),
                settings_data.user_id
            )
        )
        
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新用户设置失败")
        
        # 返回更新后的设置
        return settings_data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))