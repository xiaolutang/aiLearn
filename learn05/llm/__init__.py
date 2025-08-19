#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM模块 - 智能教学助手的大语言模型集成模块

本模块提供了完整的LLM集成功能，包括：
- 多种LLM客户端支持（OpenAI、通义千问等）
- 智能教学代理（教材分析、学情分析、辅导方案生成等）
- 上下文管理和会话状态保持
- 性能优化和缓存机制
- 提示词模板管理
"""

__version__ = "1.0.0"
__author__ = "智能教学助手开发团队"

# 导入核心类和函数
try:
    # 新的统一架构
    from .unified_interface import (
        LLMProvider,
        LLMRequest,
        LLMResponse,
        LLMUsage,
        LLMException,
        LLMRateLimitException,
        LLMQuotaExceededException,
        LLMServiceUnavailableException,
        LLMTimeoutException,
        LLMAuthenticationException,
        LLMValidationException
    )
    
    from .manager import (
        LLMManager,
        get_llm_manager,
        generate_text,
        chat_completion,
        stream_text,
        stream_chat_completion
    )
    
    from .factory import (
        LLMFactory,
        get_llm_client,
        get_unified_llm_client,
        get_global_llm_client
    )
    
    from .config import (
        get_llm_config,
        get_config_manager
    )
    
    from .monitoring import (
        get_performance_monitor,
        record_llm_request
    )
    
    # 兼容旧的接口
    try:
        from .base import LLMInterface, LLMRateLimiter, LLMRetryHandler
        from .openai_client import OpenAIClient
        from .client_factory import LLMClientFactory
    except ImportError:
        pass
    
    # 导入智能体
    try:
        from .agents.teaching_analysis_agent import TeachingAnalysisAgent
        from .agents.learning_status_agent import LearningStatusAgent
        from .agents.tutoring_agent import TutoringAgent
        from .agents.agent_manager import AgentManager
    except ImportError:
        pass
    
    # 导入工具函数
    try:
        from .llm_utils import (
            format_prompt,
            validate_response,
            parse_json_response,
            calculate_tokens,
            format_messages,
            extract_content,
            handle_api_error
        )
    except ImportError:
        pass
    
    __all__ = [
        # 新的统一架构
        'LLMProvider',
        'LLMRequest',
        'LLMResponse', 
        'LLMUsage',
        'LLMException',
        'LLMRateLimitException',
        'LLMQuotaExceededException',
        'LLMServiceUnavailableException',
        'LLMTimeoutException',
        'LLMAuthenticationException',
        'LLMValidationException',
        
        # 管理器和工厂
        'LLMManager',
        'get_llm_manager',
        'LLMFactory',
        'get_llm_client',
        'get_unified_llm_client',
        'get_global_llm_client',
        
        # 配置和监控
        'get_llm_config',
        'get_config_manager',
        'get_performance_monitor',
        'record_llm_request',
        
        # 便捷函数
        'generate_text',
        'chat_completion',
        'stream_text',
        'stream_chat_completion',
        
        # 兼容旧接口（如果可用）
        'LLMInterface',
        'LLMRateLimiter', 
        'LLMRetryHandler',
        'OpenAIClient',
        'LLMClientFactory',
        
        # 智能体（如果可用）
        'TeachingAnalysisAgent',
        'LearningStatusAgent', 
        'TutoringAgent',
        'AgentManager',
        
        # 工具函数（如果可用）
        'format_prompt',
        'validate_response',
        'parse_json_response',
        'calculate_tokens',
        'format_messages',
        'extract_content',
        'handle_api_error'
    ]
    
except ImportError as e:
    # 如果某些模块导入失败，提供基本的错误信息
    import warnings
    warnings.warn(f"LLM模块部分功能不可用: {e}", ImportWarning)
    
    __all__ = []

# 模块信息
def get_version():
    """获取模块版本"""
    return __version__

def get_available_agents():
    """获取可用的智能体列表"""
    agents = []
    try:
        from .agents.teaching_analysis_agent import TeachingAnalysisAgent
        agents.append('TeachingAnalysisAgent')
    except ImportError:
        pass
    
    try:
        from .agents.learning_status_agent import LearningStatusAgent
        agents.append('LearningStatusAgent')
    except ImportError:
        pass
    
    try:
        from .agents.tutoring_agent import TutoringAgent
        agents.append('TutoringAgent')
    except ImportError:
        pass
    
    try:
        from .agents.agent_manager import AgentManager
        agents.append('AgentManager')
    except ImportError:
        pass
    
    return agents

def get_available_clients():
    """获取可用的LLM客户端列表"""
    clients = []
    try:
        from .openai_client import OpenAIClient
        clients.append('OpenAIClient')
    except ImportError:
        pass
    
    return clients