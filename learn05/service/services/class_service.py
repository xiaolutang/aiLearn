# -*- coding: utf-8 -*-
"""
班级管理服务模块
提供班级相关的业务逻辑
"""

import logging
from typing import Dict, List, Optional, Any, Union
import datetime

from models.class_model import (
    ClassBase, ClassCreate, ClassUpdate, ClassResponse,
    ClassMemberCreate, ClassMemberUpdate, ClassMemberResponse,
    ClassSubjectCreate, ClassSubjectResponse,
    ClassPerformance, PaginatedClasses, PaginatedClassMembers, PaginatedClassSubjects,
    CLASS_ROLES, is_valid_class_role
)
from models.user import UserResponse
from models.grade import GradeResponse, GradeStatistics
from config.core_config import get_config, get_db_url
from database import DatabaseManager
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from llm.factory import get_llm_client

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取配置
config = get_config()


class ClassService:
    """班级管理服务类"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """初始化班级管理服务
        
        Args:
            db_manager: 数据库管理器实例(可选，默认创建新的)
        """
        self.db_manager = db_manager or DatabaseManager(get_db_url())
        self.llm_client = get_llm_client("openai")
    
    def create_class(self, class_data: ClassCreate) -> ClassResponse:
        """创建班级
        
        Args:
            class_data: 班级创建数据
            
        Returns:
            ClassResponse: 创建的班级响应
        """
        logger.info(f"创建班级: {class_data.name}")
        
        # 检查班级名称是否已存在
        existing_class = self.db_manager.execute_query(
            "SELECT * FROM classes WHERE name = ?",
            (class_data.name,)
        )
        
        if existing_class and len(existing_class) > 0:
            raise ValueError(f"班级名称 '{class_data.name}' 已存在")
        
        # 创建班级
        result = self.db_manager.execute_query(
            """
            INSERT INTO classes (id, name, description, grade_level, teacher_id, 
            start_date, end_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                class_data.id,
                class_data.name,
                class_data.description,
                class_data.grade_level,
                class_data.teacher_id,
                class_data.start_date,
                class_data.end_date,
                class_data.created_at,
                class_data.updated_at
            )
        )
        
        if result is None:
            raise Exception("创建班级失败")
        
        # 创建班级成员记录（添加班主任）
        if class_data.teacher_id:
            self.add_class_member(
                ClassMemberCreate(
                    class_id=class_data.id,
                    student_id=class_data.teacher_id,
                    role="teacher",
                    join_date=class_data.created_at
                )
            )
        
        # 返回班级响应
        return ClassResponse(
            id=class_data.id,
            name=class_data.name,
            description=class_data.description,
            grade_level=class_data.grade_level,
            teacher_id=class_data.teacher_id,
            student_count=1 if class_data.teacher_id else 0,
            start_date=class_data.start_date,
            end_date=class_data.end_date,
            created_at=class_data.created_at,
            updated_at=class_data.updated_at
        )
    
    def get_class(self, class_id: str) -> Optional[ClassResponse]:
        """获取单个班级
        
        Args:
            class_id: 班级ID
            
        Returns:
            Optional[ClassResponse]: 班级响应，如果不存在则返回None
        """
        logger.debug(f"获取班级: ID={class_id}")
        
        result = self.db_manager.execute_query(
            "SELECT * FROM classes WHERE id = ?",
            (class_id,)
        )
        
        if not result or len(result) == 0:
            return None
        
        class_data = result[0]
        
        # 获取学生数量
        student_count = self.db_manager.execute_query(
            "SELECT COUNT(*) FROM class_members WHERE class_id = ?",
            (class_id,)
        )
        
        return ClassResponse(
            id=class_data[0],
            name=class_data[1],
            description=class_data[2],
            grade_level=class_data[3],
            teacher_id=class_data[4],
            student_count=student_count[0][0] if student_count else 0,
            start_date=class_data[5],
            end_date=class_data[6],
            created_at=class_data[7],
            updated_at=class_data[8]
        )
    
    def update_class(self, class_id: str, class_data: ClassUpdate) -> ClassResponse:
        """更新班级信息
        
        Args:
            class_id: 班级ID
            class_data: 班级更新数据
            
        Returns:
            ClassResponse: 更新后的班级响应
        """
        logger.info(f"更新班级信息: ID={class_id}")
        
        # 检查班级是否存在
        existing_class = self.db_manager.execute_query(
            "SELECT * FROM classes WHERE id = ?",
            (class_id,)
        )
        
        if not existing_class or len(existing_class) == 0:
            raise ValueError(f"班级不存在: {class_id}")
        
        # 检查班级名称是否已被其他班级使用
        if class_data.name is not None:
            other_class = self.db_manager.execute_query(
                "SELECT * FROM classes WHERE name = ? AND id != ?",
                (class_data.name, class_id)
            )
            
            if other_class and len(other_class) > 0:
                raise ValueError(f"班级名称 '{class_data.name}' 已被使用")
        
        # 构建更新字段和参数
        update_fields = []
        params = []
        
        if class_data.name is not None:
            update_fields.append("name = ?")
            params.append(class_data.name)
        
        if class_data.description is not None:
            update_fields.append("description = ?")
            params.append(class_data.description)
        
        if class_data.grade_level is not None:
            update_fields.append("grade_level = ?")
            params.append(class_data.grade_level)
        
        if class_data.teacher_id is not None:
            update_fields.append("teacher_id = ?")
            params.append(class_data.teacher_id)
        
        if class_data.start_date is not None:
            update_fields.append("start_date = ?")
            params.append(class_data.start_date)
        
        if class_data.end_date is not None:
            update_fields.append("end_date = ?")
            params.append(class_data.end_date)
        
        # 添加更新时间和班级ID
        update_fields.append("updated_at = ?")
        params.append(datetime.datetime.now())
        params.append(class_id)
        
        # 执行更新
        if update_fields:
            query = f"UPDATE classes SET {', '.join(update_fields)} WHERE id = ?"
            self.db_manager.execute_query(query, tuple(params))
        
        # 返回更新后的班级
        updated_class = self.db_manager.execute_query(
            "SELECT * FROM classes WHERE id = ?",
            (class_id,)
        )
        
        if not updated_class or len(updated_class) == 0:
            raise Exception("更新班级失败")
        
        class_data = updated_class[0]
        
        # 获取学生数量
        student_count = self.db_manager.execute_query(
            "SELECT COUNT(*) FROM class_members WHERE class_id = ?",
            (class_id,)
        )
        
        return ClassResponse(
            id=class_data[0],
            name=class_data[1],
            description=class_data[2],
            grade_level=class_data[3],
            teacher_id=class_data[4],
            student_count=student_count[0][0] if student_count else 0,
            start_date=class_data[5],
            end_date=class_data[6],
            created_at=class_data[7],
            updated_at=class_data[8]
        )
    
    def delete_class(self, class_id: str) -> bool:
        """删除班级
        
        Args:
            class_id: 班级ID
            
        Returns:
            bool: 是否删除成功
        """
        logger.info(f"删除班级: ID={class_id}")
        
        # 检查班级是否存在
        existing_class = self.db_manager.execute_query(
            "SELECT * FROM classes WHERE id = ?",
            (class_id,)
        )
        
        if not existing_class or len(existing_class) == 0:
            raise ValueError(f"班级不存在: {class_id}")
        
        # 先删除班级相关的所有记录（班级成员、班级科目等）
        self.db_manager.execute_query("DELETE FROM class_members WHERE class_id = ?", (class_id,))
        self.db_manager.execute_query("DELETE FROM class_subjects WHERE class_id = ?", (class_id,))
        
        # 执行删除班级
        result = self.db_manager.execute_query(
            "DELETE FROM classes WHERE id = ?",
            (class_id,)
        )
        
        return result is not None
    
    def get_classes(self, page: int = 1, limit: int = 10, **filters) -> PaginatedClasses:
        """获取班级列表
        
        Args:
            page: 当前页码
            limit: 每页数量
            **filters: 过滤条件
            
        Returns:
            PaginatedClasses: 分页班级列表
        """
        logger.info(f"获取班级列表: 页码={page}, 每页数量={limit}, 过滤条件={filters}")
        
        # 构建查询条件
        query_parts = ["SELECT * FROM classes WHERE 1=1"]
        params = []
        
        # 添加过滤条件
        if "grade_level" in filters:
            query_parts.append("AND grade_level = ?")
            params.append(filters["grade_level"])
        
        if "teacher_id" in filters:
            query_parts.append("AND teacher_id = ?")
            params.append(filters["teacher_id"])
        
        if "search" in filters:
            search_term = f"%{filters['search']}%"
            query_parts.append("AND (name LIKE ? OR description LIKE ?)")
            params.extend([search_term, search_term])
        
        # 添加分页
        offset = (page - 1) * limit
        query_parts.append("ORDER BY created_at DESC")
        query_parts.append("LIMIT ? OFFSET ?")
        params.extend([limit, offset])
        
        # 执行查询
        query = " ".join(query_parts)
        results = self.db_manager.execute_query(query, tuple(params))
        
        # 构建班级列表
        classes = []
        for class_data in results:
            # 获取学生数量
            student_count = self.db_manager.execute_query(
                "SELECT COUNT(*) FROM class_members WHERE class_id = ?",
                (class_data[0],)
            )
            
            classes.append(ClassResponse(
                id=class_data[0],
                name=class_data[1],
                description=class_data[2],
                grade_level=class_data[3],
                teacher_id=class_data[4],
                student_count=student_count[0][0] if student_count else 0,
                start_date=class_data[5],
                end_date=class_data[6],
                created_at=class_data[7],
                updated_at=class_data[8]
            ))
        
        # 获取总数
        total_query = "SELECT COUNT(*) FROM classes WHERE 1=1"
        if len(query_parts) > 1:
            total_query += " " + " ".join(query_parts[1:-2])  # 不包含ORDER BY, LIMIT和OFFSET
        total_result = self.db_manager.execute_query(total_query, tuple(params[:-2]))  # 不包含LIMIT和OFFSET参数
        total = total_result[0][0] if total_result else 0
        
        # 计算总页数
        total_pages = (total + limit - 1) // limit
        
        return PaginatedClasses(
            classes=classes,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    def add_class_member(self, member_data: ClassMemberCreate) -> ClassMemberResponse:
        """添加班级成员
        
        Args:
            member_data: 班级成员创建数据
            
        Returns:
            ClassMemberResponse: 创建的班级成员响应
        """
        logger.info(f"添加班级成员: 班级ID={member_data.class_id}, 学生ID={member_data.student_id}")
        
        # 验证角色
        if not is_valid_class_role(member_data.role):
            raise ValueError(f"无效的角色: {member_data.role}")
        
        # 检查成员是否已存在
        existing_member = self.db_manager.execute_query(
            """
            SELECT * FROM class_members 
            WHERE class_id = ? AND student_id = ?
            """,
            (member_data.class_id, member_data.student_id)
        )
        
        if existing_member and len(existing_member) > 0:
            raise ValueError("成员已存在于班级中")
        
        # 创建班级成员
        result = self.db_manager.execute_query(
            """
            INSERT INTO class_members (id, class_id, student_id, role, 
            join_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                member_data.id,
                member_data.class_id,
                member_data.student_id,
                member_data.role,
                member_data.join_date,
                member_data.created_at,
                member_data.updated_at
            )
        )
        
        if result is None:
            raise Exception("添加班级成员失败")
        
        # 获取用户信息
        user_info = self.db_manager.execute_query(
            "SELECT username, full_name, email FROM users WHERE id = ?",
            (member_data.student_id,)
        )
        
        user = None
        if user_info and len(user_info) > 0:
            user = {
                "id": member_data.student_id,
                "username": user_info[0][0],
                "full_name": user_info[0][1],
                "email": user_info[0][2]
            }
        
        # 返回班级成员响应
        return ClassMemberResponse(
            id=member_data.id,
            class_id=member_data.class_id,
            student_id=member_data.student_id,
            role=member_data.role,
            role_display=get_role_display_name(member_data.role),
            join_date=member_data.join_date,
            user=user,
            created_at=member_data.created_at,
            updated_at=member_data.updated_at
        )
    
    def get_class_members(self, class_id: str, page: int = 1, limit: int = 10, 
                         role: str = None) -> PaginatedClassMembers:
        """获取班级成员列表
        
        Args:
            class_id: 班级ID
            page: 当前页码
            limit: 每页数量
            role: 成员角色过滤(可选)
            
        Returns:
            PaginatedClassMembers: 分页班级成员列表
        """
        logger.info(f"获取班级成员列表: 班级ID={class_id}, 页码={page}, 每页数量={limit}, 角色={role}")
        
        # 构建查询条件
        query_parts = [
            """
            SELECT cm.*, u.username, u.full_name, u.email 
            FROM class_members cm
            JOIN users u ON cm.student_id = u.id
            WHERE cm.class_id = ?
            """
        ]
        params = [class_id]
        
        # 添加角色过滤
        if role:
            query_parts.append("AND cm.role = ?")
            params.append(role)
        
        # 添加分页
        offset = (page - 1) * limit
        query_parts.append("ORDER BY cm.role ASC, u.full_name ASC")
        query_parts.append("LIMIT ? OFFSET ?")
        params.extend([limit, offset])
        
        # 执行查询
        query = " ".join(query_parts)
        results = self.db_manager.execute_query(query, tuple(params))
        
        # 构建班级成员列表
        members = []
        for member_data in results:
            user = {
                "id": member_data[2],
                "username": member_data[7],
                "full_name": member_data[8],
                "email": member_data[9]
            }
            
            members.append(ClassMemberResponse(
                id=member_data[0],
                class_id=member_data[1],
                student_id=member_data[2],
                role=member_data[3],
                role_display=get_role_display_name(member_data[3]),
                join_date=member_data[4],
                user=user,
                created_at=member_data[5],
                updated_at=member_data[6]
            ))
        
        # 获取总数
        total_query = "SELECT COUNT(*) FROM class_members WHERE class_id = ?"
        if role:
            total_query += " AND role = ?"
        total_result = self.db_manager.execute_query(total_query, tuple(params[:-2]))  # 不包含LIMIT和OFFSET参数
        total = total_result[0][0] if total_result else 0
        
        # 计算总页数
        total_pages = (total + limit - 1) // limit
        
        return PaginatedClassMembers(
            members=members,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    def update_class_member(self, member_id: str, member_data: ClassMemberUpdate) -> ClassMemberResponse:
        """更新班级成员信息
        
        Args:
            member_id: 班级成员ID
            member_data: 班级成员更新数据
            
        Returns:
            ClassMemberResponse: 更新后的班级成员响应
        """
        logger.info(f"更新班级成员信息: ID={member_id}")
        
        # 检查成员是否存在
        existing_member = self.db_manager.execute_query(
            "SELECT * FROM class_members WHERE id = ?",
            (member_id,)
        )
        
        if not existing_member or len(existing_member) == 0:
            raise ValueError(f"班级成员不存在: {member_id}")
        
        # 验证角色
        if member_data.role and not is_valid_class_role(member_data.role):
            raise ValueError(f"无效的角色: {member_data.role}")
        
        # 构建更新字段和参数
        update_fields = []
        params = []
        
        if member_data.role is not None:
            update_fields.append("role = ?")
            params.append(member_data.role)
        
        # 添加更新时间和成员ID
        update_fields.append("updated_at = ?")
        params.append(datetime.datetime.now())
        params.append(member_id)
        
        # 执行更新
        if update_fields:
            query = f"UPDATE class_members SET {', '.join(update_fields)} WHERE id = ?"
            self.db_manager.execute_query(query, tuple(params))
        
        # 返回更新后的成员信息
        updated_member = self.db_manager.execute_query(
            """
            SELECT cm.*, u.username, u.full_name, u.email 
            FROM class_members cm
            JOIN users u ON cm.student_id = u.id
            WHERE cm.id = ?
            """,
            (member_id,)
        )
        
        if not updated_member or len(updated_member) == 0:
            raise Exception("更新班级成员失败")
        
        member_data = updated_member[0]
        user = {
            "id": member_data[2],
            "username": member_data[7],
            "full_name": member_data[8],
            "email": member_data[9]
        }
        
        return ClassMemberResponse(
            id=member_data[0],
            class_id=member_data[1],
            student_id=member_data[2],
            role=member_data[3],
            role_display=get_role_display_name(member_data[3]),
            join_date=member_data[4],
            user=user,
            created_at=member_data[5],
            updated_at=member_data[6]
        )
    
    def remove_class_member(self, member_id: str) -> bool:
        """移除班级成员
        
        Args:
            member_id: 班级成员ID
            
        Returns:
            bool: 是否移除成功
        """
        logger.info(f"移除班级成员: ID={member_id}")
        
        # 检查成员是否存在
        existing_member = self.db_manager.execute_query(
            "SELECT * FROM class_members WHERE id = ?",
            (member_id,)
        )
        
        if not existing_member or len(existing_member) == 0:
            raise ValueError(f"班级成员不存在: {member_id}")
        
        # 执行移除
        result = self.db_manager.execute_query(
            "DELETE FROM class_members WHERE id = ?",
            (member_id,)
        )
        
        return result is not None
    
    def add_class_subject(self, subject_data: ClassSubjectCreate) -> ClassSubjectResponse:
        """添加班级科目
        
        Args:
            subject_data: 班级科目创建数据
            
        Returns:
            ClassSubjectResponse: 创建的班级科目响应
        """
        logger.info(f"添加班级科目: 班级ID={subject_data.class_id}, 科目ID={subject_data.subject_id}")
        
        # 检查班级科目是否已存在
        existing_subject = self.db_manager.execute_query(
            """
            SELECT * FROM class_subjects 
            WHERE class_id = ? AND subject_id = ?
            """,
            (subject_data.class_id, subject_data.subject_id)
        )
        
        if existing_subject and len(existing_subject) > 0:
            raise ValueError("科目已添加到班级中")
        
        # 创建班级科目
        result = self.db_manager.execute_query(
            """
            INSERT INTO class_subjects (id, class_id, subject_id, teacher_id, 
            start_date, end_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subject_data.id,
                subject_data.class_id,
                subject_data.subject_id,
                subject_data.teacher_id,
                subject_data.start_date,
                subject_data.end_date,
                subject_data.created_at,
                subject_data.updated_at
            )
        )
        
        if result is None:
            raise Exception("添加班级科目失败")
        
        # 获取科目信息
        subject_info = self.db_manager.execute_query(
            "SELECT name, description, full_score FROM subjects WHERE id = ?",
            (subject_data.subject_id,)
        )
        
        subject = None
        if subject_info and len(subject_info) > 0:
            subject = {
                "id": subject_data.subject_id,
                "name": subject_info[0][0],
                "description": subject_info[0][1],
                "full_score": subject_info[0][2]
            }
        
        # 返回班级科目响应
        return ClassSubjectResponse(
            id=subject_data.id,
            class_id=subject_data.class_id,
            subject_id=subject_data.subject_id,
            teacher_id=subject_data.teacher_id,
            start_date=subject_data.start_date,
            end_date=subject_data.end_date,
            subject=subject,
            created_at=subject_data.created_at,
            updated_at=subject_data.updated_at
        )
    
    def get_class_subjects(self, class_id: str, page: int = 1, limit: int = 10) -> PaginatedClassSubjects:
        """获取班级科目列表
        
        Args:
            class_id: 班级ID
            page: 当前页码
            limit: 每页数量
            
        Returns:
            PaginatedClassSubjects: 分页班级科目列表
        """
        logger.info(f"获取班级科目列表: 班级ID={class_id}, 页码={page}, 每页数量={limit}")
        
        # 构建查询
        offset = (page - 1) * limit
        results = self.db_manager.execute_query(
            """
            SELECT cs.*, s.name, s.description, s.full_score 
            FROM class_subjects cs
            JOIN subjects s ON cs.subject_id = s.id
            WHERE cs.class_id = ?
            ORDER BY s.name ASC
            LIMIT ? OFFSET ?
            """,
            (class_id, limit, offset)
        )
        
        # 构建班级科目列表
        subjects = []
        for subject_data in results:
            subject = {
                "id": subject_data[2],
                "name": subject_data[8],
                "description": subject_data[9],
                "full_score": subject_data[10]
            }
            
            subjects.append(ClassSubjectResponse(
                id=subject_data[0],
                class_id=subject_data[1],
                subject_id=subject_data[2],
                teacher_id=subject_data[3],
                start_date=subject_data[4],
                end_date=subject_data[5],
                subject=subject,
                created_at=subject_data[6],
                updated_at=subject_data[7]
            ))
        
        # 获取总数
        total_result = self.db_manager.execute_query(
            "SELECT COUNT(*) FROM class_subjects WHERE class_id = ?",
            (class_id,)
        )
        total = total_result[0][0] if total_result else 0
        
        # 计算总页数
        total_pages = (total + limit - 1) // limit
        
        return PaginatedClassSubjects(
            subjects=subjects,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    def analyze_class_performance(self, class_id: str, exam_id: str = None) -> ClassPerformance:
        """分析班级表现
        
        Args:
            class_id: 班级ID
            exam_id: 考试ID(可选)
            
        Returns:
            ClassPerformance: 班级表现分析
        """
        logger.info(f"分析班级表现: 班级ID={class_id}, 考试ID={exam_id}")
        
        # 获取班级信息
        class_info = self.get_class(class_id)
        if not class_info:
            raise ValueError(f"班级不存在: {class_id}")
        
        # 获取班级成员
        members = self.get_class_members(class_id, role="student")
        
        # 获取班级科目
        subjects = self.get_class_subjects(class_id)
        
        # 分析各科目表现
        subject_performances = {}
        
        for subject in subjects.subjects:
            # 获取科目成绩统计
            if exam_id:
                # 获取特定考试的成绩统计
                grade_service = __import__('services.grade_service', fromlist=['get_grade_service'])
                grade_service_instance = grade_service.get_grade_service()
                
                statistics = grade_service_instance.analyze_grade_statistics(exam_id, subject.subject_id)
                
                subject_performances[subject.subject_id] = {
                    "subject_name": subject.subject.name,
                    "average_score": statistics.average_score,
                    "highest_score": statistics.highest_score,
                    "lowest_score": statistics.lowest_score,
                    "median_score": statistics.median_score,
                    "standard_deviation": statistics.standard_deviation,
                    "grade_distribution": statistics.grade_distribution
                }
        
        # 生成班级表现总结
        performance_summary = self._generate_performance_summary(
            class_name=class_info.name,
            subject_performances=subject_performances,
            total_students=members.total
        )
        
        return ClassPerformance(
            class_id=class_id,
            class_name=class_info.name,
            total_students=members.total,
            subject_performances=subject_performances,
            performance_summary=performance_summary,
            analyzed_at=datetime.datetime.now()
        )
    
    def _generate_performance_summary(self, class_name: str, subject_performances: Dict[str, Dict[str, Any]], 
                                    total_students: int) -> str:
        """使用大模型生成班级表现总结
        
        Args:
            class_name: 班级名称
            subject_performances: 各科目表现数据
            total_students: 学生总数
            
        Returns:
            str: 班级表现总结文本
        """
        logger.info(f"为班级生成表现总结: {class_name}")
        
        # 构建提示词
        prompt = f"""
        作为一名教育专家，请根据以下班级的成绩数据，生成一份班级表现总结报告。
        
        班级名称: {class_name}
        学生总数: {total_students}
        各科目表现数据: {subject_performances}
        
        请提供以下内容:
        1. 班级整体表现评估
        2. 各科目具体分析（优势科目和需要改进的科目）
        3. 针对班级整体的教学建议
        4. 提升班级整体成绩的方法和策略
        
        请使用专业但易于理解的语言，避免使用过于复杂的术语。
        """
        
        try:
            # 调用大模型
            result = self.llm_client.generate(prompt)
            return result
            
        except Exception as e:
            logger.error(f"生成班级表现总结失败: {str(e)}")
            return f"{class_name}的整体表现良好，各科目成绩分布合理。建议针对不同科目的特点，制定有针对性的教学计划，帮助学生提升成绩。"


# 创建全局班级服务实例
_global_class_service = ClassService()

def get_class_service() -> ClassService:
    """获取全局班级服务实例
    
    Returns:
        ClassService: 班级服务实例
    """
    return _global_class_service