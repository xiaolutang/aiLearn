# LLM配置管理模块
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMInterface(ABC):
    """
    LLM抽象接口，定义与大语言模型交互的标准方法
    """
    
    @abstractmethod
    def generate_response(self, messages: list, model: str, **kwargs) -> Any:
        """生成模型响应"""
        pass
    
    @abstractmethod
    def stream_response(self, messages: list, model: str, **kwargs) -> Any:
        """流式获取模型响应"""
        pass


class TongYiLLM(LLMInterface):
    """
    通义千问大模型实现
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # 如果未提供参数，则从环境变量获取
        self.api_key = api_key or os.getenv("TONG_YI_API_KEY")
        self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        # 初始化OpenAI客户端（通义千问兼容OpenAI API）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_response(self, messages: list, model: str = "qwen-plus", **kwargs) -> Any:
        """生成完整的模型响应"""
        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            **kwargs
        )
    
    def stream_response(self, messages: list, model: str = "qwen-plus", **kwargs) -> Any:
        """流式获取模型响应"""
        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            stream=True,
            **kwargs
        )


class OpenAILLM(LLMInterface):
    """
    OpenAI大模型实现
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # 如果未提供参数，则从环境变量获取
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or "https://api.openai.com/v1"
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_response(self, messages: list, model: str = "gpt-3.5-turbo", **kwargs) -> Any:
        """生成完整的模型响应"""
        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            **kwargs
        )
    
    def stream_response(self, messages: list, model: str = "gpt-3.5-turbo", **kwargs) -> Any:
        """流式获取模型响应"""
        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            stream=True,
            **kwargs
        )


class LLMCreator:
    """
    LLM工厂类，负责创建不同类型的LLM实例
    """
    
    @staticmethod
    def create_llm(llm_type: str, **kwargs) -> LLMInterface:
        """
        创建指定类型的LLM实例
        
        Args:
            llm_type: LLM类型，如"tongyi"、"openai"
            **kwargs: 其他参数，如api_key、base_url等
            
        Returns:
            LLMInterface实例
            
        Raises:
            ValueError: 不支持的LLM类型
        """
        llm_type = llm_type.lower()
        
        if llm_type == "tongyi":
            return TongYiLLM(**kwargs)
        elif llm_type == "openai":
            return OpenAILLM(**kwargs)
        else:
            raise ValueError(f"不支持的LLM类型: {llm_type}")


# 全局配置
class LLMConfig:
    """
    LLM配置类，管理全局LLM设置
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # 从环境变量加载默认配置
        self.default_llm_type = os.getenv("DEFAULT_LLM_TYPE", "tongyi")
        self.default_model = os.getenv("DEFAULT_MODEL", "qwen-plus")
        self.llm_instances = {}
    
    def get_llm(self, llm_type: Optional[str] = None, **kwargs) -> LLMInterface:
        """
        获取LLM实例，如果实例不存在则创建
        
        Args:
            llm_type: LLM类型，如不提供则使用默认类型
            **kwargs: 其他参数
            
        Returns:
            LLMInterface实例
        """
        llm_type = llm_type or self.default_llm_type
        
        # 创建缓存键
        cache_key = f"{llm_type}:{'-'.join([f'{k}={v}' for k, v in sorted(kwargs.items())])}"
        
        # 检查实例是否已存在
        if cache_key not in self.llm_instances:
            self.llm_instances[cache_key] = LLMCreator.create_llm(llm_type, **kwargs)
        
        return self.llm_instances[cache_key]
    
    def set_default_llm(self, llm_type: str, model: Optional[str] = None):
        """
        设置默认LLM类型和模型
        
        Args:
            llm_type: LLM类型
            model: 模型名称
        """
        self.default_llm_type = llm_type
        if model:
            self.default_model = model
        # 清除缓存的实例，下次获取时会重新创建
        self.llm_instances.clear()


# 创建全局配置实例
global_llm_config = LLMConfig()


# 工具函数：获取默认LLM实例
def get_default_llm() -> LLMInterface:
    """
    获取默认的LLM实例
    
    Returns:
        LLMInterface实例
    """
    return global_llm_config.get_llm()


# 工具函数：生成响应
def generate_llm_response(messages: list, model: Optional[str] = None, 
                          llm_type: Optional[str] = None, stream: bool = False, 
                          **kwargs) -> Any:
    """
    生成LLM响应的便捷函数
    
    Args:
        messages: 消息列表
        model: 模型名称，如不提供则使用默认模型
        llm_type: LLM类型，如不提供则使用默认类型
        stream: 是否使用流式输出
        **kwargs: 其他参数
        
    Returns:
        模型响应
    """
    llm = global_llm_config.get_llm(llm_type)
    
    if model is None:
        model = global_llm_config.default_model
    
    if stream:
        return llm.stream_response(messages, model, **kwargs)
    else:
        return llm.generate_response(messages, model, **kwargs)