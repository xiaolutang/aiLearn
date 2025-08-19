#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的测试运行器
用于验证LLM模块的单元测试
"""

import sys
import os
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """运行测试的主函数"""
    print("LLM模块单元测试 - 简化版")
    print("=" * 50)
    
    # 设置测试目录
    test_dir = Path(__file__).parent
    print(f"测试目录: {test_dir}")
    
    # 发现测试
    loader = unittest.TestLoader()
    
    try:
        # 尝试加载测试配置
        sys.path.insert(0, str(test_dir))
        import test_config
        print("✓ 测试配置加载成功")
    except ImportError as e:
        print(f"⚠ 测试配置加载失败: {e}")
    
    # 尝试发现并运行测试
    try:
        suite = loader.discover(str(test_dir), pattern='test_*.py')
        test_count = suite.countTestCases()
        print(f"发现 {test_count} 个测试用例")
        
        if test_count == 0:
            print("没有找到测试用例")
            return 1
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # 输出结果
        print("\n" + "=" * 50)
        print(f"测试完成: 运行 {result.testsRun} 个测试")
        print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"失败: {len(result.failures)}")
        print(f"错误: {len(result.errors)}")
        
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback.split('\n')[-2] if traceback else 'Unknown'}")
        
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback.split('\n')[-2] if traceback else 'Unknown'}")
        
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"测试运行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())