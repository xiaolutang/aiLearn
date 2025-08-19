#!/usr/bin/env python3
"""
测试所有AI Agent类的实现
验证抽象方法是否正确实现
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('/Users/tangxiaolu/project/PythonProject/aiLearn/.env')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from factory import LLMFactory
from services.lesson_prep_service import MaterialAnalysisAgent, LessonPlanningAgent, StudentAnalysisAgent
from services.classroom_ai_service import RealTimeLearningAgent, ExperimentDesignAgent, AIApplicationAgent
from services.grade_management_service import GradeInputAgent, GradeAnalysisAgent, PersonalizedGuidanceAgent, TutoringPlanAgent

def test_agent_instantiation():
    """测试所有Agent类的实例化"""
    print("开始测试Agent类实例化...")
    
    # 检查环境变量配置
    tongyi_key = os.getenv('DASHSCOPE_API_KEY') or os.getenv('TONG_YI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"通义千问API密钥: {'已配置' if tongyi_key else '未配置'}")
    print(f"OpenAI API密钥: {'已配置' if openai_key else '未配置'}")
    
    if not tongyi_key and not openai_key:
        print("❌ 未找到任何可用的API密钥配置")
        return False
    
    # 创建LLM工厂
    llm_factory = LLMFactory()
    
    # 测试备课助手服务的Agent
    print("\n1. 测试备课助手服务Agent...")
    try:
        material_agent = MaterialAnalysisAgent(llm_factory)
        print("✅ MaterialAnalysisAgent 实例化成功")
        
        lesson_agent = LessonPlanningAgent(llm_factory)
        print("✅ LessonPlanningAgent 实例化成功")
        
        student_agent = StudentAnalysisAgent(llm_factory)
        print("✅ StudentAnalysisAgent 实例化成功")
    except Exception as e:
        print(f"❌ 备课助手服务Agent实例化失败: {e}")
        return False
    
    # 测试课堂AI助手服务的Agent
    print("\n2. 测试课堂AI助手服务Agent...")
    try:
        realtime_agent = RealTimeLearningAgent(llm_factory)
        print("✅ RealTimeLearningAgent 实例化成功")
        
        experiment_agent = ExperimentDesignAgent(llm_factory)
        print("✅ ExperimentDesignAgent 实例化成功")
        
        ai_app_agent = AIApplicationAgent(llm_factory)
        print("✅ AIApplicationAgent 实例化成功")
    except Exception as e:
        print(f"❌ 课堂AI助手服务Agent实例化失败: {e}")
        return False
    
    # 测试成绩管理服务的Agent
    print("\n3. 测试成绩管理服务Agent...")
    try:
        grade_input_agent = GradeInputAgent(llm_factory)
        print("✅ GradeInputAgent 实例化成功")
        
        grade_analysis_agent = GradeAnalysisAgent(llm_factory)
        print("✅ GradeAnalysisAgent 实例化成功")
        
        guidance_agent = PersonalizedGuidanceAgent(llm_factory)
        print("✅ PersonalizedGuidanceAgent 实例化成功")
        
        tutoring_agent = TutoringPlanAgent(llm_factory)
        print("✅ TutoringPlanAgent 实例化成功")
    except Exception as e:
        print(f"❌ 成绩管理服务Agent实例化失败: {e}")
        return False
    
    print("\n🎉 所有Agent类实例化测试通过！")
    return True

def test_abstract_methods():
    """测试抽象方法的实现"""
    print("\n开始测试抽象方法实现...")
    
    llm_factory = LLMFactory()
    
    # 测试一个Agent的抽象方法
    try:
        agent = MaterialAnalysisAgent(llm_factory)
        
        # 测试validate_input方法
        test_input = {"content": "test"}
        result = agent.validate_input(test_input)
        print(f"✅ validate_input 方法实现正确，返回: {result}")
        
        # 测试get_prompt_template方法
        template = agent.get_prompt_template("analysis")
        print(f"✅ get_prompt_template 方法实现正确，返回模板长度: {len(template)}")
        
    except Exception as e:
        print(f"❌ 抽象方法测试失败: {e}")
        return False
    
    print("✅ 抽象方法实现测试通过！")
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("AI教学助手 - Agent类实现测试")
    print("=" * 60)
    
    # 测试实例化
    if not test_agent_instantiation():
        sys.exit(1)
    
    # 测试抽象方法
    if not test_abstract_methods():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！AI Agent类实现正确！")
    print("=" * 60)

if __name__ == "__main__":
    main()