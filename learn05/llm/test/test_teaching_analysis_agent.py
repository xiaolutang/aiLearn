# -*- coding: utf-8 -*-
"""
教材分析智能体单元测试
测试TeachingAnalysisAgent的教材分析功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from llm.agents.teaching_analysis_agent import TeachingAnalysisAgent
from llm.agents.base_agent import (
    AgentType,
    AgentTask,
    AgentResponse,
    TaskPriority
)
from test_config import (
    create_mock_llm_client,
    TEST_CONFIG,
    TEST_DATA,
    MOCK_LLM_RESPONSES,
    assert_response_valid
)


class TestTeachingAnalysisAgent:
    """测试TeachingAnalysisAgent类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.agent = TeachingAnalysisAgent(
            llm_client=self.mock_llm_client,
            config=TEST_CONFIG
        )
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        assert self.agent.agent_type == AgentType.TEACHING_ANALYSIS
        assert self.agent.llm_client == self.mock_llm_client
        assert isinstance(self.agent.config, dict)
        
        # 检查特定配置
        assert "analysis_depth" in self.agent.config
        assert "include_examples" in self.agent.config
        assert "knowledge_extraction" in self.agent.config
    
    def test_analyze_teaching_material(self):
        """测试教材分析功能"""
        # 设置模拟响应
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["teaching_analysis"]
        
        task = AgentTask(
            task_id="analysis_001",
            task_type="analyze_material",
            input_data={
                "content": TEST_DATA["math_lesson"],
                "subject": "数学",
                "grade": "初中二年级"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert_response_valid(response, ["success", "data", "message"])
        assert response.success is True
        
        # 检查分析结果结构
        analysis_data = response.data
        assert "knowledge_points" in analysis_data
        assert "difficulty_level" in analysis_data
        assert "learning_objectives" in analysis_data
        assert "key_concepts" in analysis_data
        
        # 验证LLM客户端被调用
        self.mock_llm_client.generate_response.assert_called_once()
    
    def test_extract_knowledge_points(self):
        """测试知识点提取"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["knowledge_extraction"]
        
        task = AgentTask(
            task_id="extract_001",
            task_type="extract_knowledge",
            input_data={
                "content": TEST_DATA["physics_lesson"],
                "extraction_type": "detailed"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        knowledge_points = response.data["knowledge_points"]
        
        assert isinstance(knowledge_points, list)
        assert len(knowledge_points) > 0
        
        # 检查知识点结构
        for point in knowledge_points:
            assert "name" in point
            assert "description" in point
            assert "importance" in point
    
    def test_analyze_difficulty_level(self):
        """测试难度分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["difficulty_analysis"]
        
        task = AgentTask(
            task_id="difficulty_001",
            task_type="analyze_difficulty",
            input_data={
                "content": TEST_DATA["chemistry_lesson"],
                "target_grade": "高中一年级"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        difficulty_data = response.data
        
        assert "overall_difficulty" in difficulty_data
        assert "difficulty_factors" in difficulty_data
        assert "recommendations" in difficulty_data
        
        # 验证难度等级
        overall_difficulty = difficulty_data["overall_difficulty"]
        assert overall_difficulty in ["简单", "中等", "困难", "很困难"]
    
    def test_generate_learning_objectives(self):
        """测试学习目标生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["learning_objectives"]
        
        task = AgentTask(
            task_id="objectives_001",
            task_type="generate_objectives",
            input_data={
                "content": TEST_DATA["english_lesson"],
                "subject": "英语",
                "duration": "45分钟"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        objectives = response.data["learning_objectives"]
        
        assert isinstance(objectives, list)
        assert len(objectives) >= 3
        
        # 检查目标结构
        for objective in objectives:
            assert "description" in objective
            assert "type" in objective  # 知识、技能、态度
            assert "measurable" in objective
    
    def test_analyze_prerequisites(self):
        """测试前置知识分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["prerequisites_analysis"]
        
        task = AgentTask(
            task_id="prereq_001",
            task_type="analyze_prerequisites",
            input_data={
                "content": TEST_DATA["math_lesson"],
                "subject": "数学"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        prerequisites = response.data["prerequisites"]
        
        assert isinstance(prerequisites, list)
        
        # 检查前置知识结构
        for prereq in prerequisites:
            assert "knowledge_point" in prereq
            assert "importance_level" in prereq
            assert "description" in prereq
    
    def test_generate_teaching_suggestions(self):
        """测试教学建议生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["teaching_suggestions"]
        
        task = AgentTask(
            task_id="suggestions_001",
            task_type="generate_suggestions",
            input_data={
                "content": TEST_DATA["physics_lesson"],
                "class_size": 30,
                "available_time": 40
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        suggestions = response.data["teaching_suggestions"]
        
        assert "methods" in suggestions
        assert "activities" in suggestions
        assert "resources" in suggestions
        assert "assessment" in suggestions
    
    def test_invalid_task_type(self):
        """测试无效任务类型"""
        task = AgentTask(
            task_id="invalid_001",
            task_type="invalid_type",
            input_data={}
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "不支持的任务类型" in response.message
        assert response.error_code == "INVALID_TASK_TYPE"
    
    def test_missing_required_data(self):
        """测试缺少必需数据"""
        task = AgentTask(
            task_id="missing_001",
            task_type="analyze_material",
            input_data={}  # 缺少content字段
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "缺少必需的输入数据" in response.message
        assert response.error_code == "MISSING_DATA"
    
    def test_llm_client_error(self):
        """测试LLM客户端错误"""
        # 模拟LLM客户端抛出异常
        self.mock_llm_client.generate_response.side_effect = Exception("LLM服务不可用")
        
        task = AgentTask(
            task_id="error_001",
            task_type="analyze_material",
            input_data={
                "content": TEST_DATA["math_lesson"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "LLM服务不可用" in response.message
        assert response.error_code == "LLM_ERROR"
    
    def test_get_capabilities(self):
        """测试获取智能体能力"""
        capabilities = self.agent.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_tasks" in capabilities
        assert "supported_subjects" in capabilities
        assert "analysis_features" in capabilities
        
        # 检查支持的任务类型
        supported_tasks = capabilities["supported_tasks"]
        expected_tasks = [
            "analyze_material",
            "extract_knowledge",
            "analyze_difficulty",
            "generate_objectives",
            "analyze_prerequisites",
            "generate_suggestions"
        ]
        
        for task_type in expected_tasks:
            assert task_type in supported_tasks
    
    def test_batch_analysis(self):
        """测试批量分析"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["batch_analysis"]
        
        task = AgentTask(
            task_id="batch_001",
            task_type="batch_analyze",
            input_data={
                "materials": [
                    {"content": TEST_DATA["math_lesson"], "subject": "数学"},
                    {"content": TEST_DATA["physics_lesson"], "subject": "物理"}
                ]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        batch_results = response.data["batch_results"]
        
        assert isinstance(batch_results, list)
        assert len(batch_results) == 2
        
        # 检查每个分析结果
        for result in batch_results:
            assert "material_index" in result
            assert "analysis" in result
            assert "subject" in result
    
    def test_custom_analysis_config(self):
        """测试自定义分析配置"""
        custom_config = {
            "analysis_depth": "deep",
            "include_examples": True,
            "knowledge_extraction": True,
            "generate_questions": True
        }
        
        agent = TeachingAnalysisAgent(
            llm_client=self.mock_llm_client,
            config=custom_config
        )
        
        assert agent.config["analysis_depth"] == "deep"
        assert agent.config["include_examples"] is True
        assert agent.config["generate_questions"] is True
    
    def test_performance_metrics(self):
        """测试性能指标"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["teaching_analysis"]
        
        task = AgentTask(
            task_id="perf_001",
            task_type="analyze_material",
            input_data={
                "content": TEST_DATA["math_lesson"]
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        assert response.processing_time is not None
        assert response.processing_time > 0
        
        # 检查性能是否在合理范围内（小于5秒）
        assert response.processing_time < 5.0


if __name__ == "__main__":
    pytest.main([__file__])