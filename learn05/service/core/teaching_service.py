# -*- coding: utf-8 -*-
"""
教学服务模块

本模块实现了智能教学相关的核心业务逻辑，包括课程管理、学习分析、个性化推荐等。
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

from .ai_service import AIServiceManager, AIRequest, AIProvider
from .cache_service import CacheManager

logger = logging.getLogger(__name__)

class LearningStyle(Enum):
    """学习风格"""
    VISUAL = "visual"  # 视觉型
    AUDITORY = "auditory"  # 听觉型
    KINESTHETIC = "kinesthetic"  # 动觉型
    READING = "reading"  # 阅读型

class DifficultyLevel(Enum):
    """难度等级"""
    BEGINNER = "beginner"  # 初级
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级
    EXPERT = "expert"  # 专家级

class ContentType(Enum):
    """内容类型"""
    TEXT = "text"  # 文本
    IMAGE = "image"  # 图片
    VIDEO = "video"  # 视频
    AUDIO = "audio"  # 音频
    INTERACTIVE = "interactive"  # 交互式
    EXPERIMENT = "experiment"  # 实验

class AssessmentType(Enum):
    """评估类型"""
    QUIZ = "quiz"  # 测验
    ASSIGNMENT = "assignment"  # 作业
    PROJECT = "project"  # 项目
    EXAM = "exam"  # 考试
    DISCUSSION = "discussion"  # 讨论

@dataclass
class LearningObjective:
    """学习目标"""
    id: str
    title: str
    description: str
    subject: str
    difficulty: DifficultyLevel
    estimated_time: int  # 预计学习时间（分钟）
    prerequisites: List[str] = None  # 前置知识点
    keywords: List[str] = None  # 关键词
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.keywords is None:
            self.keywords = []

@dataclass
class LearningContent:
    """学习内容"""
    id: str
    objective_id: str
    title: str
    content_type: ContentType
    content: str
    metadata: Dict[str, Any] = None
    duration: Optional[int] = None  # 内容时长（秒）
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class StudentProfile:
    """学生档案"""
    student_id: str
    name: str
    grade_level: str
    learning_style: LearningStyle
    strengths: List[str] = None  # 优势学科
    weaknesses: List[str] = None  # 薄弱学科
    interests: List[str] = None  # 兴趣爱好
    learning_pace: float = 1.0  # 学习节奏（相对于平均水平）
    attention_span: int = 30  # 注意力持续时间（分钟）
    preferred_content_types: List[ContentType] = None
    
    def __post_init__(self):
        if self.strengths is None:
            self.strengths = []
        if self.weaknesses is None:
            self.weaknesses = []
        if self.interests is None:
            self.interests = []
        if self.preferred_content_types is None:
            self.preferred_content_types = [ContentType.TEXT]

@dataclass
class LearningProgress:
    """学习进度"""
    student_id: str
    objective_id: str
    progress: float  # 完成百分比
    time_spent: int  # 已花费时间（分钟）
    last_accessed: datetime
    mastery_level: float  # 掌握程度（0-1）
    attempts: int = 0  # 尝试次数
    
class TeachingService:
    """教学服务"""
    
    def __init__(self, ai_manager: AIServiceManager, cache_manager: CacheManager):
        self.ai_manager = ai_manager
        self.cache_manager = cache_manager
        
        # 教学提示词模板
        self.prompts = {
            "content_generation": """
你是一位经验丰富的教师，请为以下学习目标生成高质量的教学内容：

学习目标：{objective}
难度等级：{difficulty}
目标学生：{target_audience}
内容类型：{content_type}

请生成结构化的教学内容，包括：
1. 核心概念解释
2. 具体例子
3. 练习题目
4. 总结要点

内容应该清晰易懂，符合学生的认知水平。
""",
            "personalized_recommendation": """
基于学生的学习档案和进度，为其推荐个性化的学习内容：

学生档案：{student_profile}
学习进度：{learning_progress}
可选内容：{available_content}

请分析学生的学习特点，推荐最适合的学习路径和内容，并说明推荐理由。
""",
            "learning_analysis": """
分析学生的学习数据，提供个性化的学习建议：

学生ID：{student_id}
学习数据：{learning_data}
表现统计：{performance_stats}

请分析学生的学习模式、优势和不足，提供具体的改进建议。
""",
            "adaptive_assessment": """
根据学生的能力水平生成自适应评估题目：

学科：{subject}
知识点：{topic}
学生能力：{ability_level}
题目类型：{question_type}
难度要求：{difficulty}

请生成{num_questions}道题目，包括题目、选项（如适用）和标准答案。
"""
        }
    
    async def generate_learning_content(
        self,
        objective: LearningObjective,
        target_audience: str,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """生成学习内容"""
        try:
            # 检查缓存
            cache_key = f"content_{objective.id}_{content_type.value}_{hash(target_audience)}"
            cached_content = await self.cache_manager.get("teaching", cache_key)
            if cached_content:
                return cached_content
            
            # 构建AI请求
            prompt = self.prompts["content_generation"].format(
                objective=f"{objective.title}: {objective.description}",
                difficulty=objective.difficulty.value,
                target_audience=target_audience,
                content_type=content_type.value
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的教学内容设计师，擅长创建高质量的教育材料。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI content generation failed: {response.error}")
            
            # 解析生成的内容
            content_data = {
                "objective_id": objective.id,
                "content_type": content_type.value,
                "generated_content": response.content,
                "metadata": {
                    "difficulty": objective.difficulty.value,
                    "estimated_time": objective.estimated_time,
                    "generated_at": datetime.now().isoformat(),
                    "ai_model": response.model,
                    "target_audience": target_audience
                }
            }
            
            # 缓存结果
            await self.cache_manager.set("teaching", cache_key, content_data, 7200)
            
            return content_data
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            raise
    
    async def get_personalized_recommendations(
        self,
        student_profile: StudentProfile,
        learning_progress: List[LearningProgress],
        available_objectives: List[LearningObjective]
    ) -> Dict[str, Any]:
        """获取个性化学习推荐"""
        try:
            # 检查缓存
            cache_key = f"recommendations_{student_profile.student_id}_{hash(str(learning_progress))}"
            cached_recommendations = await self.cache_manager.get("teaching", cache_key)
            if cached_recommendations:
                return cached_recommendations
            
            # 分析学习进度
            progress_summary = self._analyze_learning_progress(learning_progress)
            
            # 筛选适合的学习目标
            suitable_objectives = self._filter_suitable_objectives(
                student_profile, progress_summary, available_objectives
            )
            
            # 构建AI推荐请求
            prompt = self.prompts["personalized_recommendation"].format(
                student_profile=asdict(student_profile),
                learning_progress=progress_summary,
                available_content=[asdict(obj) for obj in suitable_objectives[:10]]  # 限制数量
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位个性化学习专家，擅长根据学生特点推荐最适合的学习内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI recommendation failed: {response.error}")
            
            recommendations = {
                "student_id": student_profile.student_id,
                "recommended_objectives": suitable_objectives[:5],  # 前5个推荐
                "ai_analysis": response.content,
                "learning_path": self._generate_learning_path(suitable_objectives[:5]),
                "estimated_completion_time": sum(obj.estimated_time for obj in suitable_objectives[:5]),
                "generated_at": datetime.now().isoformat()
            }
            
            # 缓存推荐结果
            await self.cache_manager.set("teaching", cache_key, recommendations, 3600)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Personalized recommendation error: {str(e)}")
            raise
    
    async def analyze_learning_performance(
        self,
        student_id: str,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """分析学习表现"""
        try:
            # 检查缓存
            cache_key = f"analysis_{student_id}_{time_range[0].date()}_{time_range[1].date()}"
            cached_analysis = await self.cache_manager.get("analytics", cache_key)
            if cached_analysis:
                return cached_analysis
            
            # 获取学习数据（这里使用模拟数据）
            learning_data = await self._get_learning_data(student_id, time_range)
            performance_stats = self._calculate_performance_stats(learning_data)
            
            # 构建AI分析请求
            prompt = self.prompts["learning_analysis"].format(
                student_id=student_id,
                learning_data=learning_data,
                performance_stats=performance_stats
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位学习分析专家，擅长从学习数据中发现模式和提供改进建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI analysis failed: {response.error}")
            
            analysis_result = {
                "student_id": student_id,
                "time_range": {
                    "start": time_range[0].isoformat(),
                    "end": time_range[1].isoformat()
                },
                "performance_stats": performance_stats,
                "ai_insights": response.content,
                "recommendations": self._extract_recommendations(response.content),
                "trends": self._analyze_trends(learning_data),
                "generated_at": datetime.now().isoformat()
            }
            
            # 缓存分析结果
            await self.cache_manager.set("analytics", cache_key, analysis_result, 1800)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Learning performance analysis error: {str(e)}")
            raise
    
    async def generate_adaptive_assessment(
        self,
        subject: str,
        topic: str,
        student_ability: float,
        question_type: AssessmentType,
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """生成自适应评估"""
        try:
            # 根据学生能力确定难度
            if student_ability < 0.3:
                difficulty = DifficultyLevel.BEGINNER
            elif student_ability < 0.6:
                difficulty = DifficultyLevel.INTERMEDIATE
            elif student_ability < 0.8:
                difficulty = DifficultyLevel.ADVANCED
            else:
                difficulty = DifficultyLevel.EXPERT
            
            # 检查缓存
            cache_key = f"assessment_{subject}_{topic}_{difficulty.value}_{question_type.value}_{num_questions}"
            cached_assessment = await self.cache_manager.get("teaching", cache_key)
            if cached_assessment:
                return cached_assessment
            
            # 构建AI请求
            prompt = self.prompts["adaptive_assessment"].format(
                subject=subject,
                topic=topic,
                ability_level=f"{student_ability:.2f} ({difficulty.value})",
                question_type=question_type.value,
                difficulty=difficulty.value,
                num_questions=num_questions
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的教育评估专家，擅长设计高质量的评估题目。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI assessment generation failed: {response.error}")
            
            assessment_data = {
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty.value,
                "question_type": question_type.value,
                "num_questions": num_questions,
                "questions": response.content,
                "target_ability": student_ability,
                "estimated_time": num_questions * 3,  # 每题3分钟
                "generated_at": datetime.now().isoformat()
            }
            
            # 缓存评估
            await self.cache_manager.set("teaching", cache_key, assessment_data, 3600)
            
            return assessment_data
            
        except Exception as e:
            logger.error(f"Adaptive assessment generation error: {str(e)}")
            raise
    
    def _analyze_learning_progress(self, progress_list: List[LearningProgress]) -> Dict[str, Any]:
        """分析学习进度"""
        if not progress_list:
            return {"total_objectives": 0, "average_progress": 0, "average_mastery": 0}
        
        total_progress = sum(p.progress for p in progress_list)
        total_mastery = sum(p.mastery_level for p in progress_list)
        total_time = sum(p.time_spent for p in progress_list)
        
        return {
            "total_objectives": len(progress_list),
            "completed_objectives": len([p for p in progress_list if p.progress >= 100]),
            "average_progress": total_progress / len(progress_list),
            "average_mastery": total_mastery / len(progress_list),
            "total_time_spent": total_time,
            "recent_activity": max(p.last_accessed for p in progress_list).isoformat()
        }
    
    def _filter_suitable_objectives(
        self,
        student_profile: StudentProfile,
        progress_summary: Dict[str, Any],
        available_objectives: List[LearningObjective]
    ) -> List[LearningObjective]:
        """筛选适合的学习目标"""
        suitable = []
        
        for objective in available_objectives:
            # 根据学生水平筛选难度
            avg_mastery = progress_summary.get("average_mastery", 0.5)
            
            if avg_mastery < 0.3 and objective.difficulty in [DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]:
                continue
            elif avg_mastery > 0.8 and objective.difficulty == DifficultyLevel.BEGINNER:
                continue
            
            # 根据学习节奏调整
            if student_profile.learning_pace < 0.8 and objective.estimated_time > student_profile.attention_span:
                continue
            
            suitable.append(objective)
        
        # 按难度和预计时间排序
        suitable.sort(key=lambda x: (x.difficulty.value, x.estimated_time))
        
        return suitable
    
    def _generate_learning_path(self, objectives: List[LearningObjective]) -> List[Dict[str, Any]]:
        """生成学习路径"""
        path = []
        
        for i, objective in enumerate(objectives):
            step = {
                "step": i + 1,
                "objective_id": objective.id,
                "title": objective.title,
                "difficulty": objective.difficulty.value,
                "estimated_time": objective.estimated_time,
                "prerequisites": objective.prerequisites
            }
            path.append(step)
        
        return path
    
    async def _get_learning_data(self, student_id: str, time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """获取学习数据（模拟实现）"""
        # 这里应该从数据库获取真实的学习数据
        return {
            "sessions": 15,
            "total_time": 450,  # 分钟
            "objectives_completed": 8,
            "average_score": 78.5,
            "subjects": ["数学", "物理", "化学"],
            "activity_pattern": "evening_learner",
            "engagement_level": 0.75
        }
    
    def _calculate_performance_stats(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算表现统计"""
        return {
            "efficiency": learning_data["objectives_completed"] / (learning_data["total_time"] / 60),  # 每小时完成目标数
            "consistency": 0.8,  # 学习一致性
            "improvement_rate": 0.15,  # 改进率
            "engagement_score": learning_data["engagement_level"] * 100
        }
    
    def _extract_recommendations(self, ai_content: str) -> List[str]:
        """从AI分析中提取建议（简化实现）"""
        # 这里应该使用更复杂的NLP技术来提取建议
        recommendations = [
            "增加练习时间以提高熟练度",
            "关注薄弱知识点的复习",
            "保持当前的学习节奏",
            "尝试不同的学习方法"
        ]
        return recommendations
    
    def _analyze_trends(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析学习趋势"""
        return {
            "score_trend": "improving",  # improving, declining, stable
            "time_trend": "consistent",
            "engagement_trend": "increasing",
            "difficulty_progression": "appropriate"
        }
    
    # 课堂实时分析功能
    async def analyze_classroom_interaction(
        self,
        classroom_id: str,
        interaction_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析课堂互动"""
        try:
            # 分析互动模式
            interaction_stats = self._calculate_interaction_stats(interaction_data)
            
            # 识别需要关注的学生
            attention_alerts = self._identify_attention_issues(interaction_data)
            
            # 生成教学建议
            teaching_suggestions = await self._generate_teaching_suggestions(
                interaction_stats, attention_alerts
            )
            
            return {
                "classroom_id": classroom_id,
                "analysis_time": datetime.now().isoformat(),
                "interaction_stats": interaction_stats,
                "attention_alerts": attention_alerts,
                "teaching_suggestions": teaching_suggestions,
                "overall_engagement": interaction_stats.get("average_engagement", 0.5)
            }
            
        except Exception as e:
            logger.error(f"Classroom interaction analysis error: {str(e)}")
            raise
    
    def _calculate_interaction_stats(self, interaction_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算互动统计"""
        if not interaction_data:
            return {}
        
        total_interactions = len(interaction_data)
        active_students = len(set(i.get("student_id") for i in interaction_data if i.get("student_id")))
        
        return {
            "total_interactions": total_interactions,
            "active_students": active_students,
            "average_engagement": sum(i.get("engagement_score", 0.5) for i in interaction_data) / total_interactions,
            "question_count": len([i for i in interaction_data if i.get("type") == "question"]),
            "answer_count": len([i for i in interaction_data if i.get("type") == "answer"]),
            "participation_rate": active_students / max(1, total_interactions) * 100
        }
    
    def _identify_attention_issues(self, interaction_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别注意力问题"""
        alerts = []
        
        # 分析每个学生的参与度
        student_engagement = {}
        for interaction in interaction_data:
            student_id = interaction.get("student_id")
            if student_id:
                if student_id not in student_engagement:
                    student_engagement[student_id] = []
                student_engagement[student_id].append(interaction.get("engagement_score", 0.5))
        
        # 识别低参与度学生
        for student_id, scores in student_engagement.items():
            avg_engagement = sum(scores) / len(scores)
            if avg_engagement < 0.3:
                alerts.append({
                    "student_id": student_id,
                    "type": "low_engagement",
                    "severity": "high" if avg_engagement < 0.2 else "medium",
                    "description": f"学生参与度较低 ({avg_engagement:.2f})"
                })
        
        return alerts
    
    async def _generate_teaching_suggestions(
        self,
        interaction_stats: Dict[str, Any],
        attention_alerts: List[Dict[str, Any]]
    ) -> List[str]:
        """生成教学建议"""
        suggestions = []
        
        # 基于统计数据的建议
        engagement = interaction_stats.get("average_engagement", 0.5)
        if engagement < 0.4:
            suggestions.append("建议增加互动环节，提高学生参与度")
        elif engagement > 0.8:
            suggestions.append("学生参与度很高，可以适当增加难度")
        
        participation_rate = interaction_stats.get("participation_rate", 0)
        if participation_rate < 50:
            suggestions.append("建议鼓励更多学生参与讨论")
        
        # 基于注意力警报的建议
        if attention_alerts:
            suggestions.append(f"有{len(attention_alerts)}名学生需要特别关注")
            suggestions.append("建议采用更多样化的教学方式")
        
        return suggestions