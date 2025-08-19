# -*- coding: utf-8 -*-
"""
学情分析智能体单元测试
测试LearningStatusAgent的学情分析功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from llm.agents.learning_status_agent import LearningStatusAgent
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


class TestLearningStatusAgent:
    """测试LearningStatusAgent类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.agent = LearningStatusAgent(
            llm_client=self.mock_llm_client,
            config=TEST_CONFIG
        )
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        assert self.agent.agent_type == AgentType.LEARNING_STATUS
        assert self.agent.llm_client == self.mock_llm_client
        assert isinstance(self.agent.config, dict)
        
        # 检查特定配置
        assert "analysis_dimensions" in self.agent.config
        assert "include_trends" in self.agent.config
        assert "generate_insights" in self.agent.config
    
    def test_analyze_individual_student(self):
        """测试个人学情分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["individual_analysis"]
        
        task = AgentTask(
            task_id="individual_001",
            task_type="analyze_individual",
            input_data={
                "student_id": "STU001",
                "student_data": MOCK_STUDENT_DATA[0],
                "grade_data": MOCK_GRADE_DATA[:5],  # 最近5次成绩
                "analysis_period": "本学期"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert_response_valid(response, ["success", "data", "message"])
        assert response.success is True
        
        # 检查分析结果结构
        analysis_data = response.data
        assert "student_profile" in analysis_data
        assert "performance_summary" in analysis_data
        assert "strengths" in analysis_data
        assert "weaknesses" in analysis_data
        assert "learning_trends" in analysis_data
        assert "recommendations" in analysis_data
        
        # 验证LLM客户端被调用
        self.mock_llm_client.generate_response.assert_called_once()
    
    def test_analyze_class_performance(self):
        """测试班级学情分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["class_analysis"]
        
        task = AgentTask(
            task_id="class_001",
            task_type="analyze_class",
            input_data={
                "class_id": "CLASS_2A",
                "students_data": MOCK_STUDENT_DATA,
                "grade_data": MOCK_GRADE_DATA,
                "subject": "数学"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        class_analysis = response.data
        
        assert "class_overview" in class_analysis
        assert "performance_distribution" in class_analysis
        assert "top_performers" in class_analysis
        assert "struggling_students" in class_analysis
        assert "class_trends" in class_analysis
        assert "teaching_suggestions" in class_analysis
    
    def test_identify_learning_patterns(self):
        """测试学习模式识别"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["learning_patterns"]
        
        task = AgentTask(
            task_id="patterns_001",
            task_type="identify_patterns",
            input_data={
                "student_id": "STU002",
                "historical_data": MOCK_GRADE_DATA,
                "time_span": "整个学年"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        patterns = response.data["learning_patterns"]
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        # 检查模式结构
        for pattern in patterns:
            assert "pattern_type" in pattern
            assert "description" in pattern
            assert "confidence" in pattern
            assert "evidence" in pattern
    
    def test_generate_progress_report(self):
        """测试学习进度报告生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["progress_report"]
        
        task = AgentTask(
            task_id="progress_001",
            task_type="generate_progress_report",
            input_data={
                "student_id": "STU003",
                "start_date": "2024-09-01",
                "end_date": "2024-12-31",
                "subjects": ["数学", "物理", "化学"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        report = response.data["progress_report"]
        
        assert "report_period" in report
        assert "overall_progress" in report
        assert "subject_progress" in report
        assert "achievements" in report
        assert "areas_for_improvement" in report
        assert "next_steps" in report
    
    def test_compare_students(self):
        """测试学生对比分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["student_comparison"]
        
        task = AgentTask(
            task_id="compare_001",
            task_type="compare_students",
            input_data={
                "student_ids": ["STU001", "STU002", "STU003"],
                "comparison_metrics": ["总分", "各科成绩", "学习趋势"],
                "time_period": "最近一个月"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        comparison = response.data["comparison_result"]
        
        assert "students_compared" in comparison
        assert "comparison_summary" in comparison
        assert "relative_performance" in comparison
        assert "insights" in comparison
    
    def test_predict_performance(self):
        """测试成绩预测"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["performance_prediction"]
        
        task = AgentTask(
            task_id="predict_001",
            task_type="predict_performance",
            input_data={
                "student_id": "STU001",
                "historical_grades": MOCK_GRADE_DATA,
                "prediction_period": "下个月",
                "subjects": ["数学", "英语"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        prediction = response.data["performance_prediction"]
        
        assert "predicted_scores" in prediction
        assert "confidence_level" in prediction
        assert "factors_considered" in prediction
        assert "recommendations" in prediction
    
    def test_analyze_subject_performance(self):
        """测试学科表现分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["subject_analysis"]
        
        task = AgentTask(
            task_id="subject_001",
            task_type="analyze_subject",
            input_data={
                "student_id": "STU002",
                "subject": "数学",
                "grade_data": [g for g in MOCK_GRADE_DATA if g["subject"] == "数学"],
                "include_subtopics": True
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        subject_analysis = response.data["subject_analysis"]
        
        assert "subject_name" in subject_analysis
        assert "overall_performance" in subject_analysis
        assert "topic_breakdown" in subject_analysis
        assert "improvement_areas" in subject_analysis
        assert "study_suggestions" in subject_analysis
    
    def test_generate_learning_insights(self):
        """测试学习洞察生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["learning_insights"]
        
        task = AgentTask(
            task_id="insights_001",
            task_type="generate_insights",
            input_data={
                "analysis_scope": "class",
                "class_data": MOCK_STUDENT_DATA,
                "grade_data": MOCK_GRADE_DATA,
                "insight_types": ["趋势分析", "异常检测", "相关性分析"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        insights = response.data["learning_insights"]
        
        assert isinstance(insights, list)
        
        # 检查洞察结构
        for insight in insights:
            assert "type" in insight
            assert "description" in insight
            assert "importance" in insight
            assert "actionable_steps" in insight
    
    def test_invalid_task_type(self):
        """测试无效任务类型"""
        task = AgentTask(
            task_id="invalid_001",
            task_type="invalid_analysis",
            input_data={}
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "不支持的任务类型" in response.message
        assert response.error_code == "INVALID_TASK_TYPE"
    
    def test_missing_student_data(self):
        """测试缺少学生数据"""
        task = AgentTask(
            task_id="missing_001",
            task_type="analyze_individual",
            input_data={
                "student_id": "STU999"
                # 缺少student_data和grade_data
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "缺少必需的学生数据" in response.message
        assert response.error_code == "MISSING_DATA"
    
    def test_insufficient_grade_data(self):
        """测试成绩数据不足"""
        task = AgentTask(
            task_id="insufficient_001",
            task_type="identify_patterns",
            input_data={
                "student_id": "STU001",
                "historical_data": MOCK_GRADE_DATA[:1]  # 只有一条记录
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "成绩数据不足" in response.message
        assert response.error_code == "INSUFFICIENT_DATA"
    
    def test_llm_client_error(self):
        """测试LLM客户端错误"""
        self.mock_llm_client.generate_response.side_effect = Exception("LLM服务异常")
        
        task = AgentTask(
            task_id="error_001",
            task_type="analyze_individual",
            input_data={
                "student_id": "STU001",
                "student_data": MOCK_STUDENT_DATA[0],
                "grade_data": MOCK_GRADE_DATA
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "LLM服务异常" in response.message
        assert response.error_code == "LLM_ERROR"
    
    def test_get_capabilities(self):
        """测试获取智能体能力"""
        capabilities = self.agent.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_tasks" in capabilities
        assert "analysis_types" in capabilities
        assert "data_requirements" in capabilities
        
        # 检查支持的任务类型
        supported_tasks = capabilities["supported_tasks"]
        expected_tasks = [
            "analyze_individual",
            "analyze_class",
            "identify_patterns",
            "generate_progress_report",
            "compare_students",
            "predict_performance",
            "analyze_subject",
            "generate_insights"
        ]
        
        for task_type in expected_tasks:
            assert task_type in supported_tasks
    
    def test_batch_student_analysis(self):
        """测试批量学生分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["batch_student_analysis"]
        
        task = AgentTask(
            task_id="batch_001",
            task_type="batch_analyze_students",
            input_data={
                "student_ids": ["STU001", "STU002", "STU003"],
                "analysis_type": "comprehensive",
                "include_recommendations": True
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        batch_results = response.data["batch_analysis"]
        
        assert isinstance(batch_results, list)
        assert len(batch_results) == 3
        
        # 检查每个分析结果
        for result in batch_results:
            assert "student_id" in result
            assert "analysis_summary" in result
            assert "recommendations" in result
    
    def test_custom_analysis_config(self):
        """测试自定义分析配置"""
        custom_config = {
            "analysis_dimensions": ["成绩", "学习习惯", "参与度"],
            "include_trends": True,
            "generate_insights": True,
            "prediction_enabled": True,
            "min_data_points": 5
        }
        
        agent = LearningStatusAgent(
            llm_client=self.mock_llm_client,
            config=custom_config
        )
        
        assert agent.config["analysis_dimensions"] == ["成绩", "学习习惯", "参与度"]
        assert agent.config["prediction_enabled"] is True
        assert agent.config["min_data_points"] == 5
    
    def test_performance_metrics(self):
        """测试性能指标"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["individual_analysis"]
        
        task = AgentTask(
            task_id="perf_001",
            task_type="analyze_individual",
            input_data={
                "student_id": "STU001",
                "student_data": MOCK_STUDENT_DATA[0],
                "grade_data": MOCK_GRADE_DATA
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        assert response.processing_time is not None
        assert response.processing_time > 0
        
        # 检查性能是否在合理范围内
        assert response.processing_time < 10.0


if __name__ == "__main__":
    pytest.main([__file__])