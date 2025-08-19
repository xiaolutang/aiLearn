import ast
import sys

# 检查notification_system.py文件的语法和缩进
with open('notification_system.py', 'r', encoding='utf-8') as f:
    content = f.read()

try:
    ast.parse(content)
    print("文件语法正确")
except SyntaxError as e:
    print(f"语法错误: {e}")
    print(f"行号: {e.lineno}, 列号: {e.offset}")
    print(f"错误信息: {e.text}")