# -*- coding: utf-8 -*-
"""
智能作业批改API路由
提供作业提交、批改、统计等功能
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import io
import logging

from core.homework_service import (
    HomeworkGradingService, 
    HomeworkSubmission, 
    GradingResult, 
    GradingCriteria,
    SubjectType,
    SubmissionType
)
from core.ai_service import AIServiceManager
from core.cache_service import CacheManager
from core.task_service import TaskQueue
from auth import get_current_user
from models.user import UserInDB as User
from database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/homework", tags=["智能作业批改"])

# 初始化服务
ai_manager = AIServiceManager()
homework_service = HomeworkGradingService(ai_manager)

# 请求模型
from pydantic import BaseModel, validator

class HomeworkSubmissionRequest(BaseModel):
    """作业提交请求"""
    student_id: str
    student_name: str
    subject: SubjectType
    assignment_id: str
    submission_type: SubmissionType
    content: Optional[str] = None
    image_urls: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('content')
    def validate_content(cls, v, values):
        submission_type = values.get('submission_type')
        if submission_type == SubmissionType.TEXT and not v:
            raise ValueError('文本作业必须提供内容')
        return v
    
    @validator('image_urls')
    def validate_image_urls(cls, v, values):
        submission_type = values.get('submission_type')
        if submission_type == SubmissionType.IMAGE and (not v or len(v) == 0):
            raise ValueError('图像作业必须提供图片URL')
        return v

class BatchGradingRequest(BaseModel):
    """批量批改请求"""
    submissions: List[HomeworkSubmissionRequest]
    criteria: Optional[GradingCriteria] = None
    
    @validator('submissions')
    def validate_submissions(cls, v):
        if len(v) == 0:
            raise ValueError('批量批改至少需要一份作业')
        if len(v) > 50:
            raise ValueError('单次批量批改最多支持50份作业')
        return v

class GradingCriteriaRequest(BaseModel):
    """批改标准请求"""
    subject: SubjectType
    total_score: int = 100
    question_weights: Optional[Dict[str, float]] = None
    grading_rules: Optional[Dict[str, Any]] = None
    strict_mode: bool = False

class StatisticsRequest(BaseModel):
    """统计查询请求"""
    student_id: Optional[str] = None
    subject: Optional[SubjectType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    class_id: Optional[str] = None

# 响应模型
class GradingResponse(BaseModel):
    """批改响应"""
    success: bool
    message: str
    data: Optional[GradingResult] = None
    task_id: Optional[str] = None  # 异步任务ID

class BatchGradingResponse(BaseModel):
    """批量批改响应"""
    success: bool
    message: str
    total_count: int
    completed_count: int
    failed_count: int
    results: List[GradingResult]
    task_id: Optional[str] = None

class StatisticsResponse(BaseModel):
    """统计响应"""
    success: bool
    data: Dict[str, Any]

# API路由

@router.post("/submit", response_model=GradingResponse, summary="提交作业进行批改")
async def submit_homework(
    submission: HomeworkSubmissionRequest,
    criteria: Optional[GradingCriteriaRequest] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交作业进行AI批改
    
    - **submission**: 作业提交信息
    - **criteria**: 批改标准（可选）
    - 支持文本、图像、文件等多种作业类型
    - 返回批改结果或异步任务ID
    """
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin'] and current_user.id != submission.student_id:
            raise HTTPException(status_code=403, detail="无权限提交此作业")
        
        # 转换请求为服务模型
        homework_submission = HomeworkSubmission(
            student_id=submission.student_id,
            student_name=submission.student_name,
            subject=submission.subject,
            assignment_id=submission.assignment_id,
            submission_type=submission.submission_type,
            content=submission.content,
            image_urls=submission.image_urls,
            metadata=submission.metadata or {}
        )
        
        # 转换批改标准
        grading_criteria = None
        if criteria:
            grading_criteria = GradingCriteria(
                subject=criteria.subject,
                total_score=criteria.total_score,
                question_weights=criteria.question_weights or {},
                grading_rules=criteria.grading_rules or {},
                strict_mode=criteria.strict_mode
            )
        
        # 执行批改
        result = await homework_service.grade_homework(homework_submission, grading_criteria)
        
        # 记录批改历史（后台任务）
        background_tasks.add_task(
            _save_grading_history, 
            db, 
            result, 
            current_user.id
        )
        
        return GradingResponse(
            success=True,
            message="作业批改完成",
            data=result
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"作业批改失败: {str(e)}")
        raise HTTPException(status_code=500, detail="作业批改服务异常")

@router.post("/batch", response_model=BatchGradingResponse, summary="批量批改作业")
async def batch_grade_homework(
    request: BatchGradingRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量批改作业
    
    - **submissions**: 作业提交列表
    - **criteria**: 统一批改标准
    - 支持最多50份作业的批量处理
    - 返回批改结果汇总
    """
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise HTTPException(status_code=403, detail="无权限进行批量批改")
        
        # 转换请求
        submissions = [
            HomeworkSubmission(
                student_id=sub.student_id,
                student_name=sub.student_name,
                subject=sub.subject,
                assignment_id=sub.assignment_id,
                submission_type=sub.submission_type,
                content=sub.content,
                image_urls=sub.image_urls,
                metadata=sub.metadata or {}
            )
            for sub in request.submissions
        ]
        
        # 执行批量批改
        results = await homework_service.batch_grade_homework(submissions, request.criteria)
        
        # 统计结果
        completed_count = len([r for r in results if not r.requires_manual_review])
        failed_count = len([r for r in results if r.ai_confidence < 0.3])
        
        # 保存批改历史（后台任务）
        background_tasks.add_task(
            _save_batch_grading_history,
            db,
            results,
            current_user.id
        )
        
        return BatchGradingResponse(
            success=True,
            message=f"批量批改完成，共{len(results)}份作业",
            total_count=len(results),
            completed_count=completed_count,
            failed_count=failed_count,
            results=results
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"批量批改失败: {str(e)}")
        raise HTTPException(status_code=500, detail="批量批改服务异常")

@router.post("/upload", summary="上传作业文件")
async def upload_homework_file(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    student_name: str = Form(...),
    subject: SubjectType = Form(...),
    assignment_id: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传作业文件（图片、PDF等）
    
    - 支持图片格式：jpg, jpeg, png, gif
    - 支持文档格式：pdf, doc, docx
    - 文件大小限制：10MB
    """
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin'] and current_user.id != student_id:
            raise HTTPException(status_code=403, detail="无权限上传此作业")
        
        # 文件类型检查
        allowed_types = {
            'image': ['jpg', 'jpeg', 'png', 'gif'],
            'document': ['pdf', 'doc', 'docx']
        }
        
        file_extension = file.filename.split('.')[-1].lower()
        file_type = None
        
        for type_name, extensions in allowed_types.items():
            if file_extension in extensions:
                file_type = type_name
                break
        
        if not file_type:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        # 文件大小检查（10MB）
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件大小超过限制（10MB）")
        
        # 保存文件（这里应该保存到云存储或本地存储）
        file_content = await file.read()
        file_url = await _save_uploaded_file(file_content, file.filename, student_id, assignment_id)
        
        # 根据文件类型创建提交
        if file_type == 'image':
            submission_type = SubmissionType.IMAGE
            image_urls = [file_url]
            content = None
        else:
            submission_type = SubmissionType.FILE
            image_urls = None
            content = f"文件：{file.filename}"
        
        submission = HomeworkSubmission(
            student_id=student_id,
            student_name=student_name,
            subject=subject,
            assignment_id=assignment_id,
            submission_type=submission_type,
            content=content,
            image_urls=image_urls,
            metadata={
                'file_name': file.filename,
                'file_size': file.size,
                'file_type': file_type,
                'file_url': file_url
            }
        )
        
        # 执行批改
        result = await homework_service.grade_homework(submission)
        
        return {
            "success": True,
            "message": "文件上传并批改完成",
            "file_url": file_url,
            "grading_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail="文件上传服务异常")

@router.get("/statistics", response_model=StatisticsResponse, summary="获取批改统计")
async def get_grading_statistics(
    student_id: Optional[str] = None,
    subject: Optional[SubjectType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    class_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取作业批改统计信息
    
    - 支持按学生、科目、时间范围、班级筛选
    - 返回成绩分布、错误分析、改进建议等
    """
    try:
        # 权限检查
        if current_user.role == 'student' and current_user.id != student_id:
            raise HTTPException(status_code=403, detail="无权限查看其他学生统计")
        
        # 获取统计数据
        stats = await homework_service.get_grading_statistics(
            student_id=student_id,
            subject=subject,
            start_date=start_date,
            end_date=end_date
        )
        
        return StatisticsResponse(
            success=True,
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="统计服务异常")

@router.get("/export", summary="导出批改报告")
async def export_grading_report(
    format_type: str = "json",
    student_id: Optional[str] = None,
    subject: Optional[SubjectType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出批改报告
    
    - **format_type**: 导出格式（json, csv, excel）
    - 支持按条件筛选导出数据
    - 返回文件下载流
    """
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise HTTPException(status_code=403, detail="无权限导出报告")
        
        # 查询批改记录（这里应该从数据库查询）
        # 暂时使用模拟数据
        results = []  # 从数据库查询的结果
        
        # 生成报告
        report_content = await homework_service.export_grading_report(results, format_type)
        
        # 设置响应头
        if format_type == "csv":
            media_type = "text/csv"
            filename = f"grading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        elif format_type == "json":
            media_type = "application/json"
            filename = f"grading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            raise HTTPException(status_code=400, detail="不支持的导出格式")
        
        # 返回文件流
        return StreamingResponse(
            io.BytesIO(report_content.encode('utf-8')),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail="导出服务异常")

@router.get("/result/{submission_id}", response_model=GradingResponse, summary="获取批改结果")
async def get_grading_result(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据提交ID获取批改结果
    """
    try:
        # 从数据库查询批改结果
        # 这里应该实现数据库查询逻辑
        result = None  # 从数据库查询
        
        if not result:
            raise HTTPException(status_code=404, detail="批改结果不存在")
        
        # 权限检查
        if (current_user.role == 'student' and 
            current_user.id != result.student_id):
            raise HTTPException(status_code=403, detail="无权限查看此批改结果")
        
        return GradingResponse(
            success=True,
            message="获取批改结果成功",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取批改结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail="查询服务异常")

# 辅助函数

async def _save_uploaded_file(file_content: bytes, filename: str, student_id: str, assignment_id: str) -> str:
    """
    保存上传的文件并返回URL
    """
    # 这里应该实现文件保存逻辑（云存储或本地存储）
    # 返回文件访问URL
    import uuid
    file_id = str(uuid.uuid4())
    file_url = f"/files/homework/{student_id}/{assignment_id}/{file_id}_{filename}"
    
    # 实际保存文件的逻辑
    # ...
    
    return file_url

async def _save_grading_history(db: Session, result: GradingResult, grader_id: str):
    """
    保存批改历史记录
    """
    try:
        # 这里应该实现数据库保存逻辑
        logger.info(f"保存批改历史: {result.submission_id}")
    except Exception as e:
        logger.error(f"保存批改历史失败: {str(e)}")

async def _save_batch_grading_history(db: Session, results: List[GradingResult], grader_id: str):
    """
    保存批量批改历史记录
    """
    try:
        # 这里应该实现批量数据库保存逻辑
        logger.info(f"保存批量批改历史: {len(results)}条记录")
    except Exception as e:
        logger.error(f"保存批量批改历史失败: {str(e)}")