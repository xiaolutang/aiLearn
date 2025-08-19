# -*- coding: utf-8 -*-
"""
LangGraph SQL智能体单元测试
测试LangGraphSQLAgent的工作流编排和状态管理功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from llm.agents.langgraph_sql_agent import LangGraphSQLAgent
from llm.agents.base_agent import (
    AgentType,
    AgentTask,
    AgentResponse,
    TaskPriority
)
from test_config import (
    create_mock_llm_client,
    create_mock_db_manager,
    TEST_CONFIG,
    MOCK_STUDENT_DATA,
    MOCK_GRADE_DATA,
    MOCK_LLM_RESPONSES,
    assert_response_valid
)


class TestLangGraphSQLAgent:
    """测试LangGraphSQLAgent类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.mock_db_manager = create_mock_db_manager()
        
        self.agent = LangGraphSQLAgent(
            llm_client=self.mock_llm_client,
            db_manager=self.mock_db_manager,
            config=TEST_CONFIG
        )
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        assert self.agent.llm_client == self.mock_llm_client
        assert self.agent.db_manager == self.mock_db_manager
        assert isinstance(self.agent.config, dict)
        
        # 检查LangGraph特定配置
        assert "workflow" in self.agent.config
        assert "state_management" in self.agent.config
        assert "node_timeout" in self.agent.config
        assert "max_retries" in self.agent.config
        
        # 检查工作流是否已创建
        assert hasattr(self.agent, 'workflow')
        assert self.agent.workflow is not None
    
    def test_workflow_graph_structure(self):
        """测试工作流图结构"""
        # 检查工作流节点
        workflow_nodes = self.agent.workflow.get_graph().nodes
        expected_nodes = [
            "nlp_to_sql",
            "execute_sql", 
            "explain_result",
            "__start__",
            "__end__"
        ]
        
        for node in expected_nodes:
            assert node in workflow_nodes
        
        # 检查工作流边
        workflow_edges = self.agent.workflow.get_graph().edges
        assert len(workflow_edges) > 0
    
    def test_nlp_to_sql_node(self):
        """测试自然语言转SQL节点"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_query_simple"]
        
        # 创建初始状态
        state = {
            "natural_language_query": "查询所有学生的姓名和年龄",
            "table_schema": {
                "students": {
                    "columns": ["id", "name", "age", "class_id"],
                    "types": ["INTEGER", "TEXT", "INTEGER", "INTEGER"]
                }
            },
            "sql_query": None,
            "execution_results": None,
            "explanation": None,
            "errors": []
        }
        
        # 调用节点函数
        updated_state = self.agent._nlp_to_sql_node(state)
        
        # 验证状态更新
        assert "sql_query" in updated_state
        assert updated_state["sql_query"] is not None
        assert "SELECT" in updated_state["sql_query"].upper()
        assert "name" in updated_state["sql_query"].lower()
        assert "age" in updated_state["sql_query"].lower()
        
        # 验证LLM客户端被调用
        self.mock_llm_client.generate_response.assert_called_once()
    
    def test_execute_sql_node(self):
        """测试执行SQL节点"""
        # 设置数据库管理器返回结果
        mock_results = [
            {"name": "张三", "age": 16},
            {"name": "李四", "age": 17},
            {"name": "王五", "age": 16}
        ]
        self.mock_db_manager.execute_query.return_value = mock_results
        
        # 创建包含SQL查询的状态
        state = {
            "natural_language_query": "查询所有学生的姓名和年龄",
            "sql_query": "SELECT name, age FROM students",
            "execution_results": None,
            "explanation": None,
            "errors": []
        }
        
        # 调用节点函数
        updated_state = self.agent._execute_sql_node(state)
        
        # 验证状态更新
        assert "execution_results" in updated_state
        assert updated_state["execution_results"] is not None
        
        results = updated_state["execution_results"]
        assert "data" in results
        assert "row_count" in results
        assert "execution_time" in results
        
        # 验证查询结果
        assert len(results["data"]) == 3
        assert results["data"][0]["name"] == "张三"
        assert results["row_count"] == 3
        
        # 验证数据库管理器被调用
        self.mock_db_manager.execute_query.assert_called_once_with(
            "SELECT name, age FROM students"
        )
    
    def test_explain_result_node(self):
        """测试解释结果节点"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_explanation"]
        
        # 创建包含执行结果的状态
        state = {
            "natural_language_query": "查询所有学生的姓名和年龄",
            "sql_query": "SELECT name, age FROM students",
            "execution_results": {
                "data": [
                    {"name": "张三", "age": 16},
                    {"name": "李四", "age": 17}
                ],
                "row_count": 2,
                "execution_time": 0.05
            },
            "explanation": None,
            "errors": []
        }
        
        # 调用节点函数
        updated_state = self.agent._explain_result_node(state)
        
        # 验证状态更新
        assert "explanation" in updated_state
        assert updated_state["explanation"] is not None
        
        explanation = updated_state["explanation"]
        assert "summary" in explanation
        assert "insights" in explanation
        assert "recommendations" in explanation
        
        # 验证LLM客户端被调用
        self.mock_llm_client.generate_response.assert_called()
    
    def test_complete_workflow_execution(self):
        """测试完整工作流执行"""
        # 设置模拟响应
        self.mock_llm_client.generate_response.side_effect = [
            MOCK_LLM_RESPONSES["sql_query_simple"],  # NLP to SQL
            MOCK_LLM_RESPONSES["sql_explanation"]    # Explain results
        ]
        
        mock_results = [
            {"name": "张三", "age": 16},
            {"name": "李四", "age": 17}
        ]
        self.mock_db_manager.execute_query.return_value = mock_results
        
        task = AgentTask(
            task_id="workflow_001",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "查询所有学生的姓名和年龄",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age", "class_id"],
                        "types": ["INTEGER", "TEXT", "INTEGER", "INTEGER"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert_response_valid(response, ["success", "data", "message"])
        assert response.success is True
        
        # 检查完整工作流结果
        workflow_data = response.data
        assert "sql_query" in workflow_data
        assert "execution_results" in workflow_data
        assert "explanation" in workflow_data
        assert "workflow_state" in workflow_data
        
        # 验证SQL查询
        assert "SELECT" in workflow_data["sql_query"].upper()
        
        # 验证执行结果
        execution_results = workflow_data["execution_results"]
        assert "data" in execution_results
        assert len(execution_results["data"]) == 2
        
        # 验证解释
        explanation = workflow_data["explanation"]
        assert "summary" in explanation
    
    def test_workflow_with_complex_query(self):
        """测试复杂查询的工作流"""
        # 设置模拟响应
        self.mock_llm_client.generate_response.side_effect = [
            MOCK_LLM_RESPONSES["sql_query_complex"],  # NLP to SQL
            MOCK_LLM_RESPONSES["sql_explanation"]     # Explain results
        ]
        
        mock_results = [
            {"name": "张三", "score": 98},
            {"name": "李四", "score": 96},
            {"name": "王五", "score": 95}
        ]
        self.mock_db_manager.execute_query.return_value = mock_results
        
        task = AgentTask(
            task_id="workflow_002",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "查询数学成绩大于90分的学生姓名，按成绩降序排列",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age", "class_id"],
                        "types": ["INTEGER", "TEXT", "INTEGER", "INTEGER"]
                    },
                    "grades": {
                        "columns": ["id", "student_id", "subject", "score", "exam_date"],
                        "types": ["INTEGER", "INTEGER", "TEXT", "REAL", "DATE"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        workflow_data = response.data
        
        # 验证复杂查询的SQL
        sql_query = workflow_data["sql_query"]
        assert "JOIN" in sql_query.upper() or "WHERE" in sql_query.upper()
        assert "score > 90" in sql_query or "score>90" in sql_query
        assert "ORDER BY" in sql_query.upper()
    
    def test_workflow_error_handling(self):
        """测试工作流错误处理"""
        # 设置LLM客户端抛出异常
        self.mock_llm_client.generate_response.side_effect = Exception("LLM服务不可用")
        
        task = AgentTask(
            task_id="workflow_003",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "查询所有学生",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name"],
                        "types": ["INTEGER", "TEXT"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "LLM服务不可用" in response.message
        assert response.error_code == "WORKFLOW_ERROR"
        
        # 检查错误状态
        if "workflow_state" in response.data:
            workflow_state = response.data["workflow_state"]
            assert "errors" in workflow_state
            assert len(workflow_state["errors"]) > 0
    
    def test_workflow_database_error(self):
        """测试工作流数据库错误"""
        # 设置正常的LLM响应
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_query_simple"]
        
        # 设置数据库管理器抛出异常
        self.mock_db_manager.execute_query.side_effect = Exception("数据库连接失败")
        
        task = AgentTask(
            task_id="workflow_004",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "查询所有学生",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name"],
                        "types": ["INTEGER", "TEXT"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "数据库连接失败" in response.message
        assert response.error_code == "WORKFLOW_ERROR"
    
    def test_workflow_state_persistence(self):
        """测试工作流状态持久化"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_query_simple"]
        
        mock_results = [{"name": "张三", "age": 16}]
        self.mock_db_manager.execute_query.return_value = mock_results
        
        task = AgentTask(
            task_id="workflow_005",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "查询学生信息",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age"],
                        "types": ["INTEGER", "TEXT", "INTEGER"]
                    }
                },
                "persist_state": True
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        
        # 检查状态持久化
        workflow_data = response.data
        assert "workflow_state" in workflow_data
        
        workflow_state = workflow_data["workflow_state"]
        assert "natural_language_query" in workflow_state
        assert "sql_query" in workflow_state
        assert "execution_results" in workflow_state
        assert "step_history" in workflow_state
    
    def test_workflow_retry_mechanism(self):
        """测试工作流重试机制"""
        # 设置第一次调用失败，第二次成功
        self.mock_llm_client.generate_response.side_effect = [
            Exception("临时网络错误"),
            MOCK_LLM_RESPONSES["sql_query_simple"]
        ]
        
        mock_results = [{"name": "张三", "age": 16}]
        self.mock_db_manager.execute_query.return_value = mock_results
        
        # 配置重试
        retry_config = TEST_CONFIG.copy()
        retry_config["max_retries"] = 2
        retry_config["retry_delay"] = 0.1
        
        agent = LangGraphSQLAgent(
            llm_client=self.mock_llm_client,
            db_manager=self.mock_db_manager,
            config=retry_config
        )
        
        task = AgentTask(
            task_id="workflow_006",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "查询学生信息",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age"],
                        "types": ["INTEGER", "TEXT", "INTEGER"]
                    }
                }
            }
        )
        
        response = agent.process_task(task)
        
        # 重试后应该成功
        assert response.success is True
        
        # 验证LLM客户端被调用了两次（第一次失败，第二次成功）
        assert self.mock_llm_client.generate_response.call_count >= 2
    
    def test_workflow_timeout_handling(self):
        """测试工作流超时处理"""
        # 设置超时配置
        timeout_config = TEST_CONFIG.copy()
        timeout_config["node_timeout"] = 0.001  # 1毫秒超时
        
        # 模拟慢响应
        def slow_response(*args, **kwargs):
            import time
            time.sleep(0.1)  # 100毫秒延迟
            return MOCK_LLM_RESPONSES["sql_query_simple"]
        
        self.mock_llm_client.generate_response.side_effect = slow_response
        
        agent = LangGraphSQLAgent(
            llm_client=self.mock_llm_client,
            db_manager=self.mock_db_manager,
            config=timeout_config
        )
        
        task = AgentTask(
            task_id="workflow_007",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "查询学生信息",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name"],
                        "types": ["INTEGER", "TEXT"]
                    }
                }
            }
        )
        
        response = agent.process_task(task)
        
        # 超时应该导致失败
        assert response.success is False
        assert "超时" in response.message or "timeout" in response.message.lower()
    
    def test_workflow_conditional_routing(self):
        """测试工作流条件路由"""
        # 测试SQL验证失败的情况
        invalid_sql_response = {
            "sql_query": "INVALID SQL SYNTAX",
            "confidence": 0.2,
            "validation_errors": ["语法错误"]
        }
        
        self.mock_llm_client.generate_response.return_value = invalid_sql_response
        
        task = AgentTask(
            task_id="workflow_008",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "无效查询请求",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name"],
                        "types": ["INTEGER", "TEXT"]
                    }
                },
                "validate_sql": True
            }
        )
        
        response = self.agent.process_task(task)
        
        # 应该检测到SQL无效并处理
        assert response.success is False
        assert "SQL验证失败" in response.message or "语法错误" in response.message
    
    def test_get_capabilities(self):
        """测试获取智能体能力"""
        capabilities = self.agent.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_tasks" in capabilities
        assert "workflow_features" in capabilities
        assert "state_management" in capabilities
        
        # 检查工作流特性
        workflow_features = capabilities["workflow_features"]
        assert "graph_execution" in workflow_features
        assert "state_persistence" in workflow_features
        assert "error_recovery" in workflow_features
        assert "conditional_routing" in workflow_features
    
    def test_custom_workflow_config(self):
        """测试自定义工作流配置"""
        custom_config = {
            "workflow": {
                "enable_parallel_execution": True,
                "checkpoint_frequency": "every_node",
                "state_compression": True
            },
            "state_management": {
                "memory_limit": "100MB",
                "persistence_backend": "memory",
                "cleanup_policy": "auto"
            },
            "node_timeout": 30.0,
            "max_retries": 3,
            "retry_delay": 1.0
        }
        
        agent = LangGraphSQLAgent(
            llm_client=self.mock_llm_client,
            db_manager=self.mock_db_manager,
            config=custom_config
        )
        
        assert agent.config["workflow"]["enable_parallel_execution"] is True
        assert agent.config["state_management"]["memory_limit"] == "100MB"
        assert agent.config["node_timeout"] == 30.0
        assert agent.config["max_retries"] == 3
    
    def test_workflow_performance_metrics(self):
        """测试工作流性能指标"""
        self.mock_llm_client.generate_response.side_effect = [
            MOCK_LLM_RESPONSES["sql_query_simple"],
            MOCK_LLM_RESPONSES["sql_explanation"]
        ]
        
        mock_results = [{"name": "张三", "age": 16}]
        self.mock_db_manager.execute_query.return_value = mock_results
        
        task = AgentTask(
            task_id="workflow_009",
            task_type="nl_to_sql_workflow",
            input_data={
                "query": "查询学生信息",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age"],
                        "types": ["INTEGER", "TEXT", "INTEGER"]
                    }
                },
                "collect_metrics": True
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        assert response.processing_time is not None
        
        # 检查性能指标
        if "performance_metrics" in response.data:
            metrics = response.data["performance_metrics"]
            assert "total_execution_time" in metrics
            assert "node_execution_times" in metrics
            assert "state_transitions" in metrics
            
            node_times = metrics["node_execution_times"]
            assert "nlp_to_sql" in node_times
            assert "execute_sql" in node_times
            assert "explain_result" in node_times


if __name__ == "__main__":
    pytest.main([__file__])