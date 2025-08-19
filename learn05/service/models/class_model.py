# -*- coding: utf-8 -*-
"""
班级模型模块
定义班级相关的数据结构
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import datetime
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassBase(BaseModel):
    """班级基础模型"""
    name: str = Field(..., min_length=2, max_length=100, description="班级名称")
    grade_level: str = Field(..., min_length=1, max_length=20, description="年级")
    teacher_id: str = Field(..., description="班主任ID")
    start_year: int = Field(..., ge=2000, le=datetime.datetime.now().year + 5, description="入学年份")
    description: Optional[str] = Field(None, max_length=500, description="班级描述")
    capacity: int = Field(30, ge=5, le=100, description="班级容量")
    is_active: bool = Field(True, description="是否活跃")
    
    @validator('start_year')
    def validate_start_year(cls, v):
        """验证入学年份"""
        current_year = datetime.datetime.now().year
        if v < 2000 or v > current_year + 5:
            raise ValueError(f"入学年份必须在2000到{current_year + 5}之间")
        return v


class ClassCreate(ClassBase):
    """班级创建模型"""
    pass


class ClassUpdate(ClassBase):
    """班级更新模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="班级名称")
    grade_level: Optional[str] = Field(None, min_length=1, max_length=20, description="年级")
    teacher_id: Optional[str] = Field(None, description="班主任ID")
    start_year: Optional[int] = Field(None, ge=2000, le=datetime.datetime.now().year + 5, description="入学年份")
    capacity: Optional[int] = Field(None, ge=5, le=100, description="班级容量")
    is_active: Optional[bool] = Field(None, description="是否活跃")


class ClassInDB(ClassBase):
    """数据库中的班级模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="班级ID")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    
    class Config:
        """配置类"""
        orm_mode = True


class ClassResponse(ClassBase):
    """班级响应模型"""
    id: str = Field(..., description="班级ID")
    created_at: datetime.datetime = Field(..., description="创建时间")
    updated_at: datetime.datetime = Field(..., description="更新时间")
    # 关联数据(可选，根据需要返回)
    teacher_name: Optional[str] = Field(None, description="班主任姓名")
    student_count: int = Field(0, description="学生人数")
    subject_count: int = Field(0, description="开设科目数")


class ClassMember(BaseModel):
    """班级成员模型"""
    class_id: str = Field(..., description="班级ID")
    user_id: str = Field(..., description="用户ID")
    role: str = Field("student", description="成员角色", pattern=r"^(teacher|student|assistant)$")
    join_date: datetime.datetime = Field(default_factory=datetime.datetime.now, description="加入日期")
    is_active: bool = Field(True, description="是否活跃")


class ClassMemberCreate(ClassMember):
    """班级成员创建模型"""
    pass


class ClassMemberUpdate(ClassMember):
    """班级成员更新模型"""
    class_id: Optional[str] = Field(None, description="班级ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    role: Optional[str] = Field(None, description="成员角色", pattern=r"^(teacher|student|assistant)$")
    is_active: Optional[bool] = Field(None, description="是否活跃")


class ClassMemberInDB(ClassMember):
    """数据库中的班级成员模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="成员ID")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    
    class Config:
        """配置类"""
        orm_mode = True


class ClassMemberResponse(ClassMember):
    """班级成员响应模型"""
    id: str = Field(..., description="成员ID")
    # 关联数据(可选，根据需要返回)
    user_name: Optional[str] = Field(None, description="用户姓名")
    class_name: Optional[str] = Field(None, description="班级名称")


class ClassSubject(BaseModel):
    """班级科目模型"""
    class_id: str = Field(..., description="班级ID")
    subject_id: str = Field(..., description="科目ID")
    teacher_id: Optional[str] = Field(None, description="授课教师ID")
    semester: str = Field(..., description="学期")
    is_active: bool = Field(True, description="是否活跃")


class ClassSubjectCreate(ClassSubject):
    """班级科目创建模型"""
    pass


class ClassSubjectInDB(ClassSubject):
    """数据库中的班级科目模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="班级科目ID")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    
    class Config:
        """配置类"""
        orm_mode = True


class ClassSubjectResponse(ClassSubject):
    """班级科目响应模型"""
    id: str = Field(..., description="班级科目ID")
    # 关联数据(可选，根据需要返回)
    class_name: Optional[str] = Field(None, description="班级名称")
    subject_name: Optional[str] = Field(None, description="科目名称")
    teacher_name: Optional[str] = Field(None, description="授课教师姓名")


class ClassPerformance(BaseModel):
    """班级表现模型"""
    class_id: str = Field(..., description="班级ID")
    subject_id: str = Field(..., description="科目ID")
    exam_id: Optional[str] = Field(None, description="考试ID")
    average_score: float = Field(..., ge=0, le=100, description="平均分")
    median_score: float = Field(..., ge=0, le=100, description="中位数")
    pass_rate: float = Field(..., ge=0, le=100, description="及格率")
    excellent_rate: float = Field(..., ge=0, le=100, description="优秀率")
    data_date: datetime.date = Field(default_factory=datetime.date.today, description="数据日期")
    compared_to_previous: Optional[float] = Field(None, description="与上次对比的变化")


class ClassPerformanceInDB(ClassPerformance):
    """数据库中的班级表现模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="班级表现ID")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="更新时间")
    
    class Config:
        """配置类"""
        orm_mode = True


class ClassPerformanceResponse(ClassPerformance):
    """班级表现响应模型"""
    id: str = Field(..., description="班级表现ID")
    # 关联数据(可选，根据需要返回)
    class_name: Optional[str] = Field(None, description="班级名称")
    subject_name: Optional[str] = Field(None, description="科目名称")
    exam_name: Optional[str] = Field(None, description="考试名称")


class PaginatedClasses(BaseModel):
    """分页班级列表模型"""
    classes: List[ClassResponse] = Field(..., description="班级列表")
    total: int = Field(..., description="总班级数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class PaginatedClassMembers(BaseModel):
    """分页班级成员列表模型"""
    members: List[ClassMemberResponse] = Field(..., description="班级成员列表")
    total: int = Field(..., description="总成员数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class PaginatedClassSubjects(BaseModel):
    """分页班级科目列表模型"""
    subjects: List[ClassSubjectResponse] = Field(..., description="班级科目列表")
    total: int = Field(..., description="总科目数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


# 班级相关的常量
CLASS_ROLES = {
    "teacher": "班主任",
    "assistant": "助教",
    "student": "学生"
}


def get_class_role_display(role: str) -> str:
    """获取班级角色的显示名称
    
    Args:
        role: 角色代码
        
    Returns:
        str: 角色显示名称
    """
    return CLASS_ROLES.get(role, role)


def is_valid_class_role(role: str) -> bool:
    """检查是否为有效的班级角色
    
    Args:
        role: 角色代码
        
    Returns:
        bool: 是否有效
    """
    return role in CLASS_ROLES