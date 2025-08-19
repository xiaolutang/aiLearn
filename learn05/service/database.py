#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库访问层
提供对象关系映射和数据库操作功能
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, CheckConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from datetime import datetime
import os

# 数据库URL
# 获取当前文件所在目录
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(CURRENT_DIR, 'student_database.db')}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特有参数
    echo=False  # 生产环境中应设为False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


# 数据模型定义

class DatabaseManager:
    """数据库管理器类，提供执行SQL查询的功能"""
    
    def __init__(self, db_url=DATABASE_URL):
        """初始化数据库管理器
        
        Args:
            db_url: 数据库连接URL
        """
        self.engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},  # SQLite特有参数
            echo=False  # 生产环境中应设为False
        )
    
    def execute_query(self, query: str, params = None):
        """执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数(可选) - 支持元组、字典或列表格式
            
        Returns:
            list: 查询结果列表，每行是一个元组
        """
        with self.engine.connect() as connection:
            if params:
                # 处理不同格式的参数
                if isinstance(params, (tuple, list)):
                    # 对于元组或列表，转换为字典格式
                    # 将 ? 占位符替换为 :param0, :param1 等
                    param_dict = {}
                    modified_query = query
                    param_index = 0
                    while '?' in modified_query:
                        param_name = f'param{param_index}'
                        modified_query = modified_query.replace('?', f':{param_name}', 1)
                        if param_index < len(params):
                            param_dict[param_name] = params[param_index]
                        param_index += 1
                    result = connection.execute(text(modified_query), param_dict)
                else:
                    # 字典格式直接使用
                    result = connection.execute(text(query), params)
            else:
                result = connection.execute(text(query))
            
            # 对于SELECT查询，返回结果
            if query.strip().upper().startswith('SELECT'):
                return [tuple(row) for row in result.fetchall()]
            # 对于INSERT/UPDATE/DELETE等，提交事务并返回影响的行数
            else:
                connection.commit()
                return result.rowcount


class User(Base):
    """用户表模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, CheckConstraint("role IN ('teacher', 'student', 'parent', 'admin')"), nullable=False)
    related_id = Column(Integer)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系定义
    notifications = relationship("Notification", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")


class Role(Base):
    """角色表模型"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    permissions = Column(Text, default="{}")  # 存储JSON格式的权限信息
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    users = relationship("User", secondary="user_roles", back_populates="roles")


class UserRole(Base):
    """用户角色关联表模型"""
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)


class Student(Base):
    """学生表模型"""
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    student_number = Column(String, unique=True, index=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False)
    gender = Column(String)
    date_of_birth = Column(String)
    contact_info = Column(String)
    
    # 关系定义
    class_ = relationship("Class", back_populates="students")
    grades = relationship("Grade", back_populates="student")
    attendance = relationship("Attendance", back_populates="student")
    class_performances = relationship("ClassPerformance", back_populates="student")
    learning_status = relationship("LearningStatus", back_populates="student")
    tutoring_plans = relationship("TutoringPlan", back_populates="student")


class Class(Base):
    """班级表模型"""
    __tablename__ = "classes"
    
    class_id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String, nullable=False)
    grade_level = Column(Integer, nullable=False)
    head_teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    
    # 关系定义
    students = relationship("Student", back_populates="class_")
    head_teacher = relationship("Teacher", back_populates="classes")


class Teacher(Base):
    """教师表模型"""
    __tablename__ = "teachers"
    
    teacher_id = Column(Integer, primary_key=True, index=True)
    teacher_name = Column(String, nullable=False)
    teacher_number = Column(String, unique=True, index=True, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"))
    contact_info = Column(String)
    
    # 关系定义
    classes = relationship("Class", back_populates="head_teacher")
    teaching_resources = relationship("TeachingResource", back_populates="author")


class Subject(Base):
    """科目表模型"""
    __tablename__ = "subjects"
    
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, nullable=False)
    credit = Column(Integer, nullable=False)
    
    # 关系定义
    teachers = relationship("Teacher")
    grades = relationship("Grade", back_populates="subject")


class Grade(Base):
    """成绩表模型"""
    __tablename__ = "grades"
    
    grade_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    exam_date = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    exam_type = Column(String, nullable=False)
    
    # 关系定义
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")


class Course(Base):
    """课程安排表模型"""
    __tablename__ = "courses"
    
    course_id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False)
    course_code = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    
    # 关系定义
    class_ = relationship("Class")
    subject = relationship("Subject")
    teacher = relationship("Teacher")


class Attendance(Base):
    """考勤表模型"""
    __tablename__ = "attendance"
    
    attendance_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, nullable=False)
    reason = Column(String)
    
    # 关系定义
    student = relationship("Student", back_populates="attendance")
    class_ = relationship("Class")


class ClassPerformance(Base):
    """课堂表现表模型"""
    __tablename__ = "class_performance"
    
    performance_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False)
    date = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    comment = Column(String)
    
    # 关系定义
    student = relationship("Student", back_populates="class_performances")
    teacher = relationship("Teacher")
    class_ = relationship("Class")


class Textbook(Base):
    """教材表模型"""
    __tablename__ = "textbooks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String)
    subject = Column(String, nullable=False)
    grade = Column(Integer, nullable=False)
    publisher = Column(String)
    chapters = Column(Text)  # JSON格式存储章节信息
    knowledge_points = Column(Text)  # JSON格式存储知识点信息
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class LearningStatus(Base):
    """学情表模型"""
    __tablename__ = "learning_status"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    knowledge_point = Column(String, nullable=False)
    mastery_level = Column(Integer, CheckConstraint("mastery_level BETWEEN 1 AND 10"))
    weakness_analysis = Column(String)
    improvement_suggestions = Column(String)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    student = relationship("Student", back_populates="learning_status")


class TeachingResource(Base):
    """教学资源表模型"""
    __tablename__ = "teaching_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, CheckConstraint("type IN ('教案', '课件', '练习题', '视频', '其他')"), nullable=False)
    content = Column(Text)
    file_path = Column(String)
    author_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False)
    subject = Column(String, nullable=False)
    grade = Column(Integer, nullable=False)
    tags = Column(Text)  # JSON格式存储标签
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    author = relationship("Teacher", back_populates="teaching_resources")


class TutoringPlan(Base):
    """辅导方案表模型"""
    __tablename__ = "tutoring_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    plan_content = Column(Text, nullable=False)
    resources = Column(Text)  # JSON格式存储推荐资源列表
    progress = Column(Integer, CheckConstraint("progress BETWEEN 0 AND 100"), default=0)
    effect_evaluation = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    student = relationship("Student", back_populates="tutoring_plans")


class Notification(Base):
    """消息通知表模型"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    notification_type = Column(String, default="info")  # 通知类型：info, system, class, grade, plan, progress等
    priority = Column(String, default="normal")  # 优先级：high, normal, low
    related_id = Column(Integer, nullable=True)  # 相关联的ID，如班级ID、学生ID等
    related_type = Column(String, nullable=True)  # 相关联的类型，如class, student, grade等
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系定义
    user = relationship("User", back_populates="notifications")


# 数据库操作函数

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    # 仅创建不存在的表
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("数据库初始化完成")


def get_student_by_id(db, student_id: int):
    """根据ID获取学生信息"""
    return db.query(Student).filter(Student.student_id == student_id).first()


def get_class_by_id(db, class_id: int):
    """根据ID获取班级信息"""
    return db.query(Class).filter(Class.class_id == class_id).first()


def get_user_by_username(db, username: str):
    """根据用户名获取用户信息"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db, email: str):
    """根据邮箱获取用户信息"""
    return db.query(User).filter(User.email == email).first()

def get_user(db, user_id: int):
    """根据用户ID获取用户信息"""
    return db.query(User).filter(User.id == user_id).first()


def get_grades_by_student_id(db, student_id: int):
    """获取学生的所有成绩"""
    return db.query(Grade).filter(Grade.student_id == student_id).all()


def get_grades_by_class_id_and_subject_id(db, class_id: int, subject_id: int, exam_type: str = None):
    """获取班级某科目的成绩"""
    query = db.query(Grade).join(Student).filter(
        Student.class_id == class_id,
        Grade.subject_id == subject_id
    )
    
    if exam_type:
        query = query.filter(Grade.exam_type == exam_type)
        
    return query.all()


def get_students_by_class_id(db, class_id: int):
    """获取班级的所有学生"""
    return db.query(Student).filter(Student.class_id == class_id).all()


def get_subject_by_id(db, subject_id: int):
    """根据ID获取科目信息"""
    return db.query(Subject).filter(Subject.subject_id == subject_id).first()


def get_tutoring_plan_by_id(db, plan_id: int):
    """根据ID获取辅导方案"""
    return db.query(TutoringPlan).filter(TutoringPlan.id == plan_id).first()


def get_tutoring_plans_by_student_id(db, student_id: int):
    """获取学生的所有辅导方案"""
    return db.query(TutoringPlan).filter(TutoringPlan.student_id == student_id).all()


def get_learning_status_by_student_id(db, student_id: int):
    """获取学生的学情信息"""
    return db.query(LearningStatus).filter(LearningStatus.student_id == student_id).all()


def get_notifications_by_user_id(db, user_id: int, is_read: bool = None):
    """获取用户的通知"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
        
    return query.order_by(Notification.created_at.desc()).all()


def get_teaching_resources(db, subject: str = None, grade: int = None, resource_type: str = None):
    """获取教学资源"""
    query = db.query(TeachingResource)
    
    if subject:
        query = query.filter(TeachingResource.subject == subject)
    if grade:
        query = query.filter(TeachingResource.grade == grade)
    if resource_type:
        query = query.filter(TeachingResource.type == resource_type)
        
    return query.order_by(TeachingResource.created_at.desc()).all()


def get_textbooks(db, subject: str = None, grade: int = None):
    """获取教材"""
    query = db.query(Textbook)
    
    if subject:
        query = query.filter(Textbook.subject == subject)
    if grade:
        query = query.filter(Textbook.grade == grade)
        
    return query.order_by(Textbook.grade, Textbook.subject).all()


def get_student_attendance(db, student_id: int, start_date: str = None, end_date: str = None):
    """获取学生的考勤记录"""
    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
        
    return query.order_by(Attendance.date.desc()).all()


def get_student_class_performance(db, student_id: int, start_date: str = None, end_date: str = None):
    """获取学生的课堂表现记录"""
    query = db.query(ClassPerformance).filter(ClassPerformance.student_id == student_id)
    
    if start_date:
        query = query.filter(ClassPerformance.date >= start_date)
    if end_date:
        query = query.filter(ClassPerformance.date <= end_date)
        
    return query.order_by(ClassPerformance.date.desc()).all()


if __name__ == "__main__":
    # 初始化数据库
    init_db()