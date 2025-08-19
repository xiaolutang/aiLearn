# 智能教学助手运维指南

## 概述

本文档为智能教学助手项目的运维工程师专用指南，提供完整的服务部署、监控、维护和故障处理方案。

## 项目架构

### 服务组件

- **后端服务** (端口8000): 提供API接口和业务逻辑处理
- **大模型服务** (端口8001): 提供AI智能体和大模型推理服务
- **前端服务** (端口8080): 提供用户界面和交互体验

### 技术栈

- **后端**: Python + FastAPI
- **AI服务**: Python + 通义千问/OpenAI API
- **前端**: HTML + JavaScript + CSS
- **运维**: Bash脚本 + YAML配置

## 快速开始

### 1. 环境准备

确保系统已安装以下依赖：

```bash
# Python 3.8+
python3 --version

# 必要的Python包
pip3 install python-dotenv fastapi uvicorn

# 系统工具
which lsof curl bc
```

### 2. 配置API密钥

编辑项目根目录的 `.env` 文件：

```bash
# 大模型API密钥
OPENAI_API_KEY=your_openai_api_key
TONG_YI_API_KEY=your_tongyi_api_key
DASHSCOPE_API_KEY=your_dashscope_api_key

# 数据库配置
DATABASE_URL=sqlite:///./smart_teaching.db

# Redis配置
REDIS_URL=redis://localhost:6379
```

### 3. 启动所有服务

```bash
cd /Users/tangxiaolu/project/PythonProject/aiLearn/learn05/devops/scripts

# 启动所有服务
./start_services.sh

# 检查服务状态
./start_services.sh status
```

## 运维脚本使用指南

### 服务启动脚本 (start_services.sh)

```bash
# 启动所有服务
./start_services.sh

# 启动单个服务
./start_services.sh backend    # 启动后端服务
./start_services.sh llm        # 启动大模型服务
./start_services.sh frontend   # 启动前端服务

# 检查服务状态
./start_services.sh status
```

### 服务停止脚本 (stop_services.sh)

```bash
# 停止所有服务
./stop_services.sh

# 停止单个服务
./stop_services.sh backend     # 停止后端服务
./stop_services.sh llm         # 停止大模型服务
./stop_services.sh frontend    # 停止前端服务

# 清理临时文件
./stop_services.sh cleanup
```

### 服务监控脚本 (monitor_services.sh)

```bash
# 查看服务状态
./monitor_services.sh status

# 查看完整监控信息
./monitor_services.sh full

# 实时监控模式
./monitor_services.sh watch     # 默认5秒刷新
./monitor_services.sh watch 10  # 10秒刷新间隔

# 生成监控报告
./monitor_services.sh report

# 查看日志摘要
./monitor_services.sh logs
```

## 目录结构

```
devops/
├── scripts/                 # 运维脚本
│   ├── start_services.sh   # 服务启动脚本
│   ├── stop_services.sh    # 服务停止脚本
│   └── monitor_services.sh # 服务监控脚本
├── config/                 # 配置文件
│   └── services.yaml       # 服务配置
├── monitoring/             # 监控相关
├── logs/                   # 日志文件
│   ├── pids/              # 进程ID文件
│   ├── backend.log        # 后端服务日志
│   ├── llm.log            # 大模型服务日志
│   ├── frontend.log       # 前端服务日志
│   └── monitor.log        # 监控日志
├── tools/                  # 运维工具
└── docs/                   # 文档
    └── README.md          # 本文档
```

## 服务配置

### 端口分配

| 服务 | 端口 | 协议 | 描述 |
|------|------|------|------|
| 后端服务 | 8000 | HTTP | API接口服务 |
| 大模型服务 | 8001 | HTTP | AI智能体服务 |
| 前端服务 | 8080 | HTTP | 用户界面服务 |

### 服务依赖关系

```
前端服务 (8080)
    ↓
后端服务 (8000) ← → 大模型服务 (8001)
```

## 监控和告警

### 健康检查

所有服务都配置了健康检查端点：

- 后端服务: `http://127.0.0.1:8000`
- 大模型服务: `http://localhost:8001`
- 前端服务: `http://localhost:8080`

### 监控指标

- **服务状态**: 运行/停止状态
- **进程信息**: PID, CPU使用率, 内存使用率
- **系统资源**: CPU, 内存, 磁盘使用情况
- **网络连接**: 各端口连接数统计
- **日志监控**: 错误日志和异常检测

### 告警规则

- 服务停止运行
- CPU使用率超过80%
- 内存使用率超过80%
- 磁盘使用率超过90%
- 连续健康检查失败

## 故障处理

### 常见问题

#### 1. 服务启动失败

**症状**: 服务无法启动或立即退出

**排查步骤**:
```bash
# 检查端口占用
lsof -i :8000
lsof -i :8001
lsof -i :8080

# 查看错误日志
tail -f devops/logs/backend.log
tail -f devops/logs/llm.log
tail -f devops/logs/frontend.log

# 检查环境变量
env | grep -E "(API_KEY|DATABASE|REDIS)"
```

**解决方案**:
- 确保端口未被占用
- 检查API密钥配置
- 验证依赖包安装
- 检查文件权限

#### 2. API密钥未设置

**症状**: 大模型服务启动时报错"API密钥未设置"

**解决方案**:
```bash
# 检查.env文件
cat .env | grep API_KEY

# 确保llm目录下有.env文件
ls -la llm/.env

# 如果不存在，复制配置文件
cp .env llm/.env
```

#### 3. 服务响应缓慢

**症状**: 服务响应时间过长

**排查步骤**:
```bash
# 检查系统资源
./monitor_services.sh full

# 检查进程状态
ps aux | grep -E "(python|server)"

# 检查网络连接
netstat -an | grep -E ":(8000|8001|8080)"
```

**解决方案**:
- 重启相关服务
- 检查系统资源使用情况
- 优化代码性能
- 增加服务器资源

### 紧急处理流程

1. **立即响应** (5分钟内)
   - 确认故障范围
   - 启动应急预案
   - 通知相关人员

2. **快速恢复** (15分钟内)
   - 重启故障服务
   - 切换备用方案
   - 验证服务恢复

3. **根因分析** (1小时内)
   - 分析故障原因
   - 制定预防措施
   - 更新运维文档

## 性能优化

### 系统调优

```bash
# 增加文件描述符限制
ulimit -n 65536

# 优化TCP参数
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
```

### 应用优化

- 启用HTTP缓存
- 使用连接池
- 优化数据库查询
- 实施负载均衡

## 安全最佳实践

### 访问控制

- 限制服务绑定地址
- 配置防火墙规则
- 使用HTTPS加密
- 实施API限流

### 密钥管理

- 定期轮换API密钥
- 使用环境变量存储敏感信息
- 避免在代码中硬编码密钥
- 实施密钥访问审计

## 备份和恢复

### 备份策略

```bash
# 每日备份脚本
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份配置文件
cp -r devops/config $BACKUP_DIR/

# 备份日志文件
cp -r devops/logs $BACKUP_DIR/

# 备份数据库
cp *.db $BACKUP_DIR/ 2>/dev/null || true
```

### 恢复流程

1. 停止所有服务
2. 恢复配置文件
3. 恢复数据文件
4. 重启服务
5. 验证功能正常

## 联系信息

- **运维负责人**: DevOps工程师
- **紧急联系**: 7x24小时运维支持
- **技术支持**: 开发团队

## 更新日志

- **v1.0** (2025-08-19): 初始版本，包含基础运维功能
  - 服务启动/停止脚本
  - 服务监控脚本
  - 基础配置文件
  - 运维文档

---

*本文档由DevOps运维工程师维护，如有问题请及时反馈。*