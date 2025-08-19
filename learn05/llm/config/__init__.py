# Config package

from .config_manager import ConfigManager
from .settings import LLMSettings

# 创建全局配置管理器实例
_config_manager = None

def get_config_manager():
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_llm_config():
    """获取LLM配置"""
    return get_config_manager().get_config()

__all__ = [
    'ConfigManager',
    'LLMSettings', 
    'get_config_manager',
    'get_llm_config'
]