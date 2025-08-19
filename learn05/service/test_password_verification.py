#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('.')

# 确保在正确的目录下
os.chdir('/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service')

from auth import verify_password
from database import SessionLocal, User

def test_password_verification():
    """测试密码验证"""
    db = SessionLocal()
    try:
        # 获取第一个用户
        user = db.query(User).filter(User.username == 'admin01').first()
        if user:
            print(f"用户: {user.username}")
            print(f"数据库密码哈希: {user.password}")
            
            # 测试正确密码
            correct_password = "Admin01!"
            is_valid = verify_password(correct_password, user.password)
            print(f"验证密码 '{correct_password}': {is_valid}")
            
            # 测试错误密码
            wrong_password = "wrongpassword"
            is_valid_wrong = verify_password(wrong_password, user.password)
            print(f"验证错误密码 '{wrong_password}': {is_valid_wrong}")
            
        else:
            print("未找到用户 admin01")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_password_verification()