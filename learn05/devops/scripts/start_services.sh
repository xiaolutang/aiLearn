#!/bin/bash
# 智能教学助手服务启动脚本
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
LOG_DIR="$PROJECT_ROOT/devops/logs"
PID_DIR="$PROJECT_ROOT/devops/logs/pids"

# 创建必要目录
mkdir -p "$LOG_DIR" "$PID_DIR"

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

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    
    if check_port 8000; then
        log_warning "端口8000已被占用，后端服务可能已在运行"
        return 0
    fi
    
    cd "$PROJECT_ROOT/service"
    nohup python3 server.py > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$PID_DIR/backend.pid"
    
    # 等待服务启动
    sleep 3
    
    if check_port 8000; then
        log_success "后端服务启动成功 - http://127.0.0.1:8000"
        return 0
    else
        log_error "后端服务启动失败"
        return 1
    fi
}

# 启动大模型服务
start_llm() {
    log_info "启动大模型服务..."
    
    if check_port 8001; then
        log_warning "端口8001已被占用，大模型服务可能已在运行"
        return 0
    fi
    
    cd "$PROJECT_ROOT/llm"
    nohup python3 main.py > "$LOG_DIR/llm.log" 2>&1 &
    echo $! > "$PID_DIR/llm.pid"
    
    # 等待服务启动
    sleep 5
    
    if check_port 8001; then
        log_success "大模型服务启动成功 - http://localhost:8001"
        return 0
    else
        log_error "大模型服务启动失败"
        return 1
    fi
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."
    
    if check_port 8080; then
        log_warning "端口8080已被占用，前端服务可能已在运行"
        return 0
    fi
    
    cd "$PROJECT_ROOT/ui/ui2.0"
    nohup python3 -m http.server 8080 > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "$PID_DIR/frontend.pid"
    
    # 等待服务启动
    sleep 2
    
    if check_port 8080; then
        log_success "前端服务启动成功 - http://localhost:8080"
        return 0
    else
        log_error "前端服务启动失败"
        return 1
    fi
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    echo "=== 服务状态报告 ==="
    
    # 检查后端服务
    if check_port 8000; then
        echo -e "${GREEN}✓${NC} 后端服务: 运行中 (http://127.0.0.1:8000)"
    else
        echo -e "${RED}✗${NC} 后端服务: 未运行"
    fi
    
    # 检查大模型服务
    if check_port 8001; then
        echo -e "${GREEN}✓${NC} 大模型服务: 运行中 (http://localhost:8001)"
    else
        echo -e "${RED}✗${NC} 大模型服务: 未运行"
    fi
    
    # 检查前端服务
    if check_port 8080; then
        echo -e "${GREEN}✓${NC} 前端服务: 运行中 (http://localhost:8080)"
    else
        echo -e "${RED}✗${NC} 前端服务: 未运行"
    fi
    
    echo "========================"
}

# 主函数
main() {
    log_info "智能教学助手服务启动器 v1.0"
    log_info "DevOps运维工程师专用工具"
    
    case "${1:-all}" in
        "backend")
            start_backend
            ;;
        "llm")
            start_llm
            ;;
        "frontend")
            start_frontend
            ;;
        "all")
            start_backend
            start_llm
            start_frontend
            ;;
        "status")
            check_services
            ;;
        *)
            echo "用法: $0 {backend|llm|frontend|all|status}"
            echo "  backend  - 启动后端服务"
            echo "  llm      - 启动大模型服务"
            echo "  frontend - 启动前端服务"
            echo "  all      - 启动所有服务 (默认)"
            echo "  status   - 检查服务状态"
            exit 1
            ;;
    esac
    
    echo ""
    check_services
    
    log_success "服务启动完成！"
    log_info "使用 './stop_services.sh' 停止所有服务"
    log_info "使用 './start_services.sh status' 查看服务状态"
}

main "$@"