#!/bin/bash
# 智能教学助手服务停止脚本
# DevOps运维工程师专用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/Users/tangxiaolu/project/PythonProject/aiLearn/learn05"
PID_DIR="$PROJECT_ROOT/devops/logs/pids"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 停止服务函数
stop_service() {
    local service_name=$1
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            log_info "停止${service_name}服务 (PID: $pid)..."
            kill $pid
            sleep 2
            
            # 如果进程仍在运行，强制杀死
            if ps -p $pid > /dev/null 2>&1; then
                log_warning "强制停止${service_name}服务..."
                kill -9 $pid
            fi
            
            log_success "${service_name}服务已停止"
        else
            log_warning "${service_name}服务进程不存在 (PID: $pid)"
        fi
        rm -f "$pid_file"
    else
        log_warning "${service_name}服务PID文件不存在"
    fi
}

# 通过端口停止服务
stop_by_port() {
    local port=$1
    local service_name=$2
    
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        log_info "通过端口$port停止${service_name}服务 (PID: $pid)..."
        kill $pid 2>/dev/null || true
        sleep 2
        
        # 检查是否还在运行
        local check_pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$check_pid" ]; then
            log_warning "强制停止端口$port上的${service_name}服务..."
            kill -9 $check_pid 2>/dev/null || true
        fi
        
        log_success "${service_name}服务已停止"
    else
        log_info "端口$port上没有运行${service_name}服务"
    fi
}

# 停止后端服务
stop_backend() {
    log_info "停止后端服务..."
    stop_service "backend"
    stop_by_port 8000 "后端"
}

# 停止大模型服务
stop_llm() {
    log_info "停止大模型服务..."
    stop_service "llm"
    stop_by_port 8001 "大模型"
}

# 停止前端服务
stop_frontend() {
    log_info "停止前端服务..."
    stop_service "frontend"
    stop_by_port 8080 "前端"
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    
    # 清理PID文件
    if [ -d "$PID_DIR" ]; then
        rm -f "$PID_DIR"/*.pid
    fi
    
    log_success "清理完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    echo "=== 服务状态报告 ==="
    
    # 检查后端服务
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} 后端服务: 仍在运行 (端口8000)"
    else
        echo -e "${GREEN}✓${NC} 后端服务: 已停止"
    fi
    
    # 检查大模型服务
    if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} 大模型服务: 仍在运行 (端口8001)"
    else
        echo -e "${GREEN}✓${NC} 大模型服务: 已停止"
    fi
    
    # 检查前端服务
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} 前端服务: 仍在运行 (端口8080)"
    else
        echo -e "${GREEN}✓${NC} 前端服务: 已停止"
    fi
    
    echo "========================"
}

# 主函数
main() {
    log_info "智能教学助手服务停止器 v1.0"
    log_info "DevOps运维工程师专用工具"
    
    case "${1:-all}" in
        "backend")
            stop_backend
            ;;
        "llm")
            stop_llm
            ;;
        "frontend")
            stop_frontend
            ;;
        "all")
            stop_backend
            stop_llm
            stop_frontend
            cleanup
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "用法: $0 {backend|llm|frontend|all|cleanup}"
            echo "  backend  - 停止后端服务"
            echo "  llm      - 停止大模型服务"
            echo "  frontend - 停止前端服务"
            echo "  all      - 停止所有服务 (默认)"
            echo "  cleanup  - 清理临时文件"
            exit 1
            ;;
    esac
    
    echo ""
    check_services
    
    log_success "服务停止完成！"
}

main "$@"