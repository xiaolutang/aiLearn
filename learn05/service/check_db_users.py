#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的用户数据
"""

import sqlite3
import hashlib
import pandas as pd

def check_database_users():
    """检查数据库中的用户数据"""
    print("=== 检查数据库中的用户数据 ===")
    
    # 连接数据库
    db_path = "/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/intelligent_tutoring.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询前10个用户
        cursor.execute("""
            SELECT id, username, password_hash, email, full_name, role, is_active 
            FROM users 
            WHERE username LIKE 'admin%' 
            ORDER BY username 
            LIMIT 10
        """)
        
        users = cursor.fetchall()
        
        print(f"\n找到 {len(users)} 个admin用户:")
        
        for user in users:
            user_id, username, password_hash, email, full_name, role, is_active = user
            print(f"\n--- 用户: {username} ---")
            print(f"ID: {user_id}")
            print(f"邮箱: {email}")
            print(f"姓名: {full_name}")
            print(f"角色: {role}")
            print(f"激活状态: {is_active}")
            print(f"密码哈希: {password_hash[:50]}...")
            
            # 计算预期的密码哈希
            expected_password = f"{username.capitalize()}!"
            expected_hash = hashlib.sha256(expected_password.encode()).hexdigest()
            
            print(f"预期密码: {expected_password}")
            print(f"预期哈希: {expected_hash[:50]}...")
            print(f"哈希匹配: {'✅' if password_hash == expected_hash else '❌'}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")

def check_excel_data():
    """检查Excel文件中的数据"""
    print("\n=== 检查Excel文件中的数据 ===")
    
    excel_path = "/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount/user_accounts_20250817_174924.xlsx"
    
    try:
        df = pd.read_excel(excel_path)
        
        # 查看前5个admin用户
        admin_users = df[df['username'].str.startswith('admin')].head(5)
        
        print(f"\nExcel中的前5个admin用户:")
        for _, user in admin_users.iterrows():
            print(f"\n--- 用户: {user['username']} ---")
            print(f"密码: {user['password']}")
            print(f"邮箱: {user['email']}")
            print(f"姓名: {user['full_name']}")
            print(f"角色: {user['role']}")
            
            # 计算密码哈希
            password_hash = hashlib.sha256(user['password'].encode()).hexdigest()
            print(f"密码哈希: {password_hash[:50]}...")
            
    except Exception as e:
        print(f"❌ Excel文件读取失败: {e}")

if __name__ == "__main__":
    check_database_users()
    check_excel_data()