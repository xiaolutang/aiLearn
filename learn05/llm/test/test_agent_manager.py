# -*- coding: utf-8 -*-
"""
智能体管理器单元测试
测试AgentManager的智能体管理和调度功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from llm.agents.agent_manager import AgentManager
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


class MockTeachingAgent(BaseTeachingAgent):
    """模拟教学智能体"""
    
    def __init__(self, agent_type: AgentType, processing_time: float = 0.1, should_fail: bool = False):
        super().__init__(agent_type=agent_type)
        self.processing_time = processing_time
        self.should_fail = should_fail
        self.processed_tasks = []
    
    def process_task(self, task: AgentTask) -> AgentResponse:
        """处理任务"""
        import time
        start_time = time.time()
        
        # 记录处理的任务
        self.processed_tasks.append(task)
        
        # 模拟处理时间
        time.sleep(self.processing_time)
        
        if self.should_fail:
            return AgentResponse(
                success=False,
                message="模拟处理失败",
                error_code="MOCK_ERROR",
                processing_time=time.time() - start_time
            )
        
        return AgentResponse(
            success=True,
            data={"result": f"处理完成 - {task.task_id}"},
            message="任务处理成功",
            processing_time=time.time() - start_time
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取智能体能力"""
        return {
            "supported_tasks": ["analysis", "generation"],
            "max_concurrent_tasks": 3,
            "estimated_processing_time": self.processing_time
        }


class TestAgentManager:
    """测试AgentManager类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.manager = AgentManager(
            llm_client=self.mock_llm_client,
            config=TEST_CONFIG
        )
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.llm_client == self.mock_llm_client
        assert isinstance(self.manager.config, dict)
        assert isinstance(self.manager.agents, dict)
        assert isinstance(self.manager.task_queue, list)
        assert len(self.manager.agents) == 0
        assert len(self.manager.task_queue) == 0
    
    def test_register_agent(self):
        """测试注册智能体"""
        agent = MockTeachingAgent(AgentType.TEACHING_ANALYSIS)
        
        # 注册智能体
        self.manager.register_agent(AgentType.TEACHING_ANALYSIS, agent)
        
        assert AgentType.TEACHING_ANALYSIS in self.manager.agents
        assert self.manager.agents[AgentType.TEACHING_ANALYSIS] == agent
    
    def test_register_multiple_agents(self):
        """测试注册多个智能体"""
        teaching_agent = MockTeachingAgent(AgentType.TEACHING_ANALYSIS)
        learning_agent = MockTeachingAgent(AgentType.LEARNING_STATUS)
        
        self.manager.register_agent(AgentType.TEACHING_ANALYSIS, teaching_agent)
        self.manager.register_agent(AgentType.LEARNING_STATUS, learning_agent)
        
        assert len(self.manager.agents) == 2
        assert AgentType.TEACHING_ANALYSIS in self.manager.agents
        assert AgentType.LEARNING_STATUS in self.manager.agents
    
    def test_get_agent(self):
        """测试获取智能体"""
        agent = MockTeachingAgent(AgentType.TUTORING_PLAN)
        self.manager.register_agent(AgentType.TUTORING_PLAN, agent)
        
        retrieved_agent = self.manager.get_agent(AgentType.TUTORING_PLAN)
        assert retrieved_agent == agent
        
        # 测试获取不存在的智能体
        non_existent_agent = self.manager.get_agent(AgentType.CLASSROOM_AI)
        assert non_existent_agent is None
    
    def test_get_available_agents(self):
        """测试获取可用智能体列表"""
        teaching_agent = MockTeachingAgent(AgentType.TEACHING_ANALYSIS)
        learning_agent = MockTeachingAgent(AgentType.LEARNING_STATUS)
        
        self.manager.register_agent(AgentType.TEACHING_ANALYSIS, teaching_agent)
        self.manager.register_agent(AgentType.LEARNING_STATUS, learning_agent)
        
        available_agents = self.manager.get_available_agents()
        
        assert len(available_agents) == 2
        assert AgentType.TEACHING_ANALYSIS in available_agents
        assert AgentType.LEARNING_STATUS in available_agents
    
    def test_submit_task(self):
        """测试提交任务"""
        agent = MockTeachingAgent(AgentType.TEACHING_ANALYSIS)
        self.manager.register_agent(AgentType.TEACHING_ANALYSIS, agent)
        
        task = AgentTask(
            task_id="test_001",
            task_type="analysis",
            input_data={"content": "test content"}
        )
        
        response = self.manager.submit_task(AgentType.TEACHING_ANALYSIS, task)
        
        assert_response_valid(response, ["success", "data", "message"])
        assert response.success is True
        assert "处理完成" in response.data["result"]
        assert len(agent.processed_tasks) == 1
        assert agent.processed_tasks[0] == task
    
    def test_submit_task_to_nonexistent_agent(self):
        """测试向不存在的智能体提交任务"""
        task = AgentTask(
            task_id="test_002",
            task_type="analysis",
            input_data={}
        )
        
        response = self.manager.submit_task(AgentType.CLASSROOM_AI, task)
        
        assert response.success is False
        assert "智能体不存在" in response.message
        assert response.error_code == "AGENT_NOT_FOUND"
    
    def test_submit_task_with_failure(self):
        """测试任务处理失败"""
        agent = MockTeachingAgent(AgentType.LEARNING_STATUS, should_fail=True)
        self.manager.register_agent(AgentType.LEARNING_STATUS, agent)
        
        task = AgentTask(
            task_id="test_003",
            task_type="analysis",
            input_data={}
        )
        
        response = self.manager.submit_task(AgentType.LEARNING_STATUS, task)
        
        assert response.success is False
        assert "模拟处理失败" in response.message
        assert response.error_code == "MOCK_ERROR"
    
    def test_get_agent_capabilities(self):
        """测试获取智能体能力"""
        agent = MockTeachingAgent(AgentType.TUTORING_PLAN)
        self.manager.register_agent(AgentType.TUTORING_PLAN, agent)
        
        capabilities = self.manager.get_agent_capabilities(AgentType.TUTORING_PLAN)
        
        assert isinstance(capabilities, dict)
        assert "supported_tasks" in capabilities
        assert "max_concurrent_tasks" in capabilities
        assert capabilities["max_concurrent_tasks"] == 3
    
    def test_get_capabilities_for_nonexistent_agent(self):
        """测试获取不存在智能体的能力"""
        capabilities = self.manager.get_agent_capabilities(AgentType.CLASSROOM_AI)
        assert capabilities is None
    
    def test_task_priority_handling(self):
        """测试任务优先级处理"""
        agent = MockTeachingAgent(AgentType.TEACHING_ANALYSIS, processing_time=0.05)
        self.manager.register_agent(AgentType.TEACHING_ANALYSIS, agent)
        
        # 创建不同优先级的任务
        high_task = AgentTask(
            task_id="high_001",
            task_type="analysis",
            input_data={},
            priority=TaskPriority.HIGH
        )
        
        low_task = AgentTask(
            task_id="low_001",
            task_type="analysis",
            input_data={},
            priority=TaskPriority.LOW
        )
        
        # 提交任务
        high_response = self.manager.submit_task(AgentType.TEACHING_ANALYSIS, high_task)
        low_response = self.manager.submit_task(AgentType.TEACHING_ANALYSIS, low_task)
        
        assert high_response.success is True
        assert low_response.success is True
        
        # 验证任务都被处理
        assert len(agent.processed_tasks) == 2
    
    def test_manager_statistics(self):
        """测试管理器统计信息"""
        teaching_agent = MockTeachingAgent(AgentType.TEACHING_ANALYSIS)
        learning_agent = MockTeachingAgent(AgentType.LEARNING_STATUS)
        
        self.manager.register_agent(AgentType.TEACHING_ANALYSIS, teaching_agent)
        self.manager.register_agent(AgentType.LEARNING_STATUS, learning_agent)
        
        # 提交一些任务
        task1 = AgentTask(task_id="task_001", task_type="analysis", input_data={})
        task2 = AgentTask(task_id="task_002", task_type="analysis", input_data={})
        
        self.manager.submit_task(AgentType.TEACHING_ANALYSIS, task1)
        self.manager.submit_task(AgentType.LEARNING_STATUS, task2)
        
        # 检查统计信息
        stats = self.manager.get_statistics()
        
        assert isinstance(stats, dict)
        assert "total_agents" in stats
        assert "total_tasks_processed" in stats
        assert stats["total_agents"] == 2
        assert stats["total_tasks_processed"] >= 2
    
    def test_manager_with_custom_config(self):
        """测试自定义配置的管理器"""
        custom_config = {
            "max_concurrent_tasks": 10,
            "task_timeout": 30,
            "retry_attempts": 5
        }
        
        manager = AgentManager(config=custom_config)
        
        assert manager.config["max_concurrent_tasks"] == 10
        assert manager.config["task_timeout"] == 30
        assert manager.config["retry_attempts"] == 5
    
    def test_unregister_agent(self):
        """测试注销智能体"""
        agent = MockTeachingAgent(AgentType.TEACHING_ANALYSIS)
        self.manager.register_agent(AgentType.TEACHING_ANALYSIS, agent)
        
        # 确认智能体已注册
        assert AgentType.TEACHING_ANALYSIS in self.manager.agents
        
        # 注销智能体
        success = self.manager.unregister_agent(AgentType.TEACHING_ANALYSIS)
        
        assert success is True
        assert AgentType.TEACHING_ANALYSIS not in self.manager.agents
        
        # 尝试注销不存在的智能体
        success = self.manager.unregister_agent(AgentType.CLASSROOM_AI)
        assert success is False
    
    def test_clear_all_agents(self):
        """测试清除所有智能体"""
        teaching_agent = MockTeachingAgent(AgentType.TEACHING_ANALYSIS)
        learning_agent = MockTeachingAgent(AgentType.LEARNING_STATUS)
        
        self.manager.register_agent(AgentType.TEACHING_ANALYSIS, teaching_agent)
        self.manager.register_agent(AgentType.LEARNING_STATUS, learning_agent)
        
        assert len(self.manager.agents) == 2
        
        # 清除所有智能体
        self.manager.clear_all_agents()
        
        assert len(self.manager.agents) == 0
        assert len(self.manager.get_available_agents()) == 0
    
    def test_agent_health_check(self):
        """测试智能体健康检查"""
        agent = MockTeachingAgent(AgentType.TUTORING_PLAN)
        self.manager.register_agent(AgentType.TUTORING_PLAN, agent)
        
        # 健康的智能体
        health_status = self.manager.check_agent_health(AgentType.TUTORING_PLAN)
        assert health_status["status"] == "healthy"
        assert health_status["agent_type"] == AgentType.TUTORING_PLAN.value
        
        # 不存在的智能体
        health_status = self.manager.check_agent_health(AgentType.CLASSROOM_AI)
        assert health_status["status"] == "not_found"


if __name__ == "__main__":
    pytest.main([__file__])