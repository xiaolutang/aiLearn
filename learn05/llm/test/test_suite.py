#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件
组织和管理LLM模块的所有测试用例
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入所有测试模块
try:
    from test.test_llm_client import *
    from test.test_database_manager import *
    from test.test_config_manager import *
    from test.test_cache import *
    from test.test_context_management import *
    from test.test_prompts import *
    from test.test_langgraph_sql_agent import *
    from test.test_sql_agent import *
    from test.test_classroom_ai_agent import *
    from test.test_teaching_analysis_agent import *
    from test.test_learning_status_agent import *
    from test.test_tutoring_agent import *
    from test.test_agent_manager import *
except ImportError as e:
    print(f"警告: 无法导入某些测试模块: {e}")
    print("请确保所有测试文件都已正确创建")

class LLMTestSuite:
    """LLM模块测试套件"""
    
    @staticmethod
    def create_core_suite() -> unittest.TestSuite:
        """创建核心功能测试套件"""
        suite = unittest.TestSuite()
        
        # 核心组件测试
        core_test_classes = [
            # LLM客户端测试
            'TestLLMInterface',
            'TestOpenAIClient', 
            'TestMockLLMClient',
            'TestLLMClientFactory',
            'TestLLMUtils',
            
            # 数据库管理测试
            'TestMockDatabaseManager',
            'TestDatabaseUtils',
            'TestModels',
            
            # 配置管理测试
            'TestMockConfigManager',
            'TestLLMConfig',
            'TestDatabaseConfig',
            'TestCacheConfig',
            'TestAgentConfig',
            'TestEnvironmentSettings',
        ]
        
        for test_class_name in core_test_classes:
            try:
                test_class = globals().get(test_class_name)
                if test_class:
                    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
            except Exception as e:
                print(f"警告: 无法加载测试类 {test_class_name}: {e}")
        
        return suite
    
    @staticmethod
    def create_agent_suite() -> unittest.TestSuite:
        """创建智能体测试套件"""
        suite = unittest.TestSuite()
        
        # 智能体测试
        agent_test_classes = [
            # 教材分析智能体
            'TestTeachingAnalysisAgent',
            'TestTeachingAnalysisAgentIntegration',
            
            # 学情分析智能体
            'TestLearningStatusAgent', 
            'TestLearningStatusAgentIntegration',
            
            # 辅导智能体
            'TestTutoringAgent',
            'TestTutoringAgentIntegration',
            
            # 课堂AI智能体
            'TestClassroomAIAgent',
            'TestClassroomAIAgentIntegration',
            
            # SQL智能体
            'TestSQLAgent',
            'TestBasicSQLAgent',
            'TestLangGraphSQLAgent',
            
            # 智能体管理器
            'TestAgentManager',
            'TestAgentManagerIntegration',
        ]
        
        for test_class_name in agent_test_classes:
            try:
                test_class = globals().get(test_class_name)
                if test_class:
                    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
            except Exception as e:
                print(f"警告: 无法加载测试类 {test_class_name}: {e}")
        
        return suite
    
    @staticmethod
    def create_utility_suite() -> unittest.TestSuite:
        """创建工具类测试套件"""
        suite = unittest.TestSuite()
        
        # 工具类测试
        utility_test_classes = [
            # 缓存管理测试
            'TestCacheManager',
            'TestCacheResponseDecorator',
            'TestCachedLLMWrapper',
            'TestCacheKeyGeneration',
            
            # 上下文管理测试
            'TestContextManager',
            'TestContextAwareLLMWrapper',
            
            # 提示词管理测试
            'TestBasePromptTemplate',
            'TestTeachingPrompts',
            'TestLearningPrompts', 
            'TestTutoringPrompts',
            'TestClassroomPrompts',
            'TestPromptManager',
        ]
        
        for test_class_name in utility_test_classes:
            try:
                test_class = globals().get(test_class_name)
                if test_class:
                    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
            except Exception as e:
                print(f"警告: 无法加载测试类 {test_class_name}: {e}")
        
        return suite
    
    @staticmethod
    def create_integration_suite() -> unittest.TestSuite:
        """创建集成测试套件"""
        suite = unittest.TestSuite()
        
        # 集成测试类
        integration_test_classes = [
            'TestTeachingAnalysisAgentIntegration',
            'TestLearningStatusAgentIntegration', 
            'TestTutoringAgentIntegration',
            'TestClassroomAIAgentIntegration',
            'TestAgentManagerIntegration',
            'TestLLMClientIntegration',
        ]
        
        for test_class_name in integration_test_classes:
            try:
                test_class = globals().get(test_class_name)
                if test_class:
                    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
            except Exception as e:
                print(f"警告: 无法加载测试类 {test_class_name}: {e}")
        
        return suite
    
    @staticmethod
    def create_performance_suite() -> unittest.TestSuite:
        """创建性能测试套件"""
        suite = unittest.TestSuite()
        
        # 性能测试类
        performance_test_classes = [
            'TestLLMClientPerformance',
            'TestDatabasePerformance', 
            'TestCachePerformance',
            'TestAgentPerformance',
        ]
        
        for test_class_name in performance_test_classes:
            try:
                test_class = globals().get(test_class_name)
                if test_class:
                    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
            except Exception as e:
                print(f"警告: 无法加载测试类 {test_class_name}: {e}")
        
        return suite
    
    @staticmethod
    def create_error_handling_suite() -> unittest.TestSuite:
        """创建错误处理测试套件"""
        suite = unittest.TestSuite()
        
        # 错误处理测试类
        error_test_classes = [
            'TestLLMClientErrorHandling',
            'TestDatabaseErrorHandling',
            'TestAgentErrorHandling',
            'TestCacheErrorHandling',
            'TestContextErrorHandling',
        ]
        
        for test_class_name in error_test_classes:
            try:
                test_class = globals().get(test_class_name)
                if test_class:
                    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
            except Exception as e:
                print(f"警告: 无法加载测试类 {test_class_name}: {e}")
        
        return suite
    
    @staticmethod
    def create_full_suite() -> unittest.TestSuite:
        """创建完整测试套件"""
        full_suite = unittest.TestSuite()
        
        # 添加所有子套件
        full_suite.addTest(LLMTestSuite.create_core_suite())
        full_suite.addTest(LLMTestSuite.create_agent_suite())
        full_suite.addTest(LLMTestSuite.create_utility_suite())
        full_suite.addTest(LLMTestSuite.create_integration_suite())
        
        return full_suite
    
    @staticmethod
    def create_quick_suite() -> unittest.TestSuite:
        """创建快速测试套件（仅核心功能）"""
        quick_suite = unittest.TestSuite()
        
        # 只添加核心和工具类测试
        quick_suite.addTest(LLMTestSuite.create_core_suite())
        quick_suite.addTest(LLMTestSuite.create_utility_suite())
        
        return quick_suite
    
    @staticmethod
    def create_smoke_suite() -> unittest.TestSuite:
        """创建冒烟测试套件（最基本的功能测试）"""
        suite = unittest.TestSuite()
        
        # 冒烟测试类（基本功能验证）
        smoke_test_classes = [
            'TestLLMInterface',
            'TestMockDatabaseManager',
            'TestMockConfigManager',
            'TestCacheManager',
            'TestTeachingAnalysisAgent',
            'TestAgentManager',
        ]
        
        for test_class_name in smoke_test_classes:
            try:
                test_class = globals().get(test_class_name)
                if test_class:
                    # 只运行每个测试类的第一个测试方法
                    loader = unittest.TestLoader()
                    tests = loader.loadTestsFromTestCase(test_class)
                    if tests.countTestCases() > 0:
                        # 获取第一个测试方法
                        first_test = list(tests)[0]
                        suite.addTest(first_test)
            except Exception as e:
                print(f"警告: 无法加载测试类 {test_class_name}: {e}")
        
        return suite

def get_suite_by_name(suite_name: str) -> unittest.TestSuite:
    """根据名称获取测试套件"""
    suite_map = {
        'core': LLMTestSuite.create_core_suite,
        'agent': LLMTestSuite.create_agent_suite,
        'utility': LLMTestSuite.create_utility_suite,
        'integration': LLMTestSuite.create_integration_suite,
        'performance': LLMTestSuite.create_performance_suite,
        'error': LLMTestSuite.create_error_handling_suite,
        'full': LLMTestSuite.create_full_suite,
        'quick': LLMTestSuite.create_quick_suite,
        'smoke': LLMTestSuite.create_smoke_suite,
    }
    
    suite_func = suite_map.get(suite_name.lower())
    if suite_func:
        return suite_func()
    else:
        raise ValueError(f"未知的测试套件名称: {suite_name}")

def list_available_suites() -> list[str]:
    """列出所有可用的测试套件"""
    return [
        'core - 核心功能测试',
        'agent - 智能体测试', 
        'utility - 工具类测试',
        'integration - 集成测试',
        'performance - 性能测试',
        'error - 错误处理测试',
        'full - 完整测试套件',
        'quick - 快速测试套件',
        'smoke - 冒烟测试套件',
    ]

def run_suite(suite_name: str = 'full', verbosity: int = 2) -> unittest.TestResult:
    """运行指定的测试套件"""
    try:
        suite = get_suite_by_name(suite_name)
        runner = unittest.TextTestRunner(verbosity=verbosity)
        
        print(f"\n运行测试套件: {suite_name}")
        print(f"测试用例数量: {suite.countTestCases()}")
        print("=" * 50)
        
        result = runner.run(suite)
        
        print("\n" + "=" * 50)
        print(f"测试套件 '{suite_name}' 运行完成")
        print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"失败: {len(result.failures)}")
        print(f"错误: {len(result.errors)}")
        
        return result
        
    except Exception as e:
        print(f"运行测试套件时出错: {e}")
        raise

if __name__ == '__main__':
    import argparse

class MockConfigManager:
    """Mock配置管理器"""
    def __init__(self, *args, **kwargs):
        pass
    
    def get_config(self, key, default=None):
        return default
    
    def set_config(self, key, value):
        pass


import argparse
import sys

class MockDatabaseManager:
    """Mock数据库管理器"""
    def __init__(self, *args, **kwargs):
        pass
    
    def execute_query(self, query, params=None):
        return []
    
    def get_table_schema(self, table_name):
        return {}
    
    def get_all_tables(self):
        return []

    
    parser = argparse.ArgumentParser(description='LLM模块测试套件')
    parser.add_argument(
        'suite', 
        nargs='?', 
        default='full',
        help='要运行的测试套件名称'
    )
    parser.add_argument(
        '-v', '--verbosity',
        type=int,
        default=2,
        help='测试输出详细程度'
    )
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='列出所有可用的测试套件'
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("可用的测试套件:")
        for suite_info in list_available_suites():
            print(f"  {suite_info}")
    else:
        try:
            result = run_suite(args.suite, args.verbosity)
            # sys.exit removed else 1)
        except KeyboardInterrupt:
            print("\n测试被用户中断")
            # sys.exit removed
        except Exception as e:
            print(f"\n测试运行失败: {e}")
            # sys.exit removed