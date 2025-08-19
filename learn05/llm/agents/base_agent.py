# -*- coding: utf-8 -*-
"""
智能教学助手基础智能体模块
定义所有教学智能体的基础接口和通用功能
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """智能体类型枚举"""
    # 备课助手相关
    TEACHING_ANALYSIS = "teaching_analysis"  # 教材分析
    ANALYSIS = "analysis"                    # 通用分析
    PLANNING = "planning"                    # 教学规划
    
    # 课堂AI助手相关
    MONITORING = "monitoring"                # 实时监控
    REAL_TIME_LEARNING = "real_time_learning"  # 实时学习
    DESIGN = "design"                        # 设计助手
    APPLICATION = "application"              # AI应用
    CLASSROOM_AI = "classroom_ai"            # 课堂AI助手
    
    # 成绩管理相关
    DATA_PROCESSING = "data_processing"      # 数据处理
    GUIDANCE = "guidance"                    # 个性化指导
    
    # 通用类型
    LEARNING_STATUS = "learning_status"      # 学情分析
    TUTORING_PLAN = "tutoring_plan"          # 辅导方案
    EXERCISE_GENERATION = "exercise_generation"  # 练习生成
    PERFORMANCE_ANALYSIS = "performance_analysis"  # 成绩分析


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class AgentTask:
    """智能体任务数据类"""
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: float = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class AgentResponse:
    """智能体响应数据类"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""
    error_code: Optional[str] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTeachingAgent(ABC):
    """教学智能体基础抽象类"""
    
    def __init__(self, agent_type: AgentType, llm_client=None, config: Optional[Dict] = None):
        """
        初始化智能体
        
        Args:
            agent_type: 智能体类型
            llm_client: 大模型客户端
            config: 配置参数
        """
        self.agent_type = agent_type
        self.llm_client = llm_client
        self.config = config or {}
        self.task_history: List[AgentTask] = []
        
        # 默认配置
        self.default_config = {
            "max_retries": 3,
            "timeout": 30,
            "temperature": 0.7,
            "max_tokens": 2000,
            "enable_cache": True,
            "cache_ttl": 3600  # 缓存时间（秒）
        }
        
        # 合并配置
        self.config = {**self.default_config, **self.config}
        
        logger.info(f"初始化{agent_type.value}智能体")
    
    @abstractmethod
    def process_task(self, task: AgentTask) -> AgentResponse:
        """
        处理任务的抽象方法
        
        Args:
            task: 要处理的任务
            
        Returns:
            AgentResponse: 处理结果
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据的抽象方法
        
        Args:
            input_data: 输入数据
            
        Returns:
            bool: 验证是否通过
        """
        pass
    
    @abstractmethod
    def get_prompt_template(self, task_type: str) -> str:
        """
        获取提示词模板的抽象方法
        
        Args:
            task_type: 任务类型
            
        Returns:
            str: 提示词模板
        """
        pass
    
    def execute_task(self, task_type: str, input_data: Dict[str, Any], 
                    priority: TaskPriority = TaskPriority.MEDIUM) -> AgentResponse:
        """
        执行任务的通用方法
        
        Args:
            task_type: 任务类型
            input_data: 输入数据
            priority: 任务优先级
            
        Returns:
            AgentResponse: 执行结果
        """
        start_time = time.time()
        
        # 创建任务
        task = AgentTask(
            task_id=f"{self.agent_type.value}_{int(start_time)}",
            task_type=task_type,
            input_data=input_data,
            priority=priority
        )
        
        try:
            # 验证输入
            if not self.validate_input(input_data):
                return AgentResponse(
                    success=False,
                    message="输入数据验证失败",
                    error_code="INVALID_INPUT"
                )
            
            # 处理任务
            response = self.process_task(task)
            
            # 记录处理时间
            processing_time = time.time() - start_time
            response.processing_time = processing_time
            
            # 更新任务状态
            task.completed_at = time.time()
            task.result = response.data
            
            # 添加到历史记录
            self.task_history.append(task)
            
            logger.info(f"任务{task.task_id}执行完成，耗时{processing_time:.2f}秒")
            
            return response
            
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            logger.error(error_msg)
            
            task.error = error_msg
            self.task_history.append(task)
            
            return AgentResponse(
                success=False,
                message=error_msg,
                error_code="EXECUTION_ERROR",
                processing_time=time.time() - start_time
            )
    
    def get_task_history(self, limit: int = 10) -> List[AgentTask]:
        """
        获取任务历史记录
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            List[AgentTask]: 任务历史记录
        """
        return self.task_history[-limit:]
    
    def clear_task_history(self):
        """清空任务历史记录"""
        self.task_history.clear()
        logger.info(f"{self.agent_type.value}智能体历史记录已清空")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        获取智能体信息
        
        Returns:
            Dict[str, Any]: 智能体信息
        """
        return {
            "agent_type": self.agent_type.value,
            "config": self.config,
            "task_count": len(self.task_history),
            "last_task_time": self.task_history[-1].created_at if self.task_history else None
        }
    
    def _call_llm(self, prompt: str, **kwargs) -> str:
        """
        调用大模型的通用方法
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            str: 大模型响应
        """
        if not self.llm_client:
            raise ValueError("LLM客户端未初始化")
        
        # 合并配置参数
        llm_params = {
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 2000),
            **kwargs
        }
        
        try:
            response = self.llm_client.generate(prompt, **llm_params)
            return response
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            raise
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """
        格式化提示词模板
        
        Args:
            template: 提示词模板
            **kwargs: 模板参数
            
        Returns:
            str: 格式化后的提示词
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"提示词模板参数缺失: {str(e)}")
            raise ValueError(f"提示词模板参数缺失: {str(e)}")