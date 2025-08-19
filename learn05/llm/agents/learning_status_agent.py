# -*- coding: utf-8 -*-
"""
学情分析智能体模块
提供学生学习情况分析、成绩趋势分析、薄弱环节识别等功能
"""

import json
import logging
import statistics
from typing import Dict, List, Optional, Any
from .base_agent import BaseTeachingAgent, AgentType, AgentTask, AgentResponse

logger = logging.getLogger(__name__)


class LearningStatusAgent(BaseTeachingAgent):
    """学情分析智能体"""
    
    def __init__(self, llm_client=None, config: Optional[Dict] = None):
        super().__init__(AgentType.LEARNING_STATUS, llm_client, config)
        
        # 学情分析专用配置
        self.analysis_config = {
            "min_grade_records": 3,        # 最少成绩记录数
            "trend_analysis_period": 6,    # 趋势分析周期（月）
            "weakness_threshold": 0.6,     # 薄弱环节阈值
            "improvement_threshold": 0.1,  # 进步阈值
            "analysis_dimensions": [       # 分析维度
                "overall_performance",     # 整体表现
                "subject_performance",     # 学科表现
                "knowledge_mastery",       # 知识掌握
                "learning_trend",          # 学习趋势
                "weakness_analysis"        # 薄弱分析
            ]
        }
        
        self.analysis_config.update(config.get("analysis_config", {}) if config else {})
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证学情分析输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            bool: 验证是否通过
        """
        required_fields = ["student_id"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in input_data:
                logger.error(f"缺少必需字段: {field}")
                return False
        
        # 检查成绩数据
        grades = input_data.get("grades", [])
        if len(grades) < self.analysis_config["min_grade_records"]:
            logger.warning(f"成绩记录数量不足: {len(grades)} < {self.analysis_config['min_grade_records']}")
        
        return True
    
    def get_prompt_template(self, task_type: str) -> str:
        """
        获取学情分析提示词模板
        
        Args:
            task_type: 任务类型
            
        Returns:
            str: 提示词模板
        """
        templates = {
            "comprehensive_analysis": """
你是一位专业的教育数据分析师和学习顾问。请基于以下学生数据进行全面的学情分析：

学生信息：
- 学生ID：{student_id}
- 姓名：{student_name}
- 年级：{grade}
- 班级：{class_name}

成绩数据：
{grades_data}

学习行为数据：
{learning_behavior}

请进行以下分析：

1. **整体学习表现评估**：
   - 总体成绩水平（优秀/良好/中等/待提高）
   - 与班级平均水平对比
   - 与年级平均水平对比
   - 学习稳定性评价

2. **学科表现分析**：
   - 各学科成绩分布
   - 优势学科识别
   - 薄弱学科识别
   - 学科间平衡性分析

3. **学习趋势分析**：
   - 成绩变化趋势（上升/下降/稳定）
   - 进步最明显的学科
   - 退步需要关注的学科
   - 学习动力和积极性评估

4. **知识掌握情况**：
   - 各知识点掌握程度
   - 基础知识掌握情况
   - 综合应用能力评估
   - 学习方法有效性分析

5. **问题诊断与建议**：
   - 主要学习问题识别
   - 问题产生原因分析
   - 针对性改进建议
   - 学习策略优化方案

请以JSON格式返回分析结果，包含以下字段：
- overall_assessment: 整体评估
- subject_analysis: 学科分析
- learning_trend: 学习趋势
- knowledge_mastery: 知识掌握
- recommendations: 改进建议
""",
            
            "weakness_analysis": """
你是一位经验丰富的学习诊断专家。请分析学生的薄弱环节：

学生成绩数据：
{grades_data}

知识点掌握情况：
{knowledge_points}

请分析：

1. **薄弱环节识别**：
   - 成绩较低的学科/知识点
   - 错误率较高的题型
   - 理解困难的概念

2. **薄弱原因分析**：
   - 基础知识不牢固
   - 学习方法不当
   - 练习量不足
   - 理解能力限制

3. **改进策略**：
   - 基础知识补强计划
   - 学习方法调整建议
   - 练习重点和方向
   - 辅导资源推荐

请以JSON格式返回分析结果。
""",
            
            "progress_tracking": """
你是一位学习进度跟踪专家。请分析学生的学习进步情况：

历史成绩数据：
{historical_grades}

最近成绩数据：
{recent_grades}

分析时间段：{analysis_period}

请分析：

1. **进步情况评估**：
   - 整体进步幅度
   - 各学科进步情况
   - 进步速度评估

2. **进步原因分析**：
   - 有效的学习策略
   - 努力程度提升
   - 外部帮助效果

3. **持续改进建议**：
   - 保持优势的方法
   - 进一步提升的方向
   - 潜在风险预警

请以JSON格式返回分析结果。
"""
        }
        
        return templates.get(task_type, templates["comprehensive_analysis"])
    
    def process_task(self, task: AgentTask) -> AgentResponse:
        """
        处理学情分析任务
        
        Args:
            task: 分析任务
            
        Returns:
            AgentResponse: 分析结果
        """
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            if task_type == "comprehensive_analysis":
                return self._comprehensive_analysis(input_data)
            elif task_type == "weakness_analysis":
                return self._analyze_weakness(input_data)
            elif task_type == "progress_tracking":
                return self._track_progress(input_data)
            else:
                return AgentResponse(
                    success=False,
                    message=f"不支持的任务类型: {task_type}",
                    error_code="UNSUPPORTED_TASK_TYPE"
                )
                
        except Exception as e:
            logger.error(f"学情分析任务处理失败: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"任务处理失败: {str(e)}",
                error_code="PROCESSING_ERROR"
            )
    
    def _comprehensive_analysis(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        综合学情分析
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 分析结果
        """
        student_id = input_data["student_id"]
        student_name = input_data.get("student_name", "未知")
        grade = input_data.get("grade", "未知")
        class_name = input_data.get("class_name", "未知")
        grades = input_data.get("grades", [])
        learning_behavior = input_data.get("learning_behavior", {})
        
        # 预处理成绩数据
        grades_data = self._format_grades_data(grades)
        learning_behavior_text = self._format_learning_behavior(learning_behavior)
        
        # 获取提示词模板
        template = self.get_prompt_template("comprehensive_analysis")
        
        # 格式化提示词
        prompt = self._format_prompt(
            template,
            student_id=student_id,
            student_name=student_name,
            grade=grade,
            class_name=class_name,
            grades_data=grades_data,
            learning_behavior=learning_behavior_text
        )
        
        # 调用大模型
        response_text = self._call_llm(prompt)
        
        # 解析响应
        try:
            analysis_result = self._parse_json_response(response_text)
            
            # 添加统计数据
            statistics_data = self._calculate_statistics(grades)
            
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "comprehensive_analysis",
                    "student_info": {
                        "student_id": student_id,
                        "student_name": student_name,
                        "grade": grade,
                        "class_name": class_name
                    },
                    "statistics": statistics_data,
                    "analysis_result": analysis_result
                },
                message="综合学情分析完成"
            )
            
        except Exception as e:
            logger.error(f"分析结果解析失败: {str(e)}")
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "comprehensive_analysis",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="分析完成，但结果格式需要手动处理"
            )
    
    def _analyze_weakness(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        薄弱环节分析
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 分析结果
        """
        grades = input_data.get("grades", [])
        knowledge_points = input_data.get("knowledge_points", [])
        
        grades_data = self._format_grades_data(grades)
        knowledge_points_text = self._format_knowledge_points(knowledge_points)
        
        template = self.get_prompt_template("weakness_analysis")
        prompt = self._format_prompt(
            template,
            grades_data=grades_data,
            knowledge_points=knowledge_points_text
        )
        
        response_text = self._call_llm(prompt)
        
        try:
            weakness_analysis = self._parse_json_response(response_text)
            
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "weakness_analysis",
                    "weakness_analysis": weakness_analysis
                },
                message="薄弱环节分析完成"
            )
            
        except Exception as e:
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "weakness_analysis",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="薄弱环节分析完成，格式需要手动处理"
            )
    
    def _track_progress(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        学习进度跟踪
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 跟踪结果
        """
        historical_grades = input_data.get("historical_grades", [])
        recent_grades = input_data.get("recent_grades", [])
        analysis_period = input_data.get("analysis_period", "最近3个月")
        
        historical_data = self._format_grades_data(historical_grades)
        recent_data = self._format_grades_data(recent_grades)
        
        template = self.get_prompt_template("progress_tracking")
        prompt = self._format_prompt(
            template,
            historical_grades=historical_data,
            recent_grades=recent_data,
            analysis_period=analysis_period
        )
        
        response_text = self._call_llm(prompt)
        
        try:
            progress_analysis = self._parse_json_response(response_text)
            
            # 计算进步统计
            progress_stats = self._calculate_progress_statistics(
                historical_grades, recent_grades
            )
            
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "progress_tracking",
                    "progress_statistics": progress_stats,
                    "progress_analysis": progress_analysis
                },
                message="学习进度跟踪完成"
            )
            
        except Exception as e:
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "progress_tracking",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="进度跟踪完成，格式需要手动处理"
            )
    
    def _format_grades_data(self, grades: List[Dict]) -> str:
        """
        格式化成绩数据为文本
        
        Args:
            grades: 成绩列表
            
        Returns:
            str: 格式化的成绩数据
        """
        if not grades:
            return "暂无成绩数据"
        
        formatted_data = []
        for grade in grades:
            exam_name = grade.get("exam_name", "未知考试")
            subject = grade.get("subject", "未知科目")
            score = grade.get("score", 0)
            total_score = grade.get("total_score", 100)
            exam_date = grade.get("exam_date", "未知日期")
            
            formatted_data.append(
                f"- {exam_date} {exam_name} {subject}: {score}/{total_score} ({score/total_score*100:.1f}%)"
            )
        
        return "\n".join(formatted_data)
    
    def _format_learning_behavior(self, behavior: Dict) -> str:
        """
        格式化学习行为数据
        
        Args:
            behavior: 学习行为数据
            
        Returns:
            str: 格式化的学习行为数据
        """
        if not behavior:
            return "暂无学习行为数据"
        
        formatted_data = []
        for key, value in behavior.items():
            formatted_data.append(f"- {key}: {value}")
        
        return "\n".join(formatted_data)
    
    def _format_knowledge_points(self, knowledge_points: List[Dict]) -> str:
        """
        格式化知识点数据
        
        Args:
            knowledge_points: 知识点列表
            
        Returns:
            str: 格式化的知识点数据
        """
        if not knowledge_points:
            return "暂无知识点数据"
        
        formatted_data = []
        for kp in knowledge_points:
            name = kp.get("name", "未知知识点")
            mastery = kp.get("mastery_level", 0)
            formatted_data.append(f"- {name}: 掌握程度 {mastery}/10")
        
        return "\n".join(formatted_data)
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析JSON响应
        
        Args:
            response_text: 响应文本
            
        Returns:
            Dict[str, Any]: 解析后的数据
        """
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text.strip()
        
        return json.loads(json_text)
    
    def _calculate_statistics(self, grades: List[Dict]) -> Dict[str, Any]:
        """
        计算成绩统计数据
        
        Args:
            grades: 成绩列表
            
        Returns:
            Dict[str, Any]: 统计数据
        """
        if not grades:
            return {}
        
        scores = []
        subjects = {}
        
        for grade in grades:
            score = grade.get("score", 0)
            total_score = grade.get("total_score", 100)
            subject = grade.get("subject", "未知")
            
            percentage = score / total_score * 100 if total_score > 0 else 0
            scores.append(percentage)
            
            if subject not in subjects:
                subjects[subject] = []
            subjects[subject].append(percentage)
        
        stats = {
            "total_exams": len(grades),
            "average_score": statistics.mean(scores) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "score_std": statistics.stdev(scores) if len(scores) > 1 else 0,
            "subject_averages": {}
        }
        
        for subject, subject_scores in subjects.items():
            stats["subject_averages"][subject] = {
                "average": statistics.mean(subject_scores),
                "count": len(subject_scores)
            }
        
        return stats
    
    def _calculate_progress_statistics(self, historical: List[Dict], 
                                     recent: List[Dict]) -> Dict[str, Any]:
        """
        计算进步统计数据
        
        Args:
            historical: 历史成绩
            recent: 最近成绩
            
        Returns:
            Dict[str, Any]: 进步统计
        """
        if not historical or not recent:
            return {}
        
        hist_avg = statistics.mean([g.get("score", 0) / g.get("total_score", 100) * 100 
                                   for g in historical])
        recent_avg = statistics.mean([g.get("score", 0) / g.get("total_score", 100) * 100 
                                     for g in recent])
        
        improvement = recent_avg - hist_avg
        improvement_rate = improvement / hist_avg * 100 if hist_avg > 0 else 0
        
        return {
            "historical_average": hist_avg,
            "recent_average": recent_avg,
            "improvement_points": improvement,
            "improvement_rate": improvement_rate,
            "trend": "上升" if improvement > 0 else "下降" if improvement < 0 else "稳定"
        }
    
    def analyze_student_learning(self, student_id: str, grades: List[Dict], 
                               student_info: Dict = None) -> Dict[str, Any]:
        """
        分析学生学习情况的便捷方法
        
        Args:
            student_id: 学生ID
            grades: 成绩列表
            student_info: 学生信息
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        input_data = {
            "student_id": student_id,
            "grades": grades
        }
        
        if student_info:
            input_data.update(student_info)
        
        response = self.execute_task("comprehensive_analysis", input_data)
        return response.data if response.success else {"error": response.message}