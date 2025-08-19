#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import bcrypt
from database import SessionLocal, User

def test_hash_methods():
    """测试不同的哈希方法来找出正确的密码验证方式"""
    db = SessionLocal()
    try:
        # 获取admin01用户
        user = db.query(User).filter(User.username == 'admin01').first()
        if not user:
            print("未找到用户 admin01")
            return
        
        stored_hash = user.password
        password = "Admin01!"
        
        print(f"用户: {user.username}")
        print(f"存储的哈希: {stored_hash}")
        print(f"哈希长度: {len(stored_hash)}")
        print(f"测试密码: {password}")
        print("\n=== 测试不同哈希方法 ===")
        
        # 1. 纯SHA256
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"1. SHA256: {sha256_hash}")
        print(f"   匹配: {stored_hash == sha256_hash}")
        
        # 2. SHA256 + 用户名作为盐
        sha256_with_username = hashlib.sha256((password + user.username).encode()).hexdigest()
        print(f"2. SHA256 + username: {sha256_with_username}")
        print(f"   匹配: {stored_hash == sha256_with_username}")
        
        # 3. SHA256 + 固定盐
        common_salts = ['salt', 'secret', 'key', 'admin', '']
        for salt in common_salts:
            salted_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            print(f"3. SHA256 + '{salt}': {salted_hash}")
            print(f"   匹配: {stored_hash == salted_hash}")
            
            # 也试试盐在前面
            salted_hash2 = hashlib.sha256((salt + password).encode()).hexdigest()
            print(f"4. '{salt}' + SHA256: {salted_hash2}")
            print(f"   匹配: {stored_hash == salted_hash2}")
        
        # 5. MD5
        md5_hash = hashlib.md5(password.encode()).hexdigest()
        print(f"5. MD5: {md5_hash}")
        print(f"   匹配: {stored_hash == md5_hash}")
        
        # 6. 尝试其他用户看看是否有规律
        print("\n=== 检查其他用户 ===")
        other_users = db.query(User).filter(User.username.in_(['admin02', 'teacher01', 'student01'])).all()
        for other_user in other_users:
            print(f"用户: {other_user.username}, 哈希: {other_user.password}")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_hash_methods()