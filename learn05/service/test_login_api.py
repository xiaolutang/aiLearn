#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试登录API
"""

import requests
import json

def test_login_api():
    """测试登录API"""
    print("=== 测试登录API ===")
    
    url = "http://127.0.0.1:8000/api/v1/auth/login"
    
    # 测试数据
    test_users = [
        {"username": "admin01", "password": "Admin01!"},
        {"username": "admin02", "password": "Admin02!"},
        {"username": "admin03", "password": "Admin03!"}
    ]
    
    for user_data in test_users:
        print(f"\n--- 测试用户: {user_data['username']} ---")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url,
                json=user_data,
                headers=headers,
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"响应文本: {response.text}")
                
            if response.status_code == 200:
                print("✅ 登录成功")
            else:
                print("❌ 登录失败")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_login_api()