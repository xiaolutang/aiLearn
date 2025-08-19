#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手性能测试

功能：
1. 测试系统响应时间
2. 测试数据处理性能
3. 测试内存使用情况
4. 测试数据库查询性能
5. 测试大数据量处理能力

作者：测试工程师
日期：2024年12月
"""

import json
import asyncio
import aiohttp
import time
import psutil
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import sys
import os
import random
import string

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PerformanceTester:
    """性能测试类"""
    
    def __init__(self, config_file: str = "test_accounts.json", base_url: str = "http://localhost:8000"):
        self.config_file = config_file
        self.base_url = base_url
        self.test_accounts = {}
        self.session_tokens = {}
        self.test_results = []
        
        # 性能测试配置
        self.response_time_threshold = 2.0  # 秒
        self.memory_threshold = 500  # MB
        self.cpu_threshold = 80  # 百分比
        
        # 加载测试账号
        self._load_test_accounts()
        
        logger.info(f"性能测试器初始化完成，基础URL: {self.base_url}")
    
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
    
    def get_system_metrics(self) -> Dict:
        """获取系统性能指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            memory_available_mb = memory.available / 1024 / 1024
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # 网络IO
            network = psutil.net_io_counters()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory": {
                    "percent": memory_percent,
                    "used_mb": memory_used_mb,
                    "available_mb": memory_available_mb,
                    "total_mb": memory.total / 1024 / 1024
                },
                "disk_percent": disk_percent,
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {}
    
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
                        self.session_tokens[account_id] = token
                        
                        return {
                            "success": True,
                            "account_id": account_id,
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
    
    async def test_api_response_time(self, account_id: str, endpoint: str, method: str = "GET", data: Dict = None, iterations: int = 10) -> Dict:
        """测试API响应时间"""
        if account_id not in self.session_tokens:
            auth_result = await self.authenticate_user(account_id)
            if not auth_result.get("success", False):
                return {"success": False, "error": "认证失败"}
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        status_codes = []
        
        headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    if method.upper() == "GET":
                        async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                            response_time = time.time() - start_time
                            status_codes.append(response.status)
                            
                            if response.status == 200:
                                await response.json()  # 确保完全接收响应
                                response_times.append(response_time)
                                successful_requests += 1
                            else:
                                failed_requests += 1
                    
                    elif method.upper() == "POST":
                        async with session.post(f"{self.base_url}{endpoint}", json=data, headers=headers) as response:
                            response_time = time.time() - start_time
                            status_codes.append(response.status)
                            
                            if response.status in [200, 201]:
                                await response.json()  # 确保完全接收响应
                                response_times.append(response_time)
                                successful_requests += 1
                            else:
                                failed_requests += 1
                
                # 短暂等待，避免过于频繁的请求
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_requests += 1
                logger.error(f"API请求异常: {e}")
        
        # 计算统计信息
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # 计算95百分位数
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = median_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        success_rate = (successful_requests / iterations * 100) if iterations > 0 else 0
        
        # 性能评级
        if avg_response_time <= 0.5:
            performance_rating = "优秀"
        elif avg_response_time <= 1.0:
            performance_rating = "良好"
        elif avg_response_time <= 2.0:
            performance_rating = "一般"
        else:
            performance_rating = "需要优化"
        
        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "response_times": {
                "average": avg_response_time,
                "median": median_response_time,
                "min": min_response_time,
                "max": max_response_time,
                "p95": p95_response_time
            },
            "performance_rating": performance_rating,
            "meets_threshold": avg_response_time <= self.response_time_threshold,
            "status_codes": list(set(status_codes))
        }
    
    async def test_large_data_processing(self, account_id: str) -> Dict:
        """测试大数据量处理性能"""
        logger.info("开始测试大数据量处理性能...")
        
        # 生成大量测试数据
        def generate_large_grade_data(num_students: int = 1000, num_subjects: int = 10):
            """生成大量成绩数据"""
            subjects = ["数学", "语文", "英语", "物理", "化学", "生物", "历史", "地理", "政治", "体育"]
            grades_data = []
            
            for student_id in range(1, num_students + 1):
                for subject in subjects[:num_subjects]:
                    grade = {
                        "student_id": f"student_{student_id:04d}",
                        "student_name": f"学生{student_id}",
                        "subject": subject,
                        "score": random.randint(60, 100),
                        "exam_name": "期末考试",
                        "exam_date": "2024-01-15",
                        "class_name": f"高一{(student_id - 1) // 50 + 1}班"
                    }
                    grades_data.append(grade)
            
            return grades_data
        
        test_results = {}
        
        # 测试不同数据量的处理性能
        data_sizes = [100, 500, 1000, 2000]
        
        for size in data_sizes:
            logger.info(f"测试 {size} 条数据的处理性能...")
            
            # 生成测试数据
            test_data = generate_large_grade_data(num_students=size//10, num_subjects=10)
            
            # 记录系统指标（处理前）
            metrics_before = self.get_system_metrics()
            
            start_time = time.time()
            
            # 批量上传成绩数据
            upload_result = await self.test_api_response_time(
                account_id,
                "/api/grades/batch-upload",
                "POST",
                {"grades": test_data},
                iterations=1
            )
            
            processing_time = time.time() - start_time
            
            # 记录系统指标（处理后）
            metrics_after = self.get_system_metrics()
            
            # 计算性能指标
            records_per_second = len(test_data) / processing_time if processing_time > 0 else 0
            
            # 计算内存使用变化
            memory_usage_change = 0
            if metrics_before and metrics_after:
                memory_usage_change = metrics_after["memory"]["used_mb"] - metrics_before["memory"]["used_mb"]
            
            test_results[f"{size}_records"] = {
                "data_size": len(test_data),
                "processing_time": processing_time,
                "records_per_second": records_per_second,
                "upload_success": upload_result.get("success_rate", 0) > 0,
                "response_time": upload_result.get("response_times", {}).get("average", 0),
                "memory_usage_change_mb": memory_usage_change,
                "system_metrics_before": metrics_before,
                "system_metrics_after": metrics_after
            }
            
            # 等待系统恢复
            await asyncio.sleep(2)
        
        # 分析性能趋势
        processing_times = [result["processing_time"] for result in test_results.values()]
        records_per_second_values = [result["records_per_second"] for result in test_results.values()]
        
        # 计算性能评级
        avg_records_per_second = statistics.mean(records_per_second_values) if records_per_second_values else 0
        
        if avg_records_per_second >= 1000:
            performance_rating = "优秀"
        elif avg_records_per_second >= 500:
            performance_rating = "良好"
        elif avg_records_per_second >= 200:
            performance_rating = "一般"
        else:
            performance_rating = "需要优化"
        
        return {
            "test_type": "大数据量处理性能测试",
            "test_results": test_results,
            "performance_summary": {
                "avg_records_per_second": avg_records_per_second,
                "max_records_per_second": max(records_per_second_values) if records_per_second_values else 0,
                "min_records_per_second": min(records_per_second_values) if records_per_second_values else 0,
                "performance_rating": performance_rating
            }
        }
    
    async def test_memory_usage(self, account_id: str, duration: int = 60) -> Dict:
        """测试内存使用情况"""
        logger.info(f"开始测试内存使用情况，持续 {duration} 秒...")
        
        memory_samples = []
        start_time = time.time()
        end_time = start_time + duration
        
        # 定义测试操作
        test_operations = [
            ("/api/grades/list", "GET", None),
            ("/api/grades/analysis", "POST", {
                "exam_name": "测试考试",
                "subject": "数学",
                "analysis_type": "detailed"
            }),
            ("/api/lesson/material-analysis", "POST", {
                "title": "测试教材",
                "content": "这是一个测试教材内容" * 100,  # 较大的内容
                "subject": "数学"
            }),
            ("/api/data/export", "POST", {
                "export_type": "grades",
                "format": "excel",
                "filters": {}
            })
        ]
        
        operation_count = 0
        
        while time.time() < end_time:
            # 记录当前内存使用情况
            metrics = self.get_system_metrics()
            if metrics:
                memory_samples.append({
                    "timestamp": metrics["timestamp"],
                    "memory_used_mb": metrics["memory"]["used_mb"],
                    "memory_percent": metrics["memory"]["percent"],
                    "cpu_percent": metrics["cpu_percent"],
                    "operation_count": operation_count
                })
            
            # 执行随机操作
            endpoint, method, data = random.choice(test_operations)
            
            try:
                await self.test_api_response_time(account_id, endpoint, method, data, iterations=1)
                operation_count += 1
            except Exception as e:
                logger.error(f"内存测试操作异常: {e}")
            
            # 等待一段时间
            await asyncio.sleep(2)
        
        # 分析内存使用情况
        if memory_samples:
            memory_values = [sample["memory_used_mb"] for sample in memory_samples]
            memory_percentages = [sample["memory_percent"] for sample in memory_samples]
            cpu_values = [sample["cpu_percent"] for sample in memory_samples]
            
            memory_stats = {
                "initial_memory_mb": memory_values[0] if memory_values else 0,
                "final_memory_mb": memory_values[-1] if memory_values else 0,
                "peak_memory_mb": max(memory_values) if memory_values else 0,
                "avg_memory_mb": statistics.mean(memory_values) if memory_values else 0,
                "memory_growth_mb": (memory_values[-1] - memory_values[0]) if len(memory_values) >= 2 else 0,
                "peak_memory_percent": max(memory_percentages) if memory_percentages else 0,
                "avg_cpu_percent": statistics.mean(cpu_values) if cpu_values else 0,
                "peak_cpu_percent": max(cpu_values) if cpu_values else 0
            }
            
            # 内存使用评级
            if memory_stats["peak_memory_percent"] <= 60:
                memory_rating = "优秀"
            elif memory_stats["peak_memory_percent"] <= 75:
                memory_rating = "良好"
            elif memory_stats["peak_memory_percent"] <= 85:
                memory_rating = "一般"
            else:
                memory_rating = "需要优化"
            
            # 检查内存泄漏
            memory_leak_detected = memory_stats["memory_growth_mb"] > 100  # 增长超过100MB认为可能有内存泄漏
            
        else:
            memory_stats = {}
            memory_rating = "无法评估"
            memory_leak_detected = False
        
        return {
            "test_type": "内存使用测试",
            "test_duration": duration,
            "total_operations": operation_count,
            "memory_statistics": memory_stats,
            "memory_rating": memory_rating,
            "memory_leak_detected": memory_leak_detected,
            "memory_samples": memory_samples,
            "meets_memory_threshold": memory_stats.get("peak_memory_percent", 100) <= 80
        }
    
    async def test_database_performance(self, account_id: str) -> Dict:
        """测试数据库查询性能"""
        logger.info("开始测试数据库查询性能...")
        
        # 定义不同复杂度的查询操作
        query_tests = [
            {
                "name": "简单查询",
                "endpoint": "/api/grades/list",
                "method": "GET",
                "data": None,
                "expected_time": 0.5
            },
            {
                "name": "条件查询",
                "endpoint": "/api/grades/search",
                "method": "POST",
                "data": {
                    "filters": {
                        "subject": "数学",
                        "score_range": {"min": 80, "max": 100}
                    }
                },
                "expected_time": 1.0
            },
            {
                "name": "聚合查询",
                "endpoint": "/api/grades/statistics",
                "method": "POST",
                "data": {
                    "group_by": ["subject", "class_name"],
                    "metrics": ["avg", "max", "min", "count"]
                },
                "expected_time": 2.0
            },
            {
                "name": "复杂分析查询",
                "endpoint": "/api/grades/advanced-analysis",
                "method": "POST",
                "data": {
                    "analysis_type": "trend_analysis",
                    "time_range": "last_semester",
                    "include_predictions": True
                },
                "expected_time": 3.0
            },
            {
                "name": "大数据量查询",
                "endpoint": "/api/grades/export",
                "method": "POST",
                "data": {
                    "format": "json",
                    "include_all_fields": True,
                    "date_range": "all_time"
                },
                "expected_time": 5.0
            }
        ]
        
        query_results = []
        
        for query_test in query_tests:
            logger.info(f"测试 {query_test['name']}...")
            
            # 执行查询性能测试
            result = await self.test_api_response_time(
                account_id,
                query_test["endpoint"],
                query_test["method"],
                query_test["data"],
                iterations=5
            )
            
            # 添加期望时间和性能评估
            result["query_name"] = query_test["name"]
            result["expected_time"] = query_test["expected_time"]
            result["meets_expectation"] = result["response_times"]["average"] <= query_test["expected_time"]
            
            # 查询性能评级
            actual_time = result["response_times"]["average"]
            expected_time = query_test["expected_time"]
            
            if actual_time <= expected_time * 0.5:
                result["query_performance"] = "优秀"
            elif actual_time <= expected_time:
                result["query_performance"] = "良好"
            elif actual_time <= expected_time * 1.5:
                result["query_performance"] = "一般"
            else:
                result["query_performance"] = "需要优化"
            
            query_results.append(result)
            
            # 等待一段时间
            await asyncio.sleep(1)
        
        # 计算总体数据库性能
        successful_queries = sum(1 for result in query_results if result["success_rate"] > 80)
        total_queries = len(query_results)
        
        avg_response_times = [result["response_times"]["average"] for result in query_results if result["success_rate"] > 0]
        overall_avg_response_time = statistics.mean(avg_response_times) if avg_response_times else 0
        
        queries_meeting_expectation = sum(1 for result in query_results if result["meets_expectation"])
        expectation_rate = (queries_meeting_expectation / total_queries * 100) if total_queries > 0 else 0
        
        # 总体数据库性能评级
        if expectation_rate >= 90 and overall_avg_response_time <= 2.0:
            overall_db_performance = "优秀"
        elif expectation_rate >= 80 and overall_avg_response_time <= 3.0:
            overall_db_performance = "良好"
        elif expectation_rate >= 70 and overall_avg_response_time <= 5.0:
            overall_db_performance = "一般"
        else:
            overall_db_performance = "需要优化"
        
        return {
            "test_type": "数据库查询性能测试",
            "query_results": query_results,
            "performance_summary": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "success_rate": (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                "queries_meeting_expectation": queries_meeting_expectation,
                "expectation_rate": expectation_rate,
                "overall_avg_response_time": overall_avg_response_time,
                "overall_performance_rating": overall_db_performance
            }
        }
    
    async def run_full_performance_test(self) -> Dict:
        """运行完整的性能测试套件"""
        logger.info("开始执行完整性能测试套件...")
        
        test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
        # 选择一个教师账号进行测试
        teacher_accounts = [acc_id for acc_id, acc in self.test_accounts.items() 
                           if acc['role'] == 'teacher' and acc['status'] == 'active']
        
        if not teacher_accounts:
            logger.error("没有找到活跃的教师账号")
            return test_results
        
        test_account = teacher_accounts[0]
        logger.info(f"使用账号 {test_account} 进行性能测试")
        
        # 认证测试账号
        auth_result = await self.authenticate_user(test_account)
        if not auth_result.get("success", False):
            logger.error("测试账号认证失败")
            return test_results
        
        # 1. API响应时间测试
        logger.info("执行API响应时间测试...")
        api_endpoints = [
            ("/api/user/profile", "GET", None),
            ("/api/grades/list", "GET", None),
            ("/api/lesson/list", "GET", None),
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
        
        api_response_results = []
        for endpoint, method, data in api_endpoints:
            result = await self.test_api_response_time(test_account, endpoint, method, data, iterations=10)
            api_response_results.append(result)
        
        test_results["tests"]["api_response_time"] = api_response_results
        
        # 2. 大数据量处理性能测试
        logger.info("执行大数据量处理性能测试...")
        large_data_result = await self.test_large_data_processing(test_account)
        test_results["tests"]["large_data_processing"] = large_data_result
        
        # 3. 内存使用测试
        logger.info("执行内存使用测试...")
        memory_result = await self.test_memory_usage(test_account, duration=30)
        test_results["tests"]["memory_usage"] = memory_result
        
        # 4. 数据库查询性能测试
        logger.info("执行数据库查询性能测试...")
        db_performance_result = await self.test_database_performance(test_account)
        test_results["tests"]["database_performance"] = db_performance_result
        
        # 生成测试摘要
        test_results["end_time"] = datetime.now().isoformat()
        
        # 计算各项性能指标
        api_avg_times = [result["response_times"]["average"] for result in api_response_results if result["success_rate"] > 0]
        overall_api_avg_time = statistics.mean(api_avg_times) if api_avg_times else 0
        
        api_success_rates = [result["success_rate"] for result in api_response_results]
        overall_api_success_rate = statistics.mean(api_success_rates) if api_success_rates else 0
        
        summary = {
            "test_account": test_account,
            "api_performance": {
                "overall_avg_response_time": overall_api_avg_time,
                "overall_success_rate": overall_api_success_rate,
                "meets_response_threshold": overall_api_avg_time <= self.response_time_threshold,
                "tested_endpoints": len(api_endpoints)
            },
            "data_processing_performance": {
                "avg_records_per_second": large_data_result["performance_summary"]["avg_records_per_second"],
                "performance_rating": large_data_result["performance_summary"]["performance_rating"]
            },
            "memory_performance": {
                "peak_memory_percent": memory_result["memory_statistics"].get("peak_memory_percent", 0),
                "memory_rating": memory_result["memory_rating"],
                "memory_leak_detected": memory_result["memory_leak_detected"],
                "meets_memory_threshold": memory_result["meets_memory_threshold"]
            },
            "database_performance": {
                "overall_avg_response_time": db_performance_result["performance_summary"]["overall_avg_response_time"],
                "expectation_rate": db_performance_result["performance_summary"]["expectation_rate"],
                "performance_rating": db_performance_result["performance_summary"]["overall_performance_rating"]
            }
        }
        
        # 计算总体性能评分
        performance_scores = []
        
        # API性能评分 (0-100)
        if overall_api_avg_time <= 0.5:
            api_score = 100
        elif overall_api_avg_time <= 1.0:
            api_score = 85
        elif overall_api_avg_time <= 2.0:
            api_score = 70
        else:
            api_score = 50
        performance_scores.append(api_score)
        
        # 数据处理性能评分 (0-100)
        records_per_second = large_data_result["performance_summary"]["avg_records_per_second"]
        if records_per_second >= 1000:
            data_score = 100
        elif records_per_second >= 500:
            data_score = 85
        elif records_per_second >= 200:
            data_score = 70
        else:
            data_score = 50
        performance_scores.append(data_score)
        
        # 内存性能评分 (0-100)
        memory_percent = memory_result["memory_statistics"].get("peak_memory_percent", 100)
        if memory_percent <= 60:
            memory_score = 100
        elif memory_percent <= 75:
            memory_score = 85
        elif memory_percent <= 85:
            memory_score = 70
        else:
            memory_score = 50
        performance_scores.append(memory_score)
        
        # 数据库性能评分 (0-100)
        expectation_rate = db_performance_result["performance_summary"]["expectation_rate"]
        if expectation_rate >= 90:
            db_score = 100
        elif expectation_rate >= 80:
            db_score = 85
        elif expectation_rate >= 70:
            db_score = 70
        else:
            db_score = 50
        performance_scores.append(db_score)
        
        overall_performance_score = statistics.mean(performance_scores) if performance_scores else 0
        
        if overall_performance_score >= 90:
            overall_rating = "优秀"
        elif overall_performance_score >= 80:
            overall_rating = "良好"
        elif overall_performance_score >= 70:
            overall_rating = "一般"
        else:
            overall_rating = "需要优化"
        
        summary["overall_performance"] = {
            "score": overall_performance_score,
            "rating": overall_rating,
            "component_scores": {
                "api_performance": api_score,
                "data_processing": data_score,
                "memory_usage": memory_score,
                "database_performance": db_score
            }
        }
        
        test_results["summary"] = summary
        
        # 保存测试结果
        with open("performance_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        logger.info("性能测试套件执行完成")
        logger.info(f"总体性能评分: {overall_performance_score:.1f}分 ({overall_rating})")
        
        return test_results

# 主执行函数
async def main():
    """主执行函数"""
    try:
        # 初始化性能测试器
        tester = PerformanceTester()
        
        # 运行完整性能测试
        results = await tester.run_full_performance_test()
        
        # 输出测试结果摘要
        print("\n" + "="*50)
        print("性能测试结果摘要")
        print("="*50)
        
        summary = results["summary"]
        if summary:
            overall_perf = summary["overall_performance"]
            print(f"总体性能评分: {overall_perf['score']:.1f}分")
            print(f"性能等级: {overall_perf['rating']}")
            
            print("\n各项性能指标:")
            
            api_perf = summary["api_performance"]
            print(f"  API响应性能: {api_perf['overall_avg_response_time']:.2f}s (成功率 {api_perf['overall_success_rate']:.1f}%)")
            
            data_perf = summary["data_processing_performance"]
            print(f"  数据处理性能: {data_perf['avg_records_per_second']:.0f} 记录/秒 ({data_perf['performance_rating']})")
            
            memory_perf = summary["memory_performance"]
            print(f"  内存使用: 峰值 {memory_perf['peak_memory_percent']:.1f}% ({memory_perf['memory_rating']})")
            
            db_perf = summary["database_performance"]
            print(f"  数据库性能: 期望达成率 {db_perf['expectation_rate']:.1f}% ({db_perf['performance_rating']})")
            
            print("\n组件评分:")
            comp_scores = overall_perf["component_scores"]
            print(f"  API性能: {comp_scores['api_performance']}分")
            print(f"  数据处理: {comp_scores['data_processing']}分")
            print(f"  内存使用: {comp_scores['memory_usage']}分")
            print(f"  数据库性能: {comp_scores['database_performance']}分")
        
        print("\n详细测试结果已保存到: performance_test_results.json")
        print("测试日志已保存到: performance_test.log")
        
    except Exception as e:
        logger.error(f"性能测试执行失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())