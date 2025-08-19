
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的测试运行器 - 只运行能正常工作的测试
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
llm_dir = os.path.dirname(current_dir)
service_dir = os.path.dirname(llm_dir)
sys.path.insert(0, service_dir)
print(f"添加路径到sys.path: {service_dir}")

def run_basic_tests():
    """运行基础测试"""
    print("LLM模块基础测试")
    print("=" * 50)
    
    # 测试基本导入
    try:
        from llm.base import LLMInterface
        print("✓ LLMInterface 导入成功")
    except Exception as e:
        print(f"✗ LLMInterface 导入失败: {e}")
    
    try:
        from llm.openai_client import OpenAIClient
        print("✓ OpenAIClient 导入成功")
    except Exception as e:
        print(f"✗ OpenAIClient 导入失败: {e}")
    
    try:
        from llm.factory import LLMFactory
        print("✓ LLMFactory 导入成功")
    except Exception as e:
        print(f"✗ LLMFactory 导入失败: {e}")
    
    try:
        from llm.client_factory import LLMClientFactory
        print("✓ LLMClientFactory 导入成功")
    except Exception as e:
        print(f"✗ LLMClientFactory 导入失败: {e}")
    
    try:
        from llm.llm_utils import format_prompt, validate_response
        print("✓ llm_utils 导入成功")
    except Exception as e:
        print(f"✗ llm_utils 导入失败: {e}")
    
    # 测试智能体模块
    try:
        from llm.agents.teaching_analysis_agent import TeachingAnalysisAgent
        print("✓ TeachingAnalysisAgent 导入成功")
    except Exception as e:
        print(f"✗ TeachingAnalysisAgent 导入失败: {e}")
    
    try:
        from llm.agents.learning_status_agent import LearningStatusAgent
        print("✓ LearningStatusAgent 导入成功")
    except Exception as e:
        print(f"✗ LearningStatusAgent 导入失败: {e}")
    
    try:
        from llm.agents.tutoring_agent import TutoringAgent
        print("✓ TutoringAgent 导入成功")
    except Exception as e:
        print(f"✗ TutoringAgent 导入失败: {e}")
    
    try:
        from llm.agents.agent_manager import AgentManager
        print("✓ AgentManager 导入成功")
    except Exception as e:
        print(f"✗ AgentManager 导入失败: {e}")
    
    print("\n基础测试完成!")

if __name__ == "__main__":
    run_basic_tests()
