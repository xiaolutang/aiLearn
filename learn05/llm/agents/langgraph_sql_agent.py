# -*- coding: utf-8 -*-
"""
基于LangGraph的SQL代理实现
使用LangGraph工作流将自然语言转换为SQL查询，执行查询并返回结果
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel

from langgraph.graph import StateGraph as Graph
from llm.agents.sql_agent import SQLAgent
from sql_connect import DatabaseManager
from config.core_config import get_db_url

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowState(BaseModel):
    """
    LangGraph工作流状态模型
    """
    natural_language: str
    sql_query: str = ""
    result: str = ""
    explanation: str = ""


class LangGraphSQLAgent(SQLAgent):
    """基于LangGraph的SQL代理实现"""
    
    def __init__(self, llm_client):
        """初始化LangGraph SQL代理
        
        Args:
            llm_client: 大模型客户端
        """
        # 创建数据库管理器
        db_url = get_db_url()
        db_manager = DatabaseManager(db_url)
        
        # 调用父类初始化
        super().__init__(llm_client, db_manager)
        
        # 创建LangGraph工作流
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        """创建LangGraph工作流"""
        # 初始化工作流图
        workflow = Graph(state_schema=WorkflowState)
        
        # 添加工作流节点
        workflow.add_node('nlp_to_sql', self._nlp_to_sql_node)
        workflow.add_node('execute_sql', self._execute_sql_node)
        workflow.add_node('explain_result', self._explain_result_node)
        
        # 设置工作流边和入口/出口点
        workflow.set_entry_point('nlp_to_sql')
        workflow.add_edge('nlp_to_sql', 'execute_sql')
        workflow.add_edge('execute_sql', 'explain_result')
        workflow.set_finish_point('explain_result')
        
        # 编译工作流
        return workflow.compile()
    
    def _nlp_to_sql_node(self, state: WorkflowState) -> WorkflowState:
        """自然语言转SQL节点"""
        try:
            # 使用父类的方法将自然语言转换为SQL
            sql_query = self.nlp_to_sql(state.natural_language)
            
            # 返回更新后的状态
            return WorkflowState(
                natural_language=state.natural_language,
                sql_query=sql_query,
                result=state.result,
                explanation=state.explanation
            )
        except Exception as e:
            logger.error(f"自然语言转SQL节点失败: {e}")
            # 如果出错，返回包含错误信息的状态
            return WorkflowState(
                natural_language=state.natural_language,
                sql_query=f"错误: {str(e)}",
                result="",
                explanation="处理失败"
            )
    
    def _execute_sql_node(self, state: WorkflowState) -> WorkflowState:
        """执行SQL节点"""
        # 如果之前的步骤已经出错，直接传递状态
        if state.sql_query.startswith("错误:"):
            return state
        
        try:
            # 使用父类的方法执行SQL查询
            result = self.execute_sql(state.sql_query)
            
            # 将结果转换为字符串格式，便于传递
            result_str = str(result)
            
            # 返回更新后的状态
            return WorkflowState(
                natural_language=state.natural_language,
                sql_query=state.sql_query,
                result=result_str,
                explanation=state.explanation
            )
        except Exception as e:
            logger.error(f"执行SQL节点失败: {e}")
            # 如果出错，返回包含错误信息的状态
            return WorkflowState(
                natural_language=state.natural_language,
                sql_query=state.sql_query,
                result=f"错误: {str(e)}",
                explanation="处理失败"
            )
    
    def _explain_result_node(self, state: WorkflowState) -> WorkflowState:
        """解释结果节点"""
        # 如果之前的步骤已经出错，直接传递状态
        if state.result.startswith("错误:") or state.sql_query.startswith("错误:"):
            return state
        
        try:
            # 使用父类的方法解释查询结果
            explanation = self.explain_result(state.sql_query, state.result)
            
            # 返回更新后的状态
            return WorkflowState(
                natural_language=state.natural_language,
                sql_query=state.sql_query,
                result=state.result,
                explanation=explanation
            )
        except Exception as e:
            logger.error(f"解释结果节点失败: {e}")
            # 如果出错，返回包含错误信息的状态
            return WorkflowState(
                natural_language=state.natural_language,
                sql_query=state.sql_query,
                result=state.result,
                explanation=f"错误: {str(e)}"
            )
    
    def run(self, natural_language: str) -> Dict[str, Any]:
        """运行完整的SQL代理流程
        
        Args:
            natural_language: 自然语言查询
            
        Returns:
            Dict[str, Any]: 包含SQL查询、结果和解释的字典
        """
        try:
            # 运行LangGraph工作流
            result = self.workflow.invoke({'natural_language': natural_language})
            
            # 将结果转换为字典格式返回
            if isinstance(result, dict):
                return result
            elif hasattr(result, '__dict__'):
                return result.__dict__
            else:
                # 处理可能的其他返回类型
                return {
                    "natural_language": natural_language,
                    "sql_query": getattr(result, 'sql_query', ''),
                    "result": getattr(result, 'result', ''),
                    "explanation": getattr(result, 'explanation', '')
                }
        except Exception as e:
            logger.error(f"SQL代理运行失败: {e}")
            raise