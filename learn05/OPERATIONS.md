# 智能教学助手运维指南

## 概述

本文档提供智能教学助手后端服务的日常运维指南，包括监控、维护、故障处理和性能优化等内容。

## 日常监控

### 1. 服务健康检查

#### 自动化健康检查

```bash
# 使用部署脚本检查状态
./deploy.sh status

# 检查所有服务
docker-compose ps

# 检查特定服务
curl -f http://localhost:8000/health || echo "服务异常"
```

#### 手动健康检查清单

- [ ] 后端API服务响应正常
- [ ] 数据库连接正常
- [ ] Redis缓存服务正常
- [ ] 大模型API调用正常
- [ ] 文件上传功能正常
- [ ] 日志记录正常

### 2. 性能监控指标

#### 关键指标

| 指标类型 | 指标名称 | 正常范围 | 告警阈值 |
|---------|---------|---------|----------|
| 响应时间 | API平均响应时间 | < 500ms | > 2s |
| 错误率 | HTTP 5xx错误率 | < 1% | > 5% |
| 资源使用 | CPU使用率 | < 70% | > 85% |
| 资源使用 | 内存使用率 | < 80% | > 90% |
| 资源使用 | 磁盘使用率 | < 80% | > 90% |
| 业务指标 | 大模型API成功率 | > 95% | < 90% |

#### 监控命令

```bash
# CPU和内存使用情况
top -p $(pgrep -f uvicorn)

# 磁盘使用情况
df -h

# 网络连接状态
netstat -tulpn | grep :8000

# 进程状态
ps aux | grep uvicorn
```

### 3. 日志监控

#### 日志文件位置

```
logs/
├── app.log              # 应用主日志
├── error.log            # 错误日志
├── access.log           # API访问日志
├── llm.log              # 大模型调用日志
├── performance.log      # 性能日志
└── security.log         # 安全日志
```

#### 日志监控脚本

```bash
#!/bin/bash
# log_monitor.sh - 日志监控脚本

# 检查错误日志
ERROR_COUNT=$(grep -c "ERROR" logs/error.log | tail -100)
if [ "$ERROR_COUNT" -gt 10 ]; then
    echo "警告: 发现 $ERROR_COUNT 个错误"
fi

# 检查大模型API失败
LLM_ERRORS=$(grep -c "LLM API Error" logs/llm.log | tail -100)
if [ "$LLM_ERRORS" -gt 5 ]; then
    echo "警告: 大模型API调用失败 $LLM_ERRORS 次"
fi

# 检查异常访问模式
SUSPICIOUS_IPS=$(awk '{print $1}' logs/access.log | sort | uniq -c | awk '$1 > 1000 {print $2, $1}')
if [ -n "$SUSPICIOUS_IPS" ]; then
    echo "警告: 发现可疑IP访问模式:"
    echo "$SUSPICIOUS_IPS"
fi
```

## 备份策略

### 1. 数据备份

#### 自动备份脚本

```bash
#!/bin/bash
# backup.sh - 自动备份脚本

BACKUP_DIR="/opt/backups/ai-tutor"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
cp data/ai_tutor.db "$BACKUP_DIR/ai_tutor_$DATE.db"

# 备份配置文件
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env nginx/ monitoring/

# 备份上传文件
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" uploads/

# 清理旧备份（保留30天）
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: $DATE"
```

#### 设置定时备份

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点备份）
0 2 * * * /opt/ai-tutor/scripts/backup.sh >> /var/log/ai-tutor-backup.log 2>&1
```

### 2. 备份验证

```bash
#!/bin/bash
# verify_backup.sh - 备份验证脚本

LATEST_BACKUP=$(ls -t /opt/backups/ai-tutor/*.db | head -1)

if [ -f "$LATEST_BACKUP" ]; then
    # 检查备份文件完整性
    sqlite3 "$LATEST_BACKUP" "PRAGMA integrity_check;"
    
    if [ $? -eq 0 ]; then
        echo "备份验证成功: $LATEST_BACKUP"
    else
        echo "备份验证失败: $LATEST_BACKUP"
        exit 1
    fi
else
    echo "未找到备份文件"
    exit 1
fi
```

## 故障处理

### 1. 常见故障及解决方案

#### 服务无响应

**症状**: API请求超时或无响应

**诊断步骤**:
```bash
# 1. 检查进程状态
ps aux | grep uvicorn

# 2. 检查端口占用
lsof -i :8000

# 3. 检查系统资源
top
free -h
df -h

# 4. 检查日志
tail -f logs/error.log
```

**解决方案**:
```bash
# 重启服务
./deploy.sh restart

# 如果问题持续，检查配置
cat .env | grep -v "#"

# 清理临时文件
rm -rf temp/*
```

#### 数据库连接失败

**症状**: 数据库相关操作失败

**诊断步骤**:
```bash
# 1. 检查数据库文件
ls -la data/ai_tutor.db

# 2. 检查文件权限
stat data/ai_tutor.db

# 3. 测试数据库连接
sqlite3 data/ai_tutor.db ".tables"
```

**解决方案**:
```bash
# 修复权限
chown www-data:www-data data/ai_tutor.db
chmod 644 data/ai_tutor.db

# 如果数据库损坏，从备份恢复
cp /opt/backups/ai-tutor/ai_tutor_latest.db data/ai_tutor.db
```

#### 大模型API调用失败

**症状**: 辅导方案生成失败

**诊断步骤**:
```bash
# 1. 检查API密钥配置
grep API_KEY .env

# 2. 测试网络连接
curl -I https://dashscope.aliyuncs.com

# 3. 检查API调用日志
grep "LLM API" logs/llm.log | tail -20
```

**解决方案**:
```bash
# 更新API密钥
vim .env

# 重启服务使配置生效
./deploy.sh restart

# 检查API配额和限制
curl -H "Authorization: Bearer $TONGYI_API_KEY" https://dashscope.aliyuncs.com/api/v1/usage
```

#### 内存泄漏

**症状**: 内存使用持续增长

**诊断步骤**:
```bash
# 1. 监控内存使用
watch -n 5 'ps aux | grep uvicorn'

# 2. 检查内存分配
cat /proc/$(pgrep uvicorn)/status | grep Vm

# 3. 分析内存使用模式
valgrind --tool=massif python -m uvicorn service.main:app
```

**解决方案**:
```bash
# 定期重启服务（临时方案）
echo "0 4 * * * /opt/ai-tutor/deploy.sh restart" | crontab -

# 优化代码（长期方案）
# - 检查循环引用
# - 优化大对象处理
# - 使用内存分析工具
```

### 2. 紧急故障处理流程

#### 故障响应流程

1. **故障发现** (0-5分钟)
   - 监控告警触发
   - 用户反馈问题
   - 定期检查发现

2. **初步评估** (5-10分钟)
   - 确定故障范围和影响
   - 评估故障严重程度
   - 决定是否需要紧急处理

3. **故障处理** (10-30分钟)
   - 执行快速修复措施
   - 记录处理过程
   - 验证修复效果

4. **故障恢复** (30-60分钟)
   - 全面验证系统功能
   - 监控系统稳定性
   - 通知相关人员

5. **事后分析** (1-24小时)
   - 分析故障根本原因
   - 制定预防措施
   - 更新运维文档

#### 紧急联系方式

```bash
# 创建紧急联系脚本
#!/bin/bash
# emergency_contact.sh

SEVERITY=$1
MESSAGE=$2

case $SEVERITY in
    "critical")
        # 发送短信和邮件
        echo "严重故障: $MESSAGE" | mail -s "AI教学助手严重故障" admin@example.com
        ;;
    "warning")
        # 发送邮件
        echo "警告: $MESSAGE" | mail -s "AI教学助手警告" admin@example.com
        ;;
esac
```

## 性能优化

### 1. 数据库优化

#### SQLite优化

```sql
-- 启用WAL模式
PRAGMA journal_mode=WAL;

-- 设置缓存大小
PRAGMA cache_size=10000;

-- 启用外键约束
PRAGMA foreign_keys=ON;

-- 分析表统计信息
ANALYZE;
```

#### 迁移到PostgreSQL

```bash
# 1. 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE ai_tutor;
CREATE USER ai_tutor_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_tutor TO ai_tutor_user;

# 3. 更新配置
echo "DATABASE_URL=postgresql://ai_tutor_user:secure_password@localhost/ai_tutor" >> .env

# 4. 迁移数据
python scripts/migrate_to_postgresql.py
```

### 2. 缓存优化

#### Redis配置优化

```bash
# redis.conf 优化配置
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### 应用层缓存策略

```python
# 缓存配置示例
CACHE_CONFIG = {
    'grade_analysis': {'ttl': 3600},  # 1小时
    'student_profile': {'ttl': 1800}, # 30分钟
    'class_statistics': {'ttl': 7200}, # 2小时
}
```

### 3. 应用优化

#### 异步处理优化

```python
# 使用异步任务处理耗时操作
from celery import Celery

app = Celery('ai_tutor')

@app.task
def generate_tutoring_plan_async(student_id, subject):
    # 异步生成辅导方案
    pass
```

#### 连接池优化

```python
# 数据库连接池配置
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600,
}
```

## 安全运维

### 1. 安全监控

#### 安全检查清单

- [ ] 定期更新系统补丁
- [ ] 监控异常登录尝试
- [ ] 检查文件权限设置
- [ ] 审计API访问日志
- [ ] 验证SSL证书有效性
- [ ] 检查防火墙规则

#### 安全监控脚本

```bash
#!/bin/bash
# security_check.sh

# 检查失败登录尝试
FAILED_LOGINS=$(grep "login failed" logs/security.log | wc -l)
if [ "$FAILED_LOGINS" -gt 50 ]; then
    echo "警告: 检测到 $FAILED_LOGINS 次失败登录尝试"
fi

# 检查可疑IP
SUSPICIOUS_IPS=$(awk '/login failed/ {print $1}' logs/security.log | sort | uniq -c | awk '$1 > 10 {print $2}')
if [ -n "$SUSPICIOUS_IPS" ]; then
    echo "警告: 发现可疑IP: $SUSPICIOUS_IPS"
fi

# 检查文件权限
find . -name "*.py" -perm 777 -exec echo "警告: 文件权限过于宽松: {}" \;
```

### 2. 访问控制

#### IP白名单配置

```nginx
# Nginx IP白名单配置
location /admin {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://ai_tutor_backend;
}
```

#### API限流配置

```python
# 应用层限流配置
RATE_LIMIT_CONFIG = {
    'default': '100/hour',
    'login': '10/minute',
    'upload': '20/hour',
    'llm_api': '50/hour',
}
```

## 容量规划

### 1. 资源使用预测

#### 用户增长模型

```python
# 容量规划计算
def calculate_resource_needs(users, growth_rate, months):
    """
    计算资源需求
    """
    future_users = users * (1 + growth_rate) ** months
    
    # 基于用户数估算资源需求
    cpu_cores = max(2, future_users // 1000)
    memory_gb = max(4, future_users // 500)
    storage_gb = max(20, future_users * 0.1)
    
    return {
        'users': future_users,
        'cpu_cores': cpu_cores,
        'memory_gb': memory_gb,
        'storage_gb': storage_gb
    }
```

#### 性能基准测试

```bash
# 使用Apache Bench进行压力测试
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# 使用wrk进行更详细的测试
wrk -t12 -c400 -d30s http://localhost:8000/api/v1/grades
```

### 2. 扩容策略

#### 垂直扩容

```bash
# 增加服务器资源
# 1. 停止服务
./deploy.sh stop

# 2. 升级硬件配置
# 3. 更新配置文件
vim .env

# 4. 重启服务
./deploy.sh start
```

#### 水平扩容

```yaml
# docker-compose.yml 多实例配置
version: '3.8'
services:
  ai-tutor-backend-1:
    build: .
    ports:
      - "8000:8000"
  
  ai-tutor-backend-2:
    build: .
    ports:
      - "8002:8000"
  
  ai-tutor-backend-3:
    build: .
    ports:
      - "8003:8000"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - ai-tutor-backend-1
      - ai-tutor-backend-2
      - ai-tutor-backend-3
```

## 运维自动化

### 1. 自动化脚本

#### 健康检查自动化

```bash
#!/bin/bash
# auto_health_check.sh

CHECK_INTERVAL=300  # 5分钟
MAX_FAILURES=3
FAILURE_COUNT=0

while true; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): 健康检查通过"
        FAILURE_COUNT=0
    else
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        echo "$(date): 健康检查失败 ($FAILURE_COUNT/$MAX_FAILURES)"
        
        if [ $FAILURE_COUNT -ge $MAX_FAILURES ]; then
            echo "$(date): 服务异常，尝试重启"
            ./deploy.sh restart
            FAILURE_COUNT=0
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
```

#### 日志清理自动化

```bash
#!/bin/bash
# auto_log_cleanup.sh

# 压缩7天前的日志
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;

# 删除30天前的压缩日志
find logs/ -name "*.log.gz" -mtime +30 -delete

# 清理临时文件
find temp/ -type f -mtime +1 -delete

echo "$(date): 日志清理完成"
```

### 2. 监控告警自动化

#### Prometheus告警规则

```yaml
# 自动告警配置
groups:
  - name: auto-recovery
    rules:
      - alert: ServiceAutoRestart
        expr: up == 0
        for: 5m
        labels:
          severity: critical
          action: restart
        annotations:
          summary: "服务自动重启"
          description: "服务已自动重启"
```

#### 告警处理脚本

```bash
#!/bin/bash
# alert_handler.sh

ALERT_TYPE=$1
ALERT_MESSAGE=$2

case $ALERT_TYPE in
    "service_down")
        echo "$(date): 检测到服务停止，尝试重启"
        ./deploy.sh restart
        ;;
    "high_memory")
        echo "$(date): 内存使用率过高，清理缓存"
        redis-cli FLUSHALL
        ;;
    "disk_full")
        echo "$(date): 磁盘空间不足，清理日志"
        ./scripts/auto_log_cleanup.sh
        ;;
esac
```

## 运维工具

### 1. 监控仪表板

#### 自定义监控脚本

```python
#!/usr/bin/env python3
# monitor_dashboard.py

import psutil
import requests
import json
from datetime import datetime

def get_system_metrics():
    """获取系统指标"""
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'timestamp': datetime.now().isoformat()
    }

def get_service_metrics():
    """获取服务指标"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return {
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'response_time': response.elapsed.total_seconds()
        }
    except:
        return {
            'status': 'down',
            'response_time': None
        }

def main():
    metrics = {
        'system': get_system_metrics(),
        'service': get_service_metrics()
    }
    
    print(json.dumps(metrics, indent=2))

if __name__ == '__main__':
    main()
```

### 2. 运维工具集

#### 一键运维脚本

```bash
#!/bin/bash
# ops_toolkit.sh

show_help() {
    echo "智能教学助手运维工具集"
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  status      - 显示服务状态"
    echo "  logs        - 查看日志"
    echo "  backup      - 执行备份"
    echo "  cleanup     - 清理临时文件"
    echo "  monitor     - 显示监控信息"
    echo "  restart     - 重启服务"
    echo "  update      - 更新应用"
    echo "  help        - 显示帮助信息"
}

case $1 in
    "status")
        ./deploy.sh status
        ;;
    "logs")
        tail -f logs/app.log
        ;;
    "backup")
        ./scripts/backup.sh
        ;;
    "cleanup")
        ./scripts/auto_log_cleanup.sh
        ;;
    "monitor")
        python3 scripts/monitor_dashboard.py
        ;;
    "restart")
        ./deploy.sh restart
        ;;
    "update")
        ./deploy.sh update
        ;;
    "help"|*)
        show_help
        ;;
esac
```

## 总结

本运维指南涵盖了智能教学助手后端服务的完整运维流程，包括：

1. **日常监控**: 服务健康检查、性能监控、日志分析
2. **备份策略**: 自动备份、备份验证、恢复流程
3. **故障处理**: 常见问题诊断、紧急故障响应
4. **性能优化**: 数据库优化、缓存策略、应用调优
5. **安全运维**: 安全监控、访问控制、威胁防护
6. **容量规划**: 资源预测、扩容策略
7. **运维自动化**: 自动化脚本、监控告警

建议运维人员：
- 定期执行健康检查
- 监控关键性能指标
- 及时处理告警信息
- 保持系统和依赖的更新
- 定期进行备份验证
- 持续优化系统性能

通过遵循本指南，可以确保智能教学助手后端服务的稳定运行和高可用性。