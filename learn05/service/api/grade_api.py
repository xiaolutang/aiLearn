# -*- coding: utf-8 -*-
"""
成绩API接口
提供成绩相关的HTTP接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional, Dict, Any
import pandas as pd
import io
from datetime import datetime

from models.grade import (
    GradeCreate, GradeUpdate, GradeResponse, GradeStatistics, 
    PaginatedGrades, ExamCreate, ExamResponse, SubjectCreate, 
    SubjectResponse, PaginatedExams, PaginatedSubjects, 
    StudentPerformance, CustomReportRequest
)
from models.class_model import ClassPerformance
from services.grade_service import get_grade_service, GradeService
from services.user_service import get_current_user
from models.user import UserResponse

# 创建路由器
router = APIRouter()


@router.post("/", response_model=GradeResponse, status_code=status.HTTP_201_CREATED, tags=["成绩管理"])
async def create_grade(
    grade_data: GradeCreate,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建成绩记录
    
    Args:
        grade_data: 成绩创建数据
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        GradeResponse: 创建的成绩记录
        
    Raises:
        HTTPException: 创建失败
    """
    try:
        return grade_service.create_grade(grade_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=PaginatedGrades, tags=["成绩管理"])
async def get_grades(
    page: int = 1,
    limit: int = 10,
    student_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    exam_id: Optional[str] = None,
    class_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取成绩列表
    
    Args:
        page: 当前页码
        limit: 每页数量
        student_id: 学生ID过滤
        subject_id: 科目ID过滤
        exam_id: 考试ID过滤
        class_id: 班级ID过滤
        start_date: 开始日期
        end_date: 结束日期
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        PaginatedGrades: 分页成绩列表
    """
    # 构建过滤条件
    filters = {}
    if student_id:
        filters["student_id"] = student_id
    if subject_id:
        filters["subject_id"] = subject_id
    if exam_id:
        filters["exam_id"] = exam_id
    if class_id:
        filters["class_id"] = class_id
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    return grade_service.get_grades(page=page, limit=limit, **filters)


@router.get("/{grade_id}", response_model=GradeResponse, tags=["成绩管理"])
async def get_grade(
    grade_id: str,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取单个成绩记录
    
    Args:
        grade_id: 成绩ID
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        GradeResponse: 成绩记录
        
    Raises:
        HTTPException: 成绩记录不存在
    """
    grade = grade_service.get_grade_by_id(grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成绩记录不存在")
    return grade


@router.put("/{grade_id}", response_model=GradeResponse, tags=["成绩管理"])
async def update_grade(
    grade_id: str,
    grade_data: GradeUpdate,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新成绩记录
    
    Args:
        grade_id: 成绩ID
        grade_data: 成绩更新数据
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        GradeResponse: 更新后的成绩记录
        
    Raises:
        HTTPException: 更新失败或成绩记录不存在
    """
    try:
        return grade_service.update_grade(grade_id, grade_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["成绩管理"])
async def delete_grade(
    grade_id: str,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除成绩记录
    
    Args:
        grade_id: 成绩ID
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        None
        
    Raises:
        HTTPException: 删除失败或成绩记录不存在
    """
    try:
        result = grade_service.delete_grade(grade_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除成绩记录失败")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/import", response_model=Dict[str, Any], tags=["成绩管理"])
async def import_grades(
    file: UploadFile = File(...),
    class_id: str = None,
    exam_id: str = None,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """批量导入成绩（Excel文件）
    
    Args:
        file: Excel文件
        class_id: 班级ID
        exam_id: 考试ID
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        Dict[str, Any]: 导入结果统计
        
    Raises:
        HTTPException: 导入失败
    """
    # 验证文件类型
    if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xls'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只支持Excel文件格式")
    
    try:
        # 读取文件内容
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 导入成绩
        result = grade_service.import_grades_from_excel(df, class_id, exam_id)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"导入失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"导入失败: {str(e)}")
    finally:
        await file.close()


@router.post("/export", tags=["成绩管理"])
async def export_grades(
    filters: Dict[str, Any],
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """导出成绩数据
    
    Args:
        filters: 过滤条件
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        文件下载响应
    """
    try:
        # 导出成绩数据
        excel_data = grade_service.export_grades_to_excel(**filters)
        
        # 返回文件下载响应
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=grades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"导出失败: {str(e)}")


@router.get("/statistics/student/{student_id}", response_model=StudentPerformance, tags=["成绩统计"])
async def get_student_performance(
    student_id: str,
    subject_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取学生成绩表现
    
    Args:
        student_id: 学生ID
        subject_id: 科目ID（可选）
        start_date: 开始日期
        end_date: 结束日期
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        StudentPerformance: 学生成绩表现
        
    Raises:
        HTTPException: 获取失败
    """
    try:
        # 构建过滤条件
        filters = {}
        if subject_id:
            filters["subject_id"] = subject_id
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        
        return grade_service.get_student_performance(student_id, **filters)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/class/{class_id}", response_model=ClassPerformance, tags=["成绩统计"])
async def get_class_performance(
    class_id: str,
    subject_id: Optional[str] = None,
    exam_id: Optional[str] = None,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取班级成绩表现
    
    Args:
        class_id: 班级ID
        subject_id: 科目ID（可选）
        exam_id: 考试ID（可选）
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        ClassPerformance: 班级成绩表现
        
    Raises:
        HTTPException: 获取失败
    """
    try:
        # 构建过滤条件
        filters = {}
        if subject_id:
            filters["subject_id"] = subject_id
        if exam_id:
            filters["exam_id"] = exam_id
        
        return grade_service.get_class_performance(class_id, **filters)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/subject/{subject_id}", response_model=GradeStatistics, tags=["成绩统计"])
async def get_subject_statistics(
    subject_id: str,
    class_id: Optional[str] = None,
    exam_id: Optional[str] = None,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取科目成绩统计
    
    Args:
        subject_id: 科目ID
        class_id: 班级ID（可选）
        exam_id: 考试ID（可选）
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        GradeStatistics: 科目成绩统计
        
    Raises:
        HTTPException: 获取失败
    """
    try:
        # 构建过滤条件
        filters = {}
        if class_id:
            filters["class_id"] = class_id
        if exam_id:
            filters["exam_id"] = exam_id
        
        return grade_service.get_subject_statistics(subject_id, **filters)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/custom-report", response_model=Dict[str, Any], tags=["成绩统计"])
async def generate_custom_report(
    request: CustomReportRequest,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """生成自定义成绩报告
    
    Args:
        request: 自定义报告请求
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        Dict[str, Any]: 自定义报告数据
        
    Raises:
        HTTPException: 生成失败
    """
    try:
        return grade_service.generate_custom_report(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/ai-analysis/{student_id}", response_model=Dict[str, str], tags=["AI分析"])
async def get_ai_analysis(
    student_id: str,
    subject_id: Optional[str] = None,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取AI生成的学生成绩分析
    
    Args:
        student_id: 学生ID
        subject_id: 科目ID（可选）
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        Dict[str, str]: AI分析结果
        
    Raises:
        HTTPException: 获取失败
    """
    try:
        # 构建过滤条件
        filters = {}
        if subject_id:
            filters["subject_id"] = subject_id
        
        return grade_service.get_ai_analysis(student_id, **filters)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/ai-recommendation/{student_id}", response_model=Dict[str, str], tags=["AI分析"])
async def get_ai_recommendation(
    student_id: str,
    subject_id: Optional[str] = None,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取AI生成的学习建议
    
    Args:
        student_id: 学生ID
        subject_id: 科目ID（可选）
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        Dict[str, str]: AI学习建议
        
    Raises:
        HTTPException: 获取失败
    """
    try:
        # 构建过滤条件
        filters = {}
        if subject_id:
            filters["subject_id"] = subject_id
        
        return grade_service.get_ai_recommendation(student_id, **filters)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/exams", response_model=ExamResponse, status_code=status.HTTP_201_CREATED, tags=["考试管理"])
async def create_exam(
    exam_data: ExamCreate,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建考试
    
    Args:
        exam_data: 考试创建数据
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        ExamResponse: 创建的考试
        
    Raises:
        HTTPException: 创建失败
    """
    try:
        return grade_service.create_exam(exam_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/exams", response_model=PaginatedExams, tags=["考试管理"])
async def get_exams(
    page: int = 1,
    limit: int = 10,
    class_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取考试列表
    
    Args:
        page: 当前页码
        limit: 每页数量
        class_id: 班级ID过滤
        start_date: 开始日期
        end_date: 结束日期
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        PaginatedExams: 分页考试列表
    """
    # 构建过滤条件
    filters = {}
    if class_id:
        filters["class_id"] = class_id
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    return grade_service.get_exams(page=page, limit=limit, **filters)


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, tags=["科目管理"])
async def create_subject(
    subject_data: SubjectCreate,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建科目
    
    Args:
        subject_data: 科目创建数据
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        SubjectResponse: 创建的科目
        
    Raises:
        HTTPException: 创建失败
    """
    try:
        return grade_service.create_subject(subject_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/subjects", response_model=PaginatedSubjects, tags=["科目管理"])
async def get_subjects(
    page: int = 1,
    limit: int = 10,
    grade_service: GradeService = Depends(get_grade_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取科目列表
    
    Args:
        page: 当前页码
        limit: 每页数量
        grade_service: 成绩服务实例
        current_user: 当前登录用户
        
    Returns:
        PaginatedSubjects: 分页科目列表
    """
    return grade_service.get_subjects(page=page, limit=limit)