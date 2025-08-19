# -*- coding: utf-8 -*-
"""
数据分析API路由

本模块提供数据分析相关的API接口。
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from database import get_db, User
from models.response import APIResponse, ResponseBuilder
from middleware.exception_handler import BusinessException, AuthenticationException
from auth import get_current_user
from grade_management import GradeManager, GradeAnalyzer, get_grade_statistics, get_student_grade_analysis
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalyticsRequest(BaseModel):
    """分析请求模型"""
    analysis_type: str
    time_range: Optional[str] = "last_month"
    subjects: Optional[List[str]] = None
    classes: Optional[List[str]] = None
    grade_levels: Optional[List[str]] = None


class TrendAnalysis(BaseModel):
    """趋势分析响应模型"""
    period: str
    average_score: float
    improvement_rate: float
    trend_direction: str
    data_points: List[Dict[str, Any]]


class ComparisonAnalysis(BaseModel):
    """对比分析响应模型"""
    comparison_type: str
    baseline: Dict[str, Any]
    target: Dict[str, Any]
    difference: Dict[str, Any]
    insights: List[str]


class PredictiveAnalysis(BaseModel):
    """预测分析响应模型"""
    prediction_type: str
    current_performance: Dict[str, Any]
    predicted_performance: Dict[str, Any]
    confidence_level: float
    recommendations: List[str]


@router.get("/overview", response_model=APIResponse[Dict[str, Any]])
async def get_analytics_overview(
    request: Request,
    time_range: str = Query("last_month", description="时间范围"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分析概览"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看分析概览")
        
        # 计算时间范围
        end_date = datetime.now()
        if time_range == "last_week":
            start_date = end_date - timedelta(weeks=1)
        elif time_range == "last_month":
            start_date = end_date - timedelta(days=30)
        elif time_range == "last_quarter":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # 构建查询条件
        filters = {
            "exam_date_start": start_date,
            "exam_date_end": end_date
        }
        
        # 获取统计数据
        statistics = get_grade_statistics(db, filters)
        
        # 构建概览数据
        overview = {
            "time_range": time_range,
            "period": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            "summary": {
                "total_students": statistics.get("total_count", 0),
                "average_score": statistics.get("average_score", 0),
                "pass_rate": statistics.get("pass_rate", 0),
                "excellent_rate": statistics.get("excellent_rate", 0)
            },
            "subject_performance": statistics.get("subject_statistics", {}),
            "class_performance": statistics.get("class_statistics", {}),
            "score_distribution": statistics.get("score_distribution", {}),
            "insights": [
                "本期整体表现良好" if statistics.get("average_score", 0) >= 80 else "本期表现有待提升",
                f"及格率为{statistics.get('pass_rate', 0):.1f}%",
                f"优秀率为{statistics.get('excellent_rate', 0):.1f}%"
            ]
        }
        
        return ResponseBuilder.success(overview, "获取分析概览成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取分析概览异常: {e}")
        raise BusinessException("获取分析概览失败")


@router.get("/trends", response_model=APIResponse[TrendAnalysis])
async def get_trend_analysis(
    request: Request,
    analysis_type: str = Query("score_trend", description="分析类型"),
    subject: Optional[str] = Query(None, description="科目"),
    class_name: Optional[str] = Query(None, description="班级"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取趋势分析"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看趋势分析")
        
        # 模拟趋势分析数据
        trend_data = TrendAnalysis(
            period="最近3个月",
            average_score=82.5,
            improvement_rate=5.2,
            trend_direction="上升",
            data_points=[
                {"date": "2024-01-01", "score": 78.5, "count": 120},
                {"date": "2024-02-01", "score": 80.2, "count": 125},
                {"date": "2024-03-01", "score": 82.5, "count": 130}
            ]
        )
        
        return ResponseBuilder.success(trend_data, "获取趋势分析成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取趋势分析异常: {e}")
        raise BusinessException("获取趋势分析失败")


@router.get("/comparison", response_model=APIResponse[ComparisonAnalysis])
async def get_comparison_analysis(
    request: Request,
    comparison_type: str = Query("class_comparison", description="对比类型"),
    baseline: str = Query(..., description="基准"),
    target: str = Query(..., description="目标"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对比分析"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看对比分析")
        
        # 模拟对比分析数据
        comparison_data = ComparisonAnalysis(
            comparison_type=comparison_type,
            baseline={
                "name": baseline,
                "average_score": 78.5,
                "pass_rate": 85.2,
                "student_count": 45
            },
            target={
                "name": target,
                "average_score": 82.3,
                "pass_rate": 89.1,
                "student_count": 42
            },
            difference={
                "score_diff": 3.8,
                "pass_rate_diff": 3.9,
                "performance_level": "目标表现更好"
            },
            insights=[
                "目标组在平均分上领先3.8分",
                "目标组的及格率高出3.9个百分点",
                "建议基准组学习目标组的教学方法"
            ]
        )
        
        return ResponseBuilder.success(comparison_data, "获取对比分析成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取对比分析异常: {e}")
        raise BusinessException("获取对比分析失败")


@router.get("/prediction", response_model=APIResponse[PredictiveAnalysis])
async def get_predictive_analysis(
    request: Request,
    prediction_type: str = Query("performance_prediction", description="预测类型"),
    student_name: Optional[str] = Query(None, description="学生姓名"),
    subject: Optional[str] = Query(None, description="科目"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预测分析"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            if current_user.role == 'student' and student_name != current_user.full_name:
                raise ValidationException("学生只能查看自己的预测分析")
        
        # 模拟预测分析数据
        prediction_data = PredictiveAnalysis(
            prediction_type=prediction_type,
            current_performance={
                "average_score": 78.5,
                "trend": "稳定",
                "recent_scores": [76, 78, 80, 79, 81]
            },
            predicted_performance={
                "next_exam_score": 82.3,
                "confidence_interval": [79.1, 85.5],
                "improvement_potential": "中等"
            },
            confidence_level=0.75,
            recommendations=[
                "加强薄弱知识点练习",
                "保持当前学习节奏",
                "重点关注错题复习",
                "建议增加模拟练习"
            ]
        )
        
        return ResponseBuilder.success(prediction_data, "获取预测分析成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取预测分析异常: {e}")
        raise BusinessException("获取预测分析失败")


@router.get("/student/{student_name}", response_model=APIResponse[Dict[str, Any]])
async def get_student_analytics(
    student_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学生个人分析"""
    try:
        # 权限检查
        if current_user.role == 'student' and student_name != current_user.full_name:
            raise ValidationException("学生只能查看自己的分析")
        elif current_user.role not in ['teacher', 'admin', 'student']:
            raise ValidationException("无权查看学生分析")
        
        # 获取学生分析
        analysis = get_student_grade_analysis(db, student_name)
        
        if not analysis:
            raise ValidationException("未找到该学生的成绩记录")
        
        return ResponseBuilder.success(analysis, "获取学生分析成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取学生分析异常: {e}")
        raise BusinessException("获取学生分析失败")


@router.post("/custom", response_model=APIResponse[Dict[str, Any]])
async def create_custom_analysis(
    request: Request,
    analysis_request: AnalyticsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建自定义分析"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以创建自定义分析")
        
        logger.info(f"创建自定义分析 - 用户: {current_user.username}, 类型: {analysis_request.analysis_type}")
        
        # 模拟自定义分析结果
        custom_analysis = {
            "analysis_id": f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": analysis_request.analysis_type,
            "parameters": analysis_request.dict(),
            "results": {
                "summary": "自定义分析完成",
                "data": {},
                "insights": ["这是一个自定义分析示例"]
            },
            "created_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        return ResponseBuilder.success(custom_analysis, "自定义分析创建成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"创建自定义分析异常: {e}")
        raise BusinessException("创建自定义分析失败")