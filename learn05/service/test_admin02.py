#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
from database import SessionLocal, User

def test_admin02():
    """测试admin02的密码验证"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == 'admin02').first()
        password = 'Admin02!'
        
        print(f"用户: {user.username}")
        print(f"存储哈希: {user.password}")
        print(f"测试密码: {password}")
        
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"SHA256哈希: {sha256_hash}")
        print(f"匹配: {user.password == sha256_hash}")
        
        # 尝试其他可能的编码方式
        print("\n=== 尝试其他编码方式 ===")
        
        # UTF-8编码
        utf8_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        print(f"UTF-8编码: {utf8_hash}")
        print(f"匹配: {user.password == utf8_hash}")
        
        # 小写
        lower_hash = hashlib.sha256(password.lower().encode()).hexdigest()
        print(f"小写: {lower_hash}")
        print(f"匹配: {user.password == lower_hash}")
        
        # 大写
        upper_hash = hashlib.sha256(password.upper().encode()).hexdigest()
        print(f"大写: {upper_hash}")
        print(f"匹配: {user.password == upper_hash}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_admin02()