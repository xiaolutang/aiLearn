#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json

def create_test_accounts_json():
    """从Excel文件创建test_accounts.json"""
    try:
        # 读取Excel文件
        df = pd.read_excel('tests/test_accounts.xlsx')
        
        # 转换为JSON格式
        accounts = []
        for _, row in df.iterrows():
            account = {
                'username': row['用户名'],
                'password': row['密码'],
                'role': row['角色'],
                'email': row['邮箱'],
                'status': row['状态'],
                'description': row['描述']
            }
            accounts.append(account)
        
        # 保存为JSON文件
        with open('tests/test_accounts.json', 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
        
        print(f"成功创建test_accounts.json，包含{len(accounts)}个测试账号")
        
    except Exception as e:
        print(f"创建失败: {e}")

if __name__ == "__main__":
    create_test_accounts_json()