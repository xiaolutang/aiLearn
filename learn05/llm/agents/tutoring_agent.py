# -*- coding: utf-8 -*-
"""
辅导方案生成智能体模块
提供个性化学习辅导方案生成、练习题推荐、学习计划制定等功能
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .base_agent import BaseTeachingAgent, AgentType, AgentTask, AgentResponse

logger = logging.getLogger(__name__)


class TutoringAgent(BaseTeachingAgent):
    """辅导方案生成智能体"""
    
    def __init__(self, llm_client=None, config: Optional[Dict] = None):
        super().__init__(AgentType.TUTORING, llm_client, config)
        
        # 辅导方案生成专用配置
        self.tutoring_config = {
            "plan_duration_weeks": 4,       # 默认计划周期（周）
            "daily_study_hours": 2,         # 每日学习时间（小时）
            "difficulty_levels": [          # 难度等级
                "基础", "提高", "拓展", "竞赛"
            ],
            "learning_styles": [            # 学习风格
                "视觉型", "听觉型", "动手型", "阅读型"
            ],
            "subject_priorities": {         # 学科优先级权重
                "语文": 1.0,
                "数学": 1.2,
                "英语": 1.1,
                "物理": 1.0,
                "化学": 1.0,
                "生物": 0.9
            },
            "exercise_types": [             # 练习题类型
                "基础练习", "综合应用", "真题模拟", "专项突破"
            ]
        }
        
        self.tutoring_config.update(config.get("tutoring_config", {}) if config else {})
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证辅导方案生成输入数据
        
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
        
        # 检查学习目标
        learning_goals = input_data.get("learning_goals", [])
        if not learning_goals:
            logger.warning("未设置学习目标，将生成通用辅导方案")
        
        return True
    
    def get_prompt_template(self, task_type: str) -> str:
        """
        获取辅导方案生成提示词模板
        
        Args:
            task_type: 任务类型
            
        Returns:
            str: 提示词模板
        """
        templates = {
            "comprehensive_plan": """
你是一位资深的个性化教育专家和学习规划师。请基于以下学生信息生成全面的个性化辅导方案：

学生基本信息：
- 学生ID：{student_id}
- 姓名：{student_name}
- 年级：{grade}
- 班级：{class_name}

学习现状分析：
{learning_status}

薄弱环节：
{weakness_areas}

学习目标：
{learning_goals}

时间安排：
- 计划周期：{plan_duration}周
- 每日可用学习时间：{daily_hours}小时
- 学习风格偏好：{learning_style}

请生成包含以下内容的个性化辅导方案：

1. **总体学习策略**：
   - 学习重点和优先级
   - 学习方法建议
   - 时间分配策略
   - 阶段性目标设定

2. **分科辅导计划**：
   - 各学科具体学习计划
   - 知识点梳理和重点突破
   - 练习安排和难度递进
   - 复习巩固策略

3. **周计划安排**：
   - 每周学习重点
   - 具体学习任务
   - 练习题目推荐
   - 阶段性检测安排

4. **学习资源推荐**：
   - 教材和参考书
   - 在线学习资源
   - 练习题库推荐
   - 辅助学习工具

5. **进度监控方案**：
   - 学习进度跟踪方法
   - 效果评估标准
   - 调整优化机制
   - 激励措施建议

请以JSON格式返回辅导方案，包含以下字段：
- overall_strategy: 总体策略
- subject_plans: 分科计划
- weekly_schedule: 周计划
- resources: 学习资源
- monitoring: 监控方案
""",
            
            "exercise_recommendation": """
你是一位专业的题目推荐专家。请基于学生的学习情况推荐合适的练习题：

学生信息：
- 年级：{grade}
- 学科：{subject}
- 当前水平：{current_level}

薄弱知识点：
{weak_points}

学习目标：
{target_goals}

题目要求：
- 难度等级：{difficulty_level}
- 题目数量：{exercise_count}
- 练习类型：{exercise_type}

请推荐练习题目，包含：

1. **基础巩固题**：
   - 针对薄弱知识点的基础练习
   - 题目类型和数量
   - 预期完成时间

2. **能力提升题**：
   - 综合应用类题目
   - 思维训练题目
   - 解题技巧练习

3. **检测评估题**：
   - 阶段性测试题目
   - 模拟考试题目
   - 自我评估标准

请以JSON格式返回推荐结果。
""",
            
            "study_schedule": """
你是一位学习时间管理专家。请为学生制定详细的学习时间表：

学生信息：
- 年级：{grade}
- 可用学习时间：每日{daily_hours}小时
- 学习周期：{duration}周

学科安排：
{subjects_info}

学习目标：
{learning_objectives}

请制定：

1. **每日时间安排**：
   - 各学科时间分配
   - 学习内容安排
   - 休息时间规划

2. **每周重点安排**：
   - 周学习主题
   - 重点突破内容
   - 复习巩固安排

3. **阶段性安排**：
   - 月度学习目标
   - 阶段性检测
   - 调整优化节点

请以JSON格式返回时间安排。
"""
        }
        
        return templates.get(task_type, templates["comprehensive_plan"])
    
    def process_task(self, task: AgentTask) -> AgentResponse:
        """
        处理辅导方案生成任务
        
        Args:
            task: 生成任务
            
        Returns:
            AgentResponse: 生成结果
        """
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            if task_type == "comprehensive_plan":
                return self._generate_comprehensive_plan(input_data)
            elif task_type == "exercise_recommendation":
                return self._recommend_exercises(input_data)
            elif task_type == "study_schedule":
                return self._create_study_schedule(input_data)
            else:
                return AgentResponse(
                    success=False,
                    message=f"不支持的任务类型: {task_type}",
                    error_code="UNSUPPORTED_TASK_TYPE"
                )
                
        except Exception as e:
            logger.error(f"辅导方案生成任务处理失败: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"任务处理失败: {str(e)}",
                error_code="PROCESSING_ERROR"
            )
    
    def _generate_comprehensive_plan(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        生成综合辅导方案
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 生成结果
        """
        student_id = input_data["student_id"]
        student_name = input_data.get("student_name", "未知")
        grade = input_data.get("grade", "未知")
        class_name = input_data.get("class_name", "未知")
        
        learning_status = input_data.get("learning_status", "暂无学习现状数据")
        weakness_areas = input_data.get("weakness_areas", [])
        learning_goals = input_data.get("learning_goals", [])
        
        plan_duration = input_data.get("plan_duration", self.tutoring_config["plan_duration_weeks"])
        daily_hours = input_data.get("daily_hours", self.tutoring_config["daily_study_hours"])
        learning_style = input_data.get("learning_style", "综合型")
        
        # 格式化数据
        weakness_text = self._format_weakness_areas(weakness_areas)
        goals_text = self._format_learning_goals(learning_goals)
        status_text = self._format_learning_status(learning_status)
        
        # 获取提示词模板
        template = self.get_prompt_template("comprehensive_plan")
        
        # 格式化提示词
        prompt = self._format_prompt(
            template,
            student_id=student_id,
            student_name=student_name,
            grade=grade,
            class_name=class_name,
            learning_status=status_text,
            weakness_areas=weakness_text,
            learning_goals=goals_text,
            plan_duration=plan_duration,
            daily_hours=daily_hours,
            learning_style=learning_style
        )
        
        # 调用大模型
        response_text = self._call_llm(prompt)
        
        # 解析响应
        try:
            tutoring_plan = self._parse_json_response(response_text)
            
            # 添加计划元数据
            plan_metadata = {
                "plan_id": f"plan_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "duration_weeks": plan_duration,
                "daily_hours": daily_hours,
                "learning_style": learning_style,
                "target_subjects": list(set([w.get("subject", "通用") for w in weakness_areas])),
                "plan_type": "comprehensive"
            }
            
            return AgentResponse(
                success=True,
                data={
                    "plan_type": "comprehensive_plan",
                    "student_info": {
                        "student_id": student_id,
                        "student_name": student_name,
                        "grade": grade,
                        "class_name": class_name
                    },
                    "plan_metadata": plan_metadata,
                    "tutoring_plan": tutoring_plan
                },
                message="综合辅导方案生成完成"
            )
            
        except Exception as e:
            logger.error(f"辅导方案解析失败: {str(e)}")
            return AgentResponse(
                success=True,
                data={
                    "plan_type": "comprehensive_plan",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="辅导方案生成完成，但格式需要手动处理"
            )
    
    def _recommend_exercises(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        推荐练习题目
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 推荐结果
        """
        grade = input_data.get("grade", "未知")
        subject = input_data.get("subject", "通用")
        current_level = input_data.get("current_level", "中等")
        weak_points = input_data.get("weak_points", [])
        target_goals = input_data.get("target_goals", [])
        difficulty_level = input_data.get("difficulty_level", "基础")
        exercise_count = input_data.get("exercise_count", 20)
        exercise_type = input_data.get("exercise_type", "综合练习")
        
        # 格式化数据
        weak_points_text = self._format_weak_points(weak_points)
        goals_text = self._format_target_goals(target_goals)
        
        template = self.get_prompt_template("exercise_recommendation")
        prompt = self._format_prompt(
            template,
            grade=grade,
            subject=subject,
            current_level=current_level,
            weak_points=weak_points_text,
            target_goals=goals_text,
            difficulty_level=difficulty_level,
            exercise_count=exercise_count,
            exercise_type=exercise_type
        )
        
        response_text = self._call_llm(prompt)
        
        try:
            exercise_recommendations = self._parse_json_response(response_text)
            
            return AgentResponse(
                success=True,
                data={
                    "recommendation_type": "exercise_recommendation",
                    "subject": subject,
                    "difficulty_level": difficulty_level,
                    "exercise_count": exercise_count,
                    "recommendations": exercise_recommendations
                },
                message="练习题推荐完成"
            )
            
        except Exception as e:
            return AgentResponse(
                success=True,
                data={
                    "recommendation_type": "exercise_recommendation",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="练习题推荐完成，格式需要手动处理"
            )
    
    def _create_study_schedule(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        创建学习时间表
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 时间表结果
        """
        grade = input_data.get("grade", "未知")
        daily_hours = input_data.get("daily_hours", 2)
        duration = input_data.get("duration", 4)
        subjects_info = input_data.get("subjects_info", [])
        learning_objectives = input_data.get("learning_objectives", [])
        
        subjects_text = self._format_subjects_info(subjects_info)
        objectives_text = self._format_learning_objectives(learning_objectives)
        
        template = self.get_prompt_template("study_schedule")
        prompt = self._format_prompt(
            template,
            grade=grade,
            daily_hours=daily_hours,
            duration=duration,
            subjects_info=subjects_text,
            learning_objectives=objectives_text
        )
        
        response_text = self._call_llm(prompt)
        
        try:
            study_schedule = self._parse_json_response(response_text)
            
            # 生成具体的日期安排
            schedule_dates = self._generate_schedule_dates(duration)
            
            return AgentResponse(
                success=True,
                data={
                    "schedule_type": "study_schedule",
                    "duration_weeks": duration,
                    "daily_hours": daily_hours,
                    "schedule_dates": schedule_dates,
                    "study_schedule": study_schedule
                },
                message="学习时间表创建完成"
            )
            
        except Exception as e:
            return AgentResponse(
                success=True,
                data={
                    "schedule_type": "study_schedule",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="学习时间表创建完成，格式需要手动处理"
            )
    
    def _format_weakness_areas(self, weakness_areas: List[Dict]) -> str:
        """
        格式化薄弱环节数据
        
        Args:
            weakness_areas: 薄弱环节列表
            
        Returns:
            str: 格式化的薄弱环节数据
        """
        if not weakness_areas:
            return "暂无明确薄弱环节"
        
        formatted_data = []
        for area in weakness_areas:
            subject = area.get("subject", "未知科目")
            topic = area.get("topic", "未知知识点")
            level = area.get("weakness_level", "中等")
            formatted_data.append(f"- {subject} - {topic} (薄弱程度: {level})")
        
        return "\n".join(formatted_data)
    
    def _format_learning_goals(self, learning_goals: List[Dict]) -> str:
        """
        格式化学习目标数据
        
        Args:
            learning_goals: 学习目标列表
            
        Returns:
            str: 格式化的学习目标数据
        """
        if not learning_goals:
            return "暂无明确学习目标"
        
        formatted_data = []
        for goal in learning_goals:
            subject = goal.get("subject", "通用")
            target = goal.get("target", "未知目标")
            deadline = goal.get("deadline", "未设定")
            formatted_data.append(f"- {subject}: {target} (期限: {deadline})")
        
        return "\n".join(formatted_data)
    
    def _format_learning_status(self, learning_status) -> str:
        """
        格式化学习现状数据
        
        Args:
            learning_status: 学习现状
            
        Returns:
            str: 格式化的学习现状数据
        """
        if isinstance(learning_status, dict):
            formatted_data = []
            for key, value in learning_status.items():
                formatted_data.append(f"- {key}: {value}")
            return "\n".join(formatted_data)
        else:
            return str(learning_status)
    
    def _format_weak_points(self, weak_points: List[str]) -> str:
        """
        格式化薄弱知识点
        
        Args:
            weak_points: 薄弱知识点列表
            
        Returns:
            str: 格式化的薄弱知识点
        """
        if not weak_points:
            return "暂无明确薄弱知识点"
        
        return "\n".join([f"- {point}" for point in weak_points])
    
    def _format_target_goals(self, target_goals: List[str]) -> str:
        """
        格式化目标
        
        Args:
            target_goals: 目标列表
            
        Returns:
            str: 格式化的目标
        """
        if not target_goals:
            return "暂无明确目标"
        
        return "\n".join([f"- {goal}" for goal in target_goals])
    
    def _format_subjects_info(self, subjects_info: List[Dict]) -> str:
        """
        格式化学科信息
        
        Args:
            subjects_info: 学科信息列表
            
        Returns:
            str: 格式化的学科信息
        """
        if not subjects_info:
            return "暂无学科信息"
        
        formatted_data = []
        for subject in subjects_info:
            name = subject.get("name", "未知科目")
            priority = subject.get("priority", "中等")
            time_allocation = subject.get("time_allocation", "未设定")
            formatted_data.append(f"- {name}: 优先级{priority}, 时间分配{time_allocation}")
        
        return "\n".join(formatted_data)
    
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
    
    def _generate_schedule_dates(self, duration_weeks: int) -> Dict[str, Any]:
        """
        生成时间表日期
        
        Args:
            duration_weeks: 持续周数
            
        Returns:
            Dict[str, Any]: 日期安排
        """
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        weeks = []
        current_date = start_date
        
        for week in range(duration_weeks):
            week_start = current_date + timedelta(weeks=week)
            week_end = week_start + timedelta(days=6)
            
            weeks.append({
                "week_number": week + 1,
                "start_date": week_start.strftime("%Y-%m-%d"),
                "end_date": week_end.strftime("%Y-%m-%d"),
                "days": [
                    (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
                    for i in range(7)
                ]
            })
        
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_weeks": duration_weeks,
            "weeks": weeks
        }
    
    def generate_tutoring_plan(self, student_id: str, learning_analysis: Dict,
                             goals: List[Dict] = None, duration_weeks: int = 4) -> Dict[str, Any]:
        """
        生成辅导方案的便捷方法
        
        Args:
            student_id: 学生ID
            learning_analysis: 学习分析结果
            goals: 学习目标
            duration_weeks: 计划周期
            
        Returns:
            Dict[str, Any]: 辅导方案
        """
        input_data = {
            "student_id": student_id,
            "learning_status": learning_analysis,
            "learning_goals": goals or [],
            "plan_duration": duration_weeks
        }
        
        response = self.execute_task("comprehensive_plan", input_data)
        return response.data if response.success else {"error": response.message}
    
    def recommend_exercises_for_student(self, subject: str, weak_points: List[str],
                                      difficulty: str = "基础", count: int = 20) -> Dict[str, Any]:
        """
        为学生推荐练习题的便捷方法
        
        Args:
            subject: 学科
            weak_points: 薄弱知识点
            difficulty: 难度等级
            count: 题目数量
            
        Returns:
            Dict[str, Any]: 练习推荐
        """
        input_data = {
            "subject": subject,
            "weak_points": weak_points,
            "difficulty_level": difficulty,
            "exercise_count": count
        }
        
        response = self.execute_task("exercise_recommendation", input_data)
        return response.data if response.success else {"error": response.message}