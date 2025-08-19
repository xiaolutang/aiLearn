# -*- coding: utf-8 -*-
"""
课堂AI助手单元测试
测试ClassroomAIAgent的课堂互动和实时分析功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from llm.agents.classroom_ai_agent import ClassroomAIAgent
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
    TEST_DATA,
    MOCK_LLM_RESPONSES,
    assert_response_valid
)


class TestClassroomAIAgent:
    """测试ClassroomAIAgent类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.agent = ClassroomAIAgent(
            llm_client=self.mock_llm_client,
            config=TEST_CONFIG
        )
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        assert self.agent.agent_type == AgentType.CLASSROOM_AI
        assert self.agent.llm_client == self.mock_llm_client
        assert isinstance(self.agent.config, dict)
        
        # 检查特定配置
        assert "real_time_analysis" in self.agent.config
        assert "interaction_support" in self.agent.config
        assert "content_generation" in self.agent.config
        assert "response_speed" in self.agent.config
    
    def test_answer_student_question(self):
        """测试回答学生问题"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["student_question_answer"]
        
        task = AgentTask(
            task_id="question_001",
            task_type="answer_question",
            input_data={
                "student_id": "STU001",
                "question": "什么是二次函数的顶点公式？",
                "subject": "数学",
                "context": "正在学习二次函数的图像和性质",
                "difficulty_level": "中等"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert_response_valid(response, ["success", "data", "message"])
        assert response.success is True
        
        # 检查回答结构
        answer_data = response.data
        assert "answer" in answer_data
        assert "explanation" in answer_data
        assert "examples" in answer_data
        assert "follow_up_questions" in answer_data
        assert "confidence_level" in answer_data
        
        # 验证LLM客户端被调用
        self.mock_llm_client.generate_response.assert_called_once()
    
    def test_generate_interactive_content(self):
        """测试生成互动内容"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["interactive_content"]
        
        task = AgentTask(
            task_id="interactive_001",
            task_type="generate_interactive_content",
            input_data={
                "topic": "化学反应平衡",
                "subject": "化学",
                "grade_level": "高中二年级",
                "interaction_type": "问答游戏",
                "duration": "15分钟",
                "class_size": 35
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        content = response.data["interactive_content"]
        
        assert "activity_name" in content
        assert "instructions" in content
        assert "questions" in content
        assert "scoring_system" in content
        assert "time_allocation" in content
        
        # 检查问题结构
        questions = content["questions"]
        assert isinstance(questions, list)
        assert len(questions) > 0
        
        for question in questions:
            assert "question_text" in question
            assert "options" in question
            assert "correct_answer" in question
            assert "explanation" in question
    
    def test_analyze_class_engagement(self):
        """测试课堂参与度分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["engagement_analysis"]
        
        task = AgentTask(
            task_id="engagement_001",
            task_type="analyze_engagement",
            input_data={
                "class_id": "CLASS_3A",
                "lesson_topic": "牛顿运动定律",
                "interaction_data": {
                    "questions_asked": 12,
                    "students_participated": 18,
                    "total_students": 30,
                    "response_time_avg": 8.5,
                    "correct_answers_rate": 0.75
                },
                "time_period": "本节课"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        analysis = response.data["engagement_analysis"]
        
        assert "overall_engagement_score" in analysis
        assert "participation_rate" in analysis
        assert "attention_indicators" in analysis
        assert "improvement_suggestions" in analysis
        assert "individual_insights" in analysis
    
    def test_provide_real_time_feedback(self):
        """测试实时反馈提供"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["real_time_feedback"]
        
        task = AgentTask(
            task_id="feedback_001",
            task_type="provide_feedback",
            input_data={
                "student_id": "STU002",
                "student_response": "我觉得这个公式应该是 F = ma",
                "correct_answer": "F = ma",
                "context": "牛顿第二定律讨论",
                "feedback_type": "鼓励性"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        feedback = response.data["feedback"]
        
        assert "feedback_message" in feedback
        assert "correctness_assessment" in feedback
        assert "encouragement" in feedback
        assert "next_steps" in feedback
        assert "confidence_boost" in feedback
    
    def test_generate_quiz_questions(self):
        """测试生成测验问题"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["quiz_questions"]
        
        task = AgentTask(
            task_id="quiz_001",
            task_type="generate_quiz",
            input_data={
                "topic": "三角函数",
                "subject": "数学",
                "difficulty_levels": ["简单", "中等", "困难"],
                "question_count": 8,
                "question_types": ["选择题", "填空题", "计算题"],
                "time_limit": "20分钟"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        quiz = response.data["quiz"]
        
        assert "quiz_title" in quiz
        assert "instructions" in quiz
        assert "questions" in quiz
        assert "answer_key" in quiz
        assert "scoring_rubric" in quiz
        
        # 检查问题数量和类型
        questions = quiz["questions"]
        assert len(questions) == 8
        
        for question in questions:
            assert "id" in question
            assert "type" in question
            assert "difficulty" in question
            assert "content" in question
            assert "points" in question
    
    def test_facilitate_group_discussion(self):
        """测试促进小组讨论"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["group_discussion"]
        
        task = AgentTask(
            task_id="discussion_001",
            task_type="facilitate_discussion",
            input_data={
                "discussion_topic": "环境保护的重要性",
                "subject": "生物",
                "group_size": 6,
                "discussion_duration": "25分钟",
                "learning_objectives": [
                    "理解生态系统平衡",
                    "分析人类活动对环境的影响",
                    "提出环保解决方案"
                ]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        discussion_guide = response.data["discussion_guide"]
        
        assert "opening_questions" in discussion_guide
        assert "discussion_prompts" in discussion_guide
        assert "role_assignments" in discussion_guide
        assert "time_management" in discussion_guide
        assert "conclusion_activities" in discussion_guide
    
    def test_adapt_teaching_pace(self):
        """测试教学节奏调整"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["pace_adaptation"]
        
        task = AgentTask(
            task_id="pace_001",
            task_type="adapt_pace",
            input_data={
                "current_topic": "电磁感应",
                "class_understanding_level": 0.65,
                "time_remaining": "15分钟",
                "planned_content": ["法拉第定律", "楞次定律", "应用实例"],
                "student_feedback": [
                    "概念有点难理解",
                    "需要更多例子",
                    "公式推导太快了"
                ]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        adaptation = response.data["pace_adaptation"]
        
        assert "recommended_pace" in adaptation
        assert "content_prioritization" in adaptation
        assert "teaching_adjustments" in adaptation
        assert "student_support_strategies" in adaptation
        assert "time_reallocation" in adaptation
    
    def test_generate_lesson_summary(self):
        """测试生成课堂总结"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["lesson_summary"]
        
        task = AgentTask(
            task_id="summary_001",
            task_type="generate_summary",
            input_data={
                "lesson_topic": "细胞分裂",
                "subject": "生物",
                "key_concepts_covered": [
                    "有丝分裂过程",
                    "减数分裂特点",
                    "细胞周期调控"
                ],
                "student_questions": [
                    "为什么需要减数分裂？",
                    "癌细胞分裂有什么特点？"
                ],
                "class_performance": "良好"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        summary = response.data["lesson_summary"]
        
        assert "main_topics" in summary
        assert "key_takeaways" in summary
        assert "student_achievements" in summary
        assert "areas_for_review" in summary
        assert "homework_suggestions" in summary
        assert "next_lesson_preview" in summary
    
    def test_handle_classroom_disruption(self):
        """测试处理课堂干扰"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["disruption_handling"]
        
        task = AgentTask(
            task_id="disruption_001",
            task_type="handle_disruption",
            input_data={
                "disruption_type": "学生注意力分散",
                "severity_level": "中等",
                "current_activity": "讲解新概念",
                "affected_students": 8,
                "time_context": "课程中段"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        handling_strategy = response.data["disruption_handling"]
        
        assert "immediate_actions" in handling_strategy
        assert "engagement_techniques" in handling_strategy
        assert "prevention_strategies" in handling_strategy
        assert "follow_up_measures" in handling_strategy
    
    def test_invalid_task_type(self):
        """测试无效任务类型"""
        task = AgentTask(
            task_id="invalid_001",
            task_type="invalid_classroom_task",
            input_data={}
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "不支持的任务类型" in response.message
        assert response.error_code == "INVALID_TASK_TYPE"
    
    def test_missing_question_content(self):
        """测试缺少问题内容"""
        task = AgentTask(
            task_id="missing_001",
            task_type="answer_question",
            input_data={
                "student_id": "STU001"
                # 缺少question字段
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "缺少问题内容" in response.message
        assert response.error_code == "MISSING_QUESTION"
    
    def test_insufficient_context(self):
        """测试上下文信息不足"""
        task = AgentTask(
            task_id="context_001",
            task_type="provide_feedback",
            input_data={
                "student_id": "STU001",
                "student_response": "答案是42"
                # 缺少context和correct_answer
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "上下文信息不足" in response.message
        assert response.error_code == "INSUFFICIENT_CONTEXT"
    
    def test_llm_client_error(self):
        """测试LLM客户端错误"""
        self.mock_llm_client.generate_response.side_effect = Exception("LLM连接超时")
        
        task = AgentTask(
            task_id="error_001",
            task_type="answer_question",
            input_data={
                "student_id": "STU001",
                "question": "什么是光合作用？",
                "subject": "生物"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "LLM连接超时" in response.message
        assert response.error_code == "LLM_ERROR"
    
    def test_get_capabilities(self):
        """测试获取智能体能力"""
        capabilities = self.agent.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_tasks" in capabilities
        assert "interaction_features" in capabilities
        assert "real_time_capabilities" in capabilities
        
        # 检查支持的任务类型
        supported_tasks = capabilities["supported_tasks"]
        expected_tasks = [
            "answer_question",
            "generate_interactive_content",
            "analyze_engagement",
            "provide_feedback",
            "generate_quiz",
            "facilitate_discussion",
            "adapt_pace",
            "generate_summary",
            "handle_disruption"
        ]
        
        for task_type in expected_tasks:
            assert task_type in supported_tasks
    
    def test_real_time_response_speed(self):
        """测试实时响应速度"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["student_question_answer"]
        
        task = AgentTask(
            task_id="speed_001",
            task_type="answer_question",
            input_data={
                "student_id": "STU001",
                "question": "简单问题测试",
                "subject": "数学",
                "priority": TaskPriority.URGENT  # 紧急任务
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        assert response.processing_time is not None
        
        # 实时响应应该很快（小于3秒）
        assert response.processing_time < 3.0
    
    def test_custom_classroom_config(self):
        """测试自定义课堂配置"""
        custom_config = {
            "real_time_analysis": True,
            "interaction_support": True,
            "content_generation": True,
            "response_speed": "fast",
            "max_question_length": 500,
            "feedback_style": "encouraging",
            "quiz_difficulty_auto_adjust": True
        }
        
        agent = ClassroomAIAgent(
            llm_client=self.mock_llm_client,
            config=custom_config
        )
        
        assert agent.config["response_speed"] == "fast"
        assert agent.config["feedback_style"] == "encouraging"
        assert agent.config["quiz_difficulty_auto_adjust"] is True
    
    def test_batch_question_answering(self):
        """测试批量问题回答"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["batch_questions"]
        
        task = AgentTask(
            task_id="batch_001",
            task_type="batch_answer_questions",
            input_data={
                "questions": [
                    {"student_id": "STU001", "question": "什么是重力？", "subject": "物理"},
                    {"student_id": "STU002", "question": "如何计算面积？", "subject": "数学"},
                    {"student_id": "STU003", "question": "细胞的结构是什么？", "subject": "生物"}
                ],
                "response_style": "简洁明了"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        batch_answers = response.data["batch_answers"]
        
        assert isinstance(batch_answers, list)
        assert len(batch_answers) == 3
        
        # 检查每个回答
        for answer in batch_answers:
            assert "student_id" in answer
            assert "question" in answer
            assert "answer" in answer
            assert "subject" in answer


if __name__ == "__main__":
    pytest.main([__file__])