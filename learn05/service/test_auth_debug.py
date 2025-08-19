#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试认证功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, get_user_by_username

# 直接导入认证函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配"""
    # 检查是否是bcrypt格式的哈希
    if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
        import bcrypt
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    else:
        # 兼容SHA256格式的哈希（用于模拟数据）
        import hashlib
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def authenticate_user(db, username: str, password: str):
    """用户认证"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
import pandas as pd

def test_auth_debug():
    """调试认证功能"""
    print("=== 认证功能调试 ===")
    
    # 获取数据库连接
    db = next(get_db())
    
    # 读取Excel文件获取正确密码
    excel_file = "/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount/user_accounts_20250817_174924.xlsx"
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        print(f"Excel文件包含 {len(df)} 个用户")
        
        # 测试前3个admin用户
        admin_users = df[df['用户名'].str.startswith('admin')].head(3)
        
        for _, row in admin_users.iterrows():
            username = row['用户名']
            password = row['密码']
            
            print(f"\n--- 测试用户: {username} ---")
            print(f"Excel中的密码: {password}")
            
            # 从数据库获取用户
            user = get_user_by_username(db, username)
            if user:
                print(f"数据库中找到用户: {user.username}")
                print(f"数据库中的密码哈希: {user.password[:50]}...")
                
                # 测试密码验证
                verify_result = verify_password(password, user.password)
                print(f"verify_password结果: {verify_result}")
                
                # 测试authenticate_user
                auth_result = authenticate_user(db, username, password)
                print(f"authenticate_user结果: {auth_result is not False}")
                
                if auth_result:
                    print(f"认证成功，用户ID: {auth_result.id}")
                else:
                    print("认证失败")
                    
                    # 手动计算SHA256哈希进行比较
                    import hashlib
                    manual_hash = hashlib.sha256(password.encode()).hexdigest()
                    print(f"手动计算的SHA256: {manual_hash}")
                    print(f"哈希匹配: {manual_hash == user.password}")
            else:
                print(f"数据库中未找到用户: {username}")
    else:
        print(f"Excel文件不存在: {excel_file}")
    
    db.close()

if __name__ == "__main__":
    test_auth_debug()