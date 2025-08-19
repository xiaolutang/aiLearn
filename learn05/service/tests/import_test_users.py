#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入测试用户脚本
从test_accounts.xlsx文件中读取测试账号并导入到数据库
"""

import sys
import os
import pandas as pd
import bcrypt

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, User, Role, Base, engine

def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def create_roles(db):
    """创建角色"""
    roles_data = [
        {"name": "admin", "description": "系统管理员"},
        {"name": "teacher", "description": "教师"},
        {"name": "principal", "description": "校长"},
        {"name": "director", "description": "教务主任"},
        {"name": "student", "description": "学生"},
        {"name": "parent", "description": "家长"},
        {"name": "guest", "description": "访客"}
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"创建角色: {role_data['name']}")
    
    db.commit()
    print("角色创建完成")

def import_test_users():
    """导入测试用户"""
    # 创建数据库表
    create_tables()
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 创建角色
        create_roles(db)
        
        # 读取Excel文件
        df = pd.read_excel('tests/test_accounts.xlsx')
        print(f"读取到 {len(df)} 个测试账号")
        
        # 角色名称映射
        role_mapping = {
            '系统管理员': 'admin',
            '教师': 'teacher',
            '校长': 'admin',  # 校长映射为admin
            '教务主任': 'admin',  # 教务主任映射为admin
            '学生': 'student',
            '家长': 'parent',
            '访客': 'student'  # 访客映射为student
        }
        
        # 导入用户
        for index, row in df.iterrows():
            username = row['用户名']
            password = row['密码']
            email = row['邮箱']
            role_chinese = row['角色']
            role_name = role_mapping.get(role_chinese, role_chinese.lower())
            status = row['状态']
            
            # 检查用户是否已存在
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                print(f"用户 {username} 已存在，跳过")
                continue
            
            # 获取角色
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                print(f"角色 {role_name} 不存在，跳过用户 {username}")
                continue
            
            # 创建用户
            # 使用bcrypt哈希密码
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                role=role_name,
                is_active=(status == 'active'),
                phone_number=None
            )
            
            db.add(user)
            db.flush()  # 获取用户ID
            
            # 检查角色关联是否已存在
            from database import UserRole
            existing_role = db.query(UserRole).filter(
                UserRole.user_id == user.id,
                UserRole.role_id == role.id
            ).first()
            
            if not existing_role:
                # 添加角色关联
                user.roles.append(role)
            
            print(f"创建用户: {username} ({role_name})")
        
        db.commit()
        print("测试用户导入完成")
        
        # 验证导入结果
        user_count = db.query(User).count()
        print(f"数据库中共有 {user_count} 个用户")
        
    except Exception as e:
        print(f"导入失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_test_users()