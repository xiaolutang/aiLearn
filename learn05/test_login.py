#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手登录流程测试脚本

功能：
1. 读取Excel文件中的测试账号数据
2. 对每个账号进行登录测试
3. 生成测试结果报告
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('login_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LoginTester:
    """登录测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def load_test_accounts(self, excel_file: str) -> List[Dict[str, Any]]:
        """从Excel文件加载测试账号"""
        try:
            df = pd.read_excel(excel_file)
            accounts = df.to_dict('records')
            logger.info(f"从 {excel_file} 加载了 {len(accounts)} 个测试账号")
            return accounts
        except Exception as e:
            logger.error(f"加载Excel文件失败: {e}")
            return []
    
    def test_login(self, username: str, password: str, user_type: str = "student") -> Dict[str, Any]:
        """测试单个账号登录"""
        start_time = time.time()
        result = {
            'username': username,
            'user_type': user_type,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'response_time': 0,
            'status_code': None,
            'error_message': None,
            'token': None
        }
        
        try:
            # 准备登录数据
            login_data = {
                "username": username,
                "password": password
            }
            
            # 发送登录请求
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            result['status_code'] = response.status_code
            result['response_time'] = round(time.time() - start_time, 3)
            
            if response.status_code == 200:
                response_data = response.json()
                result['success'] = True
                result['token'] = response_data.get('access_token', '')
                logger.info(f"✅ {username} 登录成功 ({result['response_time']}s)")
            else:
                result['error_message'] = response.text
                logger.warning(f"❌ {username} 登录失败: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            result['error_message'] = "请求超时"
            result['response_time'] = round(time.time() - start_time, 3)
            logger.error(f"❌ {username} 登录超时")
            
        except requests.exceptions.ConnectionError:
            result['error_message'] = "连接错误"
            result['response_time'] = round(time.time() - start_time, 3)
            logger.error(f"❌ {username} 连接失败")
            
        except Exception as e:
            result['error_message'] = str(e)
            result['response_time'] = round(time.time() - start_time, 3)
            logger.error(f"❌ {username} 登录异常: {e}")
        
        return result
    
    def test_user_info(self, token: str, username: str) -> Dict[str, Any]:
        """测试获取用户信息"""
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"✅ {username} 用户信息获取成功")
                return {'success': True, 'user_info': user_info}
            else:
                logger.warning(f"❌ {username} 用户信息获取失败: {response.status_code}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"❌ {username} 用户信息获取异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_batch_test(self, excel_files: List[str]) -> Dict[str, Any]:
        """批量测试多个Excel文件中的账号"""
        all_results = []
        summary = {
            'total_accounts': 0,
            'successful_logins': 0,
            'failed_logins': 0,
            'success_rate': 0,
            'avg_response_time': 0,
            'test_start_time': datetime.now().isoformat(),
            'test_end_time': None
        }
        
        logger.info("开始批量登录测试...")
        
        for excel_file in excel_files:
            if not Path(excel_file).exists():
                logger.warning(f"文件不存在: {excel_file}")
                continue
                
            accounts = self.load_test_accounts(excel_file)
            
            for account in accounts:
                # 从Excel列名获取用户名和密码
                username = account.get('username') or account.get('用户名') or account.get('账号')
                password = account.get('password') or account.get('密码') or account.get('Password')
                user_type = account.get('user_type') or account.get('用户类型') or account.get('角色')
                
                if not username or not password:
                    logger.warning(f"跳过无效账号: {account}")
                    continue
                
                # 执行登录测试
                result = self.test_login(username, password, user_type)
                
                # 如果登录成功，测试获取用户信息
                if result['success'] and result['token']:
                    user_info_result = self.test_user_info(result['token'], username)
                    result['user_info_test'] = user_info_result
                
                all_results.append(result)
                
                # 添加延迟避免请求过快
                time.sleep(0.5)
        
        # 计算统计信息
        summary['total_accounts'] = len(all_results)
        summary['successful_logins'] = sum(1 for r in all_results if r['success'])
        summary['failed_logins'] = summary['total_accounts'] - summary['successful_logins']
        summary['success_rate'] = round(
            (summary['successful_logins'] / summary['total_accounts'] * 100) if summary['total_accounts'] > 0 else 0, 2
        )
        summary['avg_response_time'] = round(
            sum(r['response_time'] for r in all_results) / len(all_results) if all_results else 0, 3
        )
        summary['test_end_time'] = datetime.now().isoformat()
        
        return {
            'summary': summary,
            'detailed_results': all_results
        }
    
    def generate_report(self, test_results: Dict[str, Any], output_file: str = "login_test_report.json"):
        """生成测试报告"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试报告已生成: {output_file}")
            
            # 打印摘要
            summary = test_results['summary']
            print("\n" + "="*50)
            print("登录测试结果摘要")
            print("="*50)
            print(f"总测试账号数: {summary['total_accounts']}")
            print(f"成功登录数: {summary['successful_logins']}")
            print(f"失败登录数: {summary['failed_logins']}")
            print(f"成功率: {summary['success_rate']}%")
            print(f"平均响应时间: {summary['avg_response_time']}秒")
            print(f"测试开始时间: {summary['test_start_time']}")
            print(f"测试结束时间: {summary['test_end_time']}")
            print("="*50)
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")

def main():
    """主函数"""
    # 测试账号Excel文件列表
    excel_files = [
        "testAccount/admin_users.xlsx",
        "testAccount/teacher_users.xlsx", 
        "testAccount/student_users.xlsx",
        "testAccount/parent_users.xlsx"
    ]
    
    # 创建测试器实例
    tester = LoginTester()
    
    # 首先测试服务器连接
    try:
        response = requests.get(f"{tester.base_url}/docs", timeout=5)
        if response.status_code == 200:
            logger.info("✅ 后端服务连接正常")
        else:
            logger.warning(f"⚠️ 后端服务响应异常: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ 无法连接到后端服务: {e}")
        return
    
    # 执行批量测试
    test_results = tester.run_batch_test(excel_files)
    
    # 生成报告
    tester.generate_report(test_results)
    
    # 生成简化的Markdown报告
    generate_markdown_report(test_results)

def generate_markdown_report(test_results: Dict[str, Any]):
    """生成Markdown格式的测试报告"""
    summary = test_results['summary']
    detailed_results = test_results['detailed_results']
    
    markdown_content = f"""# 智能教学助手登录测试报告

## 测试概览

- **测试时间**: {summary['test_start_time']} ~ {summary['test_end_time']}
- **总测试账号数**: {summary['total_accounts']}
- **成功登录数**: {summary['successful_logins']}
- **失败登录数**: {summary['failed_logins']}
- **成功率**: {summary['success_rate']}%
- **平均响应时间**: {summary['avg_response_time']}秒

## 详细测试结果

| 用户名 | 用户类型 | 登录状态 | 响应时间(s) | 状态码 | 错误信息 |
|--------|----------|----------|-------------|--------|----------|
"""
    
    for result in detailed_results:
        status = "✅ 成功" if result['success'] else "❌ 失败"
        error_msg = result.get('error_message', '') or ''
        markdown_content += f"| {result['username']} | {result.get('user_type', 'N/A')} | {status} | {result['response_time']} | {result.get('status_code', 'N/A')} | {error_msg} |\n"
    
    markdown_content += f"""

## 测试结论

{'✅ 登录功能正常' if summary['success_rate'] >= 90 else '⚠️ 登录功能存在问题，需要进一步检查'}

## 建议

1. 检查失败账号的具体原因
2. 优化响应时间较长的接口
3. 完善错误处理机制
"""
    
    try:
        with open('login_test_report.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info("Markdown测试报告已生成: login_test_report.md")
    except Exception as e:
        logger.error(f"生成Markdown报告失败: {e}")

if __name__ == "__main__":
    main()