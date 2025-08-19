#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手安全性测试

功能：
1. 测试用户认证安全性
2. 测试权限控制安全性
3. 测试数据传输安全性
4. 测试输入验证安全性
5. 测试会话管理安全性
6. 测试常见安全漏洞

作者：测试工程师
日期：2024年12月
"""

import json
import asyncio
import aiohttp
import time
import hashlib
import base64
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import sys
import re
import urllib.parse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SecurityTester:
    """安全性测试类"""
    
    def __init__(self, config_file: str = "test_accounts.json", base_url: str = "http://localhost:8000"):
        self.config_file = config_file
        self.base_url = base_url
        self.test_accounts = {}
        self.session_tokens = {}
        self.security_test_results = []
        
        # 安全测试配置
        self.max_login_attempts = 5
        self.session_timeout = 3600  # 1小时
        
        # 加载测试账号
        self._load_test_accounts()
        
        logger.info(f"安全性测试器初始化完成，基础URL: {self.base_url}")
    
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
    
    def generate_malicious_payloads(self) -> Dict[str, List[str]]:
        """生成恶意载荷用于安全测试"""
        return {
            "sql_injection": [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "admin'--",
                "' OR 1=1#",
                "1' AND (SELECT COUNT(*) FROM users) > 0 --"
            ],
            "xss_payloads": [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg onload=alert('XSS')>",
                "<iframe src=javascript:alert('XSS')></iframe>",
                "<body onload=alert('XSS')>"
            ],
            "command_injection": [
                "; ls -la",
                "| cat /etc/passwd",
                "&& whoami",
                "; rm -rf /",
                "| nc -l 4444",
                "; cat /etc/shadow"
            ],
            "path_traversal": [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "..%252f..%252f..%252fetc%252fpasswd"
            ],
            "ldap_injection": [
                "*)(uid=*))(|(uid=*",
                "*)(|(password=*))",
                "admin)(&(password=*",
                "*))%00"
            ],
            "nosql_injection": [
                "{'$ne': null}",
                "{'$gt': ''}",
                "{'$regex': '.*'}",
                "{'$where': 'this.username == this.password'}"
            ]
        }
    
    async def test_authentication_security(self) -> Dict:
        """测试认证安全性"""
        logger.info("开始测试认证安全性...")
        
        test_results = {
            "test_type": "认证安全性测试",
            "tests": {},
            "vulnerabilities": [],
            "security_score": 0
        }
        
        # 1. 测试弱密码登录
        logger.info("测试弱密码登录...")
        weak_passwords = ["123456", "password", "admin", "123123", "qwerty", "abc123"]
        weak_password_results = []
        
        for password in weak_passwords:
            try:
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        "username": "admin",
                        "password": password
                    }
                    
                    async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                        if response.status == 200:
                            weak_password_results.append({
                                "password": password,
                                "login_successful": True,
                                "vulnerability": "弱密码可以登录"
                            })
                            test_results["vulnerabilities"].append(f"弱密码 '{password}' 可以成功登录")
                        else:
                            weak_password_results.append({
                                "password": password,
                                "login_successful": False
                            })
            except Exception as e:
                logger.error(f"弱密码测试异常: {e}")
        
        test_results["tests"]["weak_password_test"] = weak_password_results
        
        # 2. 测试暴力破解防护
        logger.info("测试暴力破解防护...")
        brute_force_results = []
        
        # 连续尝试错误密码
        for attempt in range(10):
            try:
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        "username": "admin",
                        "password": f"wrong_password_{attempt}"
                    }
                    
                    start_time = time.time()
                    async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                        response_time = time.time() - start_time
                        
                        brute_force_results.append({
                            "attempt": attempt + 1,
                            "status_code": response.status,
                            "response_time": response_time,
                            "blocked": response.status == 429  # Too Many Requests
                        })
                        
                        # 如果被阻止，说明有防护机制
                        if response.status == 429:
                            logger.info(f"第 {attempt + 1} 次尝试被阻止，存在暴力破解防护")
                            break
                
                await asyncio.sleep(0.5)  # 短暂等待
                
            except Exception as e:
                logger.error(f"暴力破解测试异常: {e}")
        
        # 检查是否有暴力破解防护
        blocked_attempts = sum(1 for result in brute_force_results if result["blocked"])
        if blocked_attempts == 0:
            test_results["vulnerabilities"].append("缺少暴力破解防护机制")
        
        test_results["tests"]["brute_force_protection"] = {
            "total_attempts": len(brute_force_results),
            "blocked_attempts": blocked_attempts,
            "protection_exists": blocked_attempts > 0,
            "attempts_details": brute_force_results
        }
        
        # 3. 测试SQL注入攻击
        logger.info("测试SQL注入攻击...")
        sql_injection_results = []
        malicious_payloads = self.generate_malicious_payloads()
        
        for payload in malicious_payloads["sql_injection"]:
            try:
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        "username": payload,
                        "password": "any_password"
                    }
                    
                    async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                        response_text = await response.text()
                        
                        # 检查是否有SQL错误信息泄露
                        sql_error_indicators = [
                            "sql", "mysql", "postgresql", "sqlite", "oracle",
                            "syntax error", "database error", "query failed"
                        ]
                        
                        has_sql_error = any(indicator in response_text.lower() for indicator in sql_error_indicators)
                        
                        sql_injection_results.append({
                            "payload": payload,
                            "status_code": response.status,
                            "sql_error_exposed": has_sql_error,
                            "login_successful": response.status == 200
                        })
                        
                        if has_sql_error:
                            test_results["vulnerabilities"].append(f"SQL注入载荷 '{payload}' 导致数据库错误信息泄露")
                        
                        if response.status == 200:
                            test_results["vulnerabilities"].append(f"SQL注入载荷 '{payload}' 绕过了认证")
                
            except Exception as e:
                logger.error(f"SQL注入测试异常: {e}")
        
        test_results["tests"]["sql_injection_test"] = sql_injection_results
        
        # 4. 测试会话固定攻击
        logger.info("测试会话固定攻击...")
        session_fixation_results = []
        
        # 获取一个有效的会话令牌
        valid_account = next((acc for acc in self.test_accounts.values() if acc['status'] == 'active'), None)
        if valid_account:
            try:
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        "username": valid_account['username'],
                        "password": valid_account['password']
                    }
                    
                    async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            original_token = result.get('token', '')
                            
                            # 再次登录，检查是否生成新的会话令牌
                            async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response2:
                                if response2.status == 200:
                                    result2 = await response2.json()
                                    new_token = result2.get('token', '')
                                    
                                    session_fixation_results.append({
                                        "original_token": original_token[:20] + "...",
                                        "new_token": new_token[:20] + "...",
                                        "tokens_different": original_token != new_token,
                                        "session_regenerated": original_token != new_token
                                    })
                                    
                                    if original_token == new_token:
                                        test_results["vulnerabilities"].append("会话令牌未在重新登录时更新，存在会话固定风险")
            
            except Exception as e:
                logger.error(f"会话固定测试异常: {e}")
        
        test_results["tests"]["session_fixation_test"] = session_fixation_results
        
        # 计算认证安全评分
        security_issues = len(test_results["vulnerabilities"])
        max_possible_issues = 10  # 假设最多可能有10个安全问题
        
        security_score = max(0, (max_possible_issues - security_issues) / max_possible_issues * 100)
        test_results["security_score"] = security_score
        
        if security_score >= 90:
            test_results["security_rating"] = "优秀"
        elif security_score >= 80:
            test_results["security_rating"] = "良好"
        elif security_score >= 70:
            test_results["security_rating"] = "一般"
        else:
            test_results["security_rating"] = "需要加强"
        
        return test_results
    
    async def test_authorization_security(self) -> Dict:
        """测试权限控制安全性"""
        logger.info("开始测试权限控制安全性...")
        
        test_results = {
            "test_type": "权限控制安全性测试",
            "tests": {},
            "vulnerabilities": [],
            "security_score": 0
        }
        
        # 获取不同角色的账号
        student_accounts = [acc for acc in self.test_accounts.values() if acc['role'] == 'student' and acc['status'] == 'active']
        teacher_accounts = [acc for acc in self.test_accounts.values() if acc['role'] == 'teacher' and acc['status'] == 'active']
        admin_accounts = [acc for acc in self.test_accounts.values() if acc['role'] == 'admin' and acc['status'] == 'active']
        
        # 1. 测试垂直权限提升
        logger.info("测试垂直权限提升...")
        vertical_privilege_results = []
        
        if student_accounts and admin_accounts:
            student_account = student_accounts[0]
            
            # 学生账号登录
            try:
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        "username": student_account['username'],
                        "password": student_account['password']
                    }
                    
                    async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            student_token = result.get('token', '')
                            
                            # 尝试访问管理员功能
                            admin_endpoints = [
                                "/api/admin/users",
                                "/api/admin/system-config",
                                "/api/admin/logs",
                                "/api/admin/statistics"
                            ]
                            
                            headers = {"Authorization": f"Bearer {student_token}"}
                            
                            for endpoint in admin_endpoints:
                                try:
                                    async with session.get(f"{self.base_url}{endpoint}", headers=headers) as admin_response:
                                        vertical_privilege_results.append({
                                            "endpoint": endpoint,
                                            "student_access_granted": admin_response.status == 200,
                                            "status_code": admin_response.status
                                        })
                                        
                                        if admin_response.status == 200:
                                            test_results["vulnerabilities"].append(f"学生账号可以访问管理员端点: {endpoint}")
                                
                                except Exception as e:
                                    logger.error(f"垂直权限测试异常: {e}")
            
            except Exception as e:
                logger.error(f"学生账号登录失败: {e}")
        
        test_results["tests"]["vertical_privilege_escalation"] = vertical_privilege_results
        
        # 2. 测试水平权限提升
        logger.info("测试水平权限提升...")
        horizontal_privilege_results = []
        
        if len(student_accounts) >= 2:
            student1 = student_accounts[0]
            student2 = student_accounts[1]
            
            # 学生1登录
            try:
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        "username": student1['username'],
                        "password": student1['password']
                    }
                    
                    async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            student1_token = result.get('token', '')
                            
                            # 尝试访问学生2的数据
                            student2_endpoints = [
                                f"/api/student/{student2['id']}/grades",
                                f"/api/student/{student2['id']}/profile",
                                f"/api/student/{student2['id']}/progress"
                            ]
                            
                            headers = {"Authorization": f"Bearer {student1_token}"}
                            
                            for endpoint in student2_endpoints:
                                try:
                                    async with session.get(f"{self.base_url}{endpoint}", headers=headers) as other_response:
                                        horizontal_privilege_results.append({
                                            "endpoint": endpoint,
                                            "cross_user_access_granted": other_response.status == 200,
                                            "status_code": other_response.status
                                        })
                                        
                                        if other_response.status == 200:
                                            test_results["vulnerabilities"].append(f"学生可以访问其他学生的数据: {endpoint}")
                                
                                except Exception as e:
                                    logger.error(f"水平权限测试异常: {e}")
            
            except Exception as e:
                logger.error(f"学生账号登录失败: {e}")
        
        test_results["tests"]["horizontal_privilege_escalation"] = horizontal_privilege_results
        
        # 3. 测试未授权访问
        logger.info("测试未授权访问...")
        unauthorized_access_results = []
        
        # 不使用任何认证令牌访问受保护的端点
        protected_endpoints = [
            "/api/user/profile",
            "/api/grades/list",
            "/api/lesson/list",
            "/api/admin/users",
            "/api/student/progress"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint in protected_endpoints:
                    try:
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            unauthorized_access_results.append({
                                "endpoint": endpoint,
                                "unauthorized_access_granted": response.status == 200,
                                "status_code": response.status
                            })
                            
                            if response.status == 200:
                                test_results["vulnerabilities"].append(f"未授权访问成功: {endpoint}")
                    
                    except Exception as e:
                        logger.error(f"未授权访问测试异常: {e}")
        
        except Exception as e:
            logger.error(f"未授权访问测试失败: {e}")
        
        test_results["tests"]["unauthorized_access"] = unauthorized_access_results
        
        # 4. 测试令牌篡改
        logger.info("测试令牌篡改...")
        token_tampering_results = []
        
        if student_accounts:
            student_account = student_accounts[0]
            
            try:
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        "username": student_account['username'],
                        "password": student_account['password']
                    }
                    
                    async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            original_token = result.get('token', '')
                            
                            # 生成篡改的令牌
                            tampered_tokens = [
                                original_token[:-5] + "XXXXX",  # 修改末尾
                                "XXXXX" + original_token[5:],   # 修改开头
                                original_token.replace('a', 'b'),  # 替换字符
                                base64.b64encode(b"fake_token").decode(),  # 完全伪造的令牌
                            ]
                            
                            for tampered_token in tampered_tokens:
                                try:
                                    headers = {"Authorization": f"Bearer {tampered_token}"}
                                    async with session.get(f"{self.base_url}/api/user/profile", headers=headers) as tamper_response:
                                        token_tampering_results.append({
                                            "tampered_token": tampered_token[:20] + "...",
                                            "access_granted": tamper_response.status == 200,
                                            "status_code": tamper_response.status
                                        })
                                        
                                        if tamper_response.status == 200:
                                            test_results["vulnerabilities"].append("篡改的令牌仍然有效")
                                
                                except Exception as e:
                                    logger.error(f"令牌篡改测试异常: {e}")
            
            except Exception as e:
                logger.error(f"令牌篡改测试失败: {e}")
        
        test_results["tests"]["token_tampering"] = token_tampering_results
        
        # 计算权限控制安全评分
        security_issues = len(test_results["vulnerabilities"])
        max_possible_issues = 15  # 假设最多可能有15个权限安全问题
        
        security_score = max(0, (max_possible_issues - security_issues) / max_possible_issues * 100)
        test_results["security_score"] = security_score
        
        if security_score >= 90:
            test_results["security_rating"] = "优秀"
        elif security_score >= 80:
            test_results["security_rating"] = "良好"
        elif security_score >= 70:
            test_results["security_rating"] = "一般"
        else:
            test_results["security_rating"] = "需要加强"
        
        return test_results
    
    async def test_input_validation_security(self) -> Dict:
        """测试输入验证安全性"""
        logger.info("开始测试输入验证安全性...")
        
        test_results = {
            "test_type": "输入验证安全性测试",
            "tests": {},
            "vulnerabilities": [],
            "security_score": 0
        }
        
        # 获取一个有效的教师账号进行测试
        teacher_accounts = [acc for acc in self.test_accounts.values() if acc['role'] == 'teacher' and acc['status'] == 'active']
        
        if not teacher_accounts:
            logger.error("没有找到活跃的教师账号")
            return test_results
        
        teacher_account = teacher_accounts[0]
        
        # 教师账号登录
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "username": teacher_account['username'],
                    "password": teacher_account['password']
                }
                
                async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                    if response.status != 200:
                        logger.error("教师账号登录失败")
                        return test_results
                    
                    result = await response.json()
                    teacher_token = result.get('token', '')
                    headers = {"Authorization": f"Bearer {teacher_token}"}
                    
                    malicious_payloads = self.generate_malicious_payloads()
                    
                    # 1. 测试XSS攻击
                    logger.info("测试XSS攻击...")
                    xss_results = []
                    
                    for payload in malicious_payloads["xss_payloads"]:
                        try:
                            # 测试在成绩录入中的XSS
                            grade_data = {
                                "student_name": payload,
                                "subject": "数学",
                                "score": 85,
                                "exam_name": "测试考试"
                            }
                            
                            async with session.post(f"{self.base_url}/api/grades/add", json=grade_data, headers=headers) as xss_response:
                                response_text = await xss_response.text()
                                
                                # 检查响应中是否包含未转义的脚本
                                script_reflected = "<script>" in response_text or "javascript:" in response_text
                                
                                xss_results.append({
                                    "payload": payload,
                                    "status_code": xss_response.status,
                                    "script_reflected": script_reflected,
                                    "data_accepted": xss_response.status in [200, 201]
                                })
                                
                                if script_reflected:
                                    test_results["vulnerabilities"].append(f"XSS载荷被反射: {payload}")
                                
                                if xss_response.status in [200, 201] and "<script>" in payload:
                                    test_results["vulnerabilities"].append(f"恶意脚本数据被接受: {payload}")
                        
                        except Exception as e:
                            logger.error(f"XSS测试异常: {e}")
                    
                    test_results["tests"]["xss_test"] = xss_results
                    
                    # 2. 测试命令注入
                    logger.info("测试命令注入...")
                    command_injection_results = []
                    
                    for payload in malicious_payloads["command_injection"]:
                        try:
                            # 测试在文件上传或处理功能中的命令注入
                            file_data = {
                                "filename": f"test{payload}.txt",
                                "content": "测试内容",
                                "description": "测试文件"
                            }
                            
                            async with session.post(f"{self.base_url}/api/files/upload", json=file_data, headers=headers) as cmd_response:
                                response_text = await response.text()
                                
                                # 检查是否有命令执行的迹象
                                command_executed = any(indicator in response_text.lower() for indicator in [
                                    "root:", "bin/bash", "command not found", "permission denied"
                                ])
                                
                                command_injection_results.append({
                                    "payload": payload,
                                    "status_code": cmd_response.status,
                                    "command_executed": command_executed,
                                    "data_accepted": cmd_response.status in [200, 201]
                                })
                                
                                if command_executed:
                                    test_results["vulnerabilities"].append(f"命令注入成功: {payload}")
                        
                        except Exception as e:
                            logger.error(f"命令注入测试异常: {e}")
                    
                    test_results["tests"]["command_injection_test"] = command_injection_results
                    
                    # 3. 测试路径遍历
                    logger.info("测试路径遍历...")
                    path_traversal_results = []
                    
                    for payload in malicious_payloads["path_traversal"]:
                        try:
                            # 测试文件下载功能的路径遍历
                            async with session.get(f"{self.base_url}/api/files/download?filename={urllib.parse.quote(payload)}", headers=headers) as path_response:
                                response_text = await response.text()
                                
                                # 检查是否泄露了系统文件内容
                                system_file_leaked = any(indicator in response_text.lower() for indicator in [
                                    "root:x:", "daemon:", "[users]", "windows"
                                ])
                                
                                path_traversal_results.append({
                                    "payload": payload,
                                    "status_code": path_response.status,
                                    "system_file_leaked": system_file_leaked,
                                    "access_granted": path_response.status == 200
                                })
                                
                                if system_file_leaked:
                                    test_results["vulnerabilities"].append(f"路径遍历成功，泄露系统文件: {payload}")
                        
                        except Exception as e:
                            logger.error(f"路径遍历测试异常: {e}")
                    
                    test_results["tests"]["path_traversal_test"] = path_traversal_results
                    
                    # 4. 测试文件上传安全性
                    logger.info("测试文件上传安全性...")
                    file_upload_results = []
                    
                    dangerous_files = [
                        {"filename": "malicious.php", "content": "<?php system($_GET['cmd']); ?>", "type": "PHP脚本"},
                        {"filename": "malicious.jsp", "content": "<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>", "type": "JSP脚本"},
                        {"filename": "malicious.exe", "content": "MZ\x90\x00\x03\x00\x00\x00", "type": "可执行文件"},
                        {"filename": "../../../malicious.txt", "content": "路径遍历测试", "type": "路径遍历"}
                    ]
                    
                    for file_info in dangerous_files:
                        try:
                            file_data = {
                                "filename": file_info["filename"],
                                "content": file_info["content"],
                                "description": f"测试{file_info['type']}"
                            }
                            
                            async with session.post(f"{self.base_url}/api/files/upload", json=file_data, headers=headers) as upload_response:
                                file_upload_results.append({
                                    "filename": file_info["filename"],
                                    "file_type": file_info["type"],
                                    "upload_successful": upload_response.status in [200, 201],
                                    "status_code": upload_response.status
                                })
                                
                                if upload_response.status in [200, 201]:
                                    test_results["vulnerabilities"].append(f"危险文件上传成功: {file_info['filename']} ({file_info['type']})")
                        
                        except Exception as e:
                            logger.error(f"文件上传测试异常: {e}")
                    
                    test_results["tests"]["file_upload_test"] = file_upload_results
        
        except Exception as e:
            logger.error(f"输入验证测试失败: {e}")
        
        # 计算输入验证安全评分
        security_issues = len(test_results["vulnerabilities"])
        max_possible_issues = 20  # 假设最多可能有20个输入验证安全问题
        
        security_score = max(0, (max_possible_issues - security_issues) / max_possible_issues * 100)
        test_results["security_score"] = security_score
        
        if security_score >= 90:
            test_results["security_rating"] = "优秀"
        elif security_score >= 80:
            test_results["security_rating"] = "良好"
        elif security_score >= 70:
            test_results["security_rating"] = "一般"
        else:
            test_results["security_rating"] = "需要加强"
        
        return test_results
    
    async def test_session_management_security(self) -> Dict:
        """测试会话管理安全性"""
        logger.info("开始测试会话管理安全性...")
        
        test_results = {
            "test_type": "会话管理安全性测试",
            "tests": {},
            "vulnerabilities": [],
            "security_score": 0
        }
        
        # 获取一个有效的账号进行测试
        active_accounts = [acc for acc in self.test_accounts.values() if acc['status'] == 'active']
        
        if not active_accounts:
            logger.error("没有找到活跃的测试账号")
            return test_results
        
        test_account = active_accounts[0]
        
        # 1. 测试会话超时
        logger.info("测试会话超时...")
        session_timeout_results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "username": test_account['username'],
                    "password": test_account['password']
                }
                
                async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        token = result.get('token', '')
                        headers = {"Authorization": f"Bearer {token}"}
                        
                        # 立即测试令牌有效性
                        async with session.get(f"{self.base_url}/api/user/profile", headers=headers) as profile_response:
                            immediate_access = profile_response.status == 200
                        
                        # 等待一段时间后再次测试（模拟会话超时）
                        await asyncio.sleep(5)  # 等待5秒
                        
                        async with session.get(f"{self.base_url}/api/user/profile", headers=headers) as delayed_response:
                            delayed_access = delayed_response.status == 200
                        
                        session_timeout_results.append({
                            "immediate_access": immediate_access,
                            "delayed_access": delayed_access,
                            "session_persistent": delayed_access,
                            "delay_seconds": 5
                        })
        
        except Exception as e:
            logger.error(f"会话超时测试异常: {e}")
        
        test_results["tests"]["session_timeout_test"] = session_timeout_results
        
        # 2. 测试会话注销
        logger.info("测试会话注销...")
        session_logout_results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "username": test_account['username'],
                    "password": test_account['password']
                }
                
                async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        token = result.get('token', '')
                        headers = {"Authorization": f"Bearer {token}"}
                        
                        # 测试注销前的访问
                        async with session.get(f"{self.base_url}/api/user/profile", headers=headers) as before_logout:
                            access_before_logout = before_logout.status == 200
                        
                        # 执行注销
                        async with session.post(f"{self.base_url}/api/auth/logout", headers=headers) as logout_response:
                            logout_successful = logout_response.status == 200
                        
                        # 测试注销后的访问
                        async with session.get(f"{self.base_url}/api/user/profile", headers=headers) as after_logout:
                            access_after_logout = after_logout.status == 200
                        
                        session_logout_results.append({
                            "access_before_logout": access_before_logout,
                            "logout_successful": logout_successful,
                            "access_after_logout": access_after_logout,
                            "session_invalidated": not access_after_logout
                        })
                        
                        if access_after_logout:
                            test_results["vulnerabilities"].append("注销后会话令牌仍然有效")
        
        except Exception as e:
            logger.error(f"会话注销测试异常: {e}")
        
        test_results["tests"]["session_logout_test"] = session_logout_results
        
        # 3. 测试并发会话
        logger.info("测试并发会话...")
        concurrent_session_results = []
        
        try:
            # 创建多个并发会话
            sessions = []
            tokens = []
            
            for i in range(3):
                async with aiohttp.ClientSession() as session:
                    login_data = {
                        "username": test_account['username'],
                        "password": test_account['password']
                    }
                    
                    async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            token = result.get('token', '')
                            tokens.append(token)
            
            # 测试所有令牌是否都有效
            valid_tokens = 0
            for i, token in enumerate(tokens):
                try:
                    async with aiohttp.ClientSession() as session:
                        headers = {"Authorization": f"Bearer {token}"}
                        async with session.get(f"{self.base_url}/api/user/profile", headers=headers) as response:
                            if response.status == 200:
                                valid_tokens += 1
                except Exception as e:
                    logger.error(f"并发会话测试异常: {e}")
            
            concurrent_session_results.append({
                "total_sessions_created": len(tokens),
                "valid_concurrent_sessions": valid_tokens,
                "multiple_sessions_allowed": valid_tokens > 1
            })
            
            # 如果允许多个并发会话，可能存在安全风险
            if valid_tokens > 1:
                test_results["vulnerabilities"].append(f"允许 {valid_tokens} 个并发会话，可能存在安全风险")
        
        except Exception as e:
            logger.error(f"并发会话测试异常: {e}")
        
        test_results["tests"]["concurrent_session_test"] = concurrent_session_results
        
        # 计算会话管理安全评分
        security_issues = len(test_results["vulnerabilities"])
        max_possible_issues = 5  # 假设最多可能有5个会话管理安全问题
        
        security_score = max(0, (max_possible_issues - security_issues) / max_possible_issues * 100)
        test_results["security_score"] = security_score
        
        if security_score >= 90:
            test_results["security_rating"] = "优秀"
        elif security_score >= 80:
            test_results["security_rating"] = "良好"
        elif security_score >= 70:
            test_results["security_rating"] = "一般"
        else:
            test_results["security_rating"] = "需要加强"
        
        return test_results
    
    async def run_full_security_test(self) -> Dict:
        """运行完整的安全性测试套件"""
        logger.info("开始执行完整安全性测试套件...")
        
        test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
            "overall_vulnerabilities": []
        }
        
        # 1. 认证安全性测试
        logger.info("执行认证安全性测试...")
        auth_security_result = await self.test_authentication_security()
        test_results["tests"]["authentication_security"] = auth_security_result
        test_results["overall_vulnerabilities"].extend(auth_security_result["vulnerabilities"])
        
        # 2. 权限控制安全性测试
        logger.info("执行权限控制安全性测试...")
        authz_security_result = await self.test_authorization_security()
        test_results["tests"]["authorization_security"] = authz_security_result
        test_results["overall_vulnerabilities"].extend(authz_security_result["vulnerabilities"])
        
        # 3. 输入验证安全性测试
        logger.info("执行输入验证安全性测试...")
        input_validation_result = await self.test_input_validation_security()
        test_results["tests"]["input_validation_security"] = input_validation_result
        test_results["overall_vulnerabilities"].extend(input_validation_result["vulnerabilities"])
        
        # 4. 会话管理安全性测试
        logger.info("执行会话管理安全性测试...")
        session_security_result = await self.test_session_management_security()
        test_results["tests"]["session_management_security"] = session_security_result
        test_results["overall_vulnerabilities"].extend(session_security_result["vulnerabilities"])
        
        # 生成测试摘要
        test_results["end_time"] = datetime.now().isoformat()
        
        # 计算各项安全评分
        security_scores = {
            "authentication": auth_security_result["security_score"],
            "authorization": authz_security_result["security_score"],
            "input_validation": input_validation_result["security_score"],
            "session_management": session_security_result["security_score"]
        }
        
        # 计算总体安全评分
        overall_security_score = sum(security_scores.values()) / len(security_scores) if security_scores else 0
        
        # 统计漏洞
        total_vulnerabilities = len(test_results["overall_vulnerabilities"])
        
        # 按严重程度分类漏洞
        high_risk_keywords = ["sql注入", "命令注入", "路径遍历", "权限提升", "未授权访问"]
        medium_risk_keywords = ["xss", "会话", "令牌", "暴力破解"]
        
        high_risk_vulnerabilities = []
        medium_risk_vulnerabilities = []
        low_risk_vulnerabilities = []
        
        for vuln in test_results["overall_vulnerabilities"]:
            vuln_lower = vuln.lower()
            if any(keyword in vuln_lower for keyword in high_risk_keywords):
                high_risk_vulnerabilities.append(vuln)
            elif any(keyword in vuln_lower for keyword in medium_risk_keywords):
                medium_risk_vulnerabilities.append(vuln)
            else:
                low_risk_vulnerabilities.append(vuln)
        
        # 生成安全等级
        if overall_security_score >= 95 and total_vulnerabilities == 0:
            security_level = "非常安全"
        elif overall_security_score >= 90 and len(high_risk_vulnerabilities) == 0:
            security_level = "安全"
        elif overall_security_score >= 80 and len(high_risk_vulnerabilities) <= 1:
            security_level = "较安全"
        elif overall_security_score >= 70:
            security_level = "一般"
        else:
            security_level = "存在安全风险"
        
        summary = {
            "total_vulnerabilities": total_vulnerabilities,
            "high_risk_vulnerabilities": len(high_risk_vulnerabilities),
            "medium_risk_vulnerabilities": len(medium_risk_vulnerabilities),
            "low_risk_vulnerabilities": len(low_risk_vulnerabilities),
            "security_scores": security_scores,
            "overall_security_score": overall_security_score,
            "security_level": security_level,
            "vulnerability_details": {
                "high_risk": high_risk_vulnerabilities,
                "medium_risk": medium_risk_vulnerabilities,
                "low_risk": low_risk_vulnerabilities
            },
            "security_recommendations": self._generate_security_recommendations(test_results["overall_vulnerabilities"])
        }
        
        test_results["summary"] = summary
        
        # 保存测试结果
        with open("security_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        logger.info("安全性测试套件执行完成")
        logger.info(f"总体安全评分: {overall_security_score:.1f}分 ({security_level})")
        logger.info(f"发现漏洞总数: {total_vulnerabilities} (高风险: {len(high_risk_vulnerabilities)}, 中风险: {len(medium_risk_vulnerabilities)}, 低风险: {len(low_risk_vulnerabilities)})")
        
        return test_results
    
    def _generate_security_recommendations(self, vulnerabilities: List[str]) -> List[str]:
        """生成安全建议"""
        recommendations = []
        
        vuln_text = " ".join(vulnerabilities).lower()
        
        if "sql注入" in vuln_text or "sql" in vuln_text:
            recommendations.append("使用参数化查询或ORM框架防止SQL注入攻击")
        
        if "xss" in vuln_text or "脚本" in vuln_text:
            recommendations.append("对所有用户输入进行HTML转义和输出编码")
        
        if "命令注入" in vuln_text:
            recommendations.append("避免直接执行用户输入的命令，使用白名单验证")
        
        if "权限" in vuln_text or "未授权" in vuln_text:
            recommendations.append("实施严格的权限控制和访问验证机制")
        
        if "会话" in vuln_text or "令牌" in vuln_text:
            recommendations.append("加强会话管理，实施会话超时和安全注销")
        
        if "暴力破解" in vuln_text:
            recommendations.append("实施账号锁定和验证码机制防止暴力破解")
        
        if "路径遍历" in vuln_text:
            recommendations.append("验证和限制文件访问路径，使用安全的文件操作API")
        
        if "文件上传" in vuln_text:
            recommendations.append("限制文件上传类型，扫描恶意文件，隔离上传目录")
        
        # 通用安全建议
        if not recommendations:
            recommendations.append("继续保持良好的安全实践")
        
        recommendations.extend([
            "定期进行安全审计和渗透测试",
            "保持系统和依赖库的及时更新",
            "实施安全日志记录和监控",
            "对敏感数据进行加密存储和传输"
        ])
        
        return recommendations

# 主执行函数
async def main():
    """主执行函数"""
    try:
        # 初始化安全性测试器
        tester = SecurityTester()
        
        # 运行完整安全性测试
        results = await tester.run_full_security_test()
        
        # 输出测试结果摘要
        print("\n" + "="*50)
        print("安全性测试结果摘要")
        print("="*50)
        
        summary = results["summary"]
        print(f"总体安全评分: {summary['overall_security_score']:.1f}分")
        print(f"安全等级: {summary['security_level']}")
        print(f"发现漏洞总数: {summary['total_vulnerabilities']}")
        
        print("\n漏洞分布:")
        print(f"  高风险漏洞: {summary['high_risk_vulnerabilities']}个")
        print(f"  中风险漏洞: {summary['medium_risk_vulnerabilities']}个")
        print(f"  低风险漏洞: {summary['low_risk_vulnerabilities']}个")
        
        print("\n各项安全评分:")
        scores = summary["security_scores"]
        print(f"  认证安全: {scores['authentication']:.1f}分")
        print(f"  权限控制: {scores['authorization']:.1f}分")
        print(f"  输入验证: {scores['input_validation']:.1f}分")
        print(f"  会话管理: {scores['session_management']:.1f}分")
        
        if summary['high_risk_vulnerabilities'] > 0:
            print("\n高风险漏洞:")
            for vuln in summary['vulnerability_details']['high_risk']:
                print(f"  - {vuln}")
        
        print("\n安全建议:")
        for i, recommendation in enumerate(summary['security_recommendations'][:5], 1):
            print(f"  {i}. {recommendation}")
        
        print("\n详细测试结果已保存到: security_test_results.json")
        print("测试日志已保存到: security_test.log")
        
    except Exception as e:
        logger.error(f"安全性测试执行失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())