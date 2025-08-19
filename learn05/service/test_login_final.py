#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import time
from datetime import datetime
import json

def test_login_functionality():
    """测试登录功能"""
    # API端点
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    # 读取用户账号信息
    excel_path = '/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount/user_accounts_20250817_174924.xlsx'
    
    try:
        df = pd.read_excel(excel_path)
        print(f"读取了 {len(df)} 个用户账号")
        
        # 测试前10个用户
        test_users = df.head(10)
        
        success_count = 0
        fail_count = 0
        results = []
        
        print("\n开始登录测试...")
        print("=" * 50)
        
        for index, row in test_users.iterrows():
            username = row['用户名']
            password = row['密码']
            role = row['角色']
            
            # 准备登录数据
            login_data = {
                "username": username,
                "password": password
            }
            
            try:
                # 发送登录请求
                response = requests.post(
                    login_url,
                    json=login_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    if "access_token" in result_data:
                        success_count += 1
                        status = "成功"
                        print(f"✓ {username} ({role}) - 登录成功")
                    else:
                        fail_count += 1
                        status = "失败 - 无token"
                        print(f"✗ {username} ({role}) - 登录失败: 响应中无access_token")
                else:
                    fail_count += 1
                    status = f"失败 - HTTP {response.status_code}"
                    print(f"✗ {username} ({role}) - 登录失败: HTTP {response.status_code}")
                    if response.status_code == 422:
                        print(f"  详细错误: {response.text}")
                    elif response.status_code == 401:
                        print(f"  认证失败: {response.text}")
                
                results.append({
                    "用户名": username,
                    "密码": password,
                    "角色": role,
                    "状态": status,
                    "HTTP状态码": response.status_code
                })
                
            except requests.exceptions.RequestException as e:
                fail_count += 1
                status = f"网络错误: {str(e)}"
                print(f"✗ {username} ({role}) - 网络错误: {e}")
                results.append({
                    "用户名": username,
                    "密码": password,
                    "角色": role,
                    "状态": status,
                    "HTTP状态码": "N/A"
                })
            
            # 避免请求过快
            time.sleep(0.1)
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("测试结果汇总:")
        print(f"总测试用户数: {len(test_users)}")
        print(f"登录成功: {success_count}")
        print(f"登录失败: {fail_count}")
        print(f"成功率: {success_count/len(test_users)*100:.1f}%")
        
        # 保存详细结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_df = pd.DataFrame(results)
        output_file = f"login_test_results_{timestamp}.xlsx"
        results_df.to_excel(output_file, index=False)
        print(f"\n详细结果已保存到: {output_file}")
        
        # 如果有失败的，显示失败原因统计
        if fail_count > 0:
            print("\n失败原因统计:")
            fail_results = results_df[~results_df['状态'].str.contains('成功')]
            status_counts = fail_results['状态'].value_counts()
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_functionality()