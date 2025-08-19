# -*- coding: utf-8 -*-
"""
成绩管理API路由

本模块提供成绩管理相关的API接口。
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import pandas as pd
import io
import json
import httpx
import os
import time

from database import get_db, User, Grade, Student, Subject
from models.response import APIResponse, ResponseBuilder, PaginatedResponse
from middleware.exception_handler import (
    AuthenticationException,
    BusinessException,
    ResourceNotFoundException,
    ValidationException
)
from auth import get_current_user, role_required
from grade_management import (
    GradeManager,
    GradeAnalyzer,
    calculate_gpa,
    convert_score_to_grade,
    get_subject_difficulty,
    get_grade_statistics,
    get_student_grade_analysis
)
from pydantic import BaseModel, validator
from enum import Enum

logger = logging.getLogger(__name__)

router = APIRouter()

# AI服务集成客户端
class AIServiceClient:
    """AI服务集成客户端"""
    
    def __init__(self):
        self.base_url = os.getenv('AI_SERVICE_URL', 'http://localhost:8000/api/v1/ai-service')
        self.timeout = 30.0
    
    async def _make_request(self, method: str, endpoint: str, data: dict = None):
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if method.upper() == 'POST':
                response = await client.post(url, json=data, headers=headers)
            elif method.upper() == 'GET':
                response = await client.get(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
    
    async def analyze_grades(self, student_id: str, subject: str = None, time_range: str = "semester"):
        """成绩分析"""
        data = {
            'student_id': student_id,
            'subject': subject,
            'time_range': time_range
        }
        return await self._make_request('POST', '/grades/analyze', data)
    
    async def generate_guidance(self, student_id: str, analysis_data: dict):
        """生成个性化指导"""
        data = {
            'student_id': student_id,
            'analysis_data': analysis_data
        }
        return await self._make_request('POST', '/grades/generate-guidance', data)
    
    async def health_check(self):
        """健康检查"""
        try:
            return await self._make_request('GET', '/health')
        except Exception:
            return {'status': 'error', 'message': 'AI service unavailable'}

# 初始化AI服务客户端
ai_service_client = AIServiceClient()


def get_grades(db: Session, filters: dict, page: int, page_size: int):
    """查询成绩记录
    
    Args:
        db: 数据库会话
        filters: 查询过滤条件
        page: 页码
        page_size: 每页大小
        
    Returns:
        tuple: (成绩列表, 总数)
    """
    # 使用关联查询获取学生和科目信息
    query = db.query(Grade).join(Student).join(Subject)
    
    # 应用过滤条件
    if filters.get('student_name'):
        query = query.filter(Student.student_name.like(f"%{filters['student_name']}%"))
    if filters.get('student_id'):
        query = query.filter(Grade.student_id == filters['student_id'])
    if filters.get('subject'):
        query = query.filter(Subject.subject_name == filters['subject'])
    if filters.get('exam_type'):
        query = query.filter(Grade.exam_type == filters['exam_type'])
    if filters.get('score_min'):
        query = query.filter(Grade.score >= filters['score_min'])
    if filters.get('score_max'):
        query = query.filter(Grade.score <= filters['score_max'])
    if filters.get('exam_date_start'):
        query = query.filter(Grade.exam_date >= filters['exam_date_start'].strftime('%Y-%m-%d'))
    if filters.get('exam_date_end'):
        query = query.filter(Grade.exam_date <= filters['exam_date_end'].strftime('%Y-%m-%d'))
    
    # 获取总数
    total_count = query.count()
    
    # 分页查询
    offset = (page - 1) * page_size
    grades = query.offset(offset).limit(page_size).all()
    
    return grades, total_count


# 枚举类型
class SubjectType(str, Enum):
    """科目类型"""
    CHINESE = "语文"
    MATH = "数学"
    ENGLISH = "英语"
    PHYSICS = "物理"
    CHEMISTRY = "化学"
    BIOLOGY = "生物"
    HISTORY = "历史"
    GEOGRAPHY = "地理"
    POLITICS = "政治"
    OTHER = "其他"


class ExamType(str, Enum):
    """考试类型"""
    MONTHLY = "月考"
    MIDTERM = "期中考试"
    FINAL = "期末考试"
    MOCK = "模拟考试"
    QUIZ = "小测验"
    HOMEWORK = "作业"
    OTHER = "其他"


# 请求模型
class GradeCreateRequest(BaseModel):
    """创建成绩请求模型"""
    student_name: str
    student_id: Optional[str] = None
    subject: SubjectType
    exam_type: ExamType
    exam_name: str
    score: float
    total_score: float = 100.0
    exam_date: datetime
    class_name: Optional[str] = None
    grade_level: Optional[str] = None
    semester: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('student_name')
    def validate_student_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('学生姓名不能为空')
        if len(v) > 50:
            raise ValueError('学生姓名长度不能超过50个字符')
        return v.strip()
    
    @validator('exam_name')
    def validate_exam_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('考试名称不能为空')
        if len(v) > 100:
            raise ValueError('考试名称长度不能超过100个字符')
        return v.strip()
    
    @validator('score')
    def validate_score(cls, v, values):
        if v < 0:
            raise ValueError('成绩不能为负数')
        if 'total_score' in values and v > values['total_score']:
            raise ValueError('成绩不能超过总分')
        return v
    
    @validator('total_score')
    def validate_total_score(cls, v):
        if v <= 0:
            raise ValueError('总分必须大于0')
        if v > 1000:
            raise ValueError('总分不能超过1000')
        return v


class GradeUpdateRequest(BaseModel):
    """更新成绩请求模型"""
    student_name: Optional[str] = None
    student_id: Optional[str] = None
    subject: Optional[SubjectType] = None
    exam_type: Optional[ExamType] = None
    exam_name: Optional[str] = None
    score: Optional[float] = None
    total_score: Optional[float] = None
    exam_date: Optional[datetime] = None
    class_name: Optional[str] = None
    grade_level: Optional[str] = None
    semester: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('score')
    def validate_score(cls, v, values):
        if v is not None:
            if v < 0:
                raise ValueError('成绩不能为负数')
            if 'total_score' in values and values['total_score'] and v > values['total_score']:
                raise ValueError('成绩不能超过总分')
        return v
    
    @validator('total_score')
    def validate_total_score(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('总分必须大于0')
            if v > 1000:
                raise ValueError('总分不能超过1000')
        return v


class GradeQueryRequest(BaseModel):
    """成绩查询请求模型"""
    student_name: Optional[str] = None
    student_id: Optional[str] = None
    subject: Optional[SubjectType] = None
    exam_type: Optional[ExamType] = None
    exam_name: Optional[str] = None
    class_name: Optional[str] = None
    grade_level: Optional[str] = None
    semester: Optional[str] = None
    exam_date_start: Optional[datetime] = None
    exam_date_end: Optional[datetime] = None
    score_min: Optional[float] = None
    score_max: Optional[float] = None
    page: int = 1
    page_size: int = 20
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('页码必须大于0')
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('每页大小必须在1-100之间')
        return v


class BatchGradeRequest(BaseModel):
    """批量成绩操作请求模型"""
    grade_ids: List[int]
    action: str  # 'delete', 'export', etc.
    
    @validator('grade_ids')
    def validate_grade_ids(cls, v):
        if not v:
            raise ValueError('成绩ID列表不能为空')
        if len(v) > 1000:
            raise ValueError('批量操作的成绩数量不能超过1000条')
        return v
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['delete', 'export']
        if v not in allowed_actions:
            raise ValueError(f'操作类型必须是以下之一: {", ".join(allowed_actions)}')
        return v


# 响应模型
class GradeResponse(BaseModel):
    """成绩响应模型"""
    id: int
    student_name: str
    student_id: Optional[str]
    subject: str
    exam_type: str
    exam_name: str
    score: float
    total_score: float
    percentage: float
    exam_date: datetime
    class_name: Optional[str]
    grade_level: Optional[str]
    semester: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class GradeStatistics(BaseModel):
    """成绩统计响应模型"""
    total_count: int
    average_score: float
    highest_score: float
    lowest_score: float
    pass_rate: float
    excellent_rate: float
    score_distribution: Dict[str, int]
    subject_statistics: Dict[str, Dict[str, float]]
    class_statistics: Dict[str, Dict[str, float]]


class ImportResult(BaseModel):
    """导入结果模型"""
    success_count: int
    error_count: int
    total_count: int
    errors: List[Dict[str, Any]]
    warnings: List[str]


@router.post("/", response_model=APIResponse[GradeResponse])
async def create_grade_endpoint(
    request: Request,
    grade_data: GradeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建成绩记录"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise BusinessException("只有教师和管理员可以创建成绩记录")
        
        logger.info(f"创建成绩记录 - 用户: {current_user.username}, 学生: {grade_data.student_name}")
        
        # 查找学生ID
        student = db.query(Student).filter(Student.student_name == grade_data.student_name).first()
        if not student:
            raise BusinessException(f"未找到学生: {grade_data.student_name}")
        
        # 查找科目ID
        subject = db.query(Subject).filter(Subject.subject_name == grade_data.subject).first()
        if not subject:
            raise BusinessException(f"未找到科目: {grade_data.subject}")
        
        # 创建成绩记录
        grade = Grade(
            student_id=student.student_id,
            subject_id=subject.subject_id,
            exam_date=grade_data.exam_date.strftime('%Y-%m-%d'),
            score=grade_data.score,
            exam_type=grade_data.exam_type.value if hasattr(grade_data.exam_type, 'value') else grade_data.exam_type
        )
        
        db.add(grade)
        db.commit()
        db.refresh(grade)
        
        # 构建响应
        percentage = (grade.score / grade_data.total_score) * 100 if grade_data.total_score > 0 else 0
        grade_response = GradeResponse(
            id=grade.grade_id,
            student_name=grade_data.student_name,
            student_id=str(grade.student_id),
            subject=grade_data.subject,
            exam_type=grade.exam_type,
            exam_name=grade_data.exam_name or grade.exam_type,
            score=grade.score,
            total_score=grade_data.total_score,
            percentage=percentage,
            exam_date=grade_data.exam_date,
            class_name=grade_data.class_name,
            grade_level=grade_data.grade_level,
            semester=grade_data.semester,
            notes=grade_data.notes,
            created_at=datetime.now(),
            updated_at=None
        )
        
        return ResponseBuilder.success(
            grade_response,
            "成绩记录创建成功"
        )
        
    except BusinessException as e:
        raise e
    except Exception as e:
        logger.error(f"创建成绩记录异常: {e}")
        raise BusinessException("创建成绩记录失败")


@router.get("/", response_model=APIResponse[PaginatedResponse[GradeResponse]])
async def get_grades_endpoint(
    request: Request,
    student_name: Optional[str] = Query(None, description="学生姓名"),
    student_id: Optional[str] = Query(None, description="学生学号"),
    subject: Optional[SubjectType] = Query(None, description="科目"),
    exam_type: Optional[ExamType] = Query(None, description="考试类型"),
    exam_name: Optional[str] = Query(None, description="考试名称"),
    class_name: Optional[str] = Query(None, description="班级"),
    grade_level: Optional[str] = Query(None, description="年级"),
    semester: Optional[str] = Query(None, description="学期"),
    exam_date_start: Optional[datetime] = Query(None, description="考试开始日期"),
    exam_date_end: Optional[datetime] = Query(None, description="考试结束日期"),
    score_min: Optional[float] = Query(None, description="最低分数"),
    score_max: Optional[float] = Query(None, description="最高分数"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询成绩记录"""
    try:
        # 构建查询条件
        filters = {
            "student_name": student_name,
            "student_id": student_id,
            "subject": subject,
            "exam_type": exam_type,
            "exam_name": exam_name,
            "class_name": class_name,
            "grade_level": grade_level,
            "semester": semester,
            "exam_date_start": exam_date_start,
            "exam_date_end": exam_date_end,
            "score_min": score_min,
            "score_max": score_max
        }
        
        # 移除空值
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # 权限控制：学生只能查看自己的成绩
        if current_user.role == 'student':
            filters['student_name'] = current_user.username
        
        # 查询成绩
        grades, total_count = get_grades(db, filters, page, page_size)
        
        # 构建分页响应
        grade_responses = []
        for grade in grades:
            grade_response = GradeResponse(
                id=grade.grade_id,
                student_name=getattr(grade.student, 'student_name', '') if hasattr(grade, 'student') else '',
                student_id=str(grade.student_id),
                subject=getattr(grade.subject, 'subject_name', '') if hasattr(grade, 'subject') else '',
                exam_type=grade.exam_type,
                exam_name=grade.exam_type,  # 暂时使用exam_type作为exam_name
                score=grade.score,
                total_score=100.0,  # 默认满分100
                percentage=grade.score,  # 暂时使用score作为percentage
                exam_date=datetime.strptime(grade.exam_date, '%Y-%m-%d') if isinstance(grade.exam_date, str) else grade.exam_date,
                class_name=None,
                grade_level=None,
                semester=None,
                notes=None,
                created_at=datetime.now(),
                updated_at=None
            )
            grade_responses.append(grade_response)
        
        total_pages = (total_count + page_size - 1) // page_size
        paginated_response = PaginatedResponse(
            items=grade_responses,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
        return ResponseBuilder.success(
            paginated_response,
            "查询成绩记录成功"
        )
        
    except Exception as e:
        logger.error(f"查询成绩记录异常: {e}")
        raise BusinessException("查询成绩记录失败")


@router.get("/{grade_id}", response_model=APIResponse[GradeResponse])
async def get_grade_endpoint(
    grade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个成绩记录"""
    try:
        # 查询成绩记录
        grades, _ = get_grades(db, {"id": grade_id}, 1, 1)
        
        if not grades:
            raise ResourceNotFoundException("成绩记录不存在")
        
        grade = grades[0]
        
        # 权限检查：学生只能查看自己的成绩
        if current_user.role == 'student' and grade.student_name != current_user.full_name:
            raise ValidationException("无权查看此成绩记录")
        
        return ResponseBuilder.success(
            GradeResponse.from_orm(grade),
            "获取成绩记录成功"
        )
        
    except (ResourceNotFoundException, ValidationException) as e:
        raise e
    except Exception as e:
        logger.error(f"获取成绩记录异常: {e}")
        raise BusinessException("获取成绩记录失败")


@router.put("/{grade_id}", response_model=APIResponse[GradeResponse])
async def update_grade_endpoint(
    grade_id: int,
    grade_data: GradeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新成绩记录"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以更新成绩记录")
        
        logger.info(f"更新成绩记录 - 用户: {current_user.username}, 成绩ID: {grade_id}")
        
        # 更新成绩记录
        grade_manager = GradeManager(db)
        grade = grade_manager.update_grade(grade_id, **grade_data.dict(exclude_unset=True))
        
        if not grade:
            raise ResourceNotFoundException("成绩记录不存在")
        
        return ResponseBuilder.success(
            GradeResponse.from_orm(grade),
            "成绩记录更新成功"
        )
        
    except (ResourceNotFoundException, ValidationException) as e:
        raise e
    except Exception as e:
        logger.error(f"更新成绩记录异常: {e}")
        raise BusinessException("更新成绩记录失败")


@router.delete("/{grade_id}", response_model=APIResponse[dict])
async def delete_grade_endpoint(
    grade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除成绩记录"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以删除成绩记录")
        
        logger.info(f"删除成绩记录 - 用户: {current_user.username}, 成绩ID: {grade_id}")
        
        # 删除成绩记录
        grade_manager = GradeManager(db)
        success = grade_manager.delete_grade(grade_id)
        
        if not success:
            raise ResourceNotFoundException("成绩记录不存在")
        
        return ResponseBuilder.success(
            {"message": "成绩记录删除成功"},
            "成绩记录删除成功"
        )
        
    except (ResourceNotFoundException, ValidationException) as e:
        raise e
    except Exception as e:
        logger.error(f"删除成绩记录异常: {e}")
        raise BusinessException("删除成绩记录失败")


@router.post("/import", response_model=APIResponse[ImportResult])
async def import_grades_endpoint(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从Excel文件导入成绩"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以导入成绩")
        
        # 文件类型检查
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise ValidationException("只支持Excel文件格式(.xlsx, .xls)")
        
        # 文件大小检查（10MB限制）
        if file.size > 10 * 1024 * 1024:
            raise ValidationException("文件大小不能超过10MB")
        
        logger.info(f"导入成绩文件 - 用户: {current_user.username}, 文件: {file.filename}")
        
        # 读取文件内容
        content = await file.read()
        
        # 导入成绩
        grade_manager = GradeManager(db)
        result = grade_manager.import_grades_from_excel(content)
        
        return ResponseBuilder.success(
            ImportResult(**result),
            f"导入完成，成功{result['success_count']}条，失败{result['error_count']}条"
        )
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"导入成绩异常: {e}")
        raise BusinessException("导入成绩失败")


@router.get("/statistics/overview", response_model=APIResponse[GradeStatistics])
async def get_grade_statistics_endpoint(
    request: Request,
    subject: Optional[SubjectType] = Query(None, description="科目"),
    exam_type: Optional[ExamType] = Query(None, description="考试类型"),
    class_name: Optional[str] = Query(None, description="班级"),
    grade_level: Optional[str] = Query(None, description="年级"),
    semester: Optional[str] = Query(None, description="学期"),
    exam_date_start: Optional[datetime] = Query(None, description="考试开始日期"),
    exam_date_end: Optional[datetime] = Query(None, description="考试结束日期"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取成绩统计信息"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看统计信息")
        
        # 构建查询条件
        filters = {
            "subject": subject,
            "exam_type": exam_type,
            "class_name": class_name,
            "grade_level": grade_level,
            "semester": semester,
            "exam_date_start": exam_date_start,
            "exam_date_end": exam_date_end
        }
        
        # 移除空值
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # 获取统计信息
        class_id = filters.get('class_name')  # 将class_name转换为class_id
        subject_id = None
        if filters.get('subject'):
            # 根据科目名称查找科目ID
            subject_obj = db.query(Subject).filter(Subject.subject_name == filters['subject'].value).first()
            if subject_obj:
                subject_id = subject_obj.subject_id
        
        statistics = get_grade_statistics(class_id=class_id, subject_id=subject_id, db=db)
        
        # 如果没有数据，返回默认统计信息
        if not statistics.get('has_data', False):
            grade_stats = GradeStatistics(
                total_count=0,
                average_score=0.0,
                highest_score=0.0,
                lowest_score=0.0,
                pass_rate=0.0,
                excellent_rate=0.0,
                score_distribution={},
                subject_statistics={},
                class_statistics={}
            )
        else:
            # 构造符合GradeStatistics模型的数据
            grade_stats = GradeStatistics(
                total_count=statistics.get('total_count', 0),
                average_score=float(statistics.get('average_score', 0)),
                highest_score=float(statistics.get('highest_score', 0)),
                lowest_score=float(statistics.get('lowest_score', 0)),
                pass_rate=float(statistics.get('pass_rate', 0)),
                excellent_rate=0.0,  # 简化处理
                score_distribution={},  # 简化处理
                subject_statistics={},  # 简化处理
                class_statistics={}  # 简化处理
            )
        
        return ResponseBuilder.success(
            grade_stats,
            "获取统计信息成功"
        )
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取统计信息异常: {e}")
        raise BusinessException("获取统计信息失败")


@router.get("/analysis/student/{student_name}", response_model=APIResponse[dict])
async def get_student_analysis_endpoint(
    student_name: str,
    subject: Optional[str] = Query(None, description="科目"),
    time_range: Optional[str] = Query("semester", description="时间范围"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学生成绩分析"""
    try:
        # 权限检查：学生只能查看自己的分析
        if current_user.role == 'student' and student_name != current_user.full_name:
            raise ValidationException("无权查看此学生的分析")
        elif current_user.role not in ['teacher', 'admin', 'student']:
            raise ValidationException("无权查看学生分析")
        
        # 获取学生ID
        student = db.query(Student).filter(Student.student_name == student_name).first()
        if not student:
            raise ResourceNotFoundException("学生不存在")
        
        # 优先调用AI服务集成接口
        try:
            ai_analysis = await ai_service_client.analyze_grades(
                student_id=str(student.student_id),
                subject=subject,
                time_range=time_range
            )
            
            if ai_analysis.get('success'):
                # 转换AI服务返回的结果格式
                analysis_result = {
                    'student_name': student_name,
                    'student_id': str(student.student_id),
                    'analysis_type': 'ai_enhanced',
                    'overall_performance': ai_analysis.get('data', {}).get('overall_performance', {}),
                    'subject_analysis': ai_analysis.get('data', {}).get('subject_analysis', {}),
                    'trends': ai_analysis.get('data', {}).get('trends', {}),
                    'recommendations': ai_analysis.get('data', {}).get('recommendations', []),
                    'generated_at': datetime.now().isoformat(),
                    'ai_insights': ai_analysis.get('data', {}).get('insights', [])
                }
                
                return ResponseBuilder.success(
                    analysis_result,
                    "AI增强成绩分析获取成功"
                )
        except Exception as ai_error:
            logger.warning(f"AI服务调用失败，回退到传统分析: {ai_error}")
        
        # 回退到原有的分析方法
        analysis = get_student_grade_analysis(db, student_name)
        
        if not analysis:
            raise ResourceNotFoundException("未找到该学生的成绩记录")
        
        return ResponseBuilder.success(
            analysis,
            "获取学生分析成功"
        )
        
    except (ResourceNotFoundException, ValidationException) as e:
        raise e
    except Exception as e:
        logger.error(f"获取学生分析异常: {e}")
        raise BusinessException("获取学生分析失败")


@router.post("/guidance/generate", response_model=APIResponse[dict])
async def generate_student_guidance_endpoint(
    student_name: str = Query(..., description="学生姓名"),
    subject: Optional[str] = Query(None, description="科目"),
    focus_areas: Optional[List[str]] = Query(None, description="关注领域"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成学生个性化指导建议"""
    try:
        # 权限检查
        if current_user.role == 'student' and student_name != current_user.full_name:
            raise ValidationException("无权为此学生生成指导")
        elif current_user.role not in ['teacher', 'admin', 'student']:
            raise ValidationException("无权生成学生指导")
        
        # 获取学生ID
        student = db.query(Student).filter(Student.student_name == student_name).first()
        if not student:
            raise ResourceNotFoundException("学生不存在")
        
        # 先获取学生的成绩分析数据
        try:
            analysis_data = await ai_service_client.analyze_grades(
                student_id=str(student.student_id),
                subject=subject,
                time_range="semester"
            )
            
            if not analysis_data.get('success'):
                # 如果AI分析失败，使用传统方法获取基础数据
                analysis_data = {
                    'data': {
                        'overall_performance': {'average_score': 0},
                        'subject_analysis': {},
                        'trends': {},
                        'weak_areas': focus_areas or []
                    }
                }
        except Exception:
            # 使用默认分析数据
            analysis_data = {
                'data': {
                    'overall_performance': {'average_score': 0},
                    'subject_analysis': {},
                    'trends': {},
                    'weak_areas': focus_areas or []
                }
            }
        
        # 调用AI服务生成个性化指导
        try:
            guidance_result = await ai_service_client.generate_guidance(
                student_id=str(student.student_id),
                analysis_data=analysis_data.get('data', {})
            )
            
            if guidance_result.get('success'):
                guidance_data = {
                    'student_name': student_name,
                    'student_id': str(student.student_id),
                    'subject': subject,
                    'guidance_type': 'ai_personalized',
                    'recommendations': guidance_result.get('data', {}).get('recommendations', []),
                    'study_plan': guidance_result.get('data', {}).get('study_plan', {}),
                    'focus_areas': guidance_result.get('data', {}).get('focus_areas', []),
                    'improvement_strategies': guidance_result.get('data', {}).get('improvement_strategies', []),
                    'generated_at': datetime.now().isoformat(),
                    'ai_confidence': guidance_result.get('data', {}).get('confidence', 0.8)
                }
                
                return ResponseBuilder.success(
                    guidance_data,
                    "个性化指导生成成功"
                )
            else:
                raise Exception("AI服务返回失败状态")
                
        except Exception as ai_error:
            logger.warning(f"AI指导生成失败: {ai_error}")
            
            # 提供基础的指导建议
            basic_guidance = {
                'student_name': student_name,
                'student_id': str(student.student_id),
                'subject': subject,
                'guidance_type': 'basic',
                'recommendations': [
                    "建议加强基础知识的学习和巩固",
                    "多做练习题，提高解题熟练度",
                    "及时向老师请教疑难问题"
                ],
                'study_plan': {
                    'daily_study_time': '1-2小时',
                    'weekly_review': '每周复习一次',
                    'practice_frequency': '每日练习'
                },
                'focus_areas': focus_areas or ['基础知识', '解题技巧'],
                'improvement_strategies': [
                    "制定学习计划",
                    "定期自我检测",
                    "寻求帮助"
                ],
                'generated_at': datetime.now().isoformat(),
                'ai_confidence': 0.5
            }
            
            return ResponseBuilder.success(
                basic_guidance,
                "基础指导建议生成成功"
            )
        
    except (ResourceNotFoundException, ValidationException) as e:
        raise e
    except Exception as e:
        logger.error(f"生成学生指导异常: {e}")
        raise BusinessException("生成学生指导失败")


@router.post("/batch", response_model=APIResponse[dict])
async def batch_grade_operation(
    request: Request,
    batch_data: BatchGradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量成绩操作"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以进行批量操作")
        
        logger.info(f"批量操作 - 用户: {current_user.username}, 操作: {batch_data.action}, 数量: {len(batch_data.grade_ids)}")
        
        if batch_data.action == 'delete':
            # 批量删除
            success_count = 0
            for grade_id in batch_data.grade_ids:
                if delete_grade(db, grade_id):
                    success_count += 1
            
            return ResponseBuilder.success(
                {
                    "action": "delete",
                    "success_count": success_count,
                    "total_count": len(batch_data.grade_ids)
                },
                f"批量删除完成，成功删除{success_count}条记录"
            )
        
        elif batch_data.action == 'export':
            # 批量导出
            filters = {"ids": batch_data.grade_ids}
            export_data = export_grades_to_excel(db, filters)
            
            return ResponseBuilder.success(
                {
                    "action": "export",
                    "file_data": export_data,
                    "total_count": len(batch_data.grade_ids)
                },
                "批量导出完成"
            )
        
        else:
            raise ValidationException(f"不支持的操作类型: {batch_data.action}")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"批量操作异常: {e}")
        raise BusinessException("批量操作失败")


@router.get("/export/excel")
async def export_grades_to_excel_endpoint(
    student_name: Optional[str] = Query(None, description="学生姓名"),
    class_name: Optional[str] = Query(None, description="班级名称"),
    subject: Optional[SubjectType] = Query(None, description="科目"),
    exam_type: Optional[ExamType] = Query(None, description="考试类型"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出成绩到Excel文件"""
    try:
        logger.info(f"用户 {current_user.username} 导出成绩数据")
        
        # 权限检查
        if current_user.role == "student":
            # 学生只能导出自己的成绩
            student_name = current_user.username
        
        # 构建查询条件
        filters = {}
        if student_name:
            filters['student_name'] = student_name
        if class_name:
            filters['class_name'] = class_name
        if subject:
            filters['subject'] = subject
        if exam_type:
            filters['exam_type'] = exam_type
        if start_date:
            filters['exam_date_start'] = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            filters['exam_date_end'] = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 获取成绩数据
        grades, _ = get_grades(db, filters, 1, 10000)  # 获取大量数据用于导出
        
        # 构建Excel数据
        excel_data = []
        for grade in grades:
            excel_data.append({
                '学生姓名': getattr(grade.student, 'student_name', '') if hasattr(grade, 'student') else '',
                '学号': str(grade.student_id),
                '科目': getattr(grade.subject, 'subject_name', '') if hasattr(grade, 'subject') else '',
                '考试类型': grade.exam_type,
                '成绩': grade.score,
                '考试日期': grade.exam_date
            })
        
        # 创建DataFrame
        df = pd.DataFrame(excel_data)
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='成绩数据', index=False)
        
        output.seek(0)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grades_export_{timestamp}.xlsx"
        
        # 返回文件流
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"导出成绩失败: {str(e)}")
        raise BusinessException(f"导出成绩失败: {str(e)}")


@router.post("/validate", response_model=APIResponse[dict])
async def validate_grade_data_endpoint(
    grade_data: GradeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """验证成绩数据"""
    try:
        logger.info(f"用户 {current_user.username} 验证成绩数据")
        
        # 权限检查
        if current_user.role not in ["teacher", "admin"]:
            raise ValidationException("权限不足")
        
        validation_errors = []
        warnings = []
        
        # 验证学生是否存在
        student = db.query(Student).filter(Student.student_name == grade_data.student_name).first()
        if not student:
            validation_errors.append(f"学生 '{grade_data.student_name}' 不存在")
        
        # 验证科目是否存在
        subject = db.query(Subject).filter(Subject.subject_name == grade_data.subject).first()
        if not subject:
            validation_errors.append(f"科目 '{grade_data.subject}' 不存在")
        
        # 验证成绩范围
        if grade_data.score < 0 or grade_data.score > grade_data.total_score:
            validation_errors.append(f"成绩 {grade_data.score} 超出有效范围 [0, {grade_data.total_score}]")
        
        # 检查是否存在重复记录
        if student and subject:
            existing_grade = db.query(Grade).filter(
                Grade.student_id == student.student_id,
                Grade.subject_id == subject.subject_id,
                Grade.exam_date == grade_data.exam_date.strftime('%Y-%m-%d'),
                Grade.exam_type == grade_data.exam_type
            ).first()
            
            if existing_grade:
                warnings.append("存在相同学生、科目、日期和考试类型的成绩记录")
        
        validation_result = {
            "is_valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "warnings": warnings,
            "student_exists": student is not None,
            "subject_exists": subject is not None
        }
        
        return ResponseBuilder.success(
            validation_result,
            "数据验证完成"
        )
    
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"验证成绩数据失败: {str(e)}")
        raise BusinessException(f"验证成绩数据失败: {str(e)}")