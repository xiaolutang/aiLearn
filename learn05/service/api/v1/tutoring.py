# -*- coding: utf-8 -*-
"""
辅导方案API路由

本模块提供辅导方案相关的API接口。
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from database import get_db, User
from models.response import APIResponse, ResponseBuilder, PaginatedResponse
from middleware.exception_handler import BusinessException, AuthenticationException, ValidationException
from auth import get_current_user
from tutoring_plan import TutoringPlanGenerator, LearningResourceManager, get_student_learning_status
from pydantic import BaseModel, validator
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class TutoringPlanRequest(BaseModel):
    """辅导方案请求模型"""
    student_name: str
    subjects: List[str]
    focus_areas: Optional[List[str]] = None
    difficulty_level: str = "medium"
    duration_weeks: int = 4
    
    @validator('student_name')
    def validate_student_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('学生姓名不能为空')
        return v.strip()
    
    @validator('subjects')
    def validate_subjects(cls, v):
        if not v:
            raise ValueError('科目列表不能为空')
        return v
    
    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        allowed_levels = ['easy', 'medium', 'hard']
        if v not in allowed_levels:
            raise ValueError(f'难度级别必须是以下之一: {", ".join(allowed_levels)}')
        return v
    
    @validator('duration_weeks')
    def validate_duration_weeks(cls, v):
        if v < 1 or v > 52:
            raise ValueError('辅导周数必须在1-52之间')
        return v


class TutoringPlanResponse(BaseModel):
    """辅导方案响应模型"""
    id: int
    student_name: str
    subjects: List[str]
    plan_content: Dict[str, Any]
    difficulty_level: str
    duration_weeks: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


@router.post("/plans", response_model=APIResponse[TutoringPlanResponse])
async def create_tutoring_plan(
    request: Request,
    plan_request: TutoringPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成辅导方案"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以生成辅导方案")
        
        logger.info(f"生成辅导方案 - 用户: {current_user.username}, 学生: {plan_request.student_name}")
        
        # 创建辅导方案生成器
        plan_generator = TutoringPlanGenerator(db=db)
        
        # 查找学生ID（这里简化处理，实际应该通过学生姓名查找）
        from database import Student
        student = db.query(Student).filter(Student.student_name == plan_request.student_name).first()
        if not student:
            raise ValidationException(f"未找到学生: {plan_request.student_name}")
        
        # 生成辅导方案（暂时不指定科目ID，生成全科方案）
        plan = plan_generator.generate_tutoring_plan(
            student_id=student.student_id,
            duration_days=plan_request.duration_weeks * 7,
            plan_type="comprehensive"
        )
        
        # 构造响应数据
        response_data = {
            "id": plan.id,
            "student_name": plan_request.student_name,
            "subjects": plan_request.subjects,
            "plan_content": {"content": plan.plan_content},
            "difficulty_level": plan_request.difficulty_level,
            "duration_weeks": plan_request.duration_weeks,
            "status": "draft",
            "created_at": plan.created_at,
            "updated_at": plan.updated_at
        }
        
        return ResponseBuilder.success(
            response_data,
            "辅导方案生成成功"
        )
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"生成辅导方案异常: {e}")
        raise BusinessException("生成辅导方案失败")


@router.get("/plans", response_model=APIResponse[PaginatedResponse[TutoringPlanResponse]])
async def get_tutoring_plans_endpoint(
    request: Request,
    student_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取辅导方案列表"""
    try:
        # 构建查询条件
        filters = {}
        if student_name:
            filters['student_name'] = student_name
        if status:
            filters['status'] = status
        
        # 权限控制：学生只能查看自己的方案
        if current_user.role == 'student':
            filters['student_name'] = current_user.full_name
        
        # 查询辅导方案
        plans, total_count = get_tutoring_plans(db, filters, page, page_size)
        
        plan_responses = [TutoringPlanResponse.from_orm(plan) for plan in plans]
        paginated_response = PaginatedResponse(
            items=plan_responses,
            total=total_count,
            page=page,
            page_size=page_size,
            pages=(total_count + page_size - 1) // page_size
        )
        
        return ResponseBuilder.success(paginated_response, "获取辅导方案列表成功")
        
    except Exception as e:
        logger.error(f"获取辅导方案列表异常: {e}")
        raise BusinessException("获取辅导方案列表失败")