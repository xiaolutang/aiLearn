# -*- coding: utf-8 -*-
"""
课堂AI助手智能体模块
提供实时学情分析、课堂互动内容生成、教学建议等功能
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from .base_agent import BaseTeachingAgent, AgentType, AgentTask, AgentResponse

logger = logging.getLogger(__name__)


class ClassroomAIAgent(BaseTeachingAgent):
    """课堂AI助手智能体"""
    
    def __init__(self, llm_client=None, config: Optional[Dict] = None):
        super().__init__(AgentType.CLASSROOM_AI, llm_client, config)
        
        # 课堂AI助手专用配置
        self.classroom_config = {
            "interaction_types": [          # 互动类型
                "问答互动", "小组讨论", "实验演示", "游戏化学习"
            ],
            "difficulty_adaptation": {      # 难度自适应
                "easy_threshold": 0.8,     # 简单阈值
                "hard_threshold": 0.4,     # 困难阈值
                "adaptation_speed": 0.1    # 适应速度
            },
            "engagement_indicators": [      # 参与度指标
                "回答正确率", "提问频率", "互动积极性", "注意力集中度"
            ],
            "teaching_strategies": [        # 教学策略
                "讲授式", "启发式", "讨论式", "实践式", "游戏式"
            ],
            "real_time_analysis": {         # 实时分析配置
                "analysis_interval": 30,   # 分析间隔（秒）
                "min_data_points": 5,      # 最少数据点
                "confidence_threshold": 0.7 # 置信度阈值
            }
        }
        
        self.classroom_config.update(config.get("classroom_config", {}) if config else {})
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证课堂AI助手输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            bool: 验证是否通过
        """
        required_fields = ["class_id"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in input_data:
                logger.error(f"缺少必需字段: {field}")
                return False
        
        # 检查课堂数据
        classroom_data = input_data.get("classroom_data", {})
        if not classroom_data:
            logger.warning("缺少课堂数据，将使用默认分析模式")
        
        return True
    
    def get_prompt_template(self, task_type: str) -> str:
        """
        获取课堂AI助手提示词模板
        
        Args:
            task_type: 任务类型
            
        Returns:
            str: 提示词模板
        """
        templates = {
            "real_time_analysis": """
你是一位专业的课堂教学分析师和AI助手。请基于实时课堂数据进行学情分析：

课堂基本信息：
- 班级ID：{class_id}
- 课程：{subject}
- 章节：{chapter}
- 授课时间：{class_time}
- 学生人数：{student_count}

实时课堂数据：
{classroom_data}

学生互动数据：
{interaction_data}

当前教学内容：
{teaching_content}

请进行以下实时分析：

1. **整体课堂状态评估**：
   - 学生参与度水平（高/中/低）
   - 理解程度评估
   - 注意力集中情况
   - 课堂氛围评价

2. **个体学生分析**：
   - 表现突出的学生
   - 需要关注的学生
   - 学习困难的学生
   - 参与度异常的学生

3. **教学效果评估**：
   - 知识点掌握情况
   - 教学方法有效性
   - 互动环节效果
   - 进度安排合理性

4. **实时教学建议**：
   - 教学策略调整建议
   - 互动方式优化
   - 难度调整建议
   - 关注重点提醒

5. **下一步行动建议**：
   - 即时干预措施
   - 内容调整建议
   - 互动活动推荐
   - 评估检测建议

请以JSON格式返回分析结果，包含以下字段：
- classroom_status: 课堂状态
- student_analysis: 学生分析
- teaching_effectiveness: 教学效果
- recommendations: 教学建议
- next_actions: 下一步行动
""",
            
            "interaction_generation": """
你是一位创新的教学设计专家。请为当前课堂生成互动内容：

课堂信息：
- 学科：{subject}
- 年级：{grade}
- 当前主题：{topic}
- 学生水平：{student_level}

教学目标：
{learning_objectives}

学生特点：
{student_characteristics}

时间限制：{time_limit}分钟

请设计以下互动内容：

1. **问答互动**：
   - 启发性问题设计
   - 分层次问题安排
   - 回答评价标准
   - 引导性提示

2. **小组活动**：
   - 活动主题和目标
   - 分组策略建议
   - 活动流程设计
   - 成果展示方式

3. **实践操作**：
   - 动手实验设计
   - 操作步骤指导
   - 安全注意事项
   - 结果分析引导

4. **游戏化元素**：
   - 学习游戏设计
   - 竞赛规则制定
   - 奖励机制设置
   - 参与激励方案

请以JSON格式返回互动内容设计。
""",
            
            "teaching_suggestion": """
你是一位经验丰富的教学顾问。请基于课堂情况提供教学建议：

当前教学情况：
- 课程进度：{progress}
- 学生掌握情况：{mastery_level}
- 课堂反馈：{classroom_feedback}
- 教学难点：{teaching_difficulties}

学生表现数据：
{student_performance}

教学目标：
{teaching_goals}

请提供以下建议：

1. **教学策略优化**：
   - 当前策略评估
   - 改进建议
   - 替代方案
   - 实施步骤

2. **内容调整建议**：
   - 重点内容强化
   - 难点突破方法
   - 内容删减建议
   - 补充材料推荐

3. **学生管理建议**：
   - 个别辅导安排
   - 分层教学策略
   - 激励措施建议
   - 课堂纪律管理

4. **评估改进建议**：
   - 评估方式优化
   - 反馈机制改进
   - 进度跟踪方法
   - 效果评价标准

请以JSON格式返回教学建议。
"""
        }
        
        return templates.get(task_type, templates["real_time_analysis"])
    
    def process_task(self, task: AgentTask) -> AgentResponse:
        """
        处理课堂AI助手任务
        
        Args:
            task: AI助手任务
            
        Returns:
            AgentResponse: 处理结果
        """
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            if task_type == "real_time_analysis":
                return self._analyze_classroom_realtime(input_data)
            elif task_type == "interaction_generation":
                return self._generate_interactions(input_data)
            elif task_type == "teaching_suggestion":
                return self._provide_teaching_suggestions(input_data)
            else:
                return AgentResponse(
                    success=False,
                    message=f"不支持的任务类型: {task_type}",
                    error_code="UNSUPPORTED_TASK_TYPE"
                )
                
        except Exception as e:
            logger.error(f"课堂AI助手任务处理失败: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"任务处理失败: {str(e)}",
                error_code="PROCESSING_ERROR"
            )
    
    def _analyze_classroom_realtime(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        实时课堂分析
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 分析结果
        """
        class_id = input_data["class_id"]
        subject = input_data.get("subject", "未知科目")
        chapter = input_data.get("chapter", "未知章节")
        class_time = input_data.get("class_time", datetime.now().isoformat())
        student_count = input_data.get("student_count", 0)
        
        classroom_data = input_data.get("classroom_data", {})
        interaction_data = input_data.get("interaction_data", {})
        teaching_content = input_data.get("teaching_content", "当前教学内容")
        
        # 格式化数据
        classroom_text = self._format_classroom_data(classroom_data)
        interaction_text = self._format_interaction_data(interaction_data)
        content_text = self._format_teaching_content(teaching_content)
        
        # 获取提示词模板
        template = self.get_prompt_template("real_time_analysis")
        
        # 格式化提示词
        prompt = self._format_prompt(
            template,
            class_id=class_id,
            subject=subject,
            chapter=chapter,
            class_time=class_time,
            student_count=student_count,
            classroom_data=classroom_text,
            interaction_data=interaction_text,
            teaching_content=content_text
        )
        
        # 调用大模型
        response_text = self._call_llm(prompt)
        
        # 解析响应
        try:
            analysis_result = self._parse_json_response(response_text)
            
            # 添加分析元数据
            analysis_metadata = {
                "analysis_id": f"analysis_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "analysis_time": datetime.now().isoformat(),
                "class_id": class_id,
                "subject": subject,
                "chapter": chapter,
                "student_count": student_count,
                "analysis_type": "real_time"
            }
            
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "real_time_analysis",
                    "analysis_metadata": analysis_metadata,
                    "classroom_analysis": analysis_result
                },
                message="实时课堂分析完成"
            )
            
        except Exception as e:
            logger.error(f"课堂分析结果解析失败: {str(e)}")
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "real_time_analysis",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="课堂分析完成，但格式需要手动处理"
            )
    
    def _generate_interactions(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        生成课堂互动内容
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 生成结果
        """
        subject = input_data.get("subject", "通用")
        grade = input_data.get("grade", "未知")
        topic = input_data.get("topic", "当前主题")
        student_level = input_data.get("student_level", "中等")
        learning_objectives = input_data.get("learning_objectives", [])
        student_characteristics = input_data.get("student_characteristics", {})
        time_limit = input_data.get("time_limit", 15)
        
        # 格式化数据
        objectives_text = self._format_learning_objectives(learning_objectives)
        characteristics_text = self._format_student_characteristics(student_characteristics)
        
        template = self.get_prompt_template("interaction_generation")
        prompt = self._format_prompt(
            template,
            subject=subject,
            grade=grade,
            topic=topic,
            student_level=student_level,
            learning_objectives=objectives_text,
            student_characteristics=characteristics_text,
            time_limit=time_limit
        )
        
        response_text = self._call_llm(prompt)
        
        try:
            interaction_content = self._parse_json_response(response_text)
            
            return AgentResponse(
                success=True,
                data={
                    "generation_type": "interaction_generation",
                    "subject": subject,
                    "topic": topic,
                    "time_limit": time_limit,
                    "interaction_content": interaction_content
                },
                message="课堂互动内容生成完成"
            )
            
        except Exception as e:
            return AgentResponse(
                success=True,
                data={
                    "generation_type": "interaction_generation",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="互动内容生成完成，格式需要手动处理"
            )
    
    def _provide_teaching_suggestions(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        提供教学建议
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 建议结果
        """
        progress = input_data.get("progress", "正常")
        mastery_level = input_data.get("mastery_level", "中等")
        classroom_feedback = input_data.get("classroom_feedback", {})
        teaching_difficulties = input_data.get("teaching_difficulties", [])
        student_performance = input_data.get("student_performance", {})
        teaching_goals = input_data.get("teaching_goals", [])
        
        # 格式化数据
        feedback_text = self._format_classroom_feedback(classroom_feedback)
        difficulties_text = self._format_teaching_difficulties(teaching_difficulties)
        performance_text = self._format_student_performance(student_performance)
        goals_text = self._format_teaching_goals(teaching_goals)
        
        template = self.get_prompt_template("teaching_suggestion")
        prompt = self._format_prompt(
            template,
            progress=progress,
            mastery_level=mastery_level,
            classroom_feedback=feedback_text,
            teaching_difficulties=difficulties_text,
            student_performance=performance_text,
            teaching_goals=goals_text
        )
        
        response_text = self._call_llm(prompt)
        
        try:
            teaching_suggestions = self._parse_json_response(response_text)
            
            return AgentResponse(
                success=True,
                data={
                    "suggestion_type": "teaching_suggestion",
                    "current_progress": progress,
                    "mastery_level": mastery_level,
                    "teaching_suggestions": teaching_suggestions
                },
                message="教学建议生成完成"
            )
            
        except Exception as e:
            return AgentResponse(
                success=True,
                data={
                    "suggestion_type": "teaching_suggestion",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="教学建议生成完成，格式需要手动处理"
            )
    
    def _format_classroom_data(self, classroom_data: Dict) -> str:
        """
        格式化课堂数据
        
        Args:
            classroom_data: 课堂数据
            
        Returns:
            str: 格式化的课堂数据
        """
        if not classroom_data:
            return "暂无课堂数据"
        
        formatted_data = []
        for key, value in classroom_data.items():
            formatted_data.append(f"- {key}: {value}")
        
        return "\n".join(formatted_data)
    
    def _format_interaction_data(self, interaction_data: Dict) -> str:
        """
        格式化互动数据
        
        Args:
            interaction_data: 互动数据
            
        Returns:
            str: 格式化的互动数据
        """
        if not interaction_data:
            return "暂无互动数据"
        
        formatted_data = []
        for key, value in interaction_data.items():
            formatted_data.append(f"- {key}: {value}")
        
        return "\n".join(formatted_data)
    
    def _format_teaching_content(self, teaching_content) -> str:
        """
        格式化教学内容
        
        Args:
            teaching_content: 教学内容
            
        Returns:
            str: 格式化的教学内容
        """
        if isinstance(teaching_content, dict):
            formatted_data = []
            for key, value in teaching_content.items():
                formatted_data.append(f"- {key}: {value}")
            return "\n".join(formatted_data)
        else:
            return str(teaching_content)
    
    def _format_learning_objectives(self, objectives: List[str]) -> str:
        """
        格式化学习目标
        
        Args:
            objectives: 学习目标列表
            
        Returns:
            str: 格式化的学习目标
        """
        if not objectives:
            return "暂无明确学习目标"
        
        return "\n".join([f"- {obj}" for obj in objectives])
    
    def _format_student_characteristics(self, characteristics: Dict) -> str:
        """
        格式化学生特点
        
        Args:
            characteristics: 学生特点
            
        Returns:
            str: 格式化的学生特点
        """
        if not characteristics:
            return "暂无学生特点数据"
        
        formatted_data = []
        for key, value in characteristics.items():
            formatted_data.append(f"- {key}: {value}")
        
        return "\n".join(formatted_data)
    
    def _format_classroom_feedback(self, feedback: Dict) -> str:
        """
        格式化课堂反馈
        
        Args:
            feedback: 课堂反馈
            
        Returns:
            str: 格式化的课堂反馈
        """
        if not feedback:
            return "暂无课堂反馈"
        
        formatted_data = []
        for key, value in feedback.items():
            formatted_data.append(f"- {key}: {value}")
        
        return "\n".join(formatted_data)
    
    def _format_teaching_difficulties(self, difficulties: List[str]) -> str:
        """
        格式化教学难点
        
        Args:
            difficulties: 教学难点列表
            
        Returns:
            str: 格式化的教学难点
        """
        if not difficulties:
            return "暂无明确教学难点"
        
        return "\n".join([f"- {diff}" for diff in difficulties])
    
    def _format_student_performance(self, performance: Dict) -> str:
        """
        格式化学生表现
        
        Args:
            performance: 学生表现数据
            
        Returns:
            str: 格式化的学生表现
        """
        if not performance:
            return "暂无学生表现数据"
        
        formatted_data = []
        for key, value in performance.items():
            formatted_data.append(f"- {key}: {value}")
        
        return "\n".join(formatted_data)
    
    def _format_teaching_goals(self, goals: List[str]) -> str:
        """
        格式化教学目标
        
        Args:
            goals: 教学目标列表
            
        Returns:
            str: 格式化的教学目标
        """
        if not goals:
            return "暂无明确教学目标"
        
        return "\n".join([f"- {goal}" for goal in goals])
    
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
    
    def analyze_classroom_realtime(self, class_id: str, classroom_data: Dict,
                                 interaction_data: Dict = None) -> Dict[str, Any]:
        """
        实时分析课堂情况的便捷方法
        
        Args:
            class_id: 班级ID
            classroom_data: 课堂数据
            interaction_data: 互动数据
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        input_data = {
            "class_id": class_id,
            "classroom_data": classroom_data,
            "interaction_data": interaction_data or {}
        }
        
        response = self.execute_task("real_time_analysis", input_data)
        return response.data if response.success else {"error": response.message}
    
    def generate_classroom_interactions(self, subject: str, topic: str, grade: str,
                                      time_limit: int = 15) -> Dict[str, Any]:
        """
        生成课堂互动内容的便捷方法
        
        Args:
            subject: 学科
            topic: 主题
            grade: 年级
            time_limit: 时间限制
            
        Returns:
            Dict[str, Any]: 互动内容
        """
        input_data = {
            "subject": subject,
            "topic": topic,
            "grade": grade,
            "time_limit": time_limit
        }
        
        response = self.execute_task("interaction_generation", input_data)
        return response.data if response.success else {"error": response.message}