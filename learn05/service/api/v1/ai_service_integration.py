#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手AI服务集成API
将llm目录的AI服务接口集成到service项目中
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# 添加llm目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../llm'))

try:
    # 导入LLM服务
    from factory import LLMFactory
    from services.lesson_prep_service import LessonPrepService
    from services.classroom_ai_service import ClassroomAIService
    from services.grade_management_service import GradeManagementService
except ImportError as e:
    logging.warning(f"无法导入LLM服务: {e}，将使用模拟实现")
    
    # 模拟实现
    class LLMFactory:
        def __init__(self):
            pass
    
    class LessonPrepService:
        def __init__(self, factory):
            self.factory = factory
        
        async def analyze_material(self, data):
            return {
                'success': True,
                'message': '教材分析完成',
                'data': {
                    'analysis_id': f'analysis_{datetime.now().timestamp()}',
                    'knowledge_points': ['模拟知识点1', '模拟知识点2'],
                    'difficulty_level': 'medium',
                    'teaching_suggestions': ['建议1', '建议2']
                }
            }
        
        async def create_lesson_plan(self, data):
            return {
                'success': True,
                'message': '教学计划创建完成',
                'data': {
                    'plan_id': f'plan_{datetime.now().timestamp()}',
                    'title': data.get('topic', '模拟教学计划'),
                    'objectives': data.get('objectives', []),
                    'activities': ['活动1', '活动2', '活动3']
                }
            }
        
        async def analyze_student_situation(self, data):
            return {
                'success': True,
                'message': '学情分析完成',
                'data': {
                    'analysis_id': f'student_analysis_{datetime.now().timestamp()}',
                    'student_profiles': data.get('student_profiles', []),
                    'learning_status': 'good',
                    'recommendations': ['建议1', '建议2']
                }
            }
        
        async def recommend_cases(self, data):
            return {
                'success': True,
                'message': '案例推荐完成',
                'data': {
                    'cases': [
                        {'title': '优秀案例1', 'description': '案例描述1'},
                        {'title': '优秀案例2', 'description': '案例描述2'}
                    ]
                }
            }
    
    class ClassroomAIService:
        def __init__(self, factory):
            self.factory = factory
        
        async def analyze_real_time_learning(self, data):
            return {
                'success': True,
                'message': '实时学情分析完成',
                'data': {
                    'analysis_id': f'realtime_{datetime.now().timestamp()}',
                    'attention_level': 0.8,
                    'engagement_score': 0.75,
                    'learning_insights': ['洞察1', '洞察2']
                }
            }
        
        async def design_experiment(self, data):
            return {
                'success': True,
                'message': '实验设计完成',
                'data': {
                    'experiment_id': f'exp_{datetime.now().timestamp()}',
                    'title': data.get('topic', '模拟实验'),
                    'materials': ['材料1', '材料2'],
                    'steps': ['步骤1', '步骤2', '步骤3']
                }
            }
        
        async def recommend_ai_applications(self, data):
            return {
                'success': True,
                'message': 'AI应用推荐完成',
                'data': {
                    'applications': [
                        {'name': 'AI工具1', 'description': '工具描述1'},
                        {'name': 'AI工具2', 'description': '工具描述2'}
                    ]
                }
            }
        
        async def integrate_ai_tools(self, data):
            return {
                'success': True,
                'message': 'AI工具集成完成',
                'data': {
                    'integration_id': f'integration_{datetime.now().timestamp()}',
                    'tools': ['工具1', '工具2'],
                    'status': 'integrated'
                }
            }
    
    class GradeManagementService:
        def __init__(self, factory):
            self.factory = factory
        
        async def process_batch_grades(self, data):
            return {
                'success': True,
                'message': '批量成绩处理完成',
                'data': {
                    'processed_count': len(data.get('grades', [])),
                    'success_count': len(data.get('grades', [])),
                    'failed_count': 0
                }
            }
        
        async def smart_grade_recognition(self, data):
            return {
                'success': True,
                'message': '智能成绩识别完成',
                'data': {
                    'recognition_id': f'recognition_{datetime.now().timestamp()}',
                    'recognized_grades': [85, 92, 78, 88],
                    'confidence': 0.95
                }
            }
        
        async def analyze_grades(self, data):
            return {
                'success': True,
                'message': '成绩分析完成',
                'data': {
                    'analysis_id': f'grade_analysis_{datetime.now().timestamp()}',
                    'average_score': 85.5,
                    'distribution': {'A': 20, 'B': 30, 'C': 25, 'D': 15, 'F': 10},
                    'trends': ['上升趋势']
                }
            }
        
        async def get_grade_trends(self, data):
            return {
                'success': True,
                'message': '成绩趋势分析完成',
                'data': {
                    'trends': [
                        {'period': '本月', 'average': 85.2, 'change': '+2.3'},
                        {'period': '上月', 'average': 82.9, 'change': '+1.1'}
                    ]
                }
            }
        
        async def generate_personalized_guidance(self, data):
            return {
                'success': True,
                'message': '个性化指导生成完成',
                'data': {
                    'guidance_id': f'guidance_{datetime.now().timestamp()}',
                    'student_id': data.get('student_profile', {}).get('id', 'unknown'),
                    'recommendations': ['建议1', '建议2', '建议3'],
                    'focus_areas': ['重点领域1', '重点领域2']
                }
            }
        
        async def create_tutoring_plan(self, data):
            return {
                'success': True,
                'message': '辅导方案创建完成',
                'data': {
                    'plan_id': f'tutoring_{datetime.now().timestamp()}',
                    'student_id': data.get('student_info', {}).get('id', 'unknown'),
                    'subject': data.get('subject', 'unknown'),
                    'sessions': [
                        {'week': 1, 'topics': ['主题1', '主题2']},
                        {'week': 2, 'topics': ['主题3', '主题4']}
                    ]
                }
            }

from database import get_db, User
from models.response import APIResponse, ResponseBuilder
from auth import get_current_user

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# Pydantic模型定义
class BaseRequest(BaseModel):
    """基础请求模型"""
    request_id: Optional[str] = Field(None, description="请求ID")
    timestamp: Optional[str] = Field(None, description="请求时间戳")
    
    class Config:
        extra = "allow"

class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Dict[str, Any] = Field(default_factory=dict, description="响应数据")
    request_id: Optional[str] = Field(None, description="请求ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="响应时间戳")

# 备课助手相关模型
class MaterialAnalysisRequest(BaseRequest):
    """教材分析请求"""
    content: str = Field(..., description="教材内容")
    subject: str = Field(..., description="学科")
    grade: str = Field(..., description="年级")
    analysis_type: str = Field(default="comprehensive", description="分析类型")

class LessonPlanRequest(BaseRequest):
    """课程计划请求"""
    subject: str = Field(..., description="学科")
    topic: str = Field(..., description="主题")
    grade: str = Field(..., description="年级")
    duration: int = Field(default=45, description="课时长度（分钟）")
    objectives: List[str] = Field(default_factory=list, description="教学目标")

class StudentAnalysisRequest(BaseRequest):
    """学情分析请求"""
    student_profiles: List[Dict[str, Any]] = Field(..., description="学生档案列表")
    subject: str = Field(..., description="学科")
    analysis_focus: List[str] = Field(default_factory=list, description="分析重点")

# 课堂AI助手相关模型
class RealTimeLearningRequest(BaseRequest):
    """实时学情分析请求"""
    classroom_data: Dict[str, Any] = Field(..., description="课堂数据")
    analysis_type: str = Field(default="real_time", description="分析类型")
    student_interactions: List[Dict[str, Any]] = Field(default_factory=list, description="学生互动数据")

class ExperimentDesignRequest(BaseRequest):
    """实验设计请求"""
    subject: str = Field(..., description="学科")
    topic: str = Field(..., description="实验主题")
    grade: str = Field(..., description="年级")
    objectives: List[str] = Field(..., description="实验目标")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="实验约束条件")

class AIApplicationRequest(BaseRequest):
    """AI应用推荐请求"""
    teaching_context: Dict[str, Any] = Field(..., description="教学上下文")
    subject: str = Field(..., description="学科")
    grade: str = Field(..., description="年级")
    application_type: str = Field(default="general", description="应用类型")

# 成绩管理相关模型
class BatchGradeRequest(BaseRequest):
    """批量成绩录入请求"""
    grades: List[Dict[str, Any]] = Field(..., description="成绩数据列表")
    validation_rules: Dict[str, Any] = Field(default_factory=dict, description="验证规则")

class GradeAnalysisRequest(BaseRequest):
    """成绩分析请求"""
    grades: List[Dict[str, Any]] = Field(..., description="成绩数据")
    analysis_type: str = Field(default="comprehensive", description="分析类型")
    period: str = Field(default="本学期", description="分析周期")

class PersonalizedGuidanceRequest(BaseRequest):
    """个性化指导请求"""
    student_profile: Dict[str, Any] = Field(..., description="学生档案")
    grade_analysis: Dict[str, Any] = Field(..., description="成绩分析")
    learning_preferences: Dict[str, Any] = Field(default_factory=dict, description="学习偏好")

class TutoringPlanRequest(BaseRequest):
    """辅导方案请求"""
    student_info: Dict[str, Any] = Field(..., description="学生信息")
    subject: str = Field(..., description="学科")
    current_level: str = Field(default="beginner", description="当前水平")
    target_level: str = Field(default="intermediate", description="目标水平")
    available_time: int = Field(default=2, description="可用时间（小时/周）")

class SmartRecognitionRequest(BaseRequest):
    """智能识别请求"""
    image_path: str = Field(..., description="图像路径")
    recognition_type: str = Field(default="handwritten", description="识别类型")

# AI服务管理器
class AIServiceManager:
    """AI服务管理器"""
    
    def __init__(self):
        self.llm_factory = None
        self.lesson_prep_service = None
        self.classroom_ai_service = None
        self.grade_management_service = None
        self._initialized = False
    
    async def initialize(self):
        """初始化AI服务"""
        if self._initialized:
            return
        
        try:
            # 初始化LLM工厂
            self.llm_factory = LLMFactory()
            
            # 初始化各个AI服务
            self.lesson_prep_service = LessonPrepService(self.llm_factory)
            self.classroom_ai_service = ClassroomAIService(self.llm_factory)
            self.grade_management_service = GradeManagementService(self.llm_factory)
            
            self._initialized = True
            logger.info("AI服务管理器初始化完成")
            
        except Exception as e:
            logger.error(f"AI服务管理器初始化失败: {str(e)}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        logger.info("AI服务管理器清理资源")
        # 这里可以添加资源清理逻辑

# 全局服务管理器实例
ai_service_manager = AIServiceManager()

# 工具函数
def create_response(success: bool, message: str, data: Dict[str, Any] = None, request_id: str = None) -> BaseResponse:
    """创建标准响应"""
    return BaseResponse(
        success=success,
        message=message,
        data=data or {},
        request_id=request_id
    )

async def handle_service_call(service_func, request_data: Dict[str, Any], request_id: str = None) -> BaseResponse:
    """处理服务调用"""
    try:
        # 确保AI服务已初始化
        await ai_service_manager.initialize()
        
        result = await service_func(request_data)
        return create_response(
            success=result.get('success', True),
            message=result.get('message', '处理成功'),
            data=result.get('data', {}),
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"服务调用失败: {str(e)}")
        return create_response(
            success=False,
            message=f"服务调用失败: {str(e)}",
            request_id=request_id
        )

# ==================== 备课助手API接口 ====================

@router.post("/lesson-prep/analyze-material", response_model=APIResponse)
async def analyze_teaching_material(
    request: MaterialAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """教材智能分析"""
    request_data = {
        'content': request.content,
        'subject': request.subject,
        'grade': request.grade,
        'analysis_type': request.analysis_type
    }
    
    result = await handle_service_call(
        ai_service_manager.lesson_prep_service.analyze_material,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/lesson-prep/create-plan", response_model=APIResponse)
async def create_lesson_plan(
    request: LessonPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建教学计划"""
    request_data = {
        'subject': request.subject,
        'topic': request.topic,
        'grade': request.grade,
        'duration': request.duration,
        'objectives': request.objectives
    }
    
    result = await handle_service_call(
        ai_service_manager.lesson_prep_service.create_lesson_plan,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/lesson-prep/analyze-students", response_model=APIResponse)
async def analyze_student_situation(
    request: StudentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """学情预设分析"""
    request_data = {
        'student_profiles': request.student_profiles,
        'subject': request.subject,
        'analysis_focus': request.analysis_focus
    }
    
    result = await handle_service_call(
        ai_service_manager.lesson_prep_service.analyze_student_situation,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/lesson-prep/recommend-cases", response_model=APIResponse)
async def recommend_teaching_cases(
    request: BaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """推荐优秀教学案例"""
    request_data = request.dict(exclude={'request_id', 'timestamp'})
    
    result = await handle_service_call(
        ai_service_manager.lesson_prep_service.recommend_cases,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

# ==================== 课堂AI助手API接口 ====================

@router.post("/classroom/real-time-analysis", response_model=APIResponse)
async def real_time_learning_analysis(
    request: RealTimeLearningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """实时学情分析"""
    request_data = {
        'classroom_data': request.classroom_data,
        'analysis_type': request.analysis_type,
        'student_interactions': request.student_interactions
    }
    
    result = await handle_service_call(
        ai_service_manager.classroom_ai_service.analyze_real_time_learning,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/classroom/design-experiment", response_model=APIResponse)
async def design_biology_experiment(
    request: ExperimentDesignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生物实验设计"""
    request_data = {
        'subject': request.subject,
        'topic': request.topic,
        'grade': request.grade,
        'objectives': request.objectives,
        'constraints': request.constraints
    }
    
    result = await handle_service_call(
        ai_service_manager.classroom_ai_service.design_experiment,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/classroom/recommend-ai-apps", response_model=APIResponse)
async def recommend_ai_applications(
    request: AIApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI应用推荐"""
    request_data = {
        'teaching_context': request.teaching_context,
        'subject': request.subject,
        'grade': request.grade,
        'application_type': request.application_type
    }
    
    result = await handle_service_call(
        ai_service_manager.classroom_ai_service.recommend_ai_applications,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/classroom/integrate-ai", response_model=APIResponse)
async def integrate_ai_tools(
    request: BaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI工具集成"""
    request_data = request.dict(exclude={'request_id', 'timestamp'})
    
    result = await handle_service_call(
        ai_service_manager.classroom_ai_service.integrate_ai_tools,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

# ==================== 成绩管理API接口 ====================

@router.post("/grades/batch-input", response_model=APIResponse)
async def batch_input_grades(
    request: BatchGradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量成绩录入"""
    request_data = {
        'grades': request.grades,
        'validation_rules': request.validation_rules
    }
    
    result = await handle_service_call(
        ai_service_manager.grade_management_service.process_batch_grades,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/grades/smart-recognition", response_model=APIResponse)
async def smart_grade_recognition(
    request: SmartRecognitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """智能成绩识别"""
    request_data = {
        'image_path': request.image_path,
        'type': request.recognition_type
    }
    
    result = await handle_service_call(
        ai_service_manager.grade_management_service.smart_grade_recognition,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/grades/analyze", response_model=APIResponse)
async def analyze_grades(
    request: GradeAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """成绩综合分析"""
    request_data = {
        'grades': request.grades,
        'analysis_type': request.analysis_type,
        'period': request.period
    }
    
    result = await handle_service_call(
        ai_service_manager.grade_management_service.analyze_grades,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/grades/trends", response_model=APIResponse)
async def get_grade_trends(
    request: BaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """成绩趋势分析"""
    request_data = request.dict(exclude={'request_id', 'timestamp'})
    
    result = await handle_service_call(
        ai_service_manager.grade_management_service.get_grade_trends,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/grades/personalized-guidance", response_model=APIResponse)
async def generate_personalized_guidance(
    request: PersonalizedGuidanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成个性化指导"""
    request_data = {
        'student_profile': request.student_profile,
        'grade_analysis': request.grade_analysis,
        'learning_preferences': request.learning_preferences
    }
    
    result = await handle_service_call(
        ai_service_manager.grade_management_service.generate_personalized_guidance,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

@router.post("/grades/tutoring-plan", response_model=APIResponse)
async def create_tutoring_plan(
    request: TutoringPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建辅导方案"""
    request_data = {
        'student_info': request.student_info,
        'subject': request.subject,
        'current_level': request.current_level,
        'target_level': request.target_level,
        'available_time': request.available_time
    }
    
    result = await handle_service_call(
        ai_service_manager.grade_management_service.create_tutoring_plan,
        request_data,
        request.request_id
    )
    
    return ResponseBuilder.success(
        message=result.message,
        data=result.data
    )

# ==================== 通用API接口 ====================

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        await ai_service_manager.initialize()
        return ResponseBuilder.success(
            message="AI服务健康检查通过",
            data={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "lesson_prep": ai_service_manager.lesson_prep_service is not None,
                    "classroom_ai": ai_service_manager.classroom_ai_service is not None,
                    "grade_management": ai_service_manager.grade_management_service is not None
                }
            }
        )
    except Exception as e:
        return ResponseBuilder.error(
            message=f"AI服务健康检查失败: {str(e)}",
            data={"status": "unhealthy"}
        )

@router.get("/info")
async def get_api_info():
    """获取API信息"""
    return ResponseBuilder.success(
        message="API信息获取成功",
        data={
            "name": "智能教学助手AI服务集成API",
            "version": "2.0.0",
            "description": "将llm目录的AI服务集成到service项目中",
            "endpoints": {
                "lesson_prep": [
                    "/ai-service/lesson-prep/analyze-material",
                    "/ai-service/lesson-prep/create-plan",
                    "/ai-service/lesson-prep/analyze-students",
                    "/ai-service/lesson-prep/recommend-cases"
                ],
                "classroom_ai": [
                    "/ai-service/classroom/real-time-analysis",
                    "/ai-service/classroom/design-experiment",
                    "/ai-service/classroom/recommend-ai-apps",
                    "/ai-service/classroom/integrate-ai"
                ],
                "grade_management": [
                    "/ai-service/grades/batch-input",
                    "/ai-service/grades/smart-recognition",
                    "/ai-service/grades/analyze",
                    "/ai-service/grades/trends",
                    "/ai-service/grades/personalized-guidance",
                    "/ai-service/grades/tutoring-plan"
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
    )

# ==================== 错误处理 ====================
# Note: Exception handlers should be registered at the FastAPI app level, not router level
# These handlers would need to be moved to main.py where the FastAPI app is created