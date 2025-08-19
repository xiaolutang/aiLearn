# -*- coding: utf-8 -*-
"""
数据库管理单元测试
测试数据库管理器和相关功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sqlite3
import tempfile
import os

# from llm.database.database_manager import MockDatabaseManager
# from llm.database.models import (
#     Student,
#     Grade,
#     Subject,
#     TeachingMaterial,
#     LearningRecord
# )
# from llm.database_utils import (
#     create_connection,
#     execute_query,
#     fetch_results,
#     validate_sql_query
# )
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from test_config import (
    TEST_CONFIG,
    MOCK_STUDENT_DATA,
    MOCK_GRADE_DATA
)

class MockDatabaseManager:
    """Mock数据库管理器"""
    def __init__(self, *args, **kwargs):
        pass
    
    def execute_query(self, query, params=None):
        return []
    
    def get_table_schema(self, table_name):
        return {}
    
    def get_all_tables(self):
        return []


class TestMockDatabaseManager:
    """测试数据库管理器类"""
    
    def setup_method(self):
        """测试前的设置"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db_manager = MockDatabaseManager(
            db_path=self.temp_db.name,
            auto_create_tables=True
        )
    
    def teardown_method(self):
        """测试后的清理"""
        # 关闭数据库连接
        if hasattr(self.db_manager, 'connection') and self.db_manager.connection:
            self.db_manager.connection.close()
        
        # 删除临时数据库文件
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_manager_initialization(self):
        """测试数据库管理器初始化"""
        assert self.db_manager.db_path == self.temp_db.name
        assert self.db_manager.auto_create_tables is True
        assert self.db_manager.connection is not None
        assert isinstance(self.db_manager.connection, sqlite3.Connection)
    
    def test_create_tables(self):
        """测试创建数据表"""
        # 检查表是否被创建
        cursor = self.db_manager.connection.cursor()
        
        # 检查students表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        assert cursor.fetchone() is not None
        
        # 检查grades表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grades'")
        assert cursor.fetchone() is not None
        
        # 检查subjects表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subjects'")
        assert cursor.fetchone() is not None
        
        # 检查teaching_materials表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teaching_materials'")
        assert cursor.fetchone() is not None
        
        # 检查learning_records表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='learning_records'")
        assert cursor.fetchone() is not None
    
    def test_insert_student(self):
        """测试插入学生数据"""
        student_data = {
            "student_id": "S001",
            "name": "张三",
            "class_name": "高一(1)班",
            "grade": "高一",
            "age": 16,
            "gender": "男"
        }
        
        # 插入学生数据
        result = self.db_manager.insert_student(student_data)
        assert result is True
        
        # 验证数据是否插入成功
        student = self.db_manager.get_student_by_id("S001")
        assert student is not None
        assert student["name"] == "张三"
        assert student["class_name"] == "高一(1)班"
        assert student["grade"] == "高一"
    
    def test_insert_duplicate_student(self):
        """测试插入重复学生数据"""
        student_data = {
            "student_id": "S002",
            "name": "李四",
            "class_name": "高一(2)班",
            "grade": "高一"
        }
        
        # 第一次插入
        result1 = self.db_manager.insert_student(student_data)
        assert result1 is True
        
        # 第二次插入相同ID的学生
        result2 = self.db_manager.insert_student(student_data)
        assert result2 is False  # 应该失败
    
    def test_get_student_by_id(self):
        """测试根据ID获取学生"""
        # 先插入学生数据
        student_data = {
            "student_id": "S003",
            "name": "王五",
            "class_name": "高一(3)班",
            "grade": "高一"
        }
        self.db_manager.insert_student(student_data)
        
        # 获取学生数据
        student = self.db_manager.get_student_by_id("S003")
        assert student is not None
        assert student["student_id"] == "S003"
        assert student["name"] == "王五"
        
        # 获取不存在的学生
        nonexistent_student = self.db_manager.get_student_by_id("S999")
        assert nonexistent_student is None
    
    def test_get_students_by_class(self):
        """测试根据班级获取学生列表"""
        # 插入多个学生数据
        students_data = [
            {"student_id": "S004", "name": "学生A", "class_name": "高一(1)班", "grade": "高一"},
            {"student_id": "S005", "name": "学生B", "class_name": "高一(1)班", "grade": "高一"},
            {"student_id": "S006", "name": "学生C", "class_name": "高一(2)班", "grade": "高一"}
        ]
        
        for student_data in students_data:
            self.db_manager.insert_student(student_data)
        
        # 获取高一(1)班的学生
        class_students = self.db_manager.get_students_by_class("高一(1)班")
        assert len(class_students) == 2
        assert all(student["class_name"] == "高一(1)班" for student in class_students)
        
        # 获取不存在班级的学生
        empty_class = self.db_manager.get_students_by_class("不存在的班级")
        assert len(empty_class) == 0
    
    def test_insert_grade(self):
        """测试插入成绩数据"""
        # 先插入学生和科目数据
        student_data = {"student_id": "S007", "name": "测试学生", "class_name": "高一(1)班", "grade": "高一"}
        subject_data = {"subject_id": "MATH001", "subject_name": "数学", "grade": "高一"}
        
        self.db_manager.insert_student(student_data)
        self.db_manager.insert_subject(subject_data)
        
        # 插入成绩数据
        grade_data = {
            "grade_id": "G001",
            "student_id": "S007",
            "subject_id": "MATH001",
            "score": 85.5,
            "exam_type": "期中考试",
            "exam_date": "2024-01-15"
        }
        
        result = self.db_manager.insert_grade(grade_data)
        assert result is True
        
        # 验证成绩数据
        grade = self.db_manager.get_grade_by_id("G001")
        assert grade is not None
        assert grade["score"] == 85.5
        assert grade["exam_type"] == "期中考试"
    
    def test_get_grades_by_student(self):
        """测试获取学生的所有成绩"""
        # 准备测试数据
        student_data = {"student_id": "S008", "name": "成绩测试学生", "class_name": "高一(1)班", "grade": "高一"}
        subjects_data = [
            {"subject_id": "MATH002", "subject_name": "数学", "grade": "高一"},
            {"subject_id": "ENG002", "subject_name": "英语", "grade": "高一"}
        ]
        
        self.db_manager.insert_student(student_data)
        for subject_data in subjects_data:
            self.db_manager.insert_subject(subject_data)
        
        # 插入多个成绩
        grades_data = [
            {"grade_id": "G002", "student_id": "S008", "subject_id": "MATH002", "score": 90, "exam_type": "期中"},
            {"grade_id": "G003", "student_id": "S008", "subject_id": "ENG002", "score": 88, "exam_type": "期中"}
        ]
        
        for grade_data in grades_data:
            self.db_manager.insert_grade(grade_data)
        
        # 获取学生成绩
        student_grades = self.db_manager.get_grades_by_student("S008")
        assert len(student_grades) == 2
        assert all(grade["student_id"] == "S008" for grade in student_grades)
    
    def test_get_grades_by_subject(self):
        """测试获取科目的所有成绩"""
        # 准备测试数据
        students_data = [
            {"student_id": "S009", "name": "学生1", "class_name": "高一(1)班", "grade": "高一"},
            {"student_id": "S010", "name": "学生2", "class_name": "高一(1)班", "grade": "高一"}
        ]
        subject_data = {"subject_id": "MATH003", "subject_name": "数学", "grade": "高一"}
        
        for student_data in students_data:
            self.db_manager.insert_student(student_data)
        self.db_manager.insert_subject(subject_data)
        
        # 插入成绩数据
        grades_data = [
            {"grade_id": "G004", "student_id": "S009", "subject_id": "MATH003", "score": 92, "exam_type": "期中"},
            {"grade_id": "G005", "student_id": "S010", "subject_id": "MATH003", "score": 87, "exam_type": "期中"}
        ]
        
        for grade_data in grades_data:
            self.db_manager.insert_grade(grade_data)
        
        # 获取科目成绩
        subject_grades = self.db_manager.get_grades_by_subject("MATH003")
        assert len(subject_grades) == 2
        assert all(grade["subject_id"] == "MATH003" for grade in subject_grades)
    
    def test_update_student(self):
        """测试更新学生信息"""
        # 插入学生数据
        student_data = {"student_id": "S011", "name": "原始姓名", "class_name": "高一(1)班", "grade": "高一"}
        self.db_manager.insert_student(student_data)
        
        # 更新学生信息
        update_data = {"name": "更新姓名", "class_name": "高一(2)班"}
        result = self.db_manager.update_student("S011", update_data)
        assert result is True
        
        # 验证更新结果
        updated_student = self.db_manager.get_student_by_id("S011")
        assert updated_student["name"] == "更新姓名"
        assert updated_student["class_name"] == "高一(2)班"
        assert updated_student["grade"] == "高一"  # 未更新的字段保持不变
    
    def test_delete_student(self):
        """测试删除学生"""
        # 插入学生数据
        student_data = {"student_id": "S012", "name": "待删除学生", "class_name": "高一(1)班", "grade": "高一"}
        self.db_manager.insert_student(student_data)
        
        # 确认学生存在
        assert self.db_manager.get_student_by_id("S012") is not None
        
        # 删除学生
        result = self.db_manager.delete_student("S012")
        assert result is True
        
        # 确认学生已删除
        assert self.db_manager.get_student_by_id("S012") is None
    
    def test_execute_custom_query(self):
        """测试执行自定义查询"""
        # 插入测试数据
        students_data = [
            {"student_id": "S013", "name": "查询测试1", "class_name": "高一(1)班", "grade": "高一"},
            {"student_id": "S014", "name": "查询测试2", "class_name": "高一(1)班", "grade": "高一"},
            {"student_id": "S015", "name": "查询测试3", "class_name": "高一(2)班", "grade": "高一"}
        ]
        
        for student_data in students_data:
            self.db_manager.insert_student(student_data)
        
        # 执行自定义查询
        query = "SELECT COUNT(*) as count FROM students WHERE class_name = ?"
        params = ("高一(1)班",)
        
        result = self.db_manager.execute_query(query, params)
        assert result is not None
        assert result[0]["count"] == 2
    
    def test_get_class_statistics(self):
        """测试获取班级统计信息"""
        # 准备测试数据
        students_data = [
            {"student_id": "S016", "name": "统计学生1", "class_name": "高一(1)班", "grade": "高一"},
            {"student_id": "S017", "name": "统计学生2", "class_name": "高一(1)班", "grade": "高一"},
            {"student_id": "S018", "name": "统计学生3", "class_name": "高一(1)班", "grade": "高一"}
        ]
        
        subject_data = {"subject_id": "MATH004", "subject_name": "数学", "grade": "高一"}
        
        for student_data in students_data:
            self.db_manager.insert_student(student_data)
        self.db_manager.insert_subject(subject_data)
        
        # 插入成绩数据
        grades_data = [
            {"grade_id": "G006", "student_id": "S016", "subject_id": "MATH004", "score": 85, "exam_type": "期中"},
            {"grade_id": "G007", "student_id": "S017", "subject_id": "MATH004", "score": 90, "exam_type": "期中"},
            {"grade_id": "G008", "student_id": "S018", "subject_id": "MATH004", "score": 78, "exam_type": "期中"}
        ]
        
        for grade_data in grades_data:
            self.db_manager.insert_grade(grade_data)
        
        # 获取班级统计信息
        stats = self.db_manager.get_class_statistics("高一(1)班", "MATH004")
        
        assert stats is not None
        assert stats["student_count"] == 3
        assert stats["average_score"] == (85 + 90 + 78) / 3
        assert stats["max_score"] == 90
        assert stats["min_score"] == 78
    
    def test_backup_database(self):
        """测试数据库备份"""
        # 插入一些测试数据
        student_data = {"student_id": "S019", "name": "备份测试", "class_name": "高一(1)班", "grade": "高一"}
        self.db_manager.insert_student(student_data)
        
        # 创建备份文件路径
        backup_path = tempfile.NamedTemporaryFile(delete=False, suffix='_backup.db').name
        
        try:
            # 执行备份
            result = self.db_manager.backup_database(backup_path)
            assert result is True
            
            # 验证备份文件存在
            assert os.path.exists(backup_path)
            
            # 验证备份文件内容
            backup_manager = MockDatabaseManager(backup_path)
            backup_student = backup_manager.get_student_by_id("S019")
            assert backup_student is not None
            assert backup_student["name"] == "备份测试"
            
            backup_manager.connection.close()
            
        finally:
            # 清理备份文件
            if os.path.exists(backup_path):
                os.unlink(backup_path)
    
    def test_database_connection_error_handling(self):
        """测试数据库连接错误处理"""
        # 尝试连接到无效路径
        invalid_path = "/invalid/path/database.db"
        
        with pytest.raises(Exception):
            MockDatabaseManager(invalid_path)
    
    def test_transaction_rollback(self):
        """测试事务回滚"""
        # 开始事务
        self.db_manager.begin_transaction()
        
        try:
            # 插入学生数据
            student_data = {"student_id": "S020", "name": "事务测试", "class_name": "高一(1)班", "grade": "高一"}
            self.db_manager.insert_student(student_data)
            
            # 确认数据在事务中存在
            student = self.db_manager.get_student_by_id("S020")
            assert student is not None
            
            # 回滚事务
            self.db_manager.rollback_transaction()
            
            # 确认数据已回滚
            student = self.db_manager.get_student_by_id("S020")
            assert student is None
            
        except Exception:
            self.db_manager.rollback_transaction()
            raise
    
    def test_transaction_commit(self):
        """测试事务提交"""
        # 开始事务
        self.db_manager.begin_transaction()
        
        try:
            # 插入学生数据
            student_data = {"student_id": "S021", "name": "提交测试", "class_name": "高一(1)班", "grade": "高一"}
            self.db_manager.insert_student(student_data)
            
            # 提交事务
            self.db_manager.commit_transaction()
            
            # 确认数据已提交
            student = self.db_manager.get_student_by_id("S021")
            assert student is not None
            assert student["name"] == "提交测试"
            
        except Exception:
            self.db_manager.rollback_transaction()
            raise


class TestDatabaseUtils:
    """测试数据库工具函数"""
    
    def setup_method(self):
        """测试前的设置"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
    
    def teardown_method(self):
        """测试后的清理"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_create_connection(self):
        """测试创建数据库连接"""
        connection = create_connection(self.temp_db.name)
        
        assert connection is not None
        assert isinstance(connection, sqlite3.Connection)
        
        connection.close()
    
    def test_create_connection_invalid_path(self):
        """测试无效路径的连接创建"""
        invalid_path = "/invalid/path/test.db"
        
        with pytest.raises(Exception):
            create_connection(invalid_path)
    
    def test_execute_query_select(self):
        """测试执行SELECT查询"""
        connection = create_connection(self.temp_db.name)
        
        # 创建测试表
        connection.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER
            )
        """)
        
        # 插入测试数据
        connection.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("测试1", 100))
        connection.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("测试2", 200))
        connection.commit()
        
        # 执行查询
        result = execute_query(connection, "SELECT * FROM test_table WHERE value > ?", (150,))
        
        assert result is not None
        assert len(result) == 1
        assert result[0]["name"] == "测试2"
        assert result[0]["value"] == 200
        
        connection.close()
    
    def test_execute_query_insert(self):
        """测试执行INSERT查询"""
        connection = create_connection(self.temp_db.name)
        
        # 创建测试表
        connection.execute("""
            CREATE TABLE test_insert (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # 执行插入
        result = execute_query(
            connection, 
            "INSERT INTO test_insert (name) VALUES (?)", 
            ("插入测试",),
            fetch_results=False
        )
        
        assert result is True
        
        # 验证插入结果
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM test_insert WHERE name = ?", ("插入测试",))
        row = cursor.fetchone()
        assert row is not None
        
        connection.close()
    
    def test_fetch_results(self):
        """测试获取查询结果"""
        connection = create_connection(self.temp_db.name)
        
        # 创建测试表和数据
        connection.execute("""
            CREATE TABLE test_fetch (
                id INTEGER PRIMARY KEY,
                name TEXT,
                score REAL
            )
        """)
        
        test_data = [
            ("学生A", 85.5),
            ("学生B", 92.0),
            ("学生C", 78.5)
        ]
        
        for name, score in test_data:
            connection.execute("INSERT INTO test_fetch (name, score) VALUES (?, ?)", (name, score))
        connection.commit()
        
        # 执行查询并获取结果
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM test_fetch ORDER BY score DESC")
        
        results = fetch_results(cursor)
        
        assert len(results) == 3
        assert results[0]["name"] == "学生B"
        assert results[0]["score"] == 92.0
        assert results[1]["name"] == "学生A"
        assert results[2]["name"] == "学生C"
        
        connection.close()
    
    def test_validate_sql_query_valid(self):
        """测试有效SQL查询验证"""
        valid_queries = [
            "SELECT * FROM students",
            "SELECT name, score FROM grades WHERE score > 80",
            "SELECT COUNT(*) FROM students WHERE class_name = '高一(1)班'",
            "SELECT AVG(score) as avg_score FROM grades GROUP BY subject_id"
        ]
        
        for query in valid_queries:
            assert validate_sql_query(query) is True
    
    def test_validate_sql_query_invalid(self):
        """测试无效SQL查询验证"""
        invalid_queries = [
            "DROP TABLE students",  # 危险操作
            "DELETE FROM grades",   # 危险操作
            "UPDATE students SET name = 'hacked'",  # 危险操作
            "INSERT INTO students VALUES (1, 'test')",  # 修改操作
            "CREATE TABLE new_table (id INT)",  # 创建操作
            "ALTER TABLE students ADD COLUMN new_col TEXT",  # 修改结构
            "SELECT * FROM students; DROP TABLE grades;",  # SQL注入
            "",  # 空查询
            "INVALID SQL SYNTAX"  # 语法错误
        ]
        
        for query in invalid_queries:
            assert validate_sql_query(query) is False
    
    def test_validate_sql_query_with_whitelist(self):
        """测试带白名单的SQL查询验证"""
        allowed_tables = ["students", "grades", "subjects"]
        
        # 允许的查询
        valid_query = "SELECT * FROM students JOIN grades ON students.student_id = grades.student_id"
        assert validate_sql_query(valid_query, allowed_tables=allowed_tables) is True
        
        # 不允许的表
        invalid_query = "SELECT * FROM unauthorized_table"
        assert validate_sql_query(invalid_query, allowed_tables=allowed_tables) is False
    
    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        malicious_queries = [
            "SELECT * FROM students WHERE name = 'test'; DROP TABLE students; --",
            "SELECT * FROM students WHERE id = 1 OR 1=1",
            "SELECT * FROM students WHERE name = 'test' UNION SELECT * FROM admin_users",
            "SELECT * FROM students WHERE name = 'test'/**/OR/**/1=1",
            "SELECT * FROM students WHERE name = 'test' AND (SELECT COUNT(*) FROM admin_users) > 0"
        ]
        
        for query in malicious_queries:
            assert validate_sql_query(query) is False


class TestDatabaseModels:
    """测试数据库模型"""
    
    def test_student_model(self):
        """测试学生模型"""
        student = Student(
            student_id="S001",
            name="张三",
            class_name="高一(1)班",
            grade="高一",
            age=16,
            gender="男"
        )
        
        assert student.student_id == "S001"
        assert student.name == "张三"
        assert student.class_name == "高一(1)班"
        assert student.grade == "高一"
        assert student.age == 16
        assert student.gender == "男"
    
    def test_grade_model(self):
        """测试成绩模型"""
        grade = Grade(
            grade_id="G001",
            student_id="S001",
            subject_id="MATH001",
            score=85.5,
            exam_type="期中考试",
            exam_date="2024-01-15"
        )
        
        assert grade.grade_id == "G001"
        assert grade.student_id == "S001"
        assert grade.subject_id == "MATH001"
        assert grade.score == 85.5
        assert grade.exam_type == "期中考试"
        assert grade.exam_date == "2024-01-15"
    
    def test_subject_model(self):
        """测试科目模型"""
        subject = Subject(
            subject_id="MATH001",
            subject_name="数学",
            grade="高一",
            description="高中数学课程"
        )
        
        assert subject.subject_id == "MATH001"
        assert subject.subject_name == "数学"
        assert subject.grade == "高一"
        assert subject.description == "高中数学课程"
    
    def test_teaching_material_model(self):
        """测试教材模型"""
        material = TeachingMaterial(
            material_id="TM001",
            title="高中数学必修一",
            subject_id="MATH001",
            grade="高一",
            content="数学教材内容",
            difficulty_level="中等"
        )
        
        assert material.material_id == "TM001"
        assert material.title == "高中数学必修一"
        assert material.subject_id == "MATH001"
        assert material.grade == "高一"
        assert material.content == "数学教材内容"
        assert material.difficulty_level == "中等"
    
    def test_learning_record_model(self):
        """测试学习记录模型"""
        record = LearningRecord(
            record_id="LR001",
            student_id="S001",
            material_id="TM001",
            learning_time=120,  # 分钟
            progress=0.75,
            notes="学习笔记"
        )
        
        assert record.record_id == "LR001"
        assert record.student_id == "S001"
        assert record.material_id == "TM001"
        assert record.learning_time == 120
        assert record.progress == 0.75
        assert record.notes == "学习笔记"


if __name__ == "__main__":
    pytest.main([__file__])