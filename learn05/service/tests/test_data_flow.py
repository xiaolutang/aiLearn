#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手数据流测试

功能：
1. 测试客户端-服务端数据同步
2. 验证数据一致性
3. 测试数据传输完整性
4. 验证数据缓存机制
5. 测试离线数据处理

作者：测试工程师
日期：2024年12月
"""

import json
import asyncio
import aiohttp
import time
import hashlib
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
        logging.FileHandler('data_flow_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataFlowTester:
    """数据流测试类"""
    
    def __init__(self, config_file: str = "test_accounts.json", base_url: str = "http://localhost:8000"):
        self.config_file = config_file
        self.base_url = base_url
        self.test_accounts = {}
        self.session_tokens = {}
        self.test_data_cache = {}
        self.data_checksums = {}
        
        # 加载测试账号
        self._load_test_accounts()
        
        # 初始化测试数据
        self._init_test_data()
        
        logger.info(f"数据流测试器初始化完成，基础URL: {self.base_url}")
    
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
        self.test_data_cache = {
            "students": [
                {
                    "id": f"student_{i:03d}",
                    "name": f"学生{i}",
                    "class": f"高一({(i-1)//10+1})班",
                    "grade": "高一",
                    "subjects": ["数学", "物理", "化学", "英语", "语文"]
                }
                for i in range(1, 51)  # 50个学生
            ],
            "exams": [
                {
                    "id": f"exam_{i:03d}",
                    "name": f"测试考试{i}",
                    "subject": random.choice(["数学", "物理", "化学", "英语", "语文"]),
                    "date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "total_score": 100,
                    "duration": random.choice([90, 120, 150])
                }
                for i in range(1, 21)  # 20场考试
            ],
            "grades": [],
            "lesson_plans": [
                {
                    "id": f"lesson_{i:03d}",
                    "title": f"课程计划{i}",
                    "subject": random.choice(["数学", "物理", "化学"]),
                    "grade": "高一",
                    "duration": 45,
                    "objectives": [f"目标{j}" for j in range(1, 4)],
                    "activities": [
                        {"type": "导入", "duration": 5},
                        {"type": "新课", "duration": 30},
                        {"type": "练习", "duration": 8},
                        {"type": "总结", "duration": 2}
                    ]
                }
                for i in range(1, 11)  # 10个课程计划
            ]
        }
        
        # 生成成绩数据
        for student in self.test_data_cache["students"]:
            for exam in self.test_data_cache["exams"]:
                if exam["subject"] in student["subjects"]:
                    score = random.randint(60, 100)
                    self.test_data_cache["grades"].append({
                        "student_id": student["id"],
                        "exam_id": exam["id"],
                        "subject": exam["subject"],
                        "score": score,
                        "date": exam["date"]
                    })
        
        logger.info(f"初始化测试数据: {len(self.test_data_cache['students'])} 学生, "
                   f"{len(self.test_data_cache['exams'])} 考试, "
                   f"{len(self.test_data_cache['grades'])} 成绩记录")
    
    def _calculate_checksum(self, data: Any) -> str:
        """计算数据校验和"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
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
    
    async def test_data_upload(self, account_id: str, data_type: str, data: List[Dict]) -> Dict:
        """测试数据上传"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            
            # 计算原始数据校验和
            original_checksum = self._calculate_checksum(data)
            
            upload_payload = {
                "data_type": data_type,
                "data": data,
                "checksum": original_checksum,
                "timestamp": datetime.now().isoformat()
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/data/upload", 
                                       json=upload_payload, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # 验证服务端返回的校验和
                        server_checksum = result.get('checksum', '')
                        checksum_match = (original_checksum == server_checksum)
                        
                        logger.info(f"数据上传测试成功，类型: {data_type}, 响应时间: {response_time:.2f}s, "
                                   f"校验和匹配: {checksum_match}")
                        
                        return {
                            "success": True,
                            "response_time": response_time,
                            "data_type": data_type,
                            "record_count": len(data),
                            "original_checksum": original_checksum,
                            "server_checksum": server_checksum,
                            "checksum_match": checksum_match,
                            "upload_id": result.get('upload_id', ''),
                            "server_response": result
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"数据上传测试失败，类型: {data_type}, 状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time,
                            "data_type": data_type
                        }
        except Exception as e:
            logger.error(f"数据上传测试异常，类型: {data_type}: {e}")
            return {"success": False, "error": str(e), "data_type": data_type}
    
    async def test_data_download(self, account_id: str, data_type: str, filters: Dict = None) -> Dict:
        """测试数据下载"""
        if account_id not in self.session_tokens:
            return {"success": False, "error": "未找到有效会话"}
        
        try:
            headers = {"Authorization": f"Bearer {self.session_tokens[account_id]}"}
            
            query_params = {
                "data_type": data_type
            }
            
            if filters:
                query_params.update(filters)
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/data/download", 
                                      params=query_params, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # 验证下载数据的完整性
                        downloaded_data = result.get('data', [])
                        server_checksum = result.get('checksum', '')
                        calculated_checksum = self._calculate_checksum(downloaded_data)
                        
                        checksum_match = (server_checksum == calculated_checksum)
                        
                        logger.info(f"数据下载测试成功，类型: {data_type}, 响应时间: {response_time:.2f}s, "
                                   f"记录数: {len(downloaded_data)}, 校验和匹配: {checksum_match}")
                        
                        return {
                            "success": True,
                            "response_time": response_time,
                            "data_type": data_type,
                            "record_count": len(downloaded_data),
                            "server_checksum": server_checksum,
                            "calculated_checksum": calculated_checksum,
                            "checksum_match": checksum_match,
                            "data": downloaded_data,
                            "metadata": result.get('metadata', {})
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"数据下载测试失败，类型: {data_type}, 状态码: {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time,
                            "data_type": data_type
                        }
        except Exception as e:
            logger.error(f"数据下载测试异常，类型: {data_type}: {e}")
            return {"success": False, "error": str(e), "data_type": data_type}
    
    async def test_data_synchronization(self, account_id: str) -> Dict:
        """测试数据同步"""
        logger.info(f"开始测试账号 {account_id} 的数据同步...")
        
        sync_results = []
        
        # 测试各种数据类型的同步
        data_types = [
            ("students", self.test_data_cache["students"][:10]),  # 前10个学生
            ("exams", self.test_data_cache["exams"][:5]),        # 前5场考试
            ("grades", self.test_data_cache["grades"][:50]),     # 前50条成绩
            ("lesson_plans", self.test_data_cache["lesson_plans"][:3])  # 前3个课程计划
        ]
        
        for data_type, data in data_types:
            # 1. 上传数据
            upload_result = await self.test_data_upload(account_id, data_type, data)
            
            if upload_result["success"]:
                # 2. 等待同步完成
                await asyncio.sleep(1)
                
                # 3. 下载数据验证同步
                download_result = await self.test_data_download(account_id, data_type)
                
                if download_result["success"]:
                    # 4. 比较数据一致性
                    uploaded_checksum = upload_result["original_checksum"]
                    downloaded_checksum = download_result["calculated_checksum"]
                    
                    sync_success = (uploaded_checksum == downloaded_checksum)
                    
                    sync_results.append({
                        "data_type": data_type,
                        "upload_success": True,
                        "download_success": True,
                        "sync_success": sync_success,
                        "upload_time": upload_result["response_time"],
                        "download_time": download_result["response_time"],
                        "record_count": len(data),
                        "uploaded_checksum": uploaded_checksum,
                        "downloaded_checksum": downloaded_checksum
                    })
                    
                    logger.info(f"数据类型 {data_type} 同步测试完成，同步成功: {sync_success}")
                else:
                    sync_results.append({
                        "data_type": data_type,
                        "upload_success": True,
                        "download_success": False,
                        "sync_success": False,
                        "error": download_result.get("error", "下载失败")
                    })
            else:
                sync_results.append({
                    "data_type": data_type,
                    "upload_success": False,
                    "download_success": False,
                    "sync_success": False,
                    "error": upload_result.get("error", "上传失败")
                })
        
        # 计算同步成功率
        total_syncs = len(sync_results)
        successful_syncs = sum(1 for result in sync_results if result.get("sync_success", False))
        sync_success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
        
        return {
            "account_id": account_id,
            "total_data_types": total_syncs,
            "successful_syncs": successful_syncs,
            "sync_success_rate": sync_success_rate,
            "sync_details": sync_results
        }
    
    async def test_concurrent_data_access(self, account_ids: List[str]) -> Dict:
        """测试并发数据访问"""
        logger.info(f"开始测试 {len(account_ids)} 个账号的并发数据访问...")
        
        # 创建并发任务
        tasks = []
        for account_id in account_ids:
            # 每个账号同时进行上传和下载操作
            upload_task = self.test_data_upload(
                account_id, 
                "grades", 
                self.test_data_cache["grades"][:20]
            )
            download_task = self.test_data_download(account_id, "students")
            
            tasks.extend([upload_task, download_task])
        
        start_time = time.time()
        
        # 执行并发任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # 分析结果
        successful_operations = 0
        failed_operations = 0
        upload_times = []
        download_times = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_operations += 1
                logger.error(f"并发操作 {i} 异常: {result}")
            elif isinstance(result, dict) and result.get("success", False):
                successful_operations += 1
                response_time = result.get("response_time", 0)
                
                # 区分上传和下载操作
                if "upload_id" in result:
                    upload_times.append(response_time)
                else:
                    download_times.append(response_time)
            else:
                failed_operations += 1
        
        # 计算统计信息
        total_operations = len(results)
        success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
        
        avg_upload_time = sum(upload_times) / len(upload_times) if upload_times else 0
        avg_download_time = sum(download_times) / len(download_times) if download_times else 0
        
        return {
            "concurrent_accounts": len(account_ids),
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": success_rate,
            "total_time": total_time,
            "avg_upload_time": avg_upload_time,
            "avg_download_time": avg_download_time,
            "upload_count": len(upload_times),
            "download_count": len(download_times)
        }
    
    async def test_data_consistency(self, account_id: str) -> Dict:
        """测试数据一致性"""
        logger.info(f"开始测试账号 {account_id} 的数据一致性...")
        
        consistency_results = []
        
        # 测试数据修改后的一致性
        test_data = self.test_data_cache["students"][:5].copy()
        
        # 1. 上传原始数据
        original_upload = await self.test_data_upload(account_id, "students", test_data)
        
        if original_upload["success"]:
            # 2. 修改数据
            modified_data = test_data.copy()
            for student in modified_data:
                student["name"] = f"{student['name']}_修改"
            
            # 3. 上传修改后的数据
            modified_upload = await self.test_data_upload(account_id, "students", modified_data)
            
            if modified_upload["success"]:
                # 4. 下载数据验证一致性
                download_result = await self.test_data_download(account_id, "students")
                
                if download_result["success"]:
                    downloaded_data = download_result["data"]
                    
                    # 5. 验证数据是否为最新修改的版本
                    is_consistent = True
                    for i, student in enumerate(downloaded_data[:5]):
                        expected_name = f"{test_data[i]['name']}_修改"
                        if student.get("name") != expected_name:
                            is_consistent = False
                            break
                    
                    consistency_results.append({
                        "test_type": "数据修改一致性",
                        "success": True,
                        "is_consistent": is_consistent,
                        "original_checksum": original_upload["original_checksum"],
                        "modified_checksum": modified_upload["original_checksum"],
                        "downloaded_checksum": download_result["calculated_checksum"]
                    })
                else:
                    consistency_results.append({
                        "test_type": "数据修改一致性",
                        "success": False,
                        "error": "下载修改后数据失败"
                    })
            else:
                consistency_results.append({
                    "test_type": "数据修改一致性",
                    "success": False,
                    "error": "上传修改后数据失败"
                })
        else:
            consistency_results.append({
                "test_type": "数据修改一致性",
                "success": False,
                "error": "上传原始数据失败"
            })
        
        # 计算一致性测试成功率
        total_tests = len(consistency_results)
        consistent_tests = sum(1 for result in consistency_results 
                             if result.get("success", False) and result.get("is_consistent", False))
        consistency_rate = (consistent_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "account_id": account_id,
            "total_consistency_tests": total_tests,
            "consistent_tests": consistent_tests,
            "consistency_rate": consistency_rate,
            "test_details": consistency_results
        }
    
    async def test_data_cache_performance(self, account_id: str) -> Dict:
        """测试数据缓存性能"""
        logger.info(f"开始测试账号 {account_id} 的数据缓存性能...")
        
        cache_results = []
        
        # 测试相同数据的多次访问
        data_type = "students"
        
        # 第一次访问（冷缓存）
        first_access = await self.test_data_download(account_id, data_type)
        
        if first_access["success"]:
            first_response_time = first_access["response_time"]
            
            # 等待一小段时间
            await asyncio.sleep(0.5)
            
            # 第二次访问（热缓存）
            second_access = await self.test_data_download(account_id, data_type)
            
            if second_access["success"]:
                second_response_time = second_access["response_time"]
                
                # 计算缓存效果
                cache_improvement = ((first_response_time - second_response_time) / first_response_time * 100) if first_response_time > 0 else 0
                
                cache_results.append({
                    "test_type": "缓存性能测试",
                    "success": True,
                    "first_access_time": first_response_time,
                    "second_access_time": second_response_time,
                    "cache_improvement_percent": cache_improvement,
                    "data_type": data_type
                })
            else:
                cache_results.append({
                    "test_type": "缓存性能测试",
                    "success": False,
                    "error": "第二次访问失败"
                })
        else:
            cache_results.append({
                "test_type": "缓存性能测试",
                "success": False,
                "error": "第一次访问失败"
            })
        
        return {
            "account_id": account_id,
            "cache_test_results": cache_results
        }
    
    async def run_full_data_flow_test(self) -> Dict:
        """运行完整的数据流测试套件"""
        logger.info("开始执行完整数据流测试套件...")
        
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
        
        if not authenticated_accounts:
            logger.error("没有成功认证的账号，无法进行数据流测试")
            return test_results
        
        # 1. 数据同步测试
        logger.info("执行数据同步测试...")
        sync_results = {}
        for account_id in authenticated_accounts[:3]:  # 选择前3个账号进行同步测试
            sync_result = await self.test_data_synchronization(account_id)
            sync_results[account_id] = sync_result
        
        test_results["tests"]["data_synchronization"] = sync_results
        
        # 2. 并发数据访问测试
        logger.info("执行并发数据访问测试...")
        concurrent_result = await self.test_concurrent_data_access(authenticated_accounts[:5])
        test_results["tests"]["concurrent_access"] = concurrent_result
        
        # 3. 数据一致性测试
        logger.info("执行数据一致性测试...")
        consistency_results = {}
        for account_id in authenticated_accounts[:2]:  # 选择前2个账号进行一致性测试
            consistency_result = await self.test_data_consistency(account_id)
            consistency_results[account_id] = consistency_result
        
        test_results["tests"]["data_consistency"] = consistency_results
        
        # 4. 缓存性能测试
        logger.info("执行缓存性能测试...")
        cache_results = {}
        for account_id in authenticated_accounts[:2]:  # 选择前2个账号进行缓存测试
            cache_result = await self.test_data_cache_performance(account_id)
            cache_results[account_id] = cache_result
        
        test_results["tests"]["cache_performance"] = cache_results
        
        # 生成测试摘要
        test_results["end_time"] = datetime.now().isoformat()
        
        # 统计同步测试结果
        total_sync_tests = len(sync_results)
        successful_sync_tests = sum(1 for result in sync_results.values() 
                                   if result.get("sync_success_rate", 0) > 80)
        
        # 统计一致性测试结果
        total_consistency_tests = len(consistency_results)
        successful_consistency_tests = sum(1 for result in consistency_results.values() 
                                         if result.get("consistency_rate", 0) > 90)
        
        summary = {
            "total_accounts_tested": len(authenticated_accounts),
            "data_synchronization": {
                "total_tests": total_sync_tests,
                "successful_tests": successful_sync_tests,
                "success_rate": (successful_sync_tests / total_sync_tests * 100) if total_sync_tests > 0 else 0
            },
            "concurrent_access": {
                "success_rate": concurrent_result.get("success_rate", 0),
                "total_operations": concurrent_result.get("total_operations", 0),
                "avg_response_time": (concurrent_result.get("avg_upload_time", 0) + 
                                     concurrent_result.get("avg_download_time", 0)) / 2
            },
            "data_consistency": {
                "total_tests": total_consistency_tests,
                "successful_tests": successful_consistency_tests,
                "success_rate": (successful_consistency_tests / total_consistency_tests * 100) if total_consistency_tests > 0 else 0
            }
        }
        
        test_results["summary"] = summary
        
        # 保存测试结果
        with open("data_flow_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        logger.info("数据流测试套件执行完成")
        logger.info(f"数据同步成功率: {summary['data_synchronization']['success_rate']:.1f}%")
        logger.info(f"并发访问成功率: {summary['concurrent_access']['success_rate']:.1f}%")
        logger.info(f"数据一致性成功率: {summary['data_consistency']['success_rate']:.1f}%")
        
        return test_results

# 主执行函数
async def main():
    """主执行函数"""
    try:
        # 初始化数据流测试器
        tester = DataFlowTester()
        
        # 运行完整数据流测试
        results = await tester.run_full_data_flow_test()
        
        # 输出测试结果摘要
        print("\n" + "="*50)
        print("数据流测试结果摘要")
        print("="*50)
        
        summary = results["summary"]
        print(f"测试账号总数: {summary['total_accounts_tested']}")
        
        print("\n数据同步测试:")
        sync_summary = summary["data_synchronization"]
        print(f"  成功率: {sync_summary['success_rate']:.1f}% ({sync_summary['successful_tests']}/{sync_summary['total_tests']})")
        
        print("\n并发访问测试:")
        concurrent_summary = summary["concurrent_access"]
        print(f"  成功率: {concurrent_summary['success_rate']:.1f}%")
        print(f"  总操作数: {concurrent_summary['total_operations']}")
        print(f"  平均响应时间: {concurrent_summary['avg_response_time']:.2f}s")
        
        print("\n数据一致性测试:")
        consistency_summary = summary["data_consistency"]
        print(f"  成功率: {consistency_summary['success_rate']:.1f}% ({consistency_summary['successful_tests']}/{consistency_summary['total_tests']})")
        
        print("\n详细测试结果已保存到: data_flow_test_results.json")
        print("测试日志已保存到: data_flow_test.log")
        
    except Exception as e:
        logger.error(f"数据流测试执行失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())