#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅导方案生成模块的单元测试
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

from learn05.service.database import Base, Student, Subject, Grade, Class, TutoringPlan
from learn05.service.tutoring_plan import TutoringPlanGenerator

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


class TestTutoringPlanGenerator(unittest.TestCase):
    """辅导方案生成器的单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试会话
        self.db = TestingSessionLocal()
        
        # 创建测试数据
        # 添加测试班级
        test_class = Class(class_name="测试班级", grade_level=10)
        self.db.add(test_class)
        self.db.commit()
        
        # 添加测试学生
        test_student = Student(
            student_name="测试学生",
            student_number="S001",
            gender="男",
            date_of_birth="2005-01-01",
            class_id=test_class.class_id
        )
        self.db.add(test_student)
        self.db.commit()
        
        # 添加测试科目
        test_subject = Subject(subject_name="数学", credit=5)
        self.db.add(test_subject)
        self.db.commit()
        
        # 添加测试成绩
        test_grade = Grade(
            student_id=test_student.student_id,
            subject_id=test_subject.subject_id,
            exam_date="2023-06-01",
            score=75.0,
            exam_type="期末考试"
        )
        self.db.add(test_grade)
        self.db.commit()
        
        # 保存测试数据ID
        self.test_class_id = test_class.class_id
        self.test_student_id = test_student.student_id
        self.test_subject_id = test_subject.subject_id
        
        # 创建辅导方案生成器实例，使用mock的LLM客户端
        self.mock_llm_client = MagicMock()
        self.mock_llm_client.generate_text.return_value = "这是一个测试辅导方案，针对数学科目的学习提升。"
        
        # 使用patch装饰器模拟GradeAnalyzer
        self.grade_analyzer_patch = patch('learn05.service.tutoring_plan.GradeAnalyzer')
        self.mock_grade_analyzer = self.grade_analyzer_patch.start()
        
        # 配置mock的GradeAnalyzer
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.analyze_student_grades.return_value = {
            "has_data": True,
            "average_score": 75.0,
            "highest_score": 85.0,
            "lowest_score": 65.0,
            "weak_points": ["函数", "三角形"],
            "strong_points": ["方程", "数列"]
        }
        mock_analyzer_instance.get_progress_analysis.return_value = {
            "trend": "上升",
            "improvement": 5.0,
            "recent_exams": ["期中考试", "期末考试"]
        }
        self.mock_grade_analyzer.return_value = mock_analyzer_instance
        
        # 创建辅导方案生成器实例
        self.plan_generator = TutoringPlanGenerator(self.db, self.mock_llm_client)

    def tearDown(self):
        """测试后的清理工作"""
        # 停止所有patch
        self.grade_analyzer_patch.stop()
        
        # 清理测试数据
        self.db.query(TutoringPlan).delete()
        self.db.query(Grade).delete()
        self.db.query(Student).delete()
        self.db.query(Subject).delete()
        self.db.query(Class).delete()
        self.db.commit()
        
        # 关闭会话
        self.db.close()

    @patch('learn05.service.tutoring_plan.get_llm_client')
    def test_generate_tutoring_plan(self, mock_get_llm_client):
        """测试生成辅导方案"""
        # 配置mock
        mock_get_llm_client.return_value = self.mock_llm_client
        
        # 生成辅导方案
        plan = self.plan_generator.generate_tutoring_plan(
            student_id=self.test_student_id,
            subject_id=self.test_subject_id,
            duration_days=30,
            plan_type="comprehensive"
        )
        
        # 验证辅导方案是否生成成功
        self.assertIsNotNone(plan)
        self.assertEqual(plan.student_id, self.test_student_id)
        self.assertIn("测试辅导方案", plan.plan_content)

    @patch('learn05.service.tutoring_plan.get_llm_client')
    def test_generate_tutoring_plan_without_subject(self, mock_get_llm_client):
        """测试生成全科辅导方案"""
        # 配置mock
        mock_get_llm_client.return_value = self.mock_llm_client
        
        # 生成辅导方案（不指定科目）
        plan = self.plan_generator.generate_tutoring_plan(
            student_id=self.test_student_id,
            duration_days=30,
            plan_type="comprehensive"
        )
        
        # 验证辅导方案是否生成成功
        self.assertIsNotNone(plan)
        self.assertEqual(plan.student_id, self.test_student_id)
        self.assertIn("测试辅导方案", plan.plan_content)

    def test_generate_tutoring_plan_llm_failure(self):
        """测试大模型调用失败时的备用方案生成"""
        # 创建一个会抛出异常的mock llm_client
        mock_llm_client = MagicMock()
        mock_llm_client.generate_text.side_effect = Exception("LLM API调用失败")
        
        # 创建一个新的TutoringPlanGenerator实例，使用会失败的llm_client
        failing_plan_generator = TutoringPlanGenerator(db=self.db, llm_client=mock_llm_client)
        
        # 模拟备用方案生成方法
        with patch.object(failing_plan_generator, '_generate_fallback_plan') as mock_fallback:
            mock_fallback.return_value = "这是一个备用辅导方案。"
            
            # 生成辅导方案
            plan = failing_plan_generator.generate_tutoring_plan(
                student_id=self.test_student_id,
                subject_id=self.test_subject_id
            )
            
            # 验证是否调用了备用方案生成方法
            mock_fallback.assert_called_once()
            
            # 验证辅导方案是否生成成功
            self.assertIsNotNone(plan)
            self.assertEqual(plan.plan_content, "这是一个备用辅导方案。")


if __name__ == "__main__":
    unittest.main()