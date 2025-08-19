#!/bin/bash

# 智能教学助手启动脚本
# 用于启动后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装，请先安装Python3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        log_error "Python版本需要 >= 3.8，当前版本: $PYTHON_VERSION"
        exit 1
    fi
    
    log_success "Python环境检查通过: $PYTHON_VERSION"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖文件..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt文件不存在"
        exit 1
    fi
    
    if [ ! -f "service/requirements.txt" ]; then
        log_error "service/requirements.txt文件不存在"
        exit 1
    fi
    
    log_success "依赖文件检查通过"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    # 安装主要依赖
    pip3 install -r requirements.txt
    
    # 安装服务依赖
    pip3 install -r service/requirements.txt
    
    log_success "依赖安装完成"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p data
    mkdir -p temp
    
    log_success "目录创建完成"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_warning ".env文件不存在，从.env.example复制"
            cp .env.example .env
            log_warning "请编辑.env文件设置正确的配置"
        else
            log_error ".env和.env.example文件都不存在"
            exit 1
        fi
    fi
    
    log_success "配置文件检查完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 检查是否存在数据库初始化脚本
    if [ -f "scripts/init_db.py" ]; then
        python3 scripts/init_db.py
        log_success "数据库初始化完成"
    else
        log_warning "数据库初始化脚本不存在，跳过数据库初始化"
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    if [ -f "test_llm_integration.py" ]; then
        python3 test_llm_integration.py
        if [ $? -eq 0 ]; then
            log_success "测试通过"
        else
            log_warning "部分测试失败，但继续启动服务"
        fi
    else
        log_warning "测试文件不存在，跳过测试"
    fi
}

# 启动服务
start_service() {
    log_info "启动智能教学助手后端服务..."
    
    # 设置环境变量
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # 启动服务
    if command -v uvicorn &> /dev/null; then
        log_info "使用uvicorn启动服务..."
        uvicorn service.main:app --reload --host 0.0.0.0 --port 8000
    else
        log_info "uvicorn未安装，尝试使用python直接启动..."
        python3 -m service.main
    fi
}

# 主函数
main() {
    log_info "=== 智能教学助手后端服务启动 ==="
    
    # 检查是否在正确的目录
    if [ ! -f "service/main.py" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行检查和初始化
    check_python
    check_dependencies
    
    # 询问是否安装依赖
    read -p "是否需要安装/更新依赖? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
    fi
    
    create_directories
    check_config
    
    # 询问是否初始化数据库
    read -p "是否需要初始化数据库? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        init_database
    fi
    
    # 询问是否运行测试
    read -p "是否需要运行测试? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    # 启动服务
    start_service
}

# 处理中断信号
trap 'log_info "正在停止服务..."; exit 0' INT TERM

# 运行主函数
main "$@"