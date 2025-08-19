# -*- coding: utf-8 -*-
"""
基础智能体单元测试
测试BaseTeachingAgent的基础功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any

from llm.agents.base_agent import (
    BaseTeachingAgent,
    AgentType,
    AgentTask,
    AgentResponse,
    TaskPriority
)
from test_config import (
    create_mock_llm_client,
    TEST_CONFIG,
    assert_response_valid
)


class TestAgentTask:
    """测试AgentTask数据类"""
    
    def test_agent_task_creation(self):
        """测试任务创建"""
        task = AgentTask(
            task_id="test_task_001",
            task_type="analysis",
            input_data={"content": "test content"},
            priority=TaskPriority.HIGH
        )
        
        assert task.task_id == "test_task_001"
        assert task.task_type == "analysis"
        assert task.input_data["content"] == "test content"
        assert task.priority == TaskPriority.HIGH
        assert task.created_at is not None
        assert task.completed_at is None
        assert task.result is None
        assert task.error is None
    
    def test_agent_task_default_values(self):
        """测试任务默认值"""
        task = AgentTask(
            task_id="test_task_002",
            task_type="analysis",
            input_data={}
        )
        
        assert task.priority == TaskPriority.MEDIUM
        assert isinstance(task.created_at, float)
        assert task.created_at <= time.time()


class TestAgentResponse:
    """测试AgentResponse数据类"""
    
    def test_agent_response_creation(self):
        """测试响应创建"""
        response = AgentResponse(
            success=True,
            data={"result": "test result"},
            message="操作成功",
            processing_time=1.5
        )
        
        assert response.success is True
        assert response.data["result"] == "test result"
        assert response.message == "操作成功"
        assert response.processing_time == 1.5
        assert response.error_code is None
        assert response.metadata is None
    
    def test_agent_response_error(self):
        """测试错误响应"""
        response = AgentResponse(
            success=False,
            message="操作失败",
            error_code="ERR_001"
        )
        
        assert response.success is False
        assert response.message == "操作失败"
        assert response.error_code == "ERR_001"
        assert response.data is None


class ConcreteTeachingAgent(BaseTeachingAgent):
    """具体的教学智能体实现，用于测试"""
    
    def process_task(self, task: AgentTask) -> AgentResponse:
        """处理任务的具体实现"""
        start_time = time.time()
        
        try:
            # 模拟处理逻辑
            if task.task_type == "analysis":
                result = {"analysis_result": "分析完成"}
            elif task.task_type == "generation":
                result = {"generated_content": "生成内容"}
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")
            
            processing_time = time.time() - start_time
            
            return AgentResponse(
                success=True,
                data=result,
                message="任务处理成功",
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return AgentResponse(
                success=False,
                message=f"任务处理失败: {str(e)}",
                error_code="TASK_ERROR",
                processing_time=processing_time
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取智能体能力"""
        return {
            "supported_tasks": ["analysis", "generation"],
            "max_concurrent_tasks": 5,
            "estimated_processing_time": 2.0
        }


class TestBaseTeachingAgent:
    """测试BaseTeachingAgent基础类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.agent = ConcreteTeachingAgent(
            agent_type=AgentType.TEACHING_ANALYSIS,
            llm_client=self.mock_llm_client,
            config=TEST_CONFIG
        )
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        assert self.agent.agent_type == AgentType.TEACHING_ANALYSIS
        assert self.agent.llm_client == self.mock_llm_client
        assert isinstance(self.agent.config, dict)
        assert isinstance(self.agent.task_history, list)
        assert len(self.agent.task_history) == 0
        
        # 检查默认配置
        assert "max_retries" in self.agent.config
        assert "timeout" in self.agent.config
        assert "temperature" in self.agent.config
    
    def test_agent_config_merge(self):
        """测试配置合并"""
        custom_config = {"temperature": 0.5, "custom_param": "test"}
        agent = ConcreteTeachingAgent(
            agent_type=AgentType.LEARNING_STATUS,
            config=custom_config
        )
        
        # 自定义配置应该覆盖默认配置
        assert agent.config["temperature"] == 0.5
        assert agent.config["custom_param"] == "test"
        # 默认配置应该保留
        assert "max_retries" in agent.config
        assert "timeout" in agent.config
    
    def test_process_task_success(self):
        """测试成功处理任务"""
        task = AgentTask(
            task_id="test_001",
            task_type="analysis",
            input_data={"content": "test content"}
        )
        
        response = self.agent.process_task(task)
        
        assert_response_valid(response, ["success", "data", "message"])
        assert response.success is True
        assert "analysis_result" in response.data
        assert response.processing_time is not None
        assert response.processing_time >= 0
    
    def test_process_task_failure(self):
        """测试任务处理失败"""
        task = AgentTask(
            task_id="test_002",
            task_type="unsupported",
            input_data={}
        )
        
        response = self.agent.process_task(task)
        
        assert_response_valid(response, ["success", "message"])
        assert response.success is False
        assert "不支持的任务类型" in response.message
        assert response.error_code == "TASK_ERROR"
    
    def test_get_capabilities(self):
        """测试获取智能体能力"""
        capabilities = self.agent.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_tasks" in capabilities
        assert "analysis" in capabilities["supported_tasks"]
        assert "generation" in capabilities["supported_tasks"]
    
    def test_agent_without_llm_client(self):
        """测试没有LLM客户端的智能体"""
        agent = ConcreteTeachingAgent(
            agent_type=AgentType.TUTORING_PLAN
        )
        
        assert agent.llm_client is None
        assert agent.agent_type == AgentType.TUTORING_PLAN
        
        # 应该仍然能够处理不需要LLM的任务
        task = AgentTask(
            task_id="test_003",
            task_type="analysis",
            input_data={}
        )
        
        response = agent.process_task(task)
        assert response.success is True
    
    def test_task_priority_handling(self):
        """测试任务优先级处理"""
        high_priority_task = AgentTask(
            task_id="high_001",
            task_type="analysis",
            input_data={},
            priority=TaskPriority.HIGH
        )
        
        low_priority_task = AgentTask(
            task_id="low_001",
            task_type="analysis",
            input_data={},
            priority=TaskPriority.LOW
        )
        
        # 处理高优先级任务
        high_response = self.agent.process_task(high_priority_task)
        assert high_response.success is True
        
        # 处理低优先级任务
        low_response = self.agent.process_task(low_priority_task)
        assert low_response.success is True
        
        # 两个任务都应该成功处理
        assert high_response.success == low_response.success
    
    def test_agent_type_enum(self):
        """测试智能体类型枚举"""
        assert AgentType.TEACHING_ANALYSIS.value == "teaching_analysis"
        assert AgentType.LEARNING_STATUS.value == "learning_status"
        assert AgentType.TUTORING_PLAN.value == "tutoring_plan"
        assert AgentType.CLASSROOM_AI.value == "classroom_ai"
        
        # 测试枚举的完整性
        agent_types = list(AgentType)
        assert len(agent_types) >= 4
    
    def test_task_priority_enum(self):
        """测试任务优先级枚举"""
        assert TaskPriority.LOW.value == 1
        assert TaskPriority.MEDIUM.value == 2
        assert TaskPriority.HIGH.value == 3
        assert TaskPriority.URGENT.value == 4
        
        # 测试优先级排序
        priorities = [TaskPriority.URGENT, TaskPriority.LOW, TaskPriority.HIGH, TaskPriority.MEDIUM]
        sorted_priorities = sorted(priorities, key=lambda x: x.value)
        
        assert sorted_priorities[0] == TaskPriority.LOW
        assert sorted_priorities[-1] == TaskPriority.URGENT


if __name__ == "__main__":
    pytest.main([__file__])