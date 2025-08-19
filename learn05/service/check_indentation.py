def check_indentation(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # 跳过空行和注释行
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('#'):
            continue
        
        # 计算缩进
        indent_count = len(line) - len(line.lstrip())
        indent_type = 'space' if line.startswith(' ') else 'tab'
        
        # 检查是否有混合的缩进类型
        if '\t' in line and ' ' in line[:indent_count]:
            print(f"第{i}行: 混合使用了空格和制表符缩进")
            print(f"内容: {line.strip()}")
        
        # 检查缩进是否为4的倍数（如果是空格缩进）
        if indent_type == 'space' and indent_count % 4 != 0:
            print(f"第{i}行: 空格缩进不是4的倍数，当前缩进{indent_count}个空格")
            print(f"内容: {line.strip()}")

# 检查notification_system.py文件的缩进
check_indentation('notification_system.py')