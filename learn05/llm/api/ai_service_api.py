#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手AI服务统一API接口
提供备课助手、课堂AI助手、成绩管理等核心AI服务的统一调用接口
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from factory import LLMFactory
from services.lesson_prep_service import LessonPrepService
from services.classroom_ai_service import ClassroomAIService
from services.grade_management_service import GradeManagementService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# FastAPI应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    await ai_service_manager.initialize()
    yield
    # 关闭时清理
    await ai_service_manager.cleanup()

# 创建FastAPI应用
app = FastAPI(
    title="智能教学助手AI服务API",
    description="提供备课助手、课堂AI助手、成绩管理等核心AI服务",
    version="2.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/api/v1/lesson-prep/analyze-material", response_model=BaseResponse)
async def analyze_teaching_material(request: MaterialAnalysisRequest):
    """教材智能分析"""
    request_data = {
        'content': request.content,
        'subject': request.subject,
        'grade': request.grade,
        'analysis_type': request.analysis_type
    }
    
    return await handle_service_call(
        ai_service_manager.lesson_prep_service.analyze_material,
        request_data,
        request.request_id
    )

@app.post("/api/v1/lesson-prep/create-plan", response_model=BaseResponse)
async def create_lesson_plan(request: LessonPlanRequest):
    """创建教学计划"""
    request_data = {
        'subject': request.subject,
        'topic': request.topic,
        'grade': request.grade,
        'duration': request.duration,
        'objectives': request.objectives
    }
    
    return await handle_service_call(
        ai_service_manager.lesson_prep_service.create_lesson_plan,
        request_data,
        request.request_id
    )

@app.post("/api/v1/lesson-prep/analyze-students", response_model=BaseResponse)
async def analyze_student_situation(request: StudentAnalysisRequest):
    """学情预设分析"""
    request_data = {
        'student_profiles': request.student_profiles,
        'subject': request.subject,
        'analysis_focus': request.analysis_focus
    }
    
    return await handle_service_call(
        ai_service_manager.lesson_prep_service.analyze_student_situation,
        request_data,
        request.request_id
    )

@app.post("/api/v1/lesson-prep/recommend-cases", response_model=BaseResponse)
async def recommend_teaching_cases(request: BaseRequest):
    """推荐优秀教学案例"""
    request_data = request.dict(exclude={'request_id', 'timestamp'})
    
    return await handle_service_call(
        ai_service_manager.lesson_prep_service.recommend_cases,
        request_data,
        request.request_id
    )

# ==================== 课堂AI助手API接口 ====================

@app.post("/api/v1/classroom/real-time-analysis", response_model=BaseResponse)
async def real_time_learning_analysis(request: RealTimeLearningRequest):
    """实时学情分析"""
    request_data = {
        'classroom_data': request.classroom_data,
        'analysis_type': request.analysis_type,
        'student_interactions': request.student_interactions
    }
    
    return await handle_service_call(
        ai_service_manager.classroom_ai_service.analyze_real_time_learning,
        request_data,
        request.request_id
    )

@app.post("/api/v1/classroom/design-experiment", response_model=BaseResponse)
async def design_biology_experiment(request: ExperimentDesignRequest):
    """生物实验设计"""
    request_data = {
        'subject': request.subject,
        'topic': request.topic,
        'grade': request.grade,
        'objectives': request.objectives,
        'constraints': request.constraints
    }
    
    return await handle_service_call(
        ai_service_manager.classroom_ai_service.design_experiment,
        request_data,
        request.request_id
    )

@app.post("/api/v1/classroom/recommend-ai-apps", response_model=BaseResponse)
async def recommend_ai_applications(request: AIApplicationRequest):
    """AI应用推荐"""
    request_data = {
        'teaching_context': request.teaching_context,
        'subject': request.subject,
        'grade': request.grade,
        'application_type': request.application_type
    }
    
    return await handle_service_call(
        ai_service_manager.classroom_ai_service.recommend_ai_applications,
        request_data,
        request.request_id
    )

@app.post("/api/v1/classroom/integrate-ai", response_model=BaseResponse)
async def integrate_ai_tools(request: BaseRequest):
    """AI工具集成"""
    request_data = request.dict(exclude={'request_id', 'timestamp'})
    
    return await handle_service_call(
        ai_service_manager.classroom_ai_service.integrate_ai_tools,
        request_data,
        request.request_id
    )

# ==================== 成绩管理API接口 ====================

@app.post("/api/v1/grades/batch-input", response_model=BaseResponse)
async def batch_input_grades(request: BatchGradeRequest):
    """批量成绩录入"""
    request_data = {
        'grades': request.grades,
        'validation_rules': request.validation_rules
    }
    
    return await handle_service_call(
        ai_service_manager.grade_management_service.process_batch_grades,
        request_data,
        request.request_id
    )

@app.post("/api/v1/grades/smart-recognition", response_model=BaseResponse)
async def smart_grade_recognition(request: SmartRecognitionRequest):
    """智能成绩识别"""
    request_data = {
        'image_path': request.image_path,
        'type': request.recognition_type
    }
    
    return await handle_service_call(
        ai_service_manager.grade_management_service.smart_grade_recognition,
        request_data,
        request.request_id
    )

@app.post("/api/v1/grades/analyze", response_model=BaseResponse)
async def analyze_grades(request: GradeAnalysisRequest):
    """成绩综合分析"""
    request_data = {
        'grades': request.grades,
        'analysis_type': request.analysis_type,
        'period': request.period
    }
    
    return await handle_service_call(
        ai_service_manager.grade_management_service.analyze_grades,
        request_data,
        request.request_id
    )

@app.post("/api/v1/grades/trends", response_model=BaseResponse)
async def get_grade_trends(request: BaseRequest):
    """成绩趋势分析"""
    request_data = request.dict(exclude={'request_id', 'timestamp'})
    
    return await handle_service_call(
        ai_service_manager.grade_management_service.get_grade_trends,
        request_data,
        request.request_id
    )

@app.post("/api/v1/grades/personalized-guidance", response_model=BaseResponse)
async def generate_personalized_guidance(request: PersonalizedGuidanceRequest):
    """生成个性化指导"""
    request_data = {
        'student_profile': request.student_profile,
        'grade_analysis': request.grade_analysis,
        'learning_preferences': request.learning_preferences
    }
    
    return await handle_service_call(
        ai_service_manager.grade_management_service.generate_personalized_guidance,
        request_data,
        request.request_id
    )

@app.post("/api/v1/grades/tutoring-plan", response_model=BaseResponse)
async def create_tutoring_plan(request: TutoringPlanRequest):
    """创建辅导方案"""
    request_data = {
        'student_info': request.student_info,
        'subject': request.subject,
        'current_level': request.current_level,
        'target_level': request.target_level,
        'available_time': request.available_time
    }
    
    return await handle_service_call(
        ai_service_manager.grade_management_service.create_tutoring_plan,
        request_data,
        request.request_id
    )

# ==================== 通用API接口 ====================

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "lesson_prep": ai_service_manager.lesson_prep_service is not None,
            "classroom_ai": ai_service_manager.classroom_ai_service is not None,
            "grade_management": ai_service_manager.grade_management_service is not None
        }
    }

@app.get("/api/v1/info")
async def get_api_info():
    """获取API信息"""
    return {
        "name": "智能教学助手AI服务API",
        "version": "2.0.0",
        "description": "提供备课助手、课堂AI助手、成绩管理等核心AI服务",
        "endpoints": {
            "lesson_prep": [
                "/api/v1/lesson-prep/analyze-material",
                "/api/v1/lesson-prep/create-plan",
                "/api/v1/lesson-prep/analyze-students",
                "/api/v1/lesson-prep/recommend-cases"
            ],
            "classroom_ai": [
                "/api/v1/classroom/real-time-analysis",
                "/api/v1/classroom/design-experiment",
                "/api/v1/classroom/recommend-ai-apps",
                "/api/v1/classroom/integrate-ai"
            ],
            "grade_management": [
                "/api/v1/grades/batch-input",
                "/api/v1/grades/smart-recognition",
                "/api/v1/grades/analyze",
                "/api/v1/grades/trends",
                "/api/v1/grades/personalized-guidance",
                "/api/v1/grades/tutoring-plan"
            ]
        },
        "timestamp": datetime.now().isoformat()
    }

# ==================== 错误处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return create_response(
        success=False,
        message=f"HTTP错误: {exc.detail}",
        data={"status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未处理的异常: {str(exc)}")
    return create_response(
        success=False,
        message=f"服务器内部错误: {str(exc)}"
    )

# ==================== 中间件 ====================

@app.middleware("http")
async def log_requests(request, call_next):
    """请求日志中间件"""
    start_time = datetime.now()
    
    # 记录请求
    logger.info(f"请求开始: {request.method} {request.url}")
    
    # 处理请求
    response = await call_next(request)
    
    # 记录响应
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"请求完成: {request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ai_service_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )