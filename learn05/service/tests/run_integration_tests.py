#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手集成测试主执行器

功能：
1. 运行所有集成测试脚本
2. 生成综合测试报告
3. 统计测试结果
4. 提供测试摘要和建议

作者：测试工程师
日期：2024年12月
"""

import asyncio
import json
import time
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integration_test_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class IntegrationTestRunner:
    """集成测试运行器"""
    
    def __init__(self):
        self.test_scripts = [
            {
                "name": "认证流程测试",
                "script": "test_authentication.py",
                "description": "测试用户认证和登录流程",
                "priority": "high"
            },
            {
                "name": "权限控制测试",
                "script": "test_authorization.py",
                "description": "测试不同角色的权限控制",
                "priority": "high"
            },
            {
                "name": "核心功能测试",
                "script": "test_core_functions.py",
                "description": "测试备课、上课、成绩管理等核心功能",
                "priority": "high"
            },
            {
                "name": "数据流测试",
                "script": "test_data_flow.py",
                "description": "测试客户端-服务端数据流",
                "priority": "high"
            },
            {
                "name": "并发访问测试",
                "script": "test_concurrent_access.py",
                "description": "测试多用户并发访问",
                "priority": "medium"
            },
            {
                "name": "性能测试",
                "script": "test_performance.py",
                "description": "测试系统性能表现",
                "priority": "medium"
            },
            {
                "name": "安全性测试",
                "script": "test_security.py",
                "description": "测试系统安全性",
                "priority": "high"
            }
        ]
        
        self.test_results = {}
        self.execution_summary = {
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "tests_executed": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0
        }
        
        logger.info(f"集成测试运行器初始化完成，共 {len(self.test_scripts)} 个测试脚本")
    
    def check_prerequisites(self) -> bool:
        """检查测试前置条件"""
        logger.info("检查测试前置条件...")
        
        # 检查必要文件是否存在
        required_files = [
            "test_accounts.json",
            "test_accounts.xlsx"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"缺少必要文件: {missing_files}")
            return False
        
        # 检查测试脚本是否存在
        missing_scripts = []
        for test_info in self.test_scripts:
            script_path = test_info["script"]
            if not os.path.exists(script_path):
                missing_scripts.append(script_path)
        
        if missing_scripts:
            logger.error(f"缺少测试脚本: {missing_scripts}")
            return False
        
        # 检查Python依赖
        try:
            import aiohttp
            import pandas
            import openpyxl
        except ImportError as e:
            logger.error(f"缺少Python依赖: {e}")
            return False
        
        logger.info("前置条件检查通过")
        return True
    
    async def run_test_script(self, test_info: Dict) -> Dict:
        """运行单个测试脚本"""
        script_name = test_info["script"]
        test_name = test_info["name"]
        
        logger.info(f"开始执行测试: {test_name} ({script_name})")
        
        start_time = time.time()
        result = {
            "test_name": test_name,
            "script": script_name,
            "description": test_info["description"],
            "priority": test_info["priority"],
            "start_time": datetime.now().isoformat(),
            "status": "unknown",
            "duration": 0,
            "output": "",
            "error": "",
            "details": {}
        }
        
        try:
            # 运行测试脚本
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # 设置超时时间（根据测试类型调整）
            timeout = 300 if test_info["priority"] == "high" else 600  # 5-10分钟
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                result["output"] = stdout.decode('utf-8', errors='ignore')
                result["error"] = stderr.decode('utf-8', errors='ignore')
                result["return_code"] = process.returncode
                
                if process.returncode == 0:
                    result["status"] = "passed"
                    logger.info(f"测试通过: {test_name}")
                else:
                    result["status"] = "failed"
                    logger.error(f"测试失败: {test_name} (返回码: {process.returncode})")
                
            except asyncio.TimeoutError:
                process.kill()
                result["status"] = "timeout"
                result["error"] = f"测试超时 ({timeout}秒)"
                logger.error(f"测试超时: {test_name}")
        
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"测试执行异常: {test_name} - {e}")
        
        end_time = time.time()
        result["duration"] = end_time - start_time
        result["end_time"] = datetime.now().isoformat()
        
        # 尝试解析测试结果文件
        result_files = {
            "test_authentication.py": "authentication_test_results.json",
            "test_authorization.py": "authorization_test_results.json",
            "test_core_functions.py": "core_functions_test_results.json",
            "test_data_flow.py": "data_flow_test_results.json",
            "test_concurrent_access.py": "concurrent_access_test_results.json",
            "test_performance.py": "performance_test_results.json",
            "test_security.py": "security_test_results.json"
        }
        
        result_file = result_files.get(script_name)
        if result_file and os.path.exists(result_file):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    test_details = json.load(f)
                    result["details"] = test_details
                logger.info(f"成功加载测试详情: {result_file}")
            except Exception as e:
                logger.warning(f"无法加载测试详情文件 {result_file}: {e}")
        
        return result
    
    async def run_all_tests(self, skip_failed: bool = False) -> Dict:
        """运行所有集成测试"""
        logger.info("开始执行集成测试套件...")
        
        # 检查前置条件
        if not self.check_prerequisites():
            raise Exception("前置条件检查失败，无法执行测试")
        
        self.execution_summary["start_time"] = datetime.now().isoformat()
        start_time = time.time()
        
        # 按优先级排序测试
        high_priority_tests = [t for t in self.test_scripts if t["priority"] == "high"]
        medium_priority_tests = [t for t in self.test_scripts if t["priority"] == "medium"]
        low_priority_tests = [t for t in self.test_scripts if t["priority"] == "low"]
        
        ordered_tests = high_priority_tests + medium_priority_tests + low_priority_tests
        
        # 执行测试
        for test_info in ordered_tests:
            try:
                result = await self.run_test_script(test_info)
                self.test_results[test_info["script"]] = result
                
                # 更新执行统计
                self.execution_summary["tests_executed"] += 1
                
                if result["status"] == "passed":
                    self.execution_summary["tests_passed"] += 1
                elif result["status"] in ["failed", "error", "timeout"]:
                    self.execution_summary["tests_failed"] += 1
                    
                    # 如果是高优先级测试失败且设置了跳过失败，则停止执行
                    if test_info["priority"] == "high" and skip_failed:
                        logger.warning(f"高优先级测试失败，跳过后续测试: {test_info['name']}")
                        break
                else:
                    self.execution_summary["tests_skipped"] += 1
                
                # 在测试之间添加短暂延迟
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"执行测试时发生异常: {test_info['name']} - {e}")
                self.execution_summary["tests_failed"] += 1
        
        end_time = time.time()
        self.execution_summary["end_time"] = datetime.now().isoformat()
        self.execution_summary["total_duration"] = end_time - start_time
        
        logger.info("集成测试套件执行完成")
        
        return self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self) -> Dict:
        """生成综合测试报告"""
        logger.info("生成综合测试报告...")
        
        # 统计各类测试结果
        test_statistics = {
            "total_tests": len(self.test_results),
            "passed_tests": 0,
            "failed_tests": 0,
            "error_tests": 0,
            "timeout_tests": 0,
            "skipped_tests": 0
        }
        
        # 收集所有问题和建议
        all_issues = []
        all_recommendations = []
        
        # 按优先级分组测试结果
        priority_results = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        for script, result in self.test_results.items():
            # 统计测试状态
            status = result["status"]
            if status == "passed":
                test_statistics["passed_tests"] += 1
            elif status == "failed":
                test_statistics["failed_tests"] += 1
            elif status == "error":
                test_statistics["error_tests"] += 1
            elif status == "timeout":
                test_statistics["timeout_tests"] += 1
            else:
                test_statistics["skipped_tests"] += 1
            
            # 按优先级分组
            priority = result.get("priority", "low")
            priority_results[priority].append(result)
            
            # 收集问题和建议
            if "details" in result and result["details"]:
                details = result["details"]
                
                # 收集漏洞和问题
                if "vulnerabilities" in details:
                    all_issues.extend(details["vulnerabilities"])
                if "overall_vulnerabilities" in details:
                    all_issues.extend(details["overall_vulnerabilities"])
                if "issues" in details:
                    all_issues.extend(details["issues"])
                
                # 收集建议
                if "recommendations" in details:
                    all_recommendations.extend(details["recommendations"])
                if "security_recommendations" in details:
                    all_recommendations.extend(details["security_recommendations"])
                
                # 从摘要中收集建议
                if "summary" in details and "security_recommendations" in details["summary"]:
                    all_recommendations.extend(details["summary"]["security_recommendations"])
        
        # 计算成功率
        success_rate = (test_statistics["passed_tests"] / test_statistics["total_tests"] * 100) if test_statistics["total_tests"] > 0 else 0
        
        # 确定整体质量等级
        if success_rate >= 95 and test_statistics["failed_tests"] == 0:
            quality_level = "优秀"
        elif success_rate >= 90 and test_statistics["failed_tests"] <= 1:
            quality_level = "良好"
        elif success_rate >= 80:
            quality_level = "一般"
        elif success_rate >= 70:
            quality_level = "需要改进"
        else:
            quality_level = "存在严重问题"
        
        # 生成关键指标
        key_metrics = {
            "success_rate": success_rate,
            "total_issues_found": len(all_issues),
            "high_priority_tests_passed": sum(1 for r in priority_results["high"] if r["status"] == "passed"),
            "high_priority_tests_total": len(priority_results["high"]),
            "average_test_duration": sum(r["duration"] for r in self.test_results.values()) / len(self.test_results) if self.test_results else 0
        }
        
        # 生成测试建议
        test_recommendations = self._generate_test_recommendations(
            test_statistics, all_issues, priority_results
        )
        
        # 构建综合报告
        comprehensive_report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "test_environment": "集成测试环境",
                "test_suite_version": "1.0.0",
                "total_execution_time": self.execution_summary["total_duration"]
            },
            "execution_summary": self.execution_summary,
            "test_statistics": test_statistics,
            "key_metrics": key_metrics,
            "quality_assessment": {
                "overall_quality_level": quality_level,
                "success_rate": success_rate,
                "critical_issues_count": len([issue for issue in all_issues if any(keyword in issue.lower() for keyword in ["严重", "高风险", "critical", "high"])]),
                "readiness_for_production": success_rate >= 90 and test_statistics["failed_tests"] == 0
            },
            "test_results_by_priority": priority_results,
            "detailed_test_results": self.test_results,
            "issues_summary": {
                "total_issues": len(all_issues),
                "unique_issues": list(set(all_issues)),
                "issue_categories": self._categorize_issues(all_issues)
            },
            "recommendations": {
                "test_recommendations": test_recommendations,
                "technical_recommendations": list(set(all_recommendations))[:10],  # 去重并限制数量
                "next_steps": self._generate_next_steps(test_statistics, quality_level)
            }
        }
        
        # 保存综合报告
        report_filename = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
        
        # 生成HTML报告
        html_report = self._generate_html_report(comprehensive_report)
        html_filename = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        logger.info(f"综合测试报告已生成: {report_filename}")
        logger.info(f"HTML测试报告已生成: {html_filename}")
        
        return comprehensive_report
    
    def _categorize_issues(self, issues: List[str]) -> Dict[str, List[str]]:
        """将问题按类别分组"""
        categories = {
            "安全问题": [],
            "性能问题": [],
            "功能问题": [],
            "权限问题": [],
            "数据问题": [],
            "其他问题": []
        }
        
        for issue in issues:
            issue_lower = issue.lower()
            if any(keyword in issue_lower for keyword in ["安全", "漏洞", "注入", "xss", "sql", "security"]):
                categories["安全问题"].append(issue)
            elif any(keyword in issue_lower for keyword in ["性能", "响应", "超时", "慢", "performance"]):
                categories["性能问题"].append(issue)
            elif any(keyword in issue_lower for keyword in ["权限", "访问", "授权", "认证", "permission", "auth"]):
                categories["权限问题"].append(issue)
            elif any(keyword in issue_lower for keyword in ["数据", "同步", "一致性", "data"]):
                categories["数据问题"].append(issue)
            elif any(keyword in issue_lower for keyword in ["功能", "接口", "api", "function"]):
                categories["功能问题"].append(issue)
            else:
                categories["其他问题"].append(issue)
        
        # 移除空分类
        return {k: v for k, v in categories.items() if v}
    
    def _generate_test_recommendations(self, statistics: Dict, issues: List[str], priority_results: Dict) -> List[str]:
        """生成测试建议"""
        recommendations = []
        
        # 基于测试结果的建议
        if statistics["failed_tests"] > 0:
            recommendations.append(f"修复 {statistics['failed_tests']} 个失败的测试用例")
        
        if statistics["error_tests"] > 0:
            recommendations.append(f"解决 {statistics['error_tests']} 个测试执行错误")
        
        if statistics["timeout_tests"] > 0:
            recommendations.append(f"优化 {statistics['timeout_tests']} 个超时的测试，可能存在性能问题")
        
        # 基于优先级的建议
        high_priority_failed = sum(1 for r in priority_results["high"] if r["status"] != "passed")
        if high_priority_failed > 0:
            recommendations.append(f"优先修复 {high_priority_failed} 个高优先级测试问题")
        
        # 基于问题类型的建议
        if len(issues) > 10:
            recommendations.append("发现的问题较多，建议进行全面的代码审查")
        
        # 通用建议
        if not recommendations:
            recommendations.append("测试结果良好，继续保持代码质量")
        
        recommendations.extend([
            "定期执行集成测试以确保系统稳定性",
            "建立持续集成流水线自动化测试",
            "完善测试用例覆盖率",
            "建立测试数据管理机制"
        ])
        
        return recommendations
    
    def _generate_next_steps(self, statistics: Dict, quality_level: str) -> List[str]:
        """生成下一步行动建议"""
        next_steps = []
        
        if quality_level in ["存在严重问题", "需要改进"]:
            next_steps.extend([
                "立即修复所有失败的高优先级测试",
                "进行代码审查和重构",
                "暂停生产部署直到问题解决"
            ])
        elif quality_level == "一般":
            next_steps.extend([
                "修复失败的测试用例",
                "优化性能问题",
                "增强错误处理机制"
            ])
        elif quality_level == "良好":
            next_steps.extend([
                "解决剩余的小问题",
                "完善测试覆盖率",
                "准备生产环境部署"
            ])
        else:  # 优秀
            next_steps.extend([
                "可以考虑生产环境部署",
                "建立监控和告警机制",
                "制定运维和维护计划"
            ])
        
        return next_steps
    
    def _generate_html_report(self, report_data: Dict) -> str:
        """生成HTML格式的测试报告"""
        # 准备模板数据
        metadata = report_data["report_metadata"]
        summary = report_data["execution_summary"]
        statistics = report_data["test_statistics"]
        metrics = report_data["key_metrics"]
        quality = report_data["quality_assessment"]
        recommendations = report_data["recommendations"]
        
        # 生成测试结果HTML
        test_results_html = ""
        for script, result in report_data["detailed_test_results"].items():
            status_class = result["status"]
            test_results_html += f"""
            <div class="test-result {status_class}">
                <h4>{result['test_name']} <span class="status-{status_class}">({result['status'].upper()})</span></h4>
                <p><strong>描述:</strong> {result['description']}</p>
                <p><strong>优先级:</strong> {result['priority']}</p>
                <p><strong>执行时间:</strong> {result['duration']:.2f}秒</p>
                {f'<p><strong>错误信息:</strong> {result["error"]}</p>' if result.get('error') else ''}
            </div>
            """
        
        # 生成问题HTML
        issues_html = ""
        if report_data["issues_summary"]["total_issues"] > 0:
            issues_html = f"""
            <div class="issues">
                <h2>发现的问题 ({report_data['issues_summary']['total_issues']}个)</h2>
            """
            
            for category, issues in report_data["issues_summary"]["issue_categories"].items():
                if issues:
                    issues_html += f"<h3>{category} ({len(issues)}个)</h3><ul>"
                    for issue in issues[:5]:  # 只显示前5个
                        issues_html += f"<li>{issue}</li>"
                    if len(issues) > 5:
                        issues_html += f"<li>... 还有 {len(issues) - 5} 个问题</li>"
                    issues_html += "</ul>"
            
            issues_html += "</div>"
        
        # 生成建议HTML
        test_recommendations_html = "\n".join([f"<li>{rec}</li>" for rec in recommendations["test_recommendations"][:5]])
        technical_recommendations_html = "\n".join([f"<li>{rec}</li>" for rec in recommendations["technical_recommendations"][:5]])
        next_steps_html = "\n".join([f"<li>{step}</li>" for step in recommendations["next_steps"]])
        
        # 构建完整的HTML报告
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能教学助手集成测试报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #333; }}
        .header {{ text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .summary-card h3 {{ margin-top: 0; color: #007bff; }}
        .metric {{ font-size: 24px; font-weight: bold; color: #28a745; }}
        .status-passed {{ color: #28a745; }}
        .status-failed {{ color: #dc3545; }}
        .status-error {{ color: #fd7e14; }}
        .status-timeout {{ color: #6f42c1; }}
        .test-result {{ margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #ddd; }}
        .test-result.passed {{ border-left-color: #28a745; background-color: #d4edda; }}
        .test-result.failed {{ border-left-color: #dc3545; background-color: #f8d7da; }}
        .test-result.error {{ border-left-color: #fd7e14; background-color: #fff3cd; }}
        .test-result.timeout {{ border-left-color: #6f42c1; background-color: #e2e3f0; }}
        .recommendations {{ background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .recommendations ul {{ margin: 10px 0; }}
        .issues {{ background: #fff5f5; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #fed7d7; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
        .progress-bar {{ width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background-color: #28a745; transition: width 0.3s ease; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>智能教学助手集成测试报告</h1>
            <p>生成时间: {metadata["generated_at"]}</p>
            <p>测试环境: {metadata["test_environment"]}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>测试概览</h3>
                <div class="metric">{statistics["total_tests"]}</div>
                <p>总测试数</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {metrics["success_rate"]}%"></div>
                </div>
                <p>成功率: {metrics["success_rate"]:.1f}%</p>
            </div>
            
            <div class="summary-card">
                <h3>质量评估</h3>
                <div class="metric">{quality["overall_quality_level"]}</div>
                <p>整体质量等级</p>
                <p>生产就绪: {'是' if quality["readiness_for_production"] else '否'}</p>
            </div>
            
            <div class="summary-card">
                <h3>执行时间</h3>
                <div class="metric">{metadata["total_execution_time"]:.1f}s</div>
                <p>总执行时间</p>
                <p>平均测试时间: {metrics["average_test_duration"]:.1f}s</p>
            </div>
            
            <div class="summary-card">
                <h3>问题统计</h3>
                <div class="metric">{report_data["issues_summary"]["total_issues"]}</div>
                <p>发现问题总数</p>
                <p>关键问题: {quality["critical_issues_count"]}</p>
            </div>
        </div>
        
        <h2>测试结果详情</h2>
        <div class="test-results">
            {test_results_html}
        </div>
        
        {issues_html}
        
        <div class="recommendations">
            <h2>改进建议</h2>
            <h3>测试建议</h3>
            <ul>
                {test_recommendations_html}
            </ul>
            <h3>技术建议</h3>
            <ul>
                {technical_recommendations_html}
            </ul>
            <h3>下一步行动</h3>
            <ul>
                {next_steps_html}
            </ul>
        </div>
        
        <div class="footer">
            <p>此报告由智能教学助手集成测试系统自动生成</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def print_summary(self, report: Dict):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("智能教学助手集成测试摘要")
        print("="*60)
        
        summary = report["execution_summary"]
        statistics = report["test_statistics"]
        metrics = report["key_metrics"]
        quality = report["quality_assessment"]
        
        print(f"\n执行概览:")
        print(f"  开始时间: {summary['start_time']}")
        print(f"  结束时间: {summary['end_time']}")
        print(f"  总执行时间: {summary['total_duration']:.1f}秒")
        
        print(f"\n测试统计:")
        print(f"  总测试数: {statistics['total_tests']}")
        print(f"  通过: {statistics['passed_tests']} ({statistics['passed_tests']/statistics['total_tests']*100:.1f}%)")
        print(f"  失败: {statistics['failed_tests']}")
        print(f"  错误: {statistics['error_tests']}")
        print(f"  超时: {statistics['timeout_tests']}")
        print(f"  跳过: {statistics['skipped_tests']}")
        
        print(f"\n质量评估:")
        print(f"  整体质量等级: {quality['overall_quality_level']}")
        print(f"  成功率: {metrics['success_rate']:.1f}%")
        print(f"  发现问题总数: {metrics['total_issues_found']}")
        print(f"  生产就绪: {'是' if quality['readiness_for_production'] else '否'}")
        
        if report["issues_summary"]["total_issues"] > 0:
            print(f"\n主要问题类别:")
            for category, issues in report["issues_summary"]["issue_categories"].items():
                if issues:
                    print(f"  {category}: {len(issues)}个")
        
        print(f"\n关键建议:")
        for i, rec in enumerate(report["recommendations"]["next_steps"][:3], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)

# 主执行函数
async def main():
    """主执行函数"""
    try:
        # 初始化测试运行器
        runner = IntegrationTestRunner()
        
        # 运行所有测试
        report = await runner.run_all_tests(skip_failed=False)
        
        # 打印摘要
        runner.print_summary(report)
        
        return report
        
    except Exception as e:
        logger.error(f"集成测试执行失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())