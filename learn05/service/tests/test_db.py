# -*- coding: utf-8 -*-
"""
数据库测试脚本
直接测试数据库连接和表创建
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# 测试配置
TEST_DATABASE_URL = "sqlite:///:memory:"

# 创建测试数据库引擎和会话
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 创建测试会话工厂
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 导入database模块
import learn05.service.database as database

# 替换为测试数据库
database.engine = test_engine
database.SessionLocal = TestingSessionLocal

# 导入Base和模型类
from learn05.service.database import Base, User, Role, Class, Student, Subject, Grade

# 打印导入的模型
print("Imported models:")
print(f"Base: {Base}")
print(f"User: {User}")
print(f"Role: {Role}")
print(f"Class: {Class}")
print(f"Student: {Student}")
print(f"Subject: {Subject}")
print(f"Grade: {Grade}")

# 打印元数据中的表
print("\nTables in metadata:")
for table_name in Base.metadata.tables.keys():
    print(f"- {table_name}")

# 创建表
print("\nCreating tables...")
Base.metadata.create_all(bind=test_engine)
print("Tables created successfully.")

# 验证表是否创建成功
print("\nVerifying tables...")
with test_engine.connect() as connection:
    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = result.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"- {table[0]}")

# 测试添加数据
try:
    print("\nTesting data insertion...")
    db = TestingSessionLocal()
    
    # 添加角色
    admin_role = Role(name="admin", description="系统管理员")
    db.add(admin_role)
    db.commit()
    
    # 查询角色
    role = db.query(Role).filter(Role.name == "admin").first()
    print(f"Found role: {role.name}")
    
    print("Data insertion test passed.")
except Exception as e:
    print(f"Data insertion test failed: {e}")
finally:
    db.close()

print("\nTest completed.")