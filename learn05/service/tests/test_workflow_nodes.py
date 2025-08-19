"""
服务端工作流节点函数的单元测试
"""
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from io import StringIO
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from learn05.service.workflow_nodes import nlp_to_sql, execute_sql, explain_result
from learn05.service.state import WorkflowState
from learn05.service.database import Base

# 创建测试数据库引擎
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 立即创建所有表
Base.metadata.create_all(bind=test_engine)

class TestWorkflowNodes(unittest.TestCase):
    """工作流节点函数的单元测试类"""

    def setUp(self):
        """测试前的准备工作"""
        # 模拟环境变量
        self.env_patch = patch.dict('os.environ', {
            'LLM_MODEL': 'gpt-3.5-turbo',
            'LLM_API_KEY': 'test_api_key'
        })
        self.env_patch.start()
        
        # 模拟db_manager，使用完整的模块路径
        self.db_patch = patch('learn05.service.workflow_nodes.db_manager')
        self.mock_db_manager = self.db_patch.start()
        
        # 模拟查询结果
        test_data = 'id,name,age\n1,张三,18\n2,李四,19'
        self.mock_db_manager.run_query.return_value = test_data

    def tearDown(self):
        """测试后的清理工作"""
        self.env_patch.stop()
        self.db_patch.stop()

    @patch('learn05.service.workflow_nodes.get_table_structure')
    @patch('learn05.service.workflow_nodes.OpenAI')
    @patch.dict('learn05.service.workflow_nodes.llm_config', {'api_key': 'test_api_key'})
    def test_nlp_to_sql(self, mock_openai, mock_get_table_structure):
        """测试自然语言转SQL函数"""
        # 配置mock
        mock_response = MagicMock()
        mock_response.choices[0].message.content.strip.return_value = 'SELECT * FROM students'
        mock_openai_instance = mock_openai.return_value
        mock_completions = mock_openai_instance.chat.completions
        mock_completions.create.return_value = mock_response
        mock_get_table_structure.return_value = 'students表包含id、name、age等字段'

        # 测试函数
        state = WorkflowState(natural_language='查询所有学生信息')
        result = nlp_to_sql(state)

        # 验证结果
        self.assertEqual(result.sql_query, 'SELECT * FROM students')
        self.assertEqual(result.natural_language, '查询所有学生信息')

    def test_execute_sql(self):
        """测试执行SQL函数"""
        # 测试函数
        state = WorkflowState(natural_language='查询所有学生信息', sql_query='SELECT * FROM students')
        result = execute_sql(state)

        # 验证结果
        self.assertEqual(result.sql_query, 'SELECT * FROM students')
        self.assertEqual(result.natural_language, '查询所有学生信息')
        self.assertIsInstance(result.result, str)
        self.assertIn('id,name,age', result.result)
        self.assertIn('1,张三,18', result.result)
        self.assertIn('2,李四,19', result.result)

    @patch('learn05.service.workflow_nodes.OpenAI')
    @patch.dict('learn05.service.workflow_nodes.llm_config', {'api_key': 'test_api_key'})
    def test_explain_result(self, mock_openai):
        """测试解释结果函数"""
        # 配置mock
        mock_response = MagicMock()
        mock_response.choices[0].message.content.strip.return_value = '查询结果显示有2名学生，分别是张三(18岁)和李四(19岁)。'
        mock_openai_instance = mock_openai.return_value
        mock_completions = mock_openai_instance.chat.completions
        mock_completions.create.return_value = mock_response

        # 测试函数
        state = WorkflowState(
            natural_language='查询所有学生信息',
            sql_query='SELECT * FROM students',
            result='id,name,age\n1,张三,18\n2,李四,19'
        )
        result = explain_result(state)

        # 验证结果
        self.assertEqual(result.sql_query, 'SELECT * FROM students')
        self.assertIsInstance(result.result, str)
        self.assertEqual(result.explanation, '查询结果显示有2名学生，分别是张三(18岁)和李四(19岁)。')

if __name__ == '__main__':
    unittest.main()