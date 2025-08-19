#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import hashlib
from database import SessionLocal, User
from sqlalchemy import func

def update_passwords_from_excel():
    """从Excel文件更新数据库中的密码哈希"""
    # 读取Excel文件
    excel_path = '/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount/user_accounts_20250817_174924.xlsx'
    
    try:
        df = pd.read_excel(excel_path)
        print(f"从Excel文件读取了 {len(df)} 条用户记录")
        
        db = SessionLocal()
        updated_count = 0
        
        for index, row in df.iterrows():
            username = row['用户名']
            password = row['密码']
            
            # 查找数据库中的用户
            user = db.query(User).filter(User.username == username).first()
            if user:
                # 使用SHA256哈希密码
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                user.password = password_hash
                updated_count += 1
                
                if updated_count <= 5:  # 只打印前5个更新的用户
                    print(f"更新用户 {username}: {password} -> {password_hash}")
            else:
                print(f"警告: 数据库中未找到用户 {username}")
        
        # 提交更改
        db.commit()
        print(f"\n成功更新了 {updated_count} 个用户的密码哈希")
        
        # 验证更新结果
        print("\n=== 验证更新结果 ===")
        test_users = ['admin01', 'admin02', 'teacher01']
        for username in test_users:
            user = db.query(User).filter(User.username == username).first()
            if user:
                # 从Excel中获取对应密码
                excel_row = df[df['用户名'] == username]
                if not excel_row.empty:
                    excel_password = excel_row.iloc[0]['密码']
                    expected_hash = hashlib.sha256(excel_password.encode()).hexdigest()
                    print(f"{username}: 密码={excel_password}, 哈希匹配={user.password == expected_hash}")
        
        db.close()
        
    except Exception as e:
        print(f"更新密码时出错: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.rollback()
            db.close()

if __name__ == "__main__":
    update_passwords_from_excel()