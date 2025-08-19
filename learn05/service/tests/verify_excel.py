#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Excel文件内容的脚本
"""

import pandas as pd
import os

def verify_excel_file(excel_file: str = "test_accounts.xlsx"):
    """
    验证Excel文件内容
    
    Args:
        excel_file: Excel文件路径
    """
    if not os.path.exists(excel_file):
        print(f"❌ Excel文件不存在: {excel_file}")
        return False
    
    try:
        # 读取所有工作表
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        print(f"✅ Excel文件验证成功: {excel_file}")
        print(f"文件大小: {os.path.getsize(excel_file)} 字节")
        print(f"包含工作表数量: {len(excel_data)}")
        print("\n📊 工作表详情:")
        
        for sheet_name, df in excel_data.items():
            print(f"\n📋 工作表: {sheet_name}")
            print(f"   行数: {len(df)}")
            print(f"   列数: {len(df.columns)}")
            print(f"   列名: {list(df.columns)}")
            
            if sheet_name == "测试账号":
                print("\n🔍 测试账号预览 (前3行):")
                print(df.head(3).to_string(index=False))
                
                # 统计角色分布
                if '角色' in df.columns:
                    role_counts = df['角色'].value_counts()
                    print("\n👥 角色分布:")
                    for role, count in role_counts.items():
                        print(f"   {role}: {count}个")
                
                # 统计状态分布
                if '状态' in df.columns:
                    status_counts = df['状态'].value_counts()
                    print("\n📊 状态分布:")
                    for status, count in status_counts.items():
                        print(f"   {status}: {count}个")
            
            elif sheet_name in ["角色统计", "状态统计"]:
                print(f"\n📈 {sheet_name}:")
                print(df.to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ 验证Excel文件失败: {e}")
        return False

if __name__ == "__main__":
    verify_excel_file()