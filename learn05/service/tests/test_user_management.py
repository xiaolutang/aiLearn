#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块的单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from learn05.service.database import Base, User, Role, UserRole
from learn05.service.user_management import UserManager, authenticate_user

# 创建测试数据库引擎
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 创建测试会话工厂
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 立即创建所有表
Base.metadata.create_all(bind=test_engine)


class TestUserManager(unittest.TestCase):
    """用户管理类的单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试会话
        self.db = TestingSessionLocal()
        
        # 检查是否已存在教师角色，如果不存在则创建
        teacher_role = self.db.query(Role).filter(Role.name == "teacher").first()
        if not teacher_role:
            teacher_role = Role(name="teacher", description="教师角色")
            self.db.add(teacher_role)
            self.db.commit()
        
        # 保存测试角色ID
        self.test_role_id = teacher_role.id
        
        # 创建用户管理器实例
        self.user_manager = UserManager(self.db)

    def tearDown(self):
        """测试后的清理工作"""
        # 清理测试数据
        self.db.query(UserRole).delete()
        self.db.query(User).delete()
        self.db.query(Role).delete()
        self.db.commit()
        
        # 关闭会话
        self.db.close()

    def test_create_user(self):
        """测试创建用户"""
        # 创建用户
        user = self.user_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            phone="13800138000",
            role_ids=[self.test_role_id]
        )
        
        # 验证用户是否创建成功
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.phone_number, "13800138000")
        self.assertEqual(user.role, "teacher")
        self.assertTrue(user.is_active)

    def test_get_user_by_username(self):
        """测试根据用户名获取用户"""
        # 创建用户
        user = self.user_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role_ids=[self.test_role_id]
        )
        
        # 获取用户
        retrieved_user = self.user_manager.get_user_by_username("testuser")
        
        # 验证获取的用户是否正确
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "testuser")
        self.assertEqual(retrieved_user.email, "test@example.com")

    def test_update_user(self):
        """测试更新用户信息"""
        # 创建测试用户
        user = self.user_manager.create_user(
            username="testuser",
            password="password123",
            role_ids=[self.test_role_id],
            email="test@example.com"
        )
        
        # 更新用户信息
        updated_user = self.user_manager.update_user(
            user_id=user.id,
            email="updated@example.com",
            phone_number="1234567890"
        )
        
        # 验证更新是否成功
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.email, "updated@example.com")
        self.assertEqual(updated_user.phone_number, "1234567890")

    @patch('learn05.service.user_management.verify_password')
    def test_authenticate_user(self, mock_verify_password):
        """测试用户认证"""
        # 创建测试用户
        user = self.user_manager.create_user(
            username="testuser",
            password="password123",
            role_ids=[self.test_role_id],
            email="test@example.com"
        )
        
        # 模拟验证密码函数
        mock_verify_password.return_value = True
        
        # 测试验证用户
        authenticated_user = authenticate_user("testuser", "password123", self.db)
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.username, "testuser")
        
        # 修改模拟返回值，测试错误的密码
        mock_verify_password.return_value = False
        authenticated_user = authenticate_user("testuser", "wrongpassword", self.db)
        self.assertIsNone(authenticated_user)


if __name__ == "__main__":
    unittest.main()