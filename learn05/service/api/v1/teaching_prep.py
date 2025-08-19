# -*- coding: utf-8 -*-
"""
备课模块API路由

本模块提供备课相关的API接口，包括教材分析、教案管理、教学资源等功能。
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import time
from enum import Enum
from pydantic import BaseModel, Field

from database import get_db, User
from models.response import APIResponse, ResponseBuilder, PaginatedResponse
from middleware.exception_handler import BusinessException, ValidationException, ResourceNotFoundException
from auth import get_current_user
import httpx
import os

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
    
    async def analyze_material(self, content: str, subject: str, grade: str):
        """教材分析"""
        data = {
            'content': content,
            'subject': subject,
            'grade': grade,
            'analysis_type': 'comprehensive'
        }
        return await self._make_request('POST', '/lesson-prep/analyze-material', data)
    
    async def create_lesson_plan(self, subject: str, topic: str, grade: str, objectives: list = None):
        """创建教学计划"""
        data = {
            'subject': subject,
            'topic': topic,
            'grade': grade,
            'objectives': objectives or []
        }
        return await self._make_request('POST', '/lesson-prep/create-plan', data)
    
    async def analyze_students(self, student_profiles: list, subject: str):
        """学情分析"""
        data = {
            'student_profiles': student_profiles,
            'subject': subject
        }
        return await self._make_request('POST', '/lesson-prep/analyze-students', data)
    
    async def recommend_cases(self, subject: str, topic: str):
        """推荐教学案例"""
        data = {
            'subject': subject,
            'topic': topic
        }
        return await self._make_request('POST', '/lesson-prep/recommend-cases', data)

# 尝试导入AI服务，如果不存在则使用模拟实现
try:
    from llm.unified_client import UnifiedLLMClient
    from llm.agent_manager import AgentManager
except ImportError:
    # 模拟实现，用于开发阶段
    class UnifiedLLMClient:
        async def generate_response(self, prompt: str, **kwargs) -> str:
            return f"模拟AI响应: {prompt[:50]}..."
    
    class AgentManager:
        def get_agent(self, agent_type: str):
            return self
        
        async def execute_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
            return {"result": "模拟执行结果", "status": "success"}

# 导入备课服务
try:
    from core.ai_service import AIServiceManager, AIRequest, AIProvider
    from core.cache_service import CacheManager
    from core.teaching_prep_service import (
        TeachingPrepService, TextbookContent, KnowledgePoint, TeachingPlan,
        StudentPreset, TeachingCase, SubjectType as CoreSubjectType, TeachingPhase, DifficultyLevel as CoreDifficultyLevel,
        TeachingStyle as CoreTeachingStyle
    )
except ImportError:
    # 模拟实现
    class AIServiceManager:
        async def generate_response(self, prompt: str, **kwargs) -> str:
            return f"模拟AI响应: {prompt[:50]}..."
    
    class CacheManager:
        def get(self, key):
            return None
        
        def set(self, key, value, ttl=None):
            pass
    
    class TeachingPrepService:
        def __init__(self, ai_manager):
            self.ai_manager = ai_manager
        
        async def analyze_textbook(self, content):
            return {"analysis": "模拟分析结果"}
        
        async def generate_teaching_plan(self, **kwargs):
            return {"plan": "模拟教学计划"}
    
    class TextbookContent:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class TeachingPlan:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class StudentPreset:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class TeachingCase:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

logger = logging.getLogger(__name__)

router = APIRouter()

# 创建服务实例
ai_client = UnifiedLLMClient()
agent_manager = AgentManager()
ai_manager = AIServiceManager()
cache_manager = CacheManager()
teaching_prep_service = TeachingPrepService(ai_manager)
ai_service_client = AIServiceClient()

# ==================== 数据模型定义 ====================

class SubjectType(str, Enum):
    """学科类型枚举"""
    CHINESE = "chinese"  # 语文
    MATH = "math"  # 数学
    ENGLISH = "english"  # 英语
    PHYSICS = "physics"  # 物理
    CHEMISTRY = "chemistry"  # 化学
    BIOLOGY = "biology"  # 生物
    HISTORY = "history"  # 历史
    GEOGRAPHY = "geography"  # 地理
    POLITICS = "politics"  # 政治

class TeachingStyle(str, Enum):
    """教学风格枚举"""
    TRADITIONAL = "traditional"  # 传统教学
    INTERACTIVE = "interactive"  # 互动教学
    INQUIRY = "inquiry"  # 探究式教学
    COLLABORATIVE = "collaborative"  # 合作学习
    FLIPPED = "flipped"  # 翻转课堂

class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    EASY = "easy"  # 简单
    MEDIUM = "medium"  # 中等
    HARD = "hard"  # 困难

# 请求模型
class TextbookUploadRequest(BaseModel):
    """教材上传请求"""
    title: str = Field(..., min_length=1, max_length=200, description="教材标题")
    subject: SubjectType = Field(..., description="学科")
    grade_level: int = Field(..., ge=1, le=12, description="年级")
    chapter: str = Field(..., min_length=1, max_length=100, description="章节")
    section: Optional[str] = Field(None, max_length=100, description="节次")
    content: str = Field(..., min_length=10, description="教材内容")
    description: Optional[str] = Field(None, max_length=500, description="描述")

class LessonPlanRequest(BaseModel):
    """教案创建请求"""
    title: str = Field(..., min_length=1, max_length=200, description="教案标题")
    subject: SubjectType = Field(..., description="学科")
    grade_level: int = Field(..., ge=1, le=12, description="年级")
    duration: int = Field(..., ge=1, le=180, description="课时长度(分钟)")
    teaching_objectives: List[str] = Field(..., min_items=1, description="教学目标")
    key_points: List[str] = Field(..., min_items=1, description="重点内容")
    difficult_points: List[str] = Field(default=[], description="难点内容")
    teaching_style: TeachingStyle = Field(default=TeachingStyle.TRADITIONAL, description="教学风格")
    materials_needed: List[str] = Field(default=[], description="所需材料")
    content: str = Field(..., min_length=10, description="教案内容")

class AnalysisOptionsRequest(BaseModel):
    """分析选项请求"""
    include_knowledge_points: bool = Field(default=True, description="包含知识点分析")
    include_difficulty: bool = Field(default=True, description="包含难度分析")
    include_suggestions: bool = Field(default=True, description="包含教学建议")
    analysis_depth: str = Field(default="medium", description="分析深度")

class ResourceSearchRequest(BaseModel):
    """资源搜索请求"""
    subject: Optional[SubjectType] = Field(None, description="学科")
    grade_level: Optional[int] = Field(None, ge=1, le=12, description="年级")
    keyword: Optional[str] = Field(None, max_length=100, description="关键词")
    resource_type: Optional[str] = Field(None, description="资源类型")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")

# 响应模型
class KnowledgePoint(BaseModel):
    """知识点"""
    name: str = Field(..., description="知识点名称")
    description: str = Field(..., description="知识点描述")
    difficulty: DifficultyLevel = Field(..., description="难度等级")
    prerequisites: List[str] = Field(default=[], description="前置知识")
    related_points: List[str] = Field(default=[], description="相关知识点")

class TextbookAnalysis(BaseModel):
    """教材分析结果"""
    textbook_id: str = Field(..., description="教材ID")
    subject: SubjectType = Field(..., description="学科")
    grade_level: int = Field(..., description="年级")
    chapter: str = Field(..., description="章节")
    knowledge_points: List[KnowledgePoint] = Field(..., description="知识点列表")
    difficulty_distribution: Dict[str, int] = Field(..., description="难度分布")
    key_concepts: List[str] = Field(..., description="核心概念")
    teaching_suggestions: List[str] = Field(..., description="教学建议")
    estimated_duration: int = Field(..., description="预估课时")
    created_at: datetime = Field(..., description="创建时间")

class LessonPlan(BaseModel):
    """教案"""
    id: str = Field(..., description="教案ID")
    title: str = Field(..., description="标题")
    subject: SubjectType = Field(..., description="学科")
    grade_level: int = Field(..., description="年级")
    duration: int = Field(..., description="课时长度")
    teaching_objectives: List[str] = Field(..., description="教学目标")
    key_points: List[str] = Field(..., description="重点内容")
    difficult_points: List[str] = Field(..., description="难点内容")
    teaching_style: TeachingStyle = Field(..., description="教学风格")
    materials_needed: List[str] = Field(..., description="所需材料")
    content: str = Field(..., description="教案内容")
    status: str = Field(..., description="状态")
    created_by: str = Field(..., description="创建者")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class TeachingResource(BaseModel):
    """教学资源"""
    id: str = Field(..., description="资源ID")
    title: str = Field(..., description="资源标题")
    description: str = Field(..., description="资源描述")
    resource_type: str = Field(..., description="资源类型")
    subject: SubjectType = Field(..., description="学科")
    grade_level: int = Field(..., description="年级")
    file_url: Optional[str] = Field(None, description="文件URL")
    preview_url: Optional[str] = Field(None, description="预览URL")
    download_count: int = Field(default=0, description="下载次数")
    rating: float = Field(default=0.0, description="评分")
    tags: List[str] = Field(default=[], description="标签")
    created_at: datetime = Field(..., description="创建时间")

# ==================== API接口实现 ====================

@router.post("/textbook/upload", response_model=APIResponse[Dict[str, str]])
async def upload_textbook(
    file: UploadFile = File(...),
    subject: SubjectType = Form(...),
    grade_level: int = Form(...),
    chapter: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传教材文件
    
    Args:
        file: 教材文件
        subject: 学科
        grade_level: 年级
        chapter: 章节
        description: 描述
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        上传结果
    """
    try:
        # 验证文件类型
        allowed_types = ["application/pdf", "text/plain", "application/msword", 
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file.content_type not in allowed_types:
            raise ValidationException("不支持的文件类型")
        
        # 验证文件大小 (最大50MB)
        if file.size > 50 * 1024 * 1024:
            raise ValidationException("文件大小不能超过50MB")
        
        # 生成文件ID
        import uuid
        textbook_id = str(uuid.uuid4())
        
        # 这里应该实现文件存储逻辑
        # 暂时返回模拟结果
        
        logger.info(f"用户 {current_user.username} 上传教材: {file.filename}")
        
        return ResponseBuilder.success({
            "textbook_id": textbook_id,
            "upload_status": "success",
            "message": "教材上传成功"
        })
        
    except Exception as e:
        logger.error(f"教材上传失败: {str(e)}")
        raise BusinessException(f"教材上传失败: {str(e)}")

@router.get("/textbook/{textbook_id}/analysis", response_model=APIResponse[TextbookAnalysis])
async def get_textbook_analysis(
    textbook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取教材分析结果
    
    Args:
        textbook_id: 教材ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        教材分析结果
    """
    try:
        # 这里应该从数据库获取教材分析结果
        # 暂时返回模拟数据
        
        analysis = TextbookAnalysis(
            textbook_id=textbook_id,
            subject=SubjectType.MATH,
            grade_level=9,
            chapter="函数的概念与性质",
            knowledge_points=[
                KnowledgePoint(
                    name="函数的定义",
                    description="理解函数的概念和表示方法",
                    difficulty=DifficultyLevel.MEDIUM,
                    prerequisites=["集合", "映射"],
                    related_points=["函数的性质", "函数图像"]
                )
            ],
            difficulty_distribution={"easy": 2, "medium": 5, "hard": 3},
            key_concepts=["函数定义", "定义域", "值域", "函数图像"],
            teaching_suggestions=[
                "从实际问题引入函数概念",
                "通过图像直观理解函数性质",
                "加强练习巩固基础概念"
            ],
            estimated_duration=90,
            created_at=datetime.now()
        )
        
        logger.info(f"用户 {current_user.username} 获取教材分析: {textbook_id}")
        
        return ResponseBuilder.success(analysis)
        
    except Exception as e:
        logger.error(f"获取教材分析失败: {str(e)}")
        raise BusinessException(f"获取教材分析失败: {str(e)}")

@router.post("/textbook/analyze", response_model=APIResponse[TextbookAnalysis])
async def analyze_textbook(
    request: TextbookUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    教材智能分析
    
    Args:
        request: 教材分析请求
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        教材分析结果
    """
    try:
        # 优先使用AI服务集成接口
        try:
            ai_result = await ai_service_client.analyze_material(
                content=request.content,
                subject=request.subject.value,
                grade=str(request.grade_level)
            )
            
            # 转换AI服务返回的结果格式
            analysis = TextbookAnalysis(
                textbook_id=ai_result.get("analysis_id", f"tb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                subject=request.subject,
                grade_level=request.grade_level,
                chapter=request.chapter,
                knowledge_points=[
                    KnowledgePoint(
                        name=kp.get("name", "知识点"),
                        description=kp.get("description", "知识点描述"),
                        difficulty=DifficultyLevel(kp.get("difficulty", "medium")),
                        prerequisites=kp.get("prerequisites", []),
                        related_points=kp.get("related_points", [])
                    ) for kp in ai_result.get("knowledge_points", [])
                ],
                difficulty_distribution=ai_result.get("difficulty_analysis", {"easy": 2, "medium": 5, "hard": 3}),
                key_concepts=ai_result.get("key_concepts", ["核心概念1", "核心概念2"]),
                teaching_suggestions=ai_result.get("teaching_suggestions", [
                    "建议采用循序渐进的教学方法",
                    "可以通过实例加深理解"
                ]),
                estimated_duration=ai_result.get("estimated_duration", 45),
                created_at=datetime.now()
            )
            
        except Exception as ai_error:
            logger.warning(f"AI服务调用失败，使用备用方案: {str(ai_error)}")
            
            # 备用方案：使用原有的教学准备服务
            textbook_content = TextbookContent(
                id=f"tb_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=request.title,
                subject=request.subject,
                grade_level=request.grade_level,
                chapter=request.chapter,
                section=request.section or "第一节",
                content=request.content
            )
            
            analysis_result = await teaching_prep_service.analyze_textbook(textbook_content)
            
            # 构建分析结果
            analysis = TextbookAnalysis(
                textbook_id=textbook_content.id,
                subject=request.subject,
                grade_level=request.grade_level,
                chapter=request.chapter,
                knowledge_points=[
                    KnowledgePoint(
                        name="核心概念",
                        description="本章节的核心概念和原理",
                        difficulty=DifficultyLevel.MEDIUM,
                        prerequisites=["基础知识"],
                        related_points=["相关概念"]
                    )
                ],
                difficulty_distribution={"easy": 2, "medium": 5, "hard": 3},
                key_concepts=["核心概念1", "核心概念2"],
                teaching_suggestions=[
                    "建议采用循序渐进的教学方法",
                    "可以通过实例加深理解"
                ],
                estimated_duration=45,
                created_at=datetime.now()
            )
        
        logger.info(f"用户 {current_user.username} 分析教材: {request.title}")
        
        return ResponseBuilder.success(analysis)
        
    except Exception as e:
        logger.error(f"教材分析失败: {str(e)}")
        raise BusinessException(f"教材分析失败: {str(e)}")

@router.post("/textbook/{textbook_id}/report", response_model=APIResponse[Dict[str, Any]])
async def generate_analysis_report(
    textbook_id: str,
    options: AnalysisOptionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成教材分析报告
    
    Args:
        textbook_id: 教材ID
        options: 分析选项
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        分析报告
    """
    try:
        # 使用AI生成分析报告
        prompt = f"""
        请为教材ID {textbook_id} 生成详细的分析报告。
        分析选项:
        - 包含知识点分析: {options.include_knowledge_points}
        - 包含难度分析: {options.include_difficulty}
        - 包含教学建议: {options.include_suggestions}
        - 分析深度: {options.analysis_depth}
        """
        
        report_content = await ai_client.generate_response(prompt)
        
        import uuid
        report_id = str(uuid.uuid4())
        
        logger.info(f"用户 {current_user.username} 生成教材分析报告: {textbook_id}")
        
        return ResponseBuilder.success({
            "report_id": report_id,
            "report_content": report_content,
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"生成分析报告失败: {str(e)}")
        raise BusinessException(f"生成分析报告失败: {str(e)}")

@router.get("/lesson-plans", response_model=APIResponse[PaginatedResponse[LessonPlan]])
async def get_lesson_plans(
    subject: Optional[SubjectType] = Query(None, description="学科筛选"),
    grade_level: Optional[int] = Query(None, ge=1, le=12, description="年级筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取教案列表
    
    Args:
        subject: 学科筛选
        grade_level: 年级筛选
        page: 页码
        page_size: 每页数量
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        教案列表
    """
    try:
        # 这里应该从数据库查询教案列表
        # 暂时返回模拟数据
        
        lesson_plans = [
            LessonPlan(
                id="plan_001",
                title="函数的概念与性质",
                subject=SubjectType.MATH,
                grade_level=9,
                duration=45,
                teaching_objectives=["理解函数的概念", "掌握函数的表示方法"],
                key_points=["函数定义", "定义域和值域"],
                difficult_points=["抽象函数概念的理解"],
                teaching_style=TeachingStyle.INTERACTIVE,
                materials_needed=["多媒体设备", "函数图像卡片"],
                content="详细的教案内容...",
                status="published",
                created_by=current_user.username,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        total = len(lesson_plans)
        
        paginated_response = PaginatedResponse(
            items=lesson_plans,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
        
        logger.info(f"用户 {current_user.username} 获取教案列表")
        
        return ResponseBuilder.success(paginated_response)
        
    except Exception as e:
        logger.error(f"获取教案列表失败: {str(e)}")
        raise BusinessException(f"获取教案列表失败: {str(e)}")

@router.post("/lesson-plans", response_model=APIResponse[LessonPlan])
async def create_lesson_plan(
    plan_data: LessonPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建教案
    
    Args:
        plan_data: 教案数据
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        创建的教案
    """
    try:
        # 优先使用AI服务集成接口
        try:
            ai_result = await ai_service_client.create_lesson_plan(
                subject=plan_data.subject.value,
                topic=plan_data.title,
                grade=str(plan_data.grade_level),
                objectives=plan_data.teaching_objectives
            )
            
            # 转换AI服务返回的结果格式
            lesson_plan = LessonPlan(
                id=ai_result.get("plan_id", f"plan_{int(time.time())}"),
                title=ai_result.get("title", plan_data.title),
                subject=plan_data.subject,
                grade_level=plan_data.grade_level,
                duration=plan_data.duration,
                teaching_objectives=ai_result.get("objectives", plan_data.teaching_objectives),
                key_points=plan_data.key_points,
                difficult_points=plan_data.difficult_points,
                teaching_style=plan_data.teaching_style,
                materials_needed=ai_result.get("materials", plan_data.materials_needed),
                content=ai_result.get("content", plan_data.content),
                status="draft",
                created_by=current_user.username,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
        except Exception as ai_error:
            logger.warning(f"AI服务调用失败，使用备用方案: {str(ai_error)}")
            
            # 备用方案：使用原有的教学准备服务
            import uuid
            plan_id = str(uuid.uuid4())
            
            lesson_plan = LessonPlan(
                id=plan_id,
                title=plan_data.title,
                subject=plan_data.subject,
                grade_level=plan_data.grade_level,
                duration=plan_data.duration,
                teaching_objectives=plan_data.teaching_objectives,
                key_points=plan_data.key_points,
                difficult_points=plan_data.difficult_points,
                teaching_style=plan_data.teaching_style,
                materials_needed=plan_data.materials_needed,
                content=plan_data.content,
                status="draft",
                created_by=current_user.username,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        logger.info(f"用户 {current_user.username} 创建教案: {plan_data.title}")
        
        return ResponseBuilder.success(lesson_plan)
        
    except Exception as e:
        logger.error(f"创建教案失败: {str(e)}")
        raise BusinessException(f"创建教案失败: {str(e)}")

@router.get("/lesson-plans/{plan_id}", response_model=APIResponse[LessonPlan])
async def get_lesson_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取教案详情
    
    Args:
        plan_id: 教案ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        教案详情
    """
    try:
        # 这里应该从数据库查询教案详情
        # 暂时返回模拟数据
        
        lesson_plan = LessonPlan(
            id=plan_id,
            title="函数的概念与性质",
            subject=SubjectType.MATH,
            grade_level=9,
            duration=45,
            teaching_objectives=["理解函数的概念", "掌握函数的表示方法"],
            key_points=["函数定义", "定义域和值域"],
            difficult_points=["抽象函数概念的理解"],
            teaching_style=TeachingStyle.INTERACTIVE,
            materials_needed=["多媒体设备", "函数图像卡片"],
            content="详细的教案内容...",
            status="published",
            created_by=current_user.username,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        logger.info(f"用户 {current_user.username} 获取教案详情: {plan_id}")
        
        return ResponseBuilder.success(lesson_plan)
        
    except Exception as e:
        logger.error(f"获取教案详情失败: {str(e)}")
        raise ResourceNotFoundException(f"教案不存在: {plan_id}")

@router.put("/lesson-plans/{plan_id}", response_model=APIResponse[LessonPlan])
async def update_lesson_plan(
    plan_id: str,
    plan_data: LessonPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新教案
    
    Args:
        plan_id: 教案ID
        plan_data: 教案数据
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        更新后的教案
    """
    try:
        # 这里应该更新数据库中的教案
        # 暂时返回模拟数据
        
        lesson_plan = LessonPlan(
            id=plan_id,
            title=plan_data.title,
            subject=plan_data.subject,
            grade_level=plan_data.grade_level,
            duration=plan_data.duration,
            teaching_objectives=plan_data.teaching_objectives,
            key_points=plan_data.key_points,
            difficult_points=plan_data.difficult_points,
            teaching_style=plan_data.teaching_style,
            materials_needed=plan_data.materials_needed,
            content=plan_data.content,
            status="updated",
            created_by=current_user.username,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        logger.info(f"用户 {current_user.username} 更新教案: {plan_id}")
        
        return ResponseBuilder.success(lesson_plan)
        
    except Exception as e:
        logger.error(f"更新教案失败: {str(e)}")
        raise BusinessException(f"更新教案失败: {str(e)}")

@router.delete("/lesson-plans/{plan_id}", response_model=APIResponse[Dict[str, str]])
async def delete_lesson_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除教案
    
    Args:
        plan_id: 教案ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        删除结果
    """
    try:
        # 这里应该从数据库删除教案
        
        logger.info(f"用户 {current_user.username} 删除教案: {plan_id}")
        
        return ResponseBuilder.success({
            "message": "教案删除成功",
            "plan_id": plan_id
        })
        
    except Exception as e:
        logger.error(f"删除教案失败: {str(e)}")
        raise BusinessException(f"删除教案失败: {str(e)}")

@router.get("/resources", response_model=APIResponse[PaginatedResponse[TeachingResource]])
async def search_teaching_resources(
    search_params: ResourceSearchRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    搜索教学资源
    
    Args:
        search_params: 搜索参数
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        教学资源列表
    """
    try:
        # 这里应该从数据库搜索教学资源
        # 暂时返回模拟数据
        
        resources = [
            TeachingResource(
                id="resource_001",
                title="函数图像动画演示",
                description="生动的函数图像变化动画，帮助学生理解函数性质",
                resource_type="animation",
                subject=SubjectType.MATH,
                grade_level=9,
                file_url="/files/function_animation.mp4",
                preview_url="/previews/function_animation.jpg",
                download_count=156,
                rating=4.8,
                tags=["函数", "图像", "动画"],
                created_at=datetime.now()
            )
        ]
        
        total = len(resources)
        
        paginated_response = PaginatedResponse(
            items=resources,
            total=total,
            page=search_params.page,
            page_size=search_params.page_size,
            pages=(total + search_params.page_size - 1) // search_params.page_size
        )
        
        logger.info(f"用户 {current_user.username} 搜索教学资源")
        
        return ResponseBuilder.success(paginated_response)
        
    except Exception as e:
        logger.error(f"搜索教学资源失败: {str(e)}")
        raise BusinessException(f"搜索教学资源失败: {str(e)}")

@router.post("/lesson/plan", response_model=APIResponse[Dict[str, Any]])
async def generate_teaching_plan(
    request: LessonPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI生成教学计划
    
    Args:
        request: 教学计划请求
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        生成的教学计划
    """
    try:
        # 调用教学计划生成服务
        plan_result = await teaching_prep_service.generate_teaching_plan(
            subject=request.subject.value,
            grade_level=request.grade_level,
            title=request.title,
            objectives=request.teaching_objectives,
            key_points=request.key_points,
            difficult_points=request.difficult_points,
            teaching_style=request.teaching_style.value,
            duration=request.duration
        )
        
        logger.info(f"用户 {current_user.username} 生成教学计划: {request.title}")
        
        return ResponseBuilder.success({
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": request.title,
            "generated_plan": plan_result.get("plan", "生成的教学计划"),
            "activities": plan_result.get("activities", []),
            "assessment": plan_result.get("assessment", {}),
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"生成教学计划失败: {str(e)}")
        raise BusinessException(f"生成教学计划失败: {str(e)}")

@router.post("/ai/generate-content", response_model=APIResponse[Dict[str, Any]])
async def generate_teaching_content(
    content_type: str = Query(..., description="内容类型"),
    topic: str = Query(..., description="主题"),
    grade_level: int = Query(..., ge=1, le=12, description="年级"),
    subject: SubjectType = Query(..., description="学科"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI生成教学内容
    
    Args:
        content_type: 内容类型(lesson_plan, exercise, explanation)
        topic: 主题
        grade_level: 年级
        subject: 学科
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        生成的教学内容
    """
    try:
        # 使用AI生成教学内容
        teaching_agent = agent_manager.get_agent("teaching_analysis")
        
        result = await teaching_agent.execute_task(
            task_type="generate_content",
            content_type=content_type,
            topic=topic,
            grade_level=grade_level,
            subject=subject.value
        )
        
        logger.info(f"用户 {current_user.username} 生成教学内容: {topic}")
        
        return ResponseBuilder.success({
            "content_type": content_type,
            "topic": topic,
            "generated_content": result.get("result", "生成的教学内容"),
            "suggestions": result.get("suggestions", []),
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"生成教学内容失败: {str(e)}")
        raise BusinessException(f"生成教学内容失败: {str(e)}")

@router.get("/health", response_model=APIResponse[Dict[str, str]])
async def health_check():
    """
    健康检查接口
    
    Returns:
        服务状态
    """
    return ResponseBuilder.success({
        "status": "healthy",
        "service": "teaching-prep",
        "timestamp": datetime.now().isoformat()
    })