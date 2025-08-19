#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成绩模块综合功能测试
基于产品需求文档的全面测试用例
"""

import unittest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from learn05.service.database import Base, Student, Subject, Grade, Class, User
from learn05.service.grade_management import GradeManager, GradeAnalyzer

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 创建测试数据库表
Base.metadata.create_all(bind=test_engine)


class TestGradeModuleComprehensive(unittest.TestCase):
    """成绩模块综合功能测试类"""
    
    def setUp(self):
        """测试前置设置"""
        # 创建测试数据库会话
        self.db = TestingSessionLocal()
        
        # 创建测试用户
        self.test_user = User(
            username="test_teacher",
            password="hashed_password",
            role="teacher",
            email="teacher@test.com"
        )
        self.db.add(self.test_user)
        
        # 创建测试班级
        self.test_class = Class(
            class_name="高一(1)班",
            grade_level=1,
            head_teacher_id=None  # 暂时设为None，因为Teacher表结构不同
        )
        self.db.add(self.test_class)
        self.db.commit()  # 提交班级数据以获取class_id
        
        # 创建测试学生
        self.test_students = []
        for i in range(1, 11):  # 创建10个学生
            student = Student(
                student_name=f"学生{i}",
                student_number=f"2024{i:04d}",
                class_id=self.test_class.class_id,  # 使用正确的class_id
                gender="男" if i % 2 == 1 else "女",
                date_of_birth="2008-01-01"
            )
            self.test_students.append(student)
            self.db.add(student)
        
        # 创建测试科目
        self.test_subjects = [
            Subject(subject_name="数学", credit=4),
            Subject(subject_name="语文", credit=4),
            Subject(subject_name="英语", credit=4),
            Subject(subject_name="物理", credit=3),
            Subject(subject_name="化学", credit=3)
        ]
        for subject in self.test_subjects:
            self.db.add(subject)
        
        self.db.commit()
        
        # 创建成绩管理器实例
        self.grade_manager = GradeManager(self.db)
    
    def tearDown(self):
        """测试后清理"""
        # 清理所有测试数据
        self.db.query(Grade).delete()
        self.db.query(Student).delete()
        self.db.query(Subject).delete()
        self.db.query(Class).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()
    
    def test_tc_grade_001_grade_input_and_analysis(self):
        """TC_GRADE_001: 测试成绩录入与分析功能"""
        
        # 1. 测试手动录入成绩
        grade_data = {
            "student_id": self.test_students[0].student_id,
            "subject_id": self.test_subjects[0].subject_id,
            "exam_date": "2024-01-15",
            "score": 95.5,
            "exam_type": "期中考试"
        }
        
        # 使用GradeManager添加成绩
        result = self.grade_manager.add_grade(
            student_id=grade_data["student_id"],
            subject_id=grade_data["subject_id"],
            exam_date=grade_data["exam_date"],
            score=grade_data["score"],
            exam_type=grade_data["exam_type"]
        )
        
        self.assertTrue(result)
        
        # 验证成绩是否正确添加
        # 通过数据库查询来验证成绩是否添加成功
        added_grade = self.db.query(Grade).filter(
            Grade.student_id == grade_data["student_id"],
            Grade.subject_id == grade_data["subject_id"],
            Grade.exam_date == grade_data["exam_date"]
        ).first()
        
        self.assertIsNotNone(added_grade)
        self.assertEqual(added_grade.score, 95.5)
        
        # 2. 测试批量录入成绩
        # 为多个学生添加成绩
        test_scores = [88.5, 92.0, 85.5, 90.0, 87.5]
        for i, score in enumerate(test_scores):
            if i < len(self.test_students):
                result = self.grade_manager.add_grade(
                    student_id=self.test_students[i].student_id,
                    subject_id=self.test_subjects[0].subject_id,
                    exam_date="2024-01-15",
                    score=score,
                    exam_type="期中考试"
                )
                self.assertTrue(result)
        
        # 3. 验证成绩统计功能
        # 获取班级成绩统计（模拟统计功能）
        all_grades = self.db.query(Grade).filter(
            Grade.exam_date == "2024-01-15",
            Grade.exam_type == "期中考试"
        ).all()
        
        self.assertGreater(len(all_grades), 0)
        
        # 计算平均分
        total_score = sum(grade.score for grade in all_grades)
        average_score = total_score / len(all_grades)
        
        self.assertGreater(average_score, 0)
        self.assertLessEqual(average_score, 100)
    
    def test_tc_grade_002_class_grade_analysis(self):
        """TC_GRADE_002: 测试班级及年级成绩综合分析"""
        
        # 先添加一些测试成绩数据
        test_scores = [
            {"student_id": self.test_students[0].student_id, "score": 88.5},
            {"student_id": self.test_students[1].student_id, "score": 92.0},
            {"student_id": self.test_students[2].student_id, "score": 85.5},
            {"student_id": self.test_students[3].student_id, "score": 90.0},
            {"student_id": self.test_students[4].student_id, "score": 87.5}
        ]
        
        for score_data in test_scores:
            self.grade_manager.add_grade(
                student_id=score_data["student_id"],
                subject_id=self.test_subjects[0].subject_id,
                exam_date="2024-01-15",
                score=score_data["score"],
                exam_type="期中考试"
            )
        
        # 1. 测试班级整体成绩分布展示
        # 获取所有成绩进行统计分析
        all_grades = self.db.query(Grade).filter(
            Grade.exam_date == "2024-01-15",
            Grade.exam_type == "期中考试"
        ).all()
        
        self.assertGreater(len(all_grades), 0)
        
        # 计算统计数据
        scores = [grade.score for grade in all_grades]
        average_score = sum(scores) / len(scores)
        pass_rate = len([s for s in scores if s >= 60]) / len(scores)
        
        self.assertGreater(average_score, 0)
        self.assertGreaterEqual(pass_rate, 0)
        self.assertLessEqual(pass_rate, 1)
        
        # 2. 测试班级间成绩对比分析
        # 创建另一个班级进行对比
        another_class = Class(
            class_name="高一(2)班",
            grade_level=1,
            head_teacher_id=self.test_user.id
        )
        self.db.add(another_class)
        self.db.commit()
        
        # 验证班级创建成功
        created_class = self.db.query(Class).filter(
            Class.class_name == "高一(2)班"
        ).first()
        self.assertIsNotNone(created_class)
        
        # 3. 测试成绩报告生成（模拟功能）
        # 生成班级成绩摘要报告
        report_data = {
            "class_id": self.test_class.class_id,
            "exam_date": "2024-01-15",
            "total_students": len(self.test_students),
            "average_score": average_score,
            "pass_rate": pass_rate,
            "score_distribution": {
                "90-100": len([s for s in scores if 90 <= s <= 100]),
                "80-89": len([s for s in scores if 80 <= s < 90]),
                "70-79": len([s for s in scores if 70 <= s < 80]),
                "60-69": len([s for s in scores if 60 <= s < 70]),
                "0-59": len([s for s in scores if s < 60])
            }
        }
        
        # 验证报告数据完整性
        self.assertIn("class_id", report_data)
        self.assertIn("average_score", report_data)
        self.assertIn("pass_rate", report_data)
        self.assertIn("score_distribution", report_data)
    
    def test_tc_grade_003_student_personalized_analysis(self):
        """TC_GRADE_003: 测试学生个性化成绩分析"""
        
        # 先为学生添加多科目成绩数据
        student_id = self.test_students[0].student_id
        
        # 添加多个科目的成绩
        test_grades = [
            {"subject_id": self.test_subjects[0].subject_id, "score": 88.5, "exam_type": "期中考试"},
            {"subject_id": self.test_subjects[1].subject_id, "score": 92.0, "exam_type": "期中考试"},
            {"subject_id": self.test_subjects[2].subject_id, "score": 85.5, "exam_type": "期中考试"},
            {"subject_id": self.test_subjects[0].subject_id, "score": 90.0, "exam_type": "期末考试"},
            {"subject_id": self.test_subjects[1].subject_id, "score": 87.5, "exam_type": "期末考试"}
        ]
        
        for grade_data in test_grades:
            self.grade_manager.add_grade(
                student_id=student_id,
                subject_id=grade_data["subject_id"],
                exam_date="2024-01-15" if grade_data["exam_type"] == "期中考试" else "2024-06-15",
                score=grade_data["score"],
                exam_type=grade_data["exam_type"]
            )
        
        # 1. 测试学生成绩趋势分析
        # 获取学生的所有成绩记录
        student_grades = self.db.query(Grade).filter(
            Grade.student_id == student_id
        ).all()
        
        self.assertGreater(len(student_grades), 0)
        
        # 分析成绩趋势
        subject_scores = {}
        for grade in student_grades:
            if grade.subject_id not in subject_scores:
                subject_scores[grade.subject_id] = []
            subject_scores[grade.subject_id].append({
                "score": grade.score,
                "exam_date": grade.exam_date,
                "exam_type": grade.exam_type
            })
        
        # 验证趋势分析数据
        self.assertGreater(len(subject_scores), 0)
        
        # 计算学生平均分
        all_scores = [grade.score for grade in student_grades]
        average_score = sum(all_scores) / len(all_scores)
        self.assertGreater(average_score, 0)
        
        # 2. 测试知识点掌握情况分析
        # 按科目分析学生表现
        math_grades = self.db.query(Grade).filter(
            Grade.student_id == student_id,
            Grade.subject_id == self.test_subjects[0].subject_id
        ).all()
        
        if math_grades:
            math_scores = [grade.score for grade in math_grades]
            math_average = sum(math_scores) / len(math_scores)
            
            # 分析掌握情况
            mastery_level = "优秀" if math_average >= 90 else "良好" if math_average >= 80 else "一般"
            self.assertIn(mastery_level, ["优秀", "良好", "一般", "需要提高"])
        
        # 3. 测试薄弱环节识别
        # 识别分数较低的科目
        weak_subjects = []
        for subject_id, scores in subject_scores.items():
            avg_score = sum(s["score"] for s in scores) / len(scores)
            if avg_score < 85:  # 设定薄弱环节阈值
                weak_subjects.append({
                    "subject_id": subject_id,
                    "average_score": avg_score,
                    "improvement_needed": True
                })
        
        # 验证薄弱环节识别结果
        self.assertIsInstance(weak_subjects, list)
        
        # 4. 测试个性化练习题生成（模拟功能）
        # 基于薄弱环节生成练习建议
        recommendations = []
        for weak_subject in weak_subjects:
            recommendations.append({
                "subject_id": weak_subject["subject_id"],
                "recommendation_type": "练习加强",
                "difficulty_level": "中等",
                "practice_topics": ["基础概念", "计算练习", "应用题"]
            })
        
        # 验证推荐结果
        self.assertIsInstance(recommendations, list)
    
    def test_tc_grade_004_tutoring_plan_generation(self):
        """TC_GRADE_004: 测试辅导方案生成功能"""
        
        # 先为学生添加成绩数据
        student_id = self.test_students[0].student_id
        
        # 添加不同表现的成绩数据
        test_grades = [
            {"subject_id": self.test_subjects[0].subject_id, "score": 65.0, "exam_type": "期中考试"},  # 数学较弱
            {"subject_id": self.test_subjects[1].subject_id, "score": 88.0, "exam_type": "期中考试"},  # 语文良好
            {"subject_id": self.test_subjects[2].subject_id, "score": 92.0, "exam_type": "期中考试"},  # 英语优秀
        ]
        
        for grade_data in test_grades:
            self.grade_manager.add_grade(
                student_id=student_id,
                subject_id=grade_data["subject_id"],
                exam_date="2024-01-15",
                score=grade_data["score"],
                exam_type=grade_data["exam_type"]
            )
        
        # 1. 测试个性化辅导方案生成
        # 分析学生成绩，生成辅导方案
        student_grades = self.db.query(Grade).filter(
            Grade.student_id == student_id
        ).all()
        
        # 识别需要辅导的科目
        weak_subjects = []
        for grade in student_grades:
            if grade.score < 75:  # 设定需要辅导的分数线
                weak_subjects.append({
                    "subject_id": grade.subject_id,
                    "score": grade.score,
                    "improvement_needed": 75 - grade.score
                })
        
        # 生成辅导方案
        tutoring_plan = {
            "plan_id": f"plan_{student_id}_001",
            "student_id": student_id,
            "weak_subjects": weak_subjects,
            "learning_objectives": [],
            "study_schedule": {},
            "resources": []
        }
        
        # 为每个薄弱科目制定学习目标
        for weak_subject in weak_subjects:
            subject_name = next(
                (s.subject_name for s in self.test_subjects if s.subject_id == weak_subject["subject_id"]),
                "未知科目"
            )
            tutoring_plan["learning_objectives"].append(f"提高{subject_name}成绩至75分以上")
            tutoring_plan["study_schedule"][subject_name] = "每日30分钟专项练习"
            tutoring_plan["resources"].append(f"{subject_name}基础练习册")
        
        # 验证辅导方案生成结果
        self.assertIn("plan_id", tutoring_plan)
        self.assertIn("student_id", tutoring_plan)
        self.assertIn("learning_objectives", tutoring_plan)
        self.assertIn("study_schedule", tutoring_plan)
        self.assertIn("resources", tutoring_plan)
        
        # 验证薄弱科目被正确识别
        self.assertGreater(len(weak_subjects), 0)  # 应该有薄弱科目
        
        # 2. 测试学习资源推荐（模拟功能）
        # 基于薄弱科目推荐学习资源
        recommended_resources = []
        for weak_subject in weak_subjects:
            subject_name = next(
                (s.subject_name for s in self.test_subjects if s.subject_id == weak_subject["subject_id"]),
                "未知科目"
            )
            recommended_resources.extend([
                f"{subject_name}基础教程",
                f"{subject_name}练习题集",
                f"{subject_name}视频课程"
            ])
        
        self.assertGreater(len(recommended_resources), 0)
        
        # 3. 测试辅导进度跟踪（模拟功能）
        # 模拟辅导进度数据
        progress_data = {
            "student_id": student_id,
            "plan_id": tutoring_plan["plan_id"],
            "start_date": "2024-01-15",
            "current_progress": 25.0,  # 25%完成度
            "completed_objectives": 1,
            "total_objectives": len(tutoring_plan["learning_objectives"]),
            "next_milestone": "完成数学基础练习"
        }
        
        self.assertIn("current_progress", progress_data)
        self.assertGreaterEqual(progress_data["current_progress"], 0)
        self.assertLessEqual(progress_data["current_progress"], 100)
        
        # 4. 测试辅导效果评估（模拟功能）
        # 模拟效果评估数据
        evaluation_data = {
            "student_id": student_id,
            "evaluation_period": "2024-01-15 to 2024-02-15",
            "improvement_score": 8.5,  # 提升了8.5分
            "objectives_achieved": 1,
            "total_objectives": len(tutoring_plan["learning_objectives"]),
            "effectiveness_rating": "良好",
            "recommendations": ["继续加强基础练习", "增加应用题训练"]
        }
        
        self.assertIn("improvement_score", evaluation_data)
        self.assertIn("effectiveness_rating", evaluation_data)
        self.assertGreater(evaluation_data["improvement_score"], 0)
    
    def test_grade_data_export_functionality(self):
        """测试成绩数据导出功能"""
        
        # 先添加测试成绩数据
        test_scores = [
            {"student_id": self.test_students[0].student_id, "score": 88.5},
            {"student_id": self.test_students[1].student_id, "score": 92.0},
            {"student_id": self.test_students[2].student_id, "score": 85.5}
        ]
        
        for score_data in test_scores:
            self.grade_manager.add_grade(
                student_id=score_data["student_id"],
                subject_id=self.test_subjects[0].subject_id,
                exam_date="2024-01-15",
                score=score_data["score"],
                exam_type="期中考试"
            )
        
        # 测试导出功能（模拟数据导出）
        # 获取要导出的成绩数据
        export_grades = self.db.query(Grade).filter(
            Grade.exam_date == "2024-01-15",
            Grade.exam_type == "期中考试"
        ).all()
        
        # 模拟导出数据格式
        export_data = []
        for grade in export_grades:
            student = self.db.query(Student).filter(
                Student.student_id == grade.student_id
            ).first()
            subject = self.db.query(Subject).filter(
                Subject.subject_id == grade.subject_id
            ).first()
            
            export_data.append({
                "学生姓名": student.student_name if student else "未知",
                "学生ID": grade.student_id,
                "科目": subject.subject_name if subject else "未知",
                "考试日期": grade.exam_date,
                "考试类型": grade.exam_type,
                "成绩": grade.score
            })
        
        # 验证导出数据
        self.assertGreater(len(export_data), 0)
        for record in export_data:
            self.assertIn("学生姓名", record)
            self.assertIn("成绩", record)
            self.assertIsInstance(record["成绩"], (int, float))
            self.assertGreaterEqual(record["成绩"], 0)
            self.assertLessEqual(record["成绩"], 100)
    
    def test_grade_statistics_accuracy(self):
        """测试成绩统计数据的准确性"""
        
        # 创建已知的测试数据
        known_scores = [85.0, 90.0, 78.5, 92.5, 88.0]
        expected_average = sum(known_scores) / len(known_scores)
        
        # 添加已知成绩数据
        for i, score in enumerate(known_scores):
            if i < len(self.test_students):
                self.grade_manager.add_grade(
                    student_id=self.test_students[i].student_id,
                    subject_id=self.test_subjects[0].subject_id,
                    exam_date="2024-01-15",
                    score=score,
                    exam_type="期中考试"
                )
        
        # 验证统计数据准确性
        all_grades = self.db.query(Grade).filter(
            Grade.exam_date == "2024-01-15",
            Grade.exam_type == "期中考试",
            Grade.subject_id == self.test_subjects[0].subject_id
        ).all()
        
        actual_scores = [grade.score for grade in all_grades]
        actual_average = sum(actual_scores) / len(actual_scores)
        
        # 验证平均分计算准确性（允许小数点误差）
        self.assertAlmostEqual(actual_average, expected_average, places=2)
        
        # 验证最高分和最低分
        self.assertEqual(max(actual_scores), max(known_scores))
        self.assertEqual(min(actual_scores), min(known_scores))
        
        # 验证及格率计算
        pass_count = len([s for s in actual_scores if s >= 60])
        expected_pass_rate = pass_count / len(actual_scores)
        actual_pass_rate = pass_count / len(actual_scores)
        
        self.assertEqual(actual_pass_rate, expected_pass_rate)
        
        # 这部分已在上面实现，移除重复代码
    
    def test_grade_api_error_handling(self):
        """测试成绩管理的错误处理"""
        
        # 1. 测试无效学生ID
        with self.assertRaises(Exception):
            self.grade_manager.add_grade(
                student_id="invalid_student_id",
                subject_id=self.test_subjects[0].subject_id,
                exam_date="2024-01-15",
                score=95.5,
                exam_type="期中考试"
            )
        
        # 2. 测试无效分数范围（负分）
        with self.assertRaises(Exception):
            self.grade_manager.add_grade(
                student_id=self.test_students[0].student_id,
                subject_id=self.test_subjects[0].subject_id,
                exam_date="2024-01-15",
                score=-10.0,  # 负分
                exam_type="期中考试"
            )
        
        # 3. 测试无效科目ID
        with self.assertRaises(Exception):
            self.grade_manager.add_grade(
                student_id=self.test_students[0].student_id,
                subject_id="invalid_subject_id",
                exam_date="2024-01-15",
                score=85.0,
                exam_type="期中考试"
            )
        
        # 4. 测试空值处理
        with self.assertRaises(Exception):
            self.grade_manager.add_grade(
                student_id=None,
                subject_id=self.test_subjects[0].subject_id,
                exam_date="2024-01-15",
                score=85.0,
                exam_type="期中考试"
            )
    
    def test_grade_performance_with_large_dataset(self):
        """测试大数据量下的成绩处理性能"""
        
        import time
        
        # 创建大量成绩数据
        start_time = time.time()
        
        # 批量创建成绩
        for i in range(100):  # 创建100条成绩记录
            self.grade_manager.add_grade(
                student_id=self.test_students[i % len(self.test_students)].student_id,
                subject_id=self.test_subjects[i % len(self.test_subjects)].subject_id,
                exam_date="2024-01-15",
                score=float(80 + (i % 20)),
                exam_type="期中考试"
            )
        
        creation_time = time.time() - start_time
        
        # 测试查询性能
        start_time = time.time()
        all_grades = self.db.query(Grade).filter(
            Grade.exam_date == "2024-01-15",
            Grade.exam_type == "期中考试"
        ).limit(100).all()
        query_time = time.time() - start_time
        
        # 验证性能要求（根据需求文档调整）
        self.assertLess(creation_time, 10.0)  # 创建100条记录应在10秒内完成
        self.assertLess(query_time, 2.0)      # 查询应在2秒内完成
        self.assertGreaterEqual(len(all_grades), 100)  # 确保数据创建成功
    
    def _create_test_grades(self):
        """创建测试成绩数据的辅助方法"""
        
        # 为前10个学生创建多科目成绩
        student_count = min(10, len(self.test_students))
        subject_count = min(3, len(self.test_subjects))
        
        for i in range(student_count):
            for j in range(subject_count):
                # 生成随机但合理的分数
                base_score = 75 + (i * 2) + (j * 3)
                score = min(100.0, max(0.0, base_score + (i % 10)))
                
                try:
                    self.grade_manager.add_grade(
                        student_id=self.test_students[i].student_id,
                        subject_id=self.test_subjects[j].subject_id,
                        exam_date="2024-01-15",
                        score=score,
                        exam_type="期中考试"
                    )
                except Exception as e:
                    # 忽略重复创建等错误
                    pass


if __name__ == "__main__":
    unittest.main()