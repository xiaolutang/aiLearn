# -*- coding: utf-8 -*-
"""
提示词模板单元测试
测试各种提示词模板的生成和优化功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from llm.prompts.base_prompts import BasePromptTemplate
from llm.prompts.teaching_prompts import TeachingPrompts
from llm.prompts.learning_prompts import LearningPrompts
from llm.prompts.tutoring_prompts import TutoringPrompts
from llm.prompts.classroom_prompts import ClassroomPrompts
from llm.prompts.prompt_manager import PromptManager
from test_config import (
    MOCK_STUDENT_DATA,
    MOCK_GRADE_DATA,
    TEST_DATA,
    TEST_CONFIG
)


class TestBasePromptTemplate:
    """测试基础提示词模板类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.template = BasePromptTemplate()
    
    def test_template_initialization(self):
        """测试模板初始化"""
        assert hasattr(self.template, 'templates')
        assert isinstance(self.template.templates, dict)
        assert hasattr(self.template, 'variables')
        assert isinstance(self.template.variables, dict)
    
    def test_add_template(self):
        """测试添加模板"""
        template_name = "test_template"
        template_content = "这是一个测试模板，变量：{variable1}，{variable2}"
        
        self.template.add_template(template_name, template_content)
        
        assert template_name in self.template.templates
        assert self.template.templates[template_name] == template_content
    
    def test_get_template(self):
        """测试获取模板"""
        template_name = "test_template"
        template_content = "测试模板内容"
        
        self.template.add_template(template_name, template_content)
        retrieved_template = self.template.get_template(template_name)
        
        assert retrieved_template == template_content
    
    def test_get_nonexistent_template(self):
        """测试获取不存在的模板"""
        with pytest.raises(KeyError):
            self.template.get_template("nonexistent_template")
    
    def test_format_template(self):
        """测试格式化模板"""
        template_name = "greeting_template"
        template_content = "你好，{name}！今天是{date}。"
        
        self.template.add_template(template_name, template_content)
        
        formatted = self.template.format_template(
            template_name,
            name="张三",
            date="2024年1月15日"
        )
        
        expected = "你好，张三！今天是2024年1月15日。"
        assert formatted == expected
    
    def test_format_template_missing_variables(self):
        """测试格式化模板时缺少变量"""
        template_name = "incomplete_template"
        template_content = "你好，{name}！今天是{date}。"
        
        self.template.add_template(template_name, template_content)
        
        with pytest.raises(KeyError):
            self.template.format_template(template_name, name="张三")
    
    def test_list_templates(self):
        """测试列出所有模板"""
        self.template.add_template("template1", "内容1")
        self.template.add_template("template2", "内容2")
        
        template_list = self.template.list_templates()
        
        assert "template1" in template_list
        assert "template2" in template_list
        assert len(template_list) >= 2
    
    def test_validate_template(self):
        """测试验证模板"""
        valid_template = "你好，{name}！"
        invalid_template = "你好，{name！"  # 缺少右括号
        
        assert self.template.validate_template(valid_template) is True
        assert self.template.validate_template(invalid_template) is False


class TestTeachingPrompts:
    """测试教学提示词模板类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.prompts = TeachingPrompts()
    
    def test_material_analysis_prompt(self):
        """测试教材分析提示词"""
        prompt = self.prompts.get_material_analysis_prompt(
            content=TEST_DATA["content"],
            subject=TEST_DATA["subject"],
            grade_level=TEST_DATA["grade_level"]
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert TEST_DATA["subject"] in prompt
        assert TEST_DATA["grade_level"] in prompt
        assert "分析" in prompt
    
    def test_knowledge_extraction_prompt(self):
        """测试知识点提取提示词"""
        prompt = self.prompts.get_knowledge_extraction_prompt(
            content=TEST_DATA["content"],
            subject=TEST_DATA["subject"]
        )
        
        assert isinstance(prompt, str)
        assert "知识点" in prompt
        assert "提取" in prompt
        assert TEST_DATA["subject"] in prompt
    
    def test_difficulty_analysis_prompt(self):
        """测试难度分析提示词"""
        prompt = self.prompts.get_difficulty_analysis_prompt(
            content=TEST_DATA["content"],
            target_grade=TEST_DATA["grade_level"]
        )
        
        assert isinstance(prompt, str)
        assert "难度" in prompt
        assert "分析" in prompt
        assert TEST_DATA["grade_level"] in prompt
    
    def test_learning_objectives_prompt(self):
        """测试学习目标生成提示词"""
        prompt = self.prompts.get_learning_objectives_prompt(
            content=TEST_DATA["content"],
            subject=TEST_DATA["subject"],
            duration="45分钟"
        )
        
        assert isinstance(prompt, str)
        assert "学习目标" in prompt
        assert "45分钟" in prompt
        assert TEST_DATA["subject"] in prompt
    
    def test_prerequisite_analysis_prompt(self):
        """测试前置知识分析提示词"""
        prompt = self.prompts.get_prerequisite_analysis_prompt(
            content=TEST_DATA["content"],
            subject=TEST_DATA["subject"]
        )
        
        assert isinstance(prompt, str)
        assert "前置知识" in prompt or "先修" in prompt
        assert "分析" in prompt
    
    def test_teaching_suggestions_prompt(self):
        """测试教学建议提示词"""
        prompt = self.prompts.get_teaching_suggestions_prompt(
            content=TEST_DATA["content"],
            student_level="中等",
            class_size=35
        )
        
        assert isinstance(prompt, str)
        assert "教学建议" in prompt or "教学方法" in prompt
        assert "中等" in prompt
        assert "35" in prompt


class TestLearningPrompts:
    """测试学情分析提示词模板类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.prompts = LearningPrompts()
    
    def test_individual_analysis_prompt(self):
        """测试个人学情分析提示词"""
        student_data = MOCK_STUDENT_DATA[0]
        grade_data = MOCK_GRADE_DATA[:3]  # 取前3条成绩数据
        
        prompt = self.prompts.get_individual_analysis_prompt(
            student_info=student_data,
            grade_history=grade_data,
            analysis_period="本学期"
        )
        
        assert isinstance(prompt, str)
        assert student_data["name"] in prompt
        assert "个人" in prompt or "学情" in prompt
        assert "分析" in prompt
        assert "本学期" in prompt
    
    def test_class_analysis_prompt(self):
        """测试班级学情分析提示词"""
        prompt = self.prompts.get_class_analysis_prompt(
            class_id="CLASS_3A",
            student_count=30,
            grade_data=MOCK_GRADE_DATA,
            subject="数学"
        )
        
        assert isinstance(prompt, str)
        assert "CLASS_3A" in prompt
        assert "30" in prompt
        assert "班级" in prompt
        assert "数学" in prompt
    
    def test_learning_pattern_prompt(self):
        """测试学习模式识别提示词"""
        student_data = MOCK_STUDENT_DATA[0]
        
        prompt = self.prompts.get_learning_pattern_prompt(
            student_info=student_data,
            behavior_data={
                "study_time": "每天2小时",
                "preferred_subjects": ["数学", "物理"],
                "weak_subjects": ["英语"]
            }
        )
        
        assert isinstance(prompt, str)
        assert "学习模式" in prompt or "学习习惯" in prompt
        assert "数学" in prompt
        assert "物理" in prompt
        assert "英语" in prompt
    
    def test_progress_report_prompt(self):
        """测试学习进度报告提示词"""
        prompt = self.prompts.get_progress_report_prompt(
            student_id="STU001",
            time_period="本月",
            subjects=["数学", "语文", "英语"],
            grade_trends={
                "数学": "上升",
                "语文": "稳定",
                "英语": "下降"
            }
        )
        
        assert isinstance(prompt, str)
        assert "STU001" in prompt
        assert "本月" in prompt
        assert "进度" in prompt or "报告" in prompt
        assert "上升" in prompt
        assert "下降" in prompt
    
    def test_comparison_analysis_prompt(self):
        """测试学生对比分析提示词"""
        prompt = self.prompts.get_comparison_analysis_prompt(
            student_ids=["STU001", "STU002"],
            comparison_metrics=["平均分", "进步幅度", "学习稳定性"],
            subject="数学"
        )
        
        assert isinstance(prompt, str)
        assert "STU001" in prompt
        assert "STU002" in prompt
        assert "对比" in prompt or "比较" in prompt
        assert "平均分" in prompt
        assert "数学" in prompt


class TestTutoringPrompts:
    """测试辅导提示词模板类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.prompts = TutoringPrompts()
    
    def test_personalized_plan_prompt(self):
        """测试个性化辅导方案提示词"""
        student_profile = {
            "name": "张三",
            "grade": "高一",
            "weak_subjects": ["数学", "物理"],
            "learning_style": "视觉型",
            "available_time": "每天1小时"
        }
        
        prompt = self.prompts.get_personalized_plan_prompt(
            student_profile=student_profile,
            learning_goals=["提高数学成绩", "掌握物理基础概念"],
            time_frame="一个月"
        )
        
        assert isinstance(prompt, str)
        assert "张三" in prompt
        assert "个性化" in prompt
        assert "辅导" in prompt or "方案" in prompt
        assert "数学" in prompt
        assert "物理" in prompt
        assert "一个月" in prompt
    
    def test_exercise_recommendation_prompt(self):
        """测试练习推荐提示词"""
        prompt = self.prompts.get_exercise_recommendation_prompt(
            subject="数学",
            topic="二次函数",
            difficulty_level="中等",
            student_level="基础薄弱",
            exercise_count=10
        )
        
        assert isinstance(prompt, str)
        assert "数学" in prompt
        assert "二次函数" in prompt
        assert "练习" in prompt or "题目" in prompt
        assert "中等" in prompt
        assert "10" in prompt
    
    def test_study_plan_prompt(self):
        """测试学习计划提示词"""
        prompt = self.prompts.get_study_plan_prompt(
            subjects=["数学", "英语"],
            study_duration="2周",
            daily_time="1.5小时",
            learning_objectives=[
                "掌握函数概念",
                "提高英语阅读理解"
            ]
        )
        
        assert isinstance(prompt, str)
        assert "学习计划" in prompt
        assert "数学" in prompt
        assert "英语" in prompt
        assert "2周" in prompt
        assert "1.5小时" in prompt
    
    def test_learning_path_prompt(self):
        """测试学习路径提示词"""
        prompt = self.prompts.get_learning_path_prompt(
            subject="物理",
            current_level="初级",
            target_level="中级",
            knowledge_gaps=["力学基础", "电学概念"]
        )
        
        assert isinstance(prompt, str)
        assert "学习路径" in prompt
        assert "物理" in prompt
        assert "初级" in prompt
        assert "中级" in prompt
        assert "力学" in prompt
        assert "电学" in prompt
    
    def test_adaptive_difficulty_prompt(self):
        """测试难度自适应提示词"""
        prompt = self.prompts.get_adaptive_difficulty_prompt(
            current_performance=0.75,
            target_accuracy=0.85,
            subject="化学",
            topic="化学反应"
        )
        
        assert isinstance(prompt, str)
        assert "难度" in prompt
        assert "自适应" in prompt or "调整" in prompt
        assert "化学" in prompt
        assert "化学反应" in prompt


class TestClassroomPrompts:
    """测试课堂AI提示词模板类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.prompts = ClassroomPrompts()
    
    def test_question_answering_prompt(self):
        """测试问题回答提示词"""
        prompt = self.prompts.get_question_answering_prompt(
            student_question="什么是光合作用？",
            subject="生物",
            grade_level="初中二年级",
            context="正在学习植物生理"
        )
        
        assert isinstance(prompt, str)
        assert "光合作用" in prompt
        assert "生物" in prompt
        assert "初中二年级" in prompt
        assert "植物生理" in prompt
    
    def test_interactive_content_prompt(self):
        """测试互动内容生成提示词"""
        prompt = self.prompts.get_interactive_content_prompt(
            topic="化学元素周期表",
            interaction_type="问答游戏",
            duration="20分钟",
            participant_count=25
        )
        
        assert isinstance(prompt, str)
        assert "化学元素周期表" in prompt
        assert "问答游戏" in prompt
        assert "互动" in prompt
        assert "20分钟" in prompt
        assert "25" in prompt
    
    def test_engagement_analysis_prompt(self):
        """测试参与度分析提示词"""
        prompt = self.prompts.get_engagement_analysis_prompt(
            class_data={
                "total_students": 30,
                "active_participants": 22,
                "questions_asked": 15,
                "response_rate": 0.73
            },
            lesson_topic="牛顿运动定律"
        )
        
        assert isinstance(prompt, str)
        assert "参与度" in prompt
        assert "分析" in prompt
        assert "30" in prompt
        assert "22" in prompt
        assert "牛顿运动定律" in prompt
    
    def test_real_time_feedback_prompt(self):
        """测试实时反馈提示词"""
        prompt = self.prompts.get_real_time_feedback_prompt(
            student_response="我认为答案是重力加速度",
            correct_answer="重力加速度g=9.8m/s²",
            feedback_style="鼓励性"
        )
        
        assert isinstance(prompt, str)
        assert "重力加速度" in prompt
        assert "反馈" in prompt
        assert "鼓励" in prompt


class TestPromptManager:
    """测试提示词管理器类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.manager = PromptManager()
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert hasattr(self.manager, 'teaching_prompts')
        assert hasattr(self.manager, 'learning_prompts')
        assert hasattr(self.manager, 'tutoring_prompts')
        assert hasattr(self.manager, 'classroom_prompts')
        
        assert isinstance(self.manager.teaching_prompts, TeachingPrompts)
        assert isinstance(self.manager.learning_prompts, LearningPrompts)
        assert isinstance(self.manager.tutoring_prompts, TutoringPrompts)
        assert isinstance(self.manager.classroom_prompts, ClassroomPrompts)
    
    def test_get_prompt_by_category(self):
        """测试按类别获取提示词"""
        # 测试教学类提示词
        teaching_prompt = self.manager.get_prompt(
            category="teaching",
            prompt_type="material_analysis",
            content="测试内容",
            subject="数学",
            grade_level="高一"
        )
        
        assert isinstance(teaching_prompt, str)
        assert len(teaching_prompt) > 0
        
        # 测试学情分析类提示词
        learning_prompt = self.manager.get_prompt(
            category="learning",
            prompt_type="individual_analysis",
            student_info=MOCK_STUDENT_DATA[0],
            grade_history=MOCK_GRADE_DATA[:3],
            analysis_period="本学期"
        )
        
        assert isinstance(learning_prompt, str)
        assert len(learning_prompt) > 0
    
    def test_invalid_category(self):
        """测试无效类别"""
        with pytest.raises(ValueError):
            self.manager.get_prompt(
                category="invalid_category",
                prompt_type="test"
            )
    
    def test_invalid_prompt_type(self):
        """测试无效提示词类型"""
        with pytest.raises(AttributeError):
            self.manager.get_prompt(
                category="teaching",
                prompt_type="invalid_prompt_type"
            )
    
    def test_list_available_prompts(self):
        """测试列出可用提示词"""
        available_prompts = self.manager.list_available_prompts()
        
        assert isinstance(available_prompts, dict)
        assert "teaching" in available_prompts
        assert "learning" in available_prompts
        assert "tutoring" in available_prompts
        assert "classroom" in available_prompts
        
        # 检查每个类别都有提示词列表
        for category, prompts in available_prompts.items():
            assert isinstance(prompts, list)
            assert len(prompts) > 0
    
    def test_optimize_prompt(self):
        """测试提示词优化"""
        original_prompt = "请分析这个学生的成绩"
        
        optimized_prompt = self.manager.optimize_prompt(
            prompt=original_prompt,
            optimization_type="clarity",
            context={
                "subject": "数学",
                "grade_level": "高中",
                "analysis_depth": "详细"
            }
        )
        
        assert isinstance(optimized_prompt, str)
        assert len(optimized_prompt) >= len(original_prompt)
        # 优化后的提示词应该更详细
        assert "数学" in optimized_prompt
        assert "高中" in optimized_prompt
    
    def test_validate_prompt_parameters(self):
        """测试提示词参数验证"""
        # 测试有效参数
        valid_params = {
            "content": "测试内容",
            "subject": "数学",
            "grade_level": "高一"
        }
        
        is_valid = self.manager.validate_prompt_parameters(
            category="teaching",
            prompt_type="material_analysis",
            parameters=valid_params
        )
        
        assert is_valid is True
        
        # 测试缺少必需参数
        invalid_params = {
            "content": "测试内容"
            # 缺少subject和grade_level
        }
        
        is_valid = self.manager.validate_prompt_parameters(
            category="teaching",
            prompt_type="material_analysis",
            parameters=invalid_params
        )
        
        assert is_valid is False
    
    def test_custom_prompt_template(self):
        """测试自定义提示词模板"""
        template_name = "custom_analysis"
        template_content = "请对{subject}学科的{content}进行{analysis_type}分析"
        
        self.manager.add_custom_template(
            category="teaching",
            template_name=template_name,
            template_content=template_content
        )
        
        # 使用自定义模板
        custom_prompt = self.manager.get_prompt(
            category="teaching",
            prompt_type=template_name,
            subject="物理",
            content="力学原理",
            analysis_type="深度"
        )
        
        assert "物理" in custom_prompt
        assert "力学原理" in custom_prompt
        assert "深度" in custom_prompt
    
    def test_prompt_versioning(self):
        """测试提示词版本管理"""
        # 创建提示词的新版本
        template_name = "test_template"
        v1_content = "版本1的提示词内容"
        v2_content = "版本2的改进提示词内容"
        
        self.manager.add_template_version(
            category="teaching",
            template_name=template_name,
            content=v1_content,
            version="1.0"
        )
        
        self.manager.add_template_version(
            category="teaching",
            template_name=template_name,
            content=v2_content,
            version="2.0"
        )
        
        # 获取特定版本
        v1_prompt = self.manager.get_prompt_version(
            category="teaching",
            template_name=template_name,
            version="1.0"
        )
        
        v2_prompt = self.manager.get_prompt_version(
            category="teaching",
            template_name=template_name,
            version="2.0"
        )
        
        assert v1_prompt == v1_content
        assert v2_prompt == v2_content
        assert v1_prompt != v2_prompt


if __name__ == "__main__":
    pytest.main([__file__])