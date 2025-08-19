# 智能教学助手部署指南

## 概述

本文档提供智能教学助手后端服务的完整部署指南，包括开发环境、生产环境和容器化部署方案。

## 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **操作系统**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 8GB RAM 或更多
- **存储**: 50GB SSD
- **网络**: 稳定的互联网连接（用于大模型API调用）

### 软件依赖
- **Python**: 3.8 或更高版本
- **Docker**: 20.10+ (容器化部署)
- **Docker Compose**: 1.29+ (容器化部署)
- **Git**: 版本控制

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-tutor-backend
```

### 2. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

### 3. 使用启动脚本（推荐）

```bash
# 使用交互式启动脚本
./start.sh
```

启动脚本会自动：
- 检查Python环境
- 安装依赖
- 创建必要目录
- 初始化数据库
- 运行测试
- 启动服务

## 开发环境部署

### 手动部署步骤

#### 1. 安装Python依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r service/requirements.txt
```

#### 2. 环境变量配置

编辑 `.env` 文件，设置以下关键配置：

```env
# 应用环境
ENVIRONMENT=development
DEBUG=true

# 数据库配置
DATABASE_URL=sqlite:///./data/ai_tutor.db

# 大模型API密钥
TONGYI_API_KEY=your_tongyi_api_key
OPENAI_API_KEY=your_openai_api_key

# JWT密钥
JWT_SECRET_KEY=your_jwt_secret_key
```

#### 3. 初始化数据库

```bash
# 创建数据目录
mkdir -p data

# 运行数据库初始化（如果有）
python scripts/init_db.py
```

#### 4. 启动服务

```bash
# 使用uvicorn启动
uvicorn service.main:app --reload --host 0.0.0.0 --port 8000

# 或使用Python模块方式
python -m uvicorn service.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. 验证部署

访问以下URL验证服务：
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **OpenAPI规范**: http://localhost:8000/openapi.json

## 生产环境部署

### 使用Docker部署（推荐）

#### 1. 构建镜像

```bash
# 构建Docker镜像
docker build -t ai-tutor-backend .
```

#### 2. 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f ai-tutor-backend
```

#### 3. 使用部署脚本

```bash
# 生产环境部署
./deploy.sh prod

# 查看服务状态
./deploy.sh status

# 查看日志
./deploy.sh logs
```

### 传统部署方式

#### 1. 系统服务配置

创建systemd服务文件 `/etc/systemd/system/ai-tutor.service`：

```ini
[Unit]
Description=AI Tutor Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai-tutor
Environment=PATH=/opt/ai-tutor/venv/bin
ExecStart=/opt/ai-tutor/venv/bin/uvicorn service.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 启动服务

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start ai-tutor

# 设置开机自启
sudo systemctl enable ai-tutor

# 查看服务状态
sudo systemctl status ai-tutor
```

#### 3. Nginx反向代理

使用提供的Nginx配置文件：

```bash
# 复制配置文件
sudo cp nginx/nginx.conf /etc/nginx/sites-available/ai-tutor

# 创建软链接
sudo ln -s /etc/nginx/sites-available/ai-tutor /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

## 监控和日志

### Prometheus + Grafana监控

#### 1. 启动监控服务

```bash
# 启动包含监控的完整环境
./deploy.sh monitoring
```

#### 2. 访问监控界面

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **AlertManager**: http://localhost:9093

#### 3. 导入仪表板

在Grafana中导入 `monitoring/grafana-dashboard.json` 文件。

### 日志管理

#### 日志文件位置

```
logs/
├── app.log              # 应用日志
├── error.log            # 错误日志
├── access.log           # 访问日志
└── llm.log              # 大模型调用日志
```

#### 日志轮转配置

创建 `/etc/logrotate.d/ai-tutor`：

```
/opt/ai-tutor/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload ai-tutor
    endscript
}
```

## 安全配置

### 1. 防火墙设置

```bash
# 允许HTTP和HTTPS
sudo ufw allow 80
sudo ufw allow 443

# 允许SSH（如果需要）
sudo ufw allow 22

# 启用防火墙
sudo ufw enable
```

### 2. SSL证书配置

#### 使用Let's Encrypt

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 环境变量安全

- 使用强密码和随机密钥
- 定期轮换API密钥
- 限制文件权限：`chmod 600 .env`

## 性能优化

### 1. 数据库优化

```bash
# 生产环境使用PostgreSQL
# 在.env中配置：
DATABASE_URL=postgresql://user:password@localhost/ai_tutor
```

### 2. 缓存配置

```bash
# 启动Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# 在.env中配置：
REDIS_URL=redis://localhost:6379
```

### 3. 负载均衡

使用多个应用实例和Nginx负载均衡：

```nginx
upstream ai_tutor_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

## 备份和恢复

### 1. 数据备份

```bash
# 数据库备份
./deploy.sh backup

# 手动备份
cp data/ai_tutor.db backups/ai_tutor_$(date +%Y%m%d_%H%M%S).db
```

### 2. 配置备份

```bash
# 备份配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env nginx/ monitoring/
```

### 3. 恢复流程

```bash
# 停止服务
./deploy.sh stop

# 恢复数据
cp backups/ai_tutor_backup.db data/ai_tutor.db

# 启动服务
./deploy.sh start
```

## 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 检查日志
./deploy.sh logs

# 检查端口占用
lsof -i :8000

# 检查环境变量
cat .env
```

#### 2. 数据库连接失败

```bash
# 检查数据库文件权限
ls -la data/

# 检查数据库URL配置
grep DATABASE_URL .env
```

#### 3. 大模型API调用失败

```bash
# 检查API密钥配置
grep API_KEY .env

# 检查网络连接
curl -I https://dashscope.aliyuncs.com
```

#### 4. 内存不足

```bash
# 检查内存使用
free -h

# 检查进程内存使用
ps aux | grep uvicorn

# 重启服务释放内存
./deploy.sh restart
```

### 日志分析

```bash
# 查看错误日志
tail -f logs/error.log

# 搜索特定错误
grep "ERROR" logs/app.log

# 分析访问模式
awk '{print $1}' logs/access.log | sort | uniq -c | sort -nr
```

## 更新和维护

### 1. 应用更新

```bash
# 拉取最新代码
git pull origin main

# 更新应用
./deploy.sh update
```

### 2. 依赖更新

```bash
# 更新Python依赖
pip install -r requirements.txt --upgrade

# 重建Docker镜像
docker-compose build --no-cache
```

### 3. 定期维护

```bash
# 清理日志
find logs/ -name "*.log" -mtime +30 -delete

# 清理临时文件
find temp/ -type f -mtime +7 -delete

# 数据库优化（如果使用PostgreSQL）
psql -d ai_tutor -c "VACUUM ANALYZE;"
```

## 联系支持

如果遇到部署问题，请：

1. 查看本文档的故障排除部分
2. 检查项目的GitHub Issues
3. 提供详细的错误日志和环境信息

---

**注意**: 在生产环境中，请确保：
- 使用HTTPS
- 定期备份数据
- 监控系统性能
- 及时更新安全补丁