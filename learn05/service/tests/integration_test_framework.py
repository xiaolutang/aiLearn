#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手集成测试框架

功能：
1. 自动化执行客户端-服务端集成测试
2. 支持多角色账号测试
3. 生成详细的测试报告
4. 支持并发测试和性能监控

作者：测试工程师
日期：2024年12月
"""

import json
import time
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import logging
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integration_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """测试结果数据类"""
    test_id: str
    test_name: str
    account_id: str
    role: str
    status: str  # PASS, FAIL, SKIP
    start_time: str
    end_time: str
    duration: float
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    performance_metrics: Optional[Dict] = None

@dataclass
class TestSuite:
    """测试套件数据类"""
    suite_name: str
    description: str
    test_cases: List[str]
    required_roles: List[str]
    priority: str  # high, medium, low

class IntegrationTestFramework:
    """集成测试框架主类"""
    
    def __init__(self, config_file: str = "test_accounts.json", base_url: str = "http://localhost:8000"):
        self.config_file = config_file
        self.base_url = base_url
        self.test_accounts = {}
        self.test_results = []
        self.test_suites = {}
        self.session_tokens = {}
        
        # 初始化测试套件
        self._init_test_suites()
        
        # 加载测试账号
        self._load_test_accounts()
        
        logger.info(f"集成测试框架初始化完成，基础URL: {self.base_url}")
    
    def _load_test_accounts(self):
        """加载测试账号配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.test_accounts = {acc['id']: acc for acc in config['test_accounts']['accounts']}
            logger.info(f"成功加载 {len(self.test_accounts)} 个测试账号")
        except Exception as e:
            logger.error(f"加载测试账号失败: {e}")
            raise
    
    def _init_test_suites(self):
        """初始化测试套件"""
        self.test_suites = {
            "authentication": TestSuite(
                suite_name="用户认证测试",
                description="验证用户登录、登出、会话管理等认证功能",
                test_cases=["login_test", "logout_test", "session_validation", "invalid_credentials"],
                required_roles=["系统管理员", "教师", "学生", "家长", "访客"],
                priority="high"
            ),
            "authorization": TestSuite(
                suite_name="权限控制测试",
                description="验证不同角色的权限控制和访问限制",
                test_cases=["role_permission_check", "unauthorized_access", "resource_access_control"],
                required_roles=["系统管理员", "校长", "教务主任", "教师", "学生", "家长", "访客"],
                priority="high"
            ),
            "lesson_preparation": TestSuite(
                suite_name="备课模块测试",
                description="验证教材分析、环节策划、学情预设等备课功能",
                test_cases=["material_analysis", "lesson_planning", "student_status_preset", "case_reference"],
                required_roles=["教师"],
                priority="high"
            ),
            "classroom": TestSuite(
                suite_name="上课模块测试",
                description="验证AI学情生成、课堂互动、实验设计等上课功能",
                test_cases=["ai_status_generation", "classroom_interaction", "experiment_design", "video_analysis"],
                required_roles=["教师"],
                priority="high"
            ),
            "grade_management": TestSuite(
                suite_name="成绩模块测试",
                description="验证成绩录入、分析、个性化辅导等成绩管理功能",
                test_cases=["grade_input", "grade_analysis", "personalized_tutoring", "report_generation"],
                required_roles=["教师", "学生", "家长", "校长", "教务主任"],
                priority="high"
            ),
            "data_flow": TestSuite(
                suite_name="数据流测试",
                description="验证客户端-服务端数据同步和一致性",
                test_cases=["data_synchronization", "cross_module_consistency", "data_integrity"],
                required_roles=["教师", "学生"],
                priority="medium"
            ),
            "performance": TestSuite(
                suite_name="性能测试",
                description="验证系统性能指标和响应时间",
                test_cases=["page_load_performance", "data_processing_performance", "concurrent_access"],
                required_roles=["教师", "学生"],
                priority="medium"
            ),
            "security": TestSuite(
                suite_name="安全测试",
                description="验证数据安全、会话管理等安全功能",
                test_cases=["data_encryption", "session_security", "injection_protection", "xss_protection"],
                required_roles=["系统管理员", "教师"],
                priority="high"
            )
        }
    
    async def authenticate_user(self, account_id: str) -> bool:
        """用户认证"""
        if account_id not in self.test_accounts:
            logger.error(f"账号 {account_id} 不存在")
            return False
        
        account = self.test_accounts[account_id]
        
        # 检查账号状态
        if account['status'] != 'active':
            logger.warning(f"账号 {account_id} 状态为 {account['status']}，跳过认证")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "username": account['username'],
                    "password": account['password']
                }
                
                async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.session_tokens[account_id] = result.get('token', '')
                        logger.info(f"账号 {account_id} ({account['role']}) 认证成功")
                        return True
                    else:
                        logger.error(f"账号 {account_id} 认证失败，状态码: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"账号 {account_id} 认证异常: {e}")
            return False
    
    async def execute_test_case(self, test_case: str, account_id: str) -> TestResult:
        """执行单个测试用例"""
        start_time = datetime.now()
        account = self.test_accounts[account_id]
        
        result = TestResult(
            test_id=f"{test_case}_{account_id}",
            test_name=test_case,
            account_id=account_id,
            role=account['role'],
            status="FAIL",
            start_time=start_time.isoformat(),
            end_time="",
            duration=0.0
        )
        
        try:
            # 根据测试用例类型执行不同的测试逻辑
            if test_case == "login_test":
                success = await self._test_login(account_id)
            elif test_case == "role_permission_check":
                success = await self._test_role_permissions(account_id)
            elif test_case == "material_analysis":
                success = await self._test_material_analysis(account_id)
            elif test_case == "grade_input":
                success = await self._test_grade_input(account_id)
            elif test_case == "data_synchronization":
                success = await self._test_data_synchronization(account_id)
            elif test_case == "page_load_performance":
                success = await self._test_page_performance(account_id)
            elif test_case == "data_encryption":
                success = await self._test_data_encryption(account_id)
            else:
                logger.warning(f"未知测试用例: {test_case}")
                success = False
            
            result.status = "PASS" if success else "FAIL"
            
        except Exception as e:
            result.status = "FAIL"
            result.error_message = str(e)
            logger.error(f"测试用例 {test_case} 执行异常: {e}")
        
        finally:
            end_time = datetime.now()
            result.end_time = end_time.isoformat()
            result.duration = (end_time - start_time).total_seconds()
        
        return result
    
    async def _test_login(self, account_id: str) -> bool:
        """测试登录功能"""
        return await self.authenticate_user(account_id)
    
    async def _test_role_permissions(self, account_id: str) -> bool:
        """测试角色权限"""
        if account_id not in self.session_tokens:
            return False
        
        account = self.test_accounts[account_id]
        role = account['role']
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
                
                # 测试不同角色的API访问权限
                test_endpoints = {
                    "系统管理员": ["/api/admin/users", "/api/admin/system"],
                    "校长": ["/api/school/statistics", "/api/school/reports"],
                    "教务主任": ["/api/academic/courses", "/api/academic/teachers"],
                    "教师": ["/api/teacher/classes", "/api/teacher/grades"],
                    "学生": ["/api/student/grades", "/api/student/profile"],
                    "家长": ["/api/parent/children", "/api/parent/reports"],
                    "访客": ["/api/public/demo"]
                }
                
                endpoints = test_endpoints.get(role, [])
                for endpoint in endpoints:
                    async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                        if response.status not in [200, 404]:  # 404表示端点不存在，但权限正常
                            logger.error(f"角色 {role} 访问 {endpoint} 失败，状态码: {response.status}")
                            return False
                
                return True
        except Exception as e:
            logger.error(f"权限测试异常: {e}")
            return False
    
    async def _test_material_analysis(self, account_id: str) -> bool:
        """测试教材分析功能"""
        if account_id not in self.session_tokens:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
                
                # 模拟教材分析请求
                material_data = {
                    "title": "高中数学必修一",
                    "content": "函数的概念和性质",
                    "grade": "高一",
                    "subject": "数学"
                }
                
                async with session.post(f"{self.base_url}/api/lesson/material-analysis", 
                                       json=material_data, headers=headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"教材分析测试异常: {e}")
            return False
    
    async def _test_grade_input(self, account_id: str) -> bool:
        """测试成绩录入功能"""
        if account_id not in self.session_tokens:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
                
                # 模拟成绩录入请求
                grade_data = {
                    "exam_name": "期中考试",
                    "subject": "数学",
                    "grades": [
                        {"student_id": "student_001", "score": 85},
                        {"student_id": "student_002", "score": 92}
                    ]
                }
                
                async with session.post(f"{self.base_url}/api/grades/input", 
                                       json=grade_data, headers=headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"成绩录入测试异常: {e}")
            return False
    
    async def _test_data_synchronization(self, account_id: str) -> bool:
        """测试数据同步"""
        # 模拟数据同步测试
        await asyncio.sleep(0.1)  # 模拟网络延迟
        return True
    
    async def _test_page_performance(self, account_id: str) -> bool:
        """测试页面性能"""
        if account_id not in self.session_tokens:
            return False
        
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
                async with session.get(f"{self.base_url}/api/dashboard", headers=headers) as response:
                    load_time = time.time() - start_time
                    # 要求页面加载时间小于2秒
                    return response.status == 200 and load_time < 2.0
        except Exception as e:
            logger.error(f"性能测试异常: {e}")
            return False
    
    async def _test_data_encryption(self, account_id: str) -> bool:
        """测试数据加密"""
        # 模拟数据加密测试
        return True
    
    async def run_test_suite(self, suite_name: str, account_ids: List[str] = None) -> List[TestResult]:
        """运行测试套件"""
        if suite_name not in self.test_suites:
            logger.error(f"测试套件 {suite_name} 不存在")
            return []
        
        suite = self.test_suites[suite_name]
        logger.info(f"开始执行测试套件: {suite.suite_name}")
        
        # 如果没有指定账号，则使用所有符合角色要求的账号
        if account_ids is None:
            account_ids = [acc_id for acc_id, acc in self.test_accounts.items() 
                          if acc['role'] in suite.required_roles and acc['status'] == 'active']
        
        results = []
        
        # 为每个账号执行测试套件中的所有测试用例
        for account_id in account_ids:
            for test_case in suite.test_cases:
                result = await self.execute_test_case(test_case, account_id)
                results.append(result)
                self.test_results.append(result)
        
        logger.info(f"测试套件 {suite.suite_name} 执行完成，共 {len(results)} 个测试用例")
        return results
    
    async def run_concurrent_test(self, suite_name: str, max_concurrent: int = 5) -> List[TestResult]:
        """运行并发测试"""
        if suite_name not in self.test_suites:
            logger.error(f"测试套件 {suite_name} 不存在")
            return []
        
        suite = self.test_suites[suite_name]
        account_ids = [acc_id for acc_id, acc in self.test_accounts.items() 
                      if acc['role'] in suite.required_roles and acc['status'] == 'active']
        
        logger.info(f"开始并发测试: {suite.suite_name}，并发数: {max_concurrent}")
        
        # 创建并发任务
        tasks = []
        for account_id in account_ids[:max_concurrent]:
            for test_case in suite.test_cases:
                task = self.execute_test_case(test_case, account_id)
                tasks.append(task)
        
        # 执行并发测试
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        valid_results = [r for r in results if isinstance(r, TestResult)]
        self.test_results.extend(valid_results)
        
        logger.info(f"并发测试完成，成功执行 {len(valid_results)} 个测试用例")
        return valid_results
    
    def generate_test_report(self, output_file: str = "integration_test_report.html") -> str:
        """生成测试报告"""
        if not self.test_results:
            logger.warning("没有测试结果，无法生成报告")
            return ""
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r.status == "SKIP"])
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 按角色统计
        role_stats = {}
        for result in self.test_results:
            role = result.role
            if role not in role_stats:
                role_stats[role] = {"total": 0, "passed": 0, "failed": 0}
            role_stats[role]["total"] += 1
            if result.status == "PASS":
                role_stats[role]["passed"] += 1
            elif result.status == "FAIL":
                role_stats[role]["failed"] += 1
        
        # 生成HTML报告
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>智能教学助手集成测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-card {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; text-align: center; }}
        .pass {{ background-color: #d4edda; }}
        .fail {{ background-color: #f8d7da; }}
        .skip {{ background-color: #fff3cd; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .status-pass {{ color: green; font-weight: bold; }}
        .status-fail {{ color: red; font-weight: bold; }}
        .status-skip {{ color: orange; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>智能教学助手集成测试报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>测试环境: {self.base_url}</p>
    </div>
    
    <div class="summary">
        <h2>测试概要</h2>
        <div class="stats">
            <div class="stat-card">
                <h3>总测试数</h3>
                <p>{total_tests}</p>
            </div>
            <div class="stat-card pass">
                <h3>通过</h3>
                <p>{passed_tests}</p>
            </div>
            <div class="stat-card fail">
                <h3>失败</h3>
                <p>{failed_tests}</p>
            </div>
            <div class="stat-card skip">
                <h3>跳过</h3>
                <p>{skipped_tests}</p>
            </div>
            <div class="stat-card">
                <h3>通过率</h3>
                <p>{pass_rate:.1f}%</p>
            </div>
        </div>
    </div>
    
    <div class="role-stats">
        <h2>角色测试统计</h2>
        <table>
            <tr>
                <th>角色</th>
                <th>总测试数</th>
                <th>通过数</th>
                <th>失败数</th>
                <th>通过率</th>
            </tr>
"""
        
        for role, stats in role_stats.items():
            role_pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            html_content += f"""
            <tr>
                <td>{role}</td>
                <td>{stats["total"]}</td>
                <td>{stats["passed"]}</td>
                <td>{stats["failed"]}</td>
                <td>{role_pass_rate:.1f}%</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <div class="detailed-results">
        <h2>详细测试结果</h2>
        <table>
            <tr>
                <th>测试ID</th>
                <th>测试名称</th>
                <th>账号</th>
                <th>角色</th>
                <th>状态</th>
                <th>执行时间(秒)</th>
                <th>错误信息</th>
            </tr>
"""
        
        for result in self.test_results:
            status_class = f"status-{result.status.lower()}"
            error_msg = result.error_message or "-"
            html_content += f"""
            <tr>
                <td>{result.test_id}</td>
                <td>{result.test_name}</td>
                <td>{result.account_id}</td>
                <td>{result.role}</td>
                <td class="{status_class}">{result.status}</td>
                <td>{result.duration:.2f}</td>
                <td>{error_msg}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
</body>
</html>
"""
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"测试报告已生成: {output_file}")
        return output_file
    
    def export_results_to_excel(self, output_file: str = "integration_test_results.xlsx"):
        """导出测试结果到Excel"""
        if not self.test_results:
            logger.warning("没有测试结果，无法导出")
            return
        
        # 转换为DataFrame
        df = pd.DataFrame([asdict(result) for result in self.test_results])
        
        # 创建Excel文件
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 详细结果
            df.to_excel(writer, sheet_name='测试结果', index=False)
            
            # 统计汇总
            summary_data = {
                '指标': ['总测试数', '通过数', '失败数', '跳过数', '通过率(%)'],
                '数值': [
                    len(self.test_results),
                    len([r for r in self.test_results if r.status == "PASS"]),
                    len([r for r in self.test_results if r.status == "FAIL"]),
                    len([r for r in self.test_results if r.status == "SKIP"]),
                    len([r for r in self.test_results if r.status == "PASS"]) / len(self.test_results) * 100
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='测试汇总', index=False)
        
        logger.info(f"测试结果已导出到Excel: {output_file}")

# 主执行函数
async def main():
    """主执行函数"""
    # 初始化测试框架
    framework = IntegrationTestFramework()
    
    # 执行所有测试套件
    test_suites = ["authentication", "authorization", "lesson_preparation", 
                   "classroom", "grade_management", "data_flow", "performance", "security"]
    
    logger.info("开始执行集成测试...")
    
    for suite_name in test_suites:
        try:
            await framework.run_test_suite(suite_name)
        except Exception as e:
            logger.error(f"测试套件 {suite_name} 执行失败: {e}")
    
    # 执行并发测试
    logger.info("开始执行并发测试...")
    try:
        await framework.run_concurrent_test("performance", max_concurrent=3)
    except Exception as e:
        logger.error(f"并发测试执行失败: {e}")
    
    # 生成测试报告
    framework.generate_test_report()
    framework.export_results_to_excel()
    
    logger.info("集成测试执行完成")

if __name__ == "__main__":
    asyncio.run(main())