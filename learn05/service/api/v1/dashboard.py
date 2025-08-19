# -*- coding: utf-8 -*-
"""
工作台API路由

本模块提供工作台相关的API接口，包括概览数据、最近活动、今日课程等功能。
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from database import get_db, User
from models.response import APIResponse, ResponseBuilder
from middleware.exception_handler import BusinessException, ValidationException
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== 数据模型定义 ====================

class DashboardOverview(BaseModel):
    """工作台概览数据"""
    total_students: int = Field(..., description="学生总数")
    weekly_courses: int = Field(..., description="本周课程数")
    average_score: float = Field(..., description="平均成绩")
    preparation_hours: float = Field(..., description="备课时长")
    unread_notifications: int = Field(..., description="未读通知数")
    pending_tasks: int = Field(..., description="待处理任务数")

class RecentActivity(BaseModel):
    """最近活动"""
    id: str = Field(..., description="活动ID")
    type: str = Field(..., description="活动类型")
    title: str = Field(..., description="活动标题")
    description: str = Field(..., description="活动描述")
    timestamp: datetime = Field(..., description="时间戳")
    status: str = Field(..., description="状态")
    related_id: Optional[str] = Field(None, description="关联ID")

class TodayCourse(BaseModel):
    """今日课程"""
    id: str = Field(..., description="课程ID")
    time: str = Field(..., description="上课时间")
    subject: str = Field(..., description="科目")
    topic: str = Field(..., description="课程主题")
    class_name: str = Field(..., description="班级名称")
    location: str = Field(..., description="上课地点")
    status: str = Field(..., description="课程状态")
    preparation_status: str = Field(..., description="备课状态")

class QuickAction(BaseModel):
    """快速操作"""
    id: str = Field(..., description="操作ID")
    title: str = Field(..., description="操作标题")
    description: str = Field(..., description="操作描述")
    icon: str = Field(..., description="图标")
    url: str = Field(..., description="跳转链接")
    category: str = Field(..., description="分类")

class DashboardData(BaseModel):
    """工作台完整数据"""
    overview: DashboardOverview = Field(..., description="概览数据")
    recent_activities: List[RecentActivity] = Field(..., description="最近活动")
    today_courses: List[TodayCourse] = Field(..., description="今日课程")
    quick_actions: List[QuickAction] = Field(..., description="快速操作")

# ==================== API接口 ====================

@router.get("/overview", response_model=APIResponse[DashboardOverview])
async def get_dashboard_overview(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作台概览数据"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看工作台概览")
        
        # 模拟数据 - 实际应从数据库查询
        overview = DashboardOverview(
            total_students=156,
            weekly_courses=12,
            average_score=85.6,
            preparation_hours=8.5,
            unread_notifications=3,
            pending_tasks=5
        )
        
        return ResponseBuilder.success(overview, "获取工作台概览成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取工作台概览异常: {e}")
        raise BusinessException("获取工作台概览失败")

@router.get("/activities", response_model=APIResponse[List[RecentActivity]])
async def get_recent_activities(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取最近活动列表"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看最近活动")
        
        # 模拟数据 - 实际应从数据库查询
        activities = [
            RecentActivity(
                id="act_001",
                type="lesson_plan",
                title="创建教案",
                description="为高一生物《细胞的结构》创建了新教案",
                timestamp=datetime.now() - timedelta(hours=2),
                status="completed",
                related_id="plan_001"
            ),
            RecentActivity(
                id="act_002",
                type="grade_review",
                title="批改作业",
                description="完成了高一(3)班生物作业批改",
                timestamp=datetime.now() - timedelta(hours=4),
                status="completed",
                related_id="grade_001"
            ),
            RecentActivity(
                id="act_003",
                type="report_view",
                title="查看成绩报告",
                description="查看了期中考试成绩分析报告",
                timestamp=datetime.now() - timedelta(hours=6),
                status="completed",
                related_id="report_001"
            ),
            RecentActivity(
                id="act_004",
                type="experiment_design",
                title="设计实验方案",
                description="为《酶的活性》设计了实验方案",
                timestamp=datetime.now() - timedelta(hours=8),
                status="completed",
                related_id="exp_001"
            )
        ]
        
        # 限制返回数量
        activities = activities[:limit]
        
        return ResponseBuilder.success(activities, "获取最近活动成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取最近活动异常: {e}")
        raise BusinessException("获取最近活动失败")

@router.get("/today-courses", response_model=APIResponse[List[TodayCourse]])
async def get_today_courses(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今日课程安排"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看课程安排")
        
        # 模拟数据 - 实际应从数据库查询
        courses = [
            TodayCourse(
                id="course_001",
                time="08:00-08:45",
                subject="生物",
                topic="细胞的结构与功能",
                class_name="高一(3)班",
                location="生物实验室",
                status="upcoming",
                preparation_status="completed"
            ),
            TodayCourse(
                id="course_002",
                time="10:00-10:45",
                subject="生物",
                topic="酶的特性",
                class_name="高一(5)班",
                location="生物实验室",
                status="upcoming",
                preparation_status="in_progress"
            ),
            TodayCourse(
                id="course_003",
                time="14:30-15:15",
                subject="生物",
                topic="光合作用",
                class_name="高二(2)班",
                location="多媒体教室",
                status="upcoming",
                preparation_status="pending"
            )
        ]
        
        return ResponseBuilder.success(courses, "获取今日课程成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取今日课程异常: {e}")
        raise BusinessException("获取今日课程失败")

@router.get("/quick-actions", response_model=APIResponse[List[QuickAction]])
async def get_quick_actions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取快速操作列表"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看快速操作")
        
        # 模拟数据 - 实际应从配置或数据库查询
        actions = [
            QuickAction(
                id="action_001",
                title="智能备课",
                description="AI辅助创建教案和课件",
                icon="book",
                url="/teaching-prep",
                category="teaching"
            ),
            QuickAction(
                id="action_002",
                title="实验设计",
                description="设计生物实验方案",
                icon="flask",
                url="/experiment-design",
                category="teaching"
            ),
            QuickAction(
                id="action_003",
                title="成绩分析",
                description="查看学生成绩统计分析",
                icon="chart",
                url="/grade-analysis",
                category="analysis"
            ),
            QuickAction(
                id="action_004",
                title="AI问答",
                description="智能教学问答助手",
                icon="message",
                url="/ai-chat",
                category="ai"
            ),
            QuickAction(
                id="action_005",
                title="学情分析",
                description="学生学习情况分析",
                icon="user",
                url="/student-analysis",
                category="analysis"
            ),
            QuickAction(
                id="action_006",
                title="课堂助手",
                description="实时课堂互动工具",
                icon="presentation",
                url="/classroom-assistant",
                category="teaching"
            )
        ]
        
        return ResponseBuilder.success(actions, "获取快速操作成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取快速操作异常: {e}")
        raise BusinessException("获取快速操作失败")

@router.get("/", response_model=APIResponse[DashboardData])
async def get_dashboard_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作台完整数据"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看工作台数据")
        
        # 并发获取各模块数据
        overview_response = await get_dashboard_overview(request, current_user, db)
        activities_response = await get_recent_activities(request, 5, current_user, db)
        courses_response = await get_today_courses(request, current_user, db)
        actions_response = await get_quick_actions(request, current_user, db)
        
        # 组装完整数据
        dashboard_data = DashboardData(
            overview=overview_response.data,
            recent_activities=activities_response.data,
            today_courses=courses_response.data,
            quick_actions=actions_response.data
        )
        
        return ResponseBuilder.success(dashboard_data, "获取工作台数据成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取工作台数据异常: {e}")
        raise BusinessException("获取工作台数据失败")

@router.get("/health", response_model=APIResponse[Dict[str, str]])
async def health_check():
    """健康检查"""
    return ResponseBuilder.success({
        "status": "healthy",
        "module": "dashboard",
        "timestamp": datetime.now().isoformat()
    })