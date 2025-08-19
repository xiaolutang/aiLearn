#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成模拟数据脚本
生成500人左右的模拟用户数据和学生成绩数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, Student, Grade, Subject, Class, engine, Base
from sqlalchemy.orm import Session
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker
import hashlib

# 初始化Faker，使用中文本地化
fake = Faker('zh_CN')

def hash_password(password: str) -> str:
    """密码哈希函数"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_users_data():
    """生成用户数据"""
    users_data = []
    
    # 生成管理员用户 (10个)
    for i in range(10):
        username = f"admin{i+1:02d}"
        password = f"Admin{i+1:03d}!"
        users_data.append({
            'username': username,
            'password': hash_password(password),
            'role': 'admin',
            'email': f"{username}@school.edu.cn",
            'phone_number': fake.phone_number(),
            'is_active': True,
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        })
    
    # 生成教师用户 (80个)
    for i in range(80):
        username = f"teacher{i+1:03d}"
        password = f"Teacher{i+1:03d}!"
        users_data.append({
            'username': username,
            'password': hash_password(password),
            'role': 'teacher',
            'email': f"{username}@school.edu.cn",
            'phone_number': fake.phone_number(),
            'is_active': True,
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        })
    
    # 生成学生用户 (350个)
    for i in range(350):
        username = f"student{i+1:04d}"
        password = f"Student{i+1:04d}!"
        users_data.append({
            'username': username,
            'password': hash_password(password),
            'role': 'student',
            'email': f"{username}@student.edu.cn",
            'phone_number': fake.phone_number(),
            'is_active': True,
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        })
    
    # 生成家长用户 (60个)
    for i in range(60):
        username = f"parent{i+1:03d}"
        password = f"Parent{i+1:03d}!"
        users_data.append({
            'username': username,
            'password': hash_password(password),
            'role': 'parent',
            'email': f"{username}@parent.com",
            'phone_number': fake.phone_number(),
            'is_active': True,
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        })
    
    return users_data

def generate_classes_data():
    """生成班级数据"""
    classes_data = []
    grades = [1, 2, 3, 4, 5, 6]
    
    for grade in grades:
        for class_num in range(1, 7):  # 每个年级6个班
            classes_data.append({
                'class_name': f"{grade}年级{class_num}班",
                'grade_level': grade,
                'head_teacher_id': None  # 暂时不分配班主任
            })
    
    return classes_data

def generate_subjects_data():
    """生成科目数据"""
    subjects = [
        {'subject_name': '语文', 'credit': 4},
        {'subject_name': '数学', 'credit': 4},
        {'subject_name': '英语', 'credit': 3},
        {'subject_name': '物理', 'credit': 3},
        {'subject_name': '化学', 'credit': 3},
        {'subject_name': '生物', 'credit': 2},
        {'subject_name': '历史', 'credit': 2},
        {'subject_name': '地理', 'credit': 2},
        {'subject_name': '政治', 'credit': 2},
        {'subject_name': '体育', 'credit': 2},
        {'subject_name': '音乐', 'credit': 1},
        {'subject_name': '美术', 'credit': 1}
    ]
    
    return subjects

def generate_students_data(user_ids):
    """生成学生详细信息数据"""
    students_data = []
    
    for i, user_id in enumerate(user_ids[:350]):  # 最多350个学生
        birth_date = fake.date_of_birth(minimum_age=6, maximum_age=18)
        students_data.append({
            'student_name': fake.name(),
            'student_number': f"S{2024}{i+1:04d}",
            'gender': random.choice(['男', '女']),
            'date_of_birth': str(birth_date),
            'class_id': random.randint(1, 36),  # 36个班级
            'contact_info': fake.phone_number()
        })
    
    return students_data

def generate_grades_data(student_ids, subject_ids):
    """生成成绩数据"""
    grades_data = []
    exam_types = ['期中考试', '期末考试', '月考', '单元测试', '随堂测验']
    
    # 为每个学生生成多次考试成绩
    for student_id in student_ids:
        for _ in range(random.randint(15, 25)):  # 每个学生15-25次考试记录
            subject_id = random.choice(subject_ids)
            exam_type = random.choice(exam_types)
            
            # 根据考试类型设置不同的分数范围
            if exam_type in ['期中考试', '期末考试']:
                score = random.uniform(60, 100)  # 重要考试分数相对较高
            else:
                score = random.uniform(50, 100)  # 平时测验分数范围更大
            
            grades_data.append({
                'student_id': student_id,
                'subject_id': subject_id,
                'score': round(score, 1),
                'exam_type': exam_type,
                'exam_date': str(fake.date_between(start_date='-1y', end_date='now'))
            })
    
    return grades_data

def insert_data_to_database():
    """将生成的数据插入数据库"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("开始生成和插入模拟数据...")
        
        # 清空现有数据
        print("清空现有数据...")
        db.query(Grade).delete()
        db.query(Student).delete()
        db.query(Subject).delete()
        db.query(Class).delete()
        db.query(User).delete()
        db.commit()
        
        # 插入用户数据
        print("插入用户数据...")
        users_data = generate_users_data()
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        db.commit()
        
        # 获取用户ID
        user_ids = [user.id for user in db.query(User).all()]
        print(f"插入了 {len(user_ids)} 个用户")
        
        # 插入班级数据
        print("插入班级数据...")
        classes_data = generate_classes_data()
        for class_data in classes_data:
            class_obj = Class(**class_data)
            db.add(class_obj)
        db.commit()
        
        class_ids = [cls.class_id for cls in db.query(Class).all()]
        print(f"插入了 {len(class_ids)} 个班级")
        
        # 插入科目数据
        print("插入科目数据...")
        subjects_data = generate_subjects_data()
        for subject_data in subjects_data:
            subject = Subject(**subject_data)
            db.add(subject)
        db.commit()
        
        subject_ids = [subject.subject_id for subject in db.query(Subject).all()]
        print(f"插入了 {len(subject_ids)} 个科目")
        
        # 插入学生详细信息
        print("插入学生详细信息...")
        student_user_ids = [user.id for user in db.query(User).filter(User.role == 'student').all()]
        students_data = generate_students_data(student_user_ids)
        for student_data in students_data:
            # 确保class_id在有效范围内
            student_data['class_id'] = random.randint(1, len(class_ids))
            student = Student(**student_data)
            db.add(student)
        db.commit()
        
        student_ids = [student.student_id for student in db.query(Student).all()]
        print(f"插入了 {len(student_ids)} 个学生详细信息")
        
        # 插入成绩数据
        print("插入成绩数据...")
        grades_data = generate_grades_data(student_ids, subject_ids)
        for grade_data in grades_data:
            grade = Grade(**grade_data)
            db.add(grade)
        db.commit()
        
        grade_count = db.query(Grade).count()
        print(f"插入了 {grade_count} 条成绩记录")
        
        print("\n数据插入完成！")
        print(f"总计：")
        print(f"- 用户: {db.query(User).count()} 个")
        print(f"- 班级: {db.query(Class).count()} 个")
        print(f"- 科目: {db.query(Subject).count()} 个")
        print(f"- 学生: {db.query(Student).count()} 个")
        print(f"- 成绩记录: {db.query(Grade).count()} 条")
        
        return True
        
    except Exception as e:
        print(f"数据插入失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def export_data_to_excel():
    """导出数据到Excel文件"""
    db = SessionLocal()
    try:
        print("\n开始导出数据到Excel...")
        
        # 创建输出目录
        output_dir = "/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount"
        os.makedirs(output_dir, exist_ok=True)
        
        # 导出用户数据
        users = db.query(User).all()
        users_df = pd.DataFrame([{
            'ID': user.id,
            '用户名': user.username,
            '角色': user.role,
            '邮箱': user.email,
            '电话': user.phone_number,
            '是否激活': user.is_active,
            '创建时间': user.created_at
        } for user in users])
        
        # 导出班级数据
        classes = db.query(Class).all()
        classes_df = pd.DataFrame([{
            'ID': cls.class_id,
            '班级名称': cls.class_name,
            '年级': cls.grade_level,
            '班主任ID': cls.head_teacher_id
        } for cls in classes])
        
        # 导出科目数据
        subjects = db.query(Subject).all()
        subjects_df = pd.DataFrame([{
            'ID': subject.subject_id,
            '科目名称': subject.subject_name,
            '学分': subject.credit
        } for subject in subjects])
        
        # 导出学生数据
        students = db.query(Student).all()
        students_df = pd.DataFrame([{
            'ID': student.student_id,
            '学号': student.student_number,
            '姓名': student.student_name,
            '性别': student.gender,
            '出生日期': student.date_of_birth,
            '班级ID': student.class_id,
            '联系方式': student.contact_info
        } for student in students])
        
        # 导出成绩数据
        grades = db.query(Grade).all()
        grades_df = pd.DataFrame([{
            'ID': grade.grade_id,
            '学生ID': grade.student_id,
            '科目ID': grade.subject_id,
            '分数': grade.score,
            '考试类型': grade.exam_type,
            '考试日期': grade.exam_date
        } for grade in grades])
        
        # 创建Excel文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = os.path.join(output_dir, f"mock_data_export_{timestamp}.xlsx")
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            users_df.to_excel(writer, sheet_name='用户数据', index=False)
            classes_df.to_excel(writer, sheet_name='班级数据', index=False)
            subjects_df.to_excel(writer, sheet_name='科目数据', index=False)
            students_df.to_excel(writer, sheet_name='学生数据', index=False)
            grades_df.to_excel(writer, sheet_name='成绩数据', index=False)
        
        print(f"数据已导出到: {excel_file}")
        
        # 生成用户账号密码清单
        password_file = os.path.join(output_dir, f"user_accounts_{timestamp}.xlsx")
        accounts_df = pd.DataFrame([{
            '用户名': user.username,
            '密码': f"{user.role.title()}{user.username[len(user.role):]}!" if user.username.startswith(user.role) else f"{user.role.title()}123!",
            '角色': user.role,
            '邮箱': user.email
        } for user in users])
        
        accounts_df.to_excel(password_file, index=False)
        print(f"用户账号密码清单已导出到: {password_file}")
        
        return True
        
    except Exception as e:
        print(f"数据导出失败: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("智能教学助手 - 模拟数据生成器")
    print("=" * 50)
    
    # 插入数据
    if insert_data_to_database():
        # 导出数据
        export_data_to_excel()
        print("\n所有操作完成！")
    else:
        print("\n数据生成失败！")