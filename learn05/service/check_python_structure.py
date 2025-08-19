import tokenize
import io

# 检查Python文件的语法结构
with open('notification_system.py', 'rb') as f:
    try:
        tokens = list(tokenize.tokenize(f.readline))
        print("文件语法结构正确")
    except tokenize.TokenError as e:
        print(f"Token错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")