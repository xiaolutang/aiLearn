# -*- coding: utf-8 -*-
"""
智能教学助手智能体模块
提供教材分析、学情分析、辅导方案生成、课堂AI助手等功能
"""

from .base_agent import (
    BaseTeachingAgent,
    AgentType,
    AgentTask,
    AgentResponse,
    TaskPriority
)

from .teaching_analysis_agent import TeachingAnalysisAgent
from .learning_status_agent import LearningStatusAgent
from .tutoring_agent import TutoringAgent
from .classroom_ai_agent import ClassroomAIAgent
from .agent_manager import AgentManager

__all__ = [
    # 基础类和枚举
    'BaseTeachingAgent',
    'AgentType',
    'AgentTask',
    'AgentResponse',
    'TaskPriority',
    
    # 具体智能体
    'TeachingAnalysisAgent',
    'LearningStatusAgent',
    'TutoringAgent',
    'ClassroomAIAgent',
    
    # 管理器
    'AgentManager'
]

# 版本信息
__version__ = '1.0.0'
__author__ = 'AI Teaching Assistant Team'
__description__ = '智能教学助手智能体模块，提供全方位的教学AI支持'

# 模块级别的便捷函数
def create_agent_manager(llm_client=None, config=None):
    """
    创建智能体管理器的便捷函数
    
    Args:
        llm_client: 大模型客户端
        config: 配置信息
        
    Returns:
        AgentManager: 智能体管理器实例
    """
    return AgentManager(llm_client=llm_client, config=config)

def get_available_agent_types():
    """
    获取可用的智能体类型
    
    Returns:
        List[AgentType]: 智能体类型列表
    """
    return list(AgentType)

def get_agent_descriptions():
    """
    获取智能体描述信息
    
    Returns:
        Dict[str, str]: 智能体描述字典
    """
    return {
        AgentType.TEACHING_ANALYSIS.value: "教材分析智能体 - 提供教材内容分析、知识点识别、重点难点分析等功能",
        AgentType.LEARNING_STATUS.value: "学情分析智能体 - 提供学生学习情况分析、成绩趋势分析、薄弱环节识别等功能",
        AgentType.TUTORING.value: "辅导方案生成智能体 - 提供个性化学习辅导方案生成、练习题推荐、学习计划制定等功能",
        AgentType.CLASSROOM_AI.value: "课堂AI助手智能体 - 提供实时学情分析、课堂互动内容生成、教学建议等功能"
    }