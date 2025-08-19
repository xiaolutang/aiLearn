# -*- coding: utf-8 -*-
"""
班级API接口
提供班级相关的HTTP接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional, Dict, Any
import pandas as pd
import io
from datetime import datetime

from models.class_model import (
    ClassCreate, ClassUpdate, ClassResponse, ClassMemberCreate, 
    ClassMemberResponse, ClassSubjectCreate, ClassSubjectResponse,
    PaginatedClasses, PaginatedClassMembers, PaginatedClassSubjects,
    ClassPerformance
)
from models.grade import GradeStatistics
from services.class_service import get_class_service, ClassService
from services.user_service import get_current_user
from models.user import UserResponse

# 创建路由器
router = APIRouter()


@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED, tags=["班级管理"])
async def create_class(
    class_data: ClassCreate,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建班级
    
    Args:
        class_data: 班级创建数据
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        ClassResponse: 创建的班级
        
    Raises:
        HTTPException: 创建失败
    """
    try:
        # 检查用户是否为教师或管理员
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和管理员可以创建班级")
        
        return class_service.create_class(class_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=PaginatedClasses, tags=["班级管理"])
async def get_classes(
    page: int = 1,
    limit: int = 10,
    grade_level: Optional[str] = None,
    name: Optional[str] = None,
    teacher_id: Optional[str] = None,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取班级列表
    
    Args:
        page: 当前页码
        limit: 每页数量
        grade_level: 年级过滤
        name: 班级名称过滤
        teacher_id: 教师ID过滤
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        PaginatedClasses: 分页班级列表
    """
    # 构建过滤条件
    filters = {}
    if grade_level:
        filters["grade_level"] = grade_level
    if name:
        filters["name"] = name
    if teacher_id:
        filters["teacher_id"] = teacher_id
    
    # 如果是学生，只返回其所在的班级
    if current_user.role == "student":
        filters["student_id"] = current_user.id
    
    return class_service.get_classes(page=page, limit=limit, **filters)


@router.get("/{class_id}", response_model=ClassResponse, tags=["班级管理"])
async def get_class(
    class_id: str,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取单个班级
    
    Args:
        class_id: 班级ID
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        ClassResponse: 班级信息
        
    Raises:
        HTTPException: 班级不存在或无权限访问
    """
    # 检查用户是否有权限访问该班级
    if not class_service.check_access_permission(class_id, current_user.id, current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该班级")
    
    class_info = class_service.get_class_by_id(class_id)
    if not class_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")
    return class_info


@router.put("/{class_id}", response_model=ClassResponse, tags=["班级管理"])
async def update_class(
    class_id: str,
    class_data: ClassUpdate,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新班级
    
    Args:
        class_id: 班级ID
        class_data: 班级更新数据
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        ClassResponse: 更新后的班级信息
        
    Raises:
        HTTPException: 更新失败或班级不存在
    """
    # 检查用户是否为教师或管理员
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和管理员可以更新班级")
    
    # 检查用户是否为班级的教师或管理员
    if current_user.role == "teacher" and not class_service.is_class_teacher(class_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有班级的教师可以更新班级")
    
    try:
        return class_service.update_class(class_id, class_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["班级管理"])
async def delete_class(
    class_id: str,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除班级
    
    Args:
        class_id: 班级ID
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        None
        
    Raises:
        HTTPException: 删除失败或班级不存在
    """
    # 检查用户是否为教师或管理员
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和管理员可以删除班级")
    
    # 检查用户是否为班级的教师或管理员
    if current_user.role == "teacher" and not class_service.is_class_teacher(class_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有班级的教师可以删除班级")
    
    try:
        result = class_service.delete_class(class_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除班级失败")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{class_id}/members", response_model=ClassMemberResponse, status_code=status.HTTP_201_CREATED, tags=["班级成员"])
async def add_class_member(
    class_id: str,
    member_data: ClassMemberCreate,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """添加班级成员
    
    Args:
        class_id: 班级ID
        member_data: 班级成员创建数据
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        ClassMemberResponse: 创建的班级成员
        
    Raises:
        HTTPException: 添加失败
    """
    # 检查用户是否为教师或管理员
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和管理员可以添加班级成员")
    
    # 检查用户是否为班级的教师或管理员
    if current_user.role == "teacher" and not class_service.is_class_teacher(class_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有班级的教师可以添加班级成员")
    
    try:
        return class_service.add_class_member(class_id, member_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{class_id}/members", response_model=PaginatedClassMembers, tags=["班级成员"])
async def get_class_members(
    class_id: str,
    page: int = 1,
    limit: int = 10,
    role: Optional[str] = None,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取班级成员列表
    
    Args:
        class_id: 班级ID
        page: 当前页码
        limit: 每页数量
        role: 成员角色过滤
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        PaginatedClassMembers: 分页班级成员列表
    """
    # 检查用户是否有权限访问该班级
    if not class_service.check_access_permission(class_id, current_user.id, current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该班级")
    
    return class_service.get_class_members(class_id, page=page, limit=limit, role=role)


@router.delete("/{class_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["班级成员"])
async def remove_class_member(
    class_id: str,
    user_id: str,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """移除班级成员
    
    Args:
        class_id: 班级ID
        user_id: 用户ID
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        None
        
    Raises:
        HTTPException: 移除失败
    """
    # 检查用户是否为教师或管理员
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和管理员可以移除班级成员")
    
    # 检查用户是否为班级的教师或管理员
    if current_user.role == "teacher" and not class_service.is_class_teacher(class_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有班级的教师可以移除班级成员")
    
    try:
        result = class_service.remove_class_member(class_id, user_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="移除班级成员失败")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{class_id}/subjects", response_model=ClassSubjectResponse, status_code=status.HTTP_201_CREATED, tags=["班级科目"])
async def add_class_subject(
    class_id: str,
    subject_data: ClassSubjectCreate,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """添加班级科目
    
    Args:
        class_id: 班级ID
        subject_data: 班级科目创建数据
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        ClassSubjectResponse: 创建的班级科目
        
    Raises:
        HTTPException: 添加失败
    """
    # 检查用户是否为教师或管理员
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和管理员可以添加班级科目")
    
    # 检查用户是否为班级的教师或管理员
    if current_user.role == "teacher" and not class_service.is_class_teacher(class_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有班级的教师可以添加班级科目")
    
    try:
        return class_service.add_class_subject(class_id, subject_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{class_id}/subjects", response_model=PaginatedClassSubjects, tags=["班级科目"])
async def get_class_subjects(
    class_id: str,
    page: int = 1,
    limit: int = 10,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取班级科目列表
    
    Args:
        class_id: 班级ID
        page: 当前页码
        limit: 每页数量
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        PaginatedClassSubjects: 分页班级科目列表
    """
    # 检查用户是否有权限访问该班级
    if not class_service.check_access_permission(class_id, current_user.id, current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该班级")
    
    return class_service.get_class_subjects(class_id, page=page, limit=limit)


@router.delete("/{class_id}/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["班级科目"])
async def remove_class_subject(
    class_id: str,
    subject_id: str,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """移除班级科目
    
    Args:
        class_id: 班级ID
        subject_id: 科目ID
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        None
        
    Raises:
        HTTPException: 移除失败
    """
    # 检查用户是否为教师或管理员
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和管理员可以移除班级科目")
    
    # 检查用户是否为班级的教师或管理员
    if current_user.role == "teacher" and not class_service.is_class_teacher(class_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有班级的教师可以移除班级科目")
    
    try:
        result = class_service.remove_class_subject(class_id, subject_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="移除班级科目失败")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{class_id}/performance", response_model=ClassPerformance, tags=["班级表现"])
async def get_class_performance(
    class_id: str,
    subject_id: Optional[str] = None,
    exam_id: Optional[str] = None,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取班级整体表现
    
    Args:
        class_id: 班级ID
        subject_id: 科目ID（可选）
        exam_id: 考试ID（可选）
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        ClassPerformance: 班级表现数据
        
    Raises:
        HTTPException: 获取失败
    """
    # 检查用户是否有权限访问该班级
    if not class_service.check_access_permission(class_id, current_user.id, current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该班级")
    
    try:
        return class_service.get_class_performance(class_id, subject_id=subject_id, exam_id=exam_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{class_id}/subject-performance/{subject_id}", response_model=GradeStatistics, tags=["班级表现"])
async def get_class_subject_performance(
    class_id: str,
    subject_id: str,
    exam_id: Optional[str] = None,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取班级特定科目的表现
    
    Args:
        class_id: 班级ID
        subject_id: 科目ID
        exam_id: 考试ID（可选）
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        GradeStatistics: 班级科目表现数据
        
    Raises:
        HTTPException: 获取失败
    """
    # 检查用户是否有权限访问该班级
    if not class_service.check_access_permission(class_id, current_user.id, current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该班级")
    
    try:
        return class_service.get_class_subject_performance(class_id, subject_id, exam_id=exam_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{class_id}/ranking", response_model=List[Dict[str, Any]], tags=["班级表现"])
async def get_class_ranking(
    class_id: str,
    subject_id: Optional[str] = None,
    exam_id: Optional[str] = None,
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取班级内学生排名
    
    Args:
        class_id: 班级ID
        subject_id: 科目ID（可选）
        exam_id: 考试ID（可选）
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        List[Dict[str, Any]]: 排名数据列表
        
    Raises:
        HTTPException: 获取失败
    """
    # 检查用户是否有权限访问该班级
    if not class_service.check_access_permission(class_id, current_user.id, current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该班级")
    
    try:
        return class_service.get_class_ranking(class_id, subject_id=subject_id, exam_id=exam_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{class_id}/import-students", response_model=Dict[str, Any], tags=["班级管理"])
async def import_class_students(
    class_id: str,
    file: UploadFile = File(...),
    class_service: ClassService = Depends(get_class_service),
    current_user: UserResponse = Depends(get_current_user)
):
    """批量导入班级学生（Excel文件）
    
    Args:
        class_id: 班级ID
        file: Excel文件
        class_service: 班级服务实例
        current_user: 当前登录用户
        
    Returns:
        Dict[str, Any]: 导入结果统计
        
    Raises:
        HTTPException: 导入失败
    """
    # 检查用户是否为教师或管理员
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和管理员可以导入学生")
    
    # 检查用户是否为班级的教师或管理员
    if current_user.role == "teacher" and not class_service.is_class_teacher(class_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有班级的教师可以导入学生")
    
    # 验证文件类型
    if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xls'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只支持Excel文件格式")
    
    try:
        # 读取文件内容
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 导入学生
        result = class_service.import_class_students(class_id, df)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"导入失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"导入失败: {str(e)}")
    finally:
        await file.close()