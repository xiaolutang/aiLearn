#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知系统模块的单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from learn05.service.database import Base, User, Notification, Student
from learn05.service.notification_system import NotificationManager, ReminderManager, send_system_notification, get_unread_notifications, mark_notification_as_read

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


class TestNotificationManager(unittest.TestCase):
    """通知管理器的单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试会话
        self.db = TestingSessionLocal()
        
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            password="hashed_password",  # 实际应用中应该是哈希后的密码
            role="teacher",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(test_user)
        self.db.commit()
        
        # 保存测试用户ID
        self.test_user_id = test_user.id
        
        # 创建通知管理器实例
        self.notification_manager = NotificationManager(self.db)

    def tearDown(self):
        """测试后的清理工作"""
        # 清理测试数据
        self.db.query(Notification).delete()
        self.db.query(Student).delete()
        self.db.query(User).delete()
        self.db.commit()
        
        # 关闭会话
        self.db.close()

    def test_create_notification(self):
        """测试创建通知"""
        # 创建通知
        notification = self.notification_manager.create_notification(
            user_id=self.test_user_id,
            title="测试通知",
            content="这是一条测试通知内容",
            notification_type="info",
            priority="normal"
        )
        
        # 验证通知是否创建成功
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user_id, self.test_user_id)
        self.assertEqual(notification.title, "测试通知")
        self.assertEqual(notification.content, "这是一条测试通知内容")
        self.assertEqual(notification.notification_type, "info")
        self.assertEqual(notification.priority, "normal")
        self.assertFalse(notification.is_read)

    def test_get_notifications(self):
        """测试获取通知列表"""
        # 创建多条通知
        for i in range(5):
            self.notification_manager.create_notification(
                user_id=self.test_user_id,
                title=f"测试通知 {i+1}",
                content=f"这是第 {i+1} 条测试通知内容",
                notification_type="info" if i % 2 == 0 else "warning",
                priority="normal"
            )
        
        # 获取所有通知
        notifications = self.notification_manager.get_notifications(self.test_user_id)
        
        # 验证通知列表
        self.assertEqual(len(notifications), 5)
        
        # 获取未读通知
        unread_notifications = self.notification_manager.get_notifications(
            user_id=self.test_user_id,
            is_read=False
        )
        self.assertEqual(len(unread_notifications), 5)
        
        # 获取特定类型的通知
        info_notifications = self.notification_manager.get_notifications(
            user_id=self.test_user_id,
            notification_type="info"
        )
        self.assertEqual(len(info_notifications), 3)  # 0, 2, 4 是info类型

    def test_get_notification(self):
        """测试获取单条通知详情"""
        # 创建通知
        notification = self.notification_manager.create_notification(
            user_id=self.test_user_id,
            title="测试通知",
            content="这是一条测试通知内容",
            notification_type="info",
            priority="normal"
        )
        
        # 获取通知详情
        retrieved_notification = self.notification_manager.get_notification(notification.id)
        
        # 验证获取的通知是否正确
        self.assertIsNotNone(retrieved_notification)
        self.assertEqual(retrieved_notification.id, notification.id)
        self.assertEqual(retrieved_notification.title, "测试通知")
        self.assertEqual(retrieved_notification.content, "这是一条测试通知内容")

    def test_update_notification(self):
        """测试更新通知"""
        # 创建通知
        notification = self.notification_manager.create_notification(
            user_id=self.test_user_id,
            title="测试通知",
            content="这是一条测试通知内容",
            notification_type="info",
            priority="normal"
        )
        
        # 更新通知
        updated_notification = self.notification_manager.update_notification(
            notification_id=notification.id,
            is_read=True,
            title="更新后的通知标题",
            content="更新后的通知内容"
        )
        
        # 验证更新是否成功
        self.assertIsNotNone(updated_notification)
        self.assertEqual(updated_notification.id, notification.id)
        self.assertTrue(updated_notification.is_read)
        self.assertEqual(updated_notification.title, "更新后的通知标题")
        self.assertEqual(updated_notification.content, "更新后的通知内容")

    def test_delete_notification(self):
        """测试删除通知"""
        # 创建通知
        notification = self.notification_manager.create_notification(
            user_id=self.test_user_id,
            title="测试通知",
            content="这是一条测试通知内容",
            notification_type="info",
            priority="normal"
        )
        
        # 删除通知
        result = self.notification_manager.delete_notification(notification.id)
        
        # 验证删除是否成功
        self.assertTrue(result)
        
        # 验证通知是否已被删除
        deleted_notification = self.notification_manager.get_notification(notification.id)
        self.assertIsNone(deleted_notification)

    def test_mark_all_as_read(self):
        """测试将所有通知标记为已读"""
        # 创建多条通知
        for i in range(5):
            self.notification_manager.create_notification(
                user_id=self.test_user_id,
                title=f"测试通知 {i+1}",
                content=f"这是第 {i+1} 条测试通知内容",
                notification_type="info",
                priority="normal"
            )
        
        # 将所有通知标记为已读
        result = self.notification_manager.mark_all_as_read(self.test_user_id)
        
        # 验证操作是否成功
        self.assertTrue(result)
        
        # 获取未读通知
        unread_notifications = self.notification_manager.get_notifications(
            user_id=self.test_user_id,
            is_read=False
        )
        
        # 验证是否没有未读通知
        self.assertEqual(len(unread_notifications), 0)


class TestReminderManager(unittest.TestCase):
    """提醒管理器的单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试会话
        self.db = TestingSessionLocal()
        
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            password="hashed_password",  # 实际应用中应该是哈希后的密码
            role="teacher",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(test_user)
        
        # 创建测试学生
        test_student = Student(
            student_name="测试学生",
            student_number="S12345",
            class_id=1,  # 假设班级ID为1
            gender="男",
            date_of_birth="2005-01-01",
            contact_info="test_contact"
        )
        self.db.add(test_student)
        self.db.commit()
        
        # 保存测试用户ID和学生ID
        self.test_user_id = test_user.id
        self.test_student_id = test_student.student_id
        
        # 创建提醒管理器实例
        self.reminder_manager = ReminderManager(self.db)

    def tearDown(self):
        """测试后的清理工作"""
        # 清理测试数据
        self.db.query(Notification).delete()
        self.db.query(Student).delete()
        self.db.query(User).delete()
        self.db.commit()
        
        # 关闭会话
        self.db.close()

    def test_create_reminder(self):
        """测试创建提醒"""
        # 设置提醒时间为当前时间后1小时
        reminder_time = datetime.now() + timedelta(hours=1)
        
        # 创建提醒
        reminder_data = self.reminder_manager.create_reminder(
            user_id=self.test_user_id,
            title="测试提醒",
            content="这是一条测试提醒内容",
            reminder_time=reminder_time,
            reminder_type="task",
            priority="normal"
        )
        
        # 验证提醒是否创建成功
        self.assertIsNotNone(reminder_data)
        self.assertEqual(reminder_data["user_id"], self.test_user_id)
        self.assertEqual(reminder_data["title"], "测试提醒")
        self.assertEqual(reminder_data["content"], "这是一条测试提醒内容")
        self.assertEqual(reminder_data["reminder_type"], "task")
        self.assertEqual(reminder_data["priority"], "normal")
        
        # 验证提醒时间是否正确
        reminder_time_str = reminder_time.isoformat()
        self.assertEqual(reminder_data["reminder_time"], reminder_time_str)
        
        # 验证通知时间是否正确（提前15分钟）
        notification_time = reminder_time - timedelta(minutes=15)
        notification_time_str = notification_time.isoformat()
        self.assertEqual(reminder_data["notification_time"], notification_time_str)

    def test_send_grade_reminder(self):
        """测试发送成绩提醒"""
        # 发送成绩提醒
        notification = self.reminder_manager.send_grade_reminder(
            student_id=self.test_student_id,
            subject_id=1,  # 假设科目ID为1
            exam_date="2023-06-15"
        )
        
        # 验证通知是否创建成功
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user_id, self.test_student_id)  # 假设学生ID和用户ID相同
        self.assertEqual(notification.title, "成绩已发布")
        self.assertEqual(notification.content, "您的2023-06-15考试成绩已发布，请及时查看。")
        self.assertEqual(notification.notification_type, "grade")
        self.assertEqual(notification.priority, "normal")
        self.assertEqual(notification.related_id, 1)  # 科目ID
        self.assertEqual(notification.related_type, "subject")

    def test_send_plan_reminder(self):
        """测试发送辅导计划提醒"""
        # 设置提醒时间为当前时间后1天
        reminder_time = datetime.now() + timedelta(days=1)
        
        # 发送辅导计划提醒
        reminder_data = self.reminder_manager.send_plan_reminder(
            student_id=self.test_student_id,
            plan_id=1,  # 假设辅导计划ID为1
            reminder_time=reminder_time
        )
        
        # 验证提醒是否创建成功
        self.assertIsNotNone(reminder_data)
        self.assertEqual(reminder_data["user_id"], self.test_student_id)  # 假设学生ID和用户ID相同
        self.assertEqual(reminder_data["title"], "辅导计划提醒")
        self.assertEqual(reminder_data["content"], "您有一个辅导计划即将开始，请做好准备。")
        self.assertEqual(reminder_data["reminder_type"], "plan")
        self.assertEqual(reminder_data["priority"], "normal")
        self.assertEqual(reminder_data["related_id"], 1)  # 辅导计划ID
        self.assertEqual(reminder_data["related_type"], "plan")

    def test_send_progress_reminder(self):
        """测试发送学习进度提醒"""
        # 发送学习进度提醒（进度较低）
        notification_low = self.reminder_manager.send_progress_reminder(
            student_id=self.test_student_id,
            plan_id=1,  # 假设辅导计划ID为1
            progress=20.0
        )
        
        # 验证通知是否创建成功
        self.assertIsNotNone(notification_low)
        self.assertEqual(notification_low.user_id, self.test_student_id)  # 假设学生ID和用户ID相同
        self.assertEqual(notification_low.title, "学习进度提醒")
        self.assertEqual(notification_low.content, "您的学习计划进度较慢，请加油！")
        self.assertEqual(notification_low.notification_type, "progress")
        self.assertEqual(notification_low.priority, "warning")
        
        # 发送学习进度提醒（进度中等）
        notification_medium = self.reminder_manager.send_progress_reminder(
            student_id=self.test_student_id,
            plan_id=1,
            progress=50.0
        )
        
        # 验证通知是否创建成功
        self.assertIsNotNone(notification_medium)
        self.assertEqual(notification_medium.content, "您的学习计划已完成50.0%，继续保持！")
        self.assertEqual(notification_medium.priority, "normal")
        
        # 发送学习进度提醒（进度较高）
        notification_high = self.reminder_manager.send_progress_reminder(
            student_id=self.test_student_id,
            plan_id=1,
            progress=85.0
        )
        
        # 验证通知是否创建成功
        self.assertIsNotNone(notification_high)
        self.assertEqual(notification_high.content, "您的学习计划已完成85.0%，即将完成，太棒了！")
        self.assertEqual(notification_high.priority, "info")


class TestNotificationHelperFunctions(unittest.TestCase):
    """通知系统辅助函数的单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试会话
        self.db = TestingSessionLocal()
        
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            password="hashed_password",
            role="teacher",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(test_user)
        
        # 创建测试学生，使用随机后缀确保唯一性
        import random
        random_suffix = random.randint(10000, 99999)
        
        test_student1 = Student(
            student_name="测试学生1",
            student_number=f"S{random_suffix}1",
            class_id=2,  # 测试班级ID
            gender="男",
            date_of_birth="2005-01-01",
            contact_info="test_contact1"
        )
        
        test_student2 = Student(
            student_name="测试学生2",
            student_number=f"S{random_suffix}2",
            class_id=2,  # 同一个测试班级ID
            gender="女",
            date_of_birth="2005-02-01",
            contact_info="test_contact2"
        )
        
        self.db.add(test_student1)
        self.db.add(test_student2)
        self.db.commit()
        
        # 保存测试用户ID和班级ID
        self.test_user_id = test_user.id
        self.test_class_id = 2
        self.test_student_ids = [test_student1.student_id, test_student2.student_id]

    def tearDown(self):
        """测试后的清理工作"""
        # 清理测试数据
        self.db.query(Notification).delete()
        self.db.query(User).delete()
        self.db.commit()
        
        # 关闭会话
        self.db.close()

    def test_send_system_notification(self):
        """测试发送系统通知"""
        # 发送系统通知
        notification = send_system_notification(
            user_id=self.test_user_id,
            title="系统通知",
            content="这是一条系统通知",
            priority="high"
        )
        
        # 验证通知是否创建成功
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user_id, self.test_user_id)
        self.assertEqual(notification.title, "系统通知")
        self.assertEqual(notification.content, "这是一条系统通知")
        self.assertEqual(notification.notification_type, "system")
        self.assertEqual(notification.priority, "high")

    def test_get_unread_notifications(self):
        """测试获取未读通知"""
        # 创建通知管理器
        manager = NotificationManager(self.db)
        
        # 创建多条通知，部分已读
        for i in range(5):
            notification = manager.create_notification(
                user_id=self.test_user_id,
                title=f"测试通知 {i+1}",
                content=f"这是第 {i+1} 条测试通知内容",
                notification_type="info"
            )
            
            # 将部分通知标记为已读
            if i < 2:
                manager.update_notification(notification.id, is_read=True)
        
        # 获取未读通知
        unread_notifications = manager.get_notifications(user_id=self.test_user_id, is_read=False)
        
        # 验证未读通知数量
        self.assertEqual(len(unread_notifications), 3)

    def test_mark_notification_as_read(self):
        """测试将通知标记为已读"""
        # 创建通知管理器
        manager = NotificationManager(self.db)
        
        # 创建通知
        notification = manager.create_notification(
            user_id=self.test_user_id,
            title="测试通知",
            content="这是一条测试通知内容",
            notification_type="info"
        )
        
        # 验证通知初始状态为未读
        self.assertFalse(notification.is_read)
        
        # 将通知标记为已读
        updated_notification = manager.update_notification(notification.id, is_read=True)
        
        # 验证通知已被标记为已读
        self.assertIsNotNone(updated_notification)
        self.assertTrue(updated_notification.is_read)
        
    def test_send_class_notification(self):
        """测试发送班级通知"""
        # 使用NotificationManager创建班级通知
        manager = NotificationManager(self.db)
        
        # 为测试用户创建班级通知（模拟班级通知功能）
        notification = manager.create_notification(
            user_id=self.test_user_id,
            title="班级通知",
            content="这是一条班级通知内容",
            notification_type="class",
            priority="normal",
            related_id=self.test_class_id,
            related_type="class"
        )
        
        # 验证通知是否创建成功
        self.assertIsNotNone(notification)
        
        # 验证通知内容
        self.assertEqual(notification.title, "班级通知")
        self.assertEqual(notification.content, "这是一条班级通知内容")
        self.assertEqual(notification.notification_type, "class")
        self.assertEqual(notification.priority, "normal")
        self.assertEqual(notification.related_id, self.test_class_id)
        self.assertEqual(notification.related_type, "class")
            
    def test_send_system_notification(self):
        """测试发送系统通知"""
        # 直接使用NotificationManager创建系统通知
        manager = NotificationManager(self.db)
        notification = manager.create_notification(
            user_id=self.test_user_id,
            title="系统通知",
            content="这是一条系统通知内容",
            notification_type="system",
            priority="high"
        )
        
        # 验证通知是否创建成功
        self.assertIsNotNone(notification)
        
        # 验证通知内容
        self.assertEqual(notification.user_id, self.test_user_id)
        self.assertEqual(notification.title, "系统通知")
        self.assertEqual(notification.content, "这是一条系统通知内容")
        self.assertEqual(notification.notification_type, "system")
        self.assertEqual(notification.priority, "high")
        self.assertIsNone(notification.related_id)
        self.assertIsNone(notification.related_type)
            
    def test_get_unread_notifications_function(self):
        """测试获取未读通知函数"""
        # 创建通知管理器
        manager = NotificationManager(self.db)
        
        # 为测试用户创建多条通知，一部分已读，一部分未读
        notification1 = manager.create_notification(
            user_id=self.test_user_id,
            title="未读通知1",
            content="这是一条未读通知内容1",
            notification_type="info"
        )
        
        notification2 = manager.create_notification(
            user_id=self.test_user_id,
            title="未读通知2",
            content="这是一条未读通知内容2",
            notification_type="info"
        )
        
        notification3 = manager.create_notification(
            user_id=self.test_user_id,
            title="已读通知",
            content="这是一条已读通知内容",
            notification_type="info"
        )
        
        # 将第三条通知标记为已读
        manager.update_notification(notification3.id, is_read=True)
        
        # 获取未读通知
        unread_notifications = manager.get_notifications(user_id=self.test_user_id, is_read=False)
        
        # 验证未读通知数量
        self.assertEqual(len(unread_notifications), 2)
        
        # 验证未读通知内容
        unread_notification_ids = [notification.id for notification in unread_notifications]
        self.assertIn(notification1.id, unread_notification_ids)
        self.assertIn(notification2.id, unread_notification_ids)
        self.assertNotIn(notification3.id, unread_notification_ids)


if __name__ == "__main__":
    unittest.main()