#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成绩管理模块
提供成绩的录入、查询、更新、删除等功能，以及成绩分析功能
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import io
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from database import (
    get_db, 
    Grade, 
    Student, 
    Subject, 
    Class, 
    get_grades_by_student_id, 
    get_grades_by_class_id_and_subject_id,
    get_students_by_class_id,
    get_subject_by_id
)
from llm_client import get_llm_client, analyze_grades_simple


class GradeManager:
    """成绩管理类"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def add_grade(self, student_id: int, subject_id: int, exam_date: str, score: float, exam_type: str) -> Grade:
        """添加成绩记录"""
        # 验证参数
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            raise ValueError("分数必须在0-100之间")
        
        # 检查学生和科目是否存在
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
        
        if not student:
            raise ValueError(f"学生不存在: {student_id}")
        if not subject:
            raise ValueError(f"科目不存在: {subject_id}")
        
        # 创建成绩记录
        grade = Grade(
            student_id=student_id,
            subject_id=subject_id,
            exam_date=exam_date,
            score=float(score),
            exam_type=exam_type
        )
        
        # 保存到数据库
        self.db.add(grade)
        self.db.commit()
        self.db.refresh(grade)
        
        return grade
    
    def get_grade(self, grade_id: int) -> Optional[Grade]:
        """获取成绩记录"""
        return self.db.query(Grade).filter(Grade.grade_id == grade_id).first()
    
    def update_grade(self, grade_id: int, **kwargs) -> Optional[Grade]:
        """更新成绩记录"""
        grade = self.get_grade(grade_id)
        if not grade:
            return None
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(grade, key):
                setattr(grade, key, value)
        
        # 保存到数据库
        self.db.commit()
        self.db.refresh(grade)
        
        return grade
    
    def delete_grade(self, grade_id: int) -> bool:
        """删除成绩记录"""
        grade = self.get_grade(grade_id)
        if not grade:
            return False
        
        # 从数据库删除
        self.db.delete(grade)
        self.db.commit()
        
        return True
    
    def get_student_grades(self, student_id: int, subject_id: int = None, exam_type: str = None) -> List[Grade]:
        """获取学生的成绩记录"""
        query = self.db.query(Grade).filter(Grade.student_id == student_id)
        
        if subject_id:
            query = query.filter(Grade.subject_id == subject_id)
        
        if exam_type:
            query = query.filter(Grade.exam_type == exam_type)
        
        return query.order_by(desc(Grade.exam_date)).all()
    
    def get_class_grades(self, class_id: int, subject_id: int = None, exam_type: str = None) -> List[Dict]:
        """获取班级的成绩记录"""
        # 获取班级学生
        students = get_students_by_class_id(self.db, class_id)
        
        # 收集成绩数据
        results = []
        for student in students:
            grades = self.get_student_grades(student.student_id, subject_id, exam_type)
            for grade in grades:
                results.append({
                    "student_id": student.student_id,
                    "student_name": student.student_name,
                    "subject_id": grade.subject_id,
                    "subject_name": get_subject_by_id(self.db, grade.subject_id).subject_name,
                    "exam_date": grade.exam_date,
                    "score": grade.score,
                    "exam_type": grade.exam_type
                })
        
        return results
    
    def import_grades_from_excel(self, file_content: bytes) -> Dict[str, Any]:
        """从Excel文件导入成绩"""
        try:
            # 读取Excel文件
            df = pd.read_excel(io.BytesIO(file_content))
            
            # 验证表头
            required_columns = ["student_id", "subject_id", "exam_date", "score", "exam_type"]
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"Excel文件缺少必要的列: {', '.join(missing)}")
            
            # 准备导入结果
            result = {
                "total": len(df),
                "success": 0,
                "failed": 0,
                "errors": []
            }
            
            # 导入数据
            for index, row in df.iterrows():
                try:
                    self.add_grade(
                        student_id=int(row["student_id"]),
                        subject_id=int(row["subject_id"]),
                        exam_date=str(row["exam_date"]),
                        score=float(row["score"]),
                        exam_type=str(row["exam_type"])
                    )
                    result["success"] += 1
                except Exception as e:
                    result["failed"] += 1
                    result["errors"].append({
                        "row": index + 2,  # Excel行号从1开始，标题占一行
                        "error": str(e)
                    })
            
            return result
        except Exception as e:
            raise ValueError(f"导入Excel文件失败: {str(e)}")
    
    def export_grades_to_excel(self, grades: List[Dict]) -> bytes:
        """导出成绩到Excel文件"""
        # 转换为DataFrame
        df = pd.DataFrame(grades)
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="成绩数据")
        
        output.seek(0)
        return output.getvalue()


class GradeAnalyzer:
    """成绩分析类"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.llm_client = get_llm_client()
    
    def analyze_student_grades(self, student_id: int, subject_id: int = None, exam_type: str = None) -> Dict[str, Any]:
        """分析学生成绩"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise ValueError(f"学生不存在: {student_id}")
        
        # 获取成绩数据
        grades = get_grades_by_student_id(self.db, student_id)
        
        # 过滤数据
        if subject_id:
            grades = [g for g in grades if g.subject_id == subject_id]
        if exam_type:
            grades = [g for g in grades if g.exam_type == exam_type]
        
        if not grades:
            return {
                "student_id": student_id,
                "student_name": student.student_name,
                "has_data": False,
                "analysis": "暂无成绩数据"
            }
        
        # 计算统计指标
        scores = [g.score for g in grades]
        avg_score = np.mean(scores)
        max_score = np.max(scores)
        min_score = np.min(scores)
        median_score = np.median(scores)
        std_score = np.std(scores)
        
        # 按科目分组统计
        subject_stats = {}
        for grade in grades:
            subject = get_subject_by_id(self.db, grade.subject_id)
            subject_name = subject.subject_name
            if subject_name not in subject_stats:
                subject_stats[subject_name] = []
            subject_stats[subject_name].append(grade.score)
        
        # 计算每个科目的统计指标
        for subject_name, subject_scores in subject_stats.items():
            subject_stats[subject_name] = {
                "avg": np.mean(subject_scores),
                "max": np.max(subject_scores),
                "min": np.min(subject_scores),
                "count": len(subject_scores)
            }
        
        # 生成进步趋势（最近几次考试）
        grades_sorted = sorted(grades, key=lambda x: x.exam_date)
        trend = [{
            "exam_date": g.exam_date,
            "score": g.score,
            "subject_name": get_subject_by_id(self.db, g.subject_id).subject_name,
            "exam_type": g.exam_type
        } for g in grades_sorted]
        
        return {
            "student_id": student_id,
            "student_name": student.student_name,
            "has_data": True,
            "total_exams": len(grades),
            "average_score": round(avg_score, 2),
            "highest_score": round(max_score, 2),
            "lowest_score": round(min_score, 2),
            "median_score": round(median_score, 2),
            "standard_deviation": round(std_score, 2),
            "subject_statistics": subject_stats,
            "trend": trend
        }
    
    def analyze_class_grades(self, class_id: int, subject_id: int = None, exam_type: str = None) -> Dict[str, Any]:
        """分析班级成绩"""
        # 获取班级信息
        class_ = self.db.query(Class).filter(Class.class_id == class_id).first()
        if not class_:
            raise ValueError(f"班级不存在: {class_id}")
        
        # 获取班级学生
        students = get_students_by_class_id(self.db, class_id)
        
        # 收集所有学生的成绩数据
        all_scores = []
        student_scores = {}
        
        for student in students:
            grades = get_grades_by_student_id(self.db, student.student_id)
            
            # 过滤数据
            if subject_id:
                grades = [g for g in grades if g.subject_id == subject_id]
            if exam_type:
                grades = [g for g in grades if g.exam_type == exam_type]
            
            # 计算学生平均分
            if grades:
                scores = [g.score for g in grades]
                avg_score = np.mean(scores)
                all_scores.append(avg_score)
                student_scores[student.student_name] = round(avg_score, 2)
        
        if not all_scores:
            return {
                "class_id": class_id,
                "class_name": class_.class_name,
                "has_data": False,
                "analysis": "暂无成绩数据"
            }
        
        # 计算班级统计指标
        avg_score = np.mean(all_scores)
        max_score = np.max(all_scores)
        min_score = np.min(all_scores)
        median_score = np.median(all_scores)
        std_score = np.std(all_scores)
        
        # 计算分数分布
        bins = [0, 60, 70, 80, 90, 100]
        labels = ["不及格", "及格", "中等", "良好", "优秀"]
        distribution = pd.cut(all_scores, bins=bins, labels=labels, include_lowest=True).value_counts().to_dict()
        
        # 按分数排序
        sorted_students = sorted(student_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 获取班级名次
        ranking = {name: i + 1 for i, (name, score) in enumerate(sorted_students)}
        
        return {
            "class_id": class_id,
            "class_name": class_.class_name,
            "has_data": True,
            "total_students": len(students),
            "tested_students": len(all_scores),
            "average_score": round(avg_score, 2),
            "highest_score": round(max_score, 2),
            "lowest_score": round(min_score, 2),
            "median_score": round(median_score, 2),
            "standard_deviation": round(std_score, 2),
            "score_distribution": distribution,
            "student_rankings": ranking
        }
    
    def get_subject_comparison(self, class_id: int, exam_type: str = None) -> Dict[str, Any]:
        """比较班级各科目的成绩"""
        # 获取班级信息
        class_ = self.db.query(Class).filter(Class.class_id == class_id).first()
        if not class_:
            raise ValueError(f"班级不存在: {class_id}")
        
        # 获取所有科目
        subjects = self.db.query(Subject).all()
        
        # 比较各科目的成绩
        comparison = {}
        for subject in subjects:
            # 获取该科目的成绩
            grades = get_grades_by_class_id_and_subject_id(self.db, class_id, subject.subject_id, exam_type)
            
            if grades:
                scores = [g.score for g in grades]
                comparison[subject.subject_name] = {
                    "subject_id": subject.subject_id,
                    "average_score": round(np.mean(scores), 2),
                    "highest_score": round(np.max(scores), 2),
                    "lowest_score": round(np.min(scores), 2),
                    "student_count": len(scores)
                }
        
        return {
            "class_id": class_id,
            "class_name": class_.class_name,
            "subject_comparison": comparison
        }
    
    def get_progress_analysis(self, student_id: int, subject_id: int) -> Dict[str, Any]:
        """分析学生在某科目的进步情况"""
        # 获取学生和科目信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        subject = get_subject_by_id(self.db, subject_id)
        
        if not student:
            raise ValueError(f"学生不存在: {student_id}")
        if not subject:
            raise ValueError(f"科目不存在: {subject_id}")
        
        # 获取该科目的成绩
        grades = self.db.query(Grade).filter(
            Grade.student_id == student_id,
            Grade.subject_id == subject_id
        ).order_by(Grade.exam_date).all()
        
        if not grades:
            return {
                "student_id": student_id,
                "student_name": student.student_name,
                "subject_id": subject_id,
                "subject_name": subject.subject_name,
                "has_data": False,
                "analysis": "暂无该科目的成绩数据"
            }
        
        # 计算进步趋势
        scores = [g.score for g in grades]
        dates = [g.exam_date for g in grades]
        exam_types = [g.exam_type for g in grades]
        
        # 计算线性回归，判断进步趋势
        if len(scores) >= 2:
            x = np.arange(len(scores))
            slope, intercept = np.polyfit(x, scores, 1)
            trend = "上升" if slope > 0.5 else "下降" if slope < -0.5 else "平稳"
        else:
            slope = 0
            trend = "数据不足"
        
        # 计算其他统计指标
        avg_score = np.mean(scores)
        max_score = np.max(scores)
        min_score = np.min(scores)
        
        return {
            "student_id": student_id,
            "student_name": student.student_name,
            "subject_id": subject_id,
            "subject_name": subject.subject_name,
            "has_data": True,
            "total_exams": len(grades),
            "average_score": round(avg_score, 2),
            "highest_score": round(max_score, 2),
            "lowest_score": round(min_score, 2),
            "trend": trend,
            "trend_slope": round(slope, 4),
            "exam_history": [{
                "exam_date": date,
                "score": score,
                "exam_type": exam_type
            } for date, score, exam_type in zip(dates, scores, exam_types)]
        }
    
    def get_class_ranking(self, student_id: int, class_id: int, subject_id: int = None, exam_type: str = None) -> Dict[str, Any]:
        """获取学生在班级中的排名"""
        # 获取学生和班级信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        class_ = self.db.query(Class).filter(Class.class_id == class_id).first()
        
        if not student:
            raise ValueError(f"学生不存在: {student_id}")
        if not class_:
            raise ValueError(f"班级不存在: {class_id}")
        
        # 获取班级学生
        students = get_students_by_class_id(self.db, class_id)
        
        # 计算每个学生的平均分
        student_scores = {}
        for s in students:
            grades = get_grades_by_student_id(self.db, s.student_id)
            
            # 过滤数据
            if subject_id:
                grades = [g for g in grades if g.subject_id == subject_id]
            if exam_type:
                grades = [g for g in grades if g.exam_type == exam_type]
            
            # 计算平均分
            if grades:
                scores = [g.score for g in grades]
                avg_score = np.mean(scores)
                student_scores[s.student_id] = {
                    "name": s.student_name,
                    "score": round(avg_score, 2)
                }
        
        # 按分数排序
        sorted_students = sorted(student_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        # 获取学生排名
        ranking = None
        student_score = None
        for i, (s_id, data) in enumerate(sorted_students):
            if s_id == student_id:
                ranking = i + 1
                student_score = data["score"]
                break
        
        if ranking is None:
            return {
                "student_id": student_id,
                "student_name": student.student_name,
                "class_id": class_id,
                "class_name": class_.class_name,
                "has_data": False,
                "analysis": "暂无该学生的成绩数据"
            }
        
        return {
            "student_id": student_id,
            "student_name": student.student_name,
            "class_id": class_id,
            "class_name": class_.class_name,
            "has_data": True,
            "ranking": ranking,
            "total_students": len(students),
            "score": student_score,
            "top_percentage": round((ranking / len(students)) * 100, 2)
        }
    
    async def analyze_student_performance_with_llm(self, student_id: int, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """使用LLM分析学生成绩表现"""
        # 获取学生成绩数据
        grades = get_grades_by_student_id(self.db, student_id)
        
        # 过滤日期范围
        if start_date:
            grades = [g for g in grades if g.exam_date >= start_date]
        if end_date:
            grades = [g for g in grades if g.exam_date <= end_date]
        
        if not grades:
            return {
                "student_id": student_id,
                "has_data": False,
                "analysis": "暂无成绩数据"
            }
        
        # 准备成绩数据
        grade_data = [{
            "subject_id": g.subject_id,
            "subject_name": get_subject_by_id(self.db, g.subject_id).subject_name,
            "score": g.score,
            "exam_date": g.exam_date,
            "exam_type": g.exam_type
        } for g in grades]
        
        try:
            # 使用简化的LLM分析接口
            analysis_result = await analyze_grades_simple(grade_data)
            
            return {
                "student_id": student_id,
                "analysis": analysis_result,
                "grade_data": grade_data,
                "trend_summary": self._extract_trend_summary(analysis_result)
            }
        except Exception as e:
            return {
                "student_id": student_id,
                "has_data": True,
                "analysis": f"LLM分析失败: {str(e)}",
                "grade_data": grade_data
            }
    
    def _extract_trend_summary(self, analysis_text: str) -> str:
        """从分析结果中提取趋势摘要"""
        # 简单的关键词提取
        if "上升" in analysis_text or "提高" in analysis_text or "进步" in analysis_text:
            return "上升趋势"
        elif "下降" in analysis_text or "退步" in analysis_text or "降低" in analysis_text:
            return "下降趋势"
        elif "稳定" in analysis_text or "平稳" in analysis_text:
            return "稳定趋势"
        else:
            return "趋势不明确"


# 便捷函数
def calculate_gpa(scores: List[float], credits: List[int]) -> float:
    """计算GPA"""
    if len(scores) != len(credits):
        raise ValueError("分数和学分数量不匹配")
    
    weighted_sum = sum(score * credit for score, credit in zip(scores, credits))
    total_credits = sum(credits)
    
    if total_credits == 0:
        return 0
    
    return weighted_sum / total_credits


def convert_score_to_grade(score: float) -> str:
    """将分数转换为等级"""
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"


def get_subject_difficulty(subject_id: int, db: Session = None) -> Dict[str, Any]:
    """分析科目难度"""
    db = db or next(get_db())
    
    # 获取该科目的所有成绩
    grades = db.query(Grade).filter(Grade.subject_id == subject_id).all()
    
    if not grades:
        return {
            "subject_id": subject_id,
            "has_data": False,
            "difficulty": "未知"
        }
    
    # 计算平均分和标准差
    scores = [g.score for g in grades]
    avg_score = np.mean(scores)
    std_score = np.std(scores)
    
    # 判断难度
    if avg_score < 60:
        difficulty = "非常难"
    elif avg_score < 70:
        difficulty = "较难"
    elif avg_score < 80:
        difficulty = "中等"
    elif avg_score < 90:
        difficulty = "较易"
    else:
        difficulty = "非常易"
    
    return {
        "subject_id": subject_id,
        "has_data": True,
        "average_score": round(avg_score, 2),
        "standard_deviation": round(std_score, 2),
        "difficulty": difficulty,
        "sample_size": len(scores)
    }


def get_grade_statistics(class_id: int = None, subject_id: int = None, db: Session = None) -> Dict[str, Any]:
    """获取成绩统计信息"""
    db = db or next(get_db())
    analyzer = GradeAnalyzer(db)
    
    if class_id:
        return analyzer.analyze_class_grades(class_id, subject_id)
    else:
        # 返回全校统计
        query = db.query(Grade)
        if subject_id:
            query = query.filter(Grade.subject_id == subject_id)
        
        grades = query.all()
        if not grades:
            return {"has_data": False, "message": "暂无成绩数据"}
        
        scores = [grade.score for grade in grades]
        return {
            "has_data": True,
            "total_count": len(scores),
            "average_score": np.mean(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "pass_rate": len([s for s in scores if s >= 60]) / len(scores) * 100
        }


def get_student_grade_analysis(student_name: str, db: Session = None) -> Dict[str, Any]:
    """获取学生成绩分析"""
    db = db or next(get_db())
    
    # 根据学生姓名查找学生
    student = db.query(Student).filter(Student.student_name == student_name).first()
    if not student:
        return {"has_data": False, "message": f"学生 {student_name} 不存在"}
    
    analyzer = GradeAnalyzer(db)
    return analyzer.analyze_student_grades(student.student_id)