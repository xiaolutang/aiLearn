#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手2.0 后端API实现示例

本文件展示了核心API接口的实现示例，基于FastAPI框架
包含完整的业务逻辑、数据处理和AI服务集成

@version 2.0.0
@date 2024-12-15
@author 智能教学助手后端团队
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import uuid
import logging
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 应用初始化 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("智能教学助手2.0 API服务启动")
    await init_services()
    yield
    # 关闭时清理
    logger.info("智能教学助手2.0 API服务关闭")
    await cleanup_services()

app = FastAPI(
    title="智能教学助手2.0 API",
    description="基于AI技术的智能教学助手后端服务",
    version="2.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全配置
security = HTTPBearer()

# ==================== 数据模型定义 ====================

class ResponseCode(Enum):
    """响应状态码"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

class BaseResponse(BaseModel):
    """统一响应格式"""
    code: int = Field(description="响应状态码")
    message: str = Field(description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class PaginationRequest(BaseModel):
    """分页请求参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")

class UserRole(str, Enum):
    """用户角色"""
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"

class User(BaseModel):
    """用户信息"""
    user_id: str
    username: str
    real_name: str
    email: str
    phone: str
    avatar: str
    role: UserRole
    status: str
    last_login: str
    created_at: str
    school_info: Dict[str, Any]
    teaching_profile: Optional[Dict[str, Any]] = None
    preferences: Dict[str, Any]

# ==================== 服务初始化 ====================

async def init_services():
    """初始化各种服务"""
    # 初始化数据库连接
    await init_database()
    # 初始化Redis缓存
    await init_redis()
    # 初始化AI服务
    await init_ai_services()
    # 初始化文件存储
    await init_file_storage()

async def cleanup_services():
    """清理服务资源"""
    # 关闭数据库连接
    await close_database()
    # 关闭Redis连接
    await close_redis()
    # 清理AI服务
    await cleanup_ai_services()

async def init_database():
    """初始化数据库连接"""
    logger.info("初始化数据库连接")
    # 这里应该初始化真实的数据库连接
    pass

async def close_database():
    """关闭数据库连接"""
    logger.info("关闭数据库连接")
    pass

async def init_redis():
    """初始化Redis缓存"""
    logger.info("初始化Redis缓存")
    pass

async def close_redis():
    """关闭Redis连接"""
    logger.info("关闭Redis连接")
    pass

async def init_ai_services():
    """初始化AI服务"""
    logger.info("初始化AI服务")
    pass

async def cleanup_ai_services():
    """清理AI服务"""
    logger.info("清理AI服务")
    pass

async def init_file_storage():
    """初始化文件存储"""
    logger.info("初始化文件存储")
    pass

# ==================== 认证中间件 ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """获取当前用户信息"""
    token = credentials.credentials
    
    # 验证JWT token
    try:
        # 这里应该实现真实的JWT验证逻辑
        user_data = await verify_jwt_token(token)
        return User(**user_data)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

async def verify_jwt_token(token: str) -> Dict[str, Any]:
    """验证JWT token"""
    # 模拟用户数据
    return {
        "user_id": "teacher_001",
        "username": "zhang_teacher",
        "real_name": "张老师",
        "email": "zhang@school.edu.cn",
        "phone": "13800138000",
        "avatar": "https://example.com/avatar.jpg",
        "role": "teacher",
        "status": "active",
        "last_login": datetime.now().isoformat(),
        "created_at": "2024-01-01T00:00:00",
        "school_info": {
            "school_id": "school_001",
            "school_name": "示例中学",
            "school_code": "DEMO001",
            "school_type": "中学",
            "region": "北京市海淀区"
        },
        "teaching_profile": {
            "subject": "生物",
            "grade_levels": ["高一", "高二", "高三"],
            "teaching_years": 10,
            "certification": "高级教师",
            "specialties": ["分子生物学", "遗传学"]
        },
        "preferences": {
            "theme": "light",
            "language": "zh-CN",
            "notification_settings": {
                "email": True,
                "sms": False,
                "push": True
            }
        }
    }

# ==================== 工具函数 ====================

def create_success_response(data: Any = None, message: str = "操作成功") -> BaseResponse:
    """创建成功响应"""
    return BaseResponse(
        code=ResponseCode.SUCCESS.value,
        message=message,
        data=data
    )

def create_error_response(code: int, message: str, data: Any = None) -> BaseResponse:
    """创建错误响应"""
    return BaseResponse(
        code=code,
        message=message,
        data=data
    )

# ==================== 用户认证接口 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    login_type: str = Field(default="password", description="登录类型")
    device_info: Dict[str, str] = Field(description="设备信息")

@app.post("/api/v1/auth/login", response_model=BaseResponse)
async def login(request: LoginRequest):
    """用户登录"""
    try:
        # 验证用户凭据
        user_data = await authenticate_user(request.username, request.password)
        
        if not user_data:
            return create_error_response(
                code=ResponseCode.UNAUTHORIZED.value,
                message="用户名或密码错误"
            )
        
        # 生成访问令牌
        access_token = await generate_access_token(user_data)
        refresh_token = await generate_refresh_token(user_data)
        
        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 3600,  # 1小时
            "user_info": user_data
        }
        
        return create_success_response(response_data, "登录成功")
        
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return create_error_response(
            code=ResponseCode.INTERNAL_ERROR.value,
            message="登录失败，请稍后重试"
        )

async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """验证用户凭据"""
    # 这里应该实现真实的用户验证逻辑
    # 查询数据库，验证密码哈希等
    
    # 模拟验证成功
    if username == "zhang_teacher" and password == "password123":
        return {
            "user_id": "teacher_001",
            "username": "zhang_teacher",
            "real_name": "张老师",
            "email": "zhang@school.edu.cn",
            "phone": "13800138000",
            "avatar": "https://example.com/avatar.jpg",
            "role": "teacher",
            "status": "active",
            "last_login": datetime.now().isoformat(),
            "created_at": "2024-01-01T00:00:00",
            "school_info": {
                "school_id": "school_001",
                "school_name": "示例中学",
                "school_code": "DEMO001",
                "school_type": "中学",
                "region": "北京市海淀区"
            },
            "teaching_profile": {
                "subject": "生物",
                "grade_levels": ["高一", "高二", "高三"],
                "teaching_years": 10,
                "certification": "高级教师",
                "specialties": ["分子生物学", "遗传学"]
            },
            "preferences": {
                "theme": "light",
                "language": "zh-CN",
                "notification_settings": {
                    "email": True,
                    "sms": False,
                    "push": True
                }
            }
        }
    return None

async def generate_access_token(user_data: Dict[str, Any]) -> str:
    """生成访问令牌"""
    # 这里应该实现真实的JWT生成逻辑
    return f"access_token_{user_data['user_id']}_{int(datetime.now().timestamp())}"

async def generate_refresh_token(user_data: Dict[str, Any]) -> str:
    """生成刷新令牌"""
    # 这里应该实现真实的刷新令牌生成逻辑
    return f"refresh_token_{user_data['user_id']}_{int(datetime.now().timestamp())}"

@app.get("/api/v1/auth/user", response_model=BaseResponse)
async def get_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return create_success_response(current_user.dict(), "获取用户信息成功")

# ==================== 工作台接口 ====================

@app.get("/api/v1/dashboard/overview", response_model=BaseResponse)
async def get_dashboard_overview(current_user: User = Depends(get_current_user)):
    """获取工作台概览数据"""
    try:
        # 获取统计数据
        stats = await get_dashboard_stats(current_user.user_id)
        
        # 获取快速操作
        quick_actions = await get_quick_actions(current_user.role)
        
        overview_data = {
            "stats": stats,
            "quick_actions": quick_actions
        }
        
        return create_success_response(overview_data, "获取工作台数据成功")
        
    except Exception as e:
        logger.error(f"获取工作台数据失败: {str(e)}")
        return create_error_response(
            code=ResponseCode.INTERNAL_ERROR.value,
            message="获取工作台数据失败"
        )

async def get_dashboard_stats(user_id: str) -> Dict[str, Any]:
    """获取工作台统计数据"""
    # 模拟统计数据
    return {
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
            "total": 8,
            "trend": {
                "value": 2,
                "percentage": 33.3,
                "direction": "up",
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
            "total": 24.5,
            "trend": {
                "value": 3.2,
                "percentage": 15.0,
                "direction": "up",
                "period": "本周"
            }
        }
    }

async def get_quick_actions(role: str) -> List[Dict[str, Any]]:
    """获取快速操作"""
    if role == "teacher":
        return [
            {
                "id": "smart_lesson_prep",
                "title": "智能备课",
                "description": "AI辅助教学设计",
                "icon": "book-open",
                "color": "primary",
                "url": "/lesson-prep",
                "enabled": True
            },
            {
                "id": "experiment_design",
                "title": "实验设计",
                "description": "生物实验方案生成",
                "icon": "flask",
                "color": "secondary",
                "url": "/experiment-design",
                "enabled": True
            },
            {
                "id": "grade_analysis",
                "title": "成绩分析",
                "description": "智能成绩统计分析",
                "icon": "chart-bar",
                "color": "accent",
                "url": "/grade-analysis",
                "enabled": True
            },
            {
                "id": "ai_qa",
                "title": "AI问答",
                "description": "教学问题智能解答",
                "icon": "chat",
                "color": "success",
                "url": "/ai-chat",
                "enabled": True
            }
        ]
    return []

@app.get("/api/v1/dashboard/activities", response_model=BaseResponse)
async def get_recent_activities(
    pagination: PaginationRequest = Depends(),
    current_user: User = Depends(get_current_user)
):
    """获取最近活动列表"""
    try:
        activities = await get_user_activities(current_user.user_id, pagination)
        return create_success_response(activities, "获取活动列表成功")
        
    except Exception as e:
        logger.error(f"获取活动列表失败: {str(e)}")
        return create_error_response(
            code=ResponseCode.INTERNAL_ERROR.value,
            message="获取活动列表失败"
        )

async def get_user_activities(user_id: str, pagination: PaginationRequest) -> Dict[str, Any]:
    """获取用户活动记录"""
    # 模拟活动数据
    activities = [
        {
            "id": "activity_001",
            "type": "lesson_create",
            "title": "创建教案",
            "description": "为《细胞的分子组成》创建了新教案",
            "icon": "document-add",
            "color": "blue",
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "relative_time": "2小时前",
            "metadata": {
                "lesson_id": "lesson_001",
                "subject": "生物",
                "grade": "高一"
            }
        },
        {
            "id": "activity_002",
            "type": "homework_grade",
            "title": "批改作业",
            "description": "完成了高一(3)班的生物作业批改",
            "icon": "check-circle",
            "color": "green",
            "created_at": (datetime.now() - timedelta(hours=5)).isoformat(),
            "relative_time": "5小时前",
            "metadata": {
                "class_id": "class_003",
                "homework_count": 32
            }
        },
        {
            "id": "activity_003",
            "type": "grade_analysis",
            "title": "查看成绩报告",
            "description": "分析了期中考试成绩数据",
            "icon": "chart-bar",
            "color": "purple",
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "relative_time": "1天前",
            "metadata": {
                "exam_id": "exam_001",
                "class_count": 3
            }
        },
        {
            "id": "activity_004",
            "type": "experiment_design",
            "title": "设计实验方案",
            "description": "为《酶的特性》设计了实验方案",
            "icon": "beaker",
            "color": "orange",
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "relative_time": "2天前",
            "metadata": {
                "experiment_id": "exp_001",
                "topic": "酶的特性"
            }
        }
    ]
    
    # 分页处理
    start_idx = (pagination.page - 1) * pagination.page_size
    end_idx = start_idx + pagination.page_size
    paginated_activities = activities[start_idx:end_idx]
    
    return {
        "items": paginated_activities,
        "pagination": {
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total": len(activities),
            "total_pages": (len(activities) + pagination.page_size - 1) // pagination.page_size,
            "has_next": end_idx < len(activities),
            "has_prev": pagination.page > 1
        }
    }

@app.get("/api/v1/dashboard/schedule", response_model=BaseResponse)
async def get_daily_schedule(
    date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取今日课程安排"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        schedule = await get_teacher_schedule(current_user.user_id, date)
        return create_success_response(schedule, "获取课程安排成功")
        
    except Exception as e:
        logger.error(f"获取课程安排失败: {str(e)}")
        return create_error_response(
            code=ResponseCode.INTERNAL_ERROR.value,
            message="获取课程安排失败"
        )

async def get_teacher_schedule(user_id: str, date: str) -> Dict[str, Any]:
    """获取教师课程安排"""
    # 模拟课程安排数据
    schedule_date = datetime.strptime(date, "%Y-%m-%d")
    
    classes = [
        {
            "id": "schedule_001",
            "start_time": "08:00",
            "end_time": "08:45",
            "duration": 45,
            "subject": "生物",
            "topic": "细胞的分子组成",
            "class_info": {
                "class_id": "class_001",
                "class_name": "高一(1)班",
                "student_count": 42,
                "classroom": "生物实验室A"
            },
            "lesson_info": {
                "lesson_id": "lesson_001",
                "chapter": "第一章",
                "section": "第一节",
                "preparation_status": "completed",
                "has_courseware": True,
                "has_experiment": True
            },
            "status": "completed",
            "actions": [
                {
                    "type": "view_lesson",
                    "label": "查看教案",
                    "url": "/lesson/lesson_001",
                    "primary": True
                },
                {
                    "type": "start_class",
                    "label": "开始上课",
                    "url": "/classroom/start/schedule_001",
                    "primary": False
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
                "class_id": "class_002",
                "class_name": "高一(2)班",
                "student_count": 38,
                "classroom": "生物实验室B"
            },
            "lesson_info": {
                "lesson_id": "lesson_002",
                "chapter": "第一章",
                "section": "第二节",
                "preparation_status": "completed",
                "has_courseware": True,
                "has_experiment": False
            },
            "status": "current",
            "actions": [
                {
                    "type": "view_lesson",
                    "label": "查看教案",
                    "url": "/lesson/lesson_002",
                    "primary": False
                },
                {
                    "type": "start_class",
                    "label": "开始上课",
                    "url": "/classroom/start/schedule_002",
                    "primary": True
                }
            ]
        },
        {
            "id": "schedule_003",
            "start_time": "14:00",
            "end_time": "14:45",
            "duration": 45,
            "subject": "生物",
            "topic": "糖类和脂质",
            "class_info": {
                "class_id": "class_003",
                "class_name": "高一(3)班",
                "student_count": 40,
                "classroom": "生物实验室A"
            },
            "lesson_info": {
                "lesson_id": "lesson_003",
                "chapter": "第一章",
                "section": "第三节",
                "preparation_status": "draft",
                "has_courseware": False,
                "has_experiment": True
            },
            "status": "upcoming",
            "actions": [
                {
                    "type": "prepare_lesson",
                    "label": "完善教案",
                    "url": "/lesson-prep/lesson_003",
                    "primary": True
                },
                {
                    "type": "view_lesson",
                    "label": "查看教案",
                    "url": "/lesson/lesson_003",
                    "primary": False
                }
            ]
        }
    ]
    
    # 确定当前课程
    current_time = datetime.now().time()
    current_class = None
    
    for cls in classes:
        start_time = datetime.strptime(cls["start_time"], "%H:%M").time()
        end_time = datetime.strptime(cls["end_time"], "%H:%M").time()
        
        if start_time <= current_time <= end_time:
            current_class = {
                "class_id": cls["id"],
                "is_current": True,
                "time_remaining": int((datetime.combine(schedule_date, end_time) - 
                                     datetime.combine(schedule_date, current_time)).total_seconds() / 60)
            }
            break
    
    return {
        "date": date,
        "day_of_week": schedule_date.strftime("%A"),
        "total_classes": len(classes),
        "current_class": current_class,
        "classes": classes
    }

# ==================== 备课助手接口 ====================

class TextbookAnalysisRequest(BaseModel):
    """教材分析请求"""
    textbook_info: Dict[str, str] = Field(description="教材信息")
    analysis_options: Dict[str, bool] = Field(description="分析选项")

@app.post("/api/v1/lesson-prep/textbook-analysis", response_model=BaseResponse)
async def analyze_textbook(
    request: TextbookAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """教材智能分析"""
    try:
        # 调用AI服务进行教材分析
        analysis_result = await perform_textbook_analysis(request, current_user.user_id)
        
        return create_success_response(analysis_result, "教材分析完成")
        
    except Exception as e:
        logger.error(f"教材分析失败: {str(e)}")
        return create_error_response(
            code=ResponseCode.INTERNAL_ERROR.value,
            message="教材分析失败，请稍后重试"
        )

async def perform_textbook_analysis(request: TextbookAnalysisRequest, user_id: str) -> Dict[str, Any]:
    """执行教材分析"""
    # 模拟AI分析过程
    await asyncio.sleep(2)  # 模拟AI处理时间
    
    # 模拟分析结果
    return {
        "analysis_id": str(uuid.uuid4()),
        "textbook_info": request.textbook_info,
        "knowledge_points": [
            {
                "id": "kp_001",
                "name": "蛋白质的结构",
                "level": "core",
                "difficulty": 3,
                "description": "蛋白质的一级、二级、三级、四级结构",
                "prerequisites": ["氨基酸结构", "化学键类型"],
                "related_concepts": ["酶的结构", "抗体结构"]
            },
            {
                "id": "kp_002",
                "name": "蛋白质的功能",
                "level": "important",
                "difficulty": 2,
                "description": "蛋白质在生物体内的各种功能",
                "prerequisites": ["蛋白质结构"],
                "related_concepts": ["酶催化", "免疫反应"]
            }
        ],
        "difficulty_analysis": {
            "overall_difficulty": 3,
            "cognitive_levels": {
                "remember": 20,
                "understand": 35,
                "apply": 30,
                "analyze": 15
            },
            "challenging_points": [
                {
                    "point": "蛋白质四级结构",
                    "reason": "概念抽象，空间想象要求高",
                    "suggestions": ["使用3D模型演示", "提供多个实例"]
                }
            ]
        },
        "teaching_objectives": {
            "knowledge_objectives": [
                "理解蛋白质的结构层次",
                "掌握蛋白质的主要功能"
            ],
            "ability_objectives": [
                "能够分析蛋白质结构与功能的关系",
                "培养空间想象能力"
            ],
            "emotion_objectives": [
                "感受生物分子的精妙结构",
                "培养科学探究精神"
            ]
        },
        "teaching_suggestions": {
            "key_points": ["蛋白质结构层次", "结构与功能关系"],
            "difficult_points": ["四级结构概念", "空间构象变化"],
            "teaching_methods": [
                {
                    "method": "模型演示法",
                    "description": "使用分子模型展示蛋白质结构",
                    "applicable_points": ["结构层次", "空间构象"]
                }
            ],
            "resources": [
                {
                    "type": "animation",
                    "title": "蛋白质折叠动画",
                    "url": "https://example.com/protein-folding.mp4",
                    "duration": 180,
                    "description": "展示蛋白质折叠过程"
                }
            ]
        },
        "experiment_recommendations": [
            {
                "id": "exp_001",
                "title": "蛋白质的检测",
                "type": "group",
                "difficulty": 2,
                "duration": 45,
                "materials": ["双缩脲试剂", "蛋白质溶液", "试管"],
                "procedure": [
                    "取蛋白质溶液2ml",
                    "加入双缩脲试剂",
                    "观察颜色变化"
                ],
                "expected_results": "溶液呈紫色",
                "safety_notes": ["小心使用化学试剂"]
            }
        ],
        "assessment_suggestions": {
            "formative_assessment": ["课堂提问", "小组讨论"],
            "summative_assessment": ["单元测试", "实验报告"]
        },
        "ai_confidence": 0.92,
        "analysis_time": datetime.now().isoformat()
    }

class LessonPlanRequest(BaseModel):
    """教学计划请求"""
    lesson_info: Dict[str, Any] = Field(description="课程信息")
    teaching_preferences: Dict[str, Any] = Field(description="教学偏好")
    class_characteristics: Dict[str, Any] = Field(description="班级特点")

@app.post("/api/v1/lesson-prep/lesson-plan", response_model=BaseResponse)
async def generate_lesson_plan(
    request: LessonPlanRequest,
    current_user: User = Depends(get_current_user)
):
    """生成教学计划"""
    try:
        # 调用AI服务生成教学计划
        lesson_plan = await create_lesson_plan(request, current_user.user_id)
        
        return create_success_response(lesson_plan, "教学计划生成完成")
        
    except Exception as e:
        logger.error(f"教学计划生成失败: {str(e)}")
        return create_error_response(
            code=ResponseCode.INTERNAL_ERROR.value,
            message="教学计划生成失败，请稍后重试"
        )

async def create_lesson_plan(request: LessonPlanRequest, user_id: str) -> Dict[str, Any]:
    """创建教学计划"""
    # 模拟AI生成过程
    await asyncio.sleep(3)  # 模拟AI处理时间
    
    # 模拟教学计划结果
    return {
        "lesson_plan_id": str(uuid.uuid4()),
        "lesson_info": {
            "subject": request.lesson_info.get("subject", "生物"),
            "grade": request.lesson_info.get("grade", "高一"),
            "topic": request.lesson_info.get("topic", "蛋白质的结构与功能"),
            "duration": 45,
            "estimated_preparation_time": 120
        },
        "lesson_structure": {
            "phases": [
                {
                    "phase": "导入阶段",
                    "duration": 5,
                    "objectives": ["激发学习兴趣", "引出学习主题"],
                    "activities": [
                        {
                            "type": "question",
                            "content": "同学们知道头发、指甲的主要成分是什么吗？",
                            "duration": 2,
                            "interaction_type": "师生问答"
                        },
                        {
                            "type": "multimedia",
                            "content": "播放蛋白质3D结构动画",
                            "duration": 3,
                            "resource_url": "https://example.com/protein-3d.mp4"
                        }
                    ],
                    "teaching_tips": ["注意观察学生反应", "适时引导思考"]
                },
                {
                    "phase": "新课讲授",
                    "duration": 25,
                    "objectives": ["理解蛋白质结构层次", "掌握结构与功能关系"],
                    "activities": [
                        {
                            "type": "explanation",
                            "content": "讲解蛋白质一级结构",
                            "duration": 8,
                            "key_points": ["氨基酸序列", "肽键连接"],
                            "visual_aids": ["分子模型", "结构图"]
                        },
                        {
                            "type": "demonstration",
                            "content": "演示蛋白质折叠过程",
                            "duration": 7,
                            "materials": ["分子模型", "动画视频"]
                        },
                        {
                            "type": "group_discussion",
                            "content": "讨论蛋白质结构与功能的关系",
                            "duration": 10,
                            "group_size": 4,
                            "discussion_points": ["酶的活性中心", "抗体的特异性"]
                        }
                    ]
                },
                {
                    "phase": "巩固练习",
                    "duration": 10,
                    "objectives": ["巩固所学知识", "检验学习效果"],
                    "activities": [
                        {
                            "type": "exercise",
                            "content": "完成蛋白质结构相关练习题",
                            "duration": 8,
                            "assessment_criteria": ["准确性", "完整性"]
                        },
                        {
                            "type": "quiz",
                            "content": "快速问答检测",
                            "duration": 2,
                            "question_count": 3
                        }
                    ]
                },
                {
                    "phase": "总结作业",
                    "duration": 5,
                    "objectives": ["总结重点内容", "布置课后任务"],
                    "activities": [
                        {
                            "type": "summary",
                            "content": "总结蛋白质结构层次和功能",
                            "duration": 3
                        },
                        {
                            "type": "homework",
                            "content": "完成课后练习1-5题",
                            "duration": 2,
                            "estimated_time": 30
                        }
                    ]
                }
            ]
        },
        "resources_needed": [
            {
                "type": "教学模型",
                "name": "蛋白质分子模型",
                "quantity": "1套",
                "usage_time": "新课讲授阶段",
                "preparation_note": "课前检查模型完整性"
            },
            {
                "type": "多媒体资源",
                "name": "蛋白质结构动画",
                "url": "https://example.com/protein-animation.mp4",
                "usage_time": "导入和讲授阶段",
                "preparation_note": "提前测试播放设备"
            }
        ],
        "assessment_plan": {
            "formative_assessment": [
                {
                    "method": "课堂观察",
                    "focus": "学生参与度和理解程度",
                    "timing": "整个课堂过程"
                },
                {
                    "method": "小组讨论评价",
                    "focus": "合作能力和思维深度",
                    "timing": "新课讲授阶段"
                }
            ],
            "summative_assessment": [
                {
                    "method": "课堂练习",
                    "scoring_criteria": "知识掌握准确性",
                    "timing": "巩固练习阶段"
                },
                {
                    "method": "课后作业",
                    "scoring_criteria": "综合应用能力",
                    "timing": "课后"
                }
            ]
        },
        "differentiation_strategies": {
            "for_advanced_students": [
                "提供蛋白质工程相关拓展资料",
                "引导思考蛋白质在生物技术中的应用"
            ],
            "for_struggling_students": [
                "提供更多基础概念复习材料",
                "安排同伴辅导",
                "简化复杂概念的表述"
            ]
        },
        "potential_challenges": [
            {
                "challenge": "学生对空间结构理解困难",
                "solution": "多使用实物模型和动画演示",
                "prevention": "课前准备充足的可视化材料"
            },
            {
                "challenge": "概念过于抽象",
                "solution": "结合生活实例进行类比",
                "prevention": "准备丰富的生活化实例"
            }
        ],
        "ai_suggestions": [
            "建议增加互动环节提高学生参与度",
            "可以结合最新科研成果增加课程趣味性",
            "注意控制讲授节奏，给学生充分思考时间"
        ],
        "confidence_score": 0.89,
        "generated_at": datetime.now().isoformat()
    }

# ==================== 启动应用 ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )