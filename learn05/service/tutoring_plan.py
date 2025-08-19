#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅导方案生成模块
提供基于学生数据的个性化辅导方案生成功能
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import random

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from database import (
    get_db, 
    Student, 
    Grade, 
    Subject, 
    Class, 
    User,
    TutoringPlan,
    TeachingResource,
    LearningStatus
)
from grade_management import GradeAnalyzer
from llm_client import get_llm_client, LLMServiceClient


class TutoringPlanGenerator:
    """辅导方案生成器"""
    
    def __init__(self, db: Session = None, llm_client: LLMServiceClient = None):
        self.db = db or next(get_db())
        self.llm_client = llm_client or get_llm_client()
        self.grade_analyzer = GradeAnalyzer(self.db)
    
    def generate_tutoring_plan(self, student_id: int, subject_id: int = None, duration_days: int = 30, plan_type: str = "comprehensive") -> TutoringPlan:
        """生成个性化辅导方案"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise ValueError(f"学生不存在: {student_id}")
        
        # 获取学生成绩分析
        if subject_id:
            grade_analysis = self.grade_analyzer.analyze_student_grades(student_id, subject_id)
            progress_analysis = self.grade_analyzer.get_progress_analysis(student_id, subject_id)
            subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
            if not subject:
                raise ValueError(f"科目不存在: {subject_id}")
            subject_name = subject.subject_name
        else:
            grade_analysis = self.grade_analyzer.analyze_student_grades(student_id)
            progress_analysis = None
            subject_name = "全科"
        
        # 如果没有成绩数据，生成基础方案
        if not grade_analysis.get("has_data", False):
            return self._generate_basic_plan(student_id, subject_id)
        
        # 构建提示词
        prompt = self._build_tutoring_plan_prompt(
            student=student,
            grade_analysis=grade_analysis,
            progress_analysis=progress_analysis,
            duration_days=duration_days,
            plan_type=plan_type,
            subject_name=subject_name
        )
        
        # 调用大模型生成辅导方案
        try:
            # 使用LLM客户端生成方案
            response = self.llm_client.generate_text(prompt)
            
            if not response or not response.get('content'):
                raise Exception("LLM生成失败: 返回内容为空")
            
            plan_content = response['content']
                
        except Exception as e:
            # 如果大模型调用失败，使用备用方案生成器
            plan_content = self._generate_fallback_plan(student_id, subject_id, grade_analysis)
        
        # 保存辅导方案
        plan = TutoringPlan(
            student_id=student_id,
            plan_content=plan_content,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        return plan
    
    def _build_tutoring_plan_prompt(self, student: Student, grade_analysis: Dict, progress_analysis: Optional[Dict], duration_days: int, plan_type: str, subject_name: str) -> str:
        """构建辅导方案提示词"""
        # 学生基本信息
        basic_info = f"学生信息：姓名={student.student_name}，性别={student.gender}，出生日期={student.date_of_birth}，班级={student.class_.class_name}"
        
        # 成绩分析信息
        score_info = f"\n成绩分析：平均分={grade_analysis.get('average_score', 0)}，最高分={grade_analysis.get('highest_score', 0)}，最低分={grade_analysis.get('lowest_score', 0)}"
        
        # 科目统计信息
        if grade_analysis.get('subject_statistics'):
            subject_stats = grade_analysis['subject_statistics']
            subject_info = "\n科目表现：\n"
            for subject_name, stats in subject_stats.items():
                subject_info += f"- {subject_name}：平均分={stats.get('avg', 0)}，考试次数={stats.get('count', 0)}\n"
        else:
            subject_info = ""
        
        # 进步趋势
        trend_info = ""
        if progress_analysis and progress_analysis.get('trend'):
            trend_info = f"\n进步趋势：{progress_analysis['trend']}，斜率={progress_analysis.get('trend_slope', 0)}"
        
        # 方案要求
        plan_request = f"\n请为该学生生成一份{duration_days}天的{subject_name}辅导方案，类型为{plan_type}。方案应包含以下内容：\n"
        plan_request += "1. 学习目标（具体、可衡量）\n"
        plan_request += "2. 学习内容（重点难点分析、知识点清单）\n"
        plan_request += "3. 学习计划（每天的学习任务、时间安排）\n"
        plan_request += "4. 学习方法建议\n"
        plan_request += "5. 练习和测试安排\n"
        plan_request += "6. 家长或教师配合建议\n"
        
        # 组合提示词
        prompt = basic_info + score_info + subject_info + trend_info + plan_request
        
        return prompt
    
    def _generate_basic_plan(self, student_id: int, subject_id: int = None) -> TutoringPlan:
        """生成基础辅导方案（当没有成绩数据时）"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        
        # 确定科目信息
        if subject_id:
            subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
            subject_name = subject.subject_name if subject else "未知科目"
        else:
            subject_name = "全科"
        
        # 生成基础方案内容
        basic_plan = f"# {student.student_name}的{subject_name}基础辅导方案\n\n"
        basic_plan += "## 学习目标\n"
        basic_plan += "1. 建立对该科目的基本认知和兴趣\n"
        basic_plan += "2. 掌握基础知识点和学习方法\n"
        basic_plan += "3. 培养良好的学习习惯\n\n"
        
        basic_plan += "## 学习内容\n"
        basic_plan += "1. 课程基本概念和原理\n"
        basic_plan += "2. 基础题型练习\n"
        basic_plan += "3. 学习方法指导\n\n"
        
        basic_plan += "## 学习计划\n"
        basic_plan += "1. 第一周：基础知识学习\n"
        basic_plan += "2. 第二周：基础练习巩固\n"
        basic_plan += "3. 第三周：知识点串联和应用\n"
        basic_plan += "4. 第四周：总结和测试\n\n"
        
        basic_plan += "## 学习建议\n"
        basic_plan += "1. 保持每天固定的学习时间\n"
        basic_plan += "2. 做好学习笔记\n"
        basic_plan += "3. 及时解决学习中的问题\n"
        basic_plan += "4. 定期复习和总结\n"
        
        # 保存基础方案
        plan = TutoringPlan(
            student_id=student_id,
            plan_content=basic_plan,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        return plan
    
    def _generate_fallback_plan(self, student_id: int, subject_id: int = None, grade_analysis: Dict = None) -> str:
        """生成备用辅导方案（当大模型调用失败时）"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        
        # 确定科目信息
        if subject_id:
            subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
            subject_name = subject.subject_name if subject else "未知科目"
        else:
            subject_name = "全科"
        
        # 生成备用方案内容
        fallback_plan = f"# {student.student_name}的{subject_name}辅导方案\n\n"
        
        # 添加成绩分析信息
        if grade_analysis and grade_analysis.get('has_data'):
            fallback_plan += "## 成绩分析\n"
            fallback_plan += f"平均分：{grade_analysis.get('average_score', 0)}\n"
            fallback_plan += f"最高分：{grade_analysis.get('highest_score', 0)}\n"
            fallback_plan += f"最低分：{grade_analysis.get('lowest_score', 0)}\n\n"
        
        # 添加学习目标
        fallback_plan += "## 学习目标\n"
        avg_score = grade_analysis.get('average_score', 0) if grade_analysis else 0
        if avg_score < 60:
            fallback_plan += "1. 提高基础知识点的掌握程度\n"
            fallback_plan += "2. 确保能够完成基础题目的解答\n"
            fallback_plan += "3. 建立学习信心和兴趣\n"
        elif avg_score < 70:
            fallback_plan += "1. 巩固基础知识，提高解题能力\n"
            fallback_plan += "2. 学习中等难度题目的解题方法\n"
            fallback_plan += "3. 培养良好的学习习惯\n"
        elif avg_score < 80:
            fallback_plan += "1. 进一步提高知识点的掌握程度\n"
            fallback_plan += "2. 学习较高难度题目的解题方法\n"
            fallback_plan += "3. 提高学习效率和解题速度\n"
        else:
            fallback_plan += "1. 深入理解知识点，形成知识体系\n"
            fallback_plan += "2. 挑战高难度题目，培养创新思维\n"
            fallback_plan += "3. 拓展知识面，提高综合应用能力\n"
        fallback_plan += "\n"
        
        # 添加学习计划
        fallback_plan += "## 学习计划\n"
        fallback_plan += "1. 每周学习5天，每天学习1-2小时\n"
        fallback_plan += "2. 每天安排15分钟复习前一天的内容\n"
        fallback_plan += "3. 每周安排一次小结和测试\n"
        fallback_plan += "4. 每月安排一次大总结\n\n"
        
        # 添加学习建议
        fallback_plan += "## 学习建议\n"
        fallback_plan += "1. 制定详细的学习计划，合理安排时间\n"
        fallback_plan += "2. 做好学习笔记，定期复习\n"
        fallback_plan += "3. 多做练习题，巩固知识点\n"
        fallback_plan += "4. 遇到问题及时向老师或同学请教\n"
        fallback_plan += "5. 保持良好的心态，相信自己能够取得进步\n"
        
        return fallback_plan
    
    def get_tutoring_plan(self, plan_id: int) -> Optional[TutoringPlan]:
        """获取辅导方案"""
        return self.db.query(TutoringPlan).filter(TutoringPlan.plan_id == plan_id).first()
    
    def update_tutoring_plan(self, plan_id: int, **kwargs) -> Optional[TutoringPlan]:
        """更新辅导方案"""
        plan = self.get_tutoring_plan(plan_id)
        if not plan:
            return None
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(plan, key) and key != "plan_id":
                setattr(plan, key, value)
        
        # 更新时间
        plan.updated_at = datetime.now()
        
        # 保存到数据库
        self.db.commit()
        self.db.refresh(plan)
        
        return plan
    
    def delete_tutoring_plan(self, plan_id: int) -> bool:
        """删除辅导方案"""
        plan = self.get_tutoring_plan(plan_id)
        if not plan:
            return False
        
        # 从数据库删除
        self.db.delete(plan)
        self.db.commit()
        
        return True
    
    def get_student_plans(self, student_id: int, subject_id: int = None, status: str = None, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """获取学生的辅导方案列表"""
        # 构建查询
        query = self.db.query(TutoringPlan).filter(TutoringPlan.student_id == student_id)
        
        # 按科目过滤
        if subject_id:
            query = query.filter(TutoringPlan.subject_id == subject_id)
        
        # 按状态过滤
        if status:
            query = query.filter(TutoringPlan.status == status)
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        plans = query.order_by(desc(TutoringPlan.created_at)).offset(offset).limit(page_size).all()
        
        # 构建结果
        results = []
        for plan in plans:
            # 获取科目名称
            subject_name = "全科"
            if plan.subject_id:
                subject = self.db.query(Subject).filter(Subject.subject_id == plan.subject_id).first()
                if subject:
                    subject_name = subject.subject_name
            
            results.append({
                "plan_id": plan.plan_id,
                "student_id": plan.student_id,
                "subject_id": plan.subject_id,
                "subject_name": subject_name,
                "plan_type": plan.plan_type,
                "duration_days": plan.duration_days,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
                "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
                "status": plan.status
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "data": results
        }
    
    def activate_plan(self, plan_id: int) -> Optional[TutoringPlan]:
        """激活辅导方案"""
        # 更新方案状态
        plan = self.update_tutoring_plan(plan_id, status="active", activated_at=datetime.now())
        
        # 创建学习状态记录
        if plan:
            learning_status = LearningStatus(
                student_id=plan.student_id,
                plan_id=plan.plan_id,
                status="in_progress",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.db.add(learning_status)
            self.db.commit()
        
        return plan
    
    def complete_plan(self, plan_id: int, completion_rate: float = 100.0, feedback: str = None) -> Optional[TutoringPlan]:
        """完成辅导方案"""
        # 更新方案状态
        plan = self.update_tutoring_plan(
            plan_id,
            status="completed",
            completed_at=datetime.now(),
            completion_rate=completion_rate,
            feedback=feedback
        )
        
        # 更新学习状态记录
        if plan:
            learning_status = self.db.query(LearningStatus).filter(
                LearningStatus.plan_id == plan_id
            ).first()
            
            if learning_status:
                learning_status.status = "completed"
                learning_status.completion_rate = completion_rate
                learning_status.feedback = feedback
                learning_status.updated_at = datetime.now()
                
                self.db.commit()
        
        return plan


class LearningResourceManager:
    """学习资源管理器"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def add_learning_resource(self, resource_name: str, resource_type: str, content: str, subject_id: int = None, grade_level: str = None, tags: List[str] = None) -> TeachingResource:
        """添加学习资源"""
        # 创建学习资源
        resource = TeachingResource(
            resource_name=resource_name,
            resource_type=resource_type,
            content=content,
            subject_id=subject_id,
            grade_level=grade_level,
            tags=json.dumps(tags) if tags else "[]",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            views=0
        )
        
        # 保存到数据库
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        
        return resource
    
    def get_learning_resource(self, resource_id: int) -> Optional[TeachingResource]:
        """获取学习资源"""
        return self.db.query(TeachingResource).filter(TeachingResource.resource_id == resource_id).first()
    
    def update_learning_resource(self, resource_id: int, **kwargs) -> Optional[TeachingResource]:
        """更新学习资源"""
        resource = self.get_learning_resource(resource_id)
        if not resource:
            return None
        
        # 更新字段
        for key, value in kwargs.items():
            if key == "tags" and value:
                # 标签需要JSON序列化
                resource.tags = json.dumps(value)
            elif hasattr(resource, key) and key != "resource_id":
                setattr(resource, key, value)
        
        # 更新时间
        resource.updated_at = datetime.now()
        
        # 保存到数据库
        self.db.commit()
        self.db.refresh(resource)
        
        return resource
    
    def delete_learning_resource(self, resource_id: int) -> bool:
        """删除学习资源"""
        resource = self.get_learning_resource(resource_id)
        if not resource:
            return False
        
        # 从数据库删除
        self.db.delete(resource)
        self.db.commit()
        
        return True
    
    def get_learning_resources(self, subject_id: int = None, resource_type: str = None, grade_level: str = None, tags: List[str] = None, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """获取学习资源列表"""
        # 构建查询
        query = self.db.query(TeachingResource)
        
        # 按科目过滤
        if subject_id:
            query = query.filter(TeachingResource.subject_id == subject_id)
        
        # 按资源类型过滤
        if resource_type:
            query = query.filter(TeachingResource.resource_type == resource_type)
        
        # 按年级过滤
        if grade_level:
            query = query.filter(TeachingResource.grade_level == grade_level)
        
        # 按标签过滤
        if tags:
            for tag in tags:
                query = query.filter(TeachingResource.tags.contains(tag))
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        resources = query.order_by(desc(TeachingResource.created_at)).offset(offset).limit(page_size).all()
        
        # 构建结果
        results = []
        for resource in resources:
            results.append({
                "resource_id": resource.resource_id,
                "resource_name": resource.resource_name,
                "resource_type": resource.resource_type,
                "subject_id": resource.subject_id,
                "grade_level": resource.grade_level,
                "tags": json.loads(resource.tags),
                "created_at": resource.created_at.isoformat() if resource.created_at else None,
                "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
                "views": resource.views
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "data": results
        }
    
    def search_learning_resources(self, keyword: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """搜索学习资源"""
        # 构建查询
        query = self.db.query(TeachingResource).filter(
            (TeachingResource.resource_name.ilike(f"%{keyword}%")) | 
            (TeachingResource.content.ilike(f"%{keyword}%")) | 
            (TeachingResource.tags.ilike(f"%{keyword}%"))
        )
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        resources = query.order_by(desc(TeachingResource.created_at)).offset(offset).limit(page_size).all()
        
        # 构建结果
        results = []
        for resource in resources:
            results.append({
                "resource_id": resource.resource_id,
                "resource_name": resource.resource_name,
                "resource_type": resource.resource_type,
                "subject_id": resource.subject_id,
                "grade_level": resource.grade_level,
                "tags": json.loads(resource.tags),
                "created_at": resource.created_at.isoformat() if resource.created_at else None,
                "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
                "views": resource.views
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "data": results
        }
    
    def recommend_resources_for_student(self, student_id: int, subject_id: int = None, limit: int = 5) -> List[Dict[str, Any]]:
        """为学生推荐学习资源"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return []
        
        # 获取学生的成绩分析，找出薄弱科目
        analyzer = GradeAnalyzer(self.db)
        grade_analysis = analyzer.analyze_student_grades(student_id)
        
        # 确定要推荐的科目
        recommended_subject_ids = []
        if subject_id:
            recommended_subject_ids.append(subject_id)
        elif grade_analysis.get('subject_statistics'):
            # 找出平均分最低的2个科目
            subject_stats = grade_analysis['subject_statistics']
            sorted_subjects = sorted(subject_stats.items(), key=lambda x: x[1].get('avg', 100))
            for subject_name, stats in sorted_subjects[:2]:
                subject = self.db.query(Subject).filter(Subject.subject_name == subject_name).first()
                if subject:
                    recommended_subject_ids.append(subject.subject_id)
        
        # 查询推荐的学习资源
        resources = []
        if recommended_subject_ids:
            query = self.db.query(TeachingResource).filter(
                TeachingResource.subject_id.in_(recommended_subject_ids)
            ).order_by(desc(TeachingResource.views)).limit(limit)
            resources = query.all()
        
        # 如果没有足够的资源，随机推荐一些
        if len(resources) < limit:
            remaining = limit - len(resources)
            random_query = self.db.query(TeachingResource)
            if subject_id:
                random_query = random_query.filter(TeachingResource.subject_id == subject_id)
            random_query = random_query.order_by(self.db.func.random()).limit(remaining)
            random_resources = random_query.all()
            resources.extend(random_resources)
        
        # 构建结果
        results = []
        for resource in resources:
            results.append({
                "resource_id": resource.resource_id,
                "resource_name": resource.resource_name,
                "resource_type": resource.resource_type,
                "subject_id": resource.subject_id,
                "grade_level": resource.grade_level,
                "tags": json.loads(resource.tags),
                "created_at": resource.created_at.isoformat() if resource.created_at else None,
                "views": resource.views
            })
        
        return results


# 便捷函数
def get_student_learning_status(student_id: int, db: Session = None) -> Dict[str, Any]:
    """获取学生的学习状态"""
    db = db or next(get_db())
    
    # 获取学生正在进行的学习计划
    active_plans = db.query(TutoringPlan).filter(
        TutoringPlan.student_id == student_id,
        TutoringPlan.status == "active"
    ).all()
    
    # 获取学习状态记录
    learning_statuses = db.query(LearningStatus).filter(
        LearningStatus.student_id == student_id
    ).order_by(desc(LearningStatus.updated_at)).all()
    
    # 构建结果
    active_plan_details = []
    for plan in active_plans:
        # 获取科目名称
        subject_name = "全科"
        if plan.subject_id:
            subject = db.query(Subject).filter(Subject.subject_id == plan.subject_id).first()
            if subject:
                subject_name = subject.subject_name
        
        # 获取学习状态
        status = db.query(LearningStatus).filter(
            LearningStatus.plan_id == plan.plan_id
        ).first()
        
        active_plan_details.append({
            "plan_id": plan.plan_id,
            "subject_id": plan.subject_id,
            "subject_name": subject_name,
            "plan_type": plan.plan_type,
            "duration_days": plan.duration_days,
            "activated_at": plan.activated_at.isoformat() if plan.activated_at else None,
            "completion_rate": status.completion_rate if status else 0,
            "status": status.status if status else "not_started"
        })
    
    # 计算总体学习情况
    total_plans = db.query(TutoringPlan).filter(TutoringPlan.student_id == student_id).count()
    completed_plans = db.query(TutoringPlan).filter(
        TutoringPlan.student_id == student_id,
        TutoringPlan.status == "completed"
    ).count()
    
    return {
        "student_id": student_id,
        "active_plans": active_plan_details,
        "total_plans": total_plans,
        "completed_plans": completed_plans,
        "learning_statuses": [{
            "status_id": status.status_id,
            "plan_id": status.plan_id,
            "status": status.status,
            "completion_rate": status.completion_rate,
            "feedback": status.feedback,
            "created_at": status.created_at.isoformat() if status.created_at else None,
            "updated_at": status.updated_at.isoformat() if status.updated_at else None
        } for status in learning_statuses]
    }

def update_learning_progress(plan_id: int, progress: float, feedback: str = None, db: Session = None) -> LearningStatus:
    """更新学习进度"""
    db = db or next(get_db())
    
    # 获取学习状态记录
    status = db.query(LearningStatus).filter(LearningStatus.plan_id == plan_id).first()
    
    if not status:
        # 创建新的学习状态记录
        plan = db.query(TutoringPlan).filter(TutoringPlan.plan_id == plan_id).first()
        if not plan:
            raise ValueError(f"辅导方案不存在: {plan_id}")
        
        status = LearningStatus(
            student_id=plan.student_id,
            plan_id=plan_id,
            status="in_progress",
            completion_rate=progress,
            feedback=feedback,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(status)
    else:
        # 更新学习状态
        status.completion_rate = progress
        status.feedback = feedback
        status.updated_at = datetime.now()
        
        # 更新方案状态
        if progress >= 100:
            status.status = "completed"
            plan = db.query(TutoringPlan).filter(TutoringPlan.plan_id == plan_id).first()
            if plan:
                plan.status = "completed"
                plan.completed_at = datetime.now()
    
    db.commit()
    db.refresh(status)
    
    return status