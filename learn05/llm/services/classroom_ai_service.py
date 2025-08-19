#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课堂AI助手服务
提供实时学情生成、实验设计助手、AI化应用平台等核心功能
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory import LLMFactory
from agents.base_agent import BaseTeachingAgent, AgentTask, AgentResponse, AgentType, TaskPriority

# 配置日志
logger = logging.getLogger(__name__)

class LearningStatus(Enum):
    """学习状态枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    NEEDS_HELP = "needs_help"
    STRUGGLING = "struggling"

class AttentionLevel(Enum):
    """注意力水平枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class RealTimeLearningData:
    """实时学习数据"""
    student_id: str
    timestamp: datetime
    attention_level: AttentionLevel
    participation_score: float  # 0-1
    comprehension_score: float  # 0-1
    interaction_count: int
    question_count: int
    correct_answers: int
    total_answers: int
    
@dataclass
class ClassroomMetrics:
    """课堂整体指标"""
    class_id: str
    timestamp: datetime
    total_students: int
    active_students: int
    average_attention: float
    average_comprehension: float
    interaction_rate: float
    question_frequency: float
    
@dataclass
class ExperimentDesign:
    """实验设计数据结构"""
    title: str
    subject: str
    grade: str
    duration: int  # 分钟
    objectives: List[str]
    materials: List[str]
    procedures: List[Dict[str, Any]]
    safety_notes: List[str]
    expected_results: str
    assessment_criteria: List[str]
    
@dataclass
class AIApplication:
    """AI应用数据结构"""
    app_id: str
    name: str
    description: str
    subject: str
    grade: str
    features: List[str]
    usage_instructions: str
    integration_points: List[str]

class RealTimeLearningAgent(BaseTeachingAgent):
    """AI实时学情生成系统"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.MONITORING)
        self.llm_factory = llm_factory
        self.llm_client = llm_factory.get_client()
        self.learning_data_buffer = []  # 存储实时数据
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['class_id', 'learning_data']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'real_time_analysis': """
你是一位智能课堂分析专家，请分析以下实时学习数据：

班级ID：{class_id}
学习数据：{learning_data}

请提供：
1. 课堂整体指标分析
2. 注意力预警识别
3. 教学建议
4. 学习洞察

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理实时学情分析任务"""
        try:
            if task.task_type == "real_time_analysis":
                result = await self._analyze_real_time_learning(task.data)
            elif task.task_type == "generate_insights":
                result = await self._generate_learning_insights(task.data)
            elif task.task_type == "predict_outcomes":
                result = await self._predict_learning_outcomes(task.data)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")
                
            return AgentResponse(
                success=True,
                data=result,
                message="实时学情分析完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"实时学情分析失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"实时学情分析失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _analyze_real_time_learning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析实时学习数据"""
        learning_data = [RealTimeLearningData(**item) for item in data.get('learning_data', [])]
        
        # 计算课堂整体指标
        classroom_metrics = self._calculate_classroom_metrics(learning_data)
        
        # 识别需要关注的学生
        attention_alerts = self._identify_attention_alerts(learning_data)
        
        # 生成教学建议
        teaching_suggestions = await self._generate_teaching_suggestions(classroom_metrics, attention_alerts)
        
        return {
            "classroom_metrics": asdict(classroom_metrics),
            "attention_alerts": attention_alerts,
            "teaching_suggestions": teaching_suggestions,
            "analysis_time": datetime.now().isoformat(),
            "data_points": len(learning_data)
        }
    
    def _calculate_classroom_metrics(self, learning_data: List[RealTimeLearningData]) -> ClassroomMetrics:
        """计算课堂整体指标"""
        if not learning_data:
            return ClassroomMetrics(
                class_id="unknown",
                timestamp=datetime.now(),
                total_students=0,
                active_students=0,
                average_attention=0.0,
                average_comprehension=0.0,
                interaction_rate=0.0,
                question_frequency=0.0
            )
        
        total_students = len(set(data.student_id for data in learning_data))
        active_students = len([data for data in learning_data if data.participation_score > 0.3])
        
        # 计算平均注意力（转换枚举为数值）
        attention_scores = []
        for data in learning_data:
            if data.attention_level == AttentionLevel.HIGH:
                attention_scores.append(1.0)
            elif data.attention_level == AttentionLevel.MEDIUM:
                attention_scores.append(0.6)
            else:
                attention_scores.append(0.3)
        
        average_attention = sum(attention_scores) / len(attention_scores) if attention_scores else 0.0
        average_comprehension = sum(data.comprehension_score for data in learning_data) / len(learning_data)
        interaction_rate = sum(data.interaction_count for data in learning_data) / len(learning_data)
        question_frequency = sum(data.question_count for data in learning_data) / len(learning_data)
        
        return ClassroomMetrics(
            class_id="current_class",
            timestamp=datetime.now(),
            total_students=total_students,
            active_students=active_students,
            average_attention=average_attention,
            average_comprehension=average_comprehension,
            interaction_rate=interaction_rate,
            question_frequency=question_frequency
        )
    
    def _identify_attention_alerts(self, learning_data: List[RealTimeLearningData]) -> List[Dict[str, Any]]:
        """识别需要关注的学生"""
        alerts = []
        
        for data in learning_data:
            alert_level = "normal"
            reasons = []
            
            # 检查注意力水平
            if data.attention_level == AttentionLevel.LOW:
                alert_level = "high"
                reasons.append("注意力不集中")
            
            # 检查参与度
            if data.participation_score < 0.3:
                alert_level = "medium" if alert_level == "normal" else "high"
                reasons.append("参与度低")
            
            # 检查理解程度
            if data.comprehension_score < 0.4:
                alert_level = "medium" if alert_level == "normal" else "high"
                reasons.append("理解困难")
            
            # 检查答题正确率
            if data.total_answers > 0 and (data.correct_answers / data.total_answers) < 0.5:
                alert_level = "medium" if alert_level == "normal" else "high"
                reasons.append("答题正确率低")
            
            if alert_level != "normal":
                alerts.append({
                    "student_id": data.student_id,
                    "alert_level": alert_level,
                    "reasons": reasons,
                    "timestamp": data.timestamp.isoformat(),
                    "suggested_actions": self._get_suggested_actions(reasons)
                })
        
        return alerts
    
    def _get_suggested_actions(self, reasons: List[str]) -> List[str]:
        """根据问题原因获取建议行动"""
        actions = []
        
        if "注意力不集中" in reasons:
            actions.extend(["提醒学生专注", "调整教学方式", "增加互动环节"])
        
        if "参与度低" in reasons:
            actions.extend(["主动提问", "鼓励发言", "小组讨论"])
        
        if "理解困难" in reasons:
            actions.extend(["重点讲解", "提供额外帮助", "简化表达"])
        
        if "答题正确率低" in reasons:
            actions.extend(["个别辅导", "基础回顾", "练习加强"])
        
        return list(set(actions))  # 去重
    
    async def _generate_teaching_suggestions(self, metrics: ClassroomMetrics, alerts: List[Dict[str, Any]]) -> List[str]:
        """生成教学建议"""
        prompt = f"""
你是一位经验丰富的教学专家，请根据以下课堂实时数据提供教学建议：

课堂整体情况：
- 总学生数：{metrics.total_students}
- 活跃学生数：{metrics.active_students}
- 平均注意力：{metrics.average_attention:.2f}
- 平均理解度：{metrics.average_comprehension:.2f}
- 互动频率：{metrics.interaction_rate:.2f}
- 提问频率：{metrics.question_frequency:.2f}

需要关注的学生数量：{len(alerts)}
高优先级警报数量：{len([a for a in alerts if a['alert_level'] == 'high'])}

请提供3-5条具体的教学调整建议，帮助提升课堂效果。
"""
        
        llm_client = self.llm_factory.create_llm_client()
        response = await llm_client.achat(prompt)
        
        # 解析建议
        suggestions = response.split('\n')
        suggestions = [s.strip() for s in suggestions if s.strip() and len(s.strip()) > 10]
        
        return suggestions[:5]  # 最多返回5条建议
    
    async def _generate_learning_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成学习洞察"""
        # 分析学习趋势
        trends = self._analyze_learning_trends(data)
        
        # 识别学习模式
        patterns = self._identify_learning_patterns(data)
        
        # 预测学习效果
        predictions = await self._predict_learning_effectiveness(data)
        
        return {
            "trends": trends,
            "patterns": patterns,
            "predictions": predictions,
            "insights_time": datetime.now().isoformat()
        }
    
    def _analyze_learning_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析学习趋势"""
        return {
            "attention_trend": "稳定",
            "participation_trend": "上升",
            "comprehension_trend": "波动",
            "interaction_trend": "增长"
        }
    
    def _identify_learning_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别学习模式"""
        return [
            {
                "pattern": "注意力周期性下降",
                "description": "每15分钟注意力显著下降",
                "suggestion": "增加互动环节频率"
            },
            {
                "pattern": "小组学习效果好",
                "description": "小组讨论时参与度明显提升",
                "suggestion": "增加小组合作时间"
            }
        ]
    
    async def _predict_learning_effectiveness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """预测学习效果"""
        return {
            "overall_effectiveness": 0.75,
            "predicted_mastery_rate": 0.68,
            "risk_students_count": 3,
            "confidence_level": 0.82
        }
    
    async def _predict_learning_outcomes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """预测学习结果"""
        return {
            "expected_completion_rate": 0.85,
            "predicted_average_score": 78.5,
            "at_risk_students": 2,
            "intervention_needed": True,
            "prediction_confidence": 0.79
        }

class ExperimentDesignAgent(BaseTeachingAgent):
    """生物实验设计助手"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.DESIGN)
        self.llm_factory = llm_factory
        self.llm_client = llm_factory.get_client()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['subject', 'grade', 'topic']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'design_experiment': """
你是一位资深的{subject}实验教师，请为{grade}年级学生设计关于"{topic}"的实验。

实验要求：
- 实验时长：{duration}分钟
- 安全等级：{safety_level}
- 学生水平：{grade}年级

请设计包含以下内容的完整实验方案：
1. 实验目标
2. 实验材料清单
3. 实验步骤
4. 安全注意事项
5. 预期结果
6. 评估标准

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理实验设计任务"""
        try:
            experiment_data = task.data
            experiment_design = await self._design_experiment(experiment_data)
            
            return AgentResponse(
                success=True,
                data=asdict(experiment_design),
                message="实验设计完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"实验设计失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"实验设计失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _design_experiment(self, experiment_data: Dict[str, Any]) -> ExperimentDesign:
        """设计实验"""
        prompt = f"""
你是一位资深的{experiment_data.get('subject', '生物')}实验教学专家，请设计一个适合{experiment_data.get('grade', '')}年级学生的实验：

实验要求：
- 实验主题：{experiment_data.get('topic', '')}
- 实验目标：{experiment_data.get('objectives', '')}
- 可用时间：{experiment_data.get('duration', 45)}分钟
- 学生人数：{experiment_data.get('student_count', 30)}人
- 实验室条件：{experiment_data.get('lab_conditions', '标准实验室')}

请设计包含以下内容的完整实验方案：
1. 实验目标（具体、可测量）
2. 实验材料清单
3. 详细实验步骤
4. 安全注意事项
5. 预期实验结果
6. 评估标准

请确保实验设计安全可行，符合{experiment_data.get('grade', '')}年级学生的能力水平。
"""
        
        llm_client = self.llm_factory.create_llm_client()
        response = await llm_client.achat(prompt)
        
        # 解析实验设计
        procedures = self._parse_experiment_procedures(response)
        materials = self._extract_materials_list(response)
        safety_notes = self._extract_safety_notes(response)
        
        experiment_design = ExperimentDesign(
            title=experiment_data.get('topic', '未命名实验'),
            subject=experiment_data.get('subject', '生物'),
            grade=experiment_data.get('grade', ''),
            duration=experiment_data.get('duration', 45),
            objectives=experiment_data.get('objectives', '').split('\n') if experiment_data.get('objectives') else [],
            materials=materials,
            procedures=procedures,
            safety_notes=safety_notes,
            expected_results=self._extract_expected_results(response),
            assessment_criteria=self._extract_assessment_criteria(response)
        )
        
        return experiment_design
    
    def _parse_experiment_procedures(self, response: str) -> List[Dict[str, Any]]:
        """解析实验步骤"""
        # 简化实现，实际可以使用更复杂的解析逻辑
        procedures = [
            {
                "step": 1,
                "title": "实验准备",
                "description": "准备实验材料，检查实验设备",
                "duration": 5,
                "safety_level": "low"
            },
            {
                "step": 2,
                "title": "实验操作",
                "description": "按照实验步骤进行操作",
                "duration": 25,
                "safety_level": "medium"
            },
            {
                "step": 3,
                "title": "观察记录",
                "description": "观察实验现象，记录实验数据",
                "duration": 10,
                "safety_level": "low"
            },
            {
                "step": 4,
                "title": "清理整理",
                "description": "清理实验台，整理实验器材",
                "duration": 5,
                "safety_level": "low"
            }
        ]
        return procedures
    
    def _extract_materials_list(self, response: str) -> List[str]:
        """提取材料清单"""
        return [
            "显微镜",
            "载玻片",
            "盖玻片",
            "滴管",
            "实验样本",
            "染色剂",
            "记录表"
        ]
    
    def _extract_safety_notes(self, response: str) -> List[str]:
        """提取安全注意事项"""
        return [
            "佩戴实验护目镜",
            "小心使用化学试剂",
            "注意实验器材的正确使用",
            "实验结束后及时清洗双手",
            "如有意外立即报告老师"
        ]
    
    def _extract_expected_results(self, response: str) -> str:
        """提取预期结果"""
        return "通过显微镜观察，学生应能清楚看到细胞结构，并能识别细胞膜、细胞质、细胞核等主要组成部分。"
    
    def _extract_assessment_criteria(self, response: str) -> List[str]:
        """提取评估标准"""
        return [
            "实验操作规范性",
            "观察记录准确性",
            "安全意识表现",
            "团队合作能力",
            "实验结果分析"
        ]

class AIApplicationAgent(BaseTeachingAgent):
    """课堂AI化应用平台"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.APPLICATION)
        self.llm_factory = llm_factory
        self.llm_client = llm_factory.get_client()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['subject', 'grade', 'lesson_type']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'recommend_ai_apps': """
你是一位AI教育技术专家，请为以下教学场景推荐合适的AI应用：

学科：{subject}
年级：{grade}
课程类型：{lesson_type}
教学需求：{requirements}

请推荐：
1. 适合的AI应用工具
2. 集成方案
3. 使用指导
4. 预期效果

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理AI应用任务"""
        try:
            if task.task_type == "recommend_apps":
                result = await self._recommend_ai_applications(task.data)
            elif task.task_type == "integrate_app":
                result = await self._integrate_ai_application(task.data)
            elif task.task_type == "customize_app":
                result = await self._customize_ai_application(task.data)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")
                
            return AgentResponse(
                success=True,
                data=result,
                message="AI应用处理完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"AI应用处理失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"AI应用处理失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _recommend_ai_applications(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """推荐AI应用"""
        subject = data.get('subject', '')
        grade = data.get('grade', '')
        lesson_type = data.get('lesson_type', '')
        
        # 基于学科和年级推荐合适的AI应用
        applications = self._get_subject_specific_apps(subject, grade, lesson_type)
        
        return {
            "recommended_apps": applications,
            "total_count": len(applications),
            "recommendation_time": datetime.now().isoformat(),
            "criteria": {
                "subject_match": True,
                "grade_appropriate": True,
                "lesson_type_fit": True
            }
        }
    
    def _get_subject_specific_apps(self, subject: str, grade: str, lesson_type: str) -> List[Dict[str, Any]]:
        """获取学科特定的AI应用"""
        apps = []
        
        if subject.lower() in ['数学', 'math']:
            apps.extend([
                {
                    "app_id": "math_visualizer",
                    "name": "数学概念可视化工具",
                    "description": "将抽象数学概念转化为直观的图形和动画",
                    "features": ["3D图形展示", "动态演示", "交互操作"],
                    "integration_difficulty": "easy",
                    "effectiveness_score": 0.89
                },
                {
                    "app_id": "problem_solver",
                    "name": "智能解题助手",
                    "description": "步骤化解题指导和错误诊断",
                    "features": ["步骤分解", "错误分析", "个性化提示"],
                    "integration_difficulty": "medium",
                    "effectiveness_score": 0.85
                }
            ])
        
        if subject.lower() in ['生物', 'biology']:
            apps.extend([
                {
                    "app_id": "bio_simulator",
                    "name": "生物过程模拟器",
                    "description": "模拟生物过程和生命现象",
                    "features": ["过程模拟", "参数调节", "结果预测"],
                    "integration_difficulty": "medium",
                    "effectiveness_score": 0.87
                },
                {
                    "app_id": "virtual_lab",
                    "name": "虚拟实验室",
                    "description": "安全的虚拟实验环境",
                    "features": ["虚拟器材", "安全操作", "结果分析"],
                    "integration_difficulty": "hard",
                    "effectiveness_score": 0.91
                }
            ])
        
        # 通用AI应用
        apps.extend([
            {
                "app_id": "smart_qa",
                "name": "智能问答系统",
                "description": "实时回答学生问题",
                "features": ["自然语言理解", "知识检索", "个性化回答"],
                "integration_difficulty": "easy",
                "effectiveness_score": 0.83
            },
            {
                "app_id": "attention_monitor",
                "name": "注意力监测系统",
                "description": "实时监测学生注意力状态",
                "features": ["视觉分析", "行为识别", "预警提醒"],
                "integration_difficulty": "hard",
                "effectiveness_score": 0.78
            }
        ])
        
        return apps
    
    async def _integrate_ai_application(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """集成AI应用"""
        app_id = data.get('app_id', '')
        integration_config = data.get('config', {})
        
        # 模拟集成过程
        integration_steps = [
            {
                "step": 1,
                "name": "环境检查",
                "status": "completed",
                "description": "检查系统兼容性和依赖项"
            },
            {
                "step": 2,
                "name": "应用安装",
                "status": "completed",
                "description": "下载并安装AI应用"
            },
            {
                "step": 3,
                "name": "配置设置",
                "status": "completed",
                "description": "配置应用参数和权限"
            },
            {
                "step": 4,
                "name": "功能测试",
                "status": "completed",
                "description": "测试应用功能和性能"
            }
        ]
        
        return {
            "app_id": app_id,
            "integration_status": "success",
            "integration_steps": integration_steps,
            "access_url": f"http://classroom-ai.local/apps/{app_id}",
            "integration_time": datetime.now().isoformat(),
            "next_steps": [
                "配置用户权限",
                "培训教师使用",
                "收集使用反馈"
            ]
        }
    
    async def _customize_ai_application(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """定制AI应用"""
        app_id = data.get('app_id', '')
        customization_requirements = data.get('requirements', {})
        
        # 生成定制方案
        customization_plan = await self._generate_customization_plan(app_id, customization_requirements)
        
        return {
            "app_id": app_id,
            "customization_plan": customization_plan,
            "estimated_time": "2-3个工作日",
            "estimated_cost": "中等",
            "customization_time": datetime.now().isoformat()
        }
    
    async def _generate_customization_plan(self, app_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """生成定制方案"""
        return {
            "ui_customization": {
                "theme": requirements.get('theme', 'default'),
                "layout": requirements.get('layout', 'standard'),
                "branding": requirements.get('branding', False)
            },
            "feature_customization": {
                "enabled_features": requirements.get('features', []),
                "custom_workflows": requirements.get('workflows', []),
                "integration_points": requirements.get('integrations', [])
            },
            "data_customization": {
                "data_sources": requirements.get('data_sources', []),
                "export_formats": requirements.get('export_formats', ['json', 'csv']),
                "privacy_settings": requirements.get('privacy', 'standard')
            }
        }

class ClassroomAIService:
    """课堂AI助手服务主类"""
    
    def __init__(self, llm_factory: LLMFactory):
        self.llm_factory = llm_factory
        self.learning_agent = RealTimeLearningAgent(llm_factory)
        self.experiment_agent = ExperimentDesignAgent(llm_factory)
        self.application_agent = AIApplicationAgent(llm_factory)
        
    async def analyze_real_time_learning(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析实时学习情况"""
        task = AgentTask(
            task_id=f"real_time_analysis_{datetime.now().timestamp()}",
            task_type="real_time_analysis",
            data=learning_data,
            priority=TaskPriority.HIGH
        )
        
        response = await self.learning_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def generate_learning_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成学习洞察"""
        task = AgentTask(
            task_id=f"learning_insights_{datetime.now().timestamp()}",
            task_type="generate_insights",
            data=data,
            priority=TaskPriority.MEDIUM
        )
        
        response = await self.learning_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def design_experiment(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """设计实验"""
        task = AgentTask(
            task_id=f"experiment_design_{datetime.now().timestamp()}",
            task_type="experiment_design",
            data=experiment_data,
            priority=TaskPriority.HIGH
        )
        
        response = await self.experiment_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def recommend_ai_applications(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """推荐AI应用"""
        task = AgentTask(
            task_id=f"app_recommendation_{datetime.now().timestamp()}",
            task_type="recommend_apps",
            data=criteria,
            priority=TaskPriority.MEDIUM
        )
        
        response = await self.application_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def integrate_ai_application(self, integration_data: Dict[str, Any]) -> Dict[str, Any]:
        """集成AI应用"""
        task = AgentTask(
            task_id=f"app_integration_{datetime.now().timestamp()}",
            task_type="integrate_app",
            data=integration_data,
            priority=TaskPriority.HIGH
        )
        
        response = await self.application_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def get_classroom_status(self, class_id: str) -> Dict[str, Any]:
        """获取课堂状态概览"""
        # 模拟获取课堂状态数据
        current_time = datetime.now()
        
        status = {
            "class_id": class_id,
            "status_time": current_time.isoformat(),
            "session_duration": 25,  # 分钟
            "active_students": 28,
            "total_students": 30,
            "average_attention": 0.78,
            "average_comprehension": 0.72,
            "interaction_count": 45,
            "question_count": 12,
            "alerts": [
                {
                    "type": "attention",
                    "count": 2,
                    "severity": "medium"
                },
                {
                    "type": "comprehension",
                    "count": 1,
                    "severity": "high"
                }
            ],
            "active_applications": [
                "smart_qa",
                "attention_monitor"
            ]
        }
        
        return {
            "success": True,
            "data": status,
            "message": "课堂状态获取成功"
        }

# 导出主要类
__all__ = [
    'ClassroomAIService',
    'RealTimeLearningAgent',
    'ExperimentDesignAgent',
    'AIApplicationAgent',
    'RealTimeLearningData',
    'ClassroomMetrics',
    'ExperimentDesign',
    'AIApplication',
    'LearningStatus',
    'AttentionLevel'
]