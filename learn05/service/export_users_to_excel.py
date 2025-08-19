#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出用户数据到Excel文件
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

def export_users_to_excel():
    """
    从数据库导出用户数据到Excel文件
    """
    # 数据库文件路径
    db_path = 'student_database.db'
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        
        # 查询所有表的数据
        print("正在导出数据...")
        
        # 1. 导出学生数据
        students_query = "SELECT * FROM students"
        students_df = pd.read_sql_query(students_query, conn)
        print(f"学生数据: {len(students_df)} 条记录")
        
        # 2. 导出成绩数据
        grades_query = "SELECT * FROM grades"
        grades_df = pd.read_sql_query(grades_query, conn)
        print(f"成绩数据: {len(grades_df)} 条记录")
        
        # 3. 导出科目数据
        subjects_query = "SELECT * FROM subjects"
        subjects_df = pd.read_sql_query(subjects_query, conn)
        print(f"科目数据: {len(subjects_df)} 条记录")
        
        # 4. 查询用户表（如果存在）
        try:
            users_query = "SELECT * FROM users"
            users_df = pd.read_sql_query(users_query, conn)
            print(f"用户数据: {len(users_df)} 条记录")
        except Exception as e:
            print(f"用户表不存在或查询失败: {e}")
            users_df = pd.DataFrame()
        
        # 5. 创建详细的学生成绩报告（关联查询）
        detailed_query = """
        SELECT 
            s.student_id,
            s.student_name,
            s.student_number,
            s.class_id,
            s.gender,
            s.date_of_birth,
            sub.subject_name,
            g.score,
            g.exam_date,
            g.exam_type
        FROM students s
        LEFT JOIN grades g ON s.student_id = g.student_id
        LEFT JOIN subjects sub ON g.subject_id = sub.subject_id
        ORDER BY s.student_id, g.exam_date
        """
        detailed_df = pd.read_sql_query(detailed_query, conn)
        print(f"详细成绩报告: {len(detailed_df)} 条记录")
        
        # 关闭数据库连接
        conn.close()
        
        # 生成Excel文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"用户数据导出_{timestamp}.xlsx"
        
        # 创建Excel写入器
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # 写入各个工作表
            students_df.to_excel(writer, sheet_name='学生信息', index=False)
            grades_df.to_excel(writer, sheet_name='成绩记录', index=False)
            subjects_df.to_excel(writer, sheet_name='科目信息', index=False)
            detailed_df.to_excel(writer, sheet_name='详细成绩报告', index=False)
            
            # 如果用户表有数据，也导出
            if not users_df.empty:
                users_df.to_excel(writer, sheet_name='用户账户', index=False)
        
        print(f"\n数据导出完成！")
        print(f"文件保存为: {excel_filename}")
        print(f"文件路径: {os.path.abspath(excel_filename)}")
        
        # 显示数据统计
        print("\n=== 数据统计 ===")
        print(f"学生总数: {len(students_df)}")
        print(f"成绩记录总数: {len(grades_df)}")
        print(f"科目总数: {len(subjects_df)}")
        if not users_df.empty:
            print(f"用户账户总数: {len(users_df)}")
        
        # 显示学生分布
        if not students_df.empty:
            print("\n=== 学生年级分布 ===")
            grade_distribution = students_df['grade_level'].value_counts().sort_index()
            for grade, count in grade_distribution.items():
                print(f"{grade}: {count}人")
        
        return excel_filename
        
    except Exception as e:
        print(f"导出过程中发生错误: {e}")
        return None

if __name__ == "__main__":
    # 检查是否安装了pandas和openpyxl
    try:
        import pandas as pd
        import openpyxl
    except ImportError as e:
        print(f"缺少必要的库: {e}")
        print("请安装: pip install pandas openpyxl")
        exit(1)
    
    export_users_to_excel()