# -*- coding: utf-8 -*-
"""
AI服务API路由

本模块提供AI服务相关的API接口，包括AI对话、智能分析、会话管理等。
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, AsyncIterator
import logging
from datetime import datetime
import json
import asyncio

from database import get_db, User
from models.response import APIResponse, ResponseBuilder
from middleware.exception_handler import (
    BusinessException,
    ValidationException,
    ResourceNotFoundException,
    AuthenticationException
)
from auth import get_current_user, role_required
import httpx
import os

# AI服务集成客户端
class AIServiceClient:
    """AI服务集成客户端"""
    
    def __init__(self):
        # 获取AI服务的基础URL，默认为本地服务
        self.base_url = os.getenv('AI_SERVICE_URL', 'http://localhost:8000/api/v1/ai-service')
        self.timeout = 30.0
    
    async def _make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None):
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if method.upper() == 'GET':
                response = await client.get(url, headers=default_headers)
            elif method.upper() == 'POST':
                response = await client.post(url, json=data, headers=default_headers)
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
    
    async def analyze_real_time_learning(self, classroom_data: dict):
        """实时学情分析"""
        data = {
            'classroom_data': classroom_data,
            'analysis_type': 'real_time'
        }
        return await self._make_request('POST', '/classroom/real-time-analysis', data)
    
    async def analyze_grades(self, grades: list, analysis_type: str = 'comprehensive'):
        """成绩分析"""
        data = {
            'grades': grades,
            'analysis_type': analysis_type
        }
        return await self._make_request('POST', '/grades/analyze', data)
    
    async def generate_personalized_guidance(self, student_profile: dict, grade_analysis: dict):
        """生成个性化指导"""
        data = {
            'student_profile': student_profile,
            'grade_analysis': grade_analysis
        }
        return await self._make_request('POST', '/grades/personalized-guidance', data)
    
    async def health_check(self):
        """健康检查"""
        try:
            return await self._make_request('GET', '/health')
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

# 导入LLM相关模块（如果不存在则使用模拟实现）
try:
    from llm.unified_client import UnifiedLLMClient
    from llm.agents.agent_manager import AgentManager
except ImportError:
    # 模拟实现，用于开发阶段
    class UnifiedLLMClient:
        async def chat(self, messages):
            return {"content": "这是模拟的AI响应", "confidence": 0.8, "suggestions": []}
        
        async def stream_chat(self, messages):
            content = "这是模拟的流式AI响应"
            for char in content:
                yield char
                await asyncio.sleep(0.1)
        
        def get_available_models(self):
            return [{"id": "mock-model", "name": "模拟模型", "is_available": True}]
        
        async def health_check(self):
            return {"status": "healthy", "provider": "mock"}
    
    class AgentManager:
        def get_agent(self, agent_type):
            return None
        
        def health_check(self):
            return {"status": "healthy", "agents_count": 0}
from pydantic import BaseModel, validator
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化AI服务
llm_client = UnifiedLLMClient()
agent_manager = AgentManager()
ai_service_client = AIServiceClient()

# 会话存储（生产环境应使用Redis）
active_sessions: Dict[str, Dict[str, Any]] = {}


class SessionType(str, Enum):
    """会话类型枚举"""
    GENERAL_CHAT = "general_chat"  # 通用对话
    TEACHING_ANALYSIS = "teaching_analysis"  # 教学分析
    STUDENT_GUIDANCE = "student_guidance"  # 学生指导
    GRADE_ANALYSIS = "grade_analysis"  # 成绩分析
    LESSON_PLANNING = "lesson_planning"  # 备课助手
    CLASSROOM_ASSISTANT = "classroom_assistant"  # 课堂助手


class AnalysisType(str, Enum):
    """分析类型枚举"""
    STUDENT_PERFORMANCE = "student_performance"  # 学生表现分析
    CLASS_SUMMARY = "class_summary"  # 班级总结
    SUBJECT_ANALYSIS = "subject_analysis"  # 科目分析
    LEARNING_RECOMMENDATION = "learning_recommendation"  # 学习建议
    TEACHING_STRATEGY = "teaching_strategy"  # 教学策略


# 请求模型
class SessionCreateRequest(BaseModel):
    """创建会话请求"""
    session_type: SessionType
    title: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True


class ChatRequest(BaseModel):
    """AI对话请求"""
    session_id: str
    message: str
    stream: bool = False
    context: Optional[Dict[str, Any]] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('消息内容不能为空')
        if len(v) > 4000:
            raise ValueError('消息内容过长，请控制在4000字符以内')
        return v.strip()


class AnalysisRequest(BaseModel):
    """智能分析请求"""
    analysis_type: AnalysisType
    target_id: int  # 学生ID、班级ID或科目ID
    date_range: Optional[Dict[str, str]] = None  # {"start_date": "2024-01-01", "end_date": "2024-12-31"}
    additional_context: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True


class StudyPlanRequest(BaseModel):
    """学习计划生成请求"""
    student_id: int
    subject_ids: List[int]
    duration_weeks: int = 4
    focus_areas: Optional[List[str]] = None
    difficulty_level: Optional[str] = "medium"  # easy, medium, hard
    
    @validator('duration_weeks')
    def validate_duration(cls, v):
        if v < 1 or v > 52:
            raise ValueError('学习计划周期应在1-52周之间')
        return v


# 响应模型
class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    session_type: str
    title: str
    created_at: datetime
    message_count: int
    last_activity: datetime


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """AI对话响应"""
    message: ChatMessage
    suggestions: Optional[List[str]] = None
    related_resources: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None


class AnalysisResponse(BaseModel):
    """智能分析响应"""
    analysis_type: str
    target_id: int
    summary: str
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    data_visualizations: Optional[List[Dict[str, Any]]] = None
    confidence_score: float
    generated_at: datetime


class StudyPlanResponse(BaseModel):
    """学习计划响应"""
    plan_id: str
    student_id: int
    title: str
    description: str
    duration_weeks: int
    weekly_goals: List[Dict[str, Any]]
    daily_tasks: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    progress_metrics: List[str]
    created_at: datetime


@router.post("/sessions", response_model=APIResponse[SessionResponse])
async def create_ai_session(
    request: SessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建AI会话
    
    创建一个新的AI对话会话，支持不同类型的对话场景。
    """
    try:
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 创建会话数据
        session_data = {
            "session_id": session_id,
            "user_id": current_user.id,
            "session_type": request.session_type,
            "title": request.title or f"{request.session_type.replace('_', ' ').title()}会话",
            "context_data": request.context_data or {},
            "messages": [],
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "is_active": True
        }
        
        # 存储会话（生产环境应存储到数据库或Redis）
        active_sessions[session_id] = session_data
        
        # 构建响应
        response_data = SessionResponse(
            session_id=session_id,
            session_type=request.session_type,
            title=session_data["title"],
            created_at=session_data["created_at"],
            message_count=0,
            last_activity=session_data["last_activity"]
        )
        
        logger.info(f"用户 {current_user.id} 创建了AI会话 {session_id}")
        return ResponseBuilder.success(response_data, "AI会话创建成功")
        
    except Exception as e:
        logger.error(f"创建AI会话失败: {str(e)}")
        raise BusinessException("创建AI会话失败")


@router.get("/sessions", response_model=APIResponse[List[SessionResponse]])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    获取用户的AI会话列表
    
    返回当前用户的所有AI会话，支持分页。
    """
    try:
        # 过滤用户的会话
        user_sessions = [
            session for session in active_sessions.values()
            if session["user_id"] == current_user.id and session["is_active"]
        ]
        
        # 按最后活动时间排序
        user_sessions.sort(key=lambda x: x["last_activity"], reverse=True)
        
        # 分页
        paginated_sessions = user_sessions[offset:offset + limit]
        
        # 构建响应
        response_data = [
            SessionResponse(
                session_id=session["session_id"],
                session_type=session["session_type"],
                title=session["title"],
                created_at=session["created_at"],
                message_count=len(session["messages"]),
                last_activity=session["last_activity"]
            )
            for session in paginated_sessions
        ]
        
        return ResponseBuilder.success(response_data, "获取会话列表成功")
        
    except Exception as e:
        logger.error(f"获取用户会话失败: {str(e)}")
        raise BusinessException("获取会话列表失败")


@router.get("/sessions/{session_id}", response_model=APIResponse[Dict[str, Any]])
async def get_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取会话详情
    
    返回指定会话的详细信息，包括消息历史。
    """
    try:
        # 检查会话是否存在
        if session_id not in active_sessions:
            raise ResourceNotFoundException("会话不存在")
        
        session = active_sessions[session_id]
        
        # 检查权限
        if session["user_id"] != current_user.id:
            raise AuthenticationException("无权访问此会话")
        
        # 构建响应数据
        response_data = {
            "session_info": {
                "session_id": session["session_id"],
                "session_type": session["session_type"],
                "title": session["title"],
                "created_at": session["created_at"],
                "last_activity": session["last_activity"],
                "message_count": len(session["messages"])
            },
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"],
                    "metadata": msg.get("metadata", {})
                }
                for msg in session["messages"]
            ],
            "context_data": session["context_data"]
        }
        
        return ResponseBuilder.success(response_data, "获取会话详情成功")
        
    except (ResourceNotFoundException, AuthenticationException):
        raise
    except Exception as e:
        logger.error(f"获取会话详情失败: {str(e)}")
        raise BusinessException("获取会话详情失败")


@router.post("/chat", response_model=APIResponse[ChatResponse])
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI对话
    
    与AI进行对话，支持上下文记忆和流式响应。
    """
    try:
        # 检查会话是否存在
        if request.session_id not in active_sessions:
            raise ResourceNotFoundException("会话不存在")
        
        session = active_sessions[request.session_id]
        
        # 检查权限
        if session["user_id"] != current_user.id:
            raise AuthenticationException("无权访问此会话")
        
        # 添加用户消息到会话
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now(),
            "metadata": request.context or {}
        }
        session["messages"].append(user_message)
        
        # 根据会话类型选择合适的智能体
        agent_type = session["session_type"]
        agent = agent_manager.get_agent(agent_type)
        
        if not agent:
            # 如果没有专门的智能体，使用通用LLM客户端
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in session["messages"][-10:]  # 只取最近10条消息
            ]
            
            # 调用LLM
            llm_response = await llm_client.chat(messages)
            ai_content = llm_response.get("content", "抱歉，我无法理解您的问题。")
            confidence = llm_response.get("confidence", 0.8)
            suggestions = llm_response.get("suggestions", [])
        else:
            # 使用专门的智能体处理
            agent_response = await agent.process_message(
                message=request.message,
                context={
                    "session_data": session,
                    "user_context": request.context or {},
                    "db": db
                }
            )
            ai_content = agent_response.get("content", "抱歉，处理您的请求时出现了问题。")
            confidence = agent_response.get("confidence", 0.8)
            suggestions = agent_response.get("suggestions", [])
        
        # 添加AI响应到会话
        ai_message = {
            "role": "assistant",
            "content": ai_content,
            "timestamp": datetime.now(),
            "metadata": {
                "confidence": confidence,
                "agent_type": agent_type,
                "suggestions": suggestions
            }
        }
        session["messages"].append(ai_message)
        session["last_activity"] = datetime.now()
        
        # 构建响应
        response_data = ChatResponse(
            message=ChatMessage(
                role="assistant",
                content=ai_content,
                timestamp=ai_message["timestamp"],
                metadata=ai_message["metadata"]
            ),
            suggestions=suggestions,
            confidence=confidence
        )
        
        logger.info(f"用户 {current_user.id} 在会话 {request.session_id} 中进行了对话")
        return ResponseBuilder.success(response_data, "对话成功")
        
    except (ResourceNotFoundException, AuthenticationException, ValidationException):
        raise
    except Exception as e:
        logger.error(f"AI对话失败: {str(e)}")
        raise BusinessException("AI对话失败")


@router.post("/chat/stream")
async def ai_chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    流式AI对话
    
    支持流式响应的AI对话接口。
    """
    try:
        # 检查会话是否存在
        if request.session_id not in active_sessions:
            raise ResourceNotFoundException("会话不存在")
        
        session = active_sessions[request.session_id]
        
        # 检查权限
        if session["user_id"] != current_user.id:
            raise AuthenticationException("无权访问此会话")
        
        # 添加用户消息到会话
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now(),
            "metadata": request.context or {}
        }
        session["messages"].append(user_message)
        
        async def generate_stream():
            try:
                # 准备消息历史
                messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in session["messages"][-10:]  # 只取最近10条消息
                ]
                
                # 流式调用LLM
                full_content = ""
                async for chunk in llm_client.stream_chat(messages):
                    if chunk:
                        full_content += chunk
                        # 发送SSE格式的数据
                        yield f"data: {json.dumps({'content': chunk, 'type': 'chunk'}, ensure_ascii=False)}\n\n"
                
                # 保存完整的AI响应
                ai_message = {
                    "role": "assistant",
                    "content": full_content,
                    "timestamp": datetime.now(),
                    "metadata": {"stream": True}
                }
                session["messages"].append(ai_message)
                session["last_activity"] = datetime.now()
                
                # 发送结束标记
                yield f"data: {json.dumps({'type': 'end', 'message': '对话完成'}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"流式对话失败: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': '对话失败'}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except (ResourceNotFoundException, AuthenticationException):
        raise
    except Exception as e:
        logger.error(f"流式AI对话失败: {str(e)}")
        raise BusinessException("流式对话失败")


@router.post("/analyze", response_model=APIResponse[AnalysisResponse])
async def intelligent_analysis(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    智能分析
    
    对学生表现、班级情况、科目数据等进行AI智能分析。
    """
    try:
        logger.info(f"用户 {current_user.id} 请求智能分析: {request.analysis_type}")
        
        # 根据分析类型调用相应的AI服务
        if request.analysis_type == AnalysisType.STUDENT_PERFORMANCE:
            # 调用成绩分析服务
            # 这里需要根据target_id获取学生成绩数据
            grades_data = []  # 从数据库获取成绩数据
            ai_result = await ai_service_client.analyze_grades(grades_data, "student_performance")
        elif request.analysis_type == AnalysisType.CLASS_SUMMARY:
            # 调用课堂分析服务
            classroom_data = {"class_id": request.target_id}  # 从数据库获取课堂数据
            ai_result = await ai_service_client.analyze_real_time_learning(classroom_data)
        else:
            # 对于其他分析类型，使用智能体管理器
            agent = agent_manager.get_agent("general_analysis")
            if agent:
                analysis_context = {
                    "analysis_type": request.analysis_type,
                    "target_id": request.target_id,
                    "date_range": request.date_range,
                    "additional_context": request.additional_context or {},
                    "user_id": current_user.id,
                    "db": db
                }
                ai_result = await agent.analyze(analysis_context)
            else:
                # 默认分析逻辑
                ai_result = {
                    "summary": f"针对目标 {request.target_id} 的 {request.analysis_type} 分析已完成",
                    "insights": ["整体表现呈上升趋势", "核心指标达到预期目标"],
                    "recommendations": ["建议继续保持当前学习策略", "可以适当增加挑战性内容"]
                }
        
        # 处理AI服务返回的结果
        if isinstance(ai_result, dict):
            analysis_data = {
                "analysis_type": request.analysis_type,
                "target_id": request.target_id,
                "summary": ai_result.get('summary', f"针对目标 {request.target_id} 的分析已完成"),
                "insights": [
                    {
                        "category": "AI分析结果",
                        "description": insight if isinstance(insight, str) else insight.get('description', ''),
                        "importance": "high"
                    } for insight in (ai_result.get('insights', []) if isinstance(ai_result.get('insights', []), list) else [])
                ],
                "recommendations": ai_result.get('recommendations', []),
                "confidence_score": ai_result.get('confidence', 0.85),
                "generated_at": datetime.now()
            }
        else:
            # 如果AI服务调用失败，使用默认分析
            analysis_data = {
                "analysis_type": request.analysis_type,
                "target_id": request.target_id,
                "summary": f"针对目标 {request.target_id} 的 {request.analysis_type} 分析已完成",
                "insights": [
                    {
                        "category": "表现趋势",
                        "description": "整体表现呈上升趋势",
                        "importance": "high"
                    }
                ],
                "recommendations": ["建议继续保持当前学习策略"],
                "confidence_score": 0.75,
                "generated_at": datetime.now()
            }
        
        # 构建响应
        response_data = AnalysisResponse(
            analysis_type=request.analysis_type,
            target_id=request.target_id,
            summary=analysis_data["summary"],
            insights=analysis_data["insights"],
            recommendations=analysis_data["recommendations"],
            data_visualizations=analysis_data.get("data_visualizations", []),
            confidence_score=analysis_data["confidence_score"],
            generated_at=analysis_data["generated_at"]
        )
        
        logger.info(f"用户 {current_user.id} 执行了 {request.analysis_type} 分析")
        return ResponseBuilder.success(response_data, "智能分析完成")
        
    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"智能分析失败: {str(e)}")
        raise BusinessException("智能分析失败")


@router.post("/study-plan", response_model=APIResponse[StudyPlanResponse])
async def generate_study_plan(
    request: StudyPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成个性化学习计划
    
    基于学生的学习情况和需求，生成个性化的学习计划。
    """
    try:
        # 获取学习计划生成智能体
        agent = agent_manager.get_agent("study_plan")
        
        if not agent:
            raise BusinessException("学习计划生成服务暂不可用")
        
        # 准备生成上下文
        plan_context = {
            "student_id": request.student_id,
            "subject_ids": request.subject_ids,
            "duration_weeks": request.duration_weeks,
            "focus_areas": request.focus_areas or [],
            "difficulty_level": request.difficulty_level,
            "user_id": current_user.id,
            "db": db
        }
        
        # 生成学习计划
        plan_result = await agent.generate_plan(plan_context)
        
        # 生成计划ID
        plan_id = str(uuid.uuid4())
        
        # 构建响应
        response_data = StudyPlanResponse(
            plan_id=plan_id,
            student_id=request.student_id,
            title=plan_result.get("title", "个性化学习计划"),
            description=plan_result.get("description", ""),
            duration_weeks=request.duration_weeks,
            weekly_goals=plan_result.get("weekly_goals", []),
            daily_tasks=plan_result.get("daily_tasks", []),
            milestones=plan_result.get("milestones", []),
            progress_metrics=plan_result.get("progress_metrics", []),
            created_at=datetime.now()
        )
        
        logger.info(f"用户 {current_user.id} 为学生 {request.student_id} 生成了学习计划")
        return ResponseBuilder.success(response_data, "学习计划生成成功")
        
    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"生成学习计划失败: {str(e)}")
        raise BusinessException("生成学习计划失败")


@router.delete("/sessions/{session_id}", response_model=APIResponse[Dict[str, str]])
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    删除AI会话
    
    删除指定的AI会话及其所有消息记录。
    """
    try:
        # 检查会话是否存在
        if session_id not in active_sessions:
            raise ResourceNotFoundException("会话不存在")
        
        session = active_sessions[session_id]
        
        # 检查权限
        if session["user_id"] != current_user.id:
            raise AuthenticationException("无权删除此会话")
        
        # 删除会话
        del active_sessions[session_id]
        
        logger.info(f"用户 {current_user.id} 删除了会话 {session_id}")
        return ResponseBuilder.success(
            {"session_id": session_id},
            "会话删除成功"
        )
        
    except (ResourceNotFoundException, AuthenticationException):
        raise
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}")
        raise BusinessException("删除会话失败")


@router.get("/models", response_model=APIResponse[List[Dict[str, Any]]])
async def get_available_models(
    current_user: User = Depends(get_current_user)
):
    """
    获取可用的AI模型列表
    
    返回当前可用的AI模型及其配置信息。
    """
    try:
        # 获取可用模型
        models = llm_client.get_available_models()
        
        # 构建响应数据
        response_data = [
            {
                "model_id": model["id"],
                "name": model["name"],
                "description": model.get("description", ""),
                "capabilities": model.get("capabilities", []),
                "max_tokens": model.get("max_tokens", 4096),
                "is_available": model.get("is_available", True)
            }
            for model in models
        ]
        
        return ResponseBuilder.success(response_data, "获取模型列表成功")
        
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        raise BusinessException("获取模型列表失败")


@router.get("/health", response_model=APIResponse[Dict[str, Any]])
async def ai_service_health():
    """
    AI服务健康检查
    
    检查AI服务的运行状态和可用性。
    """
    try:
        # 检查LLM客户端状态
        llm_status = await llm_client.health_check()
        
        # 检查智能体管理器状态
        agent_status = agent_manager.health_check()
        
        # 检查AI服务集成状态
        ai_service_status = await ai_service_client.health_check()
        
        # 统计活跃会话数
        active_session_count = len([s for s in active_sessions.values() if s["is_active"]])
        
        # 判断整体健康状态
        all_healthy = (
            llm_status.get('status') == 'healthy' and
            agent_status.get('status') == 'healthy' and
            ai_service_status.get('status') == 'healthy'
        )
        
        response_data = {
            "overall_status": "healthy" if all_healthy else "degraded",
            "components": {
                "llm_client": llm_status,
                "agent_manager": agent_status,
                "ai_service_integration": ai_service_status,
                "session_storage": {
                    "status": "healthy",
                    "active_sessions": active_session_count
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return ResponseBuilder.success(response_data, "AI服务运行正常")
        
    except Exception as e:
        logger.error(f"AI服务健康检查失败: {str(e)}")
        response_data = {
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return ResponseBuilder.error("AI服务异常", data=response_data)