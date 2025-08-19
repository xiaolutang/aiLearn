# -*- coding: utf-8 -*-
"""
智能体管理器模块
提供智能体的统一管理、协调和调度功能
"""

import logging
from typing import Dict, List, Optional, Any, Type
from .base_agent import BaseTeachingAgent, AgentType, AgentTask, AgentResponse
from .teaching_analysis_agent import TeachingAnalysisAgent
from .learning_status_agent import LearningStatusAgent
from .tutoring_agent import TutoringAgent
from .classroom_ai_agent import ClassroomAIAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """智能体管理器"""
    
    def __init__(self, llm_client=None, config: Optional[Dict] = None):
        """
        初始化智能体管理器
        
        Args:
            llm_client: 大模型客户端
            config: 配置信息
        """
        self.llm_client = llm_client
        self.config = config or {}
        
        # 智能体注册表
        self.agent_registry: Dict[AgentType, Type[BaseTeachingAgent]] = {
            AgentType.TEACHING_ANALYSIS: TeachingAnalysisAgent,
            AgentType.LEARNING_STATUS: LearningStatusAgent,
            AgentType.TUTORING: TutoringAgent,
            AgentType.CLASSROOM_AI: ClassroomAIAgent
        }
        
        # 智能体实例缓存
        self.agent_instances: Dict[AgentType, BaseTeachingAgent] = {}
        
        # 管理器配置
        self.manager_config = {
            "max_concurrent_tasks": 5,     # 最大并发任务数
            "task_timeout": 300,           # 任务超时时间（秒）
            "retry_attempts": 3,           # 重试次数
            "cache_enabled": True,         # 是否启用缓存
            "performance_monitoring": True # 性能监控
        }
        
        self.manager_config.update(config.get("manager_config", {}) if config else {})
        
        # 任务队列和状态跟踪
        self.task_queue: List[AgentTask] = []
        self.task_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_response_time": 0.0,
            "agent_usage": {agent_type.value: 0 for agent_type in AgentType}
        }
    
    def get_agent(self, agent_type: AgentType) -> BaseTeachingAgent:
        """
        获取智能体实例
        
        Args:
            agent_type: 智能体类型
            
        Returns:
            BaseTeachingAgent: 智能体实例
        """
        if agent_type not in self.agent_instances:
            if agent_type not in self.agent_registry:
                raise ValueError(f"不支持的智能体类型: {agent_type}")
            
            agent_class = self.agent_registry[agent_type]
            agent_config = self.config.get(f"{agent_type.value}_config", {})
            
            self.agent_instances[agent_type] = agent_class(
                llm_client=self.llm_client,
                config=agent_config
            )
            
            logger.info(f"创建智能体实例: {agent_type.value}")
        
        return self.agent_instances[agent_type]
    
    def execute_task(self, agent_type: AgentType, task_type: str, 
                    input_data: Dict[str, Any], priority: str = "medium") -> AgentResponse:
        """
        执行智能体任务
        
        Args:
            agent_type: 智能体类型
            task_type: 任务类型
            input_data: 输入数据
            priority: 任务优先级
            
        Returns:
            AgentResponse: 执行结果
        """
        try:
            # 获取智能体实例
            agent = self.get_agent(agent_type)
            
            # 创建任务
            task = AgentTask(
                task_id=f"task_{len(self.task_history) + 1}",
                agent_type=agent_type,
                task_type=task_type,
                input_data=input_data,
                priority=priority
            )
            
            # 记录任务开始
            import time
            start_time = time.time()
            
            logger.info(f"开始执行任务: {task.task_id} ({agent_type.value} - {task_type})")
            
            # 执行任务
            response = agent.execute_task(task_type, input_data)
            
            # 记录任务完成
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 更新性能指标
            self._update_performance_metrics(agent_type, response.success, execution_time)
            
            # 记录任务历史
            self._record_task_history(task, response, execution_time)
            
            logger.info(f"任务执行完成: {task.task_id} (耗时: {execution_time:.2f}s)")
            
            return response
            
        except Exception as e:
            logger.error(f"任务执行失败: {str(e)}")
            
            # 更新失败指标
            self._update_performance_metrics(agent_type, False, 0)
            
            return AgentResponse(
                success=False,
                message=f"任务执行失败: {str(e)}",
                error_code="EXECUTION_ERROR"
            )
    
    def batch_execute_tasks(self, tasks: List[Dict[str, Any]]) -> List[AgentResponse]:
        """
        批量执行任务
        
        Args:
            tasks: 任务列表，每个任务包含agent_type, task_type, input_data等字段
            
        Returns:
            List[AgentResponse]: 执行结果列表
        """
        results = []
        
        for task_config in tasks:
            try:
                agent_type = AgentType(task_config["agent_type"])
                task_type = task_config["task_type"]
                input_data = task_config["input_data"]
                priority = task_config.get("priority", "medium")
                
                response = self.execute_task(agent_type, task_type, input_data, priority)
                results.append(response)
                
            except Exception as e:
                logger.error(f"批量任务执行失败: {str(e)}")
                results.append(AgentResponse(
                    success=False,
                    message=f"批量任务执行失败: {str(e)}",
                    error_code="BATCH_EXECUTION_ERROR"
                ))
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            Dict[str, Any]: 性能指标数据
        """
        return self.performance_metrics.copy()
    
    def get_task_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取任务历史
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            List[Dict[str, Any]]: 任务历史记录
        """
        return self.task_history[-limit:] if limit > 0 else self.task_history
    
    def clear_task_history(self):
        """
        清空任务历史
        """
        self.task_history.clear()
        logger.info("任务历史已清空")
    
    def reset_performance_metrics(self):
        """
        重置性能指标
        """
        self.performance_metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_response_time": 0.0,
            "agent_usage": {agent_type.value: 0 for agent_type in AgentType}
        }
        logger.info("性能指标已重置")
    
    def _update_performance_metrics(self, agent_type: AgentType, success: bool, execution_time: float):
        """
        更新性能指标
        
        Args:
            agent_type: 智能体类型
            success: 是否成功
            execution_time: 执行时间
        """
        self.performance_metrics["total_tasks"] += 1
        
        if success:
            self.performance_metrics["successful_tasks"] += 1
        else:
            self.performance_metrics["failed_tasks"] += 1
        
        # 更新平均响应时间
        total_tasks = self.performance_metrics["total_tasks"]
        current_avg = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (
            (current_avg * (total_tasks - 1) + execution_time) / total_tasks
        )
        
        # 更新智能体使用统计
        self.performance_metrics["agent_usage"][agent_type.value] += 1
    
    def _record_task_history(self, task: AgentTask, response: AgentResponse, execution_time: float):
        """
        记录任务历史
        
        Args:
            task: 任务信息
            response: 响应结果
            execution_time: 执行时间
        """
        from datetime import datetime
        
        history_record = {
            "task_id": task.task_id,
            "agent_type": task.agent_type.value,
            "task_type": task.task_type,
            "priority": task.priority,
            "success": response.success,
            "message": response.message,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "error_code": getattr(response, 'error_code', None)
        }
        
        self.task_history.append(history_record)
        
        # 限制历史记录数量
        max_history = self.manager_config.get("max_history_records", 1000)
        if len(self.task_history) > max_history:
            self.task_history = self.task_history[-max_history:]
    
    # 便捷方法：教材分析
    def analyze_teaching_material(self, content: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        分析教材内容
        
        Args:
            content: 教材内容
            analysis_type: 分析类型
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        response = self.execute_task(
            AgentType.TEACHING_ANALYSIS,
            analysis_type,
            {"content": content}
        )
        return response.data if response.success else {"error": response.message}
    
    # 便捷方法：学情分析
    def analyze_student_learning(self, student_id: str, grades: List[Dict], 
                               student_info: Dict = None) -> Dict[str, Any]:
        """
        分析学生学习情况
        
        Args:
            student_id: 学生ID
            grades: 成绩列表
            student_info: 学生信息
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        input_data = {
            "student_id": student_id,
            "grades": grades
        }
        
        if student_info:
            input_data.update(student_info)
        
        response = self.execute_task(
            AgentType.LEARNING_STATUS,
            "comprehensive_analysis",
            input_data
        )
        return response.data if response.success else {"error": response.message}
    
    # 便捷方法：生成辅导方案
    def generate_tutoring_plan(self, student_id: str, learning_analysis: Dict,
                             goals: List[Dict] = None, duration_weeks: int = 4) -> Dict[str, Any]:
        """
        生成辅导方案
        
        Args:
            student_id: 学生ID
            learning_analysis: 学习分析结果
            goals: 学习目标
            duration_weeks: 计划周期
            
        Returns:
            Dict[str, Any]: 辅导方案
        """
        input_data = {
            "student_id": student_id,
            "learning_status": learning_analysis,
            "learning_goals": goals or [],
            "plan_duration": duration_weeks
        }
        
        response = self.execute_task(
            AgentType.TUTORING,
            "comprehensive_plan",
            input_data
        )
        return response.data if response.success else {"error": response.message}
    
    # 便捷方法：课堂实时分析
    def analyze_classroom_realtime(self, class_id: str, classroom_data: Dict,
                                 interaction_data: Dict = None) -> Dict[str, Any]:
        """
        实时分析课堂情况
        
        Args:
            class_id: 班级ID
            classroom_data: 课堂数据
            interaction_data: 互动数据
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        input_data = {
            "class_id": class_id,
            "classroom_data": classroom_data,
            "interaction_data": interaction_data or {}
        }
        
        response = self.execute_task(
            AgentType.CLASSROOM_AI,
            "real_time_analysis",
            input_data
        )
        return response.data if response.success else {"error": response.message}
    
    # 便捷方法：生成课堂互动
    def generate_classroom_interactions(self, subject: str, topic: str, grade: str,
                                      time_limit: int = 15) -> Dict[str, Any]:
        """
        生成课堂互动内容
        
        Args:
            subject: 学科
            topic: 主题
            grade: 年级
            time_limit: 时间限制
            
        Returns:
            Dict[str, Any]: 互动内容
        """
        input_data = {
            "subject": subject,
            "topic": topic,
            "grade": grade,
            "time_limit": time_limit
        }
        
        response = self.execute_task(
            AgentType.CLASSROOM_AI,
            "interaction_generation",
            input_data
        )
        return response.data if response.success else {"error": response.message}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        获取所有智能体状态
        
        Returns:
            Dict[str, Any]: 智能体状态信息
        """
        status = {
            "registered_agents": list(self.agent_registry.keys()),
            "active_agents": list(self.agent_instances.keys()),
            "agent_details": {}
        }
        
        for agent_type, agent in self.agent_instances.items():
            status["agent_details"][agent_type.value] = {
                "agent_info": agent.get_agent_info(),
                "task_history_count": len(agent.get_task_history())
            }
        
        return status