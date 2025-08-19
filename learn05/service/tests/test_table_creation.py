#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试脚本，用于验证数据库表创建和数据访问
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.append(project_root)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from learn05.service.database import Base, User, Role, Class, Student, Subject, Grade

# 创建测试数据库引擎
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 创建会话工厂
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 打印导入的模型
print("导入的模型:")
for model in [User, Role, Class, Student, Subject, Grade]:
    print(f"- {model.__name__}")

# 创建所有表
print("\n创建表...")
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
db = TestingSessionLocal()

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

except Exception as e:
    print(f"插入数据时出错: {e}")
finally:
    db.close()

print("\n测试完成")