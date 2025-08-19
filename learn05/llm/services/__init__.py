#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI服务模块
包含备课助手、课堂AI助手、成绩管理等核心AI服务
"""

from .lesson_prep_service import (
    LessonPrepService,
    MaterialAnalysisAgent,
    LessonPlanningAgent,
    StudentAnalysisAgent,
    TeachingMaterial,
    LessonPlan,
    StudentProfile
)

from .classroom_ai_service import (
    ClassroomAIService,
    RealTimeLearningAgent,
    ExperimentDesignAgent,
    AIApplicationAgent,
    RealTimeLearningData,
    ClassroomMetrics,
    ExperimentDesign,
    AIApplication,
    LearningStatus,
    AttentionLevel
)

from .grade_management_service import (
    GradeManagementService,
    GradeInputAgent,
    GradeAnalysisAgent,
    PersonalizedGuidanceAgent,
    TutoringPlanAgent,
    StudentGrade,
    GradeAnalysis,
    TutoringPlan,
    GradeLevel,
    SubjectType
)

__all__ = [
    # 备课助手服务
    'LessonPrepService',
    'MaterialAnalysisAgent',
    'LessonPlanningAgent',
    'StudentAnalysisAgent',
    'TeachingMaterial',
    'LessonPlan',
    'StudentProfile',
    
    # 课堂AI助手相关
    'ClassroomAIService',
    'RealTimeLearningAgent',
    'ExperimentDesignAgent',
    'AIApplicationAgent',
    'RealTimeLearningData',
    'ClassroomMetrics',
    'ExperimentDesign',
    'AIApplication',
    'LearningStatus',
    'AttentionLevel',
    
    # 成绩管理服务
    'GradeManagementService',
    'GradeInputAgent',
    'GradeAnalysisAgent',
    'PersonalizedGuidanceAgent',
    'TutoringPlanAgent',
    'StudentGrade',
    'GradeAnalysis',
    'TutoringPlan',
    'GradeLevel',
    'SubjectType'
]