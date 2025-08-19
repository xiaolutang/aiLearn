# 智能教学助手2.0 API契约设计文档

## 文档概述

本文档基于智能教学助手2.0产品需求和UI设计，定义了完整的API契约规范，包括接口定义、数据模型、错误处理等，为前后端分离开发提供标准化的接口规范。

### 版本信息
- **文档版本**: v2.0.0
- **API版本**: v2
- **创建日期**: 2024-12-15
- **最后更新**: 2024-12-15

### 技术栈
- **后端框架**: FastAPI / Spring Boot
- **数据库**: MySQL + Redis + MongoDB
- **认证方式**: JWT Token
- **API风格**: RESTful API
- **数据格式**: JSON

## 1. 通用规范

### 1.1 基础URL
```
开发环境: https://api-dev.aiteach.com/v2
测试环境: https://api-test.aiteach.com/v2
生产环境: https://api.aiteach.com/v2
```

### 1.2 请求头规范
```http
Content-Type: application/json
Authorization: Bearer {jwt_token}
X-Request-ID: {unique_request_id}
X-Client-Version: 2.0.0
```

### 1.3 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2024-12-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### 1.4 HTTP状态码规范
- **200**: 请求成功
- **201**: 创建成功
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 权限不足
- **404**: 资源不存在
- **500**: 服务器内部错误

### 1.5 分页规范
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## 2. 认证与用户管理

### 2.1 用户登录
```http
POST /auth/login
```

**请求参数:**
```json
{
  "username": "teacher001",
  "password": "password123",
  "login_type": "password", // password, sms, wechat
  "device_info": {
    "device_id": "device_123",
    "device_type": "web", // web, ios, android
    "user_agent": "Mozilla/5.0..."
  }
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 7200,
    "user_info": {
      "user_id": "user_123",
      "username": "teacher001",
      "real_name": "张老师",
      "email": "teacher001@school.com",
      "phone": "13800138000",
      "avatar": "https://cdn.aiteach.com/avatars/user_123.jpg",
      "role": "teacher",
      "permissions": ["lesson:create", "grade:manage"],
      "school_info": {
        "school_id": "school_001",
        "school_name": "示例中学",
        "school_type": "high_school"
      },
      "profile": {
        "subject": "biology",
        "grade_levels": ["grade_10", "grade_11", "grade_12"],
        "teaching_years": 8,
        "certification": "高级教师"
      }
    }
  }
}
```

### 2.2 获取用户信息
```http
GET /auth/profile
```

**响应数据:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": "user_123",
    "username": "teacher001",
    "real_name": "张老师",
    "email": "teacher001@school.com",
    "phone": "13800138000",
    "avatar": "https://cdn.aiteach.com/avatars/user_123.jpg",
    "role": "teacher",
    "status": "active",
    "last_login": "2024-12-15T08:30:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "school_info": {
      "school_id": "school_001",
      "school_name": "示例中学",
      "school_code": "SCH001",
      "school_type": "high_school",
      "region": "北京市海淀区"
    },
    "teaching_profile": {
      "subject": "biology",
      "grade_levels": ["grade_10", "grade_11", "grade_12"],
      "teaching_years": 8,
      "certification": "高级教师",
      "specialties": ["分子生物学", "细胞生物学"]
    },
    "preferences": {
      "theme": "light",
      "language": "zh-CN",
      "notification_settings": {
        "email": true,
        "sms": false,
        "push": true
      }
    }
  }
}
```

## 3. 工作台数据接口

### 3.1 工作台概览数据
```http
GET /dashboard/overview
```

**查询参数:**
```
time_range: string (today, week, month, quarter, year)
school_id: string (可选，管理员查看指定学校)
```

**响应数据:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "stats": {
      "student_count": {
        "total": 156,
        "trend": {
          "value": 12,
          "percentage": 8.3,
          "direction": "up",
          "period": "本月"
        }
      },
      "course_count": {
        "total": 24,
        "trend": {
          "value": 0,
          "percentage": 0,
          "direction": "stable",
          "period": "本周"
        }
      },
      "average_score": {
        "total": 87.5,
        "trend": {
          "value": 2.3,
          "percentage": 2.7,
          "direction": "up",
          "period": "本月"
        }
      },
      "preparation_hours": {
        "total": 42,
        "trend": {
          "value": 5,
          "percentage": 13.5,
          "direction": "up",
          "period": "本周"
        }
      }
    },
    "quick_actions": [
      {
        "id": "smart_prepare",
        "title": "智能备课",
        "description": "AI辅助生成教案和课件",
        "icon": "book-open",
        "color": "primary",
        "url": "/prepare/smart",
        "enabled": true
      },
      {
        "id": "experiment_design",
        "title": "实验设计",
        "description": "生物实验方案智能推荐",
        "icon": "microscope",
        "color": "secondary",
        "url": "/experiment/design",
        "enabled": true
      },
      {
        "id": "grade_analysis",
        "title": "成绩分析",
        "description": "学生学习情况深度分析",
        "icon": "chart-bar",
        "color": "accent",
        "url": "/grades/analysis",
        "enabled": true
      },
      {
        "id": "ai_qa",
        "title": "AI问答",
        "description": "智能教学问题解答",
        "icon": "brain",
        "color": "success",
        "url": "/ai/qa",
        "enabled": true
      }
    ]
  }
}
```

### 3.2 最近活动列表
```http
GET /dashboard/activities
```

**查询参数:**
```
page: int = 1
page_size: int = 10
activity_type: string (可选: lesson, grade, experiment, analysis)
```

**响应数据:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "activity_001",
        "type": "lesson_create",
        "title": "创建了新教案",
        "description": "《细胞的结构与功能》",
        "icon": "file-alt",
        "color": "primary",
        "created_at": "2024-12-15T08:30:00Z",
        "relative_time": "2小时前",
        "metadata": {
          "lesson_id": "lesson_001",
          "subject": "biology",
          "grade": "grade_11",
          "chapter": "第二章 细胞的基本结构"
        }
      },
      {
        "id": "activity_002",
        "type": "homework_grade",
        "title": "批改了作业",
        "description": "高二(3)班生物作业",
        "icon": "users",
        "color": "secondary",
        "created_at": "2024-12-15T06:30:00Z",
        "relative_time": "4小时前",
        "metadata": {
          "homework_id": "hw_001",
          "class_id": "class_003",
          "class_name": "高二(3)班",
          "student_count": 45,
          "graded_count": 45
        }
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 25,
      "total_pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 3.3 今日课程安排
```http
GET /dashboard/schedule
```

**查询参数:**
```
date: string (YYYY-MM-DD, 默认今天)
teacher_id: string (可选，管理员查看指定教师)
```

**响应数据:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "date": "2024-12-15",
    "day_of_week": "周五",
    "total_classes": 3,
    "current_class": {
      "class_id": "schedule_001",
      "is_current": true,
      "time_remaining": 1800 // 剩余秒数
    },
    "classes": [
      {
        "id": "schedule_001",
        "start_time": "08:00",
        "end_time": "08:45",
        "duration": 45,
        "subject": "生物",
        "topic": "细胞膜的结构与功能",
        "class_info": {
          "class_id": "class_003",
          "class_name": "高二(3)班",
          "student_count": 45,
          "classroom": "生物实验室1"
        },
        "lesson_info": {
          "lesson_id": "lesson_001",
          "chapter": "第二章",
          "section": "2.1",
          "preparation_status": "completed",
          "has_courseware": true,
          "has_experiment": false
        },
        "status": "current", // upcoming, current, completed, cancelled
        "actions": [
          {
            "type": "enter_classroom",
            "label": "进入课堂",
            "url": "/classroom/enter/schedule_001",
            "primary": true
          }
        ]
      },
      {
        "id": "schedule_002",
        "start_time": "10:00",
        "end_time": "10:45",
        "duration": 45,
        "subject": "生物",
        "topic": "蛋白质的结构与功能",
        "class_info": {
          "class_id": "class_001",
          "class_name": "高二(1)班",
          "student_count": 48,
          "classroom": "教学楼A201"
        },
        "lesson_info": {
          "lesson_id": "lesson_002",
          "chapter": "第三章",
          "section": "3.1",
          "preparation_status": "draft",
          "has_courseware": false,
          "has_experiment": false
        },
        "status": "upcoming",
        "actions": [
          {
            "type": "view_lesson",
            "label": "查看教案",
            "url": "/lessons/lesson_002",
            "primary": false
          }
        ]
      }
    ]
  }
}
```

## 4. 备课助手模块

### 4.1 教材智能分析
```http
POST /prepare/textbook/analyze
```

**请求参数:**
```json
{
  "textbook_info": {
    "publisher": "人民教育出版社",
    "subject": "biology",
    "grade": "grade_11",
    "volume": "必修1",
    "edition": "2019版"
  },
  "chapter": "第二章",
  "section": "2.1",
  "content": "细胞膜的结构与功能相关内容...",
  "analysis_options": {
    "include_knowledge_points": true,
    "include_difficulty_analysis": true,
    "include_teaching_suggestions": true,
    "include_experiment_recommendations": true
  }
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "分析完成",
  "data": {
    "analysis_id": "analysis_001",
    "textbook_info": {
      "publisher": "人民教育出版社",
      "subject": "biology",
      "grade": "grade_11",
      "volume": "必修1",
      "chapter": "第二章",
      "section": "2.1",
      "title": "细胞膜的结构与功能"
    },
    "knowledge_points": [
      {
        "id": "kp_001",
        "name": "细胞膜的分子结构",
        "level": "core", // core, important, general
        "difficulty": 3, // 1-5级难度
        "description": "理解细胞膜的磷脂双分子层结构",
        "prerequisites": ["生物大分子", "磷脂的结构"],
        "related_concepts": ["膜蛋白", "胆固醇"]
      },
      {
        "id": "kp_002",
        "name": "细胞膜的功能特性",
        "level": "important",
        "difficulty": 2,
        "description": "掌握细胞膜的选择透过性",
        "prerequisites": ["细胞膜结构"],
        "related_concepts": ["载体蛋白", "通道蛋白"]
      }
    ],
    "difficulty_analysis": {
      "overall_difficulty": 3,
      "cognitive_levels": {
        "remember": 0.2,
        "understand": 0.4,
        "apply": 0.3,
        "analyze": 0.1
      },
      "challenging_points": [
        {
          "point": "膜蛋白的功能分类",
          "reason": "概念抽象，需要结合具体实例理解",
          "suggestions": ["使用动画演示", "结合实际案例"]
        }
      ]
    },
    "teaching_objectives": {
      "knowledge_objectives": [
        "描述细胞膜的分子结构模型",
        "说明细胞膜的主要功能"
      ],
      "ability_objectives": [
        "能够运用结构与功能相适应的观点分析细胞膜",
        "培养观察和分析能力"
      ],
      "emotion_objectives": [
        "体会生物结构的精巧性",
        "培养科学探究精神"
      ]
    },
    "teaching_suggestions": {
      "key_points": ["细胞膜的结构模型", "选择透过性机理"],
      "difficult_points": ["膜蛋白的功能", "载体蛋白与通道蛋白的区别"],
      "teaching_methods": [
        {
          "method": "模型建构",
          "description": "引导学生构建细胞膜结构模型",
          "applicable_points": ["细胞膜结构"]
        },
        {
          "method": "实验探究",
          "description": "通过实验验证细胞膜的选择透过性",
          "applicable_points": ["膜的功能"]
        }
      ],
      "resources": [
        {
          "type": "animation",
          "title": "细胞膜结构动画",
          "url": "https://resources.aiteach.com/animations/cell_membrane.mp4",
          "duration": 180
        },
        {
          "type": "image",
          "title": "细胞膜电镜图",
          "url": "https://resources.aiteach.com/images/membrane_em.jpg",
          "description": "细胞膜的电子显微镜图像"
        }
      ]
    },
    "experiment_recommendations": [
      {
        "id": "exp_001",
        "title": "观察细胞膜的选择透过性",
        "type": "demonstration", // demonstration, group, individual
        "difficulty": 2,
        "duration": 30,
        "materials": ["红细胞悬液", "不同浓度NaCl溶液", "显微镜"],
        "procedure": [
          "制备不同浓度的NaCl溶液",
          "分别加入红细胞悬液",
          "显微镜观察细胞形态变化",
          "记录实验现象"
        ],
        "expected_results": "低渗溶液中红细胞胀破，高渗溶液中红细胞皱缩",
        "safety_notes": ["注意显微镜的正确使用", "小心处理玻璃器皿"]
      }
    ],
    "assessment_suggestions": {
      "formative_assessment": [
        "课堂提问检查理解程度",
        "小组讨论评价参与度"
      ],
      "summative_assessment": [
        "绘制细胞膜结构图",
        "解释选择透过性现象"
      ]
    },
    "ai_confidence": 0.92,
    "analysis_time": "2024-12-15T10:30:00Z"
  }
}
```

### 4.2 教学环节策划
```http
POST /prepare/lesson/plan
```

**请求参数:**
```json
{
  "lesson_info": {
    "subject": "biology",
    "grade": "grade_11",
    "topic": "细胞膜的结构与功能",
    "duration": 45,
    "class_size": 45,
    "student_level": "average" // low, average, high
  },
  "teaching_objectives": [
    "理解细胞膜的分子结构",
    "掌握细胞膜的功能特性"
  ],
  "available_resources": {
    "has_multimedia": true,
    "has_lab": true,
    "has_models": false
  },
  "preferences": {
    "teaching_style": "interactive", // traditional, interactive, inquiry
    "include_experiment": true,
    "include_group_work": true
  }
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "教学计划生成成功",
  "data": {
    "lesson_plan_id": "plan_001",
    "lesson_info": {
      "subject": "biology",
      "grade": "grade_11",
      "topic": "细胞膜的结构与功能",
      "duration": 45,
      "estimated_preparation_time": 60
    },
    "lesson_structure": {
      "phases": [
        {
          "phase": "导入",
          "duration": 5,
          "objectives": ["激发学习兴趣", "引出学习主题"],
          "activities": [
            {
              "type": "question",
              "content": "为什么细胞能够选择性地吸收和排出物质？",
              "duration": 2,
              "interaction_type": "whole_class"
            },
            {
              "type": "multimedia",
              "content": "播放细胞膜功能视频片段",
              "duration": 3,
              "resource_url": "https://resources.aiteach.com/videos/membrane_intro.mp4"
            }
          ],
          "teaching_tips": ["注意观察学生反应", "适时引导思考"]
        },
        {
          "phase": "新课讲授",
          "duration": 25,
          "objectives": ["理解细胞膜结构", "掌握功能机理"],
          "activities": [
            {
              "type": "explanation",
              "content": "细胞膜的分子组成和结构模型",
              "duration": 10,
              "key_points": ["磷脂双分子层", "膜蛋白分布"],
              "visual_aids": ["结构示意图", "3D模型动画"]
            },
            {
              "type": "group_discussion",
              "content": "分析膜蛋白的功能类型",
              "duration": 8,
              "group_size": 4,
              "discussion_points": ["载体蛋白", "通道蛋白", "受体蛋白"]
            },
            {
              "type": "demonstration",
              "content": "红细胞在不同溶液中的形态变化",
              "duration": 7,
              "materials": ["显微镜", "红细胞悬液", "不同浓度盐溶液"]
            }
          ]
        },
        {
          "phase": "巩固练习",
          "duration": 10,
          "objectives": ["检验理解程度", "强化重点知识"],
          "activities": [
            {
              "type": "exercise",
              "content": "绘制细胞膜结构图并标注主要成分",
              "duration": 6,
              "assessment_criteria": ["结构准确性", "标注完整性"]
            },
            {
              "type": "quiz",
              "content": "选择题：细胞膜的功能特性",
              "duration": 4,
              "question_count": 3
            }
          ]
        },
        {
          "phase": "总结作业",
          "duration": 5,
          "objectives": ["梳理知识要点", "布置课后任务"],
          "activities": [
            {
              "type": "summary",
              "content": "师生共同总结本节课重点内容",
              "duration": 3,
              "key_points": ["细胞膜结构模型", "选择透过性机理"]
            },
            {
              "type": "homework",
              "content": "完成课后练习题1-5题",
              "duration": 2,
              "estimated_time": 20
            }
          ]
        }
      ]
    },
    "resources_needed": [
      {
        "type": "multimedia",
        "name": "细胞膜结构动画",
        "url": "https://resources.aiteach.com/animations/membrane_structure.mp4",
        "usage_time": "新课讲授阶段"
      },
      {
        "type": "equipment",
        "name": "显微镜",
        "quantity": 1,
        "usage_time": "演示实验"
      },
      {
        "type": "material",
        "name": "红细胞悬液",
        "quantity": "10ml",
        "preparation_note": "提前准备新鲜血液样本"
      }
    ],
    "assessment_plan": {
      "formative_assessment": [
        {
          "method": "课堂观察",
          "focus": "学生参与度和理解程度",
          "timing": "全程"
        },
        {
          "method": "小组讨论评价",
          "focus": "合作能力和思维深度",
          "timing": "新课讲授阶段"
        }
      ],
      "summative_assessment": [
        {
          "method": "结构图绘制",
          "scoring_criteria": "准确性(40%) + 完整性(30%) + 美观性(30%)",
          "timing": "巩固练习阶段"
        }
      ]
    },
    "differentiation_strategies": {
      "for_advanced_students": [
        "提供膜蛋白功能的深入资料",
        "引导思考膜结构与疾病的关系"
      ],
      "for_struggling_students": [
        "提供结构图模板",
        "安排同伴互助"
      ]
    },
    "potential_challenges": [
      {
        "challenge": "学生对分子结构理解困难",
        "solution": "多使用直观的模型和动画",
        "prevention": "课前检查相关基础知识"
      }
    ],
    "ai_suggestions": [
      "建议在讲解膜蛋白时结合具体的生理功能实例",
      "可以增加学生动手制作膜结构模型的环节"
    ],
    "confidence_score": 0.89,
    "generated_at": "2024-12-15T10:35:00Z"
  }
}
```

## 5. 课堂AI助手模块

### 5.1 实时学情生成
```http
POST /classroom/learning-state/analyze
```

**请求参数:**
```json
{
  "session_id": "session_001",
  "question_data": {
    "question_id": "q_001",
    "question_text": "细胞膜的主要成分是什么？",
    "question_type": "multiple_choice", // multiple_choice, short_answer, essay
    "knowledge_points": ["细胞膜结构", "生物大分子"],
    "difficulty_level": 2,
    "cognitive_level": "understand"
  },
  "student_responses": [
    {
      "student_id": "student_001",
      "response": "磷脂和蛋白质",
      "response_time": 45, // 秒
      "confidence_level": 0.8,
      "submission_time": "2024-12-15T10:30:00Z"
    },
    {
      "student_id": "student_002",
      "response": "蛋白质",
      "response_time": 30,
      "confidence_level": 0.6,
      "submission_time": "2024-12-15T10:30:15Z"
    }
  ],
  "context": {
    "lesson_topic": "细胞膜的结构与功能",
    "current_phase": "新课讲授",
    "previous_questions": ["q_000"]
  }
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "学情分析完成",
  "data": {
    "analysis_id": "analysis_001",
    "session_id": "session_001",
    "question_analysis": {
      "question_id": "q_001",
      "total_responses": 45,
      "response_rate": 0.96,
      "average_response_time": 38.5,
      "correctness_distribution": {
        "correct": 32,
        "partially_correct": 8,
        "incorrect": 5
      },
      "common_errors": [
        {
          "error_type": "incomplete_answer",
          "count": 8,
          "description": "只提到蛋白质，遗漏磷脂",
          "suggested_intervention": "强调细胞膜的双分子层结构"
        }
      ]
    },
    "individual_analysis": [
      {
        "student_id": "student_001",
        "correctness": 1.0,
        "response_quality": "excellent",
        "knowledge_mastery": {
          "细胞膜结构": 0.9,
          "生物大分子": 0.85
        },
        "learning_state": "on_track",
        "confidence_match": true, // 自信度与实际表现是否匹配
        "attention_level": 0.9
      },
      {
        "student_id": "student_002",
        "correctness": 0.5,
        "response_quality": "needs_improvement",
        "knowledge_mastery": {
          "细胞膜结构": 0.6,
          "生物大分子": 0.7
        },
        "learning_state": "struggling",
        "confidence_match": false,
        "attention_level": 0.7
      }
    ],
    "class_insights": {
      "overall_understanding": 0.78,
      "engagement_level": 0.85,
      "difficulty_perception": "appropriate",
      "knowledge_gaps": [
        {
          "concept": "磷脂双分子层",
          "gap_percentage": 0.18,
          "priority": "high"
        }
      ],
      "learning_pace": "normal", // slow, normal, fast
      "attention_distribution": {
        "high": 0.7,
        "medium": 0.25,
        "low": 0.05
      }
    },
    "recommendations": {
      "immediate_actions": [
        {
          "type": "clarification",
          "priority": "high",
          "description": "重点强调磷脂在细胞膜中的重要性",
          "target_students": ["student_002", "student_015"],
          "estimated_time": 3
        }
      ],
      "next_question_suggestions": [
        {
          "question_type": "diagram_labeling",
          "focus": "细胞膜结构图标注",
          "difficulty_adjustment": 0, // -1降低, 0保持, 1提高
          "reason": "巩固结构认知"
        }
      ],
      "teaching_adjustments": [
        {
          "adjustment": "增加视觉辅助",
          "reason": "部分学生对抽象概念理解困难",
          "implementation": "使用细胞膜结构模型"
        }
      ]
    },
    "confidence_score": 0.91,
    "analysis_time": "2024-12-15T10:31:00Z"
  }
}
```

### 5.2 生物实验设计助手
```http
POST /classroom/experiment/design
```

**请求参数:**
```json
{
  "experiment_requirements": {
    "topic": "观察细胞膜的选择透过性",
    "grade_level": "grade_11",
    "student_count": 45,
    "duration": 45,
    "lab_conditions": {
      "has_microscopes": true,
      "microscope_count": 15,
      "has_centrifuge": false,
      "safety_level": "basic" // basic, intermediate, advanced
    },
    "learning_objectives": [
      "观察细胞膜的选择透过性现象",
      "理解渗透作用的原理",
      "培养实验操作技能"
    ],
    "available_materials": [
      "红细胞悬液", "NaCl溶液", "蒸馏水", "载玻片", "盖玻片"
    ]
  },
  "preferences": {
    "experiment_type": "group", // demonstration, group, individual
    "safety_priority": "high",
    "include_variations": true
  }
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "实验方案设计完成",
  "data": {
    "experiment_id": "exp_001",
    "basic_info": {
      "title": "观察细胞膜的选择透过性",
      "type": "观察实验",
      "difficulty_level": 2,
      "estimated_duration": 45,
      "group_size": 3,
      "group_count": 15
    },
    "learning_objectives": {
      "knowledge_objectives": [
        "理解细胞膜的选择透过性概念",
        "掌握渗透作用的基本原理"
      ],
      "skill_objectives": [
        "学会制作临时装片",
        "掌握显微镜的正确使用方法",
        "培养观察和记录能力"
      ],
      "attitude_objectives": [
        "培养严谨的科学态度",
        "增强团队合作意识"
      ]
    },
    "materials_list": {
      "per_group": [
        {"name": "显微镜", "quantity": 1, "specification": "光学显微镜"},
        {"name": "载玻片", "quantity": 6, "specification": "清洁干燥"},
        {"name": "盖玻片", "quantity": 6, "specification": "薄片"},
        {"name": "滴管", "quantity": 3, "specification": "塑料滴管"},
        {"name": "吸水纸", "quantity": 5, "specification": "滤纸"}
      ],
      "shared_materials": [
        {"name": "红细胞悬液", "quantity": "50ml", "preparation": "新鲜制备，浓度适中"},
        {"name": "0.9% NaCl溶液", "quantity": "100ml", "note": "等渗溶液"},
        {"name": "0.3% NaCl溶液", "quantity": "100ml", "note": "低渗溶液"},
        {"name": "3% NaCl溶液", "quantity": "100ml", "note": "高渗溶液"},
        {"name": "蒸馏水", "quantity": "200ml", "note": "对照组"}
      ]
    },
    "experimental_procedure": {
      "preparation_phase": {
        "duration": 10,
        "steps": [
          {
            "step": 1,
            "description": "检查显微镜各部件是否正常",
            "time": 2,
            "safety_notes": ["轻拿轻放显微镜"]
          },
          {
            "step": 2,
            "description": "准备载玻片和盖玻片，确保清洁",
            "time": 3,
            "tips": ["用擦镜纸轻擦玻片表面"]
          },
          {
            "step": 3,
            "description": "标记不同浓度溶液的容器",
            "time": 2,
            "importance": "避免混淆不同浓度溶液"
          },
          {
            "step": 4,
            "description": "分组领取实验材料",
            "time": 3,
            "organization": "按小组有序领取"
          }
        ]
      },
      "main_experiment": {
        "duration": 25,
        "procedures": [
          {
            "procedure_name": "对照组观察",
            "duration": 8,
            "steps": [
              {
                "step": 1,
                "description": "在载玻片上滴一滴0.9% NaCl溶液",
                "time": 1,
                "technique": "滴液应适量，避免过多"
              },
              {
                "step": 2,
                "description": "加入一滴红细胞悬液，轻轻混合",
                "time": 2,
                "technique": "用滴管轻轻搅拌混合"
              },
              {
                "step": 3,
                "description": "盖上盖玻片，注意避免气泡",
                "time": 2,
                "technique": "45度角缓慢放下盖玻片"
              },
              {
                "step": 4,
                "description": "显微镜观察并记录细胞形态",
                "time": 3,
                "observation_points": ["细胞形状", "细胞大小", "细胞膜完整性"]
              }
            ]
          },
          {
            "procedure_name": "低渗环境观察",
            "duration": 8,
            "steps": [
              {
                "step": 1,
                "description": "制作0.3% NaCl溶液装片",
                "time": 3,
                "reference": "参照对照组步骤1-3"
              },
              {
                "step": 2,
                "description": "观察并记录细胞变化",
                "time": 5,
                "expected_phenomenon": "细胞胀大，可能破裂",
                "observation_interval": "每分钟观察一次"
              }
            ]
          },
          {
            "procedure_name": "高渗环境观察",
            "duration": 9,
            "steps": [
              {
                "step": 1,
                "description": "制作3% NaCl溶液装片",
                "time": 3,
                "reference": "参照对照组步骤1-3"
              },
              {
                "step": 2,
                "description": "观察并记录细胞变化",
                "time": 6,
                "expected_phenomenon": "细胞皱缩变小",
                "comparison": "与对照组对比观察"
              }
            ]
          }
        ]
      },
      "data_analysis": {
        "duration": 10,
        "activities": [
          {
            "activity": "整理观察记录",
            "time": 4,
            "requirements": ["绘制细胞形态图", "记录变化过程"]
          },
          {
            "activity": "小组讨论分析",
            "time": 4,
            "discussion_points": ["不同环境下细胞变化的原因", "细胞膜选择透过性的体现"]
          },
          {
            "activity": "得出实验结论",
            "time": 2,
            "conclusion_framework": "细胞膜具有选择透过性，水分子可以自由通过..."
          }
        ]
      }
    },
    "safety_guidelines": [
      {
        "category": "设备安全",
        "guidelines": [
          "显微镜使用时避免强光直射眼睛",
          "移动显微镜时双手托举",
          "使用完毕后将显微镜复位"
        ]
      },
      {
        "category": "材料安全",
        "guidelines": [
          "红细胞悬液为生物材料，避免直接接触",
          "实验后及时清洗双手",
          "废液统一收集处理"
        ]
      },
      {
        "category": "操作安全",
        "guidelines": [
          "小心处理玻璃器皿，避免破损",
          "滴管使用后及时清洗",
          "保持实验台面整洁"
        ]
      }
    ],
    "assessment_criteria": {
      "operation_skills": {
        "weight": 0.4,
        "criteria": [
          "显微镜使用规范性(20分)",
          "装片制作质量(15分)",
          "观察记录完整性(15分)"
        ]
      },
      "scientific_thinking": {
        "weight": 0.4,
        "criteria": [
          "现象描述准确性(20分)",
          "原理解释正确性(20分)"
        ]
      },
      "collaboration": {
        "weight": 0.2,
        "criteria": [
          "团队合作表现(10分)",
          "实验态度认真性(10分)"
        ]
      }
    },
    "troubleshooting": [
      {
        "problem": "观察不到明显的细胞变化",
        "possible_causes": ["溶液浓度不合适", "观察时间过短", "细胞悬液浓度过低"],
        "solutions": ["调整溶液浓度", "延长观察时间", "增加细胞悬液浓度"]
      },
      {
        "problem": "显微镜下看不清细胞",
        "possible_causes": ["焦距未调好", "光线不合适", "装片质量差"],
        "solutions": ["重新调焦", "调节光圈和反光镜", "重新制作装片"]
      }
    ],
    "extension_activities": [
      {
        "activity": "探究不同细胞的渗透特性",
        "description": "比较植物细胞和动物细胞在渗透环境中的不同表现",
        "difficulty": "advanced"
      },
      {
        "activity": "设计定量实验",
        "description": "测量不同浓度溶液中细胞体积的变化",
        "difficulty": "advanced"
      }
    ],
    "ai_optimization_suggestions": [
      "建议在实验前进行细胞膜结构的复习",
      "可以增加实时拍照记录功能，便于后续分析",
      "建议准备备用材料，防止实验失败"
    ],
    "confidence_score": 0.94,
    "generated_at": "2024-12-15T10:40:00Z"
  }
}
```

## 6. 成绩管理模块

### 6.1 成绩录入
```http
POST /grades/import
```

**请求参数:**
```json
{
  "import_type": "excel", // excel, manual, ocr, voice
  "exam_info": {
    "exam_name": "期中考试",
    "exam_type": "midterm", // quiz, midterm, final, homework
    "subject": "biology",
    "exam_date": "2024-12-10",
    "full_score": 100,
    "class_ids": ["class_001", "class_002", "class_003"]
  },
  "grade_data": [
    {
      "student_id": "student_001",
      "student_name": "张三",
      "class_id": "class_001",
      "total_score": 85.5,
      "section_scores": {
        "选择题": 40,
        "填空题": 25,
        "简答题": 20.5
      },
      "knowledge_point_scores": {
        "细胞结构": 0.9,
        "细胞功能": 0.8,
        "细胞分裂": 0.7
      }
    }
  ],
  "validation_options": {
    "check_duplicates": true,
    "validate_score_range": true,
    "auto_correct": false
  }
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "成绩导入成功",
  "data": {
    "import_id": "import_001",
    "import_summary": {
      "total_records": 156,
      "successful_imports": 154,
      "failed_imports": 2,
      "duplicate_records": 1,
      "validation_errors": 1
    },
    "import_details": {
      "successful_records": [
        {
          "student_id": "student_001",
          "student_name": "张三",
          "total_score": 85.5,
          "status": "imported"
        }
      ],
      "failed_records": [
        {
          "student_id": "student_999",
          "student_name": "未知学生",
          "error_type": "student_not_found",
          "error_message": "学生信息不存在",
          "suggested_action": "检查学生ID或姓名"
        }
      ],
      "validation_warnings": [
        {
          "student_id": "student_002",
          "warning_type": "score_anomaly",
          "warning_message": "成绩异常偏高，请确认",
          "current_score": 98,
          "historical_average": 75
        }
      ]
    },
    "auto_analysis": {
      "class_statistics": {
        "class_001": {
          "average": 82.3,
          "median": 84.0,
          "std_deviation": 12.5,
          "pass_rate": 0.92
        }
      },
      "subject_analysis": {
        "overall_difficulty": "moderate",
        "challenging_topics": ["细胞分裂", "遗传规律"],
        "well_mastered_topics": ["细胞结构", "酶的特性"]
      }
    },
    "next_steps": [
      {
        "action": "review_failed_records",
        "description": "检查并修正导入失败的记录",
        "priority": "high"
      },
      {
        "action": "generate_analysis_report",
        "description": "生成详细的成绩分析报告",
        "priority": "medium"
      }
    ],
    "imported_at": "2024-12-15T10:45:00Z"
  }
}
```

### 6.2 成绩分析
```http
GET /grades/analysis
```

**查询参数:**
```
exam_id: string (必填)
analysis_type: string (class, grade, individual, comparative)
class_ids: string[] (可选)
student_ids: string[] (可选)
comparison_exams: string[] (可选，用于对比分析)
```

**响应数据:**
```json
{
  "code": 200,
  "message": "分析完成",
  "data": {
    "analysis_id": "analysis_001",
    "exam_info": {
      "exam_id": "exam_001",
      "exam_name": "期中考试",
      "subject": "biology",
      "exam_date": "2024-12-10",
      "total_participants": 156
    },
    "overall_statistics": {
      "descriptive_stats": {
        "mean": 82.3,
        "median": 84.0,
        "mode": 85.0,
        "std_deviation": 12.5,
        "variance": 156.25,
        "min": 45.0,
        "max": 98.0,
        "range": 53.0,
        "quartiles": {
          "q1": 75.0,
          "q2": 84.0,
          "q3": 91.0,
          "iqr": 16.0
        }
      },
      "distribution_analysis": {
        "histogram_data": [
          {"range": "40-50", "count": 2, "percentage": 1.3},
          {"range": "50-60", "count": 5, "percentage": 3.2},
          {"range": "60-70", "count": 15, "percentage": 9.6},
          {"range": "70-80", "count": 35, "percentage": 22.4},
          {"range": "80-90", "count": 65, "percentage": 41.7},
          {"range": "90-100", "count": 34, "percentage": 21.8}
        ],
        "normality_test": {
          "test_statistic": 0.95,
          "p_value": 0.23,
          "is_normal": true,
          "interpretation": "成绩分布接近正态分布"
        },
        "skewness": -0.15,
        "kurtosis": 0.32,
        "distribution_shape": "slightly_left_skewed"
      },
      "performance_levels": {
        "excellent": {"range": "90-100", "count": 34, "percentage": 21.8},
        "good": {"range": "80-89", "count": 65, "percentage": 41.7},
        "average": {"range": "70-79", "count": 35, "percentage": 22.4},
        "below_average": {"range": "60-69", "count": 15, "percentage": 9.6},
        "poor": {"range": "<60", "count": 7, "percentage": 4.5}
      }
    },
    "class_comparison": {
      "class_001": {
        "class_name": "高二(1)班",
        "student_count": 48,
        "average": 84.2,
        "pass_rate": 0.94,
        "rank": 1,
        "strengths": ["细胞结构", "酶的特性"],
        "weaknesses": ["遗传规律"]
      },
      "class_002": {
        "class_name": "高二(2)班",
        "student_count": 52,
        "average": 81.8,
        "pass_rate": 0.92,
        "rank": 2,
        "strengths": ["细胞分裂"],
        "weaknesses": ["细胞呼吸"]
      }
    },
    "knowledge_point_analysis": {
      "细胞结构": {
        "average_score": 0.89,
        "difficulty_level": "easy",
        "mastery_rate": 0.92,
        "common_errors": ["膜结构理解不深入"],
        "improvement_suggestions": ["加强结构与功能关系的理解"]
      },
      "细胞分裂": {
        "average_score": 0.72,
        "difficulty_level": "hard",
        "mastery_rate": 0.68,
        "common_errors": ["减数分裂过程混淆", "染色体行为理解错误"],
        "improvement_suggestions": ["增加过程图解练习", "强化概念区分"]
      }
    },
    "individual_insights": [
      {
        "student_id": "student_001",
        "student_name": "张三",
        "total_score": 85.5,
        "rank": 45,
        "percentile": 71.2,
        "performance_trend": "improving",
        "strengths": ["细胞结构", "酶的特性"],
        "weaknesses": ["遗传规律"],
        "recommendations": [
          "加强遗传题型练习",
          "复习孟德尔定律"
        ],
        "learning_style": "visual",
        "attention_points": ["概念理解需要更多实例"]
      }
    ],
    "ai_insights": {
      "overall_assessment": "本次考试整体表现良好，大部分学生掌握了基础知识",
      "teaching_effectiveness": 0.85,
      "curriculum_coverage": 0.92,
      "recommended_actions": [
        {
          "priority": "high",
          "action": "加强细胞分裂教学",
          "reason": "该知识点掌握率较低",
          "implementation": "增加动画演示和练习"
        },
        {
          "priority": "medium",
          "action": "个性化辅导",
          "reason": "部分学生存在明显薄弱环节",
          "target_students": ["student_025", "student_067"]
        }
      ],
      "future_focus": ["遗传规律", "细胞呼吸", "光合作用"]
    },
    "generated_at": "2024-12-15T10:50:00Z"
  }
}
```

### 6.3 个性化学习建议
```http
POST /grades/personalized-suggestions
```

**请求参数:**
```json
{
  "student_id": "student_001",
  "analysis_period": {
    "start_date": "2024-09-01",
    "end_date": "2024-12-15"
  },
  "include_subjects": ["biology"],
  "suggestion_types": ["study_plan", "resource_recommendation", "practice_exercises"]
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "个性化建议生成成功",
  "data": {
    "student_profile": {
      "student_id": "student_001",
      "student_name": "张三",
      "class_info": {
        "class_id": "class_001",
        "class_name": "高二(1)班"
      },
      "learning_characteristics": {
        "learning_style": "visual",
        "learning_pace": "moderate",
        "attention_span": "average",
        "preferred_difficulty": "moderate_to_high"
      },
      "academic_performance": {
        "overall_grade": "B+",
        "subject_ranking": 15,
        "class_ranking": 12,
        "trend": "improving"
      }
    },
    "knowledge_mastery_map": {
      "强项知识点": [
        {
          "topic": "细胞结构",
          "mastery_level": 0.92,
          "confidence": "high",
          "last_assessment": "2024-12-10"
        },
        {
          "topic": "酶的特性",
          "mastery_level": 0.88,
          "confidence": "high",
          "last_assessment": "2024-11-25"
        }
      ],
      "薄弱知识点": [
        {
          "topic": "遗传规律",
          "mastery_level": 0.65,
          "confidence": "low",
          "error_patterns": ["基因型推导错误", "概率计算失误"],
          "improvement_priority": "high"
        },
        {
          "topic": "细胞呼吸",
          "mastery_level": 0.72,
          "confidence": "medium",
          "error_patterns": ["反应过程混淆"],
          "improvement_priority": "medium"
        }
      ]
    },
    "personalized_study_plan": {
      "plan_duration": "4周",
      "weekly_schedule": [
        {
          "week": 1,
          "focus_topic": "遗传规律基础",
          "daily_tasks": [
            {
              "day": "周一",
              "task": "复习孟德尔定律基本概念",
              "duration": 30,
              "resources": ["教材第5章", "概念图"]
            },
            {
              "day": "周三",
              "task": "练习基因型推导",
              "duration": 45,
              "resources": ["练习册P45-50", "在线题库"]
            },
            {
              "day": "周五",
              "task": "概率计算专项训练",
              "duration": 40,
              "resources": ["专项练习题", "计算方法视频"]
            }
          ],
          "week_goal": "掌握基本遗传概念和简单推导",
          "assessment": "周末小测验"
        }
      ],
      "milestone_checkpoints": [
        {
          "checkpoint": "第2周末",
          "target": "遗传规律掌握度达到75%",
          "assessment_method": "专项测试"
        },
        {
          "checkpoint": "第4周末",
          "target": "遗传规律掌握度达到85%",
          "assessment_method": "综合测试"
        }
      ]
    },
    "resource_recommendations": {
      "视频资源": [
        {
          "title": "孟德尔定律详解",
          "url": "https://resources.aiteach.com/videos/mendel_laws.mp4",
          "duration": 25,
          "difficulty": "basic",
          "relevance_score": 0.95
        }
      ],
      "练习资源": [
        {
          "title": "遗传规律专项练习",
          "type": "interactive_exercises",
          "question_count": 50,
          "difficulty_range": "basic_to_intermediate",
          "estimated_time": 60
        }
      ],
      "参考资料": [
        {
          "title": "高中生物遗传学习指南",
          "type": "pdf",
          "pages": 45,
          "focus_areas": ["概念理解", "解题技巧"]
        }
      ]
    },
    "adaptive_strategies": {
      "学习方法建议": [
        "使用思维导图整理遗传概念关系",
        "通过实际案例理解抽象概念",
        "定期回顾和总结错题"
      ],
      "时间管理建议": [
        "每日固定30分钟生物学习时间",
        "周末进行知识点总结和测试",
        "利用碎片时间复习概念"
      ],
      "心理调适建议": [
        "设定小目标，逐步提升信心",
        "遇到困难及时寻求帮助",
        "保持积极的学习态度"
      ]
    },
    "progress_tracking": {
      "tracking_metrics": [
        "知识点掌握度变化",
        "练习正确率趋势",
        "学习时间统计",
        "自信心评估"
      ],
      "feedback_schedule": {
        "daily": "学习进度记录",
        "weekly": "知识掌握度评估",
        "monthly": "综合学习报告"
      }
    },
    "ai_coaching_tips": [
      "建议采用'理解-练习-应用'的学习循环",
      "遗传题目解答时先画出遗传图解",
      "多做不同类型的遗传题目，提高应变能力"
    ],
    "generated_at": "2024-12-15T10:55:00Z"
  }
}
```

## 7. AI问答模块

### 7.1 智能问答
```http
POST /ai/chat
```

**请求参数:**
```json
{
  "session_id": "chat_session_001",
  "message": {
    "content": "请解释一下细胞膜的选择透过性原理",
    "type": "text", // text, image, voice
    "context": {
      "subject": "biology",
      "grade": "grade_11",
      "topic": "细胞膜结构与功能",
      "user_level": "student" // student, teacher
    }
  },
  "preferences": {
    "response_style": "detailed", // simple, detailed, interactive
    "include_examples": true,
    "include_diagrams": true,
    "language_level": "high_school"
  }
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "回答生成成功",
  "data": {
    "response_id": "response_001",
    "session_id": "chat_session_001",
    "answer": {
      "main_content": "细胞膜的选择透过性是指细胞膜能够选择性地允许某些物质通过，而阻止另一些物质通过的特性。这种特性主要由以下几个方面决定：\n\n1. **膜的结构基础**\n细胞膜主要由磷脂双分子层构成，其中嵌入了各种蛋白质。磷脂分子具有亲水的头部和疏水的尾部，形成了一个相对封闭的屏障。\n\n2. **透过机制**\n- **自由扩散**：小分子物质如O₂、CO₂、H₂O等可以直接通过磷脂双分子层\n- **载体蛋白介导**：葡萄糖等大分子需要特定的载体蛋白协助\n- **通道蛋白介导**：离子如Na⁺、K⁺通过特定的离子通道\n\n3. **选择性的体现**\n细胞膜对不同物质的通透性不同，这种选择性保证了细胞内环境的稳定。",
      "key_points": [
        "磷脂双分子层是选择透过性的结构基础",
        "不同物质有不同的透过方式",
        "载体蛋白和通道蛋白起关键作用",
        "选择透过性维持细胞内环境稳定"
      ],
      "examples": [
        {
          "title": "红细胞在不同溶液中的表现",
          "description": "在低渗溶液中红细胞吸水胀破，在高渗溶液中失水皱缩，说明水分子可以自由通过细胞膜",
          "relevance": "演示了细胞膜对水分子的透过性"
        }
      ],
      "visual_aids": [
        {
          "type": "diagram",
          "title": "细胞膜选择透过性示意图",
          "url": "https://resources.aiteach.com/diagrams/membrane_permeability.svg",
          "description": "展示不同物质通过细胞膜的方式"
        }
      ]
    },
    "related_questions": [
      "载体蛋白和通道蛋白有什么区别？",
      "为什么大分子物质不能直接通过细胞膜？",
      "细胞膜的选择透过性如何维持细胞内环境稳定？"
    ],
    "learning_suggestions": [
      "建议结合实验观察加深理解",
      "可以绘制不同物质透过膜的示意图",
      "思考选择透过性在生物体中的意义"
    ],
    "confidence_score": 0.94,
    "response_time": 2.3,
    "generated_at": "2024-12-15T11:00:00Z"
  }
}
```

## 8. 通知与消息模块

### 8.1 获取通知列表
```http
GET /notifications
```

**查询参数:**
```
page: int = 1
page_size: int = 20
status: string (unread, read, all)
type: string (system, grade, homework, schedule, ai_insight)
priority: string (low, medium, high, urgent)
```

**响应数据:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "unread_count": 5,
    "items": [
      {
        "id": "notif_001",
        "type": "ai_insight",
        "priority": "medium",
        "title": "学情分析报告已生成",
        "content": "高二(1)班生物课学情分析报告已完成，发现3个重点关注学生",
        "status": "unread",
        "created_at": "2024-12-15T10:30:00Z",
        "action_url": "/reports/learning-state/report_001",
        "metadata": {
          "class_id": "class_001",
          "subject": "biology",
          "report_type": "learning_state"
        }
      },
      {
        "id": "notif_002",
        "type": "homework",
        "priority": "high",
        "title": "作业批改完成",
        "content": "《细胞膜结构》作业已完成AI批改，平均分78分",
        "status": "unread",
        "created_at": "2024-12-15T09:45:00Z",
        "action_url": "/homework/results/hw_001",
        "metadata": {
          "homework_id": "hw_001",
          "class_count": 3,
          "student_count": 145
        }
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 25,
      "total_pages": 2,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## 9. 文件管理模块

### 9.1 文件上传
```http
POST /files/upload
```

**请求参数:**
```json
{
  "file_type": "lesson_material", // lesson_material, homework, exam_paper, image, video
  "category": "courseware",
  "metadata": {
    "subject": "biology",
    "grade": "grade_11",
    "chapter": "第二章",
    "tags": ["细胞膜", "结构", "功能"]
  }
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "文件上传成功",
  "data": {
    "file_id": "file_001",
    "file_name": "细胞膜结构.pptx",
    "file_size": 2048576,
    "file_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "file_url": "https://cdn.aiteach.com/files/2024/12/15/file_001.pptx",
    "thumbnail_url": "https://cdn.aiteach.com/thumbnails/file_001.jpg",
    "upload_time": "2024-12-15T11:05:00Z",
    "ai_analysis": {
      "content_summary": "包含细胞膜结构图解和功能说明",
      "slide_count": 25,
      "estimated_duration": 30,
      "key_topics": ["磷脂双分子层", "膜蛋白", "选择透过性"]
    }
  }
}
```

## 10. 错误处理规范

### 10.1 错误响应格式
```json
{
  "code": 400,
  "message": "请求参数错误",
  "error": {
    "error_code": "INVALID_PARAMETER",
    "error_type": "validation_error",
    "details": [
      {
        "field": "student_id",
        "message": "学生ID不能为空",
        "code": "REQUIRED_FIELD"
      }
    ],
    "request_id": "req_123456789",
    "timestamp": "2024-12-15T11:10:00Z"
  }
}
```

### 10.2 常见错误码
- **1001**: 参数验证失败
- **1002**: 认证失败
- **1003**: 权限不足
- **1004**: 资源不存在
- **1005**: 重复操作
- **2001**: AI服务调用失败
- **2002**: 数据分析失败
- **2003**: 文件处理失败
- **5001**: 服务器内部错误
- **5002**: 数据库连接失败
- **5003**: 第三方服务不可用

---

## 附录

### A. 数据模型定义

#### A.1 用户模型
```typescript
interface User {
  user_id: string;
  username: string;
  real_name: string;
  email: string;
  phone: string;
  avatar: string;
  role: 'teacher' | 'student' | 'admin';
  status: 'active' | 'inactive' | 'suspended';
  school_id: string;
  created_at: string;
  updated_at: string;
}
```

#### A.2 课程模型
```typescript
interface Course {
  course_id: string;
  course_name: string;
  subject: string;
  grade: string;
  teacher_id: string;
  class_ids: string[];
  status: 'active' | 'completed' | 'cancelled';
  created_at: string;
}
```

### B. 接口版本管理

- **v2.0.0**: 初始版本，包含核心功能
- **v2.1.0**: 增加AI分析功能
- **v2.2.0**: 优化性能和用户体验

### C. 安全考虑

1. **数据加密**: 敏感数据传输使用HTTPS
2. **访问控制**: 基于角色的权限管理
3. **数据脱敏**: 日志中不记录敏感信息
4. **接口限流**: 防止恶意请求

---

**文档维护**: 本文档将根据产品迭代持续更新，确保API契约的准确性和完整性。