# 智能教学助手 API 文档

## 概述

智能教学助手提供了完整的后端API服务，支持成绩管理、数据分析、AI辅导、备课上课等核心功能。本文档详细介绍了所有API接口的使用方法、参数说明和示例代码。

### 基础信息

- **API版本**: v1.0.0
- **基础URL**: `http://localhost:8000`
- **API前缀**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 快速开始

1. 启动服务：`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
2. 访问API文档：`http://localhost:8000/docs`
3. 获取API信息：`GET /api/info`

## 认证系统

### 用户登录

**接口**: `POST /api/v1/auth/login`

**描述**: 用户登录获取访问令牌

**请求参数**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "teacher001",
      "role": "teacher",
      "email": "teacher@example.com"
    }
  }
}
```

### 用户注册

**接口**: `POST /api/v1/auth/register`

**描述**: 注册新用户账户

**请求参数**:
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "role": "teacher|student|admin",
  "profile": {
    "name": "string",
    "phone": "string"
  }
}
```

### 获取用户信息

**接口**: `GET /api/v1/auth/profile`

**描述**: 获取当前用户的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "teacher001",
    "email": "teacher@example.com",
    "role": "teacher",
    "profile": {
      "name": "张老师",
      "phone": "13800138000",
      "avatar": "/uploads/avatars/teacher001.jpg"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T09:15:00Z"
  }
}
```

## 成绩管理系统

### 成绩录入

**接口**: `POST /api/v1/grades`

**描述**: 录入学生成绩

**请求参数**:
```json
{
  "student_id": 1,
  "exam_id": 1,
  "subject_id": 1,
  "score": 85.5,
  "full_score": 100,
  "exam_date": "2024-01-15"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "成绩录入成功",
  "data": {
    "id": 123,
    "student_id": 1,
    "student_name": "张三",
    "exam_id": 1,
    "exam_name": "期中考试",
    "subject_id": 1,
    "subject_name": "数学",
    "score": 85.5,
    "full_score": 100,
    "percentage": 85.5,
    "rank_in_class": 5,
    "created_at": "2024-01-15T14:30:00Z"
  }
}
```

### 批量导入成绩

**接口**: `POST /api/v1/grades/import/excel`

**描述**: 通过Excel文件批量导入成绩

**请求参数**: 
- Content-Type: `multipart/form-data`
- file: Excel文件
- class_id: 班级ID
- exam_id: 考试ID

**Excel格式要求**:
| 学号 | 姓名 | 语文 | 数学 | 英语 | 物理 | 化学 |
|------|------|------|------|------|------|------|
| 001  | 张三 | 85   | 92   | 78   | 88   | 90   |
| 002  | 李四 | 78   | 85   | 82   | 75   | 88   |

**响应示例**:
```json
{
  "success": true,
  "message": "成绩导入成功",
  "data": {
    "total_rows": 30,
    "success_count": 28,
    "error_count": 2,
    "errors": [
      {
        "row": 15,
        "student_number": "015",
        "error": "学生不存在"
      }
    ],
    "import_id": "import_20240115_143000"
  }
}
```

### 成绩查询

**接口**: `GET /api/v1/grades`

**描述**: 查询成绩列表

**查询参数**:
- `student_id`: 学生ID（可选）
- `class_id`: 班级ID（可选）
- `exam_id`: 考试ID（可选）
- `subject_id`: 科目ID（可选）
- `page`: 页码（默认1）
- `size`: 每页数量（默认20）
- `sort_by`: 排序字段（score, created_at等）
- `sort_order`: 排序方向（asc, desc）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 123,
        "student": {
          "id": 1,
          "name": "张三",
          "student_number": "001"
        },
        "exam": {
          "id": 1,
          "name": "期中考试",
          "date": "2024-01-15"
        },
        "subject": {
          "id": 1,
          "name": "数学"
        },
        "score": 85.5,
        "full_score": 100,
        "rank_in_class": 5,
        "created_at": "2024-01-15T14:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

### 成绩统计分析

**接口**: `GET /api/v1/grades/statistics`

**描述**: 获取成绩统计分析数据

**查询参数**:
- `class_id`: 班级ID
- `exam_id`: 考试ID
- `subject_id`: 科目ID（可选）
- `analysis_type`: 分析类型（class, subject, student）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_students": 45,
      "average_score": 78.5,
      "highest_score": 98,
      "lowest_score": 45,
      "pass_rate": 0.85,
      "excellent_rate": 0.35
    },
    "distribution": {
      "90-100": 8,
      "80-89": 15,
      "70-79": 12,
      "60-69": 7,
      "0-59": 3
    },
    "subject_analysis": [
      {
        "subject_id": 1,
        "subject_name": "数学",
        "average_score": 82.3,
        "difficulty_level": "中等",
        "improvement_suggestions": "加强几何题型练习"
      }
    ]
  }
}
```

## AI智能服务

### AI对话

**接口**: `POST /api/v1/ai/chat`

**描述**: 与AI助手进行对话

**请求参数**:
```json
{
  "message": "请分析一下张三同学的数学成绩趋势",
  "session_id": "session_123",
  "context": {
    "student_id": 1,
    "subject_id": 1,
    "analysis_type": "trend"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "response": "根据张三同学最近3次数学考试成绩分析，呈现稳步上升趋势。从75分提升到85分，主要在代数运算方面有显著进步。建议继续加强几何证明题的练习。",
    "session_id": "session_123",
    "suggestions": [
      "加强几何证明题练习",
      "巩固函数概念理解",
      "多做综合应用题"
    ],
    "confidence": 0.85,
    "created_at": "2024-01-15T15:30:00Z"
  }
}
```

### 学生个性化分析

**接口**: `POST /api/v1/ai/analyze/student/{student_id}`

**描述**: 对特定学生进行个性化学习分析

**路径参数**:
- `student_id`: 学生ID

**请求参数**:
```json
{
  "analysis_type": "comprehensive",
  "time_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
  },
  "subjects": [1, 2, 3],
  "include_recommendations": true
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "student": {
      "id": 1,
      "name": "张三",
      "class": "高一(1)班"
    },
    "overall_performance": {
      "average_score": 78.5,
      "rank_in_class": 15,
      "trend": "improving",
      "strength_subjects": ["数学", "物理"],
      "weak_subjects": ["英语", "化学"]
    },
    "detailed_analysis": {
      "learning_style": "视觉型学习者",
      "attention_span": "中等",
      "problem_solving_ability": "较强",
      "memory_retention": "良好"
    },
    "recommendations": [
      {
        "type": "study_method",
        "content": "建议使用思维导图整理知识点",
        "priority": "high"
      },
      {
        "type": "practice",
        "content": "每日英语听力练习30分钟",
        "priority": "medium"
      }
    ]
  }
}
```

### 生成学习计划

**接口**: `POST /api/v1/ai/generate/study-plan`

**描述**: 为学生生成个性化学习计划

**请求参数**:
```json
{
  "student_id": 1,
  "target_subjects": [1, 2],
  "time_frame": "1_month",
  "difficulty_level": "medium",
  "study_goals": [
    "提高数学成绩到90分以上",
    "掌握英语语法基础"
  ]
}
```

## 数据分析服务

### 班级成绩分析

**接口**: `GET /api/v1/analytics/class/{class_id}/performance`

**描述**: 获取班级整体成绩分析

**路径参数**:
- `class_id`: 班级ID

**查询参数**:
- `exam_id`: 考试ID（可选）
- `subject_id`: 科目ID（可选）
- `comparison_type`: 比较类型（previous_exam, grade_average）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "class_info": {
      "id": 1,
      "name": "高一(1)班",
      "total_students": 45
    },
    "performance_summary": {
      "average_score": 78.5,
      "median_score": 80,
      "standard_deviation": 12.3,
      "pass_rate": 0.85,
      "excellent_rate": 0.35
    },
    "subject_breakdown": [
      {
        "subject_id": 1,
        "subject_name": "数学",
        "average_score": 82.3,
        "pass_rate": 0.90,
        "difficulty_analysis": "中等偏难"
      }
    ],
    "trends": {
      "score_trend": "improving",
      "rank_changes": {
        "improved": 25,
        "declined": 8,
        "stable": 12
      }
    }
  }
}
```

### 年级对比分析

**接口**: `GET /api/v1/analytics/grade/{grade_level}/comparison`

**描述**: 获取年级各班级对比分析

**路径参数**:
- `grade_level`: 年级（如：1表示高一）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "grade_summary": {
      "grade_level": 1,
      "total_classes": 8,
      "total_students": 360,
      "average_score": 76.8
    },
    "class_rankings": [
      {
        "class_id": 1,
        "class_name": "高一(1)班",
        "average_score": 82.5,
        "rank": 1,
        "student_count": 45
      }
    ],
    "subject_comparison": {
      "数学": {
        "grade_average": 78.5,
        "best_class": "高一(1)班",
        "best_score": 85.2
      }
    }
  }
}
```

## 备课模块

### 创建教案

**接口**: `POST /api/v1/teaching-prep/lesson-plans`

**描述**: 创建新的教案

**请求参数**:
```json
{
  "title": "二次函数的图像与性质",
  "subject_id": 1,
  "grade_level": 1,
  "duration": 45,
  "objectives": [
    "理解二次函数的概念",
    "掌握二次函数图像的绘制方法"
  ],
  "content": {
    "introduction": "复习一次函数的相关知识",
    "main_content": "讲解二次函数的定义和性质",
    "practice": "完成课堂练习题",
    "summary": "总结本节课重点内容"
  },
  "materials": [
    "教材第3章",
    "多媒体课件",
    "练习册"
  ]
}
```

### 获取教案列表

**接口**: `GET /api/v1/teaching-prep/lesson-plans`

**描述**: 获取教师的教案列表

**查询参数**:
- `subject_id`: 科目ID（可选）
- `grade_level`: 年级（可选）
- `page`: 页码
- `size`: 每页数量

### 生成教学资源

**接口**: `POST /api/v1/teaching-prep/generate-resources`

**描述**: 基于教案内容生成教学资源

**请求参数**:
```json
{
  "lesson_plan_id": 1,
  "resource_types": ["exercises", "quiz", "slides"],
  "difficulty_level": "medium",
  "student_level": "high_school_grade_1"
}
```

## 上课模块

### 开始课堂

**接口**: `POST /api/v1/classroom/sessions`

**描述**: 开始新的课堂会话

**请求参数**:
```json
{
  "lesson_plan_id": 1,
  "class_id": 1,
  "scheduled_start": "2024-01-15T14:00:00Z",
  "duration": 45
}
```

### 课堂互动

**接口**: `POST /api/v1/classroom/sessions/{session_id}/interactions`

**描述**: 记录课堂互动活动

**请求参数**:
```json
{
  "interaction_type": "question",
  "content": "什么是二次函数的顶点？",
  "student_responses": [
    {
      "student_id": 1,
      "response": "函数图像的最高点或最低点",
      "is_correct": true
    }
  ]
}
```

### 课堂总结

**接口**: `PUT /api/v1/classroom/sessions/{session_id}/summary`

**描述**: 添加课堂总结

**请求参数**:
```json
{
  "summary": "本节课学生掌握情况良好，需要加强练习",
  "achievements": [
    "90%学生理解了二次函数概念",
    "完成了所有课堂练习"
  ],
  "next_steps": [
    "布置相关练习题",
    "下节课复习重点内容"
  ]
}
```

## 系统管理

### 健康检查

**接口**: `GET /health`

**描述**: 检查系统健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T16:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai_service": "available"
  },
  "performance": {
    "response_time": "15ms",
    "memory_usage": "45%",
    "cpu_usage": "12%"
  }
}
```

### 性能统计

**接口**: `GET /api/performance`

**描述**: 获取系统性能统计信息

**响应示例**:
```json
{
  "success": true,
  "data": {
    "middleware_status": {
      "initialized": true,
      "cache_manager": true,
      "performance_middleware": true
    },
    "performance": {
      "total_requests": 1250,
      "error_requests": 15,
      "slow_requests": 8,
      "average_response_time": 125.5
    },
    "cache": {
      "hit_rate": 0.85,
      "total_hits": 1065,
      "total_misses": 185
    },
    "rate_limit": {
      "total_requests": 1250,
      "blocked_requests": 5,
      "current_limits": {
        "default": "100/minute"
      }
    }
  }
}
```

## 错误处理

### 标准错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "具体错误信息"
  },
  "timestamp": "2024-01-15T16:30:00Z",
  "request_id": "req_123456789"
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| VALIDATION_ERROR | 422 | 参数验证失败 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| AI_SERVICE_ERROR | 503 | AI服务不可用 |

## SDK和示例代码

### Python SDK示例

```python
import requests
import json

class AILearnAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def login(self, username, password):
        """用户登录"""
        response = self.session.post(
            f'{self.base_url}/api/v1/auth/login',
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data['data']['access_token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            return data
        else:
            raise Exception(f'Login failed: {response.text}')
    
    def add_grade(self, student_id, exam_id, subject_id, score):
        """添加成绩"""
        response = self.session.post(
            f'{self.base_url}/api/v1/grades',
            json={
                'student_id': student_id,
                'exam_id': exam_id,
                'subject_id': subject_id,
                'score': score
            }
        )
        return response.json()
    
    def get_class_statistics(self, class_id, exam_id):
        """获取班级统计"""
        response = self.session.get(
            f'{self.base_url}/api/v1/grades/statistics',
            params={'class_id': class_id, 'exam_id': exam_id}
        )
        return response.json()
    
    def ai_chat(self, message, session_id=None, context=None):
        """AI对话"""
        response = self.session.post(
            f'{self.base_url}/api/v1/ai/chat',
            json={
                'message': message,
                'session_id': session_id,
                'context': context or {}
            }
        )
        return response.json()

# 使用示例
api = AILearnAPI('http://localhost:8001')

# 登录
login_result = api.login('teacher001', 'password123')
print(f"登录成功: {login_result['data']['user']['username']}")

# 添加成绩
grade_result = api.add_grade(
    student_id=1,
    exam_id=1,
    subject_id=1,
    score=85.5
)
print(f"成绩添加成功: {grade_result['data']['id']}")

# 获取班级统计
stats = api.get_class_statistics(class_id=1, exam_id=1)
print(f"班级平均分: {stats['data']['summary']['average_score']}")

# AI对话
chat_result = api.ai_chat(
    message="请分析一下这个班级的数学成绩情况",
    context={'class_id': 1, 'subject_id': 1}
)
print(f"AI回复: {chat_result['data']['response']}")
```

### JavaScript SDK示例

```javascript
class AILearnAPI {
    constructor(baseUrl, token = null) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async request(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (this.token) {
            options.headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        return await response.json();
    }
    
    async login(username, password) {
        const result = await this.request('POST', '/api/v1/auth/login', {
            username,
            password
        });
        
        if (result.success) {
            this.token = result.data.access_token;
        }
        
        return result;
    }
    
    async addGrade(studentId, examId, subjectId, score) {
        return await this.request('POST', '/api/v1/grades', {
            student_id: studentId,
            exam_id: examId,
            subject_id: subjectId,
            score: score
        });
    }
    
    async getGrades(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request('GET', `/api/v1/grades?${queryString}`);
    }
    
    async aiChat(message, sessionId = null, context = {}) {
        return await this.request('POST', '/api/v1/ai/chat', {
            message,
            session_id: sessionId,
            context
        });
    }
}

// 使用示例
const api = new AILearnAPI('http://localhost:8001');

// 登录
api.login('teacher001', 'password123')
    .then(result => {
        console.log('登录成功:', result.data.user.username);
        
        // 添加成绩
        return api.addGrade(1, 1, 1, 85.5);
    })
    .then(result => {
        console.log('成绩添加成功:', result.data.id);
        
        // 获取成绩列表
        return api.getGrades({ class_id: 1, exam_id: 1 });
    })
    .then(result => {
        console.log('成绩列表:', result.data.items);
        
        // AI对话
        return api.aiChat('请分析一下班级成绩情况', null, { class_id: 1 });
    })
    .then(result => {
        console.log('AI回复:', result.data.response);
    })
    .catch(error => {
        console.error('API调用失败:', error);
    });
```

## 部署和配置

### 环境变量配置

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=sqlite:///./ailearn.db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI服务配置
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_API_KEY=your-openai-api-key
AI_MODEL=gpt-3.5-turbo
AI_MAX_RETRIES=3
AI_CACHE_ENABLED=true
AI_CACHE_TTL=3600

# 性能优化配置
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=300
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
COMPRESSION_ENABLED=true

# 监控配置
MONITORING_PERFORMANCE=true
LOG_LEVEL=INFO
```

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "-m", "service.main"]
```

### 启动命令

```bash
# 开发环境
python -m service.main

# 生产环境
uvicorn service.main:app --host 0.0.0.0 --port 8001 --workers 4

# Docker启动
docker build -t ailearn-api .
docker run -p 8001:8001 --env-file .env ailearn-api
```

## 版本更新日志

### v1.0.0 (2024-01-15)

**新功能**:
- ✅ 完整的用户认证系统
- ✅ 成绩管理CRUD操作
- ✅ Excel批量导入导出
- ✅ 智能数据分析
- ✅ AI对话和个性化分析
- ✅ 备课和上课模块
- ✅ 性能优化中间件
- ✅ 完整的API文档

**技术特性**:
- 🚀 FastAPI + Python 3.11
- 🗄️ SQLAlchemy + SQLite/PostgreSQL
- 🔄 Redis缓存和会话管理
- 🤖 OpenAI GPT集成
- 📊 实时性能监控
- 🔒 JWT认证和权限控制
- 📈 自动API文档生成

## 技术支持

- **文档地址**: http://localhost:8000/docs
- **API测试**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health
- **性能监控**: http://localhost:8000/api/performance

---

**智能教学助手 - 让教学更智能，让学习更高效！**