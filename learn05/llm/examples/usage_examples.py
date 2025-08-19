# -*- coding: utf-8 -*-
"""
智能教学助手LLM系统使用示例
展示如何使用各个智能体和功能模块
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# 导入智能体相关模块
from ..agents import (
    AgentManager, 
    TeachingAnalysisAgent, 
    LearningStatusAgent, 
    TutoringPlanAgent,
    ClassroomAIAgent
)

# 导入提示词管理
from ..prompts import PromptManager

# 导入上下文管理
from ..context import (
    ContextManager, 
    SessionManager, 
    MemoryStore,
    SlidingWindowStrategy
)

# 导入性能优化
from ..optimization import (
    OptimizationManager,
    CacheManager,
    PerformanceMonitor,
    optimize,
    cached,
    monitored
)

# 导入LLM客户端
from ..llm_client import LLMClient, LLMConfig

class TeachingAssistantDemo:
    """智能教学助手演示类"""
    
    def __init__(self):
        # 初始化LLM客户端
        self.llm_config = LLMConfig(
            provider="tongyi",
            api_key="your-api-key",
            model="qwen-plus",
            temperature=0.7,
            max_tokens=2000
        )
        self.llm_client = LLMClient(self.llm_config)
        
        # 初始化智能体管理器
        self.agent_manager = AgentManager(self.llm_client)
        
        # 初始化提示词管理器
        self.prompt_manager = PromptManager()
        
        # 初始化上下文管理器
        self.context_manager = ContextManager()
        
        # 初始化会话管理器
        self.session_manager = SessionManager()
        
        # 初始化优化管理器
        self.optimization_manager = OptimizationManager()
        
        print("智能教学助手系统初始化完成")
    
    async def demo_teaching_analysis(self):
        """演示教材分析功能"""
        print("\n=== 教材分析演示 ===")
        
        # 模拟教材内容
        teaching_material = {
            "subject": "数学",
            "grade": "高一",
            "chapter": "函数的概念",
            "content": """
            函数是数学中的重要概念。设A、B是非空的数集，如果按照某个确定的对应关系f，
            使对于集合A中的任意一个数x，在集合B中都有唯一确定的数f(x)和它对应，
            那么就称f：A→B为从集合A到集合B的一个函数。
            """,
            "learning_objectives": [
                "理解函数的概念",
                "掌握函数的表示方法",
                "能够判断给定关系是否为函数"
            ]
        }
        
        # 获取教材分析智能体
        teaching_agent = self.agent_manager.get_agent("teaching_analysis")
        
        # 分析教材
        analysis_result = await teaching_agent.analyze_material(teaching_material)
        
        print(f"知识点分析: {json.dumps(analysis_result.get('knowledge_points', []), ensure_ascii=False, indent=2)}")
        print(f"难度评估: {analysis_result.get('difficulty_level')}")
        print(f"教学建议: {analysis_result.get('teaching_suggestions')}")
        
        return analysis_result
    
    async def demo_learning_status_analysis(self):
        """演示学情分析功能"""
        print("\n=== 学情分析演示 ===")
        
        # 模拟学生成绩数据
        student_data = {
            "student_id": "S001",
            "name": "张三",
            "grade": "高一",
            "subject_scores": {
                "数学": [85, 78, 92, 88, 90],
                "物理": [76, 82, 79, 85, 88],
                "化学": [88, 85, 90, 87, 92]
            },
            "recent_tests": [
                {
                    "subject": "数学",
                    "topic": "函数",
                    "score": 85,
                    "max_score": 100,
                    "date": "2024-01-15",
                    "wrong_questions": ["函数定义域", "复合函数"]
                }
            ]
        }
        
        # 获取学情分析智能体
        learning_agent = self.agent_manager.get_agent("learning_status")
        
        # 分析学情
        status_result = await learning_agent.analyze_learning_status(student_data)
        
        print(f"学习水平: {status_result.get('learning_level')}")
        print(f"强项科目: {status_result.get('strengths')}")
        print(f"薄弱环节: {status_result.get('weaknesses')}")
        print(f"学习趋势: {status_result.get('learning_trend')}")
        
        return status_result
    
    async def demo_tutoring_plan_generation(self):
        """演示辅导方案生成功能"""
        print("\n=== 辅导方案生成演示 ===")
        
        # 模拟学生信息和学习需求
        tutoring_request = {
            "student_info": {
                "student_id": "S001",
                "name": "张三",
                "grade": "高一",
                "learning_style": "视觉型"
            },
            "subject": "数学",
            "weak_areas": ["函数定义域", "复合函数"],
            "target_score": 95,
            "available_time": "每天1小时",
            "learning_preferences": ["图形化解释", "实例练习"]
        }
        
        # 获取辅导方案智能体
        tutoring_agent = self.agent_manager.get_agent("tutoring_plan")
        
        # 生成辅导方案
        plan_result = await tutoring_agent.generate_plan(tutoring_request)
        
        print(f"学习计划: {json.dumps(plan_result.get('study_plan', {}), ensure_ascii=False, indent=2)}")
        print(f"练习推荐: {plan_result.get('exercise_recommendations')}")
        print(f"学习资源: {plan_result.get('learning_resources')}")
        
        return plan_result
    
    async def demo_classroom_ai_assistant(self):
        """演示课堂AI助手功能"""
        print("\n=== 课堂AI助手演示 ===")
        
        # 模拟课堂情况
        classroom_context = {
            "class_info": {
                "grade": "高一",
                "subject": "数学",
                "topic": "函数的概念",
                "student_count": 45
            },
            "real_time_data": {
                "attention_level": 0.75,
                "participation_rate": 0.68,
                "question_frequency": 8,
                "difficulty_feedback": "适中"
            },
            "student_responses": [
                {"student_id": "S001", "response": "理解", "confidence": 0.8},
                {"student_id": "S002", "response": "困惑", "confidence": 0.3},
                {"student_id": "S003", "response": "理解", "confidence": 0.9}
            ]
        }
        
        # 获取课堂AI助手
        classroom_agent = self.agent_manager.get_agent("classroom_ai")
        
        # 分析课堂情况
        classroom_analysis = await classroom_agent.analyze_classroom_situation(classroom_context)
        
        print(f"课堂状态评估: {classroom_analysis.get('classroom_status')}")
        print(f"教学建议: {classroom_analysis.get('teaching_suggestions')}")
        print(f"互动内容: {classroom_analysis.get('interaction_content')}")
        
        return classroom_analysis
    
    @cached(key="demo_prompt", ttl=1800)
    async def demo_prompt_management(self):
        """演示提示词管理功能"""
        print("\n=== 提示词管理演示 ===")
        
        # 获取教学分析模板
        template = self.prompt_manager.get_template(
            "teaching_analysis", 
            "analyze_knowledge_points"
        )
        
        print(f"模板描述: {template.get('description')}")
        print(f"模板变量: {template.get('variables')}")
        
        # 格式化模板
        formatted_prompt = self.prompt_manager.format_template(
            "teaching_analysis",
            "analyze_knowledge_points",
            {
                "subject": "数学",
                "content": "函数的概念和性质",
                "grade_level": "高一"
            }
        )
        
        print(f"格式化后的提示词: {formatted_prompt[:200]}...")
        
        # 获取热门模板
        popular_templates = self.prompt_manager.get_popular_templates(limit=3)
        print(f"热门模板: {[t['name'] for t in popular_templates]}")
        
        return template
    
    @monitored
    async def demo_context_management(self):
        """演示上下文管理功能"""
        print("\n=== 上下文管理演示 ===")
        
        # 创建会话
        session_info = self.session_manager.create_session(
            user_id="teacher_001",
            user_role="teacher",
            user_info={"name": "李老师", "subject": "数学"}
        )
        
        session_id = session_info.session_id
        print(f"创建会话: {session_id}")
        
        # 创建对话上下文
        context_id = self.context_manager.create_context(
            session_id=session_id,
            context_type="teaching_consultation",
            strategy=SlidingWindowStrategy(window_size=10)
        )
        
        print(f"创建上下文: {context_id}")
        
        # 添加对话消息
        self.context_manager.add_message(
            context_id,
            role="user",
            content="请帮我分析一下这个数学题的解题思路"
        )
        
        self.context_manager.add_message(
            context_id,
            role="assistant",
            content="好的，我来帮您分析这道题。首先我们需要..."
        )
        
        # 获取对话历史
        history = self.context_manager.get_conversation_history(context_id)
        print(f"对话历史: {len(history)} 条消息")
        
        # 格式化为LLM输入
        llm_context = self.context_manager.format_for_llm(context_id)
        print(f"LLM上下文长度: {len(llm_context)} 条消息")
        
        return context_id
    
    async def demo_performance_optimization(self):
        """演示性能优化功能"""
        print("\n=== 性能优化演示 ===")
        
        # 获取系统性能统计
        system_stats = self.optimization_manager.get_monitor().get_system_stats()
        print(f"系统CPU使用率: {system_stats.get('system_cpu_usage', {}).get('current', 0):.1f}%")
        print(f"系统内存使用率: {system_stats.get('system_memory_usage', {}).get('current', 0):.1f}%")
        
        # 获取缓存统计
        cache_manager = self.optimization_manager.get_cache_manager()
        if cache_manager:
            cache_stats = cache_manager.get_stats()
            print(f"缓存命中率: {cache_stats.get('hit_rate', 0):.2f}")
            print(f"缓存大小: {cache_stats.get('size', 0)} 项")
        
        # 生成优化报告
        optimization_report = self.optimization_manager.get_optimization_report()
        print(f"优化建议数量: {len(optimization_report.get('optimization_suggestions', []))}")
        
        performance_summary = optimization_report.get('performance_summary', {})
        print(f"性能摘要: {performance_summary}")
        
        return optimization_report
    
    @optimize(cache_key="comprehensive_demo", monitor_performance=True)
    async def run_comprehensive_demo(self):
        """运行综合演示"""
        print("\n" + "="*50)
        print("智能教学助手LLM系统综合演示")
        print("="*50)
        
        try:
            # 1. 教材分析
            teaching_result = await self.demo_teaching_analysis()
            
            # 2. 学情分析
            learning_result = await self.demo_learning_status_analysis()
            
            # 3. 辅导方案生成
            tutoring_result = await self.demo_tutoring_plan_generation()
            
            # 4. 课堂AI助手
            classroom_result = await self.demo_classroom_ai_assistant()
            
            # 5. 提示词管理
            prompt_result = await self.demo_prompt_management()
            
            # 6. 上下文管理
            context_result = await self.demo_context_management()
            
            # 7. 性能优化
            optimization_result = await self.demo_performance_optimization()
            
            print("\n" + "="*50)
            print("综合演示完成")
            print("="*50)
            
            return {
                "teaching_analysis": teaching_result,
                "learning_status": learning_result,
                "tutoring_plan": tutoring_result,
                "classroom_ai": classroom_result,
                "prompt_management": prompt_result,
                "context_management": context_result,
                "performance_optimization": optimization_result
            }
            
        except Exception as e:
            print(f"演示过程中出现错误: {e}")
            return None
    
    def cleanup(self):
        """清理资源"""
        print("\n清理系统资源...")
        
        # 关闭优化管理器
        self.optimization_manager.shutdown()
        
        # 清理会话
        active_sessions = self.session_manager.get_active_sessions()
        for session in active_sessions:
            self.session_manager.terminate_session(session.session_id)
        
        print("资源清理完成")

class QuickStartExample:
    """快速开始示例"""
    
    @staticmethod
    async def simple_teaching_analysis():
        """简单的教材分析示例"""
        print("\n=== 快速开始: 教材分析 ===")
        
        # 创建LLM客户端
        llm_client = LLMClient(LLMConfig(
            provider="tongyi",
            api_key="your-api-key"
        ))
        
        # 创建教材分析智能体
        teaching_agent = TeachingAnalysisAgent(llm_client)
        
        # 分析教材
        material = {
            "subject": "数学",
            "content": "二次函数的图像和性质"
        }
        
        result = await teaching_agent.analyze_material(material)
        print(f"分析结果: {result}")
        
        return result
    
    @staticmethod
    @cached(key="quick_learning_analysis")
    async def simple_learning_analysis():
        """简单的学情分析示例"""
        print("\n=== 快速开始: 学情分析 ===")
        
        # 创建LLM客户端
        llm_client = LLMClient(LLMConfig(
            provider="tongyi",
            api_key="your-api-key"
        ))
        
        # 创建学情分析智能体
        learning_agent = LearningStatusAgent(llm_client)
        
        # 分析学情
        student_data = {
            "student_id": "S001",
            "subject_scores": {"数学": [85, 78, 92]}
        }
        
        result = await learning_agent.analyze_learning_status(student_data)
        print(f"学情分析: {result}")
        
        return result

async def main():
    """主函数"""
    print("智能教学助手LLM系统演示程序")
    print("注意: 请确保已正确配置API密钥")
    
    # 运行快速示例
    print("\n运行快速示例...")
    await QuickStartExample.simple_teaching_analysis()
    await QuickStartExample.simple_learning_analysis()
    
    # 运行完整演示
    print("\n运行完整演示...")
    demo = TeachingAssistantDemo()
    
    try:
        result = await demo.run_comprehensive_demo()
        if result:
            print("\n演示成功完成!")
        else:
            print("\n演示过程中遇到问题")
    
    finally:
        demo.cleanup()

if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())