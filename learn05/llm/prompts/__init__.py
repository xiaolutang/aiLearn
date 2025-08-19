# -*- coding: utf-8 -*-
"""
智能教学助手提示词模板库
提供各种场景下的优化提示词模板
"""

from .base_prompts import BasePromptTemplate, PromptType
from .teaching_prompts import TeachingPrompts
from .learning_prompts import LearningPrompts
from .tutoring_prompts import TutoringPrompts
from .classroom_prompts import ClassroomPrompts
from .prompt_manager import PromptManager

__all__ = [
    'BasePromptTemplate',
    'PromptType',
    'TeachingPrompts',
    'LearningPrompts',
    'TutoringPrompts',
    'ClassroomPrompts',
    'PromptManager'
]

__version__ = '1.0.0'
__author__ = 'AI Teaching Assistant Team'
__description__ = '智能教学助手提示词模板库'