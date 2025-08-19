#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有测试用例的脚本
"""

import os
import sys
import unittest

# 获取当前脚本所在目录的绝对路径
service_dir = os.path.dirname(os.path.abspath(__file__))
# 获取aiLearn目录的绝对路径（learn05的父目录）
ailearn_dir = os.path.dirname(os.path.dirname(service_dir))
# 将aiLearn目录添加到Python路径，确保可以正确导入learn05.service模块
sys.path.append(ailearn_dir)

if __name__ == '__main__':
    # 发现并运行所有测试
    test_loader = unittest.TestLoader()
    
    # 直接指定测试目录的绝对路径
    test_suite = test_loader.discover(os.path.join(service_dir, 'tests'), pattern='test_*.py')
    
    # 创建测试运行器
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # 运行测试
    result = test_runner.run(test_suite)
    
    # 根据测试结果设置退出码
    sys.exit(not result.wasSuccessful())