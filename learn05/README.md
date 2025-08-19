# 智能教学助手后端系统

## 项目简介
智能教学助手是一款面向教育领域的智能辅助系统，旨在提供高效成绩录入与分析、班级及年级成绩综合分析、学生个性化成绩分析及练题指导、辅导方案生成等功能。本项目为该系统的后端实现。

## 技术栈
- **编程语言**: Python 3.8+
- **Web框架**: FastAPI
- **数据库**: SQLite (开发环境)
- **ORM**: SQLAlchemy
- **大模型集成**: 支持OpenAI、阿里云通义千问等
- **数据处理**: Pandas, NumPy
- **API文档**: Swagger/OpenAPI
- **身份认证**: JWT
- **服务器**: Uvicorn

## 功能模块

### 1. 用户认证与管理
- 教师/管理员注册登录
- 基于JWT的身份验证
- 角色权限管理

### 2. 成绩管理系统
- 单条成绩录入与管理
- Excel批量导入成绩
- 成绩查询与统计分析

### 3. 数据分析功能
- 班级整体成绩分析
- 学生个人成绩分析
- 成绩趋势分析
- 多维度数据可视化支持

### 4. 智能辅导方案
- 基于学生成绩数据生成个性化辅导方案
- 辅导资源推荐
- 辅导进度跟踪与评估

### 5. 智能问答系统
- 自然语言转SQL查询
- 数据结果解释与分析

## 快速开始

### 环境要求
- Python 3.8+
- pip 20.0+

### 安装步骤

1. **克隆项目代码**
```bash
# 假设已在项目目录中
cd /Users/tangxiaolu/project/PythonProject/aiLearn/learn05
```

2. **安装依赖**
```bash
pip install -r service/requirements.txt
```

3. **启动服务**
```bash
cd service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

或者使用启动脚本：
```bash
python start_app.py
```

服务将在 http://localhost:8000 启动

## API文档
服务启动后，可访问以下地址查看自动生成的API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
learn05/
├── service/                    # 服务端代码目录
│   ├── intelligent_teaching_assistant.py  # 主应用文件
│   ├── sql_connect.py          # 数据库连接工具
│   ├── workflow_nodes.py       # LangGraph工作流节点
│   ├── state.py                # 工作流状态定义
│   └── requirements.txt        # 项目依赖
├── sql_agent_client/           # 客户端代码目录
├── ui/                         # UI相关代码
├── 产品/                       # 产品文档
├── 研发/                       # 研发文档
├── start_app.py                # 启动脚本
└── README.md                   # 项目文档
```

## 核心API端点

### 用户认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 成绩管理
- `GET /api/grades` - 获取成绩列表
- `POST /api/grades` - 创建新成绩记录
- `POST /api/grades/batch-import` - 批量导入成绩（Excel）

### 数据分析
- `GET /api/grades/analysis/class/{class_id}` - 班级成绩分析
- `GET /api/grades/analysis/student/{student_id}` - 学生个人成绩分析
- `GET /api/performance` - 获取学生表现数据

### 辅导方案
- `POST /api/tutoring-plans/generate/{student_id}` - 生成个性化辅导方案

### 智能问答
- `POST /api/ai/query` - 自然语言查询接口

## 环境变量配置

可以通过环境变量配置以下参数：

- `JWT_SECRET_KEY` - JWT密钥（默认: "your-secret-key"）
- `LLM_MODEL` - 大模型名称（默认: "gpt-3.5-turbo"）
- `LLM_API_KEY` - 大模型API密钥
- `OPENAI_API_KEY` - OpenAI API密钥

## 部署说明

### 开发环境
直接运行 `python start_app.py` 启动服务

### 生产环境
建议使用Gunicorn作为WSGI服务器，并使用Nginx作为反向代理

```bash
# 安装生产依赖
pip install gunicorn uvicorn

# 使用Gunicorn启动服务
cd service
gunicorn -w 4 -k uvicorn.workers.UvicornWorker intelligent_teaching_assistant:app
```

## 注意事项

1. 首次运行时，系统会自动创建SQLite数据库文件 `student_database.db`
2. 如需使用真实的大模型API，请配置相应的API密钥
3. 批量导入成绩时，请确保Excel文件包含所需的列（student_id, subject_id, score, exam_date, exam_type）
4. 开发环境下，服务默认开启热重载功能，修改代码后会自动重启

## 日志
应用日志保存在项目根目录的 `app.log` 文件中

## License
[MIT](LICENSE)