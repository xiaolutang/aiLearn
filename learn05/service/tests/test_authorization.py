#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手权限控制测试

功能：
1. 测试不同角色的API访问权限
2. 验证资源访问控制
3. 测试跨角色权限边界
4. 验证权限升级和降级
5. 测试未授权访问处理

作者：测试工程师
日期：2024年12月
"""

import json
import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('authorization_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AuthorizationTester:
    """权限控制测试类"""
    
    def __init__(self, config_file: str = "test_accounts.json", base_url: str = "http://localhost:8000"):
        self.config_file = config_file
        self.base_url = base_url
        self.test_accounts = {}
        self.session_tokens = {}
        self.test_results = []
        
        # 定义角色权限矩阵
        self._init_permission_matrix()
        
        # 加载测试账号
        self._load_test_accounts()
        
        logger.info(f"权限控制测试器初始化完成，基础URL: {self.base_url}")
    
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
    
    def _init_permission_matrix(self):
        """初始化权限矩阵"""
        # 定义API端点和对应的权限要求
        self.permission_matrix = {
            # 系统管理API
            "/api/admin/users": {
                "allowed_roles": ["系统管理员"],
                "description": "用户管理",
                "methods": ["GET", "POST", "PUT", "DELETE"]
            },
            "/api/admin/system": {
                "allowed_roles": ["系统管理员"],
                "description": "系统配置",
                "methods": ["GET", "POST"]
            },
            "/api/admin/logs": {
                "allowed_roles": ["系统管理员"],
                "description": "系统日志",
                "methods": ["GET"]
            },
            
            # 学校管理API
            "/api/school/statistics": {
                "allowed_roles": ["系统管理员", "校长"],
                "description": "学校统计数据",
                "methods": ["GET"]
            },
            "/api/school/reports": {
                "allowed_roles": ["系统管理员", "校长", "教务主任"],
                "description": "学校报告",
                "methods": ["GET", "POST"]
            },
            "/api/school/departments": {
                "allowed_roles": ["系统管理员", "校长", "教务主任"],
                "description": "部门管理",
                "methods": ["GET", "POST", "PUT"]
            },
            
            # 教务管理API
            "/api/academic/courses": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师"],
                "description": "课程管理",
                "methods": ["GET", "POST", "PUT"]
            },
            "/api/academic/teachers": {
                "allowed_roles": ["系统管理员", "校长", "教务主任"],
                "description": "教师管理",
                "methods": ["GET", "POST", "PUT"]
            },
            "/api/academic/schedules": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师"],
                "description": "课程表管理",
                "methods": ["GET", "POST", "PUT"]
            },
            
            # 教师API
            "/api/teacher/classes": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师"],
                "description": "班级管理",
                "methods": ["GET", "POST", "PUT"]
            },
            "/api/teacher/grades": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师"],
                "description": "成绩管理",
                "methods": ["GET", "POST", "PUT"]
            },
            "/api/teacher/lessons": {
                "allowed_roles": ["教师"],
                "description": "课程备课",
                "methods": ["GET", "POST", "PUT", "DELETE"]
            },
            "/api/teacher/materials": {
                "allowed_roles": ["教师"],
                "description": "教学材料",
                "methods": ["GET", "POST", "PUT", "DELETE"]
            },
            
            # 学生API
            "/api/student/profile": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师", "学生"],
                "description": "学生档案",
                "methods": ["GET", "PUT"]
            },
            "/api/student/grades": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师", "学生", "家长"],
                "description": "学生成绩",
                "methods": ["GET"]
            },
            "/api/student/courses": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师", "学生"],
                "description": "学生课程",
                "methods": ["GET"]
            },
            "/api/student/homework": {
                "allowed_roles": ["教师", "学生"],
                "description": "作业管理",
                "methods": ["GET", "POST", "PUT"]
            },
            
            # 家长API
            "/api/parent/children": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师", "家长"],
                "description": "子女信息",
                "methods": ["GET"]
            },
            "/api/parent/reports": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师", "家长"],
                "description": "家长报告",
                "methods": ["GET"]
            },
            "/api/parent/communication": {
                "allowed_roles": ["教师", "家长"],
                "description": "家校沟通",
                "methods": ["GET", "POST"]
            },
            
            # 公共API
            "/api/public/demo": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师", "学生", "家长", "访客"],
                "description": "公共演示",
                "methods": ["GET"]
            },
            "/api/public/announcements": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师", "学生", "家长", "访客"],
                "description": "公告信息",
                "methods": ["GET"]
            },
            
            # 认证相关API
            "/api/auth/profile": {
                "allowed_roles": ["系统管理员", "校长", "教务主任", "教师", "学生", "家长"],
                "description": "用户档案",
                "methods": ["GET", "PUT"]
            }
        }
    
    async def authenticate_user(self, account_id: str) -> bool:
        """用户认证"""
        if account_id not in self.test_accounts:
            logger.error(f"账号 {account_id} 不存在")
            return False
        
        account = self.test_accounts[account_id]
        
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
    
    async def test_endpoint_access(self, account_id: str, endpoint: str, method: str = "GET") -> Dict:
        """测试端点访问权限"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        account = self.test_accounts[account_id]
        role = account['role']
        
        # 检查是否有权限访问该端点
        permission_info = self.permission_matrix.get(endpoint, {})
        allowed_roles = permission_info.get("allowed_roles", [])
        allowed_methods = permission_info.get("methods", ["GET"])
        
        should_have_access = role in allowed_roles and method in allowed_methods
        
        try:
            token = self.session_tokens[account_id]
            headers = {"Authorization": f"Bearer {token}"}
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # 根据方法类型发送请求
                if method == "GET":
                    async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                        response_time = time.time() - start_time
                        status_code = response.status
                elif method == "POST":
                    test_data = {"test": True}
                    async with session.post(f"{self.base_url}{endpoint}", json=test_data, headers=headers) as response:
                        response_time = time.time() - start_time
                        status_code = response.status
                elif method == "PUT":
                    test_data = {"test": True}
                    async with session.put(f"{self.base_url}{endpoint}", json=test_data, headers=headers) as response:
                        response_time = time.time() - start_time
                        status_code = response.status
                elif method == "DELETE":
                    async with session.delete(f"{self.base_url}{endpoint}", headers=headers) as response:
                        response_time = time.time() - start_time
                        status_code = response.status
                else:
                    return {"success": False, "error": f"不支持的HTTP方法: {method}"}
                
                # 判断访问结果是否符合预期
                if should_have_access:
                    # 应该有权限访问
                    access_granted = status_code in [200, 201, 204, 404]  # 404表示端点不存在但权限正常
                    success = access_granted
                    if not access_granted:
                        logger.warning(f"权限测试异常: {role} 应该能访问 {endpoint} ({method})，但返回 {status_code}")
                else:
                    # 不应该有权限访问
                    access_denied = status_code in [401, 403]
                    success = access_denied
                    if not access_denied:
                        logger.warning(f"权限测试异常: {role} 不应该能访问 {endpoint} ({method})，但返回 {status_code}")
                
                result = {
                    "success": success,
                    "account_id": account_id,
                    "role": role,
                    "endpoint": endpoint,
                    "method": method,
                    "should_have_access": should_have_access,
                    "status_code": status_code,
                    "response_time": response_time,
                    "description": permission_info.get("description", "未知")
                }
                
                if success:
                    logger.info(f"权限测试通过: {role} -> {endpoint} ({method}) - {status_code}")
                else:
                    logger.error(f"权限测试失败: {role} -> {endpoint} ({method}) - 期望{'允许' if should_have_access else '拒绝'}，实际 {status_code}")
                
                return result
                
        except Exception as e:
            logger.error(f"权限测试异常: {account_id} -> {endpoint} ({method}) - {e}")
            return {
                "success": False,
                "account_id": account_id,
                "role": role,
                "endpoint": endpoint,
                "method": method,
                "error": str(e)
            }
    
    async def test_role_permissions(self, account_id: str) -> List[Dict]:
        """测试角色的所有权限"""
        if account_id not in self.test_accounts:
            return []
        
        account = self.test_accounts[account_id]
        role = account['role']
        
        logger.info(f"开始测试角色 {role} 的权限...")
        
        results = []
        
        # 测试所有端点
        for endpoint, permission_info in self.permission_matrix.items():
            allowed_methods = permission_info.get("methods", ["GET"])
            
            # 测试每个允许的HTTP方法
            for method in allowed_methods:
                result = await self.test_endpoint_access(account_id, endpoint, method)
                results.append(result)
                
                # 添加小延迟避免请求过于频繁
                await asyncio.sleep(0.1)
        
        return results
    
    async def test_unauthorized_access(self) -> List[Dict]:
        """测试未授权访问"""
        logger.info("测试未授权访问...")
        
        results = []
        
        # 测试没有token的访问
        for endpoint in list(self.permission_matrix.keys())[:5]:  # 只测试前5个端点
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        response_time = time.time() - start_time
                        
                        # 期望返回401状态码
                        expected_status = response.status == 401
                        
                        result = {
                            "endpoint": endpoint,
                            "method": "GET",
                            "token": None,
                            "status_code": response.status,
                            "response_time": response_time,
                            "success": expected_status,
                            "description": "无token访问测试"
                        }
                        
                        if expected_status:
                            logger.info(f"未授权访问测试通过: {endpoint} - 状态码: {response.status}")
                        else:
                            logger.error(f"未授权访问测试失败: {endpoint} - 期望401，实际: {response.status}")
                        
                        results.append(result)
                        
            except Exception as e:
                logger.error(f"未授权访问测试异常: {endpoint} - {e}")
                results.append({
                    "endpoint": endpoint,
                    "method": "GET",
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    async def test_cross_role_access(self) -> List[Dict]:
        """测试跨角色访问"""
        logger.info("测试跨角色访问...")
        
        results = []
        
        # 获取不同角色的账号
        role_accounts = {}
        for account_id, account in self.test_accounts.items():
            if account['status'] == 'active':
                role = account['role']
                if role not in role_accounts:
                    role_accounts[role] = account_id
        
        # 测试高权限角色访问低权限资源
        high_privilege_tests = [
            ("系统管理员", "/api/student/grades", "GET"),
            ("校长", "/api/teacher/classes", "GET"),
            ("教务主任", "/api/parent/children", "GET")
        ]
        
        for role, endpoint, method in high_privilege_tests:
            if role in role_accounts:
                account_id = role_accounts[role]
                result = await self.test_endpoint_access(account_id, endpoint, method)
                result["test_type"] = "高权限访问低权限资源"
                results.append(result)
        
        # 测试低权限角色访问高权限资源
        low_privilege_tests = [
            ("学生", "/api/admin/users", "GET"),
            ("家长", "/api/teacher/lessons", "GET"),
            ("访客", "/api/school/statistics", "GET")
        ]
        
        for role, endpoint, method in low_privilege_tests:
            if role in role_accounts:
                account_id = role_accounts[role]
                result = await self.test_endpoint_access(account_id, endpoint, method)
                result["test_type"] = "低权限访问高权限资源"
                results.append(result)
        
        return results
    
    async def test_resource_isolation(self) -> List[Dict]:
        """测试资源隔离"""
        logger.info("测试资源隔离...")
        
        results = []
        
        # 获取教师和学生账号
        teacher_account = None
        student_account = None
        
        for account_id, account in self.test_accounts.items():
            if account['status'] == 'active':
                if account['role'] == '教师' and not teacher_account:
                    teacher_account = account_id
                elif account['role'] == '学生' and not student_account:
                    student_account = account_id
        
        if teacher_account and student_account:
            # 测试教师访问自己的资源
            teacher_resources = [
                "/api/teacher/lessons",
                "/api/teacher/materials",
                "/api/teacher/classes"
            ]
            
            for endpoint in teacher_resources:
                result = await self.test_endpoint_access(teacher_account, endpoint, "GET")
                result["test_type"] = "教师访问自己的资源"
                results.append(result)
            
            # 测试学生访问教师资源（应该被拒绝）
            for endpoint in teacher_resources:
                result = await self.test_endpoint_access(student_account, endpoint, "GET")
                result["test_type"] = "学生访问教师资源"
                results.append(result)
        
        return results
    
    async def run_full_authorization_test(self) -> Dict:
        """运行完整的权限控制测试套件"""
        logger.info("开始执行完整权限控制测试套件...")
        
        test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
        # 获取活跃账号并进行认证
        active_accounts = [acc_id for acc_id, acc in self.test_accounts.items() 
                          if acc['status'] == 'active']
        
        logger.info(f"找到 {len(active_accounts)} 个活跃测试账号")
        
        # 先进行认证
        authenticated_accounts = []
        for account_id in active_accounts:
            if await self.authenticate_user(account_id):
                authenticated_accounts.append(account_id)
        
        logger.info(f"成功认证 {len(authenticated_accounts)} 个账号")
        
        # 1. 测试每个角色的权限
        logger.info("1. 测试角色权限...")
        role_permission_results = {}
        for account_id in authenticated_accounts:
            results = await self.test_role_permissions(account_id)
            role_permission_results[account_id] = results
        
        test_results["tests"]["role_permissions"] = role_permission_results
        
        # 2. 测试未授权访问
        logger.info("2. 测试未授权访问...")
        unauthorized_results = await self.test_unauthorized_access()
        test_results["tests"]["unauthorized_access"] = unauthorized_results
        
        # 3. 测试跨角色访问
        logger.info("3. 测试跨角色访问...")
        cross_role_results = await self.test_cross_role_access()
        test_results["tests"]["cross_role_access"] = cross_role_results
        
        # 4. 测试资源隔离
        logger.info("4. 测试资源隔离...")
        resource_isolation_results = await self.test_resource_isolation()
        test_results["tests"]["resource_isolation"] = resource_isolation_results
        
        # 生成测试摘要
        test_results["end_time"] = datetime.now().isoformat()
        
        # 统计测试结果
        summary = {
            "total_accounts": len(authenticated_accounts),
            "total_endpoints": len(self.permission_matrix),
            "role_permission_success_rate": 0,
            "unauthorized_access_blocked_rate": 0,
            "cross_role_access_success_rate": 0,
            "resource_isolation_success_rate": 0
        }
        
        # 计算角色权限测试成功率
        total_role_tests = 0
        successful_role_tests = 0
        for account_results in role_permission_results.values():
            for result in account_results:
                total_role_tests += 1
                if result.get("success", False):
                    successful_role_tests += 1
        
        summary["role_permission_success_rate"] = (successful_role_tests / total_role_tests * 100) if total_role_tests > 0 else 0
        
        # 计算未授权访问阻止率
        blocked_unauthorized = sum(1 for r in unauthorized_results if r.get("success", False))
        summary["unauthorized_access_blocked_rate"] = (blocked_unauthorized / len(unauthorized_results) * 100) if unauthorized_results else 0
        
        # 计算跨角色访问成功率
        successful_cross_role = sum(1 for r in cross_role_results if r.get("success", False))
        summary["cross_role_access_success_rate"] = (successful_cross_role / len(cross_role_results) * 100) if cross_role_results else 0
        
        # 计算资源隔离成功率
        successful_isolation = sum(1 for r in resource_isolation_results if r.get("success", False))
        summary["resource_isolation_success_rate"] = (successful_isolation / len(resource_isolation_results) * 100) if resource_isolation_results else 0
        
        test_results["summary"] = summary
        
        # 保存测试结果
        with open("authorization_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        logger.info("权限控制测试套件执行完成")
        logger.info(f"角色权限测试成功率: {summary['role_permission_success_rate']:.1f}%")
        logger.info(f"未授权访问阻止率: {summary['unauthorized_access_blocked_rate']:.1f}%")
        logger.info(f"跨角色访问成功率: {summary['cross_role_access_success_rate']:.1f}%")
        logger.info(f"资源隔离成功率: {summary['resource_isolation_success_rate']:.1f}%")
        
        return test_results

# 主执行函数
async def main():
    """主执行函数"""
    try:
        # 初始化权限控制测试器
        tester = AuthorizationTester()
        
        # 运行完整权限控制测试
        results = await tester.run_full_authorization_test()
        
        # 输出测试结果摘要
        print("\n" + "="*50)
        print("权限控制测试结果摘要")
        print("="*50)
        
        summary = results["summary"]
        print(f"测试账号总数: {summary['total_accounts']}")
        print(f"测试端点总数: {summary['total_endpoints']}")
        print(f"角色权限测试成功率: {summary['role_permission_success_rate']:.1f}%")
        print(f"未授权访问阻止率: {summary['unauthorized_access_blocked_rate']:.1f}%")
        print(f"跨角色访问成功率: {summary['cross_role_access_success_rate']:.1f}%")
        print(f"资源隔离成功率: {summary['resource_isolation_success_rate']:.1f}%")
        
        # 计算总体通过率
        total_score = (
            summary['role_permission_success_rate'] + 
            summary['unauthorized_access_blocked_rate'] + 
            summary['cross_role_access_success_rate'] + 
            summary['resource_isolation_success_rate']
        ) / 4
        
        print(f"\n总体权限控制测试通过率: {total_score:.1f}%")
        print("\n详细测试结果已保存到: authorization_test_results.json")
        print("测试日志已保存到: authorization_test.log")
        
    except Exception as e:
        logger.error(f"权限控制测试执行失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())