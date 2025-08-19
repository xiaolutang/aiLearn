# -*- coding: utf-8 -*-
"""
成绩模型模块
定义成绩相关的数据结构
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import datetime
import uuid
from decimal import Decimal, ROUND_HALF_UP

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GradeBase(BaseModel):
    """成绩基础模型"""
    student_id: str = Field(..., description="学生ID")
    subject_id: str = Field(..., description="科目ID")
    class_id: str = Field(..., description="班级ID")
    exam_id: Optional[str] = Field(None, description="考试ID")
    score: float = Field(..., ge=0, le=100, description="分数")
    exam_type: str = Field("normal", description="考试类型", pattern=r"^(quiz|normal|midterm|final)$")
    exam_date: datetime.date = Field(default_factory=datetime.date.today, description="考试日期")
    comments: Optional[str] = Field(None, max_length=500, description="评语")
    
    @validator('score')
    def validate_score(cls, v):
        """验证并格式化分数"""
        # 将分数四舍五入到小数点后一位
        if isinstance(v, (int, float)):
            return round(v, 1)
        return v


class GradeCreate(GradeBase):
    """成绩创建模型"""
    pass


class GradeUpdate(GradeBase):
    """成绩更新模型"""
    student_id: Optional[str] = Field(None, description="学生ID")
    subject_id: Optional[str] = Field(None, description="科目ID")
    class_id: Optional[str] = Field(None, description="班级ID")
    score: Optional[float] = Field(None, ge=0, le=100, description="分数")
    exam_type: Optional[str] = Field(None, description="考试类型", pattern=r"^(quiz|normal|midterm|final)$")
    exam_date: Optional[datetime.date] = Field(None, description="考试日期")


class GradeInDB(GradeBase):
    """数据库中的成绩模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="成绩ID")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者ID")
    updated_by: Optional[str] = Field(None, description="更新者ID")
    
    class Config:
        """配置类"""
        orm_mode = True


class GradeResponse(GradeBase):
    """成绩响应模型"""
    id: str = Field(..., description="成绩ID")
    created_at: datetime.datetime = Field(..., description="创建时间")
    updated_at: datetime.datetime = Field(..., description="更新时间")
    # 关联数据(可选，根据需要返回)
    student_name: Optional[str] = Field(None, description="学生姓名")
    subject_name: Optional[str] = Field(None, description="科目名称")
    class_name: Optional[str] = Field(None, description="班级名称")
    exam_name: Optional[str] = Field(None, description="考试名称")


class SubjectBase(BaseModel):
    """科目基础模型"""
    name: str = Field(..., min_length=2, max_length=50, description="科目名称")
    code: str = Field(..., min_length=2, max_length=20, description="科目代码")
    description: Optional[str] = Field(None, max_length=500, description="科目描述")
    credits: float = Field(..., ge=0, description="学分")


class SubjectCreate(SubjectBase):
    """科目创建模型"""
    pass


class SubjectUpdate(SubjectBase):
    """科目更新模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="科目名称")
    code: Optional[str] = Field(None, min_length=2, max_length=20, description="科目代码")
    credits: Optional[float] = Field(None, ge=0, description="学分")


class SubjectInDB(SubjectBase):
    """数据库中的科目模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="科目ID")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    
    class Config:
        """配置类"""
        orm_mode = True


class SubjectResponse(SubjectBase):
    """科目响应模型"""
    id: str = Field(..., description="科目ID")
    created_at: datetime.datetime = Field(..., description="创建时间")
    updated_at: datetime.datetime = Field(..., description="更新时间")


class ExamBase(BaseModel):
    """考试基础模型"""
    name: str = Field(..., min_length=2, max_length=100, description="考试名称")
    type: str = Field("normal", description="考试类型", pattern=r"^(quiz|normal|midterm|final)$")
    date: datetime.date = Field(..., description="考试日期")
    description: Optional[str] = Field(None, max_length=500, description="考试描述")
    grade_level: Optional[str] = Field(None, description="年级")


class ExamCreate(ExamBase):
    """考试创建模型"""
    pass


class ExamUpdate(ExamBase):
    """考试更新模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="考试名称")
    type: Optional[str] = Field(None, description="考试类型", pattern=r"^(quiz|normal|midterm|final)$")
    date: Optional[datetime.date] = Field(None, description="考试日期")


class ExamInDB(ExamBase):
    """数据库中的考试模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="考试ID")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    
    class Config:
        """配置类"""
        orm_mode = True


class ExamResponse(ExamBase):
    """考试响应模型"""
    id: str = Field(..., description="考试ID")
    created_at: datetime.datetime = Field(..., description="创建时间")
    updated_at: datetime.datetime = Field(..., description="更新时间")
    subject_ids: List[str] = Field(default_factory=list, description="关联的科目ID列表")


class GradeStatistics(BaseModel):
    """成绩统计数据模型"""
    count: int = Field(..., description="成绩数量")
    average: float = Field(..., description="平均分")
    median: float = Field(..., description="中位数")
    mode: float = Field(..., description="众数")
    min: float = Field(..., description="最低分")
    max: float = Field(..., description="最高分")
    variance: float = Field(..., description="方差")
    standard_deviation: float = Field(..., description="标准差")
    percentile_25: float = Field(..., description="第25百分位数")
    percentile_50: float = Field(..., description="第50百分位数")
    percentile_75: float = Field(..., description="第75百分位数")
    distribution: Dict[str, int] = Field(..., description="分数分布")  # 如 {"0-59": 10, "60-70": 20, ...}


class PaginatedGrades(BaseModel):
    """分页成绩列表模型"""
    grades: List[GradeResponse] = Field(..., description="成绩列表")
    total: int = Field(..., description="总成绩数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class PaginatedSubjects(BaseModel):
    """分页科目列表模型"""
    subjects: List[SubjectResponse] = Field(..., description="科目列表")
    total: int = Field(..., description="总科目数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class PaginatedExams(BaseModel):
    """分页考试列表模型"""
    exams: List[ExamResponse] = Field(..., description="考试列表")
    total: int = Field(..., description="总考试数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


# 成绩等级评定
GRADE_LEVELS = {
    "S": (90, 100),
    "A": (80, 89),
    "B": (70, 79),
    "C": (60, 69),
    "D": (0, 59)
}


def get_grade_level(score: float) -> str:
    """根据分数获取成绩等级
    
    Args:
        score: 分数
        
    Returns:
        str: 成绩等级
    """
    for level, (min_score, max_score) in GRADE_LEVELS.items():
        if min_score <= score <= max_score:
            return level
    return "D"  # 默认返回最低等级


def calculate_gpa(score: float) -> float:
    """根据分数计算GPA
    
    Args:
        score: 分数
        
    Returns:
        float: GPA值(4.0制)
    """
    grade_level = get_grade_level(score)
    gpa_map = {
        "S": 4.0,
        "A": 3.5,
        "B": 3.0,
        "C": 2.0,
        "D": 1.0
    }
    return gpa_map.get(grade_level, 1.0)


class StudentPerformance(BaseModel):
    """学生表现模型"""
    student_id: str = Field(..., description="学生ID")
    total_exams: int = Field(..., description="总考试数")
    average_gpa: float = Field(..., description="平均GPA")
    performance_trend: List[Dict[str, Any]] = Field(..., description="表现趋势")
    strengths: List[str] = Field(..., description="优势科目")
    weaknesses: List[str] = Field(..., description="劣势科目")
    improvement_suggestions: List[str] = Field(..., description="改进建议")
    personalized_guidance: str = Field(..., description="个性化指导")


class CustomReportRequest(BaseModel):
    """自定义报告请求模型"""
    report_type: str = Field(..., description="报告类型")
    student_ids: Optional[List[str]] = Field(None, description="学生ID列表")
    class_ids: Optional[List[str]] = Field(None, description="班级ID列表")
    subject_ids: Optional[List[str]] = Field(None, description="科目ID列表")
    start_date: Optional[datetime.date] = Field(None, description="开始日期")
    end_date: Optional[datetime.date] = Field(None, description="结束日期")
    include_details: bool = Field(True, description="是否包含详细信息")