#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手并发访问测试

功能：
1. 测试多用户并发登录
2. 测试并发API调用
3. 测试系统负载能力
4. 测试资源竞争处理
5. 测试并发数据操作

作者：测试工程师
日期：2024年12月
"""

import json
import asyncio
import aiohttp
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('concurrent_access_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ConcurrentAccessTester:
    """并发访问测试类"""
    
    def __init__(self, config_file: str = "test_accounts.json", base_url: str = "http://localhost:8000"):
        self.config_file = config_file
        self.base_url = base_url
        self.test_accounts = {}
        self.session_tokens = {}
        self.test_results = []
        self.lock = threading.Lock()
        
        # 并发测试配置
        self.max_concurrent_users = 10
        self.test_duration = 60  # 秒
        self.request_interval = 1  # 秒
        
        # 加载测试账号
        self._load_test_accounts()
        
        logger.info(f"并发访问测试器初始化完成，基础URL: {self.base_url}")
    
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
    
    async def authenticate_user(self, account_id: str) -> Dict:
        """用户认证"""
        if account_id not in self.test_accounts:
            return {"success": False, "error": f"账号 {account_id} 不存在"}
        
        account = self.test_accounts[account_id]
        
        if account['status'] != 'active':
            return {"success": False, "error": f"账号 {account_id} 状态为 {account['status']}"}
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "username": account['username'],
                    "password": account['password']
                }
                
                async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        token = result.get('token', '')
                        
                        with self.lock:
                            self.session_tokens[account_id] = token
                        
                        return {
                            "success": True,
                            "account_id": account_id,
                            "role": account['role'],
                            "response_time": response_time,
                            "token": token
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "account_id": account_id,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            return {
                "success": False,
                "account_id": account_id,
                "error": str(e)
            }
    
    async def test_concurrent_login(self, account_ids: List[str]) -> Dict:
        """测试并发登录"""
        logger.info(f"开始测试 {len(account_ids)} 个账号的并发登录...")
        
        start_time = time.time()
        
        # 创建并发登录任务
        login_tasks = [self.authenticate_user(account_id) for account_id in account_ids]
        
        # 执行并发登录
        login_results = await asyncio.gather(*login_tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # 分析登录结果
        successful_logins = 0
        failed_logins = 0
        login_times = []
        role_stats = {}
        
        for result in login_results:
            if isinstance(result, Exception):
                failed_logins += 1
                logger.error(f"并发登录异常: {result}")
            elif isinstance(result, dict):
                if result.get("success", False):
                    successful_logins += 1
                    login_times.append(result.get("response_time", 0))
                    
                    role = result.get("role", "未知")
                    if role not in role_stats:
                        role_stats[role] = {"successful": 0, "failed": 0}
                    role_stats[role]["successful"] += 1
                else:
                    failed_logins += 1
                    role = self.test_accounts.get(result.get("account_id", ""), {}).get("role", "未知")
                    if role not in role_stats:
                        role_stats[role] = {"successful": 0, "failed": 0}
                    role_stats[role]["failed"] += 1
        
        # 计算统计信息
        total_logins = len(account_ids)
        success_rate = (successful_logins / total_logins * 100) if total_logins > 0 else 0
        avg_login_time = sum(login_times) / len(login_times) if login_times else 0
        max_login_time = max(login_times) if login_times else 0
        min_login_time = min(login_times) if login_times else 0
        
        return {
            "test_type": "并发登录测试",
            "total_accounts": total_logins,
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "success_rate": success_rate,
            "total_time": total_time,
            "avg_login_time": avg_login_time,
            "max_login_time": max_login_time,
            "min_login_time": min_login_time,
            "role_statistics": role_stats,
            "concurrent_level": len(account_ids)
        }
    
    async def make_api_request(self, account_id: str, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """发起API请求"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            return {
                                "success": True,
                                "account_id": account_id,
                                "endpoint": endpoint,
                                "method": method,
                                "response_time": response_time,
                                "status_code": response.status,
                                "data_size": len(str(result))
                            }
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "account_id": account_id,
                                "endpoint": endpoint,
                                "method": method,
                                "response_time": response_time,
                                "status_code": response.status,
                                "error": error_text
                            }
                
                elif method.upper() == "POST":
                    async with session.post(f"{self.base_url}{endpoint}", json=data, headers=headers) as response:
                        response_time = time.time() - start_time
                        
                        if response.status in [200, 201]:
                            result = await response.json()
                            return {
                                "success": True,
                                "account_id": account_id,
                                "endpoint": endpoint,
                                "method": method,
                                "response_time": response_time,
                                "status_code": response.status,
                                "data_size": len(str(result))
                            }
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "account_id": account_id,
                                "endpoint": endpoint,
                                "method": method,
                                "response_time": response_time,
                                "status_code": response.status,
                                "error": error_text
                            }
        
        except Exception as e:
            return {
                "success": False,
                "account_id": account_id,
                "endpoint": endpoint,
                "method": method,
                "error": str(e)
            }
    
    async def test_concurrent_api_calls(self, account_ids: List[str], duration: int = 30) -> Dict:
        """测试并发API调用"""
        logger.info(f"开始测试 {len(account_ids)} 个账号的并发API调用，持续 {duration} 秒...")
        
        # 定义测试的API端点
        api_endpoints = [
            ("/api/user/profile", "GET", None),
            ("/api/grades/list", "GET", None),
            ("/api/lesson/list", "GET", None),
            ("/api/classroom/status", "GET", None),
            ("/api/data/statistics", "GET", None),
            ("/api/grades/analysis", "POST", {
                "exam_name": "测试考试",
                "subject": "数学",
                "analysis_type": "basic"
            }),
            ("/api/lesson/material-analysis", "POST", {
                "title": "测试教材",
                "content": "测试内容",
                "subject": "数学"
            })
        ]
        
        start_time = time.time()
        end_time = start_time + duration
        
        all_results = []
        tasks = []
        
        # 为每个账号创建持续的API调用任务
        async def continuous_api_calls(account_id: str):
            account_results = []
            while time.time() < end_time:
                # 随机选择一个API端点
                endpoint, method, data = random.choice(api_endpoints)
                
                # 发起API请求
                result = await self.make_api_request(account_id, endpoint, method, data)
                account_results.append(result)
                
                # 随机等待一段时间
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            return account_results
        
        # 创建所有账号的并发任务
        for account_id in account_ids:
            task = continuous_api_calls(account_id)
            tasks.append(task)
        
        # 执行并发任务
        account_results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_test_time = time.time() - start_time
        
        # 合并所有结果
        for account_results in account_results_list:
            if isinstance(account_results, list):
                all_results.extend(account_results)
            elif isinstance(account_results, Exception):
                logger.error(f"并发API调用异常: {account_results}")
        
        # 分析结果
        total_requests = len(all_results)
        successful_requests = sum(1 for result in all_results if result.get("success", False))
        failed_requests = total_requests - successful_requests
        
        # 计算响应时间统计
        response_times = [result.get("response_time", 0) for result in all_results if result.get("success", False)]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # 计算请求频率
        requests_per_second = total_requests / total_test_time if total_test_time > 0 else 0
        
        # 统计各端点的调用情况
        endpoint_stats = {}
        for result in all_results:
            endpoint = result.get("endpoint", "未知")
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"total": 0, "successful": 0, "failed": 0}
            
            endpoint_stats[endpoint]["total"] += 1
            if result.get("success", False):
                endpoint_stats[endpoint]["successful"] += 1
            else:
                endpoint_stats[endpoint]["failed"] += 1
        
        # 统计状态码分布
        status_code_stats = {}
        for result in all_results:
            status_code = result.get("status_code", 0)
            if status_code:
                status_code_stats[status_code] = status_code_stats.get(status_code, 0) + 1
        
        return {
            "test_type": "并发API调用测试",
            "test_duration": total_test_time,
            "concurrent_users": len(account_ids),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "requests_per_second": requests_per_second,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "endpoint_statistics": endpoint_stats,
            "status_code_distribution": status_code_stats
        }
    
    async def test_resource_competition(self, account_ids: List[str]) -> Dict:
        """测试资源竞争"""
        logger.info(f"开始测试 {len(account_ids)} 个账号的资源竞争...")
        
        # 模拟对同一资源的并发访问
        resource_id = "shared_resource_001"
        
        async def access_shared_resource(account_id: str, operation_type: str):
            """访问共享资源"""
            try:
                if operation_type == "read":
                    result = await self.make_api_request(
                        account_id, 
                        f"/api/resource/{resource_id}", 
                        "GET"
                    )
                elif operation_type == "write":
                    data = {
                        "resource_id": resource_id,
                        "data": f"来自账号 {account_id} 的数据",
                        "timestamp": datetime.now().isoformat()
                    }
                    result = await self.make_api_request(
                        account_id, 
                        f"/api/resource/{resource_id}", 
                        "POST", 
                        data
                    )
                else:
                    result = {"success": False, "error": "未知操作类型"}
                
                result["operation_type"] = operation_type
                return result
                
            except Exception as e:
                return {
                    "success": False,
                    "account_id": account_id,
                    "operation_type": operation_type,
                    "error": str(e)
                }
        
        # 创建混合的读写操作任务
        tasks = []
        for account_id in account_ids:
            # 每个账号执行多种操作
            operations = ["read", "write", "read", "write", "read"]
            for operation in operations:
                task = access_shared_resource(account_id, operation)
                tasks.append(task)
        
        start_time = time.time()
        
        # 执行并发资源访问
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # 分析结果
        total_operations = len(results)
        successful_operations = 0
        failed_operations = 0
        read_operations = 0
        write_operations = 0
        read_success = 0
        write_success = 0
        
        for result in results:
            if isinstance(result, Exception):
                failed_operations += 1
                logger.error(f"资源竞争测试异常: {result}")
            elif isinstance(result, dict):
                operation_type = result.get("operation_type", "未知")
                
                if operation_type == "read":
                    read_operations += 1
                    if result.get("success", False):
                        read_success += 1
                        successful_operations += 1
                    else:
                        failed_operations += 1
                elif operation_type == "write":
                    write_operations += 1
                    if result.get("success", False):
                        write_success += 1
                        successful_operations += 1
                    else:
                        failed_operations += 1
                else:
                    failed_operations += 1
        
        return {
            "test_type": "资源竞争测试",
            "resource_id": resource_id,
            "concurrent_users": len(account_ids),
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "overall_success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0,
            "read_operations": {
                "total": read_operations,
                "successful": read_success,
                "success_rate": (read_success / read_operations * 100) if read_operations > 0 else 0
            },
            "write_operations": {
                "total": write_operations,
                "successful": write_success,
                "success_rate": (write_success / write_operations * 100) if write_operations > 0 else 0
            },
            "test_duration": total_time
        }
    
    async def test_load_capacity(self, max_users: int = 20, step: int = 5) -> Dict:
        """测试系统负载能力"""
        logger.info(f"开始测试系统负载能力，最大用户数: {max_users}...")
        
        # 获取活跃账号
        active_accounts = [acc_id for acc_id, acc in self.test_accounts.items() 
                          if acc['status'] == 'active']
        
        if len(active_accounts) < max_users:
            logger.warning(f"活跃账号数量 ({len(active_accounts)}) 少于最大测试用户数 ({max_users})")
            max_users = len(active_accounts)
        
        load_test_results = []
        
        # 逐步增加并发用户数
        for user_count in range(step, max_users + 1, step):
            logger.info(f"测试 {user_count} 个并发用户...")
            
            test_accounts = active_accounts[:user_count]
            
            # 先进行并发登录
            login_result = await self.test_concurrent_login(test_accounts)
            
            if login_result["success_rate"] > 50:  # 如果登录成功率超过50%，继续API测试
                # 进行并发API调用测试
                api_result = await self.test_concurrent_api_calls(test_accounts, duration=15)
                
                load_test_results.append({
                    "concurrent_users": user_count,
                    "login_success_rate": login_result["success_rate"],
                    "api_success_rate": api_result["success_rate"],
                    "avg_response_time": api_result["avg_response_time"],
                    "requests_per_second": api_result["requests_per_second"],
                    "system_stable": (login_result["success_rate"] > 80 and 
                                     api_result["success_rate"] > 80 and 
                                     api_result["avg_response_time"] < 5.0)
                })
            else:
                load_test_results.append({
                    "concurrent_users": user_count,
                    "login_success_rate": login_result["success_rate"],
                    "api_success_rate": 0,
                    "avg_response_time": 0,
                    "requests_per_second": 0,
                    "system_stable": False,
                    "note": "登录成功率过低，跳过API测试"
                })
            
            # 清理会话令牌
            with self.lock:
                self.session_tokens.clear()
            
            # 等待系统恢复
            await asyncio.sleep(2)
        
        # 分析负载测试结果
        max_stable_users = 0
        performance_degradation_point = 0
        
        for result in load_test_results:
            if result["system_stable"]:
                max_stable_users = result["concurrent_users"]
            elif performance_degradation_point == 0:
                performance_degradation_point = result["concurrent_users"]
        
        return {
            "test_type": "系统负载能力测试",
            "max_tested_users": max_users,
            "max_stable_users": max_stable_users,
            "performance_degradation_point": performance_degradation_point,
            "load_test_details": load_test_results,
            "system_capacity_rating": "优秀" if max_stable_users >= max_users * 0.8 else 
                                     "良好" if max_stable_users >= max_users * 0.6 else 
                                     "一般" if max_stable_users >= max_users * 0.4 else "较差"
        }
    
    async def run_full_concurrent_test(self) -> Dict:
        """运行完整的并发访问测试套件"""
        logger.info("开始执行完整并发访问测试套件...")
        
        test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
        # 获取活跃账号
        active_accounts = [acc_id for acc_id, acc in self.test_accounts.items() 
                          if acc['status'] == 'active']
        
        logger.info(f"找到 {len(active_accounts)} 个活跃测试账号")
        
        if len(active_accounts) < 3:
            logger.error("活跃账号数量不足，无法进行并发测试")
            return test_results
        
        # 1. 并发登录测试
        logger.info("执行并发登录测试...")
        login_test_accounts = active_accounts[:min(10, len(active_accounts))]
        login_result = await self.test_concurrent_login(login_test_accounts)
        test_results["tests"]["concurrent_login"] = login_result
        
        # 2. 并发API调用测试
        logger.info("执行并发API调用测试...")
        api_test_accounts = active_accounts[:min(8, len(active_accounts))]
        
        # 先认证这些账号
        for account_id in api_test_accounts:
            await self.authenticate_user(account_id)
        
        api_result = await self.test_concurrent_api_calls(api_test_accounts, duration=30)
        test_results["tests"]["concurrent_api_calls"] = api_result
        
        # 3. 资源竞争测试
        logger.info("执行资源竞争测试...")
        resource_test_accounts = active_accounts[:min(6, len(active_accounts))]
        resource_result = await self.test_resource_competition(resource_test_accounts)
        test_results["tests"]["resource_competition"] = resource_result
        
        # 4. 系统负载能力测试
        logger.info("执行系统负载能力测试...")
        max_load_users = min(15, len(active_accounts))
        load_result = await self.test_load_capacity(max_load_users, step=3)
        test_results["tests"]["load_capacity"] = load_result
        
        # 生成测试摘要
        test_results["end_time"] = datetime.now().isoformat()
        
        summary = {
            "total_accounts_available": len(active_accounts),
            "concurrent_login": {
                "success_rate": login_result.get("success_rate", 0),
                "avg_login_time": login_result.get("avg_login_time", 0),
                "concurrent_level": login_result.get("concurrent_level", 0)
            },
            "concurrent_api_calls": {
                "success_rate": api_result.get("success_rate", 0),
                "requests_per_second": api_result.get("requests_per_second", 0),
                "avg_response_time": api_result.get("avg_response_time", 0)
            },
            "resource_competition": {
                "overall_success_rate": resource_result.get("overall_success_rate", 0),
                "read_success_rate": resource_result.get("read_operations", {}).get("success_rate", 0),
                "write_success_rate": resource_result.get("write_operations", {}).get("success_rate", 0)
            },
            "load_capacity": {
                "max_stable_users": load_result.get("max_stable_users", 0),
                "system_capacity_rating": load_result.get("system_capacity_rating", "未知")
            }
        }
        
        # 计算总体评分
        scores = [
            min(summary["concurrent_login"]["success_rate"], 100),
            min(summary["concurrent_api_calls"]["success_rate"], 100),
            min(summary["resource_competition"]["overall_success_rate"], 100)
        ]
        
        overall_score = sum(scores) / len(scores) if scores else 0
        summary["overall_concurrent_performance_score"] = overall_score
        
        if overall_score >= 90:
            summary["performance_rating"] = "优秀"
        elif overall_score >= 80:
            summary["performance_rating"] = "良好"
        elif overall_score >= 70:
            summary["performance_rating"] = "一般"
        else:
            summary["performance_rating"] = "需要改进"
        
        test_results["summary"] = summary
        
        # 保存测试结果
        with open("concurrent_access_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        logger.info("并发访问测试套件执行完成")
        logger.info(f"总体并发性能评分: {overall_score:.1f}分 ({summary['performance_rating']})")
        logger.info(f"最大稳定用户数: {summary['load_capacity']['max_stable_users']}")
        
        return test_results

# 主执行函数
async def main():
    """主执行函数"""
    try:
        # 初始化并发访问测试器
        tester = ConcurrentAccessTester()
        
        # 运行完整并发访问测试
        results = await tester.run_full_concurrent_test()
        
        # 输出测试结果摘要
        print("\n" + "="*50)
        print("并发访问测试结果摘要")
        print("="*50)
        
        summary = results["summary"]
        print(f"可用测试账号: {summary['total_accounts_available']}")
        print(f"总体性能评分: {summary['overall_concurrent_performance_score']:.1f}分")
        print(f"性能等级: {summary['performance_rating']}")
        
        print("\n各项测试结果:")
        
        login_summary = summary["concurrent_login"]
        print(f"  并发登录: {login_summary['success_rate']:.1f}% (平均 {login_summary['avg_login_time']:.2f}s)")
        
        api_summary = summary["concurrent_api_calls"]
        print(f"  并发API调用: {api_summary['success_rate']:.1f}% ({api_summary['requests_per_second']:.1f} req/s)")
        
        resource_summary = summary["resource_competition"]
        print(f"  资源竞争: {resource_summary['overall_success_rate']:.1f}%")
        
        load_summary = summary["load_capacity"]
        print(f"  负载能力: 最大稳定用户数 {load_summary['max_stable_users']} ({load_summary['system_capacity_rating']})")
        
        print("\n详细测试结果已保存到: concurrent_access_test_results.json")
        print("测试日志已保存到: concurrent_access_test.log")
        
    except Exception as e:
        logger.error(f"并发访问测试执行失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())