#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import pandas as pd
from database import SessionLocal, User

def check_password_hash():
    """检查密码哈希匹配问题"""
    db = SessionLocal()
    try:
        # 读取Excel文件
        df = pd.read_excel('tests/testAccount/admin_users_20250817_184915.xlsx')
        print("Excel中的admin用户:")
        print(df[['用户名', '密码']].head(5))
        
        # 获取数据库中的admin01用户
        user = db.query(User).filter(User.username == 'admin01').first()
        if not user:
            print("数据库中未找到admin01用户")
            return
            
        db_hash = user.password
        print(f"\n数据库中admin01的密码哈希: {db_hash}")
        
        # 测试Excel中所有密码
        print("\n测试Excel中的密码:")
        for _, row in df.iterrows():
            username = row['用户名']
            password = row['密码']
            calculated_hash = hashlib.sha256(password.encode()).hexdigest()
            
            print(f"{username}: {password} -> {calculated_hash}")
            if calculated_hash == db_hash:
                print(f"*** 找到匹配的密码: {password} ***")
                return password
        
        print("\n未找到匹配的密码")
        
        # 尝试一些常见的密码变体
        print("\n测试常见密码变体:")
        test_passwords = [
            'admin01',
            'Admin01',
            'admin01!',
            'Admin01!',
            'password',
            'admin123',
            '123456'
        ]
        
        for password in test_passwords:
            calculated_hash = hashlib.sha256(password.encode()).hexdigest()
            print(f"{password} -> {calculated_hash}")
            if calculated_hash == db_hash:
                print(f"*** 找到匹配的密码: {password} ***")
                return password
                
        print("\n所有测试密码都不匹配")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_password_hash()