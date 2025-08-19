#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查系统初始化脚本
用于验证系统角色和管理员账户是否已成功创建
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from learn05.service.database import Base, User, Role

# 创建数据库引擎
DATABASE_URL = "sqlite:///student_database.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("===== 检查系统初始化状态 =====")

# 检查角色表
print("\n1. 检查系统角色:")
roles = db.query(Role).all()
if roles:
    print(f"找到 {len(roles)} 个系统角色:")
    for role in roles:
        print(f"- ID: {role.id}, 名称: {role.name}, 描述: {role.description}")
else:
    print("未找到任何系统角色!")

# 检查管理员账户
print("\n2. 检查管理员账户:")
admin_users = db.query(User).filter(User.role == "admin").all()
if admin_users:
    print(f"找到 {len(admin_users)} 个管理员账户:")
    for user in admin_users:
        print(f"- ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 角色: {user.role}")
else:
    print("未找到管理员账户!")

# 检查所有用户
print("\n3. 检查所有用户:")
all_users = db.query(User).all()
if all_users:
    print(f"数据库中共有 {len(all_users)} 个用户账户")
else:
    print("数据库中没有用户账户!")

# 关闭数据库连接
db.close()

print("\n===== 检查完成 =====")