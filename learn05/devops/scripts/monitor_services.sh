#!/bin/bash
# 智能教学助手服务监控脚本
# DevOps运维工程师专用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/Users/tangxiaolu/project/PythonProject/aiLearn/learn05"
LOG_DIR="$PROJECT_ROOT/devops/logs"
MONITOR_LOG="$LOG_DIR/monitor.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log_monitor() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$MONITOR_LOG"
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

# 检查HTTP服务健康状态
check_http_health() {
    local url=$1
    local timeout=${2:-5}
    
    if curl -s --max-time $timeout "$url" >/dev/null 2>&1; then
        return 0  # 健康
    else
        return 1  # 不健康
    fi
}

# 获取进程CPU和内存使用率
get_process_stats() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null || echo "")
    
    if [ -n "$pid" ]; then
        local stats=$(ps -p $pid -o pid,pcpu,pmem,rss,vsz --no-headers 2>/dev/null || echo "")
        if [ -n "$stats" ]; then
            echo "$stats"
        else
            echo "N/A N/A N/A N/A N/A"
        fi
    else
        echo "N/A N/A N/A N/A N/A"
    fi
}

# 显示服务状态
show_service_status() {
    local service_name=$1
    local port=$2
    local health_url=$3
    
    printf "%-15s" "$service_name:"
    
    if check_port $port; then
        printf "${GREEN}✓ 运行中${NC} "
        
        # 健康检查
        if [ -n "$health_url" ] && check_http_health "$health_url"; then
            printf "${GREEN}[健康]${NC} "
        elif [ -n "$health_url" ]; then
            printf "${YELLOW}[异常]${NC} "
        fi
        
        # 获取进程统计信息
        local stats=$(get_process_stats $port)
        local pid=$(echo $stats | awk '{print $1}')
        local cpu=$(echo $stats | awk '{print $2}')
        local mem=$(echo $stats | awk '{print $3}')
        local rss=$(echo $stats | awk '{print $4}')
        
        printf "PID:%-6s CPU:%-6s%% MEM:%-6s%% RSS:%-8s" "$pid" "$cpu" "$mem" "$rss"
    else
        printf "${RED}✗ 停止${NC}     "
        printf "%-40s" "N/A"
    fi
    
    printf "\n"
}

# 显示系统资源使用情况
show_system_stats() {
    echo -e "\n${CYAN}=== 系统资源使用情况 ===${NC}"
    
    # CPU使用率
    local cpu_usage=$(top -l 1 -s 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    printf "CPU使用率: %s%%\n" "$cpu_usage"
    
    # 内存使用情况
    local mem_info=$(vm_stat | grep -E "Pages (free|active|inactive|speculative|wired down)")
    local page_size=4096
    local free_pages=$(echo "$mem_info" | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    local active_pages=$(echo "$mem_info" | grep "Pages active" | awk '{print $3}' | sed 's/\.//')
    local inactive_pages=$(echo "$mem_info" | grep "Pages inactive" | awk '{print $3}' | sed 's/\.//')
    local wired_pages=$(echo "$mem_info" | grep "Pages wired down" | awk '{print $4}' | sed 's/\.//')
    
    local total_mem=$((($free_pages + $active_pages + $inactive_pages + $wired_pages) * $page_size / 1024 / 1024))
    local used_mem=$((($active_pages + $inactive_pages + $wired_pages) * $page_size / 1024 / 1024))
    local free_mem=$(($free_pages * $page_size / 1024 / 1024))
    
    printf "内存使用: %dMB / %dMB (%.1f%%)\n" "$used_mem" "$total_mem" "$(echo "scale=1; $used_mem * 100 / $total_mem" | bc)"
    
    # 磁盘使用情况
    echo "磁盘使用:"
    df -h | grep -E "^/dev/" | awk '{printf "  %s: %s / %s (%s)\n", $1, $3, $2, $5}'
}

# 显示网络连接统计
show_network_stats() {
    echo -e "\n${PURPLE}=== 网络连接统计 ===${NC}"
    
    # 检查服务端口连接数
    for port in 8000 8001 8080; do
        local connections=$(netstat -an | grep ":$port " | wc -l | tr -d ' ')
        printf "端口 %d 连接数: %s\n" "$port" "$connections"
    done
}

# 显示日志摘要
show_log_summary() {
    echo -e "\n${BLUE}=== 最近日志摘要 ===${NC}"
    
    for service in backend llm frontend; do
        local log_file="$LOG_DIR/${service}.log"
        if [ -f "$log_file" ]; then
            echo "${service}服务最近日志:"
            tail -3 "$log_file" 2>/dev/null | sed 's/^/  /' || echo "  无日志内容"
        else
            echo "${service}服务: 日志文件不存在"
        fi
    done
}

# 实时监控模式
real_time_monitor() {
    local interval=${1:-5}
    
    echo -e "${CYAN}启动实时监控模式 (刷新间隔: ${interval}秒)${NC}"
    echo "按 Ctrl+C 退出监控"
    echo ""
    
    while true; do
        clear
        echo -e "${CYAN}智能教学助手服务监控 - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
        echo "=================================================="
        
        show_services_status
        show_system_stats
        show_network_stats
        
        echo -e "\n${YELLOW}下次刷新: ${interval}秒后${NC}"
        
        sleep $interval
    done
}

# 显示所有服务状态
show_services_status() {
    echo -e "\n${GREEN}=== 服务状态概览 ===${NC}"
    printf "%-15s %-20s %-40s\n" "服务" "状态" "进程信息"
    echo "----------------------------------------------------------------"
    
    show_service_status "后端服务" 8000 "http://127.0.0.1:8000"
    show_service_status "大模型服务" 8001 "http://localhost:8001"
    show_service_status "前端服务" 8080 "http://localhost:8080"
}

# 生成监控报告
generate_report() {
    local report_file="$LOG_DIR/monitor_report_$(date '+%Y%m%d_%H%M%S').txt"
    
    {
        echo "智能教学助手服务监控报告"
        echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "=================================================="
        
        show_services_status
        show_system_stats
        show_network_stats
        show_log_summary
        
    } > "$report_file"
    
    echo "监控报告已生成: $report_file"
}

# 主函数
main() {
    case "${1:-status}" in
        "status")
            echo -e "${CYAN}智能教学助手服务监控器 v1.0${NC}"
            echo -e "${CYAN}DevOps运维工程师专用工具${NC}"
            show_services_status
            ;;
        "full")
            echo -e "${CYAN}智能教学助手完整监控报告${NC}"
            show_services_status
            show_system_stats
            show_network_stats
            show_log_summary
            ;;
        "watch")
            real_time_monitor "${2:-5}"
            ;;
        "report")
            generate_report
            ;;
        "logs")
            show_log_summary
            ;;
        *)
            echo "用法: $0 {status|full|watch|report|logs}"
            echo "  status - 显示服务状态 (默认)"
            echo "  full   - 显示完整监控信息"
            echo "  watch  - 实时监控模式 (可选参数: 刷新间隔秒数)"
            echo "  report - 生成监控报告"
            echo "  logs   - 显示日志摘要"
            echo ""
            echo "示例:"
            echo "  $0 watch 10    # 10秒间隔实时监控"
            echo "  $0 full        # 显示完整信息"
            exit 1
            ;;
    esac
}

# 记录监控日志
log_monitor "监控脚本执行: $*"

main "$@"