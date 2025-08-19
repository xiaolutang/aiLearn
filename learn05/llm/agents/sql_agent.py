# -*- coding: utf-8 -*-
"""
SQL代理模块
提供将自然语言转换为SQL查询并执行的功能
"""

import logging
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLAgent(ABC):
    """SQL代理抽象类"""
    
    @abstractmethod
    def nlp_to_sql(self, natural_language: str) -> str:
        """将自然语言转换为SQL查询
        
        Args:
            natural_language: 自然语言查询
            
        Returns:
            str: SQL查询语句
        """
        pass
    
    @abstractmethod
    def execute_sql(self, sql_query: str) -> Any:
        """执行SQL查询
        
        Args:
            sql_query: SQL查询语句
            
        Returns:
            Any: 查询结果
        """
        pass
    
    @abstractmethod
    def explain_result(self, sql_query: str, result: Any) -> str:
        """解释查询结果
        
        Args:
            sql_query: SQL查询语句
            result: 查询结果
            
        Returns:
            str: 结果解释
        """
        pass
    
    @abstractmethod
    def run(self, natural_language: str) -> Dict[str, Any]:
        """运行完整的SQL代理流程
        
        Args:
            natural_language: 自然语言查询
            
        Returns:
            Dict[str, Any]: 包含SQL查询、结果和解释的字典
        """
        pass


class BasicSQLAgent(SQLAgent):
    """基础SQL代理实现"""
    
    def __init__(self, llm_client, db_manager):
        """\初始化SQL代理
        
        Args:
            llm_client: 大模型客户端
            db_manager: 数据库管理器
        """
        self.llm_client = llm_client
        self.db_manager = db_manager
    
    def get_table_structure(self) -> str:
        """获取数据库表结构信息
        
        Returns:
            str: 表结构描述字符串
        """
        # 默认获取所有表的结构
        tables = ['students', 'classes', 'teachers', 'subjects', 'grades', 'courses', 'attendance', 'class_performance']
        
        # 使用数据库管理器获取表信息
        if hasattr(self.db_manager, 'get_table_info'):
            return self.db_manager.get_table_info(tables)
        
        # 如果数据库管理器没有提供get_table_info方法，返回一个默认的表结构描述
        return "数据库表结构信息获取失败"
    
    def nlp_to_sql(self, natural_language: str) -> str:
        """将自然语言转换为SQL查询"""
        logger.info(f"将自然语言转换为SQL: {natural_language}")
        
        # 获取表结构信息
        table_info = self.get_table_structure()
        
        # 构造提示词
        prompt = f"""
        你是一个SQL查询专家。请根据以下表结构，将自然语言查询转换为SQL查询:
        {table_info}
        自然语言查询: {natural_language}
        请仅返回SQL查询语句，不要包含其他解释。
        """
        
        # 调用大模型生成SQL
        try:
            sql_query = self.llm_client.generate(prompt)
            logger.info(f"生成的SQL: {sql_query}")
            return sql_query
        except Exception as e:
            logger.error(f"转换SQL时出错: {e}")
            raise
    
    def execute_sql(self, sql_query: str) -> Any:
        """执行SQL查询"""
        logger.info(f"执行SQL查询: {sql_query}")
        
        # 使用数据库管理器执行查询
        try:
            if hasattr(self.db_manager, 'execute_query'):
                result = self.db_manager.execute_query(sql_query)
                return result
            else:
                raise ValueError("数据库管理器没有execute_query方法")
        except Exception as e:
            logger.error(f"执行SQL查询时出错: {e}")
            raise
    
    def explain_result(self, sql_query: str, result: Any) -> str:
        """解释查询结果"""
        logger.info(f"解释SQL查询结果")
        
        # 构造提示词，让大模型解释结果
        prompt = f"""
        你是一个数据分析专家。请根据以下SQL查询和结果，给出清晰的解释:
        SQL查询: {sql_query}
        查询结果: {result}
        请用简洁明了的语言解释查询结果，避免使用技术术语。
        """
        
        try:
            explanation = self.llm_client.generate(prompt)
            logger.info(f"生成的结果解释: {explanation}")
            return explanation
        except Exception as e:
            logger.error(f"解释结果时出错: {e}")
            raise
    
    def run(self, natural_language: str) -> Dict[str, Any]:
        """运行完整的SQL代理流程"""
        try:
            # 1. 将自然语言转换为SQL
            sql_query = self.nlp_to_sql(natural_language)
            
            # 2. 执行SQL查询
            result = self.execute_sql(sql_query)
            
            # 3. 解释查询结果
            explanation = self.explain_result(sql_query, result)
            
            # 返回完整结果
            return {
                "natural_language": natural_language,
                "sql_query": sql_query,
                "result": result,
                "explanation": explanation
            }
        except Exception as e:
            logger.error(f"SQL代理运行失败: {e}")
            raise