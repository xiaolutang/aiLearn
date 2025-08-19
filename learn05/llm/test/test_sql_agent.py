# -*- coding: utf-8 -*-
"""
SQL智能体单元测试
测试SQLAgent和BasicSQLAgent的自然语言转SQL功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from llm.agents.sql_agent import SQLAgent, BasicSQLAgent
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


class TestSQLAgent:
    """测试SQLAgent抽象基类"""
    
    def test_sql_agent_is_abstract(self):
        """测试SQLAgent是抽象类"""
        with pytest.raises(TypeError):
            SQLAgent()
    
    def test_sql_agent_methods_are_abstract(self):
        """测试SQLAgent的抽象方法"""
        # 创建一个不完整的子类
        class IncompleteSQLAgent(SQLAgent):
            pass
        
        with pytest.raises(TypeError):
            IncompleteSQLAgent()


class TestBasicSQLAgent:
    """测试BasicSQLAgent类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.mock_db_manager = create_mock_db_manager()
        
        self.agent = BasicSQLAgent(
            llm_client=self.mock_llm_client,
            db_manager=self.mock_db_manager,
            config=TEST_CONFIG
        )
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        assert self.agent.llm_client == self.mock_llm_client
        assert self.agent.db_manager == self.mock_db_manager
        assert isinstance(self.agent.config, dict)
        
        # 检查默认配置
        assert "sql_generation" in self.agent.config
        assert "query_validation" in self.agent.config
        assert "result_explanation" in self.agent.config
    
    def test_natural_language_to_sql_simple_query(self):
        """测试简单自然语言转SQL"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_query_simple"]
        
        task = AgentTask(
            task_id="sql_001",
            task_type="nl_to_sql",
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
        
        # 检查SQL生成结果
        sql_data = response.data
        assert "sql_query" in sql_data
        assert "explanation" in sql_data
        assert "confidence" in sql_data
        
        # 验证生成的SQL
        sql_query = sql_data["sql_query"]
        assert "SELECT" in sql_query.upper()
        assert "name" in sql_query.lower()
        assert "age" in sql_query.lower()
        assert "students" in sql_query.lower()
    
    def test_natural_language_to_sql_complex_query(self):
        """测试复杂自然语言转SQL"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_query_complex"]
        
        task = AgentTask(
            task_id="sql_002",
            task_type="nl_to_sql",
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
        sql_data = response.data
        
        # 验证复杂查询的SQL
        sql_query = sql_data["sql_query"]
        assert "JOIN" in sql_query.upper() or "WHERE" in sql_query.upper()
        assert "score > 90" in sql_query or "score>90" in sql_query
        assert "ORDER BY" in sql_query.upper()
        assert "DESC" in sql_query.upper()
    
    def test_execute_sql_query(self):
        """测试执行SQL查询"""
        # 设置数据库管理器返回结果
        mock_results = [
            {"name": "张三", "age": 16},
            {"name": "李四", "age": 17},
            {"name": "王五", "age": 16}
        ]
        self.mock_db_manager.execute_query.return_value = mock_results
        
        task = AgentTask(
            task_id="sql_003",
            task_type="execute_sql",
            input_data={
                "sql_query": "SELECT name, age FROM students WHERE age >= 16",
                "validate_query": True
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        execution_data = response.data
        
        assert "results" in execution_data
        assert "row_count" in execution_data
        assert "execution_time" in execution_data
        
        # 验证查询结果
        results = execution_data["results"]
        assert len(results) == 3
        assert results[0]["name"] == "张三"
        assert execution_data["row_count"] == 3
        
        # 验证数据库管理器被调用
        self.mock_db_manager.execute_query.assert_called_once_with(
            "SELECT name, age FROM students WHERE age >= 16"
        )
    
    def test_explain_sql_results(self):
        """测试解释SQL结果"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_explanation"]
        
        task = AgentTask(
            task_id="sql_004",
            task_type="explain_results",
            input_data={
                "original_query": "查询数学成绩前10名的学生",
                "sql_query": "SELECT s.name, g.score FROM students s JOIN grades g ON s.id = g.student_id WHERE g.subject = '数学' ORDER BY g.score DESC LIMIT 10",
                "results": [
                    {"name": "张三", "score": 98},
                    {"name": "李四", "score": 96},
                    {"name": "王五", "score": 95}
                ],
                "explanation_level": "详细"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        explanation_data = response.data
        
        assert "explanation" in explanation_data
        assert "summary" in explanation_data
        assert "insights" in explanation_data
        assert "recommendations" in explanation_data
        
        # 检查解释内容
        explanation = explanation_data["explanation"]
        assert "数学成绩" in explanation
        assert "前10名" in explanation or "前十名" in explanation
    
    def test_validate_sql_query(self):
        """测试SQL查询验证"""
        task = AgentTask(
            task_id="sql_005",
            task_type="validate_sql",
            input_data={
                "sql_query": "SELECT name, age FROM students WHERE age > 15",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age", "class_id"],
                        "types": ["INTEGER", "TEXT", "INTEGER", "INTEGER"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        validation_data = response.data
        
        assert "is_valid" in validation_data
        assert "validation_errors" in validation_data
        assert "suggestions" in validation_data
        
        # 有效的SQL应该通过验证
        assert validation_data["is_valid"] is True
        assert len(validation_data["validation_errors"]) == 0
    
    def test_validate_invalid_sql_query(self):
        """测试无效SQL查询验证"""
        task = AgentTask(
            task_id="sql_006",
            task_type="validate_sql",
            input_data={
                "sql_query": "SELECT invalid_column FROM non_existent_table",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age", "class_id"],
                        "types": ["INTEGER", "TEXT", "INTEGER", "INTEGER"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        validation_data = response.data
        
        # 无效的SQL应该被检测出来
        assert validation_data["is_valid"] is False
        assert len(validation_data["validation_errors"]) > 0
        
        errors = validation_data["validation_errors"]
        assert any("invalid_column" in error.lower() for error in errors)
        assert any("non_existent_table" in error.lower() for error in errors)
    
    def test_generate_sql_with_aggregation(self):
        """测试生成聚合查询SQL"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_aggregation"]
        
        task = AgentTask(
            task_id="sql_007",
            task_type="nl_to_sql",
            input_data={
                "query": "统计每个班级的平均成绩和学生人数",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age", "class_id"],
                        "types": ["INTEGER", "TEXT", "INTEGER", "INTEGER"]
                    },
                    "grades": {
                        "columns": ["id", "student_id", "subject", "score", "exam_date"],
                        "types": ["INTEGER", "INTEGER", "TEXT", "REAL", "DATE"]
                    },
                    "classes": {
                        "columns": ["id", "name", "grade_level"],
                        "types": ["INTEGER", "TEXT", "INTEGER"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        sql_data = response.data
        
        sql_query = sql_data["sql_query"]
        assert "AVG" in sql_query.upper() or "AVERAGE" in sql_query.upper()
        assert "COUNT" in sql_query.upper()
        assert "GROUP BY" in sql_query.upper()
    
    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        task = AgentTask(
            task_id="sql_008",
            task_type="validate_sql",
            input_data={
                "sql_query": "SELECT * FROM students WHERE name = 'test'; DROP TABLE students; --'",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age", "class_id"],
                        "types": ["INTEGER", "TEXT", "INTEGER", "INTEGER"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        validation_data = response.data
        
        # 包含SQL注入的查询应该被标记为无效
        assert validation_data["is_valid"] is False
        
        errors = validation_data["validation_errors"]
        assert any("注入" in error or "DROP" in error or "危险" in error for error in errors)
    
    def test_database_connection_error(self):
        """测试数据库连接错误"""
        self.mock_db_manager.execute_query.side_effect = Exception("数据库连接失败")
        
        task = AgentTask(
            task_id="sql_009",
            task_type="execute_sql",
            input_data={
                "sql_query": "SELECT * FROM students"
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "数据库连接失败" in response.message
        assert response.error_code == "DATABASE_ERROR"
    
    def test_llm_client_error(self):
        """测试LLM客户端错误"""
        self.mock_llm_client.generate_response.side_effect = Exception("LLM服务不可用")
        
        task = AgentTask(
            task_id="sql_010",
            task_type="nl_to_sql",
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
        assert response.error_code == "LLM_ERROR"
    
    def test_invalid_task_type(self):
        """测试无效任务类型"""
        task = AgentTask(
            task_id="sql_011",
            task_type="invalid_sql_task",
            input_data={}
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "不支持的任务类型" in response.message
        assert response.error_code == "INVALID_TASK_TYPE"
    
    def test_missing_query_data(self):
        """测试缺少查询数据"""
        task = AgentTask(
            task_id="sql_012",
            task_type="nl_to_sql",
            input_data={
                # 缺少query字段
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
        assert "缺少查询内容" in response.message
        assert response.error_code == "MISSING_QUERY"
    
    def test_missing_table_schema(self):
        """测试缺少表结构"""
        task = AgentTask(
            task_id="sql_013",
            task_type="nl_to_sql",
            input_data={
                "query": "查询所有学生"
                # 缺少table_schema字段
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is False
        assert "缺少表结构信息" in response.message
        assert response.error_code == "MISSING_SCHEMA"
    
    def test_get_capabilities(self):
        """测试获取智能体能力"""
        capabilities = self.agent.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_tasks" in capabilities
        assert "sql_features" in capabilities
        assert "database_support" in capabilities
        
        # 检查支持的任务类型
        supported_tasks = capabilities["supported_tasks"]
        expected_tasks = [
            "nl_to_sql",
            "execute_sql",
            "explain_results",
            "validate_sql"
        ]
        
        for task_type in expected_tasks:
            assert task_type in supported_tasks
    
    def test_custom_sql_config(self):
        """测试自定义SQL配置"""
        custom_config = {
            "sql_generation": {
                "max_query_complexity": "high",
                "allow_subqueries": True,
                "enable_optimization": True
            },
            "query_validation": {
                "strict_mode": True,
                "check_injection": True,
                "validate_syntax": True
            },
            "result_explanation": {
                "detail_level": "comprehensive",
                "include_insights": True,
                "suggest_improvements": True
            }
        }
        
        agent = BasicSQLAgent(
            llm_client=self.mock_llm_client,
            db_manager=self.mock_db_manager,
            config=custom_config
        )
        
        assert agent.config["sql_generation"]["allow_subqueries"] is True
        assert agent.config["query_validation"]["strict_mode"] is True
        assert agent.config["result_explanation"]["detail_level"] == "comprehensive"
    
    def test_batch_sql_queries(self):
        """测试批量SQL查询"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["batch_sql_queries"]
        
        task = AgentTask(
            task_id="sql_014",
            task_type="batch_nl_to_sql",
            input_data={
                "queries": [
                    "查询所有学生的姓名",
                    "统计每个班级的学生人数",
                    "查询数学成绩最高的学生"
                ],
                "table_schema": {
                    "students": {
                        "columns": ["id", "name", "age", "class_id"],
                        "types": ["INTEGER", "TEXT", "INTEGER", "INTEGER"]
                    },
                    "grades": {
                        "columns": ["id", "student_id", "subject", "score"],
                        "types": ["INTEGER", "INTEGER", "TEXT", "REAL"]
                    }
                }
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        batch_results = response.data["batch_results"]
        
        assert isinstance(batch_results, list)
        assert len(batch_results) == 3
        
        # 检查每个查询结果
        for result in batch_results:
            assert "original_query" in result
            assert "sql_query" in result
            assert "explanation" in result
    
    def test_performance_monitoring(self):
        """测试性能监控"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["sql_query_simple"]
        
        task = AgentTask(
            task_id="sql_015",
            task_type="nl_to_sql",
            input_data={
                "query": "查询所有学生",
                "table_schema": {
                    "students": {
                        "columns": ["id", "name"],
                        "types": ["INTEGER", "TEXT"]
                    }
                },
                "monitor_performance": True
            }
        )
        
        response = self.agent.process_task(task)
        
        assert response.success is True
        assert response.processing_time is not None
        assert response.processing_time > 0
        
        # 检查性能指标
        if "performance_metrics" in response.data:
            metrics = response.data["performance_metrics"]
            assert "llm_response_time" in metrics
            assert "sql_generation_time" in metrics


if __name__ == "__main__":
    pytest.main([__file__])