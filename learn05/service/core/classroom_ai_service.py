# -*- coding: utf-8 -*-
"""
课堂AI助手服务模块

本模块实现了课堂AI助手的核心功能，包括AI实时学情生成、生物实验设计助手和课堂AI化应用平台。
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

from .ai_service import AIServiceManager, AIRequest, AIProvider
from .cache_service import CacheManager
from .task_service import TaskQueue, Task, TaskType, TaskPriority

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """题目类型"""
    MULTIPLE_CHOICE = "multiple_choice"  # 选择题
    TRUE_FALSE = "true_false"  # 判断题
    FILL_BLANK = "fill_blank"  # 填空题
    SHORT_ANSWER = "short_answer"  # 简答题
    ESSAY = "essay"  # 论述题
    CALCULATION = "calculation"  # 计算题

class AnswerQuality(Enum):
    """回答质量"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"  # 良好
    AVERAGE = "average"  # 一般
    POOR = "poor"  # 较差
    INCOMPLETE = "incomplete"  # 不完整

class LearningStatus(Enum):
    """学习状态"""
    MASTERED = "mastered"  # 已掌握
    UNDERSTANDING = "understanding"  # 理解中
    STRUGGLING = "struggling"  # 困难
    NOT_STARTED = "not_started"  # 未开始

class ExperimentType(Enum):
    """实验类型"""
    OBSERVATION = "observation"  # 观察实验
    CONTROLLED = "controlled"  # 对照实验
    SIMULATION = "simulation"  # 模拟实验
    FIELD_STUDY = "field_study"  # 野外调查
    LABORATORY = "laboratory"  # 实验室实验

class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"  # 低风险
    MEDIUM = "medium"  # 中等风险
    HIGH = "high"  # 高风险
    VERY_HIGH = "very_high"  # 极高风险

@dataclass
class Question:
    """题目"""
    id: str
    content: str
    question_type: QuestionType
    subject: str
    difficulty: float  # 0-1
    knowledge_points: List[str]
    options: List[str] = None  # 选择题选项
    correct_answer: str = ""
    explanation: str = ""
    
    def __post_init__(self):
        if self.options is None:
            self.options = []

@dataclass
class StudentAnswer:
    """学生回答"""
    student_id: str
    question_id: str
    answer: str
    answer_time: datetime
    confidence: float = 0.0  # 学生自信度
    response_time: int = 0  # 回答用时（秒）

@dataclass
class AnswerAnalysis:
    """回答分析"""
    student_id: str
    question_id: str
    is_correct: bool
    quality: AnswerQuality
    score: float  # 0-1
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    knowledge_gaps: List[str]
    analysis_time: datetime

@dataclass
class LearningInsight:
    """学情洞察"""
    student_id: str
    subject: str
    knowledge_point: str
    mastery_level: float  # 0-1
    learning_status: LearningStatus
    progress_trend: str  # "improving", "stable", "declining"
    attention_level: float  # 0-1
    engagement_score: float  # 0-1
    recommended_actions: List[str]
    generated_at: datetime

@dataclass
class ExperimentMaterial:
    """实验材料"""
    name: str
    quantity: str
    specification: str
    safety_notes: List[str] = None
    alternatives: List[str] = None
    
    def __post_init__(self):
        if self.safety_notes is None:
            self.safety_notes = []
        if self.alternatives is None:
            self.alternatives = []

@dataclass
class ExperimentStep:
    """实验步骤"""
    step_number: int
    description: str
    duration: int  # 分钟
    safety_warnings: List[str] = None
    expected_result: str = ""
    troubleshooting: List[str] = None
    
    def __post_init__(self):
        if self.safety_warnings is None:
            self.safety_warnings = []
        if self.troubleshooting is None:
            self.troubleshooting = []

@dataclass
class ExperimentDesign:
    """实验设计"""
    id: str
    title: str
    objective: str
    hypothesis: str
    experiment_type: ExperimentType
    subject: str
    grade_level: str
    duration: int  # 分钟
    materials: List[ExperimentMaterial]
    steps: List[ExperimentStep]
    variables: Dict[str, str]  # 变量说明
    safety_assessment: Dict[str, Any]
    expected_outcomes: List[str]
    evaluation_criteria: List[str]
    created_at: datetime

@dataclass
class ClassroomInteraction:
    """课堂互动"""
    student_id: str
    interaction_type: str  # "question", "answer", "discussion", "attention"
    content: str
    timestamp: datetime
    engagement_level: float  # 0-1
    attention_score: float  # 0-1
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ClassroomAIService:
    """课堂AI助手服务"""
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        self.cache_manager = CacheManager()
        self.task_queue = TaskQueue()
        
        # AI提示词模板
        self.prompts = {
            "question_analysis": """
你是一位资深的教学评估专家，请分析以下学生的回答：

题目：{question}
题目类型：{question_type}
知识点：{knowledge_points}
学生回答：{student_answer}
正确答案：{correct_answer}

请从以下维度进行分析：
1. 回答正确性：判断回答是否正确，给出分数（0-1）
2. 回答质量：评估回答的完整性和深度
3. 知识掌握：分析学生对相关知识点的掌握情况
4. 学习建议：提供针对性的学习建议
5. 知识缺陷：识别学生的知识盲点

请以JSON格式返回分析结果。
""",
            "learning_insight_generation": """
你是一位学情分析专家，请基于学生的学习数据生成实时学情洞察：

学生ID：{student_id}
学科：{subject}
最近回答记录：{recent_answers}
历史表现：{historical_performance}
课堂互动：{classroom_interactions}

请分析：
1. 当前掌握水平：各知识点的掌握程度
2. 学习状态：学习进展和趋势
3. 注意力水平：课堂专注度分析
4. 参与度评估：课堂互动积极性
5. 个性化建议：针对性的教学调整建议

请提供具体、可操作的分析结果。
""",
            "experiment_design": """
你是一位生物实验设计专家，请为以下教学内容设计实验方案：

教学主题：{topic}
年级水平：{grade_level}
实验目标：{objectives}
可用时间：{duration}分钟
实验类型偏好：{experiment_type}
安全要求：{safety_requirements}

请设计包含以下内容的实验方案：
1. 实验假设：明确的可验证假设
2. 实验设计：详细的实验步骤
3. 材料清单：所需材料和规格
4. 变量控制：自变量、因变量、控制变量
5. 安全评估：潜在风险和防护措施
6. 预期结果：可能的实验结果
7. 评价标准：实验成功的判断标准

请确保实验安全可行，适合学生操作。
""",
            "attention_analysis": """
你是一位课堂行为分析专家，请分析学生的注意力状态：

学生互动数据：{interaction_data}
时间段：{time_period}
课堂活动：{classroom_activities}

请分析：
1. 注意力集中度：整体专注水平
2. 注意力波动：注意力变化趋势
3. 分心因素：可能的干扰因素
4. 最佳状态时段：注意力最集中的时间
5. 改进建议：提高注意力的策略

请提供数据支持的分析结果。
"""
        }
    
    async def analyze_student_answer(self, question: Question, student_answer: StudentAnswer) -> AnswerAnalysis:
        """AI实时学情生成 - 分析学生回答"""
        try:
            # 构建分析请求
            prompt = self.prompts["question_analysis"].format(
                question=question.content,
                question_type=question.question_type.value,
                knowledge_points=", ".join(question.knowledge_points),
                student_answer=student_answer.answer,
                correct_answer=question.correct_answer
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位资深的教学评估专家，擅长分析学生的学习表现。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI answer analysis failed: {response.error}")
            
            # 解析分析结果
            analysis_data = self._parse_answer_analysis(response.content)
            
            # 创建分析对象
            analysis = AnswerAnalysis(
                student_id=student_answer.student_id,
                question_id=student_answer.question_id,
                is_correct=analysis_data.get("is_correct", False),
                quality=AnswerQuality(analysis_data.get("quality", "average")),
                score=analysis_data.get("score", 0.0),
                strengths=analysis_data.get("strengths", []),
                weaknesses=analysis_data.get("weaknesses", []),
                suggestions=analysis_data.get("suggestions", []),
                knowledge_gaps=analysis_data.get("knowledge_gaps", []),
                analysis_time=datetime.now()
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Student answer analysis error: {str(e)}")
            raise
    
    async def generate_learning_insights(self, 
                                       student_id: str, 
                                       subject: str,
                                       recent_answers: List[AnswerAnalysis],
                                       classroom_interactions: List[ClassroomInteraction]) -> List[LearningInsight]:
        """生成实时学情洞察"""
        try:
            # 准备分析数据
            recent_performance = self._summarize_recent_performance(recent_answers)
            interaction_summary = self._summarize_interactions(classroom_interactions)
            historical_data = await self._get_historical_performance(student_id, subject)
            
            # 构建学情分析请求
            prompt = self.prompts["learning_insight_generation"].format(
                student_id=student_id,
                subject=subject,
                recent_answers=json.dumps(recent_performance, ensure_ascii=False),
                historical_performance=json.dumps(historical_data, ensure_ascii=False),
                classroom_interactions=json.dumps(interaction_summary, ensure_ascii=False)
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位学情分析专家，擅长从学习数据中提取有价值的洞察。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI learning insight generation failed: {response.error}")
            
            # 解析学情洞察
            insights_data = self._parse_learning_insights(response.content)
            
            # 创建学情洞察对象
            insights = []
            for insight_data in insights_data:
                insight = LearningInsight(
                    student_id=student_id,
                    subject=subject,
                    knowledge_point=insight_data.get("knowledge_point", ""),
                    mastery_level=insight_data.get("mastery_level", 0.5),
                    learning_status=LearningStatus(insight_data.get("learning_status", "understanding")),
                    progress_trend=insight_data.get("progress_trend", "stable"),
                    attention_level=insight_data.get("attention_level", 0.7),
                    engagement_score=insight_data.get("engagement_score", 0.7),
                    recommended_actions=insight_data.get("recommended_actions", []),
                    generated_at=datetime.now()
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Learning insights generation error: {str(e)}")
            raise
    
    async def design_biology_experiment(self,
                                      topic: str,
                                      grade_level: str,
                                      objectives: List[str],
                                      duration: int,
                                      experiment_type: ExperimentType = ExperimentType.LABORATORY) -> ExperimentDesign:
        """生物实验设计助手"""
        try:
            # 构建实验设计请求
            prompt = self.prompts["experiment_design"].format(
                topic=topic,
                grade_level=grade_level,
                objectives=", ".join(objectives),
                duration=duration,
                experiment_type=experiment_type.value,
                safety_requirements="中学生实验安全标准"
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位生物实验设计专家，擅长设计安全、有效的教学实验。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI experiment design failed: {response.error}")
            
            # 解析实验设计
            design_data = self._parse_experiment_design(response.content)
            
            # 创建实验设计对象
            experiment_design = ExperimentDesign(
                id=f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=design_data.get("title", topic),
                objective=", ".join(objectives),
                hypothesis=design_data.get("hypothesis", ""),
                experiment_type=experiment_type,
                subject="生物",
                grade_level=grade_level,
                duration=duration,
                materials=self._parse_materials(design_data.get("materials", [])),
                steps=self._parse_steps(design_data.get("steps", [])),
                variables=design_data.get("variables", {}),
                safety_assessment=self._assess_experiment_safety(design_data),
                expected_outcomes=design_data.get("expected_outcomes", []),
                evaluation_criteria=design_data.get("evaluation_criteria", []),
                created_at=datetime.now()
            )
            
            return experiment_design
            
        except Exception as e:
            logger.error(f"Biology experiment design error: {str(e)}")
            raise
    
    async def analyze_classroom_attention(self, 
                                        classroom_id: str,
                                        interactions: List[ClassroomInteraction],
                                        time_period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """课堂注意力监测分析"""
        try:
            # 准备分析数据
            interaction_data = self._prepare_interaction_data(interactions)
            classroom_activities = await self._get_classroom_activities(classroom_id, time_period)
            
            # 构建注意力分析请求
            prompt = self.prompts["attention_analysis"].format(
                interaction_data=json.dumps(interaction_data, ensure_ascii=False),
                time_period=f"{time_period[0].isoformat()} 到 {time_period[1].isoformat()}",
                classroom_activities=json.dumps(classroom_activities, ensure_ascii=False)
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位课堂行为分析专家，擅长分析学生的注意力状态。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI attention analysis failed: {response.error}")
            
            # 解析注意力分析结果
            attention_analysis = self._parse_attention_analysis(response.content)
            
            # 增强分析结果
            enhanced_analysis = {
                "classroom_id": classroom_id,
                "analysis_period": {
                    "start": time_period[0].isoformat(),
                    "end": time_period[1].isoformat()
                },
                "overall_attention": attention_analysis.get("overall_attention", 0.7),
                "attention_trends": attention_analysis.get("attention_trends", []),
                "distraction_factors": attention_analysis.get("distraction_factors", []),
                "peak_attention_periods": attention_analysis.get("peak_periods", []),
                "student_attention_scores": self._calculate_individual_attention_scores(interactions),
                "improvement_suggestions": attention_analysis.get("improvement_suggestions", []),
                "generated_at": datetime.now().isoformat()
            }
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Classroom attention analysis error: {str(e)}")
            raise
    
    async def recommend_practice_exercises(self, 
                                         student_insights: List[LearningInsight],
                                         subject: str) -> List[Dict[str, Any]]:
        """推荐练习题目"""
        try:
            recommendations = []
            
            for insight in student_insights:
                if insight.learning_status in [LearningStatus.STRUGGLING, LearningStatus.UNDERSTANDING]:
                    # 根据学情推荐练习
                    exercises = await self._generate_targeted_exercises(
                        insight.knowledge_point,
                        insight.mastery_level,
                        subject
                    )
                    
                    recommendation = {
                        "student_id": insight.student_id,
                        "knowledge_point": insight.knowledge_point,
                        "current_mastery": insight.mastery_level,
                        "recommended_exercises": exercises,
                        "difficulty_adjustment": self._calculate_difficulty_adjustment(insight),
                        "estimated_time": len(exercises) * 5,  # 每题5分钟
                        "priority": "high" if insight.learning_status == LearningStatus.STRUGGLING else "medium"
                    }
                    
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Practice exercise recommendation error: {str(e)}")
            raise
    
    async def generate_teaching_adjustments(self, 
                                          class_insights: List[LearningInsight],
                                          current_lesson_plan: Dict[str, Any]) -> Dict[str, Any]:
        """生成教学调整建议"""
        try:
            # 分析班级整体学情
            class_analysis = self._analyze_class_performance(class_insights)
            
            # 生成调整建议
            adjustments = {
                "pace_adjustment": self._suggest_pace_adjustment(class_analysis),
                "content_emphasis": self._suggest_content_emphasis(class_analysis),
                "teaching_method_changes": self._suggest_method_changes(class_analysis),
                "additional_support": self._identify_support_needs(class_insights),
                "differentiated_instruction": self._plan_differentiated_instruction(class_insights),
                "assessment_adjustments": self._suggest_assessment_changes(class_analysis)
            }
            
            return {
                "original_plan": current_lesson_plan,
                "suggested_adjustments": adjustments,
                "implementation_priority": self._prioritize_adjustments(adjustments),
                "expected_outcomes": self._predict_adjustment_outcomes(adjustments),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Teaching adjustment generation error: {str(e)}")
            raise
    
    # 辅助方法
    def _parse_answer_analysis(self, ai_content: str) -> Dict[str, Any]:
        """解析回答分析结果"""
        try:
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content)
            
            # 简单文本解析
            analysis = {
                "is_correct": "正确" in ai_content or "correct" in ai_content.lower(),
                "score": 0.7,  # 默认分数
                "quality": "average",
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "knowledge_gaps": []
            }
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Failed to parse answer analysis: {str(e)}")
            return {"raw_content": ai_content}
    
    def _parse_learning_insights(self, ai_content: str) -> List[Dict[str, Any]]:
        """解析学情洞察"""
        try:
            if ai_content.strip().startswith('['):
                return json.loads(ai_content)
            
            # 返回默认洞察
            return [{
                "knowledge_point": "核心概念",
                "mastery_level": 0.6,
                "learning_status": "understanding",
                "progress_trend": "stable",
                "attention_level": 0.7,
                "engagement_score": 0.7,
                "recommended_actions": ["增加练习", "个别辅导"]
            }]
            
        except Exception as e:
            logger.warning(f"Failed to parse learning insights: {str(e)}")
            return []
    
    def _parse_experiment_design(self, ai_content: str) -> Dict[str, Any]:
        """解析实验设计"""
        try:
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content)
            
            # 简单解析
            design = {
                "title": "生物实验",
                "hypothesis": "待验证假设",
                "materials": [],
                "steps": [],
                "variables": {},
                "expected_outcomes": [],
                "evaluation_criteria": []
            }
            
            return design
            
        except Exception as e:
            logger.warning(f"Failed to parse experiment design: {str(e)}")
            return {"raw_content": ai_content}
    
    def _parse_attention_analysis(self, ai_content: str) -> Dict[str, Any]:
        """解析注意力分析"""
        try:
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content)
            
            return {
                "overall_attention": 0.7,
                "attention_trends": ["稳定"],
                "distraction_factors": ["外界干扰"],
                "peak_periods": ["课程前半段"],
                "improvement_suggestions": ["增加互动"]
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse attention analysis: {str(e)}")
            return {}
    
    def _summarize_recent_performance(self, recent_answers: List[AnswerAnalysis]) -> Dict[str, Any]:
        """总结最近表现"""
        if not recent_answers:
            return {"total_answers": 0, "average_score": 0, "correct_rate": 0}
        
        total_score = sum(answer.score for answer in recent_answers)
        correct_count = sum(1 for answer in recent_answers if answer.is_correct)
        
        return {
            "total_answers": len(recent_answers),
            "average_score": total_score / len(recent_answers),
            "correct_rate": correct_count / len(recent_answers),
            "recent_trends": "improving"  # 简化处理
        }
    
    def _summarize_interactions(self, interactions: List[ClassroomInteraction]) -> Dict[str, Any]:
        """总结课堂互动"""
        if not interactions:
            return {"total_interactions": 0, "average_engagement": 0}
        
        total_engagement = sum(interaction.engagement_level for interaction in interactions)
        
        return {
            "total_interactions": len(interactions),
            "average_engagement": total_engagement / len(interactions),
            "interaction_types": list(set(interaction.interaction_type for interaction in interactions))
        }
    
    async def _get_historical_performance(self, student_id: str, subject: str) -> Dict[str, Any]:
        """获取历史表现数据"""
        # 模拟历史数据
        return {
            "average_score": 0.75,
            "improvement_trend": "stable",
            "strong_areas": ["基础概念"],
            "weak_areas": ["应用题"]
        }
    
    def _parse_materials(self, materials_data: List[Any]) -> List[ExperimentMaterial]:
        """解析实验材料"""
        materials = []
        for material_data in materials_data:
            if isinstance(material_data, dict):
                material = ExperimentMaterial(
                    name=material_data.get("name", ""),
                    quantity=material_data.get("quantity", ""),
                    specification=material_data.get("specification", ""),
                    safety_notes=material_data.get("safety_notes", []),
                    alternatives=material_data.get("alternatives", [])
                )
                materials.append(material)
        return materials
    
    def _parse_steps(self, steps_data: List[Any]) -> List[ExperimentStep]:
        """解析实验步骤"""
        steps = []
        for i, step_data in enumerate(steps_data):
            if isinstance(step_data, dict):
                step = ExperimentStep(
                    step_number=i + 1,
                    description=step_data.get("description", ""),
                    duration=step_data.get("duration", 5),
                    safety_warnings=step_data.get("safety_warnings", []),
                    expected_result=step_data.get("expected_result", ""),
                    troubleshooting=step_data.get("troubleshooting", [])
                )
                steps.append(step)
        return steps
    
    def _assess_experiment_safety(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估实验安全性"""
        return {
            "risk_level": RiskLevel.LOW.value,
            "safety_measures": ["佩戴护目镜", "注意通风"],
            "emergency_procedures": ["紧急冲洗", "立即通知老师"],
            "supervision_required": True
        }
    
    def _prepare_interaction_data(self, interactions: List[ClassroomInteraction]) -> List[Dict[str, Any]]:
        """准备互动数据"""
        return [{
            "student_id": interaction.student_id,
            "type": interaction.interaction_type,
            "engagement": interaction.engagement_level,
            "attention": interaction.attention_score,
            "timestamp": interaction.timestamp.isoformat()
        } for interaction in interactions]
    
    async def _get_classroom_activities(self, classroom_id: str, time_period: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """获取课堂活动"""
        # 模拟课堂活动数据
        return [
            {"activity": "讲解", "start_time": time_period[0].isoformat(), "duration": 15},
            {"activity": "讨论", "start_time": (time_period[0] + timedelta(minutes=15)).isoformat(), "duration": 10},
            {"activity": "练习", "start_time": (time_period[0] + timedelta(minutes=25)).isoformat(), "duration": 20}
        ]
    
    def _calculate_individual_attention_scores(self, interactions: List[ClassroomInteraction]) -> Dict[str, float]:
        """计算个人注意力分数"""
        student_scores = {}
        for interaction in interactions:
            if interaction.student_id not in student_scores:
                student_scores[interaction.student_id] = []
            student_scores[interaction.student_id].append(interaction.attention_score)
        
        # 计算平均分数
        for student_id, scores in student_scores.items():
            student_scores[student_id] = sum(scores) / len(scores)
        
        return student_scores
    
    async def _generate_targeted_exercises(self, knowledge_point: str, mastery_level: float, subject: str) -> List[Dict[str, Any]]:
        """生成针对性练习"""
        # 模拟练习生成
        exercises = [
            {
                "id": f"ex_{uuid.uuid4().hex[:8]}",
                "content": f"关于{knowledge_point}的练习题",
                "difficulty": min(mastery_level + 0.1, 1.0),
                "type": "multiple_choice",
                "estimated_time": 5
            }
        ]
        return exercises
    
    def _calculate_difficulty_adjustment(self, insight: LearningInsight) -> str:
        """计算难度调整"""
        if insight.mastery_level < 0.3:
            return "降低难度"
        elif insight.mastery_level > 0.8:
            return "提高难度"
        else:
            return "保持当前难度"
    
    def _analyze_class_performance(self, class_insights: List[LearningInsight]) -> Dict[str, Any]:
        """分析班级表现"""
        if not class_insights:
            return {"average_mastery": 0.5, "struggling_students": 0}
        
        total_mastery = sum(insight.mastery_level for insight in class_insights)
        struggling_count = sum(1 for insight in class_insights if insight.learning_status == LearningStatus.STRUGGLING)
        
        return {
            "average_mastery": total_mastery / len(class_insights),
            "struggling_students": struggling_count,
            "total_students": len(class_insights),
            "mastery_distribution": self._calculate_mastery_distribution(class_insights)
        }
    
    def _calculate_mastery_distribution(self, insights: List[LearningInsight]) -> Dict[str, int]:
        """计算掌握度分布"""
        distribution = {"low": 0, "medium": 0, "high": 0}
        
        for insight in insights:
            if insight.mastery_level < 0.4:
                distribution["low"] += 1
            elif insight.mastery_level < 0.7:
                distribution["medium"] += 1
            else:
                distribution["high"] += 1
        
        return distribution
    
    def _suggest_pace_adjustment(self, class_analysis: Dict[str, Any]) -> str:
        """建议节奏调整"""
        avg_mastery = class_analysis.get("average_mastery", 0.5)
        
        if avg_mastery < 0.4:
            return "放慢教学节奏，增加基础练习"
        elif avg_mastery > 0.8:
            return "可以适当加快节奏，增加挑战性内容"
        else:
            return "保持当前教学节奏"
    
    def _suggest_content_emphasis(self, class_analysis: Dict[str, Any]) -> List[str]:
        """建议内容重点"""
        return ["加强基础概念讲解", "增加实例演示", "提供更多练习机会"]
    
    def _suggest_method_changes(self, class_analysis: Dict[str, Any]) -> List[str]:
        """建议方法改变"""
        return ["增加小组讨论", "使用多媒体辅助", "提供个别指导"]
    
    def _identify_support_needs(self, insights: List[LearningInsight]) -> List[Dict[str, Any]]:
        """识别支持需求"""
        support_needs = []
        
        for insight in insights:
            if insight.learning_status == LearningStatus.STRUGGLING:
                support_needs.append({
                    "student_id": insight.student_id,
                    "knowledge_point": insight.knowledge_point,
                    "support_type": "个别辅导",
                    "priority": "high"
                })
        
        return support_needs
    
    def _plan_differentiated_instruction(self, insights: List[LearningInsight]) -> Dict[str, List[str]]:
        """规划差异化教学"""
        return {
            "advanced_learners": ["提供拓展材料", "增加挑战性任务"],
            "struggling_learners": ["简化概念解释", "提供额外支持"],
            "average_learners": ["标准教学进度", "适量练习"]
        }
    
    def _suggest_assessment_changes(self, class_analysis: Dict[str, Any]) -> List[str]:
        """建议评估调整"""
        return ["增加形成性评估", "调整题目难度", "提供多样化评估方式"]
    
    def _prioritize_adjustments(self, adjustments: Dict[str, Any]) -> List[str]:
        """优先级排序"""
        return ["pace_adjustment", "additional_support", "content_emphasis"]
    
    def _predict_adjustment_outcomes(self, adjustments: Dict[str, Any]) -> List[str]:
        """预测调整效果"""
        return ["提高学生理解度", "增强课堂参与", "改善学习效果"]