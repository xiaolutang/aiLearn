# -*- coding: utf-8 -*-
"""
辅导方案智能体单元测试
测试TutoringAgent的个性化辅导方案生成功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from llm.agents.tutoring_agent import TutoringAgent
from llm.agents.base_agent import (
    AgentType,
    AgentTask,
    AgentResponse,
    TaskPriority
)
from test_config import (
    create_mock_llm_client,
    TEST_CONFIG,
    MOCK_STUDENT_DATA,
    MOCK_GRADE_DATA,
    MOCK_LLM_RESPONSES,
    assert_response_valid
)


class TestTutoringAgent:
    """测试TutoringAgent类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.agent = TutoringAgent(
            llm_client=self.mock_llm_client,
            config=TEST_CONFIG
        )
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        assert self.agent.agent_type == AgentType.TUTORING_PLAN
        assert self.agent.llm_client == self.mock_llm_client
        assert isinstance(self.agent.config, dict)
        
        # 检查特定配置
        assert "plan_duration" in self.agent.config
        assert "difficulty_adaptation" in self.agent.config
        assert "include_exercises" in self.agent.config
        assert "progress_tracking" in self.agent.config
    
    def test_generate_personalized_plan(self):
        """测试个性化辅导方案生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["tutoring_plan"]
        
        task = AgentTask(
            task_id="plan_001",
            task_type="generate_plan",
            input_data={
                "student_id": "STU001",
                "student_profile": MOCK_STUDENT_DATA[0],
                "weak_subjects": ["数学", "物理"],
                "target_goals": ["提高数学成绩到85分以上", "掌握物理基础概念"],
                "available_time": "每周3小时",
                "plan_duration": "4周"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert_response_valid(response, ["success", "data", "message"])
        assert response.success is True
        
        # 检查辅导方案结构
        plan_data = response.data
        assert "plan_overview" in plan_data
        assert "weekly_schedule" in plan_data
        assert "learning_objectives" in plan_data
        assert "study_materials" in plan_data
        assert "practice_exercises" in plan_data
        assert "progress_milestones" in plan_data
        assert "assessment_methods" in plan_data
        
        # 验证LLM客户端被调用
        self.mock_llm_client.generate_response.assert_called_once()
    
    def test_generate_exercise_recommendations(self):
        """测试练习推荐生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["exercise_recommendations"]
        
        task = AgentTask(
            task_id="exercises_001",
            task_type="recommend_exercises",
            input_data={
                "student_id": "STU002",
                "subject": "数学",
                "topic": "二次函数",
                "difficulty_level": "中等",
                "exercise_count": 10,
                "include_solutions": True
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        exercises = response.data["exercises"]
        
        assert isinstance(exercises, list)
        assert len(exercises) <= 10
        
        # 检查练习结构
        for exercise in exercises:
            assert "question" in exercise
            assert "difficulty" in exercise
            assert "topic" in exercise
            assert "solution" in exercise
            assert "explanation" in exercise
    
    def test_create_study_schedule(self):
        """测试学习计划制定"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["study_schedule"]
        
        task = AgentTask(
            task_id="schedule_001",
            task_type="create_schedule",
            input_data={
                "student_id": "STU003",
                "subjects": ["数学", "英语", "物理"],
                "available_hours_per_week": 15,
                "preferred_study_times": ["晚上7-9点", "周末上午"],
                "exam_dates": {
                    "数学": "2024-02-15",
                    "英语": "2024-02-20",
                    "物理": "2024-02-25"
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        schedule = response.data["study_schedule"]
        
        assert "weekly_plan" in schedule
        assert "daily_tasks" in schedule
        assert "subject_allocation" in schedule
        assert "review_sessions" in schedule
        assert "flexibility_notes" in schedule
    
    def test_generate_learning_path(self):
        """测试学习路径生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["learning_path"]
        
        task = AgentTask(
            task_id="path_001",
            task_type="generate_learning_path",
            input_data={
                "student_id": "STU001",
                "current_level": "初中二年级",
                "target_level": "高中一年级",
                "subject": "数学",
                "knowledge_gaps": ["代数基础", "几何证明"],
                "learning_style": "视觉型"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        learning_path = response.data["learning_path"]
        
        assert "path_overview" in learning_path
        assert "learning_stages" in learning_path
        assert "prerequisite_skills" in learning_path
        assert "recommended_resources" in learning_path
        assert "assessment_checkpoints" in learning_path
    
    def test_adapt_difficulty_level(self):
        """测试难度自适应调整"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["difficulty_adaptation"]
        
        task = AgentTask(
            task_id="adapt_001",
            task_type="adapt_difficulty",
            input_data={
                "student_id": "STU002",
                "current_performance": {
                    "correct_rate": 0.6,
                    "completion_time": "平均",
                    "confidence_level": "中等"
                },
                "subject": "物理",
                "topic": "力学",
                "current_difficulty": "中等"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        adaptation = response.data["difficulty_adaptation"]
        
        assert "recommended_difficulty" in adaptation
        assert "adjustment_reason" in adaptation
        assert "next_steps" in adaptation
        assert "monitoring_metrics" in adaptation
    
    def test_generate_motivation_strategies(self):
        """测试学习动机策略生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["motivation_strategies"]
        
        task = AgentTask(
            task_id="motivation_001",
            task_type="generate_motivation_strategies",
            input_data={
                "student_id": "STU003",
                "motivation_issues": ["缺乏学习兴趣", "容易放弃"],
                "personality_traits": ["内向", "完美主义"],
                "interests": ["游戏", "音乐", "绘画"],
                "learning_goals": ["提高数学成绩", "增强自信心"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        strategies = response.data["motivation_strategies"]
        
        assert isinstance(strategies, list)
        
        # 检查策略结构
        for strategy in strategies:
            assert "strategy_name" in strategy
            assert "description" in strategy
            assert "implementation" in strategy
            assert "expected_outcome" in strategy
    
    def test_create_progress_tracking_plan(self):
        """测试进度跟踪计划创建"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["progress_tracking"]
        
        task = AgentTask(
            task_id="tracking_001",
            task_type="create_progress_tracking",
            input_data={
                "student_id": "STU001",
                "learning_objectives": [
                    "掌握二次函数基本概念",
                    "能够解决二次函数应用题",
                    "理解函数图像变换规律"
                ],
                "tracking_frequency": "每周",
                "assessment_methods": ["练习测试", "口头问答", "项目作业"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        tracking_plan = response.data["progress_tracking_plan"]
        
        assert "tracking_metrics" in tracking_plan
        assert "milestone_checkpoints" in tracking_plan
        assert "assessment_schedule" in tracking_plan
        assert "feedback_mechanisms" in tracking_plan
        assert "adjustment_triggers" in tracking_plan
    
    def test_generate_remedial_plan(self):
        """测试补救教学方案生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["remedial_plan"]
        
        task = AgentTask(
            task_id="remedial_001",
            task_type="generate_remedial_plan",
            input_data={
                "student_id": "STU002",
                "failing_subjects": ["数学", "化学"],
                "specific_weaknesses": {
                    "数学": ["分数运算", "方程求解"],
                    "化学": ["化学方程式", "摩尔计算"]
                },
                "time_constraints": "期末考试前2周",
                "support_resources": ["在线视频", "练习册", "一对一辅导"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        remedial_plan = response.data["remedial_plan"]
        
        assert "priority_topics" in remedial_plan
        assert "intensive_schedule" in remedial_plan
        assert "targeted_exercises" in remedial_plan
        assert "support_strategies" in remedial_plan
        assert "success_criteria" in remedial_plan
    
    def test_invalid_task_type(self):
        """测试无效任务类型"""
        task = AgentTask(
            task_id="invalid_001",
            task_type="invalid_tutoring",
            input_data={}
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "不支持的任务类型" in response.message
        assert response.error_code == "INVALID_TASK_TYPE"
    
    def test_missing_student_profile(self):
        """测试缺少学生档案"""
        task = AgentTask(
            task_id="missing_001",
            task_type="generate_plan",
            input_data={
                "student_id": "STU999"
                # 缺少student_profile
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "缺少学生档案信息" in response.message
        assert response.error_code == "MISSING_PROFILE"
    
    def test_insufficient_learning_data(self):
        """测试学习数据不足"""
        task = AgentTask(
            task_id="insufficient_001",
            task_type="adapt_difficulty",
            input_data={
                "student_id": "STU001",
                "current_performance": {}  # 空的性能数据
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "学习数据不足" in response.message
        assert response.error_code == "INSUFFICIENT_DATA"
    
    def test_llm_client_error(self):
        """测试LLM客户端错误"""
        self.mock_llm_client.generate_response.side_effect = Exception("LLM服务中断")
        
        task = AgentTask(
            task_id="error_001",
            task_type="generate_plan",
            input_data={
                "student_id": "STU001",
                "student_profile": MOCK_STUDENT_DATA[0],
                "weak_subjects": ["数学"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "LLM服务中断" in response.message
        assert response.error_code == "LLM_ERROR"
    
    def test_get_capabilities(self):
        """测试获取智能体能力"""
        capabilities = self.agent.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_tasks" in capabilities
        assert "tutoring_features" in capabilities
        assert "personalization_options" in capabilities
        
        # 检查支持的任务类型
        supported_tasks = capabilities["supported_tasks"]
        expected_tasks = [
            "generate_plan",
            "recommend_exercises",
            "create_schedule",
            "generate_learning_path",
            "adapt_difficulty",
            "generate_motivation_strategies",
            "create_progress_tracking",
            "generate_remedial_plan"
        ]
        
        for task_type in expected_tasks:
            assert task_type in supported_tasks
    
    def test_batch_plan_generation(self):
        """测试批量方案生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["batch_tutoring_plans"]
        
        task = AgentTask(
            task_id="batch_001",
            task_type="batch_generate_plans",
            input_data={
                "student_profiles": MOCK_STUDENT_DATA[:3],
                "common_subjects": ["数学", "英语"],
                "plan_template": "标准辅导方案",
                "duration": "4周"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        batch_plans = response.data["batch_plans"]
        
        assert isinstance(batch_plans, list)
        assert len(batch_plans) == 3
        
        # 检查每个方案
        for plan in batch_plans:
            assert "student_id" in plan
            assert "personalized_plan" in plan
            assert "customizations" in plan
    
    def test_custom_tutoring_config(self):
        """测试自定义辅导配置"""
        custom_config = {
            "plan_duration": "8周",
            "difficulty_adaptation": True,
            "include_exercises": True,
            "progress_tracking": True,
            "motivation_support": True,
            "max_subjects_per_plan": 3,
            "exercise_difficulty_range": ["简单", "中等", "困难"]
        }
        
        agent = TutoringAgent(
            llm_client=self.mock_llm_client,
            config=custom_config
        )
        
        assert agent.config["plan_duration"] == "8周"
        assert agent.config["motivation_support"] is True
        assert agent.config["max_subjects_per_plan"] == 3
    
    def test_performance_metrics(self):
        """测试性能指标"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["tutoring_plan"]
        
        task = AgentTask(
            task_id="perf_001",
            task_type="generate_plan",
            input_data={
                "student_id": "STU001",
                "student_profile": MOCK_STUDENT_DATA[0],
                "weak_subjects": ["数学"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        assert response.processing_time is not None
        assert response.processing_time > 0
        
        # 检查性能是否在合理范围内
        assert response.processing_time < 15.0


if __name__ == "__main__":
    pytest.main([__file__])