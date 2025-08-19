# -*- coding: utf-8 -*-
"""
课堂AI助手API路由模块

本模块提供课堂AI助手的HTTP API接口，包括：
- AI实时学情生成
- 生物实验设计助手
- 课堂注意力监测
- 智能教学调整建议
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
import httpx
import os

from core import AIServiceManager, CacheManager, ClassroomAIService
from core.classroom_ai_service import (
    Question, StudentAnswer, AnswerAnalysis, LearningInsight,
    ExperimentDesign, ClassroomInteraction, QuestionType, AnswerQuality,
    LearningStatus, ExperimentType, RiskLevel
)
from database import get_db
from auth import get_current_user

logger = logging.getLogger(__name__)

# 创建路由器
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
    
    async def analyze_learning_state(self, student_id: str, subject: str, time_range: int = 24):
        """实时学情分析"""
        data = {
            'student_id': student_id,
            'subject': subject,
            'time_range_hours': time_range
        }
        return await self._make_request('POST', '/classroom/analyze-learning-state', data)
    
    async def design_experiment(self, topic: str, grade_level: str, objectives: list, duration: int = 45):
        """实验设计"""
        data = {
            'topic': topic,
            'grade_level': grade_level,
            'objectives': objectives,
            'duration': duration
        }
        return await self._make_request('POST', '/classroom/design-experiment', data)
    
    async def analyze_attention(self, classroom_id: str, start_time: str, end_time: str):
        """注意力分析"""
        data = {
            'classroom_id': classroom_id,
            'start_time': start_time,
            'end_time': end_time
        }
        return await self._make_request('POST', '/classroom/analyze-attention', data)
    
    async def suggest_teaching_adjustment(self, class_id: str, subject: str, current_plan: dict):
        """教学调整建议"""
        data = {
            'class_id': class_id,
            'subject': subject,
            'current_lesson_plan': current_plan
        }
        return await self._make_request('POST', '/classroom/suggest-adjustment', data)

# 初始化服务
ai_manager = AIServiceManager()
cache_manager = CacheManager()
classroom_ai_service = ClassroomAIService(ai_manager)
ai_service_client = AIServiceClient()

# === 请求模型 ===

class QuestionRequest(BaseModel):
    """题目请求模型"""
    content: str = Field(..., description="题目内容")
    question_type: QuestionType = Field(..., description="题目类型")
    subject: str = Field(..., description="学科")
    difficulty: float = Field(0.5, ge=0, le=1, description="难度系数")
    knowledge_points: List[str] = Field(..., description="知识点列表")
    options: Optional[List[str]] = Field(None, description="选择题选项")
    correct_answer: str = Field("", description="正确答案")
    explanation: str = Field("", description="答案解释")

class StudentAnswerRequest(BaseModel):
    """学生回答请求模型"""
    student_id: str = Field(..., description="学生ID")
    question_id: str = Field(..., description="题目ID")
    answer: str = Field(..., description="学生答案")
    confidence: float = Field(0.0, ge=0, le=1, description="学生自信度")
    response_time: int = Field(0, ge=0, description="回答用时（秒）")

class LearningInsightRequest(BaseModel):
    """学情洞察请求模型"""
    student_id: str = Field(..., description="学生ID")
    subject: str = Field(..., description="学科")
    time_range_hours: int = Field(24, ge=1, le=168, description="时间范围（小时）")

class ExperimentDesignRequest(BaseModel):
    """实验设计请求模型"""
    topic: str = Field(..., description="实验主题")
    grade_level: str = Field(..., description="年级水平")
    objectives: List[str] = Field(..., description="实验目标")
    duration: int = Field(45, ge=10, le=120, description="实验时长（分钟）")
    experiment_type: ExperimentType = Field(ExperimentType.LABORATORY, description="实验类型")
    safety_requirements: Optional[str] = Field(None, description="安全要求")

class ClassroomInteractionRequest(BaseModel):
    """课堂互动请求模型"""
    student_id: str = Field(..., description="学生ID")
    interaction_type: str = Field(..., description="互动类型")
    content: str = Field(..., description="互动内容")
    engagement_level: float = Field(0.7, ge=0, le=1, description="参与度")
    attention_score: float = Field(0.7, ge=0, le=1, description="注意力分数")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")

class AttentionAnalysisRequest(BaseModel):
    """注意力分析请求模型"""
    classroom_id: str = Field(..., description="课堂ID")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v

class TeachingAdjustmentRequest(BaseModel):
    """教学调整请求模型"""
    class_id: str = Field(..., description="班级ID")
    subject: str = Field(..., description="学科")
    current_lesson_plan: Dict[str, Any] = Field(..., description="当前教学计划")
    analysis_period_hours: int = Field(24, ge=1, le=168, description="分析时间段（小时）")

# === 响应模型 ===

class AnswerAnalysisResponse(BaseModel):
    """回答分析响应模型"""
    student_id: str
    question_id: str
    is_correct: bool
    quality: AnswerQuality
    score: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    knowledge_gaps: List[str]
    analysis_time: datetime

class LearningInsightResponse(BaseModel):
    """学情洞察响应模型"""
    student_id: str
    subject: str
    knowledge_point: str
    mastery_level: float
    learning_status: LearningStatus
    progress_trend: str
    attention_level: float
    engagement_score: float
    recommended_actions: List[str]
    generated_at: datetime

class ExperimentMaterialResponse(BaseModel):
    """实验材料响应模型"""
    name: str
    quantity: str
    specification: str
    safety_notes: List[str]
    alternatives: List[str]

class ExperimentStepResponse(BaseModel):
    """实验步骤响应模型"""
    step_number: int
    description: str
    duration: int
    safety_warnings: List[str]
    expected_result: str
    troubleshooting: List[str]

class ExperimentDesignResponse(BaseModel):
    """实验设计响应模型"""
    id: str
    title: str
    objective: str
    hypothesis: str
    experiment_type: ExperimentType
    subject: str
    grade_level: str
    duration: int
    materials: List[ExperimentMaterialResponse]
    steps: List[ExperimentStepResponse]
    variables: Dict[str, str]
    safety_assessment: Dict[str, Any]
    expected_outcomes: List[str]
    evaluation_criteria: List[str]
    created_at: datetime

class AttentionAnalysisResponse(BaseModel):
    """注意力分析响应模型"""
    classroom_id: str
    analysis_period: Dict[str, str]
    overall_attention: float
    attention_trends: List[str]
    distraction_factors: List[str]
    peak_attention_periods: List[str]
    student_attention_scores: Dict[str, float]
    improvement_suggestions: List[str]
    generated_at: str

class TeachingAdjustmentResponse(BaseModel):
    """教学调整响应模型"""
    original_plan: Dict[str, Any]
    suggested_adjustments: Dict[str, Any]
    implementation_priority: List[str]
    expected_outcomes: List[str]
    generated_at: str

# === API路由 ===

@router.post("/answer/analyze", response_model=AnswerAnalysisResponse, summary="分析学生回答")
async def analyze_student_answer(
    question: QuestionRequest,
    student_answer: StudentAnswerRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI实时学情生成 - 分析学生回答
    
    分析学生对特定题目的回答，提供详细的学习反馈和建议。
    """
    try:
        # 权限检查
        await require_permission(current_user, "classroom:analyze")
        
        # 构建题目对象
        question_obj = Question(
            id=f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=question.content,
            question_type=question.question_type,
            subject=question.subject,
            difficulty=question.difficulty,
            knowledge_points=question.knowledge_points,
            options=question.options or [],
            correct_answer=question.correct_answer,
            explanation=question.explanation
        )
        
        # 构建学生回答对象
        answer_obj = StudentAnswer(
            student_id=student_answer.student_id,
            question_id=question_obj.id,
            answer=student_answer.answer,
            answer_time=datetime.now(),
            confidence=student_answer.confidence,
            response_time=student_answer.response_time
        )
        
        # 执行AI分析
        analysis = await classroom_ai_service.analyze_student_answer(question_obj, answer_obj)
        
        # 返回分析结果
        return AnswerAnalysisResponse(
            student_id=analysis.student_id,
            question_id=analysis.question_id,
            is_correct=analysis.is_correct,
            quality=analysis.quality,
            score=analysis.score,
            strengths=analysis.strengths,
            weaknesses=analysis.weaknesses,
            suggestions=analysis.suggestions,
            knowledge_gaps=analysis.knowledge_gaps,
            analysis_time=analysis.analysis_time
        )
        
    except Exception as e:
        logger.error(f"Answer analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"回答分析失败: {str(e)}")

@router.post("/learning-state/analyze", response_model=List[LearningInsightResponse], summary="实时学情生成")
async def generate_learning_insights(
    request: LearningInsightRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    实时学情生成
    
    基于学生的学习数据和课堂互动，生成个性化的学情分析和建议。
    """
    try:
        # 权限检查
        await require_permission(current_user, "classroom:insights")
        
        # 优先使用AI服务集成接口
        try:
            ai_result = await ai_service_client.analyze_learning_state(
                student_id=request.student_id,
                subject=request.subject,
                time_range=request.time_range_hours
            )
            
            # 转换AI服务返回的结果格式
            response_insights = []
            insights_data = ai_result.get('insights', [])
            
            for insight_data in insights_data:
                response_insights.append(LearningInsightResponse(
                    student_id=insight_data.get('student_id', request.student_id),
                    subject=insight_data.get('subject', request.subject),
                    knowledge_point=insight_data.get('knowledge_point', '综合分析'),
                    mastery_level=insight_data.get('mastery_level', 0.7),
                    learning_status=LearningStatus(insight_data.get('learning_status', 'normal')),
                    progress_trend=insight_data.get('progress_trend', 'stable'),
                    attention_level=insight_data.get('attention_level', 0.7),
                    engagement_score=insight_data.get('engagement_score', 0.7),
                    recommended_actions=insight_data.get('recommended_actions', []),
                    generated_at=datetime.now()
                ))
            
            logger.info(f"用户 {current_user['username']} 通过AI服务生成学情洞察，学生ID: {request.student_id}")
            return response_insights
            
        except Exception as ai_error:
            logger.warning(f"AI服务调用失败，使用备用方案: {str(ai_error)}")
            
            # 备用方案：使用原有的课堂AI服务
            # 获取学生最近的回答记录（模拟数据）
            recent_answers = []  # 实际应从数据库获取
            
            # 获取课堂互动记录（模拟数据）
            classroom_interactions = []  # 实际应从数据库获取
            
            # 生成学情洞察
            insights = await classroom_ai_service.generate_learning_insights(
                student_id=request.student_id,
                subject=request.subject,
                recent_answers=recent_answers,
                classroom_interactions=classroom_interactions
            )
            
            # 转换为响应模型
            response_insights = []
            for insight in insights:
                response_insights.append(LearningInsightResponse(
                    student_id=insight.student_id,
                    subject=insight.subject,
                    knowledge_point=insight.knowledge_point,
                    mastery_level=insight.mastery_level,
                    learning_status=insight.learning_status,
                    progress_trend=insight.progress_trend,
                    attention_level=insight.attention_level,
                    engagement_score=insight.engagement_score,
                    recommended_actions=insight.recommended_actions,
                    generated_at=insight.generated_at
                ))
            
            return response_insights
        
    except Exception as e:
        logger.error(f"Learning insights generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"学情洞察生成失败: {str(e)}")

@router.post("/experiment/design", response_model=ExperimentDesignResponse, summary="设计生物实验")
async def design_biology_experiment(
    request: ExperimentDesignRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生物实验设计助手
    
    基于教学需求，AI自动设计安全、有效的生物实验方案。
    """
    try:
        # 权限检查
        await require_permission(current_user, "classroom:experiment")
        
        # 优先使用AI服务集成接口
        try:
            ai_result = await ai_service_client.design_experiment(
                topic=request.topic,
                grade_level=request.grade_level,
                objectives=request.objectives,
                duration=request.duration
            )
            
            # 转换AI服务返回的结果格式
            materials_response = []
            for material_data in ai_result.get('materials', []):
                materials_response.append(ExperimentMaterialResponse(
                    name=material_data.get('name', '实验材料'),
                    quantity=material_data.get('quantity', '适量'),
                    specification=material_data.get('specification', '标准规格'),
                    safety_notes=material_data.get('safety_notes', []),
                    alternatives=material_data.get('alternatives', [])
                ))
            
            steps_response = []
            for step_data in ai_result.get('steps', []):
                steps_response.append(ExperimentStepResponse(
                    step_number=step_data.get('step_number', 1),
                    description=step_data.get('description', '实验步骤'),
                    duration=step_data.get('duration', 10),
                    safety_warnings=step_data.get('safety_warnings', []),
                    expected_result=step_data.get('expected_result', '预期结果'),
                    troubleshooting=step_data.get('troubleshooting', [])
                ))
            
            response = ExperimentDesignResponse(
                id=ai_result.get('id', f"exp_{int(time.time())}"),
                title=ai_result.get('title', f"{request.topic}实验"),
                objective=ai_result.get('objective', '实验目标'),
                hypothesis=ai_result.get('hypothesis', '实验假设'),
                experiment_type=request.experiment_type,
                subject=ai_result.get('subject', '生物'),
                grade_level=request.grade_level,
                duration=request.duration,
                materials=materials_response,
                steps=steps_response,
                variables=ai_result.get('variables', {}),
                safety_assessment=ai_result.get('safety_assessment', {}),
                expected_outcomes=ai_result.get('expected_outcomes', []),
                evaluation_criteria=ai_result.get('evaluation_criteria', []),
                created_at=datetime.now()
            )
            
            logger.info(f"用户 {current_user['username']} 通过AI服务设计实验: {request.topic}")
            return response
            
        except Exception as ai_error:
            logger.warning(f"AI服务调用失败，使用备用方案: {str(ai_error)}")
            
            # 备用方案：使用原有的课堂AI服务
            experiment_design = await classroom_ai_service.design_biology_experiment(
                topic=request.topic,
                grade_level=request.grade_level,
                objectives=request.objectives,
                duration=request.duration,
                experiment_type=request.experiment_type
            )
            
            # 转换材料列表
            materials_response = []
            for material in experiment_design.materials:
                materials_response.append(ExperimentMaterialResponse(
                    name=material.name,
                    quantity=material.quantity,
                    specification=material.specification,
                    safety_notes=material.safety_notes,
                    alternatives=material.alternatives
                ))
            
            # 转换步骤列表
            steps_response = []
            for step in experiment_design.steps:
                steps_response.append(ExperimentStepResponse(
                    step_number=step.step_number,
                    description=step.description,
                    duration=step.duration,
                    safety_warnings=step.safety_warnings,
                    expected_result=step.expected_result,
                    troubleshooting=step.troubleshooting
                ))
            
            # 返回实验设计
            return ExperimentDesignResponse(
                id=experiment_design.id,
                title=experiment_design.title,
                objective=experiment_design.objective,
                hypothesis=experiment_design.hypothesis,
                experiment_type=experiment_design.experiment_type,
                subject=experiment_design.subject,
                grade_level=experiment_design.grade_level,
                duration=experiment_design.duration,
                materials=materials_response,
                steps=steps_response,
                variables=experiment_design.variables,
                safety_assessment=experiment_design.safety_assessment,
                expected_outcomes=experiment_design.expected_outcomes,
                evaluation_criteria=experiment_design.evaluation_criteria,
                created_at=experiment_design.created_at
            )
        
    except Exception as e:
        logger.error(f"Experiment design error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"实验设计失败: {str(e)}")

@router.post("/attention/analyze", response_model=AttentionAnalysisResponse, summary="分析课堂注意力")
async def analyze_classroom_attention(
    request: AttentionAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    课堂注意力监测分析
    
    分析指定时间段内的课堂注意力状态，提供改进建议。
    """
    try:
        # 权限检查
        await require_permission(current_user, "classroom:attention")
        
        # 获取课堂互动数据（模拟数据）
        interactions = []  # 实际应从数据库获取
        
        # 执行注意力分析
        analysis_result = await classroom_ai_service.analyze_classroom_attention(
            classroom_id=request.classroom_id,
            interactions=interactions,
            time_period=(request.start_time, request.end_time)
        )
        
        # 返回分析结果
        return AttentionAnalysisResponse(**analysis_result)
        
    except Exception as e:
        logger.error(f"Attention analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"注意力分析失败: {str(e)}")

@router.post("/interaction/record", summary="记录课堂互动")
async def record_classroom_interaction(
    request: ClassroomInteractionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    记录课堂互动数据
    
    记录学生的课堂互动行为，用于后续的学情分析。
    """
    try:
        # 权限检查
        await require_permission(current_user, "classroom:record")
        
        # 创建互动记录
        interaction = ClassroomInteraction(
            student_id=request.student_id,
            interaction_type=request.interaction_type,
            content=request.content,
            timestamp=datetime.now(),
            engagement_level=request.engagement_level,
            attention_score=request.attention_score,
            metadata=request.metadata or {}
        )
        
        # 保存到数据库（实际实现）
        # db.add(interaction)
        # db.commit()
        
        return {"message": "课堂互动记录成功", "interaction_id": f"int_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
        
    except Exception as e:
        logger.error(f"Interaction recording error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"互动记录失败: {str(e)}")

@router.post("/teaching/adjust", response_model=TeachingAdjustmentResponse, summary="生成教学调整建议")
async def generate_teaching_adjustments(
    request: TeachingAdjustmentRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成智能教学调整建议
    
    基于班级学情分析，提供个性化的教学调整方案。
    """
    try:
        # 权限检查
        await require_permission(current_user, "classroom:adjust")
        
        # 获取班级学情数据（模拟数据）
        class_insights = []  # 实际应从数据库获取
        
        # 生成教学调整建议
        adjustments = await classroom_ai_service.generate_teaching_adjustments(
            class_insights=class_insights,
            current_lesson_plan=request.current_lesson_plan
        )
        
        # 返回调整建议
        return TeachingAdjustmentResponse(**adjustments)
        
    except Exception as e:
        logger.error(f"Teaching adjustment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"教学调整建议生成失败: {str(e)}")

@router.get("/exercises/recommend/{student_id}", summary="推荐练习题目")
async def recommend_practice_exercises(
    student_id: str,
    subject: str = Query(..., description="学科"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    推荐个性化练习题目
    
    基于学生的学情分析，推荐针对性的练习题目。
    """
    try:
        # 权限检查
        await require_permission(current_user, "classroom:recommend")
        
        # 获取学生学情洞察（模拟数据）
        student_insights = []  # 实际应从数据库获取
        
        # 生成练习推荐
        recommendations = await classroom_ai_service.recommend_practice_exercises(
            student_insights=student_insights,
            subject=subject
        )
        
        return {
            "student_id": student_id,
            "subject": subject,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Exercise recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"练习推荐失败: {str(e)}")

@router.get("/statistics/classroom/{classroom_id}", summary="获取课堂统计数据")
async def get_classroom_statistics(
    classroom_id: str,
    date_range: int = Query(7, ge=1, le=30, description="统计天数"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取课堂统计数据
    
    提供课堂的整体统计信息，包括参与度、注意力、学习效果等指标。
    """
    try:
        # 权限检查
        await require_permission(current_user, "classroom:statistics")
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        # 获取统计数据（模拟数据）
        statistics = {
            "classroom_id": classroom_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": date_range
            },
            "overall_metrics": {
                "average_attention": 0.75,
                "average_engagement": 0.68,
                "participation_rate": 0.82,
                "question_accuracy": 0.71
            },
            "trends": {
                "attention_trend": "improving",
                "engagement_trend": "stable",
                "performance_trend": "improving"
            },
            "top_performers": [
                {"student_id": "student_001", "score": 0.95},
                {"student_id": "student_002", "score": 0.89}
            ],
            "needs_attention": [
                {"student_id": "student_003", "issues": ["低参与度", "注意力不集中"]}
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Classroom statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"统计数据获取失败: {str(e)}")

# === 错误处理 ===

# Exception handlers should be registered at the app level, not router level
# These would be moved to main.py if needed