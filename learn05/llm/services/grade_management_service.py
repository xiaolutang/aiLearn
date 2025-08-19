#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成绩管理AI服务
提供智能录入、综合分析、个性化指导、辅导方案生成等核心功能
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from enum import Enum
import statistics
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory import LLMFactory
from agents.base_agent import BaseTeachingAgent, AgentTask, AgentResponse, AgentType, TaskPriority

# 配置日志
logger = logging.getLogger(__name__)

class GradeLevel(Enum):
    """成绩等级枚举"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"           # 良好
    AVERAGE = "average"     # 中等
    BELOW_AVERAGE = "below_average"  # 偏下
    POOR = "poor"           # 较差

class SubjectType(Enum):
    """学科类型枚举"""
    MATH = "math"
    CHINESE = "chinese"
    ENGLISH = "english"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    POLITICS = "politics"

@dataclass
class StudentGrade:
    """学生成绩数据结构"""
    student_id: str
    student_name: str
    subject: str
    score: float
    max_score: float
    exam_type: str  # 考试类型：quiz, midterm, final, homework
    exam_date: datetime
    grade_level: GradeLevel = None
    percentile: float = None
    
    def __post_init__(self):
        if self.grade_level is None:
            self.grade_level = self._calculate_grade_level()
    
    def _calculate_grade_level(self) -> GradeLevel:
        """计算成绩等级"""
        percentage = (self.score / self.max_score) * 100
        if percentage >= 90:
            return GradeLevel.EXCELLENT
        elif percentage >= 80:
            return GradeLevel.GOOD
        elif percentage >= 70:
            return GradeLevel.AVERAGE
        elif percentage >= 60:
            return GradeLevel.BELOW_AVERAGE
        else:
            return GradeLevel.POOR

@dataclass
class GradeAnalysis:
    """成绩分析结果"""
    student_id: str
    subject: str
    analysis_period: str
    overall_performance: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    strength_areas: List[str]
    weakness_areas: List[str]
    improvement_suggestions: List[str]
    predicted_performance: Dict[str, Any]
    
@dataclass
class TutoringPlan:
    """辅导方案数据结构"""
    student_id: str
    subject: str
    plan_id: str
    objectives: List[str]
    focus_areas: List[str]
    study_schedule: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    assessment_methods: List[str]
    expected_outcomes: Dict[str, Any]
    duration_weeks: int
    created_date: datetime

class GradeInputAgent(BaseTeachingAgent):
    """高效成绩录入系统"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.DATA_PROCESSING)
        self.llm_factory = llm_factory
        self.llm_client = llm_factory.get_client()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if 'batch_data' in input_data:
            return 'grades' in input_data['batch_data']
        elif 'image_data' in input_data:
            return 'image_content' in input_data['image_data']
        return False
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'batch_input': """
你是一位成绩录入专家，请处理以下批量成绩数据：

成绩数据：{grades}

请进行：
1. 数据验证
2. 格式标准化
3. 异常值检测
4. 统计分析

请以结构化的方式回答。
""",
            'smart_recognition': """
你是一位智能识别专家，请从以下图像或文本中识别成绩信息：

输入内容：{content}

请提取：
1. 学生姓名
2. 科目成绩
3. 考试信息
4. 其他相关数据

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理成绩录入任务"""
        try:
            if task.task_type == "batch_input":
                result = await self._process_batch_input(task.data)
            elif task.task_type == "smart_recognition":
                result = await self._smart_grade_recognition(task.data)
            elif task.task_type == "validate_grades":
                result = await self._validate_grade_data(task.data)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")
                
            return AgentResponse(
                success=True,
                data=result,
                message="成绩录入处理完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"成绩录入处理失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"成绩录入处理失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _process_batch_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """批量成绩录入处理"""
        grade_data = data.get('grades', [])
        processed_grades = []
        errors = []
        
        for i, grade_info in enumerate(grade_data):
            try:
                # 验证和标准化成绩数据
                validated_grade = self._validate_single_grade(grade_info)
                processed_grades.append(validated_grade)
            except Exception as e:
                errors.append({
                    "row": i + 1,
                    "error": str(e),
                    "data": grade_info
                })
        
        # 计算统计信息
        statistics_info = self._calculate_batch_statistics(processed_grades)
        
        return {
            "processed_count": len(processed_grades),
            "error_count": len(errors),
            "processed_grades": processed_grades,
            "errors": errors,
            "statistics": statistics_info,
            "processing_time": datetime.now().isoformat()
        }
    
    def _validate_single_grade(self, grade_info: Dict[str, Any]) -> Dict[str, Any]:
        """验证单个成绩数据"""
        required_fields = ['student_id', 'student_name', 'subject', 'score', 'max_score']
        
        # 检查必填字段
        for field in required_fields:
            if field not in grade_info or grade_info[field] is None:
                raise ValueError(f"缺少必填字段: {field}")
        
        # 验证分数范围
        score = float(grade_info['score'])
        max_score = float(grade_info['max_score'])
        
        if score < 0 or score > max_score:
            raise ValueError(f"分数超出有效范围: {score}/{max_score}")
        
        # 标准化数据
        validated_grade = {
            'student_id': str(grade_info['student_id']),
            'student_name': str(grade_info['student_name']).strip(),
            'subject': str(grade_info['subject']).strip(),
            'score': score,
            'max_score': max_score,
            'exam_type': grade_info.get('exam_type', 'quiz'),
            'exam_date': grade_info.get('exam_date', datetime.now().isoformat()),
            'percentage': round((score / max_score) * 100, 2)
        }
        
        return validated_grade
    
    def _calculate_batch_statistics(self, grades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算批量成绩统计信息"""
        if not grades:
            return {}
        
        scores = [grade['score'] for grade in grades]
        percentages = [grade['percentage'] for grade in grades]
        
        return {
            "total_students": len(grades),
            "average_score": round(statistics.mean(scores), 2),
            "median_score": round(statistics.median(scores), 2),
            "max_score": max(scores),
            "min_score": min(scores),
            "average_percentage": round(statistics.mean(percentages), 2),
            "pass_rate": len([p for p in percentages if p >= 60]) / len(percentages),
            "excellent_rate": len([p for p in percentages if p >= 90]) / len(percentages),
            "score_distribution": self._calculate_score_distribution(percentages)
        }
    
    def _calculate_score_distribution(self, percentages: List[float]) -> Dict[str, int]:
        """计算分数分布"""
        distribution = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "0-59": 0
        }
        
        for percentage in percentages:
            if percentage >= 90:
                distribution["90-100"] += 1
            elif percentage >= 80:
                distribution["80-89"] += 1
            elif percentage >= 70:
                distribution["70-79"] += 1
            elif percentage >= 60:
                distribution["60-69"] += 1
            else:
                distribution["0-59"] += 1
        
        return distribution
    
    async def _smart_grade_recognition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """智能成绩识别（OCR/图像识别）"""
        # 模拟OCR识别结果
        image_path = data.get('image_path', '')
        recognition_type = data.get('type', 'handwritten')  # handwritten, printed, table
        
        # 这里应该集成实际的OCR服务
        recognized_data = {
            "recognition_confidence": 0.92,
            "recognized_grades": [
                {
                    "student_name": "张三",
                    "student_id": "2023001",
                    "subject": "数学",
                    "score": 85,
                    "max_score": 100,
                    "confidence": 0.95
                },
                {
                    "student_name": "李四",
                    "student_id": "2023002",
                    "subject": "数学",
                    "score": 78,
                    "max_score": 100,
                    "confidence": 0.88
                }
            ],
            "uncertain_items": [
                {
                    "student_name": "王五",
                    "issue": "分数模糊不清",
                    "suggested_score": 82,
                    "confidence": 0.65
                }
            ]
        }
        
        return recognized_data
    
    async def _validate_grade_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证成绩数据"""
        grades = data.get('grades', [])
        validation_rules = data.get('rules', {})
        
        validation_results = {
            "valid_count": 0,
            "invalid_count": 0,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        for grade in grades:
            try:
                self._validate_single_grade(grade)
                validation_results["valid_count"] += 1
                
                # 检查异常值
                if self._is_outlier(grade, grades):
                    validation_results["warnings"].append({
                        "student_id": grade.get('student_id'),
                        "type": "outlier",
                        "message": "成绩可能为异常值，请核实"
                    })
                    
            except Exception as e:
                validation_results["invalid_count"] += 1
                validation_results["errors"].append({
                    "student_id": grade.get('student_id'),
                    "error": str(e)
                })
        
        return validation_results
    
    def _is_outlier(self, grade: Dict[str, Any], all_grades: List[Dict[str, Any]]) -> bool:
        """检查是否为异常值"""
        scores = [g['score'] for g in all_grades if g.get('subject') == grade.get('subject')]
        if len(scores) < 3:
            return False
        
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores)
        
        # 使用3σ原则检测异常值
        return abs(grade['score'] - mean_score) > 3 * std_score

class GradeAnalysisAgent(BaseTeachingAgent):
    """综合分析平台"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.ANALYSIS)
        self.llm_factory = llm_factory
        self.llm_client = llm_factory.get_client()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['grades']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'comprehensive_analysis': """
你是一位资深的教育数据分析专家，请对以下成绩数据进行综合分析：

成绩数据：{grades}
分析类型：{analysis_type}

请提供：
1. 基础统计分析
2. 学科表现分析
3. 学生排名分析
4. AI洞察建议
5. 趋势分析
6. 对比分析

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理成绩分析任务"""
        try:
            if task.task_type == "comprehensive_analysis":
                result = await self._comprehensive_grade_analysis(task.data)
            elif task.task_type == "trend_analysis":
                result = await self._trend_analysis(task.data)
            elif task.task_type == "comparative_analysis":
                result = await self._comparative_analysis(task.data)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")
                
            return AgentResponse(
                success=True,
                data=result,
                message="成绩分析完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"成绩分析失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"成绩分析失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _comprehensive_grade_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """综合成绩分析"""
        student_grades = data.get('grades', [])
        analysis_period = data.get('period', '本学期')
        
        # 基础统计分析
        basic_stats = self._calculate_basic_statistics(student_grades)
        
        # 学科表现分析
        subject_analysis = self._analyze_subject_performance(student_grades)
        
        # 学生排名分析
        ranking_analysis = self._calculate_student_rankings(student_grades)
        
        # 生成AI洞察
        ai_insights = await self._generate_ai_insights(basic_stats, subject_analysis)
        
        return {
            "analysis_period": analysis_period,
            "basic_statistics": basic_stats,
            "subject_analysis": subject_analysis,
            "ranking_analysis": ranking_analysis,
            "ai_insights": ai_insights,
            "analysis_time": datetime.now().isoformat()
        }
    
    def _calculate_basic_statistics(self, grades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算基础统计信息"""
        if not grades:
            return {}
        
        # 按学科分组
        subject_grades = {}
        for grade in grades:
            subject = grade.get('subject', '未知')
            if subject not in subject_grades:
                subject_grades[subject] = []
            subject_grades[subject].append(grade['score'])
        
        # 计算各学科统计
        subject_stats = {}
        for subject, scores in subject_grades.items():
            subject_stats[subject] = {
                "count": len(scores),
                "average": round(statistics.mean(scores), 2),
                "median": round(statistics.median(scores), 2),
                "max": max(scores),
                "min": min(scores),
                "std_dev": round(statistics.stdev(scores) if len(scores) > 1 else 0, 2)
            }
        
        # 整体统计
        all_scores = [grade['score'] for grade in grades]
        overall_stats = {
            "total_records": len(grades),
            "average_score": round(statistics.mean(all_scores), 2),
            "median_score": round(statistics.median(all_scores), 2),
            "score_range": max(all_scores) - min(all_scores),
            "std_deviation": round(statistics.stdev(all_scores) if len(all_scores) > 1 else 0, 2)
        }
        
        return {
            "overall": overall_stats,
            "by_subject": subject_stats
        }
    
    def _analyze_subject_performance(self, grades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析学科表现"""
        subject_performance = {}
        
        # 按学科分组分析
        subjects = set(grade.get('subject', '未知') for grade in grades)
        
        for subject in subjects:
            subject_grades = [g for g in grades if g.get('subject') == subject]
            scores = [g['score'] for g in subject_grades]
            
            if scores:
                avg_score = statistics.mean(scores)
                performance_level = self._get_performance_level(avg_score)
                
                subject_performance[subject] = {
                    "average_score": round(avg_score, 2),
                    "performance_level": performance_level,
                    "student_count": len(subject_grades),
                    "pass_rate": len([s for s in scores if s >= 60]) / len(scores),
                    "excellent_rate": len([s for s in scores if s >= 90]) / len(scores),
                    "improvement_needed": avg_score < 70
                }
        
        return subject_performance
    
    def _get_performance_level(self, score: float) -> str:
        """获取表现等级"""
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "中等"
        elif score >= 60:
            return "及格"
        else:
            return "不及格"
    
    def _calculate_student_rankings(self, grades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算学生排名"""
        # 按学生分组计算平均分
        student_averages = {}
        for grade in grades:
            student_id = grade.get('student_id')
            if student_id not in student_averages:
                student_averages[student_id] = {
                    'name': grade.get('student_name', ''),
                    'scores': [],
                    'subjects': set()
                }
            student_averages[student_id]['scores'].append(grade['score'])
            student_averages[student_id]['subjects'].add(grade.get('subject', ''))
        
        # 计算平均分和排名
        rankings = []
        for student_id, data in student_averages.items():
            avg_score = statistics.mean(data['scores'])
            rankings.append({
                'student_id': student_id,
                'student_name': data['name'],
                'average_score': round(avg_score, 2),
                'subject_count': len(data['subjects']),
                'total_exams': len(data['scores'])
            })
        
        # 按平均分排序
        rankings.sort(key=lambda x: x['average_score'], reverse=True)
        
        # 添加排名
        for i, student in enumerate(rankings):
            student['rank'] = i + 1
        
        return {
            "rankings": rankings[:10],  # 返回前10名
            "total_students": len(rankings)
        }
    
    async def _generate_ai_insights(self, basic_stats: Dict[str, Any], subject_analysis: Dict[str, Any]) -> List[str]:
        """生成AI洞察"""
        prompt = f"""
你是一位资深的教育数据分析专家，请根据以下成绩数据提供深入的分析洞察：

整体统计：
- 平均分：{basic_stats.get('overall', {}).get('average_score', 0)}
- 中位数：{basic_stats.get('overall', {}).get('median_score', 0)}
- 标准差：{basic_stats.get('overall', {}).get('std_deviation', 0)}

学科表现：
{json.dumps(subject_analysis, ensure_ascii=False, indent=2)}

请提供以下方面的洞察：
1. 整体学习状况评估
2. 学科间差异分析
3. 潜在问题识别
4. 改进建议
5. 关注重点

请提供具体、可操作的分析结果。
"""
        
        llm_client = self.llm_factory.create_llm_client()
        response = await llm_client.achat(prompt)
        
        # 解析洞察
        insights = response.split('\n')
        insights = [insight.strip() for insight in insights if insight.strip() and len(insight.strip()) > 10]
        
        return insights[:8]  # 返回最多8条洞察
    
    async def _trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """趋势分析"""
        historical_grades = data.get('historical_grades', [])
        time_period = data.get('time_period', 'monthly')
        
        # 按时间分组
        time_groups = self._group_by_time(historical_grades, time_period)
        
        # 计算趋势
        trends = self._calculate_trends(time_groups)
        
        return {
            "time_period": time_period,
            "trend_data": time_groups,
            "trend_analysis": trends,
            "analysis_time": datetime.now().isoformat()
        }
    
    def _group_by_time(self, grades: List[Dict[str, Any]], period: str) -> Dict[str, Any]:
        """按时间分组"""
        # 简化实现，实际应根据period参数进行不同的分组
        time_groups = {}
        
        for grade in grades:
            # 假设有exam_date字段
            exam_date = grade.get('exam_date', datetime.now().isoformat())
            if isinstance(exam_date, str):
                exam_date = datetime.fromisoformat(exam_date.replace('Z', '+00:00'))
            
            if period == 'monthly':
                key = exam_date.strftime('%Y-%m')
            elif period == 'weekly':
                key = exam_date.strftime('%Y-W%U')
            else:  # daily
                key = exam_date.strftime('%Y-%m-%d')
            
            if key not in time_groups:
                time_groups[key] = []
            time_groups[key].append(grade)
        
        return time_groups
    
    def _calculate_trends(self, time_groups: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """计算趋势"""
        trend_data = []
        
        for time_key, grades in sorted(time_groups.items()):
            scores = [g['score'] for g in grades]
            if scores:
                trend_data.append({
                    "period": time_key,
                    "average_score": round(statistics.mean(scores), 2),
                    "student_count": len(set(g.get('student_id') for g in grades)),
                    "exam_count": len(grades)
                })
        
        # 计算趋势方向
        if len(trend_data) >= 2:
            recent_avg = trend_data[-1]['average_score']
            previous_avg = trend_data[-2]['average_score']
            trend_direction = "上升" if recent_avg > previous_avg else "下降" if recent_avg < previous_avg else "稳定"
        else:
            trend_direction = "数据不足"
        
        return {
            "trend_direction": trend_direction,
            "trend_data": trend_data,
            "data_points": len(trend_data)
        }
    
    async def _comparative_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """对比分析"""
        current_grades = data.get('current_grades', [])
        comparison_grades = data.get('comparison_grades', [])
        comparison_type = data.get('type', 'period')  # period, class, school
        
        # 计算对比统计
        current_stats = self._calculate_basic_statistics(current_grades)
        comparison_stats = self._calculate_basic_statistics(comparison_grades)
        
        # 生成对比结果
        comparison_result = self._generate_comparison_result(current_stats, comparison_stats, comparison_type)
        
        return {
            "comparison_type": comparison_type,
            "current_period": current_stats,
            "comparison_period": comparison_stats,
            "comparison_result": comparison_result,
            "analysis_time": datetime.now().isoformat()
        }
    
    def _generate_comparison_result(self, current: Dict[str, Any], comparison: Dict[str, Any], comp_type: str) -> Dict[str, Any]:
        """生成对比结果"""
        current_avg = current.get('overall', {}).get('average_score', 0)
        comparison_avg = comparison.get('overall', {}).get('average_score', 0)
        
        difference = current_avg - comparison_avg
        improvement = difference > 0
        
        return {
            "average_score_difference": round(difference, 2),
            "improvement": improvement,
            "improvement_percentage": round((difference / comparison_avg * 100) if comparison_avg > 0 else 0, 2),
            "summary": f"相比{comp_type}，平均分{'提高' if improvement else '下降'}了{abs(difference):.2f}分"
        }

class PersonalizedGuidanceAgent(BaseTeachingAgent):
    """个性化指导系统"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.GUIDANCE)
        self.llm_factory = llm_factory
        self.llm_client = llm_factory.get_client()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['student_id', 'performance_data']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'generate_guidance': """
你是一位资深的个性化教育专家，请为以下学生生成个性化指导方案：

学生ID：{student_id}
学习表现：{performance_data}
学习特点：{learning_characteristics}

请提供：
1. 学习优势分析
2. 薄弱环节识别
3. 个性化学习建议
4. 学习方法指导
5. 目标设定建议
6. 家长配合建议

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理个性化指导任务"""
        try:
            if task.task_type == "generate_guidance":
                result = await self._generate_personalized_guidance(task.data)
            elif task.task_type == "create_study_plan":
                result = await self._create_study_plan(task.data)
            elif task.task_type == "recommend_resources":
                result = await self._recommend_learning_resources(task.data)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")
                
            return AgentResponse(
                success=True,
                data=result,
                message="个性化指导生成完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"个性化指导生成失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"个性化指导生成失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _generate_personalized_guidance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成个性化指导"""
        student_profile = data.get('student_profile', {})
        grade_analysis = data.get('grade_analysis', {})
        learning_preferences = data.get('learning_preferences', {})
        
        prompt = f"""
你是一位经验丰富的个性化教育专家，请为以下学生制定个性化学习指导方案：

学生信息：
- 学生ID：{student_profile.get('student_id', '')}
- 年级：{student_profile.get('grade', '')}
- 学习风格：{learning_preferences.get('learning_style', '视觉型')}
- 兴趣爱好：{learning_preferences.get('interests', [])}

成绩分析：
- 平均分：{grade_analysis.get('average_score', 0)}
- 优势学科：{grade_analysis.get('strength_subjects', [])}
- 薄弱学科：{grade_analysis.get('weakness_subjects', [])}
- 学习趋势：{grade_analysis.get('trend', '稳定')}

请提供以下方面的个性化指导：
1. 学习目标设定
2. 学习方法建议
3. 时间管理策略
4. 薄弱环节改进
5. 优势发挥建议
6. 学习资源推荐

请确保建议具体、可操作，符合学生的个性特点。
"""
        
        llm_client = self.llm_factory.create_llm_client()
        response = await llm_client.achat(prompt)
        
        # 解析指导建议
        guidance_sections = self._parse_guidance_response(response)
        
        return {
            "student_id": student_profile.get('student_id', ''),
            "guidance_sections": guidance_sections,
            "priority_actions": self._extract_priority_actions(guidance_sections),
            "follow_up_schedule": self._generate_follow_up_schedule(),
            "guidance_date": datetime.now().isoformat()
        }
    
    def _parse_guidance_response(self, response: str) -> Dict[str, List[str]]:
        """解析指导建议响应"""
        sections = {
            "学习目标": [],
            "学习方法": [],
            "时间管理": [],
            "薄弱改进": [],
            "优势发挥": [],
            "资源推荐": []
        }
        
        # 简化解析，实际可以使用更复杂的NLP技术
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in sections.keys()):
                for section in sections.keys():
                    if section in line:
                        current_section = section
                        break
            elif line and current_section and len(line) > 5:
                sections[current_section].append(line)
        
        return sections
    
    def _extract_priority_actions(self, guidance_sections: Dict[str, List[str]]) -> List[str]:
        """提取优先行动项"""
        priority_actions = []
        
        # 从各个部分提取关键行动项
        for section, items in guidance_sections.items():
            if items:
                priority_actions.append(f"{section}: {items[0]}")
        
        return priority_actions[:5]  # 最多5个优先行动项
    
    def _generate_follow_up_schedule(self) -> List[Dict[str, Any]]:
        """生成跟进计划"""
        base_date = datetime.now()
        schedule = []
        
        # 一周后第一次跟进
        schedule.append({
            "date": (base_date + timedelta(weeks=1)).isoformat(),
            "type": "progress_check",
            "description": "检查学习计划执行情况"
        })
        
        # 两周后第二次跟进
        schedule.append({
            "date": (base_date + timedelta(weeks=2)).isoformat(),
            "type": "adjustment",
            "description": "根据进展调整学习策略"
        })
        
        # 一个月后评估
        schedule.append({
            "date": (base_date + timedelta(weeks=4)).isoformat(),
            "type": "evaluation",
            "description": "全面评估指导效果"
        })
        
        return schedule
    
    async def _create_study_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建学习计划"""
        student_info = data.get('student_info', {})
        subjects = data.get('subjects', [])
        time_available = data.get('time_available', 2)  # 每天可用小时数
        
        # 生成学习计划
        study_plan = {
            "student_id": student_info.get('student_id', ''),
            "plan_duration": "4周",
            "daily_study_time": time_available,
            "weekly_schedule": self._generate_weekly_schedule(subjects, time_available),
            "subject_allocation": self._allocate_study_time(subjects),
            "milestones": self._create_study_milestones(),
            "created_date": datetime.now().isoformat()
        }
        
        return study_plan
    
    def _generate_weekly_schedule(self, subjects: List[str], daily_hours: int) -> Dict[str, List[Dict[str, Any]]]:
        """生成周学习计划"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule = {}
        
        for day in days:
            schedule[day] = []
            if day in ['Saturday', 'Sunday']:
                # 周末安排复习和练习
                schedule[day].append({
                    "time": "09:00-11:00",
                    "activity": "复习本周内容",
                    "subject": "综合"
                })
            else:
                # 工作日安排具体学科学习
                for i, subject in enumerate(subjects[:2]):  # 每天最多2个学科
                    start_hour = 19 + i
                    schedule[day].append({
                        "time": f"{start_hour:02d}:00-{start_hour+1:02d}:00",
                        "activity": "概念学习和练习",
                        "subject": subject
                    })
        
        return schedule
    
    def _allocate_study_time(self, subjects: List[str]) -> Dict[str, float]:
        """分配学习时间"""
        if not subjects:
            return {}
        
        # 简单平均分配，实际应根据学生成绩和难度调整
        time_per_subject = 1.0 / len(subjects)
        
        allocation = {}
        for subject in subjects:
            allocation[subject] = round(time_per_subject, 2)
        
        return allocation
    
    def _create_study_milestones(self) -> List[Dict[str, Any]]:
        """创建学习里程碑"""
        base_date = datetime.now()
        milestones = []
        
        # 第一周里程碑
        milestones.append({
            "week": 1,
            "date": (base_date + timedelta(weeks=1)).isoformat(),
            "goal": "完成基础概念学习",
            "success_criteria": "理解核心概念，完成基础练习"
        })
        
        # 第二周里程碑
        milestones.append({
            "week": 2,
            "date": (base_date + timedelta(weeks=2)).isoformat(),
            "goal": "强化练习和应用",
            "success_criteria": "能够独立解决中等难度问题"
        })
        
        # 第三周里程碑
        milestones.append({
            "week": 3,
            "date": (base_date + timedelta(weeks=3)).isoformat(),
            "goal": "综合运用和提升",
            "success_criteria": "掌握综合应用技能"
        })
        
        # 第四周里程碑
        milestones.append({
            "week": 4,
            "date": (base_date + timedelta(weeks=4)).isoformat(),
            "goal": "总结评估和巩固",
            "success_criteria": "达到预期学习目标"
        })
        
        return milestones
    
    async def _recommend_learning_resources(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """推荐学习资源"""
        student_profile = data.get('student_profile', {})
        subject = data.get('subject', '')
        difficulty_level = data.get('difficulty_level', 'medium')
        
        # 基于学生特点推荐资源
        resources = self._get_subject_resources(subject, difficulty_level, student_profile)
        
        return {
            "subject": subject,
            "difficulty_level": difficulty_level,
            "recommended_resources": resources,
            "recommendation_time": datetime.now().isoformat()
        }
    
    def _get_subject_resources(self, subject: str, difficulty: str, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取学科资源"""
        resources = []
        
        # 基础资源
        resources.extend([
            {
                "type": "video",
                "title": f"{subject}基础概念讲解",
                "description": "系统讲解基础概念和原理",
                "duration": "30分钟",
                "difficulty": "basic",
                "url": f"https://education.example.com/{subject}/basic"
            },
            {
                "type": "practice",
                "title": f"{subject}练习题库",
                "description": "分层次的练习题目",
                "question_count": 100,
                "difficulty": difficulty,
                "url": f"https://practice.example.com/{subject}/{difficulty}"
            }
        ])
        
        # 根据学习风格推荐
        learning_style = profile.get('learning_style', 'visual')
        if learning_style == 'visual':
            resources.append({
                "type": "interactive",
                "title": f"{subject}可视化工具",
                "description": "交互式图形化学习工具",
                "features": ["3D展示", "动画演示", "交互操作"],
                "url": f"https://visual.example.com/{subject}"
            })
        elif learning_style == 'auditory':
            resources.append({
                "type": "audio",
                "title": f"{subject}音频课程",
                "description": "专业老师音频讲解",
                "duration": "45分钟",
                "url": f"https://audio.example.com/{subject}"
            })
        
        return resources

class TutoringPlanAgent(BaseTeachingAgent):
    """辅导方案生成器"""
    
    def __init__(self, llm_factory: LLMFactory):
        super().__init__(AgentType.PLANNING)
        self.llm_factory = llm_factory
        self.llm_client = llm_factory.get_client()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ['student_id', 'weak_subjects']
        return all(field in input_data for field in required_fields)
    
    def get_prompt_template(self, task_type: str) -> str:
        """获取提示词模板"""
        templates = {
            'generate_plan': """
你是一位资深的教学辅导专家，请为以下学生制定个性化辅导方案：

学生ID：{student_id}
薄弱科目：{weak_subjects}
学习目标：{learning_goals}
时间安排：{time_schedule}

请制定：
1. 辅导目标设定
2. 学习计划安排
3. 重点知识梳理
4. 练习题推荐
5. 进度跟踪方案
6. 效果评估标准

请以结构化的方式回答。
"""
        }
        return templates.get(task_type, "")
        
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """处理辅导方案生成任务"""
        try:
            tutoring_plan = await self._generate_tutoring_plan(task.data)
            
            return AgentResponse(
                success=True,
                data=asdict(tutoring_plan),
                message="辅导方案生成完成",
                agent_type=self.agent_type
            )
        except Exception as e:
            logger.error(f"辅导方案生成失败: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                message=f"辅导方案生成失败: {str(e)}",
                agent_type=self.agent_type
            )
    
    async def _generate_tutoring_plan(self, data: Dict[str, Any]) -> TutoringPlan:
        """生成辅导方案"""
        student_info = data.get('student_info', {})
        subject = data.get('subject', '')
        current_level = data.get('current_level', 'beginner')
        target_level = data.get('target_level', 'intermediate')
        available_time = data.get('available_time', 2)  # 每周小时数
        
        prompt = f"""
你是一位专业的教育辅导专家，请为以下学生制定详细的辅导方案：

学生信息：
- 学生ID：{student_info.get('student_id', '')}
- 当前水平：{current_level}
- 目标水平：{target_level}
- 学科：{subject}
- 可用时间：每周{available_time}小时

请制定包含以下内容的辅导方案：
1. 具体学习目标（SMART原则）
2. 重点关注领域
3. 详细学习计划（按周安排）
4. 学习资源和材料
5. 评估方法和标准
6. 预期学习成果

请确保方案具体可行，符合学生的实际情况。
"""
        
        llm_client = self.llm_factory.create_llm_client()
        response = await llm_client.achat(prompt)
        
        # 解析响应并构建辅导方案
        objectives = self._extract_objectives(response)
        focus_areas = self._extract_focus_areas(response)
        study_schedule = self._create_study_schedule(available_time)
        resources = self._compile_resources(subject, current_level)
        
        tutoring_plan = TutoringPlan(
            student_id=student_info.get('student_id', ''),
            subject=subject,
            plan_id=f"plan_{datetime.now().timestamp()}",
            objectives=objectives,
            focus_areas=focus_areas,
            study_schedule=study_schedule,
            resources=resources,
            assessment_methods=self._define_assessment_methods(),
            expected_outcomes=self._define_expected_outcomes(current_level, target_level),
            duration_weeks=8,  # 默认8周计划
            created_date=datetime.now()
        )
        
        return tutoring_plan
    
    def _extract_objectives(self, response: str) -> List[str]:
        """提取学习目标"""
        # 简化实现
        return [
            "掌握基础概念和原理",
            "提高问题解决能力",
            "增强学习自信心",
            "培养良好学习习惯"
        ]
    
    def _extract_focus_areas(self, response: str) -> List[str]:
        """提取重点关注领域"""
        return [
            "基础知识巩固",
            "解题技巧训练",
            "错题分析改进",
            "学习方法优化"
        ]
    
    def _create_study_schedule(self, weekly_hours: int) -> List[Dict[str, Any]]:
        """创建学习计划"""
        schedule = []
        
        for week in range(1, 9):  # 8周计划
            if week <= 2:
                focus = "基础概念学习"
            elif week <= 4:
                focus = "技能训练和练习"
            elif week <= 6:
                focus = "综合应用和提升"
            else:
                focus = "总结复习和评估"
            
            schedule.append({
                "week": week,
                "focus": focus,
                "hours": weekly_hours,
                "activities": [
                    "概念学习",
                    "练习训练",
                    "答疑解惑",
                    "进度评估"
                ]
            })
        
        return schedule
    
    def _compile_resources(self, subject: str, level: str) -> List[Dict[str, Any]]:
        """编制学习资源"""
        return [
            {
                "type": "textbook",
                "name": f"{subject}基础教材",
                "description": "系统性教材",
                "priority": "high"
            },
            {
                "type": "workbook",
                "name": f"{subject}练习册",
                "description": "配套练习",
                "priority": "high"
            },
            {
                "type": "online",
                "name": "在线学习平台",
                "description": "互动学习资源",
                "priority": "medium"
            },
            {
                "type": "assessment",
                "name": "测评工具",
                "description": "学习效果评估",
                "priority": "medium"
            }
        ]
    
    def _define_assessment_methods(self) -> List[str]:
        """定义评估方法"""
        return [
            "周测验",
            "作业完成质量",
            "课堂参与度",
            "学习进度跟踪",
            "阶段性测试"
        ]
    
    def _define_expected_outcomes(self, current_level: str, target_level: str) -> Dict[str, Any]:
        """定义预期成果"""
        return {
            "score_improvement": "提升15-20分",
            "skill_development": "掌握核心技能",
            "confidence_boost": "增强学习信心",
            "habit_formation": "养成良好学习习惯",
            "success_rate": "85%以上"
        }

class GradeManagementService:
    """成绩管理AI服务主类"""
    
    def __init__(self, llm_factory: LLMFactory):
        self.llm_factory = llm_factory
        self.input_agent = GradeInputAgent(llm_factory)
        self.analysis_agent = GradeAnalysisAgent(llm_factory)
        self.guidance_agent = PersonalizedGuidanceAgent(llm_factory)
        self.tutoring_agent = TutoringPlanAgent(llm_factory)
        
    async def process_batch_grades(self, grade_data: Dict[str, Any]) -> Dict[str, Any]:
        """批量处理成绩"""
        task = AgentTask(
            task_id=f"batch_input_{datetime.now().timestamp()}",
            task_type="batch_input",
            data=grade_data,
            priority=TaskPriority.HIGH
        )
        
        response = await self.input_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def analyze_grades(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析成绩"""
        task = AgentTask(
            task_id=f"grade_analysis_{datetime.now().timestamp()}",
            task_type="comprehensive_analysis",
            data=analysis_data,
            priority=TaskPriority.HIGH
        )
        
        response = await self.analysis_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def generate_personalized_guidance(self, guidance_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成个性化指导"""
        task = AgentTask(
            task_id=f"guidance_{datetime.now().timestamp()}",
            task_type="generate_guidance",
            data=guidance_data,
            priority=TaskPriority.MEDIUM
        )
        
        response = await self.guidance_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def create_tutoring_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建辅导方案"""
        task = AgentTask(
            task_id=f"tutoring_plan_{datetime.now().timestamp()}",
            task_type="tutoring_plan",
            data=plan_data,
            priority=TaskPriority.HIGH
        )
        
        response = await self.tutoring_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def smart_grade_recognition(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """智能成绩识别"""
        task = AgentTask(
            task_id=f"ocr_recognition_{datetime.now().timestamp()}",
            task_type="smart_recognition",
            data=image_data,
            priority=TaskPriority.MEDIUM
        )
        
        response = await self.input_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }
    
    async def get_grade_trends(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取成绩趋势"""
        task = AgentTask(
            task_id=f"trend_analysis_{datetime.now().timestamp()}",
            task_type="trend_analysis",
            data=trend_data,
            priority=TaskPriority.MEDIUM
        )
        
        response = await self.analysis_agent.process_task(task)
        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }

# 导出主要类
__all__ = [
    'GradeManagementService',
    'GradeInputAgent',
    'GradeAnalysisAgent',
    'PersonalizedGuidanceAgent',
    'TutoringPlanAgent',
    'StudentGrade',
    'GradeAnalysis',
    'TutoringPlan',
    'GradeLevel',
    'SubjectType'
]