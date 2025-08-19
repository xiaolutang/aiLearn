# 智能教学助手 - 后端服务

这是智能教学助手的后端服务实现，提供高效成绩录入与分析、班级及年级成绩综合分析、学生个性化成绩分析及练题指导、辅导方案生成等功能。

## 技术栈

- **编程语言**: Python 3.8+
- **Web框架**: FastAPI
- **数据库**: SQLite（开发环境）、MySQL/PostgreSQL（生产环境）
- **ORM**: SQLAlchemy
- **API文档**: Swagger/OpenAPI
- **认证**: JWT (JSON Web Tokens)
- **数据处理**: Pandas、NumPy
- **大模型集成**: langchain、langgraph

## 项目结构

```
/learn05/service/
├── main.py                 # 主应用文件，整合所有功能模块
├── config.py               # 配置文件，存储应用程序的配置信息
├── database.py             # 数据库操作文件，包含数据库模型和操作函数
├── auth.py                 # 认证模块，处理用户认证和授权
├── llm_integration.py      # 大模型集成模块，处理与大模型的交互
├── grade_management.py     # 成绩管理模块，处理成绩的CRUD和分析
├── user_management.py      # 用户管理模块，处理用户的CRUD和权限管理
├── tutoring_plan.py        # 辅导方案模块，生成和管理个性化辅导方案
├── notification_system.py  # 通知系统模块，处理消息通知和提醒
├── utils.py                # 工具函数模块，提供通用的工具函数
├── test_api.py             # API测试文件，测试API接口的功能
├── requirements.txt        # 项目依赖文件
└── student_database.db     # SQLite数据库文件（开发环境）
```

## 核心功能

### 1. 用户认证与授权
- 用户注册、登录、注销
- JWT令牌管理
- 基于角色的权限控制系统（RBAC）
- 支持四种角色：超级管理员、教师、学生、家长

### 2. 成绩管理系统
- 成绩的录入、查询、更新、删除
- Excel批量导入/导出成绩数据
- 学生、班级、科目多维度的成绩统计分析
- 成绩趋势分析和排名计算

### 3. 数据分析功能
- 学生个性化成绩分析
- 班级及年级成绩综合分析
- 多维度数据统计（平均分、最高分、最低分、标准差等）
- 成绩分布图生成

### 4. 辅导方案生成
- 基于学生成绩分析的个性化辅导方案
- 学习资源推荐
- 辅导计划进度跟踪和管理
- 大模型辅助的辅导方案优化

### 5. 大模型集成
- 支持OpenAI和阿里云通义千问大模型
- 智能学情分析
- 自动生成教学建议
- 对话式学习助手

### 6. 通知系统
- 个性化消息通知
- 成绩提醒、辅导计划提醒
- 学习进度提醒
- 系统公告

## 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd /Users/tangxiaolu/project/PythonProject/aiLearn/learn05/service

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
# 执行数据库迁移脚本
python db_migration.py
```

### 3. 启动服务

```bash
# 启动开发服务器
python main.py
```

服务将在 `http://0.0.0.0:8000` 启动。

### 4. 访问API文档

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 环境变量配置

在生产环境中，建议通过环境变量配置以下参数：

- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: JWT密钥
- `LLM_API_KEY`: 大模型API密钥
- `ALIBABA_CLOUD_API_KEY`: 阿里云通义千问API密钥
- `ALIBABA_CLOUD_API_SECRET`: 阿里云通义千问API密钥
- `ENVIRONMENT`: 环境类型（development/testing/production）

## 测试

运行所有测试用例：

```bash
python run_tests.py
```

或者单独运行某个测试文件：

```bash
python -m tests.test_api
python -m tests.test_langgraph_sql_agent
python -m tests.test_workflow_nodes
```

## 部署指南

### 开发环境
- 使用SQLite数据库
- 本地FastAPI服务

### 生产环境
- 使用MySQL或PostgreSQL数据库
- 使用Docker容器化部署
- 配置Nginx反向代理
- 启用HTTPS

## 安全注意事项

1. 生产环境中务必修改默认的SECRET_KEY
2. 不要在代码中硬编码敏感信息
3. 使用环境变量配置敏感参数
4. 定期备份数据库
5. 配置适当的访问权限

## 贡献指南

1. Fork本项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目使用MIT许可证。

## 联系方式

如有任何问题或建议，请联系项目维护者。