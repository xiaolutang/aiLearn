#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手核心功能测试

功能：
1. 测试备课模块功能
2. 测试上课模块功能
3. 测试成绩管理功能
4. 测试AI功能集成
5. 验证数据处理和分析

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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('core_functions_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CoreFunctionsTester:
    """核心功能测试类"""
    
    def __init__(self, config_file: str = "test_accounts.json", base_url: str = "http://localhost:8000"):
        self.config_file = config_file
        self.base_url = base_url
        self.test_accounts = {}
        self.session_tokens = {}
        self.test_results = []
        self.test_data = {}
        
        # 初始化测试数据
        self._init_test_data()
        
        # 加载测试账号
        self._load_test_accounts()
        
        logger.info(f"核心功能测试器初始化完成，基础URL: {self.base_url}")
    
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
    
    def _init_test_data(self):
        """初始化测试数据"""
        self.test_data = {
            # 备课测试数据
            "lesson_preparation": {
                "materials": [
                    {
                        "title": "高中数学必修一 - 函数的概念",
                        "content": "函数是数学中的重要概念，描述两个变量之间的对应关系。",
                        "grade": "高一",
                        "subject": "数学",
                        "chapter": "第一章",
                        "difficulty": "中等"
                    },
                    {
                        "title": "高中物理必修一 - 匀变速直线运动",
                        "content": "匀变速直线运动是物理学中的基础运动形式。",
                        "grade": "高一",
                        "subject": "物理",
                        "chapter": "第二章",
                        "difficulty": "中等"
                    }
                ],
                "lesson_plans": [
                    {
                        "title": "函数概念教学设计",
                        "objective": "让学生理解函数的定义和基本性质",
                        "duration": 45,
                        "activities": [
                            {"type": "导入", "duration": 5, "content": "复习映射概念"},
                            {"type": "新课", "duration": 30, "content": "函数定义和表示方法"},
                            {"type": "练习", "duration": 8, "content": "基础练习题"},
                            {"type": "总结", "duration": 2, "content": "课堂小结"}
                        ]
                    }
                ]
            },
            
            # 上课测试数据
            "classroom": {
                "interactions": [
                    {
                        "type": "提问",
                        "question": "什么是函数？",
                        "expected_answer": "函数是两个变量之间的对应关系",
                        "difficulty": "基础"
                    },
                    {
                        "type": "讨论",
                        "topic": "函数在生活中的应用",
                        "duration": 10
                    }
                ],
                "experiments": [
                    {
                        "name": "函数图像绘制实验",
                        "type": "数学实验",
                        "tools": ["图形计算器", "坐标纸"],
                        "steps": [
                            "选择函数表达式",
                            "计算关键点",
                            "绘制函数图像",
                            "分析函数性质"
                        ]
                    }
                ]
            },
            
            # 成绩管理测试数据
            "grade_management": {
                "exams": [
                    {
                        "name": "期中考试",
                        "subject": "数学",
                        "date": "2024-11-15",
                        "total_score": 100,
                        "duration": 120
                    },
                    {
                        "name": "月考",
                        "subject": "物理",
                        "date": "2024-11-20",
                        "total_score": 100,
                        "duration": 90
                    }
                ],
                "students": [
                    {"id": "student_001", "name": "张三", "class": "高一(1)班"},
                    {"id": "student_002", "name": "李四", "class": "高一(1)班"},
                    {"id": "student_003", "name": "王五", "class": "高一(2)班"},
                    {"id": "student_004", "name": "赵六", "class": "高一(2)班"}
                ],
                "grades": [
                    {"student_id": "student_001", "exam": "期中考试", "subject": "数学", "score": 85},
                    {"student_id": "student_002", "exam": "期中考试", "subject": "数学", "score": 92},
                    {"student_id": "student_003", "exam": "期中考试", "subject": "数学", "score": 78},
                    {"student_id": "student_004", "exam": "期中考试", "subject": "数学", "score": 88}
                ]
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
    
    async def test_material_analysis(self, account_id: str) -> Dict:
        """测试教材分析功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            material = self.test_data["lesson_preparation"]["materials"][0]
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/lesson/material-analysis", 
                                       json=material, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"教材分析测试成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "analysis_result": result,
                            "material_title": material["title"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"教材分析测试失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"教材分析测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_lesson_planning(self, account_id: str) -> Dict:
        """测试课程规划功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            lesson_plan = self.test_data["lesson_preparation"]["lesson_plans"][0]
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/lesson/planning", 
                                       json=lesson_plan, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"课程规划测试成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "planning_result": result,
                            "lesson_title": lesson_plan["title"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"课程规划测试失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"课程规划测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_ai_status_generation(self, account_id: str) -> Dict:
        """测试AI学情生成功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            
            # 模拟学生学习数据
            student_data = {
                "student_id": "student_001",
                "subject": "数学",
                "recent_scores": [85, 78, 92, 88, 76],
                "learning_time": 120,  # 分钟
                "difficulty_areas": ["函数性质", "图像变换"],
                "strengths": ["基础计算", "概念理解"]
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/classroom/ai-status", 
                                       json=student_data, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"AI学情生成测试成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "ai_analysis": result,
                            "student_id": student_data["student_id"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"AI学情生成测试失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"AI学情生成测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_classroom_interaction(self, account_id: str) -> Dict:
        """测试课堂互动功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            interaction = self.test_data["classroom"]["interactions"][0]
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/classroom/interaction", 
                                       json=interaction, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"课堂互动测试成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "interaction_result": result,
                            "interaction_type": interaction["type"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"课堂互动测试失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"课堂互动测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_grade_input(self, account_id: str) -> Dict:
        """测试成绩录入功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            
            # 构建成绩录入数据
            exam = self.test_data["grade_management"]["exams"][0]
            grades = self.test_data["grade_management"]["grades"]
            
            grade_data = {
                "exam_name": exam["name"],
                "subject": exam["subject"],
                "date": exam["date"],
                "total_score": exam["total_score"],
                "grades": grades
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/grades/input", 
                                       json=grade_data, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"成绩录入测试成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "input_result": result,
                            "exam_name": exam["name"],
                            "grade_count": len(grades)
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"成绩录入测试失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"成绩录入测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_grade_analysis(self, account_id: str) -> Dict:
        """测试成绩分析功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            
            # 构建分析请求数据
            analysis_data = {
                "exam_name": "期中考试",
                "subject": "数学",
                "class_id": "高一(1)班",
                "analysis_type": "comprehensive",
                "include_trends": True,
                "include_distribution": True
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/grades/analysis", 
                                       json=analysis_data, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"成绩分析测试成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "analysis_result": result,
                            "exam_name": analysis_data["exam_name"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"成绩分析测试失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"成绩分析测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_personalized_tutoring(self, account_id: str) -> Dict:
        """测试个性化辅导功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            
            # 构建个性化辅导请求数据
            tutoring_data = {
                "student_id": "student_001",
                "subject": "数学",
                "weak_areas": ["函数性质", "图像变换"],
                "learning_style": "视觉型",
                "difficulty_level": "中等",
                "time_available": 60  # 分钟
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/grades/personalized-tutoring", 
                                       json=tutoring_data, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"个性化辅导测试成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "tutoring_plan": result,
                            "student_id": tutoring_data["student_id"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"个性化辅导测试失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"个性化辅导测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_data_export(self, account_id: str) -> Dict:
        """测试数据导出功能"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            
            # 构建导出请求数据
            export_data = {
                "export_type": "grades",
                "format": "excel",
                "filters": {
                    "exam_name": "期中考试",
                    "subject": "数学",
                    "date_range": {
                        "start": "2024-11-01",
                        "end": "2024-11-30"
                    }
                },
                "include_analysis": True
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/data/export", 
                                       json=export_data, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"数据导出测试成功，响应时间: {response_time:.2f}s")
                        return {
                            "success": True,
                            "response_time": response_time,
                            "export_result": result,
                            "export_type": export_data["export_type"]
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"数据导出测试失败，状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
        except Exception as e:
            logger.error(f"数据导出测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_role_specific_functions(self, account_id: str) -> List[Dict]:
        """测试角色特定功能"""
        account = self.test_accounts[account_id]
        role = account['role']
        
        logger.info(f"开始测试角色 {role} 的特定功能...")
        
        results = []
        
        if role == "教师":
            # 教师角色测试所有功能
            test_functions = [
                ("教材分析", self.test_material_analysis),
                ("课程规划", self.test_lesson_planning),
                ("AI学情生成", self.test_ai_status_generation),
                ("课堂互动", self.test_classroom_interaction),
                ("成绩录入", self.test_grade_input),
                ("成绩分析", self.test_grade_analysis),
                ("个性化辅导", self.test_personalized_tutoring),
                ("数据导出", self.test_data_export)
            ]
        elif role in ["校长", "教务主任"]:
            # 管理角色主要测试分析和导出功能
            test_functions = [
                ("成绩分析", self.test_grade_analysis),
                ("数据导出", self.test_data_export)
            ]
        elif role == "学生":
            # 学生角色主要测试查看功能
            test_functions = [
                ("成绩分析", self.test_grade_analysis)
            ]
        elif role == "家长":
            # 家长角色主要测试查看功能
            test_functions = [
                ("成绩分析", self.test_grade_analysis)
            ]
        else:
            # 其他角色
            test_functions = []
        
        for function_name, test_function in test_functions:
            try:
                result = await test_function(account_id)
                result["function_name"] = function_name
                result["role"] = role
                result["account_id"] = account_id
                results.append(result)
                
                # 添加延迟避免请求过于频繁
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"测试功能 {function_name} 异常: {e}")
                results.append({
                    "success": False,
                    "function_name": function_name,
                    "role": role,
                    "account_id": account_id,
                    "error": str(e)
                })
        
        return results
    
    async def run_full_core_functions_test(self) -> Dict:
        """运行完整的核心功能测试套件"""
        logger.info("开始执行完整核心功能测试套件...")
        
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
        
        # 测试每个角色的核心功能
        role_function_results = {}
        for account_id in authenticated_accounts:
            results = await self.test_role_specific_functions(account_id)
            role_function_results[account_id] = results
        
        test_results["tests"]["role_functions"] = role_function_results
        
        # 生成测试摘要
        test_results["end_time"] = datetime.now().isoformat()
        
        # 统计测试结果
        total_tests = 0
        successful_tests = 0
        role_stats = {}
        
        for account_id, results in role_function_results.items():
            account = self.test_accounts[account_id]
            role = account['role']
            
            if role not in role_stats:
                role_stats[role] = {"total": 0, "successful": 0, "functions": []}
            
            for result in results:
                total_tests += 1
                role_stats[role]["total"] += 1
                
                if result.get("success", False):
                    successful_tests += 1
                    role_stats[role]["successful"] += 1
                
                function_name = result.get("function_name", "未知")
                if function_name not in role_stats[role]["functions"]:
                    role_stats[role]["functions"].append(function_name)
        
        summary = {
            "total_accounts": len(authenticated_accounts),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "overall_success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "role_statistics": {}
        }
        
        # 计算每个角色的成功率
        for role, stats in role_stats.items():
            success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
            summary["role_statistics"][role] = {
                "total_tests": stats["total"],
                "successful_tests": stats["successful"],
                "success_rate": success_rate,
                "tested_functions": stats["functions"]
            }
        
        test_results["summary"] = summary
        
        # 保存测试结果
        with open("core_functions_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        logger.info("核心功能测试套件执行完成")
        logger.info(f"总体成功率: {summary['overall_success_rate']:.1f}%")
        
        for role, stats in summary["role_statistics"].items():
            logger.info(f"角色 {role}: {stats['success_rate']:.1f}% ({stats['successful_tests']}/{stats['total_tests']})")
        
        return test_results

# 主执行函数
async def main():
    """主执行函数"""
    try:
        # 初始化核心功能测试器
        tester = CoreFunctionsTester()
        
        # 运行完整核心功能测试
        results = await tester.run_full_core_functions_test()
        
        # 输出测试结果摘要
        print("\n" + "="*50)
        print("核心功能测试结果摘要")
        print("="*50)
        
        summary = results["summary"]
        print(f"测试账号总数: {summary['total_accounts']}")
        print(f"测试用例总数: {summary['total_tests']}")
        print(f"成功测试数: {summary['successful_tests']}")
        print(f"总体成功率: {summary['overall_success_rate']:.1f}%")
        
        print("\n各角色测试结果:")
        for role, stats in summary["role_statistics"].items():
            print(f"  {role}: {stats['success_rate']:.1f}% ({stats['successful_tests']}/{stats['total_tests']})")
            print(f"    测试功能: {', '.join(stats['tested_functions'])}")
        
        print("\n详细测试结果已保存到: core_functions_test_results.json")
        print("测试日志已保存到: core_functions_test.log")
        
    except Exception as e:
        logger.error(f"核心功能测试执行失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())