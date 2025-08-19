#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手AI服务测试脚本
用于验证各个AI服务模块的基本功能
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from factory import LLMFactory
from services.lesson_prep_service import LessonPrepService
from services.classroom_ai_service import ClassroomAIService
from services.grade_management_service import GradeManagementService

class AIServiceTester:
    """AI服务测试器"""
    
    def __init__(self):
        self.llm_factory = LLMFactory()
        self.lesson_prep_service = LessonPrepService(self.llm_factory)
        self.classroom_ai_service = ClassroomAIService(self.llm_factory)
        self.grade_management_service = GradeManagementService(self.llm_factory)
    
    async def test_lesson_prep_service(self):
        """测试备课助手服务"""
        print("\n=== 测试备课助手服务 ===")
        
        try:
            # 测试教材分析
            print("\n1. 测试教材分析...")
            material_data = {
                'content': '本章节介绍细胞的基本结构，包括细胞膜、细胞质、细胞核等组成部分。',
                'subject': '生物',
                'grade': '高一',
                'analysis_type': 'comprehensive'
            }
            
            result = await self.lesson_prep_service.analyze_material(material_data)
            print(f"教材分析结果: {result['success']}")
            if result['success']:
                print(f"分析内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
            # 测试课程计划创建
            print("\n2. 测试课程计划创建...")
            lesson_data = {
                'subject': '生物',
                'topic': '细胞结构',
                'grade': '高一',
                'duration': 45,
                'objectives': ['理解细胞基本结构', '掌握各组成部分功能']
            }
            
            result = await self.lesson_prep_service.create_lesson_plan(lesson_data)
            print(f"课程计划创建结果: {result['success']}")
            if result['success']:
                print(f"计划内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
            # 测试学情分析
            print("\n3. 测试学情分析...")
            student_data = {
                'student_profiles': [
                    {'student_id': '001', 'name': '张三', 'grade': '高一', 'previous_scores': [85, 78, 92]},
                    {'student_id': '002', 'name': '李四', 'grade': '高一', 'previous_scores': [76, 82, 79]}
                ],
                'subject': '生物',
                'analysis_focus': ['基础知识掌握', '学习能力评估']
            }
            
            result = await self.lesson_prep_service.analyze_student_situation(student_data)
            print(f"学情分析结果: {result['success']}")
            if result['success']:
                print(f"分析内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
        except Exception as e:
            print(f"备课助手服务测试失败: {str(e)}")
    
    async def test_classroom_ai_service(self):
        """测试课堂AI助手服务"""
        print("\n=== 测试课堂AI助手服务 ===")
        
        try:
            # 测试实时学情分析
            print("\n1. 测试实时学情分析...")
            classroom_data = {
                'classroom_data': {
                    'class_id': 'class_001',
                    'subject': '生物',
                    'topic': '细胞结构',
                    'duration': 30
                },
                'analysis_type': 'real_time',
                'student_interactions': [
                    {'student_id': '001', 'interaction_type': 'question', 'content': '细胞膜的作用是什么？'},
                    {'student_id': '002', 'interaction_type': 'answer', 'content': '控制物质进出细胞'}
                ]
            }
            
            result = await self.classroom_ai_service.analyze_real_time_learning(classroom_data)
            print(f"实时学情分析结果: {result['success']}")
            if result['success']:
                print(f"分析内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
            # 测试实验设计
            print("\n2. 测试实验设计...")
            experiment_data = {
                'subject': '生物',
                'topic': '观察细胞结构',
                'grade': '高一',
                'objectives': ['观察植物细胞结构', '识别细胞各部分'],
                'constraints': {'time': 45, 'equipment': ['显微镜', '载玻片']}
            }
            
            result = await self.classroom_ai_service.design_experiment(experiment_data)
            print(f"实验设计结果: {result['success']}")
            if result['success']:
                print(f"设计内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
            # 测试AI应用推荐
            print("\n3. 测试AI应用推荐...")
            ai_app_data = {
                'teaching_context': {
                    'subject': '生物',
                    'grade': '高一',
                    'topic': '细胞结构',
                    'class_size': 40
                },
                'subject': '生物',
                'grade': '高一',
                'application_type': 'interactive'
            }
            
            result = await self.classroom_ai_service.recommend_ai_applications(ai_app_data)
            print(f"AI应用推荐结果: {result['success']}")
            if result['success']:
                print(f"推荐内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
        except Exception as e:
            print(f"课堂AI助手服务测试失败: {str(e)}")
    
    async def test_grade_management_service(self):
        """测试成绩管理服务"""
        print("\n=== 测试成绩管理服务 ===")
        
        try:
            # 测试批量成绩录入
            print("\n1. 测试批量成绩录入...")
            grade_data = {
                'grades': [
                    {
                        'student_id': '001',
                        'student_name': '张三',
                        'subject': '生物',
                        'score': 85,
                        'max_score': 100,
                        'exam_type': 'quiz',
                        'exam_date': datetime.now().isoformat()
                    },
                    {
                        'student_id': '002',
                        'student_name': '李四',
                        'subject': '生物',
                        'score': 78,
                        'max_score': 100,
                        'exam_type': 'quiz',
                        'exam_date': datetime.now().isoformat()
                    }
                ],
                'validation_rules': {'min_score': 0, 'max_score': 100}
            }
            
            result = await self.grade_management_service.process_batch_grades(grade_data)
            print(f"批量成绩录入结果: {result['success']}")
            if result['success']:
                print(f"处理结果: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
            # 测试成绩分析
            print("\n2. 测试成绩分析...")
            analysis_data = {
                'grades': grade_data['grades'],
                'analysis_type': 'comprehensive',
                'period': '本学期'
            }
            
            result = await self.grade_management_service.analyze_grades(analysis_data)
            print(f"成绩分析结果: {result['success']}")
            if result['success']:
                print(f"分析结果: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
            # 测试个性化指导
            print("\n3. 测试个性化指导...")
            guidance_data = {
                'student_profile': {
                    'student_id': '001',
                    'grade': '高一',
                    'learning_style': 'visual'
                },
                'grade_analysis': {
                    'average_score': 85,
                    'strength_subjects': ['生物'],
                    'weakness_subjects': ['数学'],
                    'trend': '上升'
                },
                'learning_preferences': {
                    'learning_style': 'visual',
                    'interests': ['科学实验', '自然观察']
                }
            }
            
            result = await self.grade_management_service.generate_personalized_guidance(guidance_data)
            print(f"个性化指导结果: {result['success']}")
            if result['success']:
                print(f"指导内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
            # 测试辅导方案创建
            print("\n4. 测试辅导方案创建...")
            tutoring_data = {
                'student_info': {
                    'student_id': '001',
                    'name': '张三',
                    'grade': '高一'
                },
                'subject': '数学',
                'current_level': 'beginner',
                'target_level': 'intermediate',
                'available_time': 3
            }
            
            result = await self.grade_management_service.create_tutoring_plan(tutoring_data)
            print(f"辅导方案创建结果: {result['success']}")
            if result['success']:
                print(f"方案内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
        except Exception as e:
            print(f"成绩管理服务测试失败: {str(e)}")
    
    async def test_smart_recognition(self):
        """测试智能识别功能"""
        print("\n=== 测试智能识别功能 ===")
        
        try:
            recognition_data = {
                'image_path': '/path/to/grade_sheet.jpg',
                'type': 'handwritten'
            }
            
            result = await self.grade_management_service.smart_grade_recognition(recognition_data)
            print(f"智能识别结果: {result['success']}")
            if result['success']:
                print(f"识别内容: {json.dumps(result['data'], ensure_ascii=False, indent=2)[:200]}...")
            
        except Exception as e:
            print(f"智能识别测试失败: {str(e)}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("开始AI服务功能测试...")
        print(f"测试时间: {datetime.now().isoformat()}")
        
        # 运行各项测试
        await self.test_lesson_prep_service()
        await self.test_classroom_ai_service()
        await self.test_grade_management_service()
        await self.test_smart_recognition()
        
        print("\n=== 测试完成 ===")
        print("所有AI服务模块基本功能测试完成")
        print("注意: 实际LLM调用可能需要配置有效的API密钥")

async def main():
    """主函数"""
    tester = AIServiceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())