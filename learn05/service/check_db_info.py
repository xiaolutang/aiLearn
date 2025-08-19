#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import SessionLocal, User
import os
import sqlite3
from datetime import datetime

def check_database_info():
    """检查数据库信息"""
    # 检查数据库文件信息
    db_path = './student_database.db'
    if os.path.exists(db_path):
        stat = os.stat(db_path)
        print(f"数据库文件: {db_path}")
        print(f"文件大小: {stat.st_size} bytes")
        print(f"创建时间: {datetime.fromtimestamp(stat.st_ctime)}")
        print(f"修改时间: {datetime.fromtimestamp(stat.st_mtime)}")
    
    # 检查数据库中的用户信息
    db = SessionLocal()
    try:
        users = db.query(User).limit(5).all()
        print(f"\n数据库中前5个用户:")
        for user in users:
            print(f"ID: {user.id}")
            print(f"用户名: {user.username}")
            print(f"密码哈希: {user.password}")
            print(f"角色: {user.role}")
            print(f"创建时间: {user.created_at}")
            print("---")
            
        # 统计用户数量
        total_users = db.query(User).count()
        print(f"\n总用户数: {total_users}")
        
        # 按角色统计
        roles = db.query(User.role, db.func.count(User.id)).group_by(User.role).all()
        print("\n按角色统计:")
        for role, count in roles:
            print(f"{role}: {count}")
            
    except Exception as e:
        print(f"查询数据库时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_database_info()