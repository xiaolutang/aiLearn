#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的测试文件，用于验证数据库表创建和基本功能
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# 导入数据库模型
from learn05.service.database import Base, User, Role, Class, Student, Subject, Grade

# 创建测试数据库引擎
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 创建会话工厂
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_table_creation():
    """测试表创建和基本数据操作"""
    # 创建所有表
    print("创建表...")
    Base.metadata.create_all(bind=engine)
    print("表创建完成")
    
    # 验证表是否已创建
    print("\n验证表是否存在:")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
    
    # 尝试插入数据
    print("\n尝试插入数据...")
    db = next(get_db())
    
    try:
        # 创建角色
        admin_role = Role(name="admin", description="管理员角色")
        db.add(admin_role)
        db.commit()
        print("插入角色成功")

        # 查询角色
        role = db.query(Role).filter(Role.name == "admin").first()
        if role:
            print(f"查询到角色: {role.name}")
        else:
            print("未查询到角色")
        
        # 创建用户
        test_user = User(username="testuser", password="password", role="admin", email="test@example.com")
        test_user.roles.append(admin_role)
        db.add(test_user)
        db.commit()
        print("插入用户成功")
        
        # 查询用户
        user = db.query(User).filter(User.username == "testuser").first()
        if user:
            print(f"查询到用户: {user.username}")
            print(f"用户角色: {[role.name for role in user.roles]}")
        else:
            print("未查询到用户")
        
    except Exception as e:
        print(f"操作数据时出错: {e}")
        db.rollback()
    finally:
        db.close()
    
if __name__ == "__main__":
    test_table_creation()