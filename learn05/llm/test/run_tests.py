#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行器
用于执行LLM模块的所有单元测试
"""

import os
import sys
import unittest
import argparse
from typing import List, Optional
import time
from io import StringIO
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入测试配置
try:
    from test_config import set_test_env_vars, cleanup_test_env_vars
except ImportError:
    # 如果直接导入失败，尝试从当前目录导入
    import test_config
    set_test_env_vars = test_config.set_test_env_vars
    cleanup_test_env_vars = test_config.cleanup_test_env_vars

class ColoredTextTestResult(unittest.TextTestResult):
    """带颜色输出的测试结果类"""
    
    def __init__(self, stream, descriptions, verbosity, use_color=True):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.use_color = use_color
        self.verbosity = verbosity  # 确保verbosity属性存在
        
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            if self.use_color:
                self.stream.write("\033[92m✓\033[0m ")
            else:
                self.stream.write(". ")
            self.stream.write(self.getDescription(test))
            self.stream.writeln()
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            if self.use_color:
                self.stream.write("\033[91m✗\033[0m ")
            else:
                self.stream.write("E ")
            self.stream.write(self.getDescription(test))
            self.stream.writeln(" (ERROR)")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            if self.use_color:
                self.stream.write("\033[91m✗\033[0m ")
            else:
                self.stream.write("F ")
            self.stream.write(self.getDescription(test))
            self.stream.writeln(" (FAIL)")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            if self.use_color:
                self.stream.write("\033[93m-\033[0m ")
            else:
                self.stream.write("S ")
            self.stream.write(self.getDescription(test))
            self.stream.writeln(f" (SKIP: {reason})")

class ColoredTextTestRunner(unittest.TextTestRunner):
    """带颜色输出的测试运行器"""
    
    def __init__(self, use_color=True, **kwargs):
        self.use_color = use_color
        kwargs['resultclass'] = lambda stream, descriptions, verbosity: ColoredTextTestResult(stream, descriptions, verbosity, use_color)
        super().__init__(**kwargs)
    
    def run(self, test):
        result = super().run(test)
        
        # 打印总结信息
        print("\n" + "="*70)
        print("\033[1m测试结果总结\033[0m")
        print("="*70)
        
        total_tests = result.testsRun
        success_count = getattr(result, 'success_count', 0)
        error_count = len(result.errors)
        failure_count = len(result.failures)
        skip_count = len(result.skipped)
        
        print(f"总测试数: {total_tests}")
        print(f"\033[92m成功: {success_count}\033[0m")
        if failure_count > 0:
            print(f"\033[91m失败: {failure_count}\033[0m")
        if error_count > 0:
            print(f"\033[91m错误: {error_count}\033[0m")
        if skip_count > 0:
            print(f"\033[93m跳过: {skip_count}\033[0m")
        
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
        print(f"成功率: {success_rate:.1f}%")
        
        if result.wasSuccessful():
            print("\n\033[92m🎉 所有测试通过！\033[0m")
        else:
            print("\n\033[91m❌ 部分测试失败\033[0m")
        
        return result

def discover_tests(test_dir: str, pattern: str = "test_*.py") -> unittest.TestSuite:
    """发现测试用例"""
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    return suite

def run_specific_tests(test_names: List[str]) -> unittest.TestSuite:
    """运行指定的测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_name in test_names:
        try:
            # 尝试加载测试模块
            if "." in test_name:
                module_name, test_class = test_name.rsplit(".", 1)
                module = __import__(f"test.{module_name}", fromlist=[test_class])
                test_class_obj = getattr(module, test_class)
                suite.addTest(loader.loadTestsFromTestCase(test_class_obj))
            else:
                # 加载整个测试模块
                module = __import__(f"test.{test_name}", fromlist=[""])
                suite.addTest(loader.loadTestsFromModule(module))
        except (ImportError, AttributeError) as e:
            print(f"\033[91m警告: 无法加载测试 {test_name}: {e}\033[0m")
    
    return suite

def run_performance_tests() -> None:
    """运行性能测试"""
    print("\n" + "="*70)
    print("\033[1m性能测试\033[0m")
    print("="*70)
    
    # 这里可以添加性能测试逻辑
    # 例如：测试LLM响应时间、数据库查询性能等
    
    try:
        from test.test_config import MockLLMClient, MockDatabaseManager, measure_execution_time
        
        # 测试LLM客户端性能
        client = MockLLMClient()
        client.set_response_delay(0.1)  # 设置100ms延迟
        
        _, execution_time = measure_execution_time(
            client.generate_response, 
            "测试提示词"
        )
        print(f"LLM响应时间: {execution_time:.3f}秒")
        
        # 测试数据库查询性能
        db = MockDatabaseManager()
        
        _, execution_time = measure_execution_time(
            db.execute_query,
            "SELECT * FROM students WHERE grade = ?",
            ("高一",)
        )
        print(f"数据库查询时间: {execution_time:.3f}秒")
        
        print("\033[92m✓ 性能测试完成\033[0m")
        
    except Exception as e:
        print(f"\033[91m✗ 性能测试失败: {e}\033[0m")

def generate_test_report(result: unittest.TestResult, output_file: str = None) -> None:
    """生成测试报告"""
    report = StringIO()
    
    report.write("LLM模块单元测试报告\n")
    report.write("=" * 50 + "\n")
    report.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.write(f"总测试数: {result.testsRun}\n")
    report.write(f"成功数: {getattr(result, 'success_count', 0)}\n")
    report.write(f"失败数: {len(result.failures)}\n")
    report.write(f"错误数: {len(result.errors)}\n")
    report.write(f"跳过数: {len(result.skipped)}\n")
    
    if result.failures:
        report.write("\n失败详情:\n")
        report.write("-" * 30 + "\n")
        for test, traceback in result.failures:
            report.write(f"测试: {test}\n")
            report.write(f"错误: {traceback}\n\n")
    
    if result.errors:
        report.write("\n错误详情:\n")
        report.write("-" * 30 + "\n")
        for test, traceback in result.errors:
            report.write(f"测试: {test}\n")
            report.write(f"错误: {traceback}\n\n")
    
    report_content = report.getvalue()
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n测试报告已保存到: {output_file}")
    else:
        print("\n" + report_content)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LLM模块单元测试运行器")
    parser.add_argument(
        "-v", "--verbosity", 
        type=int, 
        default=2, 
        help="测试输出详细程度 (0-2)"
    )
    parser.add_argument(
        "-p", "--pattern", 
        default="test_*.py", 
        help="测试文件匹配模式"
    )
    parser.add_argument(
        "-t", "--tests", 
        nargs="*", 
        help="指定要运行的测试模块或类"
    )
    parser.add_argument(
        "--performance", 
        action="store_true", 
        help="运行性能测试"
    )
    parser.add_argument(
        "--report", 
        help="生成测试报告到指定文件"
    )
    parser.add_argument(
        "--no-color", 
        action="store_true", 
        help="禁用彩色输出"
    )
    
    args = parser.parse_args()
    
    # 设置测试环境
    set_test_env_vars()
    
    try:
        # 获取测试目录
        test_dir = os.path.dirname(os.path.abspath(__file__))
        
        print("\033[1mLLM模块单元测试运行器\033[0m")
        print("=" * 50)
        print(f"测试目录: {test_dir}")
        print(f"测试模式: {args.pattern}")
        
        # 发现或加载测试
        if args.tests:
            print(f"指定测试: {', '.join(args.tests)}")
            suite = run_specific_tests(args.tests)
        else:
            print("发现所有测试...")
            suite = discover_tests(test_dir, args.pattern)
        
        print(f"找到 {suite.countTestCases()} 个测试用例")
        print()
        
        # 运行测试
        if args.no_color:
            runner = ColoredTextTestRunner(use_color=False, verbosity=args.verbosity)
        else:
            runner = ColoredTextTestRunner(use_color=True, verbosity=args.verbosity)
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        print(f"\n总耗时: {end_time - start_time:.2f}秒")
        
        # 运行性能测试
        if args.performance:
            run_performance_tests()
        
        # 生成测试报告
        if args.report:
            generate_test_report(result, args.report)
        
        # 返回适当的退出码
        sys.exit(0 if result.wasSuccessful() else 1)
        
    except KeyboardInterrupt:
        print("\n\033[93m测试被用户中断\033[0m")
        sys.exit(1)
    except Exception as e:
        print(f"\n\033[91m测试运行器错误: {e}\033[0m")
        sys.exit(1)
    finally:
        # 清理测试环境
        cleanup_test_env_vars()

if __name__ == "__main__":
    main()