# 测试包初始化文件

import os
import sys

# 添加项目根目录到Python路径，确保测试可以正确导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

def load_tests(loader, tests, pattern):
    """加载所有测试模块"""
    test_suite = unittest.TestSuite()
    # 自动发现并加载所有以test_开头的测试模块
    test_modules = loader.discover(start_dir=os.path.dirname(__file__), pattern='test_*.py')
    test_suite.addTests(test_modules)
    return test_suite