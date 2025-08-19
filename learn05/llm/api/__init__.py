#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI服务API模块
提供智能教学助手的统一API接口
"""

from .ai_service_api import (
    app,
    ai_service_manager,
    BaseRequest,
    BaseResponse,
    MaterialAnalysisRequest,
    LessonPlanRequest,
    StudentAnalysisRequest,
    RealTimeLearningRequest,
    ExperimentDesignRequest,
    AIApplicationRequest,
    BatchGradeRequest,
    GradeAnalysisRequest,
    PersonalizedGuidanceRequest,
    TutoringPlanRequest,
    SmartRecognitionRequest
)

__all__ = [
    'app',
    'ai_service_manager',
    'BaseRequest',
    'BaseResponse',
    'MaterialAnalysisRequest',
    'LessonPlanRequest',
    'StudentAnalysisRequest',
    'RealTimeLearningRequest',
    'ExperimentDesignRequest',
    'AIApplicationRequest',
    'BatchGradeRequest',
    'GradeAnalysisRequest',
    'PersonalizedGuidanceRequest',
    'TutoringPlanRequest',
    'SmartRecognitionRequest'
]