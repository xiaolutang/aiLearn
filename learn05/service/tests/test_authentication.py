#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手认证流程测试

功能：
1. 测试所有角色的登录认证
2. 验证会话管理
3. 测试登出功能
4. 验证无效凭据处理
5. 测试会话超时

作者：测试工程师
日期：2024年12月
"""

import json
import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('authentication_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AuthenticationTester:
    """认证测试类"""
    
    def __init__(self, config_file: str = "test_accounts.json", base_url: str = "http://localhost:8000"):
        self.config_file = config_file
        self.base_url = base_url
        self.test_accounts = {}
        self.session_tokens = {}
        self.test_results = []
        
        # 加载测试账号
        self._load_test_accounts()
        
        logger.info(f"认证测试器初始化完成，基础URL: {self.base_url}")
    
    def _load_test_accounts(self):
        """加载测试账号配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
                # 为每个账号添加id字段
                self.test_accounts = {}
                for i, acc in enumerate(accounts):
                    acc['id'] = acc['username']  # 使用用户名作为id
                    self.test_accounts[acc['id']] = acc
            logger.info(f"成功加载 {len(self.test_accounts)} 个测试账号")
        except Exception as e:
            logger.error(f"加载测试账号失败: {e}")
            raise
    
    async def test_valid_login(self, account_id: str) -> Dict:
        """测试有效登录"""
        if account_id not in self.test_accounts:
            return {"success": False, "error": "账号不存在"}
        
        account = self.test_accounts[account_id]
        
        # 检查账号状态
        if account['status'] != 'active':
            return {"success": False, "error": f"账号状态为 {account['status']}"}
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                login_data = aiohttp.FormData()
                login_data.add_field('username', account['username'])
                login_data.add_field('password', account['password'])
                
                async with session.post(f"{self.base_url}/api/auth/login", data=login_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        token = result.get('access_token', '')
                        
                        if token:
                            self.session_tokens[account_id] = token
                            logger.info(f"账号 {account_id} ({account['role']}) 登录成功，响应时间: {response_time:.2f}s")
                            
                            return {
                                "success": True,
                                "token": token,
                                "response_time": response_time,
                                "user_info": {
                                    "user_id": result.get('user_id'),
                                    "username": result.get('username'),
                                    "email": result.get('email')
                                }
                            }
                        else:
                            return {"success": False, "error": "未返回有效token"}
                    else:
                        error_text = await response.text()
                        logger.error(f"账号 {account_id} 登录失败，状态码: {response.status}, 错误: {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"账号 {account_id} 登录异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_invalid_credentials(self) -> List[Dict]:
        """测试无效凭据"""
        logger.info("开始测试无效凭据...")
        
        invalid_cases = [
            {"username": "invalid_user", "password": "invalid_pass", "case": "完全无效的用户名和密码"},
            {"username": "admin", "password": "wrong_password", "case": "有效用户名，无效密码"},
            {"username": "wrong_user", "password": "Admin123!", "case": "无效用户名，有效密码格式"},
            {"username": "", "password": "password", "case": "空用户名"},
            {"username": "admin", "password": "", "case": "空密码"},
            {"username": "", "password": "", "case": "空用户名和密码"}
        ]
        
        results = []
        
        for case in invalid_cases:
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    form_data = aiohttp.FormData()
                    form_data.add_field('username', case['username'])
                    form_data.add_field('password', case['password'])
                    
                    async with session.post(f"{self.base_url}/api/auth/login", data=form_data) as response:
                        response_time = time.time() - start_time
                        
                        # 期望返回401或400状态码
                        expected_status = response.status in [400, 401, 422]
                        
                        result = {
                            "case": case["case"],
                            "username": case["username"],
                            "status_code": response.status,
                            "response_time": response_time,
                            "expected_failure": expected_status,
                            "success": expected_status
                        }
                        
                        if expected_status:
                            logger.info(f"无效凭据测试通过: {case['case']} - 状态码: {response.status}")
                        else:
                            logger.error(f"无效凭据测试失败: {case['case']} - 期望4xx，实际: {response.status}")
                        
                        results.append(result)
                        
            except Exception as e:
                logger.error(f"无效凭据测试异常: {case['case']} - {e}")
                results.append({
                    "case": case["case"],
                    "username": case["username"],
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    async def test_session_validation(self, account_id: str) -> Dict:
        """测试会话验证"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            token = self.session_tokens[account_id]
            headers = {"Authorization": f"Bearer {token}"}
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # 测试访问需要认证的端点
                async with session.get(f"{self.base_url}/api/auth/me", headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        user_info = await response.json()
                        logger.info(f"账号 {account_id} 会话验证成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "user_info": user_info
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"账号 {account_id} 会话验证失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"账号 {account_id} 会话验证异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_logout(self, account_id: str) -> Dict:
        """测试登出功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            token = self.session_tokens[account_id]
            headers = {"Authorization": f"Bearer {token}"}
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/auth/logout", headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        # 清除本地token
                        del self.session_tokens[account_id]
                        logger.info(f"账号 {account_id} 登出成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"账号 {account_id} 登出失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"账号 {account_id} 登出异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_invalid_token_access(self) -> Dict:
        """测试无效token访问"""
        logger.info("测试无效token访问...")
        
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "expired_token_12345",
            "",
            "malformed.token.here"
        ]
        
        results = []
        
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/api/auth/me", headers=headers) as response:
                        response_time = time.time() - start_time
                        
                        # 期望返回401状态码
                        expected_status = response.status == 401
                        
                        result = {
                            "token": token or "(empty)",
                            "status_code": response.status,
                            "response_time": response_time,
                            "expected_failure": expected_status,
                            "success": expected_status
                        }
                        
                        if expected_status:
                            logger.info(f"无效token测试通过: {token or '(empty)'} - 状态码: {response.status}")
                        else:
                            logger.error(f"无效token测试失败: {token or '(empty)'} - 期望401，实际: {response.status}")
                        
                        results.append(result)
                        
            except Exception as e:
                logger.error(f"无效token测试异常: {token} - {e}")
                results.append({
                    "token": token,
                    "error": str(e),
                    "success": False
                })
        
        return {"results": results, "success": all(r.get("success", False) for r in results)}
    
    async def test_concurrent_login(self, account_ids: List[str], max_concurrent: int = 5) -> Dict:
        """测试并发登录"""
        logger.info(f"开始并发登录测试，账号数: {len(account_ids)}, 并发数: {max_concurrent}")
        
        # 限制并发数
        test_accounts = account_ids[:max_concurrent]
        
        # 创建并发任务
        tasks = [self.test_valid_login(account_id) for account_id in test_accounts]
        
        start_time = time.time()
        
        # 执行并发登录
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # 统计结果
        successful_logins = 0
        failed_logins = 0
        
        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get("success", False):
                successful_logins += 1
            else:
                failed_logins += 1
                logger.error(f"并发登录失败: {test_accounts[i]} - {result}")
        
        logger.info(f"并发登录测试完成，成功: {successful_logins}, 失败: {failed_logins}, 总时间: {total_time:.2f}s")
        
        return {
            "success": failed_logins == 0,
            "total_accounts": len(test_accounts),
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "total_time": total_time,
            "average_time": total_time / len(test_accounts) if test_accounts else 0,
            "results": results
        }
    
    async def run_full_authentication_test(self) -> Dict:
        """运行完整的认证测试套件"""
        logger.info("开始执行完整认证测试套件...")
        
        test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
        # 获取活跃账号
        active_accounts = [acc_id for acc_id, acc in self.test_accounts.items() 
                          if acc['status'] == 'active']
        
        logger.info(f"找到 {len(active_accounts)} 个活跃测试账号")
        
        # 1. 测试有效登录
        logger.info("1. 测试有效登录...")
        login_results = {}
        for account_id in active_accounts:
            result = await self.test_valid_login(account_id)
            login_results[account_id] = result
        
        test_results["tests"]["valid_login"] = login_results
        
        # 2. 测试无效凭据
        logger.info("2. 测试无效凭据...")
        invalid_creds_results = await self.test_invalid_credentials()
        test_results["tests"]["invalid_credentials"] = invalid_creds_results
        
        # 3. 测试会话验证
        logger.info("3. 测试会话验证...")
        session_results = {}
        for account_id in active_accounts:
            if account_id in self.session_tokens:
                result = await self.test_session_validation(account_id)
                session_results[account_id] = result
        
        test_results["tests"]["session_validation"] = session_results
        
        # 4. 测试无效token访问
        logger.info("4. 测试无效token访问...")
        invalid_token_results = await self.test_invalid_token_access()
        test_results["tests"]["invalid_token"] = invalid_token_results
        
        # 5. 测试并发登录
        logger.info("5. 测试并发登录...")
        concurrent_results = await self.test_concurrent_login(active_accounts[:5])
        test_results["tests"]["concurrent_login"] = concurrent_results
        
        # 6. 测试登出
        logger.info("6. 测试登出...")
        logout_results = {}
        for account_id in list(self.session_tokens.keys()):
            result = await self.test_logout(account_id)
            logout_results[account_id] = result
        
        test_results["tests"]["logout"] = logout_results
        
        # 生成测试摘要
        test_results["end_time"] = datetime.now().isoformat()
        
        # 统计各项测试结果
        summary = {
            "total_accounts": len(active_accounts),
            "login_success_rate": 0,
            "session_validation_success_rate": 0,
            "logout_success_rate": 0,
            "invalid_credentials_handled": 0,
            "invalid_token_handled": 0,
            "concurrent_login_success": concurrent_results.get("success", False)
        }
        
        # 计算登录成功率
        successful_logins = sum(1 for r in login_results.values() if r.get("success", False))
        summary["login_success_rate"] = (successful_logins / len(active_accounts) * 100) if active_accounts else 0
        
        # 计算会话验证成功率
        successful_sessions = sum(1 for r in session_results.values() if r.get("success", False))
        summary["session_validation_success_rate"] = (successful_sessions / len(session_results) * 100) if session_results else 0
        
        # 计算登出成功率
        successful_logouts = sum(1 for r in logout_results.values() if r.get("success", False))
        summary["logout_success_rate"] = (successful_logouts / len(logout_results) * 100) if logout_results else 0
        
        # 计算无效凭据处理率
        handled_invalid_creds = sum(1 for r in invalid_creds_results if r.get("success", False))
        summary["invalid_credentials_handled"] = (handled_invalid_creds / len(invalid_creds_results) * 100) if invalid_creds_results else 0
        
        # 计算无效token处理率
        summary["invalid_token_handled"] = invalid_token_results.get("success", False)
        
        test_results["summary"] = summary
        
        # 保存测试结果
        with open("authentication_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        logger.info("认证测试套件执行完成")
        logger.info(f"登录成功率: {summary['login_success_rate']:.1f}%")
        logger.info(f"会话验证成功率: {summary['session_validation_success_rate']:.1f}%")
        logger.info(f"登出成功率: {summary['logout_success_rate']:.1f}%")
        logger.info(f"无效凭据处理率: {summary['invalid_credentials_handled']:.1f}%")
        logger.info(f"无效token处理: {'通过' if summary['invalid_token_handled'] else '失败'}")
        logger.info(f"并发登录测试: {'通过' if summary['concurrent_login_success'] else '失败'}")
        
        return test_results

# 主执行函数
async def main():
    """主执行函数"""
    try:
        # 初始化认证测试器
        tester = AuthenticationTester()
        
        # 运行完整认证测试
        results = await tester.run_full_authentication_test()
        
        # 输出测试结果摘要
        print("\n" + "="*50)
        print("认证测试结果摘要")
        print("="*50)
        
        summary = results["summary"]
        print(f"测试账号总数: {summary['total_accounts']}")
        print(f"登录成功率: {summary['login_success_rate']:.1f}%")
        print(f"会话验证成功率: {summary['session_validation_success_rate']:.1f}%")
        print(f"登出成功率: {summary['logout_success_rate']:.1f}%")
        print(f"无效凭据处理率: {summary['invalid_credentials_handled']:.1f}%")
        print(f"无效token处理: {'✓ 通过' if summary['invalid_token_handled'] else '✗ 失败'}")
        print(f"并发登录测试: {'✓ 通过' if summary['concurrent_login_success'] else '✗ 失败'}")
        
        # 计算总体通过率
        total_score = (
            summary['login_success_rate'] + 
            summary['session_validation_success_rate'] + 
            summary['logout_success_rate'] + 
            summary['invalid_credentials_handled'] +
            (100 if summary['invalid_token_handled'] else 0) +
            (100 if summary['concurrent_login_success'] else 0)
        ) / 6
        
        print(f"\n总体认证测试通过率: {total_score:.1f}%")
        print("\n详细测试结果已保存到: authentication_test_results.json")
        print("测试日志已保存到: authentication_test.log")
        
    except Exception as e:
        logger.error(f"认证测试执行失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())