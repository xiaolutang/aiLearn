#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型
"""

from typing import Dict, Any, Optional
from datetime import datetime

class Student:
    """学生模型"""
    def __init__(self, student_id: str, name: str, class_name: str):
        self.student_id = student_id
        self.name = name
        self.class_name = class_name
        self.created_at = datetime.now()

class Grade:
    """成绩模型"""
    def __init__(self, student_id: str, subject: str, score: float, exam_type: str):
        self.student_id = student_id
        self.subject = subject
        self.score = score
        self.exam_type = exam_type
        self.created_at = datetime.now()

class Subject:
    """科目模型"""
    def __init__(self, subject_id: str, name: str, description: str = ""):
        self.subject_id = subject_id
        self.name = name
        self.description = description

class TeachingMaterial:
    """教材模型"""
    def __init__(self, material_id: str, title: str, subject: str, content: str):
        self.material_id = material_id
        self.title = title
        self.subject = subject
        self.content = content

class LearningRecord:
    """学习记录模型"""
    def __init__(self, record_id: str, student_id: str, activity: str, duration: int):
        self.record_id = record_id
        self.student_id = student_id
        self.activity = activity
        self.duration = duration
        self.timestamp = datetime.now()
