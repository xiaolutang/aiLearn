#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import hashlib

# 确保在正确的目录下运行
os.chdir('/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service')
sys.path.append('.')

from database import SessionLocal, User
from auth import verify_password

def test_password_verification():
    """测试密码验证功能"""
    db = SessionLocal()
    try:
        # 获取admin01用户
        user = db.query(User).filter(User.username == 'admin01').first()
        if not user:
            print("未找到用户 admin01")
            return
        
        print(f"用户: {user.username}")
        print(f"存储的密码哈希: {user.password}")
        print(f"哈希长度: {len(user.password)}")
        
        # 测试正确密码
        correct_password = "Admin01!"
        print(f"\n测试正确密码: {correct_password}")
        
        # 手动计算SHA256哈希进行对比
        manual_hash = hashlib.sha256(correct_password.encode()).hexdigest()
        print(f"手动计算的SHA256哈希: {manual_hash}")
        print(f"哈希是否匹配: {user.password == manual_hash}")
        
        # 使用verify_password函数测试
        result = verify_password(correct_password, user.password)
        print(f"verify_password结果: {result}")
        
        # 测试错误密码
        wrong_password = "wrongpassword"
        print(f"\n测试错误密码: {wrong_password}")
        result_wrong = verify_password(wrong_password, user.password)
        print(f"verify_password结果: {result_wrong}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_password_verification()