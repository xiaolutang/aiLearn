# -*- coding: utf-8 -*-
"""
课堂管理API路由

本模块提供课堂管理相关的API接口，包括课堂创建、学生管理、课堂活动、实时互动等功能。"""

from fastapi import APIRouter, Depends, Query, Request, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import json
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

from database import get_db, User
from models.response import APIResponse, ResponseBuilder, PaginatedResponse
from middleware.exception_handler import BusinessException, ValidationException, ResourceNotFoundException
from auth import get_current_user

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

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, classroom_id: str):
        await websocket.accept()
        if classroom_id not in self.active_connections:
            self.active_connections[classroom_id] = []
        self.active_connections[classroom_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, classroom_id: str):
        if classroom_id in self.active_connections:
            self.active_connections[classroom_id].remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str, classroom_id: str):
        if classroom_id in self.active_connections:
            for connection in self.active_connections[classroom_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

# ==================== 数据模型定义 ====================

class ClassroomStatus(str, Enum):
    """课堂状态枚举"""
    PREPARING = "preparing"  # 准备中
    ACTIVE = "active"  # 进行中
    PAUSED = "paused"  # 暂停
    ENDED = "ended"  # 已结束

class StudentEngagement(str, Enum):
    """学生参与度枚举"""
    HIGH = "high"  # 高
    MEDIUM = "medium"  # 中
    LOW = "low"  # 低

class MessageType(str, Enum):
    """消息类型枚举"""
    TEXT = "text"  # 文本
    IMAGE = "image"  # 图片
    AUDIO = "audio"  # 音频
    VIDEO = "video"  # 视频
    FILE = "file"  # 文件
    SYSTEM = "system"  # 系统消息
    AI_RESPONSE = "ai_response"  # AI回复

class AttentionLevel(str, Enum):
    """专注度等级枚举"""
    VERY_HIGH = "very_high"  # 非常专注
    HIGH = "high"  # 专注
    MEDIUM = "medium"  # 一般
    LOW = "low"  # 不专注
    VERY_LOW = "very_low"  # 非常不专注

class QuestionType(str, Enum):
    """题目类型枚举"""
    MULTIPLE_CHOICE = "multiple_choice"  # 选择题
    TRUE_FALSE = "true_false"  # 判断题
    FILL_BLANK = "fill_blank"  # 填空题
    SHORT_ANSWER = "short_answer"  # 简答题
    ESSAY = "essay"  # 论述题

class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    EASY = "easy"  # 简单
    MEDIUM = "medium"  # 中等
    HARD = "hard"  # 困难

class InteractionType(str, Enum):
    """互动类型枚举"""
    QUIZ = "quiz"  # 随堂测验
    POLL = "poll"  # 投票
    DISCUSSION = "discussion"  # 讨论
    BRAINSTORM = "brainstorm"  # 头脑风暴
    Q_AND_A = "q_and_a"  # 问答
    QUESTION = "question"  # 提问
    EXPERIMENT = "experiment"  # 实验
    AI_ASSISTANT = "ai_assistant"  # AI助手

class ExperimentType(str, Enum):
    """实验类型枚举"""
    PHYSICS = "physics"  # 物理实验
    CHEMISTRY = "chemistry"  # 化学实验
    BIOLOGY = "biology"  # 生物实验
    VIRTUAL = "virtual"  # 虚拟实验

# ==================== 请求模型 ====================

class ClassroomCreateRequest(BaseModel):
    """创建课堂请求"""
    name: str = Field(..., min_length=1, max_length=100, description="课堂名称")
    subject: str = Field(..., description="学科")
    grade: str = Field(..., description="年级")
    class_id: str = Field(..., description="班级ID")
    scheduled_time: datetime = Field(..., description="计划开始时间")
    duration_minutes: int = Field(..., ge=10, le=300, description="课堂时长(分钟)")
    description: Optional[str] = Field(None, max_length=500, description="课堂描述")
    lesson_plan_id: Optional[str] = Field(None, description="教案ID")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('课堂名称不能为空')
        return v.strip()

class StudentResponseRequest(BaseModel):
    """学生回答请求"""
    interaction_id: str = Field(..., description="互动ID")
    response: str = Field(..., description="回答内容")
    response_time: Optional[datetime] = Field(None, description="回答时间")
    confidence_level: Optional[float] = Field(None, ge=0, le=1, description="置信度")

class AttendanceRequest(BaseModel):
    """考勤请求"""
    student_ids: List[str] = Field(..., description="学生ID列表")
    attendance_type: str = Field(..., description="考勤类型")
    notes: Optional[str] = Field(None, description="备注")

class ClassroomAnalysisRequest(BaseModel):
    """课堂分析请求"""
    analysis_type: str = Field(..., description="分析类型")
    time_range: Optional[Dict[str, datetime]] = Field(None, description="时间范围")
    metrics: List[str] = Field(..., description="分析指标")

class AIAssistantRequest(BaseModel):
    """AI助手请求"""
    question: str = Field(..., min_length=1, max_length=1000, description="问题")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    student_id: Optional[str] = Field(None, description="学生ID")
    interaction_type: str = Field(default="question", description="交互类型")
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('问题不能为空')
        return v.strip()

class ClassroomMessageRequest(BaseModel):
    """课堂消息请求"""
    message_type: MessageType = Field(..., description="消息类型")
    content: str = Field(..., description="消息内容")
    target_type: str = Field(..., description="目标类型: all, student, teacher")
    target_ids: Optional[List[str]] = Field(None, description="目标ID列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class StudentAttentionRequest(BaseModel):
    """学生专注度请求"""
    student_id: str = Field(..., description="学生ID")
    attention_level: AttentionLevel = Field(..., description="专注度等级")
    timestamp: datetime = Field(..., description="时间戳")
    notes: Optional[str] = Field(None, description="备注")

class ClassroomSettingsRequest(BaseModel):
    """课堂设置请求"""
    allow_chat: bool = Field(default=True, description="允许聊天")
    allow_screen_share: bool = Field(default=False, description="允许屏幕共享")
    auto_record: bool = Field(default=False, description="自动录制")
    ai_assistant_enabled: bool = Field(default=True, description="启用AI助手")
    interaction_mode: str = Field(default="open", description="互动模式")
    settings: Optional[Dict[str, Any]] = Field(None, description="其他设置")

class QuestionInfo(BaseModel):
    """题目信息"""
    question_text: str = Field(..., min_length=1, description="题目内容")
    question_type: QuestionType = Field(..., description="题目类型")
    options: Optional[List[str]] = Field(None, description="选项(选择题用)")
    correct_answer: str = Field(..., description="正确答案")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="难度等级")
    knowledge_points: List[str] = Field(default=[], description="涉及知识点")
    time_limit: Optional[int] = Field(None, ge=1, description="时间限制(秒)")

class StudentAnswer(BaseModel):
    """学生答案"""
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    answer: str = Field(..., description="学生答案")
    answer_time: Optional[int] = Field(None, description="答题时间(秒)")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="答题信心度")

class QuestionAnalysisRequest(BaseModel):
    """题目分析请求"""
    question_info: QuestionInfo = Field(..., description="题目信息")
    student_answers: List[StudentAnswer] = Field(..., min_items=1, description="学生答案列表")
    class_id: int = Field(..., description="班级ID")
    session_id: Optional[str] = Field(None, description="课堂会话ID")

class InteractionRequest(BaseModel):
    """课堂互动请求"""
    interaction_type: InteractionType = Field(..., description="互动类型")
    title: str = Field(..., min_length=1, max_length=200, description="互动标题")
    content: str = Field(..., min_length=1, description="互动内容")
    class_id: int = Field(..., description="班级ID")
    duration: Optional[int] = Field(None, ge=1, description="持续时间(分钟)")
    options: Optional[List[str]] = Field(None, description="选项(投票/测验用)")
    anonymous: bool = Field(default=False, description="是否匿名")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('互动标题不能为空')
        return v.strip()

class ExperimentDesignRequest(BaseModel):
    """实验设计请求"""
    experiment_name: str = Field(..., min_length=1, max_length=200, description="实验名称")
    experiment_type: ExperimentType = Field(..., description="实验类型")
    objective: str = Field(..., min_length=1, description="实验目标")
    materials: List[str] = Field(..., min_items=1, description="实验材料")
    safety_notes: List[str] = Field(default=[], description="安全注意事项")
    estimated_duration: int = Field(..., ge=1, description="预估时长(分钟)")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="难度等级")

class VideoUploadRequest(BaseModel):
    """视频上传请求"""
    class_id: int = Field(..., description="班级ID")
    lesson_title: str = Field(..., min_length=1, max_length=200, description="课程标题")
    subject: str = Field(..., description="学科")
    duration: int = Field(..., ge=1, description="视频时长(分钟)")
    description: Optional[str] = Field(None, max_length=500, description="描述")

# ==================== 响应模型 ====================

class ClassroomInfo(BaseModel):
    """课堂信息"""
    id: str = Field(..., description="课堂ID")
    name: str = Field(..., description="课堂名称")
    subject: str = Field(..., description="学科")
    grade: str = Field(..., description="年级")
    class_id: str = Field(..., description="班级ID")
    teacher_id: str = Field(..., description="教师ID")
    teacher_name: str = Field(..., description="教师姓名")
    status: ClassroomStatus = Field(..., description="课堂状态")
    scheduled_time: datetime = Field(..., description="计划开始时间")
    actual_start_time: Optional[datetime] = Field(None, description="实际开始时间")
    actual_end_time: Optional[datetime] = Field(None, description="实际结束时间")
    duration_minutes: int = Field(..., description="课堂时长")
    student_count: int = Field(..., description="学生数量")
    present_count: int = Field(..., description="出席人数")
    description: Optional[str] = Field(None, description="课堂描述")
    lesson_plan_id: Optional[str] = Field(None, description="教案ID")
    settings: Optional[Dict[str, Any]] = Field(None, description="课堂设置")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class StudentInfo(BaseModel):
    """学生信息"""
    id: str = Field(..., description="学生ID")
    name: str = Field(..., description="学生姓名")
    student_number: str = Field(..., description="学号")
    avatar: Optional[str] = Field(None, description="头像")
    engagement: StudentEngagement = Field(..., description="参与度")
    attendance_status: str = Field(..., description="出席状态")
    attention_level: AttentionLevel = Field(default=AttentionLevel.MEDIUM, description="专注度")
    last_activity: Optional[datetime] = Field(None, description="最后活动时间")
    interaction_count: int = Field(default=0, description="互动次数")
    performance_score: Optional[float] = Field(None, description="表现评分")
    online_status: bool = Field(default=False, description="在线状态")

class InteractionInfo(BaseModel):
    """互动信息"""
    id: str = Field(..., description="互动ID")
    type: InteractionType = Field(..., description="互动类型")
    title: str = Field(..., description="互动标题")
    content: str = Field(..., description="互动内容")
    options: Optional[List[str]] = Field(None, description="选项")
    status: str = Field(..., description="互动状态")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration_seconds: Optional[int] = Field(None, description="持续时间")
    participant_count: int = Field(default=0, description="参与人数")
    response_count: int = Field(default=0, description="回答数量")
    target_students: Optional[List[str]] = Field(None, description="目标学生")
    results: Optional[Dict[str, Any]] = Field(None, description="互动结果")
    created_by: str = Field(..., description="创建者")
    created_at: datetime = Field(..., description="创建时间")

class StudentResponse(BaseModel):
    """学生回答"""
    id: str = Field(..., description="回答ID")
    interaction_id: str = Field(..., description="互动ID")
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    response: str = Field(..., description="回答内容")
    response_time: datetime = Field(..., description="回答时间")
    confidence_level: Optional[float] = Field(None, description="置信度")
    is_correct: Optional[bool] = Field(None, description="是否正确")
    score: Optional[float] = Field(None, description="得分")
    feedback: Optional[str] = Field(None, description="反馈")
    ai_analysis: Optional[Dict[str, Any]] = Field(None, description="AI分析")

class ClassroomMessage(BaseModel):
    """课堂消息"""
    id: str = Field(..., description="消息ID")
    classroom_id: str = Field(..., description="课堂ID")
    sender_id: str = Field(..., description="发送者ID")
    sender_name: str = Field(..., description="发送者姓名")
    sender_type: str = Field(..., description="发送者类型")
    message_type: MessageType = Field(..., description="消息类型")
    content: str = Field(..., description="消息内容")
    target_type: str = Field(..., description="目标类型")
    target_ids: Optional[List[str]] = Field(None, description="目标ID列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    timestamp: datetime = Field(..., description="时间戳")
    read_by: List[str] = Field(default=[], description="已读用户")

class ClassroomAnalytics(BaseModel):
    """课堂分析数据"""
    classroom_id: str = Field(..., description="课堂ID")
    analysis_time: datetime = Field(..., description="分析时间")
    total_students: int = Field(..., description="总学生数")
    present_students: int = Field(..., description="出席学生数")
    attendance_rate: float = Field(..., description="出席率")
    average_engagement: float = Field(..., description="平均参与度")
    average_attention: float = Field(..., description="平均专注度")
    interaction_stats: Dict[str, int] = Field(..., description="互动统计")
    performance_distribution: Dict[str, int] = Field(..., description="表现分布")
    attention_distribution: Dict[str, int] = Field(..., description="专注度分布")
    time_analysis: Dict[str, Any] = Field(..., description="时间分析")
    ai_insights: List[str] = Field(default=[], description="AI洞察")
    recommendations: List[str] = Field(..., description="建议")

class AIAssistantResponse(BaseModel):
    """AI助手回复"""
    response_id: str = Field(..., description="回复ID")
    question: str = Field(..., description="问题")
    answer: str = Field(..., description="回答")
    confidence: float = Field(..., description="置信度")
    sources: Optional[List[str]] = Field(None, description="信息来源")
    suggestions: Optional[List[str]] = Field(None, description="建议")
    related_topics: Optional[List[str]] = Field(None, description="相关话题")
    response_time: datetime = Field(..., description="回复时间")
    context_used: Optional[Dict[str, Any]] = Field(None, description="使用的上下文")
    follow_up_questions: Optional[List[str]] = Field(None, description="后续问题")

class ClassroomSummary(BaseModel):
    """课堂总结"""
    classroom_id: str = Field(..., description="课堂ID")
    summary_type: str = Field(..., description="总结类型")
    content: str = Field(..., description="总结内容")
    key_points: List[str] = Field(..., description="关键点")
    student_performance: Dict[str, Any] = Field(..., description="学生表现")
    interaction_highlights: List[Dict[str, Any]] = Field(..., description="互动亮点")
    areas_for_improvement: List[str] = Field(..., description="改进建议")
    next_lesson_suggestions: List[str] = Field(..., description="下节课建议")
    generated_at: datetime = Field(..., description="生成时间")
    generated_by: str = Field(..., description="生成方式")

class StudentAttentionData(BaseModel):
    """学生专注度数据"""
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    attention_level: AttentionLevel = Field(..., description="专注度等级")
    attention_score: float = Field(..., ge=0, le=1, description="专注度分数")
    timestamp: datetime = Field(..., description="时间戳")
    duration_minutes: int = Field(..., description="持续时长")
    factors: Optional[List[str]] = Field(None, description="影响因素")
    notes: Optional[str] = Field(None, description="备注")

class StudentPerformance(BaseModel):
    """学生表现"""
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    correct_rate: float = Field(..., ge=0, le=1, description="正确率")
    response_time: float = Field(..., description="平均响应时间")
    participation_level: str = Field(..., description="参与度")
    understanding_level: str = Field(..., description="理解程度")
    weak_points: List[str] = Field(default=[], description="薄弱知识点")
    suggestions: List[str] = Field(default=[], description="改进建议")

class ClassLearningStatus(BaseModel):
    """班级学情状态"""
    class_id: int = Field(..., description="班级ID")
    session_id: str = Field(..., description="会话ID")
    overall_understanding: float = Field(..., ge=0, le=1, description="整体理解度")
    participation_rate: float = Field(..., ge=0, le=1, description="参与率")
    average_score: float = Field(..., ge=0, le=100, description="平均分")
    difficulty_distribution: Dict[str, int] = Field(..., description="难度分布")
    knowledge_mastery: Dict[str, float] = Field(..., description="知识点掌握情况")
    attention_level: str = Field(..., description="注意力水平")
    learning_pace: str = Field(..., description="学习节奏")
    timestamp: datetime = Field(..., description="生成时间")

class QuestionAnalysis(BaseModel):
    """题目分析结果"""
    question_id: str = Field(..., description="题目ID")
    correct_rate: float = Field(..., ge=0, le=1, description="正确率")
    average_time: float = Field(..., description="平均答题时间")
    difficulty_assessment: DifficultyLevel = Field(..., description="难度评估")
    common_errors: List[str] = Field(default=[], description="常见错误")
    knowledge_gaps: List[str] = Field(default=[], description="知识缺陷")
    teaching_suggestions: List[str] = Field(default=[], description="教学建议")
    next_questions: List[str] = Field(default=[], description="推荐后续题目")

class ExperimentDesign(BaseModel):
    """实验设计"""
    experiment_id: str = Field(..., description="实验ID")
    name: str = Field(..., description="实验名称")
    type: ExperimentType = Field(..., description="实验类型")
    objective: str = Field(..., description="实验目标")
    materials: List[str] = Field(..., description="实验材料")
    steps: List[str] = Field(..., description="实验步骤")
    safety_notes: List[str] = Field(..., description="安全注意事项")
    expected_results: List[str] = Field(..., description="预期结果")
    evaluation_criteria: List[str] = Field(..., description="评价标准")
    duration: int = Field(..., description="预估时长")
    difficulty_level: DifficultyLevel = Field(..., description="难度等级")
    created_at: datetime = Field(..., description="创建时间")

class InteractionResult(BaseModel):
    """互动结果"""
    interaction_id: str = Field(..., description="互动ID")
    participation_count: int = Field(..., description="参与人数")
    participation_rate: float = Field(..., ge=0, le=1, description="参与率")
    responses: List[Dict[str, Any]] = Field(..., description="响应数据")
    analysis_summary: str = Field(..., description="分析总结")
    insights: List[str] = Field(default=[], description="洞察")
    recommendations: List[str] = Field(default=[], description="建议")

class VideoAnalysis(BaseModel):
    """视频分析结果"""
    video_id: str = Field(..., description="视频ID")
    teaching_behaviors: List[str] = Field(..., description="教学行为")
    student_engagement: float = Field(..., ge=0, le=1, description="学生参与度")
    interaction_frequency: int = Field(..., description="互动频次")
    content_coverage: float = Field(..., ge=0, le=1, description="内容覆盖度")
    pacing_analysis: str = Field(..., description="节奏分析")
    improvement_areas: List[str] = Field(..., description="改进领域")
    strengths: List[str] = Field(..., description="优势")
    overall_rating: float = Field(..., ge=0, le=10, description="整体评分")
    generated_at: datetime = Field(..., description="分析时间")

# ==================== API接口实现 ====================

@router.post("/question-analysis", response_model=APIResponse[Dict[str, Any]])
async def analyze_question_responses(
    request: QuestionAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分析题目和学生回答，生成实时学情
    
    Args:
        request: 题目分析请求
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        分析结果和学情报告
    """
    try:
        # 使用AI分析学生回答
        agent_manager = AgentManager()
        learning_agent = agent_manager.get_agent("learning_status")
        
        # 计算基础统计
        total_students = len(request.student_answers)
        correct_answers = sum(1 for answer in request.student_answers 
                            if answer.answer.strip().lower() == request.question_info.correct_answer.strip().lower())
        correct_rate = correct_answers / total_students if total_students > 0 else 0
        
        # 分析学生表现
        student_performances = []
        for answer in request.student_answers:
            is_correct = answer.answer.strip().lower() == request.question_info.correct_answer.strip().lower()
            performance = StudentPerformance(
                student_id=answer.student_id,
                student_name=answer.student_name,
                correct_rate=1.0 if is_correct else 0.0,
                response_time=answer.answer_time or 30,
                participation_level="高" if answer.answer_time and answer.answer_time < 60 else "中",
                understanding_level="良好" if is_correct else "需要改进",
                weak_points=request.question_info.knowledge_points if not is_correct else [],
                suggestions=["加强基础练习"] if not is_correct else ["继续保持"]
            )
            student_performances.append(performance)
        
        # 生成题目分析
        question_analysis = QuestionAnalysis(
            question_id=f"q_{datetime.now().timestamp()}",
            correct_rate=correct_rate,
            average_time=sum(a.answer_time or 30 for a in request.student_answers) / total_students,
            difficulty_assessment=request.question_info.difficulty,
            common_errors=["计算错误", "概念理解不清"] if correct_rate < 0.7 else [],
            knowledge_gaps=request.question_info.knowledge_points if correct_rate < 0.5 else [],
            teaching_suggestions=[
                "需要重点讲解相关概念" if correct_rate < 0.7 else "可以进入下一个知识点",
                "建议增加练习题" if correct_rate < 0.8 else "学生掌握良好"
            ],
            next_questions=["相关基础题目", "进阶练习题"]
        )
        
        # 生成班级学情
        class_status = ClassLearningStatus(
            class_id=request.class_id,
            session_id=request.session_id or f"session_{datetime.now().timestamp()}",
            overall_understanding=correct_rate,
            participation_rate=1.0,  # 假设所有学生都参与了
            average_score=correct_rate * 100,
            difficulty_distribution={"easy": 2, "medium": 5, "hard": 3},
            knowledge_mastery={kp: correct_rate for kp in request.question_info.knowledge_points},
            attention_level="高" if correct_rate > 0.8 else "中",
            learning_pace="适中" if 0.6 <= correct_rate <= 0.9 else "需调整",
            timestamp=datetime.now()
        )
        
        logger.info(f"用户 {current_user.username} 分析题目响应，班级: {request.class_id}")
        
        return ResponseBuilder.success({
            "question_analysis": question_analysis.dict(),
            "class_learning_status": class_status.dict(),
            "student_performances": [p.dict() for p in student_performances],
            "recommendations": [
                "根据学生表现调整教学节奏",
                "关注理解困难的学生",
                "适当增加互动环节"
            ]
        })
        
    except Exception as e:
        logger.error(f"分析题目响应失败: {str(e)}")
        raise BusinessException(f"分析题目响应失败: {str(e)}")

@router.get("/learning-status/{class_id}", response_model=APIResponse[ClassLearningStatus])
async def get_realtime_learning_status(
    class_id: int,
    session_id: Optional[str] = Query(None, description="课堂会话ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取实时学情报告
    
    Args:
        class_id: 班级ID
        session_id: 课堂会话ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        实时学情状态
    """
    try:
        # 这里应该从数据库或缓存获取实时学情数据
        # 暂时返回模拟数据
        
        learning_status = ClassLearningStatus(
            class_id=class_id,
            session_id=session_id or f"session_{class_id}_{datetime.now().timestamp()}",
            overall_understanding=0.75,
            participation_rate=0.85,
            average_score=75.0,
            difficulty_distribution={"easy": 3, "medium": 7, "hard": 2},
            knowledge_mastery={
                "基础概念": 0.8,
                "应用技能": 0.7,
                "综合分析": 0.6
            },
            attention_level="中",
            learning_pace="适中",
            timestamp=datetime.now()
        )
        
        logger.info(f"用户 {current_user.username} 获取实时学情，班级: {class_id}")
        
        return ResponseBuilder.success(learning_status)
        
    except Exception as e:
        logger.error(f"获取实时学情失败: {str(e)}")
        raise BusinessException(f"获取实时学情失败: {str(e)}")

@router.post("/interaction", response_model=APIResponse[Dict[str, str]])
async def create_classroom_interaction(
    request: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建课堂互动
    
    Args:
        request: 互动请求
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        互动创建结果
    """
    try:
        import uuid
        interaction_id = str(uuid.uuid4())
        
        # 这里应该保存互动到数据库
        # 生成互动URL
        interaction_url = f"/classroom/interaction/{interaction_id}"
        
        logger.info(f"用户 {current_user.username} 创建课堂互动: {request.title}")
        
        return ResponseBuilder.success({
            "interaction_id": interaction_id,
            "interaction_url": interaction_url,
            "message": "课堂互动创建成功"
        })
        
    except Exception as e:
        logger.error(f"创建课堂互动失败: {str(e)}")
        raise BusinessException(f"创建课堂互动失败: {str(e)}")

@router.get("/interaction/{interaction_id}/results", response_model=APIResponse[InteractionResult])
async def get_interaction_results(
    interaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取互动结果
    
    Args:
        interaction_id: 互动ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        互动结果
    """
    try:
        # 这里应该从数据库获取互动结果
        # 暂时返回模拟数据
        
        result = InteractionResult(
            interaction_id=interaction_id,
            participation_count=28,
            participation_rate=0.93,
            responses=[
                {"option": "A", "count": 12, "percentage": 0.43},
                {"option": "B", "count": 8, "percentage": 0.29},
                {"option": "C", "count": 5, "percentage": 0.18},
                {"option": "D", "count": 3, "percentage": 0.10}
            ],
            analysis_summary="大部分学生选择了正确答案A，说明对该知识点掌握较好",
            insights=[
                "学生对基础概念理解清晰",
                "少数学生在应用方面还需加强"
            ],
            recommendations=[
                "可以进入下一个知识点",
                "对选择错误答案的学生进行个别指导"
            ]
        )
        
        logger.info(f"用户 {current_user.username} 获取互动结果: {interaction_id}")
        
        return ResponseBuilder.success(result)
        
    except Exception as e:
        logger.error(f"获取互动结果失败: {str(e)}")
        raise BusinessException(f"获取互动结果失败: {str(e)}")

@router.get("/experiment/templates", response_model=APIResponse[List[Dict[str, Any]]])
async def get_experiment_templates(
    experiment_type: Optional[ExperimentType] = Query(None, description="实验类型"),
    subject: Optional[str] = Query(None, description="学科"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取实验模板
    
    Args:
        experiment_type: 实验类型
        subject: 学科
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        实验模板列表
    """
    try:
        # 这里应该从数据库获取实验模板
        # 暂时返回模拟数据
        
        templates = [
            {
                "template_id": "template_001",
                "name": "单摆实验",
                "type": "physics",
                "subject": "物理",
                "description": "研究单摆周期与摆长的关系",
                "difficulty": "medium",
                "duration": 45,
                "materials": ["摆球", "细线", "支架", "秒表", "米尺"],
                "objectives": ["理解单摆运动规律", "掌握实验数据处理方法"]
            },
            {
                "template_id": "template_002",
                "name": "酸碱中和实验",
                "type": "chemistry",
                "subject": "化学",
                "description": "观察酸碱中和反应现象",
                "difficulty": "easy",
                "duration": 30,
                "materials": ["盐酸", "氢氧化钠", "酚酞", "烧杯", "滴管"],
                "objectives": ["理解酸碱中和反应", "学会使用指示剂"]
            }
        ]
        
        # 根据筛选条件过滤
        if experiment_type:
            templates = [t for t in templates if t["type"] == experiment_type.value]
        if subject:
            templates = [t for t in templates if t["subject"] == subject]
        
        logger.info(f"用户 {current_user.username} 获取实验模板")
        
        return ResponseBuilder.success(templates)
        
    except Exception as e:
        logger.error(f"获取实验模板失败: {str(e)}")
        raise BusinessException(f"获取实验模板失败: {str(e)}")

@router.post("/experiment/design", response_model=APIResponse[ExperimentDesign])
async def create_experiment_design(
    request: ExperimentDesignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建实验设计
    
    Args:
        request: 实验设计请求
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        实验设计
    """
    try:
        import uuid
        experiment_id = str(uuid.uuid4())
        
        # 使用AI生成实验步骤和预期结果
        ai_client = UnifiedLLMClient()
        
        prompt = f"""
        请为以下实验设计详细的实验步骤和预期结果：
        实验名称: {request.experiment_name}
        实验类型: {request.experiment_type.value}
        实验目标: {request.objective}
        实验材料: {', '.join(request.materials)}
        """
        
        ai_response = await ai_client.generate_response(prompt)
        
        # 生成实验设计
        experiment_design = ExperimentDesign(
            experiment_id=experiment_id,
            name=request.experiment_name,
            type=request.experiment_type,
            objective=request.objective,
            materials=request.materials,
            steps=[
                "准备实验器材",
                "按照要求组装实验装置",
                "进行实验操作",
                "记录实验数据",
                "分析实验结果"
            ],
            safety_notes=request.safety_notes or ["注意实验安全", "正确使用实验器材"],
            expected_results=["获得预期的实验数据", "验证理论假设"],
            evaluation_criteria=["实验操作规范性", "数据记录准确性", "结果分析合理性"],
            duration=request.estimated_duration,
            difficulty_level=request.difficulty_level,
            created_at=datetime.now()
        )
        
        logger.info(f"用户 {current_user.username} 创建实验设计: {request.experiment_name}")
        
        return ResponseBuilder.success(experiment_design)
        
    except Exception as e:
        logger.error(f"创建实验设计失败: {str(e)}")
        raise BusinessException(f"创建实验设计失败: {str(e)}")

@router.get("/experiment/{experiment_id}/simulation", response_model=APIResponse[Dict[str, Any]])
async def get_experiment_simulation(
    experiment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取虚拟实验演示
    
    Args:
        experiment_id: 实验ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        虚拟实验数据
    """
    try:
        # 这里应该生成或获取虚拟实验数据
        # 暂时返回模拟数据
        
        simulation_data = {
            "experiment_id": experiment_id,
            "simulation_url": f"/simulations/{experiment_id}",
            "interactive_elements": [
                {"type": "slider", "name": "摆长", "min": 0.1, "max": 2.0, "step": 0.1},
                {"type": "button", "name": "开始实验", "action": "start_experiment"},
                {"type": "display", "name": "周期显示", "unit": "秒"}
            ],
            "visualization_config": {
                "chart_type": "line",
                "x_axis": "时间",
                "y_axis": "位移",
                "animation": True
            },
            "predicted_results": {
                "period_formula": "T = 2π√(L/g)",
                "expected_data_points": 10,
                "accuracy_range": "±5%"
            }
        }
        
        logger.info(f"用户 {current_user.username} 获取虚拟实验演示: {experiment_id}")
        
        return ResponseBuilder.success(simulation_data)
        
    except Exception as e:
        logger.error(f"获取虚拟实验演示失败: {str(e)}")
        raise BusinessException(f"获取虚拟实验演示失败: {str(e)}")

@router.post("/video/upload", response_model=APIResponse[Dict[str, str]])
async def upload_classroom_video(
    file: UploadFile = File(...),
    class_id: int = Form(...),
    lesson_title: str = Form(...),
    subject: str = Form(...),
    duration: int = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传课堂视频
    
    Args:
        file: 视频文件
        class_id: 班级ID
        lesson_title: 课程标题
        subject: 学科
        duration: 视频时长
        description: 描述
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        上传结果
    """
    try:
        # 验证文件类型
        allowed_types = ["video/mp4", "video/avi", "video/mov", "video/wmv"]
        if file.content_type not in allowed_types:
            raise ValidationException("不支持的视频格式")
        
        # 验证文件大小 (最大500MB)
        if file.size > 500 * 1024 * 1024:
            raise ValidationException("视频文件大小不能超过500MB")
        
        import uuid
        video_id = str(uuid.uuid4())
        
        # 这里应该实现视频存储和处理逻辑
        
        logger.info(f"用户 {current_user.username} 上传课堂视频: {lesson_title}")
        
        return ResponseBuilder.success({
            "video_id": video_id,
            "upload_status": "success",
            "message": "视频上传成功，正在处理中"
        })
        
    except Exception as e:
        logger.error(f"上传课堂视频失败: {str(e)}")
        raise BusinessException(f"上传课堂视频失败: {str(e)}")

@router.get("/video/{video_id}/analysis", response_model=APIResponse[VideoAnalysis])
async def get_video_analysis(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取视频分析结果
    
    Args:
        video_id: 视频ID
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        视频分析结果
    """
    try:
        # 这里应该从AI分析服务获取视频分析结果
        # 暂时返回模拟数据
        
        analysis = VideoAnalysis(
            video_id=video_id,
            teaching_behaviors=[
                "讲解清晰",
                "板书工整",
                "与学生互动频繁",
                "使用多媒体辅助教学"
            ],
            student_engagement=0.78,
            interaction_frequency=15,
            content_coverage=0.85,
            pacing_analysis="节奏适中，重点突出",
            improvement_areas=[
                "可以增加更多的学生参与环节",
                "某些概念需要更详细的解释"
            ],
            strengths=[
                "教学思路清晰",
                "语言表达生动",
                "课堂氛围活跃"
            ],
            overall_rating=8.2,
            generated_at=datetime.now()
        )
        
        logger.info(f"用户 {current_user.username} 获取视频分析: {video_id}")
        
        return ResponseBuilder.success(analysis)
        
    except Exception as e:
        logger.error(f"获取视频分析失败: {str(e)}")
        raise BusinessException(f"获取视频分析失败: {str(e)}")

@router.post("/content/generate", response_model=APIResponse[Dict[str, Any]])
async def generate_classroom_content(
    content_type: str = Query(..., description="内容类型"),
    topic: str = Query(..., description="主题"),
    difficulty_level: int = Query(..., ge=1, le=5, description="难度等级"),
    student_level: str = Query(..., description="学生水平"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成课堂内容
    
    Args:
        content_type: 内容类型
        topic: 主题
        difficulty_level: 难度等级
        student_level: 学生水平
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        生成的课堂内容
    """
    try:
        # 使用AI生成课堂内容
        agent_manager = AgentManager()
        classroom_agent = agent_manager.get_agent("classroom_assistant")
        
        result = await classroom_agent.execute_task(
            task_type="generate_content",
            content_type=content_type,
            topic=topic,
            difficulty_level=difficulty_level,
            student_level=student_level
        )
        
        logger.info(f"用户 {current_user.username} 生成课堂内容: {topic}")
        
        return ResponseBuilder.success({
            "content_type": content_type,
            "topic": topic,
            "generated_content": result.get("result", "生成的课堂内容"),
            "difficulty_level": difficulty_level,
            "student_level": student_level,
            "usage_suggestions": [
                "适合课堂导入环节使用",
                "可以作为课堂练习",
                "建议结合实际案例讲解"
            ],
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"生成课堂内容失败: {str(e)}")
        raise BusinessException(f"生成课堂内容失败: {str(e)}")

@router.get("/health", response_model=APIResponse[Dict[str, str]])
async def health_check():
    """
    健康检查接口
    
    Returns:
        服务状态
    """
    return ResponseBuilder.success({
        "status": "healthy",
        "service": "classroom",
        "timestamp": datetime.now().isoformat()
    })