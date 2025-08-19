#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块
提供用户的注册、登录、权限管理等功能
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from database import get_db, User, Role, UserRole
from auth import (
    hash_password, 
    verify_password, 
    create_access_token,
    get_current_user, 
    get_user_role
)


class UserManager:
    """用户管理类"""
    
    def __init__(self, db: Session = None):
        if db is None:
            self.db = next(get_db())
        else:
            self.db = db
    
    def create_user(self, username: str, email: str, password: str, phone: str = None, role_ids: List[int] = None, role: str = None) -> User:
        """创建用户"""
        # 验证用户名和邮箱是否已存在
        existing_user = self.db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                raise ValueError(f"用户名已存在: {username}")
            if existing_user.email == email:
                raise ValueError(f"邮箱已存在: {email}")
        
        # 哈希密码
        hashed_password = hash_password(password)
        
        # 根据role_ids确定用户角色
        user_role = role or "student"  # 默认为student
        if role_ids and len(role_ids) > 0:
            # 获取第一个角色的名称作为用户的主要角色
            first_role = self.db.query(Role).filter(Role.id == role_ids[0]).first()
            if first_role:
                user_role = first_role.name
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            phone_number=phone,
            role=user_role,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )
        
        # 保存到数据库
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # 分配角色
        if role_ids:
            self.assign_roles(user.id, role_ids)
        
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """获取用户信息"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户信息"""
        return self.db.query(User).filter(User.username == username).first()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """更新用户信息"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        # 更新字段
        for key, value in kwargs.items():
            if key == "password" and value:
                # 密码需要哈希
                user.password = hash_password(value)
            elif key == "role_ids" and value:
                # 角色需要单独处理
                self.assign_roles(user_id, value)
            elif hasattr(user, key) and key != "user_id":
                setattr(user, key, value)
        
        # 更新时间
        user.updated_at = datetime.now()
        
        # 保存到数据库
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        # 从数据库删除
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """激活用户"""
        return self.update_user(user_id, is_active=True)
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """禁用用户"""
        return self.update_user(user_id, is_active=False)
    
    def assign_roles(self, user_id: int, role_ids: List[int]) -> List[UserRole]:
        """分配角色给用户"""
        # 先删除已有的角色关联
        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        
        # 创建新的角色关联
        user_roles = []
        for role_id in role_ids:
            # 验证角色是否存在
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise ValueError(f"角色不存在: {role_id}")
            
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
            user_roles.append(user_role)
        
        # 保存到数据库
        self.db.commit()
        
        return user_roles
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """获取用户的角色"""
        user = self.get_user(user_id)
        if not user:
            return []
        return user.roles
    
    def get_users(self, page: int = 1, page_size: int = 10, keyword: str = None, role_id: int = None, is_active: bool = None) -> Dict[str, Any]:
        """获取用户列表"""
        # 构建查询
        query = self.db.query(User)
        
        # 搜索关键词
        if keyword:
            query = query.filter(
                (User.username.ilike(f"%{keyword}%")) | 
                (User.full_name.ilike(f"%{keyword}%")) | 
                (User.email.ilike(f"%{keyword}%"))
            )
        
        # 按角色过滤
        if role_id:
            query = query.join(UserRole).filter(UserRole.role_id == role_id)
        
        # 按状态过滤
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        users = query.order_by(desc(User.created_at)).offset(offset).limit(page_size).all()
        
        # 构建结果
        results = []
        for user in users:
            results.append({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "is_active": user.is_active,
                "roles": [{
                    "role_id": role.id,
                    "role_name": role.name
                } for role in user.roles]
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "data": results
        }
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """修改密码"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        # 验证当前密码
        if not verify_password(current_password, user.password):
            return False
        
        # 更新密码
        user.password = hash_password(new_password)
        user.updated_at = datetime.now()
        
        # 保存到数据库
        self.db.commit()
        
        return True
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """重置密码（管理员操作）"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        # 更新密码
        user.password = hash_password(new_password)
        user.updated_at = datetime.now()
        
        # 保存到数据库
        self.db.commit()
        
        return True


class RoleManager:
    """角色管理类"""
    
    def __init__(self, db: Session = None):
        if db is None:
            self.db = next(get_db())
        else:
            self.db = db
    
    def create_role(self, name: str, description: str = None, permissions: Dict[str, Any] = None) -> Role:
        """创建角色"""
        # 验证角色名是否已存在
        existing_role = self.db.query(Role).filter(Role.name == name).first()
        if existing_role:
            raise ValueError(f"角色名已存在: {name}")
        
        # 创建角色
        role = Role(
            name=name,
            description=description,
            permissions=json.dumps(permissions) if permissions else "{}",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 保存到数据库
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        return role
    
    def get_role(self, role_id: int) -> Optional[Role]:
        """获取角色信息"""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """根据角色名获取角色信息"""
        return self.db.query(Role).filter(Role.name == name).first()
    
    def update_role(self, role_id: int, **kwargs) -> Optional[Role]:
        """更新角色信息"""
        role = self.get_role(role_id)
        if not role:
            return None
        
        # 更新字段
        for key, value in kwargs.items():
            if key == "permissions" and value:
                # 权限需要JSON序列化
                role.permissions = json.dumps(value)
            elif hasattr(role, key) and key != "role_id":
                setattr(role, key, value)
        
        # 更新时间
        role.updated_at = datetime.now()
        
        # 保存到数据库
        self.db.commit()
        self.db.refresh(role)
        
        return role
    
    def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        role = self.get_role(role_id)
        if not role:
            return False
        
        # 检查是否有用户关联此角色
        user_roles_count = self.db.query(UserRole).filter(UserRole.role_id == role_id).count()
        if user_roles_count > 0:
            raise ValueError(f"角色 '{role.name}' 有 {user_roles_count} 个用户关联，无法删除")
        
        # 从数据库删除
        self.db.delete(role)
        self.db.commit()
        
        return True
    
    def get_roles(self, page: int = 1, page_size: int = 10, keyword: str = None) -> Dict[str, Any]:
        """获取角色列表"""
        # 构建查询
        query = self.db.query(Role)
        
        # 搜索关键词
        if keyword:
            query = query.filter(
                (Role.name.ilike(f"%{keyword}%")) | 
                (Role.description.ilike(f"%{keyword}%"))
            )
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        roles = query.order_by(asc(Role.role_name)).offset(offset).limit(page_size).all()
        
        # 构建结果
        results = []
        for role in roles:
            results.append({
                "role_id": role.id,
                "role_name": role.name,
                "description": role.description,
                "permissions": json.loads(role.permissions),
                "created_at": role.created_at.isoformat() if role.created_at else None,
                "updated_at": role.updated_at.isoformat() if role.updated_at else None
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "data": results
        }
    
    def check_permission(self, user_id: int, permission: str) -> bool:
        """检查用户是否有特定权限"""
        # 获取用户的角色
        user_manager = UserManager(self.db)
        roles = user_manager.get_user_roles(user_id)
        
        # 检查每个角色的权限
        for role in roles:
            try:
                permissions = json.loads(role.permissions)
                if permissions.get(permission, False):
                    return True
            except json.JSONDecodeError:
                continue
        
        return False


# 便捷函数
def authenticate_user(username: str, password: str, db: Session = None) -> Optional[User]:
    """验证用户凭据"""
    user_manager = UserManager(db)
    
    # 获取用户
    user = user_manager.get_user_by_username(username)
    if not user or not user.is_active:
        return None
    
    # 验证密码
    if not verify_password(password, user.password):
        return None
    
    return user

def create_user_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """创建用户令牌"""
    # 创建访问令牌
    return create_access_token(
        data={"sub": str(user_id)}
    )

def get_user_profile(user_id: int, db: Session = None) -> Dict[str, Any]:
        """获取用户个人资料"""
        if db is None:
            db = next(get_db())
        user_manager = UserManager(db)
        user = user_manager.get_user(user_id)
        
        if not user:
            return None
        
        # 获取用户角色
        roles = user_manager.get_user_roles(user_id)
        
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "roles": [{
                "role_id": role.id,
                "role_name": role.name,
                "description": role.description
            } for role in roles]
        }

def init_system_roles(db: Session = None) -> List[Role]:
    """初始化系统角色"""
    if db is None:
        db = next(get_db())
    role_manager = RoleManager(db)
    
    # 定义系统角色
    system_roles = [
        {
            "name": "超级管理员",
            "description": "系统超级管理员，拥有所有权限",
            "permissions": {
                "user_manage": True,
                "role_manage": True,
                "grade_manage": True,
                "student_manage": True,
                "class_manage": True,
                "subject_manage": True,
                "tutoring_manage": True,
                "analysis": True,
                "system_config": True
            }
        },
        {
            "name": "教师",
            "description": "教师角色，拥有成绩管理、学生管理等权限",
            "permissions": {
                "grade_manage": True,
                "student_manage": True,
                "class_manage": True,
                "subject_manage": True,
                "tutoring_manage": True,
                "analysis": True,
                "user_manage": False,
                "role_manage": False,
                "system_config": False
            }
        },
        {
            "name": "学生",
            "description": "学生角色，拥有查看自己成绩、获取辅导建议等权限",
            "permissions": {
                "analysis": True,
                "tutoring_manage": True,
                "user_manage": False,
                "role_manage": False,
                "grade_manage": False,
                "student_manage": False,
                "class_manage": False,
                "subject_manage": False,
                "system_config": False
            }
        },
        {
            "name": "家长",
            "description": "家长角色，拥有查看子女成绩、获取辅导建议等权限",
            "permissions": {
                "analysis": True,
                "tutoring_manage": True,
                "user_manage": False,
                "role_manage": False,
                "grade_manage": False,
                "student_manage": False,
                "class_manage": False,
                "subject_manage": False,
                "system_config": False
            }
        }
    ]
    
    # 创建或更新角色
    created_roles = []
    for role_data in system_roles:
        role = role_manager.get_role_by_name(role_data["name"])
        if role:
            # 更新角色
            updated_role = role_manager.update_role(
                role.id,
                description=role_data["description"],
                permissions=role_data["permissions"]
            )
            created_roles.append(updated_role)
        else:
            # 创建角色
            new_role = role_manager.create_role(
                name=role_data["name"],
                description=role_data["description"],
                permissions=role_data["permissions"]
            )
            created_roles.append(new_role)
    
    return created_roles

def init_system_admin(username: str, password: str, email: str, name: str, db: Session = None) -> User:
    """初始化系统管理员账户"""
    if db is None:
        db = next(get_db())
    user_manager = UserManager(db)
    role_manager = RoleManager(db)
    
    # 检查管理员用户是否已存在
    admin_user = user_manager.get_user_by_username(username)
    if admin_user:
        return admin_user
    
    # 获取超级管理员角色
    admin_role = role_manager.get_role_by_name("超级管理员")
    if not admin_role:
        raise ValueError("超级管理员角色不存在，请先初始化系统角色")
    
    # 创建管理员用户
    admin_user = user_manager.create_user(
        username=username,
        password=password,
        email=email,
        role="admin"
    )
    
    return admin_user