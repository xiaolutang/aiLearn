#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看Excel文件内容概览
"""

import pandas as pd
import os
import glob

def view_excel_summary():
    """
    查看最新生成的Excel文件内容概览
    """
    # 查找最新的用户数据导出文件
    excel_files = glob.glob("用户数据导出_*.xlsx")
    if not excel_files:
        print("未找到用户数据导出文件")
        return
    
    # 获取最新的文件
    latest_file = max(excel_files, key=os.path.getctime)
    print(f"正在查看文件: {latest_file}")
    print(f"文件大小: {os.path.getsize(latest_file) / 1024:.1f} KB")
    print("="*50)
    
    try:
        # 读取Excel文件的所有工作表
        excel_file = pd.ExcelFile(latest_file)
        print(f"工作表列表: {excel_file.sheet_names}")
        print("="*50)
        
        # 查看每个工作表的概览
        for sheet_name in excel_file.sheet_names:
            print(f"\n【{sheet_name}】")
            df = pd.read_excel(latest_file, sheet_name=sheet_name)
            print(f"行数: {len(df)}")
            print(f"列数: {len(df.columns)}")
            print(f"列名: {list(df.columns)}")
            
            # 显示前几行数据
            if len(df) > 0:
                print("前3行数据:")
                print(df.head(3).to_string())
            print("-" * 40)
        
        print(f"\n✅ Excel文件查看完成: {latest_file}")
        return latest_file
        
    except Exception as e:
        print(f"读取Excel文件时发生错误: {e}")
        return None

if __name__ == "__main__":
    view_excel_summary()