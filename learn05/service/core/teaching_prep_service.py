# -*- coding: utf-8 -*-
"""
备课助手服务模块

本模块实现了智能备课助手的核心功能，包括教材智能分析、教学环节策划、学情预设分析和优秀案例推荐。
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

from .ai_service import AIServiceManager, AIRequest, AIProvider
from .cache_service import CacheManager
from .task_service import TaskQueue, Task, TaskType, TaskPriority

logger = logging.getLogger(__name__)

class SubjectType(Enum):
    """学科类型"""
    CHINESE = "chinese"  # 语文
    MATH = "math"  # 数学
    ENGLISH = "english"  # 英语
    PHYSICS = "physics"  # 物理
    CHEMISTRY = "chemistry"  # 化学
    BIOLOGY = "biology"  # 生物
    HISTORY = "history"  # 历史
    GEOGRAPHY = "geography"  # 地理
    POLITICS = "politics"  # 政治

class TeachingPhase(Enum):
    """教学环节"""
    INTRODUCTION = "introduction"  # 导入
    PRESENTATION = "presentation"  # 新授
    PRACTICE = "practice"  # 练习
    CONSOLIDATION = "consolidation"  # 巩固
    SUMMARY = "summary"  # 总结
    HOMEWORK = "homework"  # 作业
    ASSESSMENT = "assessment"  # 评价

class DifficultyLevel(Enum):
    """难度等级"""
    BASIC = "basic"  # 基础
    INTERMEDIATE = "intermediate"  # 中等
    ADVANCED = "advanced"  # 提高
    CHALLENGE = "challenge"  # 挑战

class TeachingStyle(Enum):
    """教学风格"""
    TRADITIONAL = "traditional"  # 传统讲授
    INTERACTIVE = "interactive"  # 互动式
    INQUIRY = "inquiry"  # 探究式
    COLLABORATIVE = "collaborative"  # 合作式
    FLIPPED = "flipped"  # 翻转课堂
    PROJECT_BASED = "project_based"  # 项目式

@dataclass
class TextbookContent:
    """教材内容"""
    id: str
    title: str
    subject: SubjectType
    grade: str
    chapter: str
    section: str
    content: str
    images: List[str] = None  # 图片URL列表
    exercises: List[Dict[str, Any]] = None  # 练习题
    key_points: List[str] = None  # 重点
    difficult_points: List[str] = None  # 难点
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.exercises is None:
            self.exercises = []
        if self.key_points is None:
            self.key_points = []
        if self.difficult_points is None:
            self.difficult_points = []

@dataclass
class KnowledgePoint:
    """知识点"""
    id: str
    name: str
    description: str
    subject: SubjectType
    difficulty: DifficultyLevel
    prerequisites: List[str] = None  # 前置知识点
    related_points: List[str] = None  # 相关知识点
    teaching_methods: List[str] = None  # 教学方法建议
    common_mistakes: List[str] = None  # 常见错误
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.related_points is None:
            self.related_points = []
        if self.teaching_methods is None:
            self.teaching_methods = []
        if self.common_mistakes is None:
            self.common_mistakes = []

@dataclass
class TeachingPlan:
    """教学计划"""
    id: str
    title: str
    subject: SubjectType
    grade: str
    duration: int  # 课时长度（分钟）
    objectives: List[str]  # 教学目标
    key_points: List[str]  # 重点
    difficult_points: List[str]  # 难点
    phases: List[Dict[str, Any]]  # 教学环节
    materials: List[str]  # 教学材料
    assessment: Dict[str, Any]  # 评价方式
    homework: Dict[str, Any]  # 作业安排
    created_at: datetime
    teacher_id: str

@dataclass
class StudentPreset:
    """学情预设"""
    grade: str
    subject: SubjectType
    knowledge_base: Dict[str, float]  # 知识掌握情况
    learning_characteristics: List[str]  # 学习特点
    common_difficulties: List[str]  # 常见困难
    attention_span: int  # 注意力持续时间
    preferred_methods: List[TeachingStyle]  # 偏好的教学方式
    motivation_factors: List[str]  # 激励因素

@dataclass
class TeachingCase:
    """教学案例"""
    id: str
    title: str
    subject: SubjectType
    grade: str
    topic: str
    teaching_style: TeachingStyle
    description: str
    objectives: List[str]
    process: List[Dict[str, Any]]  # 教学过程
    materials: List[str]
    effectiveness: float  # 效果评分
    feedback: List[str]  # 反馈
    tags: List[str]  # 标签
    author: str
    created_at: datetime

class TeachingPrepService:
    """备课助手服务"""
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        self.cache_manager = CacheManager()
        self.task_queue = TaskQueue()
        
        # AI提示词模板
        self.prompts = {
            "textbook_analysis": """
你是一位资深的教学专家，请深入分析以下教材内容：

教材信息：
- 学科：{subject}
- 年级：{grade}
- 章节：{chapter}
- 内容：{content}

请从以下维度进行分析：
1. 知识点梳理：提取核心知识点，标注重难点
2. 教学目标：制定具体、可测量的教学目标
3. 学情分析：分析学生可能的认知基础和学习困难
4. 教学建议：推荐适合的教学方法和策略
5. 评价方式：设计形成性和终结性评价方案

请以结构化的JSON格式返回分析结果。
""",
            "lesson_planning": """
你是一位优秀的教学设计师，请为以下内容设计详细的教学方案：

教学内容：{content}
学科：{subject}
年级：{grade}
课时：{duration}分钟
教学风格：{teaching_style}
学生特点：{student_characteristics}

请设计包含以下环节的教学方案：
1. 导入环节（5-8分钟）：激发兴趣，引出主题
2. 新授环节（20-25分钟）：核心内容讲解
3. 练习环节（10-15分钟）：巩固练习
4. 总结环节（3-5分钟）：梳理要点
5. 作业布置：分层作业设计

每个环节请包含：目标、活动、时间、教师行为、学生行为、设计意图。
""",
            "student_preset_analysis": """
你是一位学情分析专家，请分析以下年级学生的学习特点：

年级：{grade}
学科：{subject}
教学内容：{topic}

请从以下方面分析学生学情：
1. 认知发展水平：该年龄段学生的认知特点
2. 知识基础：学习本内容需要的前置知识
3. 学习能力：注意力、记忆力、理解力特点
4. 学习兴趣：可能的兴趣点和激励因素
5. 常见困难：学习本内容时的典型困难
6. 教学建议：针对性的教学策略建议

请提供具体、实用的分析结果。
""",
            "case_recommendation": """
你是一位教学案例专家，请根据以下需求推荐优秀的教学案例：

教学需求：
- 学科：{subject}
- 年级：{grade}
- 主题：{topic}
- 教学风格偏好：{preferred_style}
- 学生特点：{student_features}

可选案例：{available_cases}

请分析每个案例的适用性，并推荐最匹配的3-5个案例，说明推荐理由。
包含：
1. 案例匹配度分析
2. 优势特点
3. 适用场景
4. 可借鉴的亮点
5. 需要调整的地方
"""
        }
    
    async def analyze_textbook(self, textbook_content: TextbookContent) -> Dict[str, Any]:
        """教材智能分析引擎"""
        try:
            # 检查缓存
            cache_key = f"textbook_analysis_{textbook_content.id}"
            cached_result = await self.cache_manager.get("teaching_prep", cache_key)
            if cached_result:
                return cached_result
            
            # 构建分析请求
            prompt = self.prompts["textbook_analysis"].format(
                subject=textbook_content.subject.value,
                grade=textbook_content.grade,
                chapter=f"{textbook_content.chapter} - {textbook_content.section}",
                content=textbook_content.content[:2000]  # 限制内容长度
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位资深的教学专家，擅长教材分析和教学设计。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI textbook analysis failed: {response.error}")
            
            # 解析分析结果
            analysis_result = self._parse_textbook_analysis(response.content)
            
            # 增强分析结果
            enhanced_result = {
                "textbook_id": textbook_content.id,
                "subject": textbook_content.subject.value,
                "grade": textbook_content.grade,
                "chapter_info": {
                    "chapter": textbook_content.chapter,
                    "section": textbook_content.section,
                    "title": textbook_content.title
                },
                "analysis": analysis_result,
                "knowledge_points": await self._extract_knowledge_points(textbook_content),
                "difficulty_assessment": self._assess_content_difficulty(textbook_content),
                "teaching_suggestions": self._generate_teaching_suggestions(analysis_result),
                "analyzed_at": datetime.now().isoformat()
            }
            
            # 缓存结果
            await self.cache_manager.set("teaching_prep", cache_key, enhanced_result, 7200)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Textbook analysis error: {str(e)}")
            raise
    
    async def design_lesson_plan(self, 
                               content: str,
                               subject: SubjectType,
                               grade: str,
                               duration: int,
                               teaching_style: TeachingStyle,
                               student_preset: StudentPreset) -> TeachingPlan:
        """教学环节策划系统"""
        try:
            # 构建教学设计请求
            prompt = self.prompts["lesson_planning"].format(
                content=content[:1500],
                subject=subject.value,
                grade=grade,
                duration=duration,
                teaching_style=teaching_style.value,
                student_characteristics=self._format_student_characteristics(student_preset)
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位优秀的教学设计师，擅长设计高效的教学方案。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI lesson planning failed: {response.error}")
            
            # 解析教学方案
            lesson_data = self._parse_lesson_plan(response.content)
            
            # 创建教学计划对象
            teaching_plan = TeachingPlan(
                id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=lesson_data.get("title", "教学方案"),
                subject=subject,
                grade=grade,
                duration=duration,
                objectives=lesson_data.get("objectives", []),
                key_points=lesson_data.get("key_points", []),
                difficult_points=lesson_data.get("difficult_points", []),
                phases=lesson_data.get("phases", []),
                materials=lesson_data.get("materials", []),
                assessment=lesson_data.get("assessment", {}),
                homework=lesson_data.get("homework", {}),
                created_at=datetime.now(),
                teacher_id=""  # 将在API层设置
            )
            
            return teaching_plan
            
        except Exception as e:
            logger.error(f"Lesson planning error: {str(e)}")
            raise
    
    async def analyze_student_preset(self, 
                                   grade: str, 
                                   subject: SubjectType, 
                                   topic: str) -> StudentPreset:
        """学情预设分析平台"""
        try:
            # 检查缓存
            cache_key = f"student_preset_{grade}_{subject.value}_{hash(topic)}"
            cached_preset = await self.cache_manager.get("teaching_prep", cache_key)
            if cached_preset:
                return StudentPreset(**cached_preset)
            
            # 构建学情分析请求
            prompt = self.prompts["student_preset_analysis"].format(
                grade=grade,
                subject=subject.value,
                topic=topic
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位学情分析专家，深入了解不同年龄段学生的学习特点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI student preset analysis failed: {response.error}")
            
            # 解析学情分析结果
            preset_data = self._parse_student_preset(response.content)
            
            # 创建学情预设对象
            student_preset = StudentPreset(
                grade=grade,
                subject=subject,
                knowledge_base=preset_data.get("knowledge_base", {}),
                learning_characteristics=preset_data.get("learning_characteristics", []),
                common_difficulties=preset_data.get("common_difficulties", []),
                attention_span=preset_data.get("attention_span", 30),
                preferred_methods=preset_data.get("preferred_methods", [TeachingStyle.INTERACTIVE]),
                motivation_factors=preset_data.get("motivation_factors", [])
            )
            
            # 缓存结果
            await self.cache_manager.set("teaching_prep", cache_key, asdict(student_preset), 3600)
            
            return student_preset
            
        except Exception as e:
            logger.error(f"Student preset analysis error: {str(e)}")
            raise
    
    async def recommend_teaching_cases(self,
                                     subject: SubjectType,
                                     grade: str,
                                     topic: str,
                                     preferred_style: TeachingStyle,
                                     student_features: List[str]) -> List[Dict[str, Any]]:
        """优秀案例智能推荐"""
        try:
            # 获取可用案例
            available_cases = await self._get_available_cases(subject, grade, topic)
            
            if not available_cases:
                return []
            
            # 构建推荐请求
            prompt = self.prompts["case_recommendation"].format(
                subject=subject.value,
                grade=grade,
                topic=topic,
                preferred_style=preferred_style.value,
                student_features=", ".join(student_features),
                available_cases=json.dumps([self._format_case_for_ai(case) for case in available_cases[:10]], ensure_ascii=False)
            )
            
            request = AIRequest(
                provider=AIProvider.OPENAI,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位教学案例专家，擅长分析和推荐优秀的教学案例。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response = await self.ai_manager.chat_completion_with_fallback(request)
            
            if not response.success:
                raise Exception(f"AI case recommendation failed: {response.error}")
            
            # 解析推荐结果
            recommendations = self._parse_case_recommendations(response.content, available_cases)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Teaching case recommendation error: {str(e)}")
            raise
    
    async def generate_comprehensive_prep_plan(self,
                                             textbook_content: TextbookContent,
                                             teaching_style: TeachingStyle,
                                             class_duration: int) -> Dict[str, Any]:
        """生成综合备课方案"""
        try:
            # 1. 教材分析
            textbook_analysis = await self.analyze_textbook(textbook_content)
            
            # 2. 学情预设
            student_preset = await self.analyze_student_preset(
                textbook_content.grade,
                textbook_content.subject,
                textbook_content.title
            )
            
            # 3. 教学设计
            lesson_plan = await self.design_lesson_plan(
                textbook_content.content,
                textbook_content.subject,
                textbook_content.grade,
                class_duration,
                teaching_style,
                student_preset
            )
            
            # 4. 案例推荐
            recommended_cases = await self.recommend_teaching_cases(
                textbook_content.subject,
                textbook_content.grade,
                textbook_content.title,
                teaching_style,
                student_preset.learning_characteristics
            )
            
            # 5. 整合备课方案
            comprehensive_plan = {
                "plan_id": f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "textbook_info": {
                    "id": textbook_content.id,
                    "title": textbook_content.title,
                    "subject": textbook_content.subject.value,
                    "grade": textbook_content.grade,
                    "chapter": textbook_content.chapter
                },
                "textbook_analysis": textbook_analysis,
                "student_preset": asdict(student_preset),
                "lesson_plan": asdict(lesson_plan),
                "recommended_cases": recommended_cases,
                "preparation_checklist": self._generate_prep_checklist(lesson_plan),
                "risk_assessment": self._assess_teaching_risks(lesson_plan, student_preset),
                "optimization_suggestions": self._generate_optimization_suggestions(lesson_plan, textbook_analysis),
                "created_at": datetime.now().isoformat()
            }
            
            return comprehensive_plan
            
        except Exception as e:
            logger.error(f"Comprehensive prep plan generation error: {str(e)}")
            raise
    
    # 辅助方法
    def _parse_textbook_analysis(self, ai_content: str) -> Dict[str, Any]:
        """解析教材分析结果"""
        try:
            # 尝试解析JSON
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content)
            
            # 如果不是JSON，进行文本解析
            analysis = {
                "knowledge_points": [],
                "teaching_objectives": [],
                "key_points": [],
                "difficult_points": [],
                "teaching_methods": [],
                "assessment_methods": []
            }
            
            # 简单的文本解析逻辑
            lines = ai_content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if "知识点" in line or "Knowledge" in line:
                    current_section = "knowledge_points"
                elif "教学目标" in line or "Objective" in line:
                    current_section = "teaching_objectives"
                elif "重点" in line or "Key" in line:
                    current_section = "key_points"
                elif "难点" in line or "Difficult" in line:
                    current_section = "difficult_points"
                elif "教学方法" in line or "Method" in line:
                    current_section = "teaching_methods"
                elif "评价" in line or "Assessment" in line:
                    current_section = "assessment_methods"
                elif line and current_section and line.startswith(('-', '•', '1.', '2.')):
                    analysis[current_section].append(line.lstrip('-•1234567890. '))
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Failed to parse textbook analysis: {str(e)}")
            return {"raw_content": ai_content}
    
    def _parse_lesson_plan(self, ai_content: str) -> Dict[str, Any]:
        """解析教学方案"""
        try:
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content)
            
            # 文本解析逻辑
            plan = {
                "title": "教学方案",
                "objectives": [],
                "key_points": [],
                "difficult_points": [],
                "phases": [],
                "materials": [],
                "assessment": {},
                "homework": {}
            }
            
            # 解析教学环节
            phases = []
            current_phase = None
            
            lines = ai_content.split('\n')
            for line in lines:
                line = line.strip()
                if any(phase in line for phase in ["导入", "新授", "练习", "总结", "作业"]):
                    if current_phase:
                        phases.append(current_phase)
                    current_phase = {
                        "name": line,
                        "duration": 0,
                        "activities": [],
                        "objectives": []
                    }
                elif current_phase and line:
                    current_phase["activities"].append(line)
            
            if current_phase:
                phases.append(current_phase)
            
            plan["phases"] = phases
            return plan
            
        except Exception as e:
            logger.warning(f"Failed to parse lesson plan: {str(e)}")
            return {"raw_content": ai_content}
    
    def _parse_student_preset(self, ai_content: str) -> Dict[str, Any]:
        """解析学情预设"""
        try:
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content)
            
            preset = {
                "knowledge_base": {},
                "learning_characteristics": [],
                "common_difficulties": [],
                "attention_span": 30,
                "preferred_methods": [TeachingStyle.INTERACTIVE],
                "motivation_factors": []
            }
            
            # 简单文本解析
            lines = ai_content.split('\n')
            for line in lines:
                line = line.strip()
                if "特点" in line or "characteristic" in line.lower():
                    preset["learning_characteristics"].append(line)
                elif "困难" in line or "difficult" in line.lower():
                    preset["common_difficulties"].append(line)
                elif "激励" in line or "motivat" in line.lower():
                    preset["motivation_factors"].append(line)
            
            return preset
            
        except Exception as e:
            logger.warning(f"Failed to parse student preset: {str(e)}")
            return {"raw_content": ai_content}
    
    def _parse_case_recommendations(self, ai_content: str, available_cases: List[TeachingCase]) -> List[Dict[str, Any]]:
        """解析案例推荐结果"""
        recommendations = []
        
        try:
            # 简单的推荐解析逻辑
            for case in available_cases[:5]:  # 返回前5个案例
                recommendation = {
                    "case_id": case.id,
                    "title": case.title,
                    "description": case.description,
                    "teaching_style": case.teaching_style.value,
                    "effectiveness": case.effectiveness,
                    "match_score": 0.8,  # 模拟匹配分数
                    "recommendation_reason": "基于AI分析推荐",
                    "applicable_scenarios": ["常规教学", "互动教学"],
                    "adaptation_suggestions": ["可根据班级特点调整"]
                }
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.warning(f"Failed to parse case recommendations: {str(e)}")
            return []
    
    async def _extract_knowledge_points(self, textbook_content: TextbookContent) -> List[KnowledgePoint]:
        """提取知识点"""
        # 模拟知识点提取
        knowledge_points = [
            KnowledgePoint(
                id=f"kp_{textbook_content.id}_1",
                name="核心概念",
                description="本节课的核心概念",
                subject=textbook_content.subject,
                difficulty=DifficultyLevel.INTERMEDIATE
            )
        ]
        return knowledge_points
    
    def _assess_content_difficulty(self, textbook_content: TextbookContent) -> Dict[str, Any]:
        """评估内容难度"""
        return {
            "overall_difficulty": "中等",
            "complexity_factors": ["概念抽象", "逻辑关系复杂"],
            "difficulty_score": 0.6,
            "student_readiness": "需要前置知识准备"
        }
    
    def _generate_teaching_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """生成教学建议"""
        return [
            "采用循序渐进的教学方式",
            "增加互动环节提高参与度",
            "使用多媒体辅助教学",
            "设计分层练习题"
        ]
    
    def _format_student_characteristics(self, student_preset: StudentPreset) -> str:
        """格式化学生特点"""
        characteristics = [
            f"年级：{student_preset.grade}",
            f"注意力持续时间：{student_preset.attention_span}分钟",
            f"学习特点：{', '.join(student_preset.learning_characteristics)}",
            f"常见困难：{', '.join(student_preset.common_difficulties)}"
        ]
        return "\n".join(characteristics)
    
    async def _get_available_cases(self, subject: SubjectType, grade: str, topic: str) -> List[TeachingCase]:
        """获取可用案例"""
        # 模拟案例数据
        cases = [
            TeachingCase(
                id="case_001",
                title="互动式教学案例",
                subject=subject,
                grade=grade,
                topic=topic,
                teaching_style=TeachingStyle.INTERACTIVE,
                description="通过小组讨论和互动游戏进行教学",
                objectives=["提高学生参与度", "加深理解"],
                process=[],
                materials=["PPT", "小组活动卡片"],
                effectiveness=0.85,
                feedback=["学生反响良好"],
                tags=["互动", "小组合作"],
                author="张老师",
                created_at=datetime.now()
            )
        ]
        return cases
    
    def _format_case_for_ai(self, case: TeachingCase) -> Dict[str, Any]:
        """为AI格式化案例"""
        return {
            "id": case.id,
            "title": case.title,
            "teaching_style": case.teaching_style.value,
            "description": case.description,
            "effectiveness": case.effectiveness,
            "tags": case.tags
        }
    
    def _generate_prep_checklist(self, lesson_plan: TeachingPlan) -> List[str]:
        """生成备课检查清单"""
        return [
            "确认教学目标明确具体",
            "准备所需教学材料",
            "检查多媒体设备",
            "预习学生可能的问题",
            "准备课堂练习题",
            "设计课堂评价方式"
        ]
    
    def _assess_teaching_risks(self, lesson_plan: TeachingPlan, student_preset: StudentPreset) -> List[Dict[str, Any]]:
        """评估教学风险"""
        risks = [
            {
                "risk": "学生注意力不集中",
                "probability": "中等",
                "impact": "影响教学效果",
                "mitigation": "增加互动环节，控制单次讲解时间"
            },
            {
                "risk": "内容理解困难",
                "probability": "低",
                "impact": "学习目标无法达成",
                "mitigation": "提供更多例子和练习"
            }
        ]
        return risks
    
    def _generate_optimization_suggestions(self, lesson_plan: TeachingPlan, textbook_analysis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        return [
            "可以增加更多实际应用案例",
            "建议使用思维导图梳理知识结构",
            "可以设计更多层次的练习题",
            "考虑加入小组合作环节"
        ]