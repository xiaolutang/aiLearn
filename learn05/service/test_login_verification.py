#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录验证和数据一致性测试脚本
测试数据库中所有账号的登录功能，并验证数据库与导出Excel文件的一致性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import pandas as pd
from database import SessionLocal, User, Student, Grade, Subject, Class
from sqlalchemy.orm import Session
import hashlib
from datetime import datetime
import json

# API基础URL
BASE_URL = "http://localhost:8000"

def hash_password(password: str) -> str:
    """密码哈希函数"""
    return hashlib.sha256(password.encode()).hexdigest()

def test_user_login(username: str, password: str):
    """测试用户登录"""
    try:
        # 使用JSON格式的请求体
        login_data = {
            "username": username,
            "password": password,
            "remember_me": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            # 检查响应格式
            if 'data' in result and 'access_token' in result['data']:
                success = True
            else:
                success = False
        elif response.status_code == 422:
            # 验证错误，打印详细信息
            print(f"登录验证错误 - 用户: {username}, 详情: {response.json()}")
            success = False
        elif response.status_code == 401:
            # 认证失败
            print(f"登录认证失败 - 用户: {username}, 详情: {response.json()}")
            success = False
        else:
            success = False
            
        return {
            "username": username,
            "status_code": response.status_code,
            "success": success,
            "response": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {
            "username": username,
            "status_code": None,
            "success": False,
            "error": str(e)
        }

def get_database_users():
    """获取数据库中的所有用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [{
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email,
            "phone_number": user.phone_number,
            "is_active": user.is_active
        } for user in users]
    finally:
        db.close()

def get_database_stats():
    """获取数据库统计信息"""
    db = SessionLocal()
    try:
        stats = {
            "users": db.query(User).count(),
            "students": db.query(Student).count(),
            "classes": db.query(Class).count(),
            "subjects": db.query(Subject).count(),
            "grades": db.query(Grade).count()
        }
        return stats
    finally:
        db.close()

def load_excel_data(excel_file):
    """加载Excel文件数据"""
    try:
        # 读取所有工作表
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        return excel_data
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return None

def compare_data_consistency(db_users, excel_accounts):
    """比较数据库用户与Excel账号数据的一致性"""
    inconsistencies = []
    
    # 创建用户名到数据库用户的映射
    db_user_map = {user["username"]: user for user in db_users}
    
    # 检查Excel中的每个账号是否在数据库中存在
    for _, account in excel_accounts.iterrows():
        username = account["用户名"]
        role = account["角色"]
        email = account["邮箱"]
        
        if username not in db_user_map:
            inconsistencies.append({
                "type": "missing_in_db",
                "username": username,
                "issue": "Excel中的账号在数据库中不存在"
            })
        else:
            db_user = db_user_map[username]
            # 检查角色是否一致
            if db_user["role"] != role:
                inconsistencies.append({
                    "type": "role_mismatch",
                    "username": username,
                    "issue": f"角色不一致: DB={db_user['role']}, Excel={role}"
                })
            # 检查邮箱是否一致
            if db_user["email"] != email:
                inconsistencies.append({
                    "type": "email_mismatch",
                    "username": username,
                    "issue": f"邮箱不一致: DB={db_user['email']}, Excel={email}"
                })
    
    # 检查数据库中是否有Excel中没有的用户
    excel_usernames = set(excel_accounts["用户名"].tolist())
    for user in db_users:
        if user["username"] not in excel_usernames:
            inconsistencies.append({
                "type": "missing_in_excel",
                "username": user["username"],
                "issue": "数据库中的用户在Excel中不存在"
            })
    
    return inconsistencies

def main():
    """主函数"""
    print("智能教学助手 - 登录验证和数据一致性测试")
    print("=" * 60)
    
    # 1. 获取数据库统计信息
    print("\n1. 数据库统计信息:")
    db_stats = get_database_stats()
    for key, value in db_stats.items():
        print(f"   {key}: {value}")
    
    # 2. 获取数据库用户数据
    print("\n2. 获取数据库用户数据...")
    db_users = get_database_users()
    print(f"   数据库中共有 {len(db_users)} 个用户")
    
    # 3. 加载Excel账号数据
    excel_file = "/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount/user_accounts_20250817_174924.xlsx"
    print(f"\n3. 加载Excel账号数据: {excel_file}")
    
    if not os.path.exists(excel_file):
        print(f"   错误: Excel文件不存在: {excel_file}")
        return
    
    excel_accounts = pd.read_excel(excel_file)
    print(f"   Excel中共有 {len(excel_accounts)} 个账号")
    
    # 4. 数据一致性检查
    print("\n4. 数据一致性检查...")
    inconsistencies = compare_data_consistency(db_users, excel_accounts)
    
    if inconsistencies:
        print(f"   发现 {len(inconsistencies)} 个数据不一致问题:")
        for issue in inconsistencies:
            print(f"   - {issue['username']}: {issue['issue']}")
    else:
        print("   ✓ 数据库与Excel数据完全一致")
    
    # 5. 登录测试
    print("\n5. 开始登录测试...")
    login_results = []
    success_count = 0
    fail_count = 0
    
    # 测试每个账号的登录
    for _, account in excel_accounts.iterrows():
        username = account["用户名"]
        password = account["密码"]
        
        result = test_user_login(username, password)
        login_results.append(result)
        
        if result["success"]:
            success_count += 1
            print(f"   ✓ {username} 登录成功")
        else:
            fail_count += 1
            print(f"   ✗ {username} 登录失败: {result.get('error', result.get('response', '未知错误'))}")
    
    # 6. 生成测试报告
    print("\n6. 生成测试报告...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 登录测试结果
    login_df = pd.DataFrame(login_results)
    login_report_file = f"/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount/login_test_results_{timestamp}.xlsx"
    login_df.to_excel(login_report_file, index=False)
    
    # 数据一致性报告
    if inconsistencies:
        inconsistency_df = pd.DataFrame(inconsistencies)
        inconsistency_report_file = f"/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount/data_consistency_issues_{timestamp}.xlsx"
        inconsistency_df.to_excel(inconsistency_report_file, index=False)
    
    # 文本报告
    report_content = f"""智能教学助手 - 登录验证和数据一致性测试报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 数据库统计信息 ===
用户总数: {db_stats['users']}
学生总数: {db_stats['students']}
班级总数: {db_stats['classes']}
科目总数: {db_stats['subjects']}
成绩记录总数: {db_stats['grades']}

=== 数据一致性检查 ===
数据库用户数: {len(db_users)}
Excel账号数: {len(excel_accounts)}
数据不一致问题: {len(inconsistencies)} 个

=== 登录测试结果 ===
总测试账号数: {len(login_results)}
登录成功: {success_count} 个
登录失败: {fail_count} 个
成功率: {(success_count/len(login_results)*100):.2f}%

=== 详细结果 ===
登录测试详细结果已保存到: {login_report_file}
"""
    
    if inconsistencies:
        report_content += f"数据一致性问题详情已保存到: {inconsistency_report_file}\n"
    
    report_file = f"/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service/tests/testAccount/test_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n=== 测试完成 ===")
    print(f"登录成功率: {(success_count/len(login_results)*100):.2f}% ({success_count}/{len(login_results)})")
    print(f"数据一致性: {'✓ 完全一致' if not inconsistencies else f'✗ 发现{len(inconsistencies)}个问题'}")
    print(f"\n详细报告已保存到:")
    print(f"- 测试报告: {report_file}")
    print(f"- 登录结果: {login_report_file}")
    if inconsistencies:
        print(f"- 一致性问题: {inconsistency_report_file}")

if __name__ == "__main__":
    main()