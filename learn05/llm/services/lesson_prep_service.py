#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备课助手AI服务
提供教材分析、环节策划、学情预设、案例推荐等核心功能
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory import LLMFactory
from agents.base_agent import BaseTeachingAgent, AgentTask, AgentResponse, AgentType, TaskPriority

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class TeachingMaterial:
    """教学材料数据结构"""
    content: str
    subject: str
    grade: str
    chapter: str
    keywords: List[str] = None
    difficulty_level: str = "medium"
    
@dataclass
class LessonPlan:
    """课程计划数据结构"""
    title: str
    subject: str
    grade: str
    duration: int  # 分钟
    objectives: List[str]
    activities: List[Dict[str, Any]]
    materials: List[str]
    assessment: Dict[str, Any]
    
@dataclass
class StudentProfile:
    """学生画像数据结构"""
    grade: str
    subject_performance: Dict[str, float]  # 学科成绩
    learning_style: str  # 学习风格
    attention_span: int  # 注意力持续时间(分钟)
    interests: List[str]  # 兴趣爱好
    difficulties: List[str]  # 学习困难点

class MaterialAnalysisAgent(BaseTeachingAgent):
    """教材智能分析引擎"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.ANALYSIS)
        self.llm_factory = llm_factory
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['content', 'subject', 'grade']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'analyze_material': """
你是一位资深的{subject}教师，请分析以下{grade}年级的教学材料：

教材内容：{content}

请从以下几个方面进行分析：
1. 核心知识点
2. 学习难点
3. 教学目标
4. 前置知识要求
5. 教学建议
6. 评估方式
7. 拓展资源

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理教材分析任务"""
        try:
            material = TeachingMaterial(**task.data)
            analysis_result = await self._analyze_material(material)
            
            return AgentResponse(
                success=True,
                data=analysis_result,
                message="教材分析完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"教材分析失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"教材分析失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _analyze_material(self, material: TeachingMaterial) -> Dict[str, Any]:
        """分析教材内容"""
        prompt = f"""
你是一位资深的{material.subject}教师，请对以下教材内容进行深度分析：

教材信息：
- 学科：{material.subject}
- 年级：{material.grade}
- 章节：{material.chapter}
- 难度：{material.difficulty_level}

教材内容：
{material.content}

请从以下维度进行分析，并以JSON格式返回：
1. 知识点提取（knowledge_points）：列出主要知识点
2. 重难点分析（key_difficulties）：识别重点和难点
3. 教学目标建议（teaching_objectives）：建议的教学目标
4. 先修知识（prerequisites）：需要的先修知识
5. 教学建议（teaching_suggestions）：教学方法建议
6. 评估要点（assessment_points）：评估重点
7. 拓展资源（extension_resources）：相关拓展资源建议

请确保分析结果具体、实用，符合{material.grade}年级学生的认知水平。
"""
        
        llm_client = self.llm_factory.create_llm_client()
        response = await llm_client.achat(prompt)
        
        try:
            # 尝试解析JSON响应
            analysis_data = json.loads(response)
        except json.JSONDecodeError:
            # 如果不是JSON格式，进行文本解析
            analysis_data = {
                "knowledge_points": self._extract_knowledge_points(response),
                "key_difficulties": self._extract_difficulties(response),
                "teaching_objectives": self._extract_objectives(response),
                "prerequisites": self._extract_prerequisites(response),
                "teaching_suggestions": self._extract_suggestions(response),
                "assessment_points": self._extract_assessment(response),
                "extension_resources": self._extract_resources(response)
            }
        
        # 添加元数据
        analysis_data.update({
            "material_info": asdict(material),
            "analysis_time": datetime.now().isoformat(),
            "confidence_score": 0.85  # 可以后续优化为动态计算
        })
        
        return analysis_data
    
    def _extract_knowledge_points(self, text: str) -> List[str]:
        """从文本中提取知识点"""
        # 简化实现，实际可以使用更复杂的NLP技术
        lines = text.split('\n')
        knowledge_points = []
        for line in lines:
            if '知识点' in line or '要点' in line:
                knowledge_points.append(line.strip())
        return knowledge_points[:5]  # 限制数量
    
    def _extract_difficulties(self, text: str) -> List[str]:
        """提取重难点"""
        lines = text.split('\n')
        difficulties = []
        for line in lines:
            if '难点' in line or '重点' in line:
                difficulties.append(line.strip())
        return difficulties[:3]
    
    def _extract_objectives(self, text: str) -> List[str]:
        """提取教学目标"""
        lines = text.split('\n')
        objectives = []
        for line in lines:
            if '目标' in line or '掌握' in line:
                objectives.append(line.strip())
        return objectives[:4]
    
    def _extract_prerequisites(self, text: str) -> List[str]:
        """提取先修知识"""
        return ["基础数学概念", "逻辑思维能力"]  # 简化实现
    
    def _extract_suggestions(self, text: str) -> List[str]:
        """提取教学建议"""
        return ["采用启发式教学", "结合实际案例", "小组讨论"]  # 简化实现
    
    def _extract_assessment(self, text: str) -> List[str]:
        """提取评估要点"""
        return ["概念理解", "应用能力", "问题解决"]  # 简化实现
    
    def _extract_resources(self, text: str) -> List[str]:
        """提取拓展资源"""
        return ["相关视频资料", "练习题库", "参考书籍"]  # 简化实现

class LessonPlanningAgent(BaseTeachingAgent):
    """教学环节策划系统"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.PLANNING)
        self.llm_factory = llm_factory
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['subject', 'grade', 'topic']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'create_lesson_plan': """
你是一位经验丰富的{subject}教师，请为{grade}年级学生设计关于"{topic}"的课程计划。

课程要求：
- 课程时长：{duration}分钟
- 学生水平：{grade}年级
- 教学目标：{objectives}

请设计包含以下内容的完整课程计划：
1. 教学目标
2. 教学活动安排
3. 所需教学材料
4. 评估方式
5. 时间分配

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理课程策划任务"""
        try:
            planning_data = task.data
            lesson_plan = await self._create_lesson_plan(planning_data)
            
            return AgentResponse(
                success=True,
                data=asdict(lesson_plan),
                message="课程策划完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"课程策划失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"课程策划失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _create_lesson_plan(self, planning_data: Dict[str, Any]) -> LessonPlan:
        """创建课程计划"""
        prompt = f"""
你是一位经验丰富的教学设计专家，请根据以下信息设计一份详细的课程计划：

课程信息：
- 学科：{planning_data.get('subject', '')}
- 年级：{planning_data.get('grade', '')}
- 课程主题：{planning_data.get('topic', '')}
- 课程时长：{planning_data.get('duration', 45)}分钟
- 学生人数：{planning_data.get('student_count', 30)}人

教学目标：
{planning_data.get('objectives', '')}

请设计包含以下环节的课程计划：
1. 导入环节（5-10分钟）
2. 新知讲授（15-20分钟）
3. 练习巩固（10-15分钟）
4. 总结提升（5分钟）

每个环节请包含：
- 活动名称
- 时间分配
- 教学方法
- 学生活动
- 教师指导要点
- 所需材料

请以结构化的方式组织课程计划，确保符合{planning_data.get('grade', '')}年级学生的认知特点。
"""
        
        llm_client = self.llm_factory.create_llm_client()
        response = await llm_client.achat(prompt)
        
        # 解析响应并构建LessonPlan对象
        activities = self._parse_activities(response)
        
        lesson_plan = LessonPlan(
            title=planning_data.get('topic', '未命名课程'),
            subject=planning_data.get('subject', ''),
            grade=planning_data.get('grade', ''),
            duration=planning_data.get('duration', 45),
            objectives=planning_data.get('objectives', '').split('\n') if planning_data.get('objectives') else [],
            activities=activities,
            materials=self._extract_materials(response),
            assessment={
                "formative": ["课堂观察", "提问互动"],
                "summative": ["课后练习", "小测验"]
            }
        )
        
        return lesson_plan
    
    def _parse_activities(self, response: str) -> List[Dict[str, Any]]:
        """解析教学活动"""
        # 简化实现，实际可以使用更复杂的解析逻辑
        activities = [
            {
                "name": "课程导入",
                "duration": 8,
                "method": "问题导入",
                "student_activity": "思考讨论",
                "teacher_guidance": "引导思考",
                "materials": ["PPT", "问题卡片"]
            },
            {
                "name": "新知讲授",
                "duration": 20,
                "method": "讲解演示",
                "student_activity": "听讲记录",
                "teacher_guidance": "重点强调",
                "materials": ["教材", "多媒体"]
            },
            {
                "name": "练习巩固",
                "duration": 12,
                "method": "小组合作",
                "student_activity": "合作练习",
                "teacher_guidance": "巡视指导",
                "materials": ["练习册", "学具"]
            },
            {
                "name": "总结提升",
                "duration": 5,
                "method": "师生总结",
                "student_activity": "回顾反思",
                "teacher_guidance": "归纳总结",
                "materials": ["板书"]
            }
        ]
        return activities
    
    def _extract_materials(self, response: str) -> List[str]:
        """提取所需材料"""
        return ["教材", "PPT课件", "练习册", "多媒体设备", "学具"]

class StudentAnalysisAgent(BaseTeachingAgent):
    """学情预设分析平台"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.ANALYSIS)
        self.llm_factory = llm_factory
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['grade', 'subject']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'analyze_students': """
你是一位资深的教育专家，请分析以下学生的学习情况：

学科：{subject}
年级：{grade}
学生数据：{student_data}

请从以下方面进行分析：
1. 整体学习水平评估
2. 能力分组建议
3. 知识掌握情况
4. 预测学习困难点
5. 教学策略建议
6. 个性化指导方案

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理学情分析任务"""
        try:
            student_data = task.data
            analysis_result = await self._analyze_student_situation(student_data)
            
            return AgentResponse(
                success=True,
                data=analysis_result,
                message="学情分析完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"学情分析失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"学情分析失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _analyze_student_situation(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析学生学情"""
        prompt = f"""
你是一位资深的教育心理学专家，请根据以下学生信息进行学情分析：

班级信息：
- 年级：{student_data.get('grade', '')}
- 班级人数：{student_data.get('class_size', 30)}
- 学科：{student_data.get('subject', '')}

学生表现数据：
- 平均成绩：{student_data.get('average_score', 75)}
- 成绩分布：{student_data.get('score_distribution', {})}
- 学习兴趣度：{student_data.get('interest_level', 'medium')}
- 课堂参与度：{student_data.get('participation', 'medium')}

请从以下维度进行分析：
1. 整体学情评估
2. 学习能力分层
3. 知识掌握情况
4. 学习困难预测
5. 教学策略建议
6. 个性化指导方案

请提供具体、可操作的分析结果和建议。
"""
        
        llm_client = self.llm_factory.create_llm_client()
        response = await llm_client.achat(prompt)
        
        # 构建分析结果
        analysis_result = {
            "overall_assessment": self._extract_overall_assessment(response),
            "ability_grouping": self._generate_ability_grouping(student_data),
            "knowledge_mastery": self._analyze_knowledge_mastery(student_data),
            "difficulty_prediction": self._predict_difficulties(student_data),
            "teaching_strategies": self._suggest_teaching_strategies(response),
            "personalized_guidance": self._generate_personalized_guidance(student_data),
            "analysis_time": datetime.now().isoformat()
        }
        
        return analysis_result
    
    def _extract_overall_assessment(self, response: str) -> Dict[str, Any]:
        """提取整体评估"""
        return {
            "level": "中等",
            "strengths": ["基础扎实", "学习积极性较高"],
            "weaknesses": ["理解能力有待提升", "应用能力不足"],
            "recommendations": ["加强基础训练", "增加实践应用"]
        }
    
    def _generate_ability_grouping(self, student_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """生成能力分层"""
        return {
            "advanced": ["优秀学生群体", "可承担更多挑战"],
            "intermediate": ["中等学生群体", "需要适度引导"],
            "basic": ["基础学生群体", "需要重点关注"]
        }
    
    def _analyze_knowledge_mastery(self, student_data: Dict[str, Any]) -> Dict[str, float]:
        """分析知识掌握情况"""
        return {
            "基础概念": 0.8,
            "应用技能": 0.6,
            "综合分析": 0.5,
            "创新思维": 0.4
        }
    
    def _predict_difficulties(self, student_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """预测学习困难"""
        return [
            {
                "difficulty": "抽象概念理解",
                "probability": 0.7,
                "solution": "增加具体实例"
            },
            {
                "difficulty": "知识迁移应用",
                "probability": 0.6,
                "solution": "加强练习"
            }
        ]
    
    def _suggest_teaching_strategies(self, response: str) -> List[str]:
        """建议教学策略"""
        return [
            "分层教学",
            "小组合作学习",
            "多媒体辅助教学",
            "及时反馈评价"
        ]
    
    def _generate_personalized_guidance(self, student_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """生成个性化指导"""
        return {
            "优秀学生": ["提供拓展资源", "承担小组长角色"],
            "中等学生": ["加强基础训练", "提供学习方法指导"],
            "学困学生": ["一对一辅导", "降低学习难度"]
        }

class LessonPrepService:
    """备课助手服务主类"""
    
    def __init__(self, llm_factory: LLMFactory):
        self.llm_factory = llm_factory
        self.material_agent = MaterialAnalysisAgent(llm_factory)
        self.planning_agent = LessonPlanningAgent(llm_factory)
        self.student_agent = StudentAnalysisAgent(llm_factory)
        
    async def analyze_teaching_material(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析教学材料"""
        task = AgentTask(
            task_id=f"material_analysis_{datetime.now().timestamp()}",
            task_type="material_analysis",
            data=material_data,
            priority=TaskPriority.HIGH
        )
        
        response = await self.material_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def create_lesson_plan(self, planning_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建课程计划"""
        task = AgentTask(
            task_id=f"lesson_planning_{datetime.now().timestamp()}",
            task_type="lesson_planning",
            data=planning_data,
            priority=TaskPriority.HIGH
        )
        
        response = await self.planning_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def analyze_student_situation(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析学生学情"""
        task = AgentTask(
            task_id=f"student_analysis_{datetime.now().timestamp()}",
            task_type="student_analysis",
            data=student_data,
            priority=TaskPriority.MEDIUM
        )
        
        response = await self.student_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def get_case_recommendations(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取优秀案例推荐"""
        # 这里可以集成案例推荐系统
        # 暂时返回模拟数据
        recommendations = [
            {
                "title": "创新教学案例：数学概念可视化",
                "subject": query_data.get('subject', ''),
                "grade": query_data.get('grade', ''),
                "description": "通过图形化方式帮助学生理解抽象数学概念",
                "rating": 4.8,
                "usage_count": 156,
                "tags": ["可视化", "互动", "创新"]
            },
            {
                "title": "小组合作学习最佳实践",
                "subject": query_data.get('subject', ''),
                "grade": query_data.get('grade', ''),
                "description": "有效的小组合作学习组织方法和评价策略",
                "rating": 4.6,
                "usage_count": 203,
                "tags": ["合作学习", "评价", "管理"]
            }
        ]
        
        return {
            "success": True,
            "data": {
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "query_time": datetime.now().isoformat()
            },
            "message": "案例推荐获取成功"
        }

# 导出主要类
__all__ = [
    'LessonPrepService',
    'MaterialAnalysisAgent',
    'LessonPlanningAgent', 
    'StudentAnalysisAgent',
    'TeachingMaterial',
    'LessonPlan',
    'StudentProfile'
]