# -*- coding: utf-8 -*-
"""
提示词工具模块
提供提示词模板、格式化和优化相关功能
"""

import logging
from typing import Dict, List, Optional, Any, Union

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptTemplates:
    """提示词模板集合"""
    
    # SQL相关模板
    SQL_GENERATION = """
    你是一个SQL查询专家。请根据以下表结构，将自然语言查询转换为SQL查询:
    {table_info}
    自然语言查询: {natural_language}
    请仅返回SQL查询语句，不要包含其他解释。
    """
    
    SQL_EXECUTION_RESULT_EXPLANATION = """
    你是一个数据分析专家。请根据以下SQL查询和结果，给出清晰的解释:
    SQL查询: {sql_query}
    查询结果: {result}
    请用简洁明了的语言解释查询结果，避免使用技术术语。
    """
    
    # 成绩分析相关模板
    STUDENT_PERFORMANCE_ANALYSIS = """
    你是一位教育专家。请根据以下学生的成绩数据，分析其学习情况并提供个性化建议:
    学生信息: {student_info}
    成绩数据: {grade_data}
    历史表现: {historical_data}
    
    请包含以下内容:
    1. 总体成绩概况和学习状态评估
    2. 各学科表现分析(优势与劣势)
    3. 与班级/年级平均水平的对比
    4. 学习趋势分析
    5. 针对性的学习建议和改进方案
    6. 推荐的练习资源和学习方法
    
    请使用友好、鼓励的语气，避免使用过于专业的教育术语。
    """
    
    CLASS_PERFORMANCE_ANALYSIS = """
    你是一位教育专家。请根据以下班级的成绩数据，进行全面分析并提供教学建议:
    班级信息: {class_info}
    成绩数据: {grade_data}
    与其他班级对比: {comparison_data}
    
    请包含以下内容:
    1. 班级整体成绩概况
    2. 各学科表现分析
    3. 成绩分布情况(高分段、中等、低分段学生比例)
    4. 与其他班级的对比分析
    5. 班级学习特点总结
    6. 针对班级整体的教学建议和改进措施
    
    请使用专业、客观的语气，提供具体可行的建议。
    """
    
    # 辅导方案生成相关模板
    PERSONALIZED_COACHING_PLAN = """
    你是一位教育专家。请根据以下学生的学习数据，生成个性化的辅导方案:
    学生信息: {student_info}
    学习数据: {learning_data}
    学习目标: {learning_goals}
    学习偏好: {learning_preferences}
    
    辅导方案应包含:
    1. 短期目标(1-2周)
    2. 中期目标(1个月)
    3. 长期目标(3个月)
    4. 每周学习计划
    5. 推荐的学习资源和工具
    6. 学习方法指导
    7. 家长/教师配合建议
    
    请确保方案具体、可操作，符合学生的学习能力和特点。
    """
    
    # 作业/练习生成相关模板
    PRACTICE_QUESTION_GENERATION = """
    你是一位经验丰富的教师。请根据以下学习内容和学生水平，生成针对性的练习题:
    学习内容: {content}
    学生水平: {student_level}
    题目数量: {num_questions}
    难度分布: {difficulty_distribution}
    
    请生成的练习题包含:
    1. 题目内容
    2. 难度级别
    3. 参考答案
    4. 解题思路提示(可选)
    
    请确保题目能够有效检验学生对知识点的掌握程度，并且符合学生当前的学习水平。
    """


def format_prompt(prompt_template: str, **kwargs) -> str:
    """格式化提示词模板
    
    Args:
        prompt_template: 提示词模板字符串
        **kwargs: 要替换的变量
        
    Returns:
        str: 格式化后的提示词
    """
    try:
        formatted_prompt = prompt_template.format(**kwargs)
        return formatted_prompt
    except KeyError as e:
        logger.error(f"提示词格式化失败: 缺少必要的变量 {e}")
        raise
    except Exception as e:
        logger.error(f"提示词格式化失败: {e}")
        raise


def optimize_prompt_for_sql_generation(natural_language: str, table_info: str) -> str:
    """优化SQL生成的提示词
    
    Args:
        natural_language: 自然语言查询
        table_info: 表结构信息
        
    Returns:
        str: 优化后的提示词
    """
    prompt = format_prompt(
        PromptTemplates.SQL_GENERATION,
        table_info=table_info,
        natural_language=natural_language
    )
    return prompt


def optimize_prompt_for_student_analysis(student_info: str, grade_data: str, historical_data: str = "") -> str:
    """优化学生分析的提示词
    
    Args:
        student_info: 学生信息
        grade_data: 成绩数据
        historical_data: 历史表现数据(可选)
        
    Returns:
        str: 优化后的提示词
    """
    prompt = format_prompt(
        PromptTemplates.STUDENT_PERFORMANCE_ANALYSIS,
        student_info=student_info,
        grade_data=grade_data,
        historical_data=historical_data
    )
    return prompt


def optimize_prompt_for_class_analysis(class_info: str, grade_data: str, comparison_data: str = "") -> str:
    """优化班级分析的提示词
    
    Args:
        class_info: 班级信息
        grade_data: 成绩数据
        comparison_data: 与其他班级对比数据(可选)
        
    Returns:
        str: 优化后的提示词
    """
    prompt = format_prompt(
        PromptTemplates.CLASS_PERFORMANCE_ANALYSIS,
        class_info=class_info,
        grade_data=grade_data,
        comparison_data=comparison_data
    )
    return prompt


def optimize_prompt_for_coaching_plan(student_info: str, learning_data: str, learning_goals: str, learning_preferences: str = "") -> str:
    """优化辅导方案生成的提示词
    
    Args:
        student_info: 学生信息
        learning_data: 学习数据
        learning_goals: 学习目标
        learning_preferences: 学习偏好(可选)
        
    Returns:
        str: 优化后的提示词
    """
    prompt = format_prompt(
        PromptTemplates.PERSONALIZED_COACHING_PLAN,
        student_info=student_info,
        learning_data=learning_data,
        learning_goals=learning_goals,
        learning_preferences=learning_preferences
    )
    return prompt


def optimize_prompt_for_practice_generation(content: str, student_level: str, num_questions: int, difficulty_distribution: str = "简单:30%, 中等:50%, 困难:20%") -> str:
    """优化练习生成的提示词
    
    Args:
        content: 学习内容
        student_level: 学生水平
        num_questions: 题目数量
        difficulty_distribution: 难度分布(可选)
        
    Returns:
        str: 优化后的提示词
    """
    prompt = format_prompt(
        PromptTemplates.PRACTICE_QUESTION_GENERATION,
        content=content,
        student_level=student_level,
        num_questions=num_questions,
        difficulty_distribution=difficulty_distribution
    )
    return prompt