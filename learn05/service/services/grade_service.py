# -*- coding: utf-8 -*-
"""
成绩管理服务模块
提供成绩相关的业务逻辑
"""

import logging
from typing import Dict, List, Optional, Any, Union
import datetime
import pandas as pd
import numpy as np
import io
from sqlalchemy import text

from models.grade import (
    GradeCreate, GradeUpdate, GradeResponse, GradeStatistics, 
    PaginatedGrades, ExamCreate, ExamResponse, SubjectCreate, 
    SubjectResponse, PaginatedExams, PaginatedSubjects,
    StudentPerformance, CustomReportRequest, calculate_gpa, get_grade_level
)
from database import DatabaseManager
from llm_integration import llm_router
from models.class_model import ClassPerformance
from config.core_config import get_config, get_db_url
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from llm.factory import get_llm_client
from exceptions import ValidationException, BusinessException

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取配置
config = get_config()


class GradeService:
    """成绩管理服务类"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """初始化成绩管理服务
        
        Args:
            db_manager: 数据库管理器实例(可选，默认创建新的)
        """
        self.db_manager = db_manager or DatabaseManager(get_db_url())
        self.llm_client = get_llm_client("openai")
    
    def create_grade(self, grade_data: GradeCreate) -> GradeResponse:
        """创建成绩记录
        
        Args:
            grade_data: 成绩创建数据
            
        Returns:
            GradeResponse: 创建的成绩响应
        """
        logger.info(f"创建成绩记录: 学生ID={grade_data.student_id}, 考试ID={grade_data.exam_id}, 科目ID={grade_data.subject_id}")
        
        # 检查成绩是否已存在
        existing_grade = self.get_grade(grade_data.student_id, grade_data.exam_id, grade_data.subject_id)
        if existing_grade:
            raise ValueError(f"成绩记录已存在")
        
        # 计算GPA和等级
        gpa = calculate_gpa(grade_data.score, grade_data.full_score)
        grade_level = get_grade_level(grade_data.score, grade_data.full_score)
        
        # 创建成绩记录
        result = self.db_manager.execute_query(
            """
            INSERT INTO grades (id, student_id, exam_id, subject_id, score, full_score, 
            gpa, grade_level, comment, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                grade_data.id,
                grade_data.student_id,
                grade_data.exam_id,
                grade_data.subject_id,
                grade_data.score,
                grade_data.full_score,
                gpa,
                grade_level,
                grade_data.comment,
                grade_data.created_at,
                grade_data.updated_at
            )
        )
        
        if result is None:
            raise Exception("创建成绩记录失败")
        
        # 返回成绩响应
        return GradeResponse(
            id=grade_data.id,
            student_id=grade_data.student_id,
            exam_id=grade_data.exam_id,
            subject_id=grade_data.subject_id,
            score=grade_data.score,
            full_score=grade_data.full_score,
            gpa=gpa,
            grade_level=grade_level,
            comment=grade_data.comment,
            created_at=grade_data.created_at,
            updated_at=grade_data.updated_at
        )
    
    def get_grade(self, student_id: str, exam_id: str, subject_id: str) -> Optional[GradeResponse]:
        """获取单个成绩记录
        
        Args:
            student_id: 学生ID
            exam_id: 考试ID
            subject_id: 科目ID
            
        Returns:
            Optional[GradeResponse]: 成绩响应，如果不存在则返回None
        """
        logger.debug(f"获取成绩记录: 学生ID={student_id}, 考试ID={exam_id}, 科目ID={subject_id}")
        
        result = self.db_manager.execute_query(
            """
            SELECT * FROM grades 
            WHERE student_id = ? AND exam_id = ? AND subject_id = ?
            """,
            (student_id, exam_id, subject_id)
        )
        
        if not result or len(result) == 0:
            return None
        
        grade_data = result[0]
        return GradeResponse(
            id=grade_data[0],
            student_id=grade_data[1],
            exam_id=grade_data[2],
            subject_id=grade_data[3],
            score=grade_data[4],
            full_score=grade_data[5],
            gpa=grade_data[6],
            grade_level=grade_data[7],
            comment=grade_data[8],
            created_at=grade_data[9],
            updated_at=grade_data[10]
        )
    
    def update_grade(self, grade_id: str, grade_data: GradeUpdate) -> GradeResponse:
        """更新成绩记录
        
        Args:
            grade_id: 成绩ID
            grade_data: 成绩更新数据
            
        Returns:
            GradeResponse: 更新后的成绩响应
        """
        logger.info(f"更新成绩记录: ID={grade_id}")
        
        # 检查成绩是否存在
        existing_grade = self.db_manager.execute_query(
            "SELECT * FROM grades WHERE id = ?",
            (grade_id,)
        )
        
        if not existing_grade or len(existing_grade) == 0:
            raise ValueError(f"成绩记录不存在: {grade_id}")
        
        # 构建更新字段和参数
        update_fields = []
        params = []
        
        # 获取现有成绩数据
        current_grade = existing_grade[0]
        
        # 计算GPA和等级（如果分数或满分有更新）
        new_score = grade_data.score if grade_data.score is not None else current_grade[4]
        new_full_score = grade_data.full_score if grade_data.full_score is not None else current_grade[5]
        
        if grade_data.score is not None or grade_data.full_score is not None:
            new_gpa = calculate_gpa(new_score, new_full_score)
            new_grade_level = get_grade_level(new_score, new_full_score)
            update_fields.append("gpa = ?")
            params.append(new_gpa)
            update_fields.append("grade_level = ?")
            params.append(new_grade_level)
        
        if grade_data.score is not None:
            update_fields.append("score = ?")
            params.append(grade_data.score)
        
        if grade_data.full_score is not None:
            update_fields.append("full_score = ?")
            params.append(grade_data.full_score)
        
        if grade_data.comment is not None:
            update_fields.append("comment = ?")
            params.append(grade_data.comment)
        
        # 添加更新时间和成绩ID
        update_fields.append("updated_at = ?")
        params.append(datetime.datetime.now())
        params.append(grade_id)
        
        # 执行更新
        if update_fields:
            query = f"UPDATE grades SET {', '.join(update_fields)} WHERE id = ?"
            self.db_manager.execute_query(query, tuple(params))
        
        # 返回更新后的成绩
        updated_grade = self.db_manager.execute_query(
            "SELECT * FROM grades WHERE id = ?",
            (grade_id,)
        )
        
        if not updated_grade or len(updated_grade) == 0:
            raise Exception("更新成绩记录失败")
        
        grade_data = updated_grade[0]
        return GradeResponse(
            id=grade_data[0],
            student_id=grade_data[1],
            exam_id=grade_data[2],
            subject_id=grade_data[3],
            score=grade_data[4],
            full_score=grade_data[5],
            gpa=grade_data[6],
            grade_level=grade_data[7],
            comment=grade_data[8],
            created_at=grade_data[9],
            updated_at=grade_data[10]
        )
    
    def delete_grade(self, grade_id: str) -> bool:
        """删除成绩记录
        
        Args:
            grade_id: 成绩ID
            
        Returns:
            bool: 是否删除成功
        """
        logger.info(f"删除成绩记录: ID={grade_id}")
        
        # 检查成绩是否存在
        existing_grade = self.db_manager.execute_query(
            "SELECT * FROM grades WHERE id = ?",
            (grade_id,)
        )
        
        if not existing_grade or len(existing_grade) == 0:
            raise ValueError(f"成绩记录不存在: {grade_id}")
        
        # 执行删除
        result = self.db_manager.execute_query(
            "DELETE FROM grades WHERE id = ?",
            (grade_id,)
        )
        
        return result is not None
    
    def get_student_grades(self, student_id: str, page: int = 1, limit: int = 10) -> PaginatedGrades:
        """获取学生的所有成绩
        
        Args:
            student_id: 学生ID
            page: 当前页码
            limit: 每页数量
            
        Returns:
            PaginatedGrades: 分页成绩列表
        """
        logger.info(f"获取学生成绩: 学生ID={student_id}, 页码={page}, 每页数量={limit}")
        
        # 执行查询
        offset = (page - 1) * limit
        results = self.db_manager.execute_query(
            """
            SELECT * FROM grades 
            WHERE student_id = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
            """,
            (student_id, limit, offset)
        )
        
        # 构建成绩列表
        grades = []
        for grade_data in results:
            grades.append(GradeResponse(
                id=grade_data[0],
                student_id=grade_data[1],
                exam_id=grade_data[2],
                subject_id=grade_data[3],
                score=grade_data[4],
                full_score=grade_data[5],
                gpa=grade_data[6],
                grade_level=grade_data[7],
                comment=grade_data[8],
                created_at=grade_data[9],
                updated_at=grade_data[10]
            ))
        
        # 获取总数
        total_result = self.db_manager.execute_query(
            "SELECT COUNT(*) FROM grades WHERE student_id = ?",
            (student_id,)
        )
        total = total_result[0][0] if total_result else 0
        
        # 计算总页数
        total_pages = (total + limit - 1) // limit
        
        return PaginatedGrades(
            grades=grades,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    def get_exam_grades(self, exam_id: str, page: int = 1, limit: int = 10) -> PaginatedGrades:
        """获取考试的所有成绩
        
        Args:
            exam_id: 考试ID
            page: 当前页码
            limit: 每页数量
            
        Returns:
            PaginatedGrades: 分页成绩列表
        """
        logger.info(f"获取考试成绩: 考试ID={exam_id}, 页码={page}, 每页数量={limit}")
        
        # 执行查询
        offset = (page - 1) * limit
        results = self.db_manager.execute_query(
            """
            SELECT * FROM grades 
            WHERE exam_id = ? 
            ORDER BY student_id ASC 
            LIMIT ? OFFSET ?
            """,
            (exam_id, limit, offset)
        )
        
        # 构建成绩列表
        grades = []
        for grade_data in results:
            grades.append(GradeResponse(
                id=grade_data[0],
                student_id=grade_data[1],
                exam_id=grade_data[2],
                subject_id=grade_data[3],
                score=grade_data[4],
                full_score=grade_data[5],
                gpa=grade_data[6],
                grade_level=grade_data[7],
                comment=grade_data[8],
                created_at=grade_data[9],
                updated_at=grade_data[10]
            ))
        
        # 获取总数
        total_result = self.db_manager.execute_query(
            "SELECT COUNT(*) FROM grades WHERE exam_id = ?",
            (exam_id,)
        )
        total = total_result[0][0] if total_result else 0
        
        # 计算总页数
        total_pages = (total + limit - 1) // limit
        
        return PaginatedGrades(
            grades=grades,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    def get_class_grades(self, class_id: str, exam_id: str, subject_id: str = None) -> List[GradeResponse]:
        """获取班级在某考试中的成绩
        
        Args:
            class_id: 班级ID
            exam_id: 考试ID
            subject_id: 科目ID(可选)
            
        Returns:
            List[GradeResponse]: 成绩列表
        """
        logger.info(f"获取班级成绩: 班级ID={class_id}, 考试ID={exam_id}, 科目ID={subject_id}")
        
        # 构建查询
        query_parts = [
            """
            SELECT g.* FROM grades g
            JOIN class_members cm ON g.student_id = cm.student_id
            WHERE cm.class_id = ? AND g.exam_id = ?
            """
        ]
        params = [class_id, exam_id]
        
        if subject_id:
            query_parts.append("AND g.subject_id = ?")
            params.append(subject_id)
        
        query_parts.append("ORDER BY g.student_id ASC")
        
        query = " ".join(query_parts)
        results = self.db_manager.execute_query(query, tuple(params))
        
        # 构建成绩列表
        grades = []
        for grade_data in results:
            grades.append(GradeResponse(
                id=grade_data[0],
                student_id=grade_data[1],
                exam_id=grade_data[2],
                subject_id=grade_data[3],
                score=grade_data[4],
                full_score=grade_data[5],
                gpa=grade_data[6],
                grade_level=grade_data[7],
                comment=grade_data[8],
                created_at=grade_data[9],
                updated_at=grade_data[10]
            ))
        
        return grades
    
    def analyze_grade_statistics(self, exam_id: str, subject_id: str = None) -> GradeStatistics:
        """分析成绩统计数据
        
        Args:
            exam_id: 考试ID
            subject_id: 科目ID(可选)
            
        Returns:
            GradeStatistics: 成绩统计信息
        """
        logger.info(f"分析成绩统计: 考试ID={exam_id}, 科目ID={subject_id}")
        
        # 构建查询
        query_parts = ["SELECT score, full_score FROM grades WHERE exam_id = ?"]
        params = [exam_id]
        
        if subject_id:
            query_parts.append("AND subject_id = ?")
            params.append(subject_id)
        
        query = " ".join(query_parts)
        results = self.db_manager.execute_query(query, tuple(params))
        
        if not results or len(results) == 0:
            return GradeStatistics(
                total_students=0,
                average_score=0,
                highest_score=0,
                lowest_score=0,
                median_score=0,
                standard_deviation=0,
                grade_distribution={},
                full_score=100
            )
        
        # 计算统计数据
        scores = [r[0] for r in results]
        full_score = results[0][1]  # 假设所有成绩的满分相同
        
        # 计算平均分
        average_score = sum(scores) / len(scores)
        
        # 计算最高分和最低分
        highest_score = max(scores)
        lowest_score = min(scores)
        
        # 计算中位数
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        if n % 2 == 0:
            median_score = (sorted_scores[n//2 - 1] + sorted_scores[n//2]) / 2
        else:
            median_score = sorted_scores[n//2]
        
        # 计算标准差
        if n > 1:
            standard_deviation = np.std(scores, ddof=1)
        else:
            standard_deviation = 0
        
        # 计算等级分布
        grade_distribution = {}
        for score in scores:
            grade_level = get_grade_level(score, full_score)
            grade_distribution[grade_level] = grade_distribution.get(grade_level, 0) + 1
        
        return GradeStatistics(
            total_students=len(scores),
            average_score=average_score,
            highest_score=highest_score,
            lowest_score=lowest_score,
            median_score=median_score,
            standard_deviation=standard_deviation,
            grade_distribution=grade_distribution,
            full_score=full_score
        )
    
    def analyze_student_performance(self, student_id: str, subject_id: str = None) -> StudentPerformance:
        """分析学生表现
        
        Args:
            student_id: 学生ID
            subject_id: 科目ID(可选)
            
        Returns:
            StudentPerformance: 学生表现分析
        """
        logger.info(f"分析学生表现: 学生ID={student_id}, 科目ID={subject_id}")
        
        # 构建查询
        query_parts = ["SELECT score, full_score, exam_id, subject_id FROM grades WHERE student_id = ?"]
        params = [student_id]
        
        if subject_id:
            query_parts.append("AND subject_id = ?")
            params.append(subject_id)
        
        query_parts.append("ORDER BY created_at ASC")
        
        query = " ".join(query_parts)
        results = self.db_manager.execute_query(query, tuple(params))
        
        if not results or len(results) == 0:
            return StudentPerformance(
                student_id=student_id,
                total_exams=0,
                average_gpa=0,
                performance_trend=[],
                strengths=[],
                weaknesses=[],
                improvement_suggestions=[],
                personalized_guidance=""
            )
        
        # 计算总考试数
        total_exams = len(results)
        
        # 计算平均GPA
        total_gpa = sum(calculate_gpa(r[0], r[1]) for r in results)
        average_gpa = total_gpa / total_exams if total_exams > 0 else 0
        
        # 分析表现趋势
        performance_trend = []
        subject_scores = {}
        
        for result in results:
            score, full_score, exam_id, subject_id = result
            gpa = calculate_gpa(score, full_score)
            
            # 获取考试信息
            exam_info = self.db_manager.execute_query(
                "SELECT name, date FROM exams WHERE id = ?",
                (exam_id,)
            )
            exam_name = exam_info[0][0] if exam_info and len(exam_info) > 0 else f"考试 {exam_id}"
            exam_date = exam_info[0][1] if exam_info and len(exam_info) > 0 else datetime.datetime.now()
            
            performance_trend.append({
                "exam_id": exam_id,
                "exam_name": exam_name,
                "exam_date": exam_date,
                "subject_id": subject_id,
                "score": score,
                "gpa": gpa,
                "grade_level": get_grade_level(score, full_score)
            })
            
            # 按科目统计
            if subject_id not in subject_scores:
                subject_scores[subject_id] = []
            subject_scores[subject_id].append((score, full_score))
        
        # 分析优势和劣势科目
        strengths = []
        weaknesses = []
        
        for subject_id, scores in subject_scores.items():
            # 获取科目名称
            subject_info = self.db_manager.execute_query(
                "SELECT name FROM subjects WHERE id = ?",
                (subject_id,)
            )
            subject_name = subject_info[0][0] if subject_info and len(subject_info) > 0 else f"科目 {subject_id}"
            
            # 计算该科目的平均分数百分比
            avg_percentage = sum(s[0]/s[1] for s in scores) / len(scores) if len(scores) > 0 else 0
            
            if avg_percentage >= 0.85:
                strengths.append(subject_name)
            elif avg_percentage < 0.60:
                weaknesses.append(subject_name)
        
        # 生成个性化辅导建议
        improvement_suggestions = []
        if weaknesses:
            improvement_suggestions.append(f"加强{'、'.join(weaknesses)}科目的学习")
        
        if strengths:
            improvement_suggestions.append(f"保持{'、'.join(strengths)}科目的优势")
        
        # 使用大模型生成个性化指导
        personalized_guidance = self._generate_personalized_guidance(
            student_id=student_id,
            strengths=strengths,
            weaknesses=weaknesses,
            performance_trend=performance_trend
        )
        
        return StudentPerformance(
            student_id=student_id,
            total_exams=total_exams,
            average_gpa=average_gpa,
            performance_trend=performance_trend,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=improvement_suggestions,
            personalized_guidance=personalized_guidance
        )
    
    def import_grades_from_excel(self, file_content: bytes) -> Dict[str, Any]:
        """从Excel导入成绩
        
        Args:
            file_content: Excel文件内容
            
        Returns:
            Dict[str, Any]: 导入结果统计
        """
        logger.info("从Excel导入成绩")
        
        try:
            # 读取Excel文件
            df = pd.read_excel(io.BytesIO(file_content))
            
            # 验证必要列
            required_columns = ['student_id', 'exam_id', 'subject_id', 'score', 'full_score']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Excel文件缺少必要的列: {', '.join(missing_columns)}")
            
            # 准备统计数据
            total_records = len(df)
            imported_count = 0
            skipped_count = 0
            error_count = 0
            errors = []
            
            # 导入每条成绩记录
            for index, row in df.iterrows():
                try:
                    # 检查成绩是否已存在
                    existing_grade = self.get_grade(
                        student_id=row['student_id'],
                        exam_id=row['exam_id'],
                        subject_id=row['subject_id']
                    )
                    
                    if existing_grade:
                        skipped_count += 1
                        continue
                    
                    # 创建成绩记录
                    grade_create = GradeCreate(
                        id=str(index + 1),  # 使用行索引作为ID
                        student_id=row['student_id'],
                        exam_id=row['exam_id'],
                        subject_id=row['subject_id'],
                        score=float(row['score']),
                        full_score=float(row['full_score']),
                        comment=row.get('comment', '')
                    )
                    
                    self.create_grade(grade_create)
                    imported_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append({
                        "row": index + 2,  # Excel行号从2开始
                        "error": str(e)
                    })
            
            return {
                "total_records": total_records,
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "error_count": error_count,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"从Excel导入成绩失败: {str(e)}")
            raise Exception(f"从Excel导入成绩失败: {str(e)}")
    
    def _generate_personalized_guidance(self, student_id: str, strengths: List[str], 
                                      weaknesses: List[str], performance_trend: List[Dict[str, Any]]) -> str:
        """使用大模型生成个性化指导
        
        Args:
            student_id: 学生ID
            strengths: 优势科目列表
            weaknesses: 劣势科目列表
            performance_trend: 表现趋势
            
        Returns:
            str: 个性化指导文本
        """
        logger.info(f"为学生生成个性化指导: {student_id}")
        
        # 构建提示词
        prompt = f"""
        作为一名教育专家，请根据以下学生的成绩数据，生成一份个性化的学习指导建议。
        
        学生ID: {student_id}
        优势科目: {', '.join(strengths) if strengths else '无明显优势科目'}
        劣势科目: {', '.join(weaknesses) if weaknesses else '无明显劣势科目'}
        表现趋势: {performance_trend}
        
        请提供以下内容:
        1. 整体学习情况评估
        2. 各科目具体分析
        3. 针对性的学习建议
        4. 提升成绩的方法和策略
        
        请使用简明扼要的语言，避免使用过于专业的术语。
        """
        
        try:
            # 调用大模型
            result = self.llm_client.generate(prompt)
            return result
            
        except Exception as e:
            logger.error(f"生成个性化指导失败: {str(e)}")
            return "根据您的成绩数据，建议您保持优势科目，加强劣势科目的学习。具体学习方法可咨询老师或查看相关学习资料。"
    
    def export_grades_to_excel(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """导出成绩数据到Excel格式"""
        try:
            # 构建查询
            query_parts = [
                """
                SELECT g.id, s.name as student_name, g.student_id, sub.name as subject_name,
                       g.score, g.full_score, e.name as exam_name, e.date as exam_date,
                       g.comment, c.name as class_name
                FROM grades g
                LEFT JOIN students s ON g.student_id = s.id
                LEFT JOIN subjects sub ON g.subject_id = sub.id
                LEFT JOIN exams e ON g.exam_id = e.id
                LEFT JOIN class_members cm ON g.student_id = cm.student_id
                LEFT JOIN classes c ON cm.class_id = c.id
                WHERE 1=1
                """
            ]
            params = []
            
            # 应用过滤条件
            if 'student_name' in filters and filters['student_name']:
                query_parts.append("AND s.name LIKE ?")
                params.append(f"%{filters['student_name']}%")
            
            if 'class_name' in filters and filters['class_name']:
                query_parts.append("AND c.name LIKE ?")
                params.append(f"%{filters['class_name']}%")
            
            if 'subject_id' in filters and filters['subject_id']:
                query_parts.append("AND g.subject_id = ?")
                params.append(filters['subject_id'])
            
            if 'exam_id' in filters and filters['exam_id']:
                query_parts.append("AND g.exam_id = ?")
                params.append(filters['exam_id'])
            
            if 'start_date' in filters and filters['start_date']:
                query_parts.append("AND e.date >= ?")
                params.append(filters['start_date'])
            
            if 'end_date' in filters and filters['end_date']:
                query_parts.append("AND e.date <= ?")
                params.append(filters['end_date'])
            
            query_parts.append("ORDER BY e.date DESC, s.name ASC")
            
            query = " ".join(query_parts)
            results = self.db_manager.execute_query(query, tuple(params))
            
            # 转换为DataFrame
            data = []
            for result in results:
                score_percentage = (result[4] / result[5] * 100) if result[5] > 0 else 0
                data.append({
                    '成绩ID': result[0],
                    '学生姓名': result[1] or '',
                    '学号': result[2],
                    '班级': result[9] or '',
                    '科目': result[3] or '',
                    '成绩': result[4],
                    '总分': result[5],
                    '得分率': f"{score_percentage:.1f}%",
                    '考试名称': result[6] or '',
                    '考试日期': result[7].strftime('%Y-%m-%d') if result[7] else '',
                    '评语': result[8] or ''
                })
            
            return pd.DataFrame(data)
        
        except Exception as e:
            logger.error(f"导出成绩数据失败: {str(e)}")
            raise BusinessException(f"导出成绩数据失败: {str(e)}")
    
    def validate_grade_data(self, grade_data: GradeCreate) -> Dict[str, Any]:
        """验证成绩数据"""
        try:
            validation_errors = []
            warnings = []
            
            # 验证学生是否存在
            student_result = self.db_manager.execute_query(
                "SELECT id, name FROM students WHERE id = ?",
                (grade_data.student_id,)
            )
            student_exists = bool(student_result and len(student_result) > 0)
            student_name = student_result[0][1] if student_exists else None
            
            if not student_exists:
                validation_errors.append(f"学生ID '{grade_data.student_id}' 不存在")
            
            # 验证科目是否存在
            subject_result = self.db_manager.execute_query(
                "SELECT id, name FROM subjects WHERE id = ?",
                (grade_data.subject_id,)
            )
            subject_exists = bool(subject_result and len(subject_result) > 0)
            subject_name = subject_result[0][1] if subject_exists else None
            
            if not subject_exists:
                validation_errors.append(f"科目ID '{grade_data.subject_id}' 不存在")
            
            # 验证考试是否存在
            exam_result = self.db_manager.execute_query(
                "SELECT id, name FROM exams WHERE id = ?",
                (grade_data.exam_id,)
            )
            exam_exists = bool(exam_result and len(exam_result) > 0)
            exam_name = exam_result[0][1] if exam_exists else None
            
            if not exam_exists:
                validation_errors.append(f"考试ID '{grade_data.exam_id}' 不存在")
            
            # 验证成绩范围
            if grade_data.score < 0:
                validation_errors.append("成绩不能为负数")
            
            if grade_data.score > grade_data.full_score:
                validation_errors.append(f"成绩 {grade_data.score} 不能超过总分 {grade_data.full_score}")
            
            # 检查是否存在重复记录
            existing_grade = self.get_grade(
                grade_data.student_id,
                grade_data.exam_id,
                grade_data.subject_id
            )
            
            if existing_grade:
                warnings.append("存在相同学生、科目和考试的成绩记录")
            
            # 检查成绩是否异常（过高或过低）
            if grade_data.full_score > 0:
                score_percentage = grade_data.score / grade_data.full_score
                if score_percentage > 0.98:
                    warnings.append("成绩接近满分，请确认是否正确")
                elif score_percentage < 0.3:
                    warnings.append("成绩较低，请确认是否正确")
            
            return {
                "is_valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "warnings": warnings,
                "student_exists": student_exists,
                "subject_exists": subject_exists,
                "exam_exists": exam_exists,
                "student_name": student_name,
                "subject_name": subject_name,
                "exam_name": exam_name
            }
        
        except Exception as e:
            logger.error(f"验证成绩数据失败: {str(e)}")
            raise BusinessException(f"验证成绩数据失败: {str(e)}")
    
    def generate_custom_report(self, report_request: CustomReportRequest) -> Dict[str, Any]:
        """生成自定义成绩报告"""
        try:
            report_data = {
                "report_type": report_request.report_type,
                "generated_at": datetime.datetime.now().isoformat(),
                "date_range": {
                    "start_date": report_request.start_date.isoformat() if report_request.start_date else None,
                    "end_date": report_request.end_date.isoformat() if report_request.end_date else None
                }
            }
            
            if report_request.report_type == "student_performance":
                # 学生表现报告
                if not report_request.student_id:
                    raise ValidationException("学生表现报告需要指定学生ID")
                
                student_performance = self.analyze_student_performance(
                    report_request.student_id,
                    report_request.subject_id
                )
                report_data["student_performance"] = student_performance
            
            elif report_request.report_type == "class_summary":
                # 班级总结报告
                if not report_request.class_id:
                    raise ValidationException("班级总结报告需要指定班级ID")
                
                # 获取班级成绩统计
                class_grades = self.get_class_grades(
                    report_request.class_id,
                    report_request.exam_id or "all",
                    report_request.subject_id
                )
                
                # 计算班级统计数据
                if class_grades:
                    scores = [grade.score for grade in class_grades]
                    report_data["class_summary"] = {
                        "total_students": len(scores),
                        "average_score": sum(scores) / len(scores),
                        "highest_score": max(scores),
                        "lowest_score": min(scores),
                        "grades": [grade.dict() for grade in class_grades]
                    }
                else:
                    report_data["class_summary"] = {
                        "total_students": 0,
                        "average_score": 0,
                        "highest_score": 0,
                        "lowest_score": 0,
                        "grades": []
                    }
            
            elif report_request.report_type == "subject_analysis":
                # 科目分析报告
                if not report_request.subject_id:
                    raise ValidationException("科目分析报告需要指定科目ID")
                
                # 获取科目统计数据
                subject_stats = self.analyze_grade_statistics(
                    report_request.exam_id or "all",
                    report_request.subject_id
                )
                report_data["subject_analysis"] = subject_stats.dict()
            
            else:
                raise ValidationException(f"不支持的报告类型: {report_request.report_type}")
            
            return report_data
        
        except ValidationException as e:
            raise e
        except Exception as e:
            logger.error(f"生成自定义报告失败: {str(e)}")
            raise BusinessException(f"生成自定义报告失败: {str(e)}")


# 创建全局成绩服务实例
_global_grade_service = GradeService()

def get_grade_service() -> GradeService:
    """获取全局成绩服务实例
    
    Returns:
        GradeService: 成绩服务实例
    """
    return _global_grade_service