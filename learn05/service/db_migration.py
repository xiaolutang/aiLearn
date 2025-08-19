#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
用于创建架构设计文档中提到的扩展表结构
"""

import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DB_FILE = "student_database.db"


def create_extension_tables():
    """创建架构设计文档中提到的扩展表"""
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        print(f"[INFO] 连接到数据库 {DB_FILE} 成功")
        
        # 检查现有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        # 创建用户表（扩展现有teacher和student表的认证功能）
        if 'users' not in existing_tables:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,  -- 加密存储
                    role TEXT NOT NULL CHECK(role IN ('teacher', 'student', 'parent', 'admin')),
                    related_id INTEGER,      -- 关联到teacher_id或student_id
                    email TEXT UNIQUE,
                    phone_number TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("[INFO] 创建用户表 users 成功")
        else:
            print("[INFO] 用户表 users 已存在")
        
        # 创建教材表
        if 'textbooks' not in existing_tables:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS textbooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT,
                    subject TEXT NOT NULL,
                    grade INTEGER NOT NULL,
                    publisher TEXT,
                    chapters TEXT,  -- JSON格式存储章节信息
                    knowledge_points TEXT,  -- JSON格式存储知识点信息
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("[INFO] 创建教材表 textbooks 成功")
        else:
            print("[INFO] 教材表 textbooks 已存在")
        
        # 创建学情表
        if 'learning_status' not in existing_tables:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    knowledge_point TEXT NOT NULL,
                    mastery_level INTEGER CHECK(mastery_level BETWEEN 1 AND 10),
                    weakness_analysis TEXT,
                    improvement_suggestions TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
            ''')
            print("[INFO] 创建学情表 learning_status 成功")
        else:
            print("[INFO] 学情表 learning_status 已存在")
        
        # 创建教学资源表
        if 'teaching_resources' not in existing_tables:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teaching_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('教案', '课件', '练习题', '视频', '其他')),
                    content TEXT,  -- 或文件路径
                    file_path TEXT,
                    author_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    grade INTEGER NOT NULL,
                    tags TEXT,  -- JSON格式存储标签
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (author_id) REFERENCES teachers(teacher_id)
                )
            ''')
            print("[INFO] 创建教学资源表 teaching_resources 成功")
        else:
            print("[INFO] 教学资源表 teaching_resources 已存在")
        
        # 创建辅导方案表
        if 'tutoring_plans' not in existing_tables:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tutoring_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    plan_content TEXT NOT NULL,
                    resources TEXT,  -- JSON格式存储推荐资源列表
                    progress INTEGER CHECK(progress BETWEEN 0 AND 100) DEFAULT 0,
                    effect_evaluation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
            ''')
            print("[INFO] 创建辅导方案表 tutoring_plans 成功")
        else:
            print("[INFO] 辅导方案表 tutoring_plans 已存在")
        
        # 创建消息通知表
        if 'notifications' not in existing_tables:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            print("[INFO] 创建消息通知表 notifications 成功")
        else:
            print("[INFO] 消息通知表 notifications 已存在")
        
        # 创建索引以优化查询性能
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_status_student_id ON learning_status(student_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tutoring_plans_student_id ON tutoring_plans(student_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);")
        
        print("[INFO] 创建索引成功")
        
        # 提交事务
        conn.commit()
        print("[INFO] 数据库迁移完成")
        
    except sqlite3.Error as e:
        print(f"[ERROR] 数据库操作错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()
            print(f"[INFO] 已关闭数据库连接")


def insert_sample_data():
    """插入示例数据，包括一个管理员用户"""
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 检查是否已有管理员用户
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin';")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # 插入管理员用户（密码：admin123，已使用bcrypt加密）
            # 注意：在实际生产环境中，应该使用安全的方式生成和存储密码
            cursor.execute(
                "INSERT INTO users (username, password, role, email, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                ('admin', 
                 '$2b$12$8QZp1w0gA2Z8KvJ5c5zq..6U3M4x8eU9X6Qz4XvZ4y3z5b5d5f5g', 
                 'admin', 
                 'admin@example.com', 
                 datetime.now().isoformat(), 
                 datetime.now().isoformat())
            )
            print("[INFO] 已插入管理员用户")
        else:
            print("[INFO] 管理员用户已存在")
        
        # 提交事务
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"[ERROR] 插入示例数据错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()


def main():
    """主函数"""
    print("[INFO] 开始数据库迁移...")
    
    # 检查数据库文件是否存在
    if not os.path.exists(DB_FILE):
        print(f"[ERROR] 数据库文件 {DB_FILE} 不存在")
        print("[INFO] 请先运行数据生成脚本创建数据库")
        return
    
    # 创建扩展表
    create_extension_tables()
    
    # 插入示例数据
    insert_sample_data()
    
    print("[INFO] 数据库迁移脚本执行完毕")


if __name__ == "__main__":
    main()