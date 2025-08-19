#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全性测试用例
测试数据安全性和隐私保护机制，包括用户认证、权限控制、数据加密等
"""

import unittest
import sys
import os
import jwt
import bcrypt
import requests
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from passlib.context import CryptContext

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    get_db, Base, engine, SessionLocal,
    User, Student, Class, Subject, Grade, Teacher
)


class TestSecurityModule(unittest.TestCase):
    """安全性测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        
        # 创建数据库会话
        self.db = SessionLocal()
        
        # 密码加密上下文
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # JWT配置
        self.SECRET_KEY = "test-secret-key-for-security-testing"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # 创建测试用户
        self.test_user = User(
            username="security_test_user",
            password=self.pwd_context.hash("SecureP@ssw0rd123!"),
            role="teacher",
            email="security@test.com",
            phone_number="13800138000"
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)
    
    def tearDown(self):
        """测试后清理"""
        # 清理数据库数据
        self.db.query(Grade).delete()
        self.db.query(Student).delete()
        self.db.query(Subject).delete()
        self.db.query(Class).delete()
        self.db.query(Teacher).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()
    
    def test_tc_security_001_password_encryption(self):
        """测试用例TC_SECURITY_001: 密码加密安全测试"""
        print("\n执行测试用例: TC_SECURITY_001 - 密码加密安全")
        
        # 测试密码加密功能
        plain_password = "TestPassword123!"
        
        # 验证密码哈希
        hashed_password = self.pwd_context.hash(plain_password)
        
        # 验证哈希结果
        self.assertNotEqual(plain_password, hashed_password)
        self.assertTrue(hashed_password.startswith('$2b$'))
        self.assertGreater(len(hashed_password), 50)
        
        # 验证密码验证功能
        self.assertTrue(self.pwd_context.verify(plain_password, hashed_password))
        self.assertFalse(self.pwd_context.verify("WrongPassword", hashed_password))
        
        # 验证相同密码产生不同哈希（盐值随机性）
        hash1 = self.pwd_context.hash(plain_password)
        hash2 = self.pwd_context.hash(plain_password)
        self.assertNotEqual(hash1, hash2)
        
        print("密码加密安全测试完成")
        print(f"原始密码: {plain_password}")
        print(f"哈希长度: {len(hashed_password)}")
        print(f"哈希前缀: {hashed_password[:10]}...")
    
    def test_tc_security_002_password_strength_validation(self):
        """测试用例TC_SECURITY_002: 密码强度验证测试"""
        print("\n执行测试用例: TC_SECURITY_002 - 密码强度验证")
        
        # 定义密码强度验证规则
        def validate_password_strength(password):
            """验证密码强度"""
            errors = []
            
            # 长度检查
            if len(password) < 8:
                errors.append("密码长度至少8位")
            
            # 复杂度检查
            if not any(c.isupper() for c in password):
                errors.append("密码必须包含大写字母")
            
            if not any(c.islower() for c in password):
                errors.append("密码必须包含小写字母")
            
            if not any(c.isdigit() for c in password):
                errors.append("密码必须包含数字")
            
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                errors.append("密码必须包含特殊字符")
            
            # 常见密码检查
            common_passwords = [
                "123456", "password", "admin", "qwerty", 
                "123456789", "12345678", "abc123"
            ]
            if password.lower() in common_passwords:
                errors.append("不能使用常见密码")
            
            return len(errors) == 0, errors
        
        # 测试弱密码
        weak_passwords = [
            "123456",           # 太短，无复杂度
            "password",         # 常见密码
            "abcdefgh",         # 只有小写字母
            "ABCDEFGH",         # 只有大写字母
            "12345678",         # 只有数字
            "Abc123",           # 太短
            "Password123",      # 缺少特殊字符
        ]
        
        for password in weak_passwords:
            is_valid, errors = validate_password_strength(password)
            self.assertFalse(is_valid, f"弱密码 '{password}' 应该被拒绝")
            self.assertGreater(len(errors), 0)
            print(f"弱密码 '{password}': {', '.join(errors)}")
        
        # 测试强密码
        strong_passwords = [
            "SecureP@ssw0rd123!",
            "MyStr0ng#Password",
            "C0mplex&Secure99",
            "Adm1n!P@ssw0rd"
        ]
        
        for password in strong_passwords:
            is_valid, errors = validate_password_strength(password)
            self.assertTrue(is_valid, f"强密码 '{password}' 应该被接受")
            self.assertEqual(len(errors), 0)
            print(f"强密码 '{password}': 通过验证")
        
        print("密码强度验证测试完成")
    
    def test_tc_security_003_jwt_token_security(self):
        """测试用例TC_SECURITY_003: JWT令牌安全测试"""
        print("\n执行测试用例: TC_SECURITY_003 - JWT令牌安全")
        
        # 创建JWT令牌
        def create_access_token(data: dict, expires_delta: timedelta = None):
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=15)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
            return encoded_jwt
        
        # 验证JWT令牌
        def verify_token(token: str):
            try:
                payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
                return payload
            except jwt.ExpiredSignatureError:
                return None
            except Exception:
                return None
        
        # 测试正常令牌创建和验证
        user_data = {"sub": self.test_user.username, "user_id": self.test_user.id}
        token = create_access_token(user_data)
        
        # 验证令牌格式
        self.assertIsInstance(token, str)
        self.assertEqual(len(token.split('.')), 3)  # JWT应该有3个部分
        
        # 验证令牌内容
        payload = verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], self.test_user.username)
        self.assertIn("exp", payload)
        
        # 测试过期令牌
        expired_token = create_access_token(
            user_data, 
            expires_delta=timedelta(seconds=-1)  # 已过期
        )
        time.sleep(1)  # 确保令牌过期
        expired_payload = verify_token(expired_token)
        self.assertIsNone(expired_payload)
        
        # 测试无效令牌
        invalid_tokens = [
            "invalid.token.here",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
            "",
            "not.a.jwt"
        ]
        
        for invalid_token in invalid_tokens:
            invalid_payload = verify_token(invalid_token)
            self.assertIsNone(invalid_payload, f"无效令牌应该被拒绝: {invalid_token}")
        
        # 测试令牌篡改
        # 修改令牌的一个字符
        tampered_token = token[:-1] + ('a' if token[-1] != 'a' else 'b')
        tampered_payload = verify_token(tampered_token)
        self.assertIsNone(tampered_payload)
        
        print("JWT令牌安全测试完成")
        print(f"有效令牌长度: {len(token)}")
        print(f"令牌格式验证: 通过")
        print(f"过期令牌验证: 通过")
        print(f"篡改检测: 通过")
    
    def test_tc_security_004_sql_injection_protection(self):
        """测试用例TC_SECURITY_004: SQL注入防护测试"""
        print("\n执行测试用例: TC_SECURITY_004 - SQL注入防护")
        
        # 模拟用户查询功能（使用参数化查询）
        def safe_user_query(username):
            """安全的用户查询（参数化查询）"""
            try:
                user = self.db.query(User).filter(User.username == username).first()
                return user
            except Exception as e:
                print(f"查询错误: {e}")
                return None
        
        # 模拟不安全的查询（仅用于测试，实际不应使用）
        def unsafe_user_query(username):
            """不安全的用户查询（字符串拼接）"""
            try:
                # 注意：这是不安全的示例，仅用于测试
                query = f"SELECT * FROM users WHERE username = '{username}'"
                # 在实际应用中，这种查询方式是危险的
                return f"执行查询: {query}"
            except Exception as e:
                return f"查询失败: {e}"
        
        # SQL注入攻击载荷
        sql_injection_payloads = [
            "admin'; DROP TABLE users; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' OR 'x'='x",
            "1' OR '1'='1' /*",
            "admin'/**/OR/**/1=1--"
        ]
        
        # 测试参数化查询的安全性
        print("测试参数化查询安全性:")
        for payload in sql_injection_payloads:
            result = safe_user_query(payload)
            # 参数化查询应该安全地处理这些输入
            # 结果应该是None（找不到用户）而不是抛出异常或返回意外数据
            print(f"载荷: {payload[:30]}... -> 结果: {result is None}")
        
        # 验证正常用户查询仍然工作
        normal_user = safe_user_query(self.test_user.username)
        self.assertIsNotNone(normal_user)
        self.assertEqual(normal_user.username, self.test_user.username)
        
        # 测试输入验证和清理
        def validate_and_sanitize_input(user_input):
            """输入验证和清理"""
            # 检查危险字符
            dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
            
            for char in dangerous_chars:
                if char.upper() in user_input.upper():
                    return False, f"输入包含危险字符: {char}"
            
            # 长度限制
            if len(user_input) > 50:
                return False, "输入长度超过限制"
            
            # 字符类型限制（只允许字母、数字、下划线）
            if not user_input.replace('_', '').replace('-', '').isalnum():
                return False, "输入包含非法字符"
            
            return True, "输入验证通过"
        
        # 测试输入验证
        print("\n测试输入验证:")
        for payload in sql_injection_payloads:
            is_valid, message = validate_and_sanitize_input(payload)
            self.assertFalse(is_valid, f"恶意输入应该被拒绝: {payload}")
            print(f"载荷: {payload[:20]}... -> {message}")
        
        # 测试正常输入
        valid_inputs = ["admin", "user123", "test_user", "teacher-01"]
        for valid_input in valid_inputs:
            is_valid, message = validate_and_sanitize_input(valid_input)
            print(f"正常输入: {valid_input} -> {message}")
        
        print("SQL注入防护测试完成")
    
    def test_tc_security_005_xss_protection(self):
        """测试用例TC_SECURITY_005: XSS跨站脚本攻击防护测试"""
        print("\n执行测试用例: TC_SECURITY_005 - XSS跨站脚本攻击防护")
        
        # XSS攻击载荷
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>",
            "<video><source onerror=alert('XSS')>",
            "<audio src=x onerror=alert('XSS')>"
        ]
        
        # HTML转义函数
        def escape_html(text):
            """HTML转义"""
            if not isinstance(text, str):
                text = str(text)
            
            escape_chars = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#x27;',
                '/': '&#x2F;'
            }
            
            for char, escaped in escape_chars.items():
                text = text.replace(char, escaped)
            
            return text
        
        # 输入清理函数
        def sanitize_input(user_input):
            """输入清理"""
            # 移除脚本标签
            import re
            
            # 移除script标签
            user_input = re.sub(r'<script[^>]*>.*?</script>', '', user_input, flags=re.IGNORECASE | re.DOTALL)
            
            # 移除所有HTML标签
            user_input = re.sub(r'<[^>]*>', '', user_input)
            
            # 移除javascript协议
            user_input = re.sub(r'javascript:', '', user_input, flags=re.IGNORECASE)
            
            # 移除危险标签
            dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input', 'textarea', 'select']
            for tag in dangerous_tags:
                user_input = re.sub(f'<{tag}[^>]*>', '', user_input, flags=re.IGNORECASE)
                user_input = re.sub(f'</{tag}>', '', user_input, flags=re.IGNORECASE)
            
            return user_input
        
        # 测试HTML转义
        print("测试HTML转义:")
        for payload in xss_payloads:
            escaped = escape_html(payload)
            # 验证HTML标签被转义
            self.assertNotIn('<script>', escaped)
            self.assertNotIn('<img', escaped)
            self.assertNotIn('<svg', escaped)
            self.assertNotIn('<iframe', escaped)
            # 验证危险字符被转义（对于包含HTML标签的载荷）
            if '<' in payload:
                self.assertIn('&lt;', escaped)
                self.assertIn('&gt;', escaped)
            print(f"原始: {payload[:30]}...")
            print(f"转义: {escaped[:50]}...")
            print()
        
        # 测试输入清理
        print("测试输入清理:")
        for payload in xss_payloads:
            sanitized = sanitize_input(payload)
            # 验证危险内容被移除
            self.assertNotIn('<script', sanitized.lower())
            self.assertNotIn('javascript:', sanitized.lower())
            self.assertNotIn('<svg', sanitized.lower())
            self.assertNotIn('onload=', sanitized.lower())
            print(f"原始: {payload}")
            print(f"清理: {sanitized}")
            print()
        
        # 测试内容安全策略（CSP）模拟
        def validate_csp_compliance(content):
            """验证内容安全策略合规性"""
            violations = []
            
            # 检查内联脚本
            if '<script' in content.lower() and 'src=' not in content.lower():
                violations.append("内联脚本被禁止")
            
            # 检查内联样式
            if 'style=' in content.lower():
                violations.append("内联样式被禁止")
            
            # 检查事件处理器
            import re
            if re.search(r'\son\w+\s*=', content, re.IGNORECASE):
                violations.append("内联事件处理器被禁止")
            
            # 检查javascript协议
            if 'javascript:' in content.lower():
                violations.append("javascript协议被禁止")
            
            return len(violations) == 0, violations
        
        # 测试CSP合规性
        print("测试内容安全策略合规性:")
        for payload in xss_payloads:
            is_compliant, violations = validate_csp_compliance(payload)
            self.assertFalse(is_compliant, f"XSS载荷应该违反CSP: {payload}")
            print(f"载荷: {payload[:30]}... -> 违规: {', '.join(violations)}")
        
        print("XSS跨站脚本攻击防护测试完成")
    
    def test_tc_security_006_access_control(self):
        """测试用例TC_SECURITY_006: 访问控制和权限验证测试"""
        print("\n执行测试用例: TC_SECURITY_006 - 访问控制和权限验证")
        
        # 定义角色权限
        ROLE_PERMISSIONS = {
            "admin": [
                "user_management", "grade_management", "class_management", 
                "system_config", "data_export", "user_create", "user_delete"
            ],
            "teacher": [
                "grade_management", "class_management", "student_view", 
                "lesson_prep", "classroom_tools"
            ],
            "student": [
                "grade_view", "profile_edit", "homework_submit"
            ],
            "parent": [
                "child_grade_view", "teacher_contact", "schedule_view"
            ]
        }
        
        # 权限检查函数
        def has_permission(user_role, required_permission):
            """检查用户是否有指定权限"""
            if user_role not in ROLE_PERMISSIONS:
                return False
            return required_permission in ROLE_PERMISSIONS[user_role]
        
        # 创建不同角色的测试用户
        test_users = {
            "admin": User(
                username="admin_user",
                password=self.pwd_context.hash("AdminP@ss123!"),
                role="admin",
                email="admin@test.com"
            ),
            "teacher": User(
                username="teacher_user",
                password=self.pwd_context.hash("TeacherP@ss123!"),
                role="teacher",
                email="teacher@test.com"
            ),
            "student": User(
                username="student_user",
                password=self.pwd_context.hash("StudentP@ss123!"),
                role="student",
                email="student@test.com"
            ),
            "parent": User(
                username="parent_user",
                password=self.pwd_context.hash("ParentP@ss123!"),
                role="parent",
                email="parent@test.com"
            )
        }
        
        # 测试权限矩阵
        permission_tests = [
            ("admin", "user_management", True),
            ("admin", "system_config", True),
            ("teacher", "grade_management", True),
            ("teacher", "user_delete", False),
            ("student", "grade_view", True),
            ("student", "user_management", False),
            ("parent", "child_grade_view", True),
            ("parent", "grade_management", False)
        ]
        
        print("测试角色权限矩阵:")
        for role, permission, expected in permission_tests:
            result = has_permission(role, permission)
            self.assertEqual(result, expected, 
                f"角色 {role} 对权限 {permission} 的访问应该是 {expected}")
            status = "允许" if result else "拒绝"
            print(f"角色: {role:8} | 权限: {permission:20} | 结果: {status}")
        
        # 测试越权访问防护
        def simulate_api_access(user_role, endpoint, required_permission):
            """模拟API访问"""
            if not has_permission(user_role, required_permission):
                return {
                    "status": "error",
                    "code": 403,
                    "message": "权限不足"
                }
            return {
                "status": "success",
                "code": 200,
                "message": "访问成功"
            }
        
        # 测试API访问控制
        api_tests = [
            ("teacher", "/api/users/create", "user_create"),
            ("student", "/api/grades/export", "data_export"),
            ("parent", "/api/system/config", "system_config"),
            ("admin", "/api/users/delete", "user_delete")
        ]
        
        print("\n测试API访问控制:")
        for role, endpoint, permission in api_tests:
            response = simulate_api_access(role, endpoint, permission)
            expected_code = 200 if has_permission(role, permission) else 403
            self.assertEqual(response["code"], expected_code)
            print(f"角色: {role:8} | 端点: {endpoint:20} | 状态: {response['code']} - {response['message']}")
        
        # 测试资源级别的访问控制
        def check_resource_access(user_id, user_role, resource_type, resource_id, action):
            """检查资源级别的访问权限"""
            # 管理员可以访问所有资源
            if user_role == "admin":
                return True
            
            # 教师只能访问自己的班级和学生
            if user_role == "teacher":
                if resource_type == "class" and action in ["view", "edit"]:
                    # 检查是否是班主任（简化逻辑）
                    return True  # 实际应该检查teacher_id
                if resource_type == "student" and action == "view":
                    return True
                return False
            
            # 学生只能访问自己的信息
            if user_role == "student":
                if resource_type == "student" and str(resource_id) == str(user_id):
                    return action in ["view", "edit_profile"]
                if resource_type == "grade" and action == "view":
                    return True  # 简化逻辑，实际应该检查学生ID
                return False
            
            # 家长只能访问自己孩子的信息
            if user_role == "parent":
                if resource_type == "student" and action == "view":
                    # 实际应该检查parent-child关系
                    return True
                return False
            
            return False
        
        # 测试资源访问控制
        resource_tests = [
            (1, "admin", "student", 123, "delete", True),
            (2, "teacher", "student", 123, "view", True),
            (2, "teacher", "student", 123, "delete", False),
            (3, "student", "student", 3, "view", True),
            (3, "student", "student", 4, "view", False),
            (4, "parent", "student", 5, "view", True),
            (4, "parent", "grade", 5, "edit", False)
        ]
        
        print("\n测试资源级别访问控制:")
        for user_id, role, resource_type, resource_id, action, expected in resource_tests:
            result = check_resource_access(user_id, role, resource_type, resource_id, action)
            self.assertEqual(result, expected)
            status = "允许" if result else "拒绝"
            print(f"用户{user_id}({role}) 对 {resource_type}#{resource_id} 执行 {action}: {status}")
        
        print("访问控制和权限验证测试完成")
    
    def test_tc_security_007_session_security(self):
        """测试用例TC_SECURITY_007: 会话安全测试"""
        print("\n执行测试用例: TC_SECURITY_007 - 会话安全")
        
        # 模拟会话管理
        class SessionManager:
            def __init__(self):
                self.sessions = {}
                self.session_timeout = 1800  # 30分钟
                self.max_sessions_per_user = 3
            
            def create_session(self, user_id, user_agent=None, ip_address=None):
                """创建会话"""
                import uuid
                import time
                
                session_id = str(uuid.uuid4())
                session_data = {
                    "user_id": user_id,
                    "created_at": time.time(),
                    "last_activity": time.time(),
                    "user_agent": user_agent,
                    "ip_address": ip_address,
                    "is_active": True
                }
                
                # 检查用户的活跃会话数量
                user_sessions = [s for s in self.sessions.values() 
                               if s["user_id"] == user_id and s["is_active"]]
                
                if len(user_sessions) >= self.max_sessions_per_user:
                    # 移除最旧的会话
                    oldest_session = min(user_sessions, key=lambda x: x["last_activity"])
                    for sid, sdata in self.sessions.items():
                        if sdata == oldest_session:
                            self.sessions[sid]["is_active"] = False
                            break
                
                self.sessions[session_id] = session_data
                return session_id
            
            def validate_session(self, session_id, user_agent=None, ip_address=None):
                """验证会话"""
                import time
                
                if session_id not in self.sessions:
                    return False, "会话不存在"
                
                session = self.sessions[session_id]
                
                if not session["is_active"]:
                    return False, "会话已失效"
                
                # 检查超时
                if time.time() - session["last_activity"] > self.session_timeout:
                    session["is_active"] = False
                    return False, "会话已超时"
                
                # 检查用户代理（可选）
                if user_agent and session["user_agent"] != user_agent:
                    return False, "用户代理不匹配"
                
                # 检查IP地址（可选）
                if ip_address and session["ip_address"] != ip_address:
                    return False, "IP地址不匹配"
                
                # 更新最后活动时间
                session["last_activity"] = time.time()
                return True, "会话有效"
            
            def destroy_session(self, session_id):
                """销毁会话"""
                if session_id in self.sessions:
                    self.sessions[session_id]["is_active"] = False
                    return True
                return False
            
            def cleanup_expired_sessions(self):
                """清理过期会话"""
                import time
                current_time = time.time()
                
                expired_count = 0
                for session in self.sessions.values():
                    if (session["is_active"] and 
                        current_time - session["last_activity"] > self.session_timeout):
                        session["is_active"] = False
                        expired_count += 1
                
                return expired_count
        
        # 测试会话管理
        session_manager = SessionManager()
        
        # 测试会话创建
        user_id = self.test_user.id
        session_id = session_manager.create_session(
            user_id, 
            user_agent="TestAgent/1.0", 
            ip_address="192.168.1.100"
        )
        
        self.assertIsNotNone(session_id)
        self.assertEqual(len(session_id), 36)  # UUID长度
        print(f"创建会话: {session_id}")
        
        # 测试会话验证
        is_valid, message = session_manager.validate_session(
            session_id, 
            user_agent="TestAgent/1.0", 
            ip_address="192.168.1.100"
        )
        self.assertTrue(is_valid)
        print(f"会话验证: {message}")
        
        # 测试用户代理不匹配
        is_valid, message = session_manager.validate_session(
            session_id, 
            user_agent="DifferentAgent/1.0", 
            ip_address="192.168.1.100"
        )
        self.assertFalse(is_valid)
        print(f"用户代理不匹配: {message}")
        
        # 测试IP地址不匹配
        is_valid, message = session_manager.validate_session(
            session_id, 
            user_agent="TestAgent/1.0", 
            ip_address="192.168.1.200"
        )
        self.assertFalse(is_valid)
        print(f"IP地址不匹配: {message}")
        
        # 测试并发会话限制
        session_ids = []
        for i in range(5):  # 创建5个会话，超过限制
            sid = session_manager.create_session(
                user_id, 
                user_agent=f"Agent{i}/1.0", 
                ip_address=f"192.168.1.{100+i}"
            )
            session_ids.append(sid)
        
        # 验证只有最近的3个会话是活跃的
        active_sessions = sum(1 for s in session_manager.sessions.values() 
                            if s["user_id"] == user_id and s["is_active"])
        self.assertEqual(active_sessions, 3)
        print(f"活跃会话数量: {active_sessions} (限制: {session_manager.max_sessions_per_user})")
        
        # 测试会话销毁
        destroyed = session_manager.destroy_session(session_ids[-1])
        self.assertTrue(destroyed)
        print("会话销毁: 成功")
        
        # 测试过期会话清理
        # 修改超时时间进行测试
        original_timeout = session_manager.session_timeout
        session_manager.session_timeout = 0.1  # 0.1秒超时
        time.sleep(0.2)  # 等待超时
        
        expired_count = session_manager.cleanup_expired_sessions()
        print(f"清理过期会话: {expired_count} 个")
        
        # 恢复原始超时时间
        session_manager.session_timeout = original_timeout
        
        print("会话安全测试完成")
    
    def test_tc_security_008_data_encryption(self):
        """测试用例TC_SECURITY_008: 数据加密安全测试"""
        print("\n执行测试用例: TC_SECURITY_008 - 数据加密安全")
        
        # 测试数据加密
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography模块未安装，跳过数据加密测试")
        import base64
        import hashlib
        
        # 生成加密密钥
        def generate_key():
            """生成加密密钥"""
            return Fernet.generate_key()
        
        # 数据加密
        def encrypt_data(data, key):
            """加密数据"""
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data)
            return encrypted_data
        
        # 数据解密
        def decrypt_data(encrypted_data, key):
            """解密数据"""
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        
        # 测试对称加密
        print("测试对称加密:")
        key = generate_key()
        sensitive_data = "学生身份证号: 110101199001011234"
        
        # 加密
        encrypted = encrypt_data(sensitive_data, key)
        self.assertNotEqual(sensitive_data.encode(), encrypted)
        self.assertGreater(len(encrypted), len(sensitive_data))
        print(f"原始数据: {sensitive_data}")
        print(f"加密数据: {encrypted[:50]}...")
        
        # 解密
        decrypted = decrypt_data(encrypted, key)
        self.assertEqual(sensitive_data, decrypted)
        print(f"解密数据: {decrypted}")
        
        # 测试错误密钥解密
        wrong_key = generate_key()
        try:
            decrypt_data(encrypted, wrong_key)
            self.fail("错误密钥应该解密失败")
        except Exception as e:
            print(f"错误密钥解密失败: {type(e).__name__}")
        
        # 测试数据哈希
        def hash_data(data, salt=None):
            """数据哈希"""
            if salt is None:
                salt = os.urandom(32)
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            hash_obj = hashlib.pbkdf2_hmac('sha256', data, salt, 100000)
            return salt + hash_obj
        
        def verify_hash(data, hashed_data):
            """验证哈希"""
            salt = hashed_data[:32]
            stored_hash = hashed_data[32:]
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            new_hash = hashlib.pbkdf2_hmac('sha256', data, salt, 100000)
            return new_hash == stored_hash
        
        # 测试数据哈希
        print("\n测试数据哈希:")
        original_data = "敏感信息需要哈希存储"
        hashed = hash_data(original_data)
        
        self.assertNotEqual(original_data.encode(), hashed)
        self.assertEqual(len(hashed), 64)  # 32字节盐 + 32字节哈希
        print(f"原始数据: {original_data}")
        print(f"哈希数据: {hashed.hex()}")
        
        # 验证哈希
        is_valid = verify_hash(original_data, hashed)
        self.assertTrue(is_valid)
        print(f"哈希验证: {'通过' if is_valid else '失败'}")
        
        # 测试错误数据验证
        is_valid = verify_hash("错误数据", hashed)
        self.assertFalse(is_valid)
        print(f"错误数据验证: {'通过' if is_valid else '失败'}")
        
        # 测试数据库字段加密
        def encrypt_sensitive_fields(user_data, encryption_key):
            """加密敏感字段"""
            sensitive_fields = ['phone_number', 'email', 'id_card']
            encrypted_data = user_data.copy()
            
            for field in sensitive_fields:
                if field in encrypted_data and encrypted_data[field]:
                    encrypted_data[field] = encrypt_data(
                        encrypted_data[field], 
                        encryption_key
                    ).decode('latin-1')  # 存储为字符串
            
            return encrypted_data
        
        def decrypt_sensitive_fields(encrypted_data, encryption_key):
            """解密敏感字段"""
            sensitive_fields = ['phone_number', 'email', 'id_card']
            decrypted_data = encrypted_data.copy()
            
            for field in sensitive_fields:
                if field in decrypted_data and decrypted_data[field]:
                    try:
                        decrypted_data[field] = decrypt_data(
                            decrypted_data[field].encode('latin-1'), 
                            encryption_key
                        )
                    except Exception:
                        # 如果解密失败，可能是未加密的数据
                        pass
            
            return decrypted_data
        
        # 测试字段级加密
        print("\n测试字段级加密:")
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "phone_number": "13800138000",
            "id_card": "110101199001011234"
        }
        
        encryption_key = generate_key()
        encrypted_user = encrypt_sensitive_fields(user_data, encryption_key)
        
        # 验证敏感字段被加密
        self.assertNotEqual(user_data["email"], encrypted_user["email"])
        self.assertNotEqual(user_data["phone_number"], encrypted_user["phone_number"])
        self.assertEqual(user_data["username"], encrypted_user["username"])  # 非敏感字段不加密
        
        print(f"原始邮箱: {user_data['email']}")
        print(f"加密邮箱: {encrypted_user['email'][:30]}...")
        
        # 解密验证
        decrypted_user = decrypt_sensitive_fields(encrypted_user, encryption_key)
        self.assertEqual(user_data["email"], decrypted_user["email"])
        self.assertEqual(user_data["phone_number"], decrypted_user["phone_number"])
        
        print(f"解密邮箱: {decrypted_user['email']}")
        
        print("数据加密安全测试完成")


if __name__ == '__main__':
    unittest.main(verbosity=2)