#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手 - 工具函数
提供通用的工具函数和辅助功能
"""

import json
import time
import uuid
import hashlib
import datetime
import logging
from typing import Any, Dict, List, Union, Optional, Tuple
import pandas as pd
import numpy as np
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# 配置日志
def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    设置日志记录器
    参数:
        name: 日志记录器名称
        log_level: 日志级别
    返回:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 避免重复添加处理器
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# 异常处理
def handle_exception(exception: Exception, status_code: int = 500) -> JSONResponse:
    """
    处理异常，返回标准的错误响应
    参数:
        exception: 异常对象
        status_code: HTTP状态码
    返回:
        标准的错误响应
    """
    logger = setup_logger("utils")
    logger.error(f"发生错误: {str(exception)}", exc_info=True)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "message": str(exception),
            "data": None
        }
    )

# 数据验证
def validate_input(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    验证输入数据是否包含所有必需的字段
    参数:
        data: 输入数据字典
        required_fields: 必需的字段列表
    返回:
        验证是否通过
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            raise HTTPException(
                status_code=400,
                detail=f"缺少必需字段: {field}"
            )
    return True

# 分页处理
def paginate_query(query, page: int, page_size: int):
    """
    对查询结果进行分页处理
    参数:
        query: SQLAlchemy查询对象
        page: 页码
        page_size: 每页的数量
    返回:
        分页后的查询结果
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100
    
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)

# 分页结果格式化
def format_paginated_result(result: List[Any], page: int, page_size: int, total: int) -> Dict[str, Any]:
    """
    格式化分页结果
    参数:
        result: 查询结果列表
        page: 页码
        page_size: 每页的数量
        total: 总数量
    返回:
        格式化后的分页结果
    """
    return {
        "items": result,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }

# 生成唯一ID
def generate_uuid() -> str:
    """
    生成唯一ID
    返回:
        唯一ID字符串
    """
    return str(uuid.uuid4())

# 计算MD5哈希
def calculate_md5(data: str) -> str:
    """
    计算字符串的MD5哈希
    参数:
        data: 输入字符串
    返回:
        MD5哈希值
    """
    return hashlib.md5(data.encode()).hexdigest()

# 时间工具函数
def get_current_time() -> datetime.datetime:
    """
    获取当前时间
    返回:
        当前时间的datetime对象
    """
    return datetime.datetime.now()

def format_datetime(dt: datetime.datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化datetime对象为字符串
    参数:
        dt: datetime对象
        format_str: 格式化字符串
    返回:
        格式化后的时间字符串
    """
    if dt is None:
        return None
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime.datetime:
    """
    将字符串解析为datetime对象
    参数:
        date_str: 日期时间字符串
        format_str: 格式化字符串
    返回:
        解析后的datetime对象
    """
    if date_str is None:
        return None
    return datetime.datetime.strptime(date_str, format_str)

# Excel处理函数
def read_excel_file(file: UploadFile) -> pd.DataFrame:
    """
    读取Excel文件并返回DataFrame
    参数:
        file: 上传的Excel文件
    返回:
        包含Excel数据的DataFrame
    """
    try:
        # 读取文件内容
        contents = file.file.read()
        
        # 使用pandas读取Excel文件
        df = pd.read_excel(contents)
        
        # 重置文件指针
        file.file.seek(0)
        
        return df
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"读取Excel文件失败: {str(e)}"
        )

def excel_to_json(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    将DataFrame转换为JSON格式
    参数:
        df: pandas DataFrame
    返回:
        JSON格式的数据列表
    """
    # 将DataFrame转换为字典列表
    data = df.to_dict(orient="records")
    
    # 处理NaN和NaT值
    for item in data:
        for key, value in item.items():
            if pd.isna(value):
                item[key] = None
            elif isinstance(value, pd.Timestamp):
                item[key] = value.isoformat()
    
    return data

# 数值处理函数
def calculate_percentage(value: float, total: float) -> float:
    """
    计算百分比
    参数:
        value: 数值
        total: 总数
    返回:
        百分比（保留两位小数）
    """
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)

def calculate_average(values: List[float]) -> float:
    """
    计算平均值
    参数:
        values: 数值列表
    返回:
        平均值（保留两位小数）
    """
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)

def calculate_median(values: List[float]) -> float:
    """
    计算中位数
    参数:
        values: 数值列表
    返回:
        中位数
    """
    if not values:
        return 0.0
    return np.median(values)

def calculate_std(values: List[float]) -> float:
    """
    计算标准差
    参数:
        values: 数值列表
    返回:
        标准差（保留两位小数）
    """
    if not values or len(values) == 1:
        return 0.0
    return round(np.std(values), 2)

# 成绩转换函数
def score_to_grade(score: float) -> str:
    """
    将分数转换为等级
    参数:
        score: 分数
    返回:
        等级
    """
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"

def calculate_gpa(score: float) -> float:
    """
    计算GPA
    参数:
        score: 分数
    返回:
        GPA值
    """
    if score >= 90:
        return 4.0
    elif score >= 85:
        return 3.7
    elif score >= 82:
        return 3.3
    elif score >= 78:
        return 3.0
    elif score >= 75:
        return 2.7
    elif score >= 72:
        return 2.3
    elif score >= 68:
        return 2.0
    elif score >= 64:
        return 1.5
    elif score >= 60:
        return 1.0
    else:
        return 0.0

# 数据脱敏函数
def mask_sensitive_data(data: str, mask_length: int = 4) -> str:
    """
    对敏感数据进行脱敏处理
    参数:
        data: 敏感数据
        mask_length: 脱敏的长度
    返回:
        脱敏后的数据
    """
    if not data:
        return data
    
    # 邮箱脱敏
    if "@" in data:
        parts = data.split("@")
        if len(parts[0]) > 2:
            parts[0] = parts[0][0] + "*" * (len(parts[0]) - 2) + parts[0][-1]
        return "@".join(parts)
    
    # 手机号脱敏
    if data.isdigit() and len(data) == 11:
        return data[:3] + "*" * 4 + data[7:]
    
    # 身份证号脱敏
    if len(data) == 18:
        return data[:6] + "*" * 8 + data[14:]
    
    # 其他字符串脱敏
    if len(data) > mask_length:
        return data[:2] + "*" * (len(data) - 4) + data[-2:]
    
    return data

# 缓存装饰器
def cached(timeout: int = 60):
    """
    函数结果缓存装饰器
    参数:
        timeout: 缓存超时时间（秒）
    返回:
        装饰器函数
    """
    cache = {}
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # 检查缓存是否有效
            current_time = time.time()
            if key in cache:
                value, timestamp = cache[key]
                if current_time - timestamp < timeout:
                    return value
            
            # 计算结果并缓存
            value = func(*args, **kwargs)
            cache[key] = (value, current_time)
            
            # 清理过期缓存
            for k, (_, t) in list(cache.items()):
                if current_time - t >= timeout:
                    del cache[k]
            
            return value
        
        return wrapper
    
    return decorator

# 重试装饰器
def retry(max_attempts: int = 3, delay: int = 1):
    """
    函数重试装饰器
    参数:
        max_attempts: 最大尝试次数
        delay: 重试间隔（秒）
    返回:
        装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    time.sleep(delay)
        
        return wrapper
    
    return decorator

# 排序函数
def sort_by_field(items: List[Dict[str, Any]], field: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    按指定字段对列表进行排序
    参数:
        items: 要排序的列表
        field: 排序字段
        reverse: 是否降序排列
    返回:
        排序后的列表
    """
    return sorted(items, key=lambda x: x.get(field, ""), reverse=reverse)

# 过滤函数
def filter_by_field(items: List[Dict[str, Any]], field: str, value: Any) -> List[Dict[str, Any]]:
    """
    按指定字段对列表进行过滤
    参数:
        items: 要过滤的列表
        field: 过滤字段
        value: 过滤值
    返回:
        过滤后的列表
    """
    return [item for item in items if item.get(field) == value]

# 搜索函数
def search_in_fields(items: List[Dict[str, Any]], keyword: str, fields: List[str]) -> List[Dict[str, Any]]:
    """
    在指定字段中搜索关键词
    参数:
        items: 要搜索的列表
        keyword: 搜索关键词
        fields: 搜索字段列表
    返回:
        搜索结果列表
    """
    if not keyword:
        return items
    
    keyword = keyword.lower()
    result = []
    
    for item in items:
        for field in fields:
            if field in item and item[field] is not None:
                if keyword in str(item[field]).lower():
                    result.append(item)
                    break
    
    return result

# 数据转换函数
def model_to_dict(model) -> Dict[str, Any]:
    """
    将SQLAlchemy模型转换为字典
    参数:
        model: SQLAlchemy模型实例
    返回:
        模型的字典表示
    """
    result = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        if isinstance(value, datetime.datetime):
            result[column.name] = value.isoformat()
        elif isinstance(value, datetime.date):
            result[column.name] = value.isoformat()
        else:
            result[column.name] = value
    
    return result

def models_to_dicts(models) -> List[Dict[str, Any]]:
    """
    将SQLAlchemy模型列表转换为字典列表
    参数:
        models: SQLAlchemy模型实例列表
    返回:
        模型的字典表示列表
    """
    return [model_to_dict(model) for model in models]

# 统计分析函数
def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    计算数值列表的统计信息
    参数:
        values: 数值列表
    返回:
        包含统计信息的字典
    """
    if not values:
        return {
            "count": 0,
            "min": 0.0,
            "max": 0.0,
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0
        }
    
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": calculate_average(values),
        "median": calculate_median(values),
        "std": calculate_std(values)
    }

def calculate_score_distribution(scores: List[float]) -> Dict[str, int]:
    """
    计算分数分布
    参数:
        scores: 分数列表
    返回:
        分数分布统计
    """
    distribution = {
        "优秀(90-100)": 0,
        "良好(80-89)": 0,
        "中等(70-79)": 0,
        "及格(60-69)": 0,
        "不及格(0-59)": 0
    }
    
    for score in scores:
        if score >= 90:
            distribution["优秀(90-100)"] += 1
        elif score >= 80:
            distribution["良好(80-89)"] += 1
        elif score >= 70:
            distribution["中等(70-79)"] += 1
        elif score >= 60:
            distribution["及格(60-69)"] += 1
        else:
            distribution["不及格(0-59)"] += 1
    
    return distribution

# 生成唯一会话ID
def generate_session_id() -> str:
    """
    生成唯一的会话ID
    返回:
        会话ID字符串
    """
    return generate_uuid()

# 清理字符串
def clean_string(s: str) -> str:
    """
    清理字符串，去除首尾空白字符和换行符
    参数:
        s: 输入字符串
    返回:
        清理后的字符串
    """
    if s is None:
        return ""
    return s.strip()

# 检查值是否在范围内
def is_in_range(value: float, min_value: float, max_value: float) -> bool:
    """
    检查值是否在指定范围内
    参数:
        value: 要检查的值
        min_value: 最小值
        max_value: 最大值
    返回:
        是否在范围内
    """
    return min_value <= value <= max_value

# 生成随机字符串
def generate_random_string(length: int = 8) -> str:
    """
    生成随机字符串
    参数:
        length: 字符串长度
    返回:
        随机字符串
    """
    import random
    import string
    
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# 计算排名
def calculate_ranking(values: List[float], target: float) -> int:
    """
    计算目标值在列表中的排名（降序）
    参数:
        values: 数值列表
        target: 目标值
    返回:
        排名（从1开始）
    """
    sorted_values = sorted(values, reverse=True)
    if target in sorted_values:
        return sorted_values.index(target) + 1
    # 如果目标值不在列表中，找到合适的位置
    for i, value in enumerate(sorted_values):
        if target > value:
            return i + 1
    return len(sorted_values) + 1

# 计算相似度
def calculate_similarity(str1: str, str2: str) -> float:
    """
    计算两个字符串的相似度（使用编辑距离）
    参数:
        str1: 第一个字符串
        str2: 第二个字符串
    返回:
        相似度（0-1之间的值，值越大表示越相似）
    """
    # 简单实现，使用编辑距离算法
    if not str1 and not str2:
        return 1.0
    if not str1 or not str2:
        return 0.0
    
    # 计算编辑距离
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
    
    # 计算相似度（编辑距离越小，相似度越高）
    max_len = max(m, n)
    similarity = 1 - dp[m][n] / max_len
    
    return similarity