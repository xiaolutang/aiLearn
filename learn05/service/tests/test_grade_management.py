#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成绩管理模块的单元测试
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

from learn05.service.database import Base, Student, Subject, Grade, Class
from learn05.service.grade_management import GradeManager

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


class TestGradeManager(unittest.TestCase):
    """成绩管理类的单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试会话
        self.db = TestingSessionLocal()
        
        # 检查是否已存在测试班级，如果不存在则创建
        test_class = self.db.query(Class).filter(Class.class_name == "测试班级").first()
        if not test_class:
            test_class = Class(class_name="测试班级", grade_level=10)
            self.db.add(test_class)
            self.db.commit()
        
        # 检查是否已存在测试学生，如果不存在则创建
        test_student = self.db.query(Student).filter(Student.student_name == "测试学生").first()
        if not test_student:
            test_student = Student(
                student_name="测试学生",
                student_number="S12345",
                gender="男",
                date_of_birth="2005-01-01",
                class_id=test_class.class_id
            )
            self.db.add(test_student)
            self.db.commit()
        
        # 检查是否已存在测试科目，如果不存在则创建
        test_subject = self.db.query(Subject).filter(Subject.subject_name == "数学").first()
        if not test_subject:
            test_subject = Subject(subject_name="数学", credit=5)
            self.db.add(test_subject)
            self.db.commit()
        
        # 保存测试数据ID
        self.test_class_id = test_class.class_id
        self.test_student_id = test_student.student_id
        self.test_subject_id = test_subject.subject_id
        
        # 创建成绩管理器实例
        self.grade_manager = GradeManager(self.db)

    def tearDown(self):
        """测试后的清理工作"""
        # 清理测试数据
        self.db.query(Grade).delete()
        self.db.query(Student).delete()
        self.db.query(Subject).delete()
        self.db.query(Class).delete()
        self.db.commit()
        
        # 关闭会话
        self.db.close()

    def test_add_grade(self):
        """测试添加成绩记录"""
        # 添加成绩
        grade = self.grade_manager.add_grade(
            student_id=self.test_student_id,
            subject_id=self.test_subject_id,
            exam_date="2023-06-01",
            score=85.5,
            exam_type="期末考试"
        )
        
        # 验证成绩是否添加成功
        self.assertIsNotNone(grade)
        self.assertEqual(grade.student_id, self.test_student_id)
        self.assertEqual(grade.subject_id, self.test_subject_id)
        self.assertEqual(grade.exam_date, "2023-06-01")
        self.assertEqual(grade.score, 85.5)
        self.assertEqual(grade.exam_type, "期末考试")

    def test_get_grade(self):
        """测试获取成绩记录"""
        # 添加成绩
        grade = self.grade_manager.add_grade(
            student_id=self.test_student_id,
            subject_id=self.test_subject_id,
            exam_date="2023-06-01",
            score=85.5,
            exam_type="期末考试"
        )
        
        # 获取成绩
        retrieved_grade = self.grade_manager.get_grade(grade.grade_id)
        
        # 验证获取的成绩是否正确
        self.assertIsNotNone(retrieved_grade)
        self.assertEqual(retrieved_grade.grade_id, grade.grade_id)
        self.assertEqual(retrieved_grade.student_id, self.test_student_id)
        self.assertEqual(retrieved_grade.subject_id, self.test_subject_id)

    def test_update_grade(self):
        """测试更新成绩记录"""
        # 添加成绩
        grade = self.grade_manager.add_grade(
            student_id=self.test_student_id,
            subject_id=self.test_subject_id,
            exam_date="2023-06-01",
            score=85.5,
            exam_type="期末考试"
        )
        
        # 更新成绩
        updated_grade = self.grade_manager.update_grade(
            grade_id=grade.grade_id,
            score=90.0,
            exam_type="补考"
        )
        
        # 验证更新是否成功
        self.assertIsNotNone(updated_grade)
        self.assertEqual(updated_grade.grade_id, grade.grade_id)
        self.assertEqual(updated_grade.score, 90.0)
        self.assertEqual(updated_grade.exam_type, "补考")

    def test_delete_grade(self):
        """测试删除成绩记录"""
        # 添加成绩
        grade = self.grade_manager.add_grade(
            student_id=self.test_student_id,
            subject_id=self.test_subject_id,
            exam_date="2023-06-01",
            score=85.5,
            exam_type="期末考试"
        )
        
        # 删除成绩
        result = self.grade_manager.delete_grade(grade.grade_id)
        
        # 验证删除是否成功
        self.assertTrue(result)
        
        # 验证成绩是否已被删除
        deleted_grade = self.grade_manager.get_grade(grade.grade_id)
        self.assertIsNone(deleted_grade)


if __name__ == "__main__":
    unittest.main()