#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本功能测试脚本
用于验证LLM系统的核心模块是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加service目录到Python路径
service_root = Path(__file__).parent.parent.parent / "service"
sys.path.insert(0, str(service_root))

def test_module_imports():
    """测试核心模块导入"""
    print("\n=== 测试模块导入 ===")
    
    try:
        # 测试LLM客户端导入
        from llm.llm_client import LLMClient
        print("✓ LLMClient 导入成功")
    except Exception as e:
        print(f"✗ LLMClient 导入失败: {e}")
    
    try:
        # 测试智能体导入
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

def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 测试基本功能 ===")
    
    try:
        # 测试LLM工具函数
        from llm.llm_utils import TokenCounter, format_messages
        
        # 测试TokenCounter
        counter = TokenCounter()
        test_text = "这是一个测试文本"
        token_count = counter.count_tokens(test_text)
        print(f"✓ TokenCounter 工作正常，文本 '{test_text}' 的token数: {token_count}")
        
        # 测试format_messages
        messages = [{"role": "user", "content": "测试消息"}]
        formatted = format_messages(messages)
        print(f"✓ format_messages 工作正常")
        
    except Exception as e:
        print(f"✗ LLM工具函数测试失败: {e}")
    
    try:
        # 测试提示词模板
        from llm.prompts.base_prompt import BasePromptTemplate
        
        template = BasePromptTemplate(
            name="test_template",
            template="这是一个测试模板: {content}",
            variables=["content"]
        )
        
        result = template.format(content="测试内容")
        print(f"✓ BasePromptTemplate 工作正常: {result}")
        
    except Exception as e:
        print(f"✗ 提示词模板测试失败: {e}")

def test_agent_creation():
    """测试智能体创建"""
    print("\n=== 测试智能体创建 ===")
    
    try:
        from llm.agents.teaching_analysis_agent import TeachingAnalysisAgent
        from llm.llm_client import LLMClient
        
        # 创建模拟的LLM客户端
        class MockLLMClient:
            def generate_response(self, messages, **kwargs):
                return "模拟响应"
        
        mock_client = MockLLMClient()
        agent = TeachingAnalysisAgent(llm_client=mock_client)
        print("✓ TeachingAnalysisAgent 创建成功")
        
    except Exception as e:
        print(f"✗ TeachingAnalysisAgent 创建失败: {e}")
    
    try:
        from llm.agents.agent_manager import AgentManager
        
        manager = AgentManager()
        print("✓ AgentManager 创建成功")
        
    except Exception as e:
        print(f"✗ AgentManager 创建失败: {e}")

def test_configuration():
    """测试配置模块"""
    print("\n=== 测试配置模块 ===")
    
    try:
        from llm.config.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        print("✓ ConfigManager 创建成功")
        
    except Exception as e:
        print(f"✗ ConfigManager 测试失败: {e}")

def main():
    """主测试函数"""
    print("开始LLM系统基本功能测试...")
    print("=" * 50)
    
    test_module_imports()
    test_basic_functionality()
    test_agent_creation()
    test_configuration()
    
    print("\n=" * 50)
    print("基本功能测试完成")

if __name__ == "__main__":
    main()