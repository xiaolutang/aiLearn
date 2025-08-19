#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import signal
from concurrent.futures import ThreadPoolExecutor

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置信息
SERVICE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service')
PORT = 5001
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')

# 运行中的进程
processes = []

# 清除旧的日志文件
def clear_old_log():
    if os.path.exists(LOG_FILE):
        try:
            os.remove(LOG_FILE)
            print(f"已清除旧的日志文件: {LOG_FILE}")
        except Exception as e:
            print(f"清除日志文件失败: {e}")

# 启动后端服务
def start_backend():
    print("正在启动智能教学助手后端服务...")
    log_file = open(LOG_FILE, 'a')
    
    # 安装依赖
    print("正在安装依赖...")
    install_cmd = [sys.executable, '-m', 'pip', 'install', '-r', os.path.join(SERVICE_DIR, 'requirements.txt')]
    install_proc = subprocess.Popen(install_cmd, stdout=log_file, stderr=log_file)
    install_proc.wait()
    
    # 启动服务
    cmd = [sys.executable, os.path.join(SERVICE_DIR, 'intelligent_teaching_assistant.py')]
    proc = subprocess.Popen(
        cmd,
        cwd=SERVICE_DIR,
        stdout=log_file,
        stderr=log_file,
        preexec_fn=os.setsid  # 设置进程组，方便后续杀死所有子进程
    )
    
    processes.append((proc, log_file))
    
    # 等待服务启动
    time.sleep(3)
    print(f"智能教学助手后端服务已启动，端口: {PORT}")
    print(f"API文档地址: http://localhost:{PORT}/docs")
    print(f"日志文件: {LOG_FILE}")

# 停止所有进程
def stop_all_processes(signal=None, frame=None):
    print("\n正在停止所有进程...")
    
    for proc, log_file in processes:
        try:
            # 杀死进程组中的所有进程
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
            print(f"进程 {proc.pid} 已停止")
        except Exception as e:
            print(f"停止进程失败: {e}")
        
        # 关闭日志文件
        try:
            log_file.close()
        except:
            pass
    
    processes.clear()
    print("所有进程已停止")
    sys.exit(0)

# 主函数
def main():
    # 设置信号处理
    signal.signal(signal.SIGINT, stop_all_processes)
    signal.signal(signal.SIGTERM, stop_all_processes)
    
    # 清除旧日志
    clear_old_log()
    
    # 启动后端服务
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(start_backend)
    
    # 保持主进程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all_processes()

if __name__ == "__main__":
    main()