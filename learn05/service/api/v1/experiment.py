# -*- coding: utf-8 -*-
"""
实验设计API路由

本模块提供生物实验设计相关的API接口，包括实验方案生成、实验步骤规划、安全提醒等功能。
"""

from fastapi import APIRouter, Depends, Query, Request, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

from database import get_db, User
from models.response import APIResponse, ResponseBuilder, PaginatedResponse
from middleware.exception_handler import BusinessException, ValidationException, ResourceNotFoundException
from auth import get_current_user

# 尝试导入AI服务，如果不存在则使用模拟实现
try:
    from llm.unified_client import UnifiedLLMClient
except ImportError:
    class UnifiedLLMClient:
        async def generate_response(self, prompt: str, **kwargs) -> str:
            return f"模拟AI响应: {prompt[:50]}..."

logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== 枚举定义 ====================

class ExperimentType(str, Enum):
    """实验类型枚举"""
    OBSERVATION = "observation"  # 观察实验
    VERIFICATION = "verification"  # 验证实验
    EXPLORATION = "exploration"  # 探究实验
    DEMONSTRATION = "demonstration"  # 演示实验
    SIMULATION = "simulation"  # 模拟实验

class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    BEGINNER = "beginner"  # 初级
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级

class SafetyLevel(str, Enum):
    """安全等级枚举"""
    LOW = "low"  # 低风险
    MEDIUM = "medium"  # 中等风险
    HIGH = "high"  # 高风险

# ==================== 请求模型 ====================

class ExperimentDesignRequest(BaseModel):
    """实验设计请求"""
    topic: str = Field(..., min_length=1, max_length=200, description="实验主题")
    grade_level: int = Field(..., ge=7, le=12, description="年级水平")
    experiment_type: ExperimentType = Field(..., description="实验类型")
    duration_minutes: int = Field(..., ge=10, le=180, description="实验时长(分钟)")
    student_count: int = Field(..., ge=1, le=50, description="学生人数")
    available_equipment: List[str] = Field(default=[], description="可用设备")
    learning_objectives: List[str] = Field(..., min_items=1, description="学习目标")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE, description="难度等级")
    special_requirements: Optional[str] = Field(None, max_length=500, description="特殊要求")
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v.strip():
            raise ValueError('实验主题不能为空')
        return v.strip()

class ExperimentOptimizationRequest(BaseModel):
    """实验优化请求"""
    experiment_id: str = Field(..., description="实验ID")
    optimization_type: str = Field(..., description="优化类型")
    feedback: Optional[str] = Field(None, description="反馈意见")
    constraints: Optional[Dict[str, Any]] = Field(None, description="约束条件")

class ExperimentEvaluationRequest(BaseModel):
    """实验评估请求"""
    experiment_id: str = Field(..., description="实验ID")
    execution_feedback: str = Field(..., description="执行反馈")
    student_performance: Dict[str, Any] = Field(..., description="学生表现")
    safety_incidents: List[str] = Field(default=[], description="安全事件")
    improvement_suggestions: Optional[str] = Field(None, description="改进建议")

# ==================== 响应模型 ====================

class ExperimentStep(BaseModel):
    """实验步骤"""
    step_number: int = Field(..., description="步骤编号")
    title: str = Field(..., description="步骤标题")
    description: str = Field(..., description="步骤描述")
    duration_minutes: int = Field(..., description="预计时长")
    materials_needed: List[str] = Field(default=[], description="所需材料")
    safety_notes: List[str] = Field(default=[], description="安全注意事项")
    expected_results: Optional[str] = Field(None, description="预期结果")
    troubleshooting: Optional[List[str]] = Field(None, description="故障排除")

class SafetyGuideline(BaseModel):
    """安全指导"""
    category: str = Field(..., description="安全类别")
    level: SafetyLevel = Field(..., description="安全等级")
    guidelines: List[str] = Field(..., description="安全指导")
    emergency_procedures: List[str] = Field(default=[], description="应急程序")
    required_equipment: List[str] = Field(default=[], description="必需安全设备")

class ExperimentMaterial(BaseModel):
    """实验材料"""
    name: str = Field(..., description="材料名称")
    quantity: str = Field(..., description="数量")
    specification: Optional[str] = Field(None, description="规格说明")
    safety_level: SafetyLevel = Field(..., description="安全等级")
    handling_notes: Optional[str] = Field(None, description="处理注意事项")
    alternatives: List[str] = Field(default=[], description="替代材料")

class ExperimentDesign(BaseModel):
    """实验设计方案"""
    id: str = Field(..., description="实验ID")
    title: str = Field(..., description="实验标题")
    topic: str = Field(..., description="实验主题")
    grade_level: int = Field(..., description="年级水平")
    experiment_type: ExperimentType = Field(..., description="实验类型")
    difficulty_level: DifficultyLevel = Field(..., description="难度等级")
    duration_minutes: int = Field(..., description="实验时长")
    student_count: int = Field(..., description="学生人数")
    learning_objectives: List[str] = Field(..., description="学习目标")
    theoretical_background: str = Field(..., description="理论背景")
    materials: List[ExperimentMaterial] = Field(..., description="实验材料")
    steps: List[ExperimentStep] = Field(..., description="实验步骤")
    safety_guidelines: List[SafetyGuideline] = Field(..., description="安全指导")
    assessment_criteria: List[str] = Field(..., description="评估标准")
    extensions: List[str] = Field(default=[], description="拓展活动")
    created_at: datetime = Field(..., description="创建时间")
    created_by: str = Field(..., description="创建者")

class ExperimentOptimization(BaseModel):
    """实验优化建议"""
    optimization_id: str = Field(..., description="优化ID")
    experiment_id: str = Field(..., description="实验ID")
    optimization_type: str = Field(..., description="优化类型")
    suggestions: List[str] = Field(..., description="优化建议")
    modified_steps: List[ExperimentStep] = Field(default=[], description="修改的步骤")
    cost_impact: Optional[str] = Field(None, description="成本影响")
    time_impact: Optional[str] = Field(None, description="时间影响")
    safety_impact: Optional[str] = Field(None, description="安全影响")
    created_at: datetime = Field(..., description="创建时间")

class ExperimentEvaluation(BaseModel):
    """实验评估结果"""
    evaluation_id: str = Field(..., description="评估ID")
    experiment_id: str = Field(..., description="实验ID")
    overall_score: float = Field(..., ge=0, le=10, description="总体评分")
    effectiveness_score: float = Field(..., ge=0, le=10, description="有效性评分")
    safety_score: float = Field(..., ge=0, le=10, description="安全性评分")
    engagement_score: float = Field(..., ge=0, le=10, description="参与度评分")
    strengths: List[str] = Field(..., description="优势")
    weaknesses: List[str] = Field(..., description="不足")
    improvement_recommendations: List[str] = Field(..., description="改进建议")
    student_feedback_summary: str = Field(..., description="学生反馈总结")
    created_at: datetime = Field(..., description="评估时间")

# ==================== API接口 ====================

@router.post("/design", response_model=APIResponse[ExperimentDesign])
async def create_experiment_design(
    request: Request,
    design_request: ExperimentDesignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建实验设计方案"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以创建实验设计")
        
        # 生成实验ID
        experiment_id = f"exp_{int(datetime.now().timestamp())}"
        
        # 模拟AI生成实验设计
        experiment_design = ExperimentDesign(
            id=experiment_id,
            title=f"{design_request.topic}实验设计",
            topic=design_request.topic,
            grade_level=design_request.grade_level,
            experiment_type=design_request.experiment_type,
            difficulty_level=design_request.difficulty_level,
            duration_minutes=design_request.duration_minutes,
            student_count=design_request.student_count,
            learning_objectives=design_request.learning_objectives,
            theoretical_background=f"本实验旨在通过{design_request.experiment_type.value}的方式，让学生深入理解{design_request.topic}的相关概念和原理。",
            materials=[
                ExperimentMaterial(
                    name="显微镜",
                    quantity="每组1台",
                    specification="光学显微镜，放大倍数40-1000倍",
                    safety_level=SafetyLevel.LOW,
                    handling_notes="轻拿轻放，避免震动",
                    alternatives=["数字显微镜", "手持放大镜"]
                ),
                ExperimentMaterial(
                    name="载玻片",
                    quantity="每组10片",
                    specification="标准载玻片，76×26mm",
                    safety_level=SafetyLevel.MEDIUM,
                    handling_notes="小心玻璃边缘，避免划伤",
                    alternatives=["塑料载片"]
                )
            ],
            steps=[
                ExperimentStep(
                    step_number=1,
                    title="准备工作",
                    description="检查实验器材，准备实验材料",
                    duration_minutes=10,
                    materials_needed=["显微镜", "载玻片"],
                    safety_notes=["检查显微镜是否完好", "确保工作台稳固"],
                    expected_results="器材准备就绪",
                    troubleshooting=["如发现器材损坏，及时更换"]
                ),
                ExperimentStep(
                    step_number=2,
                    title="样本制备",
                    description="制备观察样本",
                    duration_minutes=15,
                    materials_needed=["载玻片", "盖玻片", "样本"],
                    safety_notes=["小心处理玻璃器材", "避免样本污染"],
                    expected_results="样本制备完成",
                    troubleshooting=["如样本破损，重新制备"]
                )
            ],
            safety_guidelines=[
                SafetyGuideline(
                    category="器材安全",
                    level=SafetyLevel.MEDIUM,
                    guidelines=["正确使用显微镜", "小心处理玻璃器材"],
                    emergency_procedures=["如有器材损坏，立即停止实验"],
                    required_equipment=["护目镜", "实验服"]
                )
            ],
            assessment_criteria=[
                "实验操作规范性",
                "观察记录准确性",
                "安全意识表现",
                "团队协作能力"
            ],
            extensions=[
                "尝试不同类型的样本",
                "比较不同放大倍数下的观察效果"
            ],
            created_at=datetime.now(),
            created_by=current_user.username
        )
        
        return ResponseBuilder.success(experiment_design, "实验设计创建成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"创建实验设计异常: {e}")
        raise BusinessException("创建实验设计失败")

@router.get("/designs", response_model=APIResponse[PaginatedResponse[ExperimentDesign]])
async def get_experiment_designs(
    request: Request,
    topic: Optional[str] = Query(None, description="主题筛选"),
    grade_level: Optional[int] = Query(None, ge=7, le=12, description="年级筛选"),
    experiment_type: Optional[ExperimentType] = Query(None, description="实验类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取实验设计列表"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看实验设计")
        
        # 模拟分页数据
        total = 25
        designs = []
        
        for i in range(min(page_size, total - (page - 1) * page_size)):
            design_id = f"exp_{1000 + (page - 1) * page_size + i}"
            designs.append(ExperimentDesign(
                id=design_id,
                title=f"实验设计 {i + 1}",
                topic="细胞结构观察",
                grade_level=10,
                experiment_type=ExperimentType.OBSERVATION,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                duration_minutes=45,
                student_count=30,
                learning_objectives=["观察细胞结构", "理解细胞功能"],
                theoretical_background="细胞是生命的基本单位",
                materials=[],
                steps=[],
                safety_guidelines=[],
                assessment_criteria=["操作规范", "观察准确"],
                created_at=datetime.now(),
                created_by=current_user.username
            ))
        
        paginated_response = PaginatedResponse(
            items=designs,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
        
        return ResponseBuilder.success(paginated_response, "获取实验设计列表成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取实验设计列表异常: {e}")
        raise BusinessException("获取实验设计列表失败")

@router.get("/designs/{experiment_id}", response_model=APIResponse[ExperimentDesign])
async def get_experiment_design(
    experiment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取实验设计详情"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看实验设计详情")
        
        # 模拟查询实验设计
        if not experiment_id.startswith('exp_'):
            raise ResourceNotFoundException("实验设计不存在")
        
        # 返回模拟数据
        design = ExperimentDesign(
            id=experiment_id,
            title="细胞结构观察实验",
            topic="细胞结构观察",
            grade_level=10,
            experiment_type=ExperimentType.OBSERVATION,
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            duration_minutes=45,
            student_count=30,
            learning_objectives=["观察细胞结构", "理解细胞功能"],
            theoretical_background="细胞是生命的基本单位，通过显微镜观察可以了解其结构特点。",
            materials=[
                ExperimentMaterial(
                    name="显微镜",
                    quantity="每组1台",
                    specification="光学显微镜，放大倍数40-1000倍",
                    safety_level=SafetyLevel.LOW,
                    handling_notes="轻拿轻放，避免震动",
                    alternatives=["数字显微镜"]
                )
            ],
            steps=[
                ExperimentStep(
                    step_number=1,
                    title="准备工作",
                    description="检查实验器材，准备实验材料",
                    duration_minutes=10,
                    materials_needed=["显微镜", "载玻片"],
                    safety_notes=["检查显微镜是否完好"],
                    expected_results="器材准备就绪"
                )
            ],
            safety_guidelines=[
                SafetyGuideline(
                    category="器材安全",
                    level=SafetyLevel.MEDIUM,
                    guidelines=["正确使用显微镜"],
                    emergency_procedures=["如有器材损坏，立即停止实验"],
                    required_equipment=["护目镜"]
                )
            ],
            assessment_criteria=["实验操作规范性", "观察记录准确性"],
            extensions=["尝试不同类型的样本"],
            created_at=datetime.now(),
            created_by=current_user.username
        )
        
        return ResponseBuilder.success(design, "获取实验设计详情成功")
        
    except (ValidationException, ResourceNotFoundException) as e:
        raise e
    except Exception as e:
        logger.error(f"获取实验设计详情异常: {e}")
        raise BusinessException("获取实验设计详情失败")

@router.post("/designs/{experiment_id}/optimize", response_model=APIResponse[ExperimentOptimization])
async def optimize_experiment(
    experiment_id: str,
    optimization_request: ExperimentOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """优化实验设计"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以优化实验设计")
        
        # 验证实验是否存在
        if not experiment_id.startswith('exp_'):
            raise ResourceNotFoundException("实验设计不存在")
        
        # 生成优化建议
        optimization = ExperimentOptimization(
            optimization_id=f"opt_{int(datetime.now().timestamp())}",
            experiment_id=experiment_id,
            optimization_type=optimization_request.optimization_type,
            suggestions=[
                "建议增加预实验环节，让学生熟悉操作",
                "可以准备备用材料，防止实验材料不足",
                "建议增加小组讨论环节，提高学生参与度"
            ],
            modified_steps=[],
            cost_impact="成本增加约10%",
            time_impact="时间延长5-10分钟",
            safety_impact="安全性提升",
            created_at=datetime.now()
        )
        
        return ResponseBuilder.success(optimization, "实验优化建议生成成功")
        
    except (ValidationException, ResourceNotFoundException) as e:
        raise e
    except Exception as e:
        logger.error(f"优化实验设计异常: {e}")
        raise BusinessException("优化实验设计失败")

@router.post("/designs/{experiment_id}/evaluate", response_model=APIResponse[ExperimentEvaluation])
async def evaluate_experiment(
    experiment_id: str,
    evaluation_request: ExperimentEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """评估实验执行效果"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以评估实验")
        
        # 验证实验是否存在
        if not experiment_id.startswith('exp_'):
            raise ResourceNotFoundException("实验设计不存在")
        
        # 生成评估结果
        evaluation = ExperimentEvaluation(
            evaluation_id=f"eval_{int(datetime.now().timestamp())}",
            experiment_id=experiment_id,
            overall_score=8.5,
            effectiveness_score=8.8,
            safety_score=9.2,
            engagement_score=8.0,
            strengths=[
                "学生参与度高",
                "实验步骤清晰",
                "安全措施到位"
            ],
            weaknesses=[
                "部分学生操作不够熟练",
                "时间安排略显紧张"
            ],
            improvement_recommendations=[
                "增加操作演示环节",
                "适当延长实验时间",
                "准备更多备用材料"
            ],
            student_feedback_summary="学生普遍反映实验有趣，但希望有更多时间进行观察和讨论。",
            created_at=datetime.now()
        )
        
        return ResponseBuilder.success(evaluation, "实验评估完成")
        
    except (ValidationException, ResourceNotFoundException) as e:
        raise e
    except Exception as e:
        logger.error(f"评估实验异常: {e}")
        raise BusinessException("评估实验失败")

@router.get("/templates", response_model=APIResponse[List[Dict[str, Any]]])
async def get_experiment_templates(
    request: Request,
    grade_level: Optional[int] = Query(None, ge=7, le=12, description="年级筛选"),
    experiment_type: Optional[ExperimentType] = Query(None, description="实验类型筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取实验模板列表"""
    try:
        # 权限检查
        if current_user.role not in ['teacher', 'admin']:
            raise ValidationException("只有教师和管理员可以查看实验模板")
        
        # 模拟模板数据
        templates = [
            {
                "id": "template_001",
                "name": "细胞观察实验模板",
                "description": "适用于细胞结构观察的标准实验模板",
                "grade_level": 10,
                "experiment_type": "observation",
                "duration_minutes": 45,
                "difficulty_level": "intermediate",
                "usage_count": 156
            },
            {
                "id": "template_002",
                "name": "酶活性实验模板",
                "description": "探究酶活性影响因素的实验模板",
                "grade_level": 11,
                "experiment_type": "exploration",
                "duration_minutes": 60,
                "difficulty_level": "advanced",
                "usage_count": 89
            },
            {
                "id": "template_003",
                "name": "光合作用演示模板",
                "description": "光合作用过程演示实验模板",
                "grade_level": 9,
                "experiment_type": "demonstration",
                "duration_minutes": 30,
                "difficulty_level": "beginner",
                "usage_count": 203
            }
        ]
        
        # 应用筛选条件
        if grade_level:
            templates = [t for t in templates if t['grade_level'] == grade_level]
        if experiment_type:
            templates = [t for t in templates if t['experiment_type'] == experiment_type.value]
        
        return ResponseBuilder.success(templates, "获取实验模板成功")
        
    except ValidationException as e:
        raise e
    except Exception as e:
        logger.error(f"获取实验模板异常: {e}")
        raise BusinessException("获取实验模板失败")

@router.get("/health", response_model=APIResponse[Dict[str, str]])
async def health_check():
    """健康检查"""
    return ResponseBuilder.success({
        "status": "healthy",
        "module": "experiment",
        "timestamp": datetime.now().isoformat()
    })