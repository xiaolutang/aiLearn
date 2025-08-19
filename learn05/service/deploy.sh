#!/bin/bash

# 智能教学助手部署脚本
# 使用方法: ./deploy.sh [环境] [操作]
# 环境: dev, staging, prod
# 操作: build, start, stop, restart, logs, status

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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
}

# 检查环境变量文件
check_env_file() {
    if [ ! -f ".env" ]; then
        log_warning ".env文件不存在，从.env.example复制"
        cp .env.example .env
        log_warning "请编辑.env文件并填入正确的配置值"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p logs data uploads nginx/ssl monitoring/grafana/{dashboards,datasources}
    
    # 设置权限
    chmod 755 logs data uploads
    
    log_success "目录创建完成"
}

# 构建镜像
build_image() {
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    local profile=${1:-""}
    log_info "启动服务..."
    
    if [ -n "$profile" ]; then
        docker-compose --profile $profile up -d
    else
        docker-compose up -d
    fi
    
    log_success "服务启动完成"
    show_status
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose restart
    log_success "服务重启完成"
    show_status
}

# 显示日志
show_logs() {
    local service=${1:-"ai-tutor-backend"}
    log_info "显示 $service 服务日志..."
    docker-compose logs -f $service
}

# 显示状态
show_status() {
    log_info "服务状态:"
    docker-compose ps
    
    echo ""
    log_info "健康检查:"
    docker-compose exec ai-tutor-backend curl -f http://localhost:8000/health 2>/dev/null && \
        log_success "后端服务健康" || log_warning "后端服务异常"
}

# 清理资源
cleanup() {
    log_info "清理Docker资源..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    log_success "清理完成"
}

# 备份数据
backup_data() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    log_info "备份数据到 $backup_dir..."
    
    mkdir -p $backup_dir
    
    # 备份数据库
    if [ -f "student_database.db" ]; then
        cp student_database.db $backup_dir/
    fi
    
    # 备份上传文件
    if [ -d "uploads" ]; then
        cp -r uploads $backup_dir/
    fi
    
    # 备份日志
    if [ -d "logs" ]; then
        cp -r logs $backup_dir/
    fi
    
    log_success "数据备份完成: $backup_dir"
}

# 更新应用
update_app() {
    log_info "更新应用..."
    
    # 备份数据
    backup_data
    
    # 拉取最新代码
    git pull origin main
    
    # 重新构建和启动
    build_image
    restart_services
    
    log_success "应用更新完成"
}

# 初始化数据
init_data() {
    log_info "初始化测试数据..."
    docker-compose exec ai-tutor-backend python init_test_data.py
    log_success "测试数据初始化完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    docker-compose exec ai-tutor-backend python -m pytest service/tests/ -v
    log_success "测试完成"
}

# 显示帮助信息
show_help() {
    echo "智能教学助手部署脚本"
    echo ""
    echo "使用方法: $0 [操作] [参数]"
    echo ""
    echo "操作:"
    echo "  build          构建Docker镜像"
    echo "  start          启动服务"
    echo "  stop           停止服务"
    echo "  restart        重启服务"
    echo "  logs [服务名]   显示日志"
    echo "  status         显示服务状态"
    echo "  cleanup        清理Docker资源"
    echo "  backup         备份数据"
    echo "  update         更新应用"
    echo "  init-data      初始化测试数据"
    echo "  test           运行测试"
    echo "  help           显示帮助信息"
    echo ""
    echo "环境配置:"
    echo "  dev            开发环境（默认）"
    echo "  prod           生产环境（包含nginx）"
    echo "  monitoring     监控环境（包含prometheus和grafana）"
    echo ""
    echo "示例:"
    echo "  $0 build                    # 构建镜像"
    echo "  $0 start                    # 启动开发环境"
    echo "  $0 start prod               # 启动生产环境"
    echo "  $0 start monitoring         # 启动监控环境"
    echo "  $0 logs ai-tutor-backend    # 查看后端日志"
    echo "  $0 status                   # 查看服务状态"
}

# 主函数
main() {
    local action=${1:-"help"}
    local param=${2:-""}
    
    # 检查依赖
    check_docker
    check_env_file
    create_directories
    
    case $action in
        "build")
            build_image
            ;;
        "start")
            start_services $param
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs $param
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "backup")
            backup_data
            ;;
        "update")
            update_app
            ;;
        "init-data")
            init_data
            ;;
        "test")
            run_tests
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "未知操作: $action"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"