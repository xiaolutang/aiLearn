# -*- coding: utf-8 -*-
"""
配置管理单元测试
测试配置管理器和相关功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import os
import tempfile
import json
import yaml

# from llm.config.config_manager import (
#     MockConfigManager,
#     LLMConfig,
#     DatabaseConfig,
#     CacheConfig,
#     AgentConfig
# )
# from llm.config.settings import (
#     DEFAULT_SETTINGS,
#     ENVIRONMENT_SETTINGS,
#     load_environment_config,
#     validate_config
# )
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from test_config import (
    TEST_CONFIG,
    MOCK_STUDENT_DATA,
    MOCK_GRADE_DATA
)

class MockConfigManager:
    """Mock配置管理器"""
    def __init__(self, *args, **kwargs):
        pass
    
    def get_config(self, key, default=None):
        return default
    
    def set_config(self, key, value):
        pass


class TestMockConfigManager:
    """测试配置管理器类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.config_manager = MockConfigManager()
        
        # 创建临时配置文件
        self.temp_config_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        
        # 写入测试配置
        test_config = {
            "llm": {
                "provider": "openai",
                "api_key": "test_api_key",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "database": {
                "type": "sqlite",
                "path": "test.db",
                "auto_create_tables": True
            },
            "cache": {
                "enabled": True,
                "max_size": 1000,
                "ttl": 3600
            }
        }
        
        json.dump(test_config, self.temp_config_file)
        self.temp_config_file.close()
    
    def teardown_method(self):
        """测试后的清理"""
        # 删除临时配置文件
        if os.path.exists(self.temp_config_file.name):
            os.unlink(self.temp_config_file.name)
    
    def test_config_manager_initialization(self):
        """测试配置管理器初始化"""
        assert self.config_manager is not None
        assert hasattr(self.config_manager, 'config')
        assert isinstance(self.config_manager.config, dict)
    
    def test_load_config_from_file(self):
        """测试从文件加载配置"""
        # 加载配置文件
        self.config_manager.load_from_file(self.temp_config_file.name)
        
        # 验证配置加载
        assert 'llm' in self.config_manager.config
        assert 'database' in self.config_manager.config
        assert 'cache' in self.config_manager.config
        
        # 验证具体配置值
        llm_config = self.config_manager.config['llm']
        assert llm_config['provider'] == 'openai'
        assert llm_config['model'] == 'gpt-3.5-turbo'
        assert llm_config['temperature'] == 0.7
    
    def test_load_config_from_nonexistent_file(self):
        """测试加载不存在的配置文件"""
        nonexistent_file = "/path/to/nonexistent/config.json"
        
        with pytest.raises(FileNotFoundError):
            self.config_manager.load_from_file(nonexistent_file)
    
    def test_load_config_from_invalid_json(self):
        """测试加载无效JSON配置文件"""
        # 创建无效JSON文件
        invalid_json_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        invalid_json_file.write("{ invalid json content }")
        invalid_json_file.close()
        
        try:
            with pytest.raises(json.JSONDecodeError):
                self.config_manager.load_from_file(invalid_json_file.name)
        finally:
            os.unlink(invalid_json_file.name)
    
    def test_load_yaml_config(self):
        """测试加载YAML配置文件"""
        # 创建YAML配置文件
        yaml_config_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False
        )
        
        yaml_config = {
            'llm': {
                'provider': 'tongyi',
                'api_key': 'yaml_test_key',
                'model': 'qwen-turbo'
            },
            'agents': {
                'teaching_analysis': {
                    'enabled': True,
                    'max_retries': 3
                }
            }
        }
        
        yaml.dump(yaml_config, yaml_config_file)
        yaml_config_file.close()
        
        try:
            # 加载YAML配置
            self.config_manager.load_from_file(yaml_config_file.name)
            
            # 验证配置
            assert self.config_manager.config['llm']['provider'] == 'tongyi'
            assert self.config_manager.config['llm']['model'] == 'qwen-turbo'
            assert self.config_manager.config['agents']['teaching_analysis']['enabled'] is True
            
        finally:
            os.unlink(yaml_config_file.name)
    
    def test_get_config_value(self):
        """测试获取配置值"""
        self.config_manager.load_from_file(self.temp_config_file.name)
        
        # 获取嵌套配置值
        provider = self.config_manager.get('llm.provider')
        assert provider == 'openai'
        
        model = self.config_manager.get('llm.model')
        assert model == 'gpt-3.5-turbo'
        
        temperature = self.config_manager.get('llm.temperature')
        assert temperature == 0.7
        
        # 获取不存在的配置值
        nonexistent = self.config_manager.get('nonexistent.key')
        assert nonexistent is None
        
        # 获取带默认值的配置
        default_value = self.config_manager.get('nonexistent.key', 'default')
        assert default_value == 'default'
    
    def test_set_config_value(self):
        """测试设置配置值"""
        # 设置新的配置值
        self.config_manager.set('llm.provider', 'tongyi')
        assert self.config_manager.get('llm.provider') == 'tongyi'
        
        # 设置嵌套配置值
        self.config_manager.set('new.nested.key', 'value')
        assert self.config_manager.get('new.nested.key') == 'value'
        
        # 设置复杂对象
        complex_config = {
            'enabled': True,
            'settings': {
                'timeout': 30,
                'retries': 3
            }
        }
        self.config_manager.set('complex', complex_config)
        assert self.config_manager.get('complex.enabled') is True
        assert self.config_manager.get('complex.settings.timeout') == 30
    
    def test_update_config(self):
        """测试更新配置"""
        self.config_manager.load_from_file(self.temp_config_file.name)
        
        # 更新配置
        update_data = {
            'llm': {
                'temperature': 0.9,
                'max_tokens': 4000
            },
            'new_section': {
                'enabled': True
            }
        }
        
        self.config_manager.update(update_data)
        
        # 验证更新结果
        assert self.config_manager.get('llm.temperature') == 0.9
        assert self.config_manager.get('llm.max_tokens') == 4000
        assert self.config_manager.get('llm.provider') == 'openai'  # 未更新的值保持不变
        assert self.config_manager.get('new_section.enabled') is True
    
    def test_save_config_to_file(self):
        """测试保存配置到文件"""
        # 设置一些配置
        self.config_manager.set('test.key', 'test_value')
        self.config_manager.set('test.number', 42)
        
        # 创建临时保存文件
        save_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        save_file.close()
        
        try:
            # 保存配置
            self.config_manager.save_to_file(save_file.name)
            
            # 验证保存结果
            assert os.path.exists(save_file.name)
            
            # 加载保存的配置验证
            new_manager = MockConfigManager()
            new_manager.load_from_file(save_file.name)
            
            assert new_manager.get('test.key') == 'test_value'
            assert new_manager.get('test.number') == 42
            
        finally:
            os.unlink(save_file.name)
    
    def test_environment_variable_override(self):
        """测试环境变量覆盖配置"""
        with patch.dict(os.environ, {
            'AILEARN_LLM_PROVIDER': 'tongyi',
            'AILEARN_LLM_API_KEY': 'env_api_key',
            'AILEARN_DATABASE_PATH': 'env_database.db'
        }):
            # 加载环境变量配置
            self.config_manager.load_from_environment()
            
            # 验证环境变量覆盖
            assert self.config_manager.get('llm.provider') == 'tongyi'
            assert self.config_manager.get('llm.api_key') == 'env_api_key'
            assert self.config_manager.get('database.path') == 'env_database.db'
    
    def test_config_validation(self):
        """测试配置验证"""
        # 有效配置
        valid_config = {
            'llm': {
                'provider': 'openai',
                'api_key': 'valid_key',
                'model': 'gpt-3.5-turbo'
            }
        }
        
        self.config_manager.config = valid_config
        assert self.config_manager.validate() is True
        
        # 无效配置 - 缺少必需字段
        invalid_config = {
            'llm': {
                'provider': 'openai'
                # 缺少 api_key
            }
        }
        
        self.config_manager.config = invalid_config
        assert self.config_manager.validate() is False
    
    def test_get_llm_config(self):
        """测试获取LLM配置对象"""
        self.config_manager.load_from_file(self.temp_config_file.name)
        
        llm_config = self.config_manager.get_llm_config()
        
        assert isinstance(llm_config, LLMConfig)
        assert llm_config.provider == 'openai'
        assert llm_config.model == 'gpt-3.5-turbo'
        assert llm_config.temperature == 0.7
        assert llm_config.max_tokens == 2000
    
    def test_get_database_config(self):
        """测试获取数据库配置对象"""
        self.config_manager.load_from_file(self.temp_config_file.name)
        
        db_config = self.config_manager.get_database_config()
        
        assert isinstance(db_config, DatabaseConfig)
        assert db_config.type == 'sqlite'
        assert db_config.path == 'test.db'
        assert db_config.auto_create_tables is True
    
    def test_get_cache_config(self):
        """测试获取缓存配置对象"""
        self.config_manager.load_from_file(self.temp_config_file.name)
        
        cache_config = self.config_manager.get_cache_config()
        
        assert isinstance(cache_config, CacheConfig)
        assert cache_config.enabled is True
        assert cache_config.max_size == 1000
        assert cache_config.ttl == 3600
    
    def test_config_sections(self):
        """测试获取配置节"""
        self.config_manager.load_from_file(self.temp_config_file.name)
        
        # 获取所有配置节
        sections = self.config_manager.get_sections()
        assert 'llm' in sections
        assert 'database' in sections
        assert 'cache' in sections
        
        # 获取特定配置节
        llm_section = self.config_manager.get_section('llm')
        assert llm_section['provider'] == 'openai'
        assert llm_section['model'] == 'gpt-3.5-turbo'
    
    def test_config_merge(self):
        """测试配置合并"""
        # 基础配置
        base_config = {
            'llm': {
                'provider': 'openai',
                'temperature': 0.7
            },
            'database': {
                'type': 'sqlite'
            }
        }
        
        # 覆盖配置
        override_config = {
            'llm': {
                'temperature': 0.9,
                'max_tokens': 4000
            },
            'cache': {
                'enabled': True
            }
        }
        
        self.config_manager.config = base_config
        merged_config = self.config_manager.merge(override_config)
        
        # 验证合并结果
        assert merged_config['llm']['provider'] == 'openai'  # 保持原值
        assert merged_config['llm']['temperature'] == 0.9    # 被覆盖
        assert merged_config['llm']['max_tokens'] == 4000     # 新增
        assert merged_config['database']['type'] == 'sqlite' # 保持原值
        assert merged_config['cache']['enabled'] is True     # 新增节
    
    def test_config_reset(self):
        """测试重置配置"""
        # 设置一些配置
        self.config_manager.set('test.key', 'value')
        assert self.config_manager.get('test.key') == 'value'
        
        # 重置配置
        self.config_manager.reset()
        
        # 验证配置已重置
        assert self.config_manager.get('test.key') is None
        assert len(self.config_manager.config) == 0


class TestLLMConfig:
    """测试LLM配置类"""
    
    def test_llm_config_creation(self):
        """测试LLM配置创建"""
        config = LLMConfig(
            provider='openai',
            api_key='test_key',
            model='gpt-4',
            temperature=0.8,
            max_tokens=3000,
            timeout=60
        )
        
        assert config.provider == 'openai'
        assert config.api_key == 'test_key'
        assert config.model == 'gpt-4'
        assert config.temperature == 0.8
        assert config.max_tokens == 3000
        assert config.timeout == 60
    
    def test_llm_config_validation(self):
        """测试LLM配置验证"""
        # 有效配置
        valid_config = LLMConfig(
            provider='openai',
            api_key='valid_key',
            model='gpt-3.5-turbo'
        )
        assert valid_config.validate() is True
        
        # 无效配置 - 缺少API密钥
        invalid_config = LLMConfig(
            provider='openai',
            api_key='',
            model='gpt-3.5-turbo'
        )
        assert invalid_config.validate() is False
        
        # 无效配置 - 无效温度值
        invalid_temp_config = LLMConfig(
            provider='openai',
            api_key='valid_key',
            model='gpt-3.5-turbo',
            temperature=2.0  # 超出范围
        )
        assert invalid_temp_config.validate() is False
    
    def test_llm_config_to_dict(self):
        """测试LLM配置转换为字典"""
        config = LLMConfig(
            provider='tongyi',
            api_key='tongyi_key',
            model='qwen-turbo',
            temperature=0.7
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['provider'] == 'tongyi'
        assert config_dict['api_key'] == 'tongyi_key'
        assert config_dict['model'] == 'qwen-turbo'
        assert config_dict['temperature'] == 0.7
    
    def test_llm_config_from_dict(self):
        """测试从字典创建LLM配置"""
        config_dict = {
            'provider': 'openai',
            'api_key': 'dict_key',
            'model': 'gpt-4',
            'temperature': 0.5,
            'max_tokens': 2500
        }
        
        config = LLMConfig.from_dict(config_dict)
        
        assert config.provider == 'openai'
        assert config.api_key == 'dict_key'
        assert config.model == 'gpt-4'
        assert config.temperature == 0.5
        assert config.max_tokens == 2500


class TestDatabaseConfig:
    """测试数据库配置类"""
    
    def test_database_config_creation(self):
        """测试数据库配置创建"""
        config = DatabaseConfig(
            type='sqlite',
            path='test.db',
            host='localhost',
            port=5432,
            username='user',
            password='pass',
            database='testdb',
            auto_create_tables=True
        )
        
        assert config.type == 'sqlite'
        assert config.path == 'test.db'
        assert config.host == 'localhost'
        assert config.port == 5432
        assert config.username == 'user'
        assert config.password == 'pass'
        assert config.database == 'testdb'
        assert config.auto_create_tables is True
    
    def test_database_config_validation(self):
        """测试数据库配置验证"""
        # SQLite配置验证
        sqlite_config = DatabaseConfig(
            type='sqlite',
            path='valid.db'
        )
        assert sqlite_config.validate() is True
        
        # PostgreSQL配置验证
        postgres_config = DatabaseConfig(
            type='postgresql',
            host='localhost',
            port=5432,
            username='user',
            password='pass',
            database='testdb'
        )
        assert postgres_config.validate() is True
        
        # 无效配置 - SQLite缺少路径
        invalid_sqlite = DatabaseConfig(
            type='sqlite',
            path=''
        )
        assert invalid_sqlite.validate() is False
        
        # 无效配置 - PostgreSQL缺少主机
        invalid_postgres = DatabaseConfig(
            type='postgresql',
            host='',
            username='user',
            password='pass'
        )
        assert invalid_postgres.validate() is False
    
    def test_database_config_connection_string(self):
        """测试数据库连接字符串生成"""
        # SQLite连接字符串
        sqlite_config = DatabaseConfig(
            type='sqlite',
            path='test.db'
        )
        sqlite_conn_str = sqlite_config.get_connection_string()
        assert 'sqlite:///test.db' in sqlite_conn_str
        
        # PostgreSQL连接字符串
        postgres_config = DatabaseConfig(
            type='postgresql',
            host='localhost',
            port=5432,
            username='user',
            password='pass',
            database='testdb'
        )
        postgres_conn_str = postgres_config.get_connection_string()
        assert 'postgresql://user:pass@localhost:5432/testdb' in postgres_conn_str


class TestCacheConfig:
    """测试缓存配置类"""
    
    def test_cache_config_creation(self):
        """测试缓存配置创建"""
        config = CacheConfig(
            enabled=True,
            max_size=2000,
            ttl=7200,
            cleanup_interval=300
        )
        
        assert config.enabled is True
        assert config.max_size == 2000
        assert config.ttl == 7200
        assert config.cleanup_interval == 300
    
    def test_cache_config_validation(self):
        """测试缓存配置验证"""
        # 有效配置
        valid_config = CacheConfig(
            enabled=True,
            max_size=1000,
            ttl=3600
        )
        assert valid_config.validate() is True
        
        # 无效配置 - 负数大小
        invalid_size_config = CacheConfig(
            enabled=True,
            max_size=-100,
            ttl=3600
        )
        assert invalid_size_config.validate() is False
        
        # 无效配置 - 负数TTL
        invalid_ttl_config = CacheConfig(
            enabled=True,
            max_size=1000,
            ttl=-1
        )
        assert invalid_ttl_config.validate() is False


class TestAgentConfig:
    """测试智能体配置类"""
    
    def test_agent_config_creation(self):
        """测试智能体配置创建"""
        config = AgentConfig(
            agent_type='teaching_analysis',
            enabled=True,
            max_retries=3,
            timeout=30,
            custom_settings={
                'analysis_depth': 'detailed',
                'include_examples': True
            }
        )
        
        assert config.agent_type == 'teaching_analysis'
        assert config.enabled is True
        assert config.max_retries == 3
        assert config.timeout == 30
        assert config.custom_settings['analysis_depth'] == 'detailed'
        assert config.custom_settings['include_examples'] is True
    
    def test_agent_config_validation(self):
        """测试智能体配置验证"""
        # 有效配置
        valid_config = AgentConfig(
            agent_type='learning_status',
            enabled=True,
            max_retries=2,
            timeout=60
        )
        assert valid_config.validate() is True
        
        # 无效配置 - 空智能体类型
        invalid_type_config = AgentConfig(
            agent_type='',
            enabled=True
        )
        assert invalid_type_config.validate() is False
        
        # 无效配置 - 负数重试次数
        invalid_retries_config = AgentConfig(
            agent_type='tutoring',
            enabled=True,
            max_retries=-1
        )
        assert invalid_retries_config.validate() is False


class TestEnvironmentSettings:
    """测试环境设置"""
    
    def test_load_environment_config(self):
        """测试加载环境配置"""
        with patch.dict(os.environ, {
            'AILEARN_LLM_PROVIDER': 'tongyi',
            'AILEARN_LLM_API_KEY': 'env_key',
            'AILEARN_DATABASE_TYPE': 'postgresql',
            'AILEARN_CACHE_ENABLED': 'true',
            'AILEARN_CACHE_MAX_SIZE': '5000'
        }):
            env_config = load_environment_config()
            
            assert env_config['llm']['provider'] == 'tongyi'
            assert env_config['llm']['api_key'] == 'env_key'
            assert env_config['database']['type'] == 'postgresql'
            assert env_config['cache']['enabled'] is True
            assert env_config['cache']['max_size'] == 5000
    
    def test_validate_config_function(self):
        """测试配置验证函数"""
        # 有效配置
        valid_config = {
            'llm': {
                'provider': 'openai',
                'api_key': 'valid_key',
                'model': 'gpt-3.5-turbo'
            },
            'database': {
                'type': 'sqlite',
                'path': 'valid.db'
            }
        }
        
        validation_result = validate_config(valid_config)
        assert validation_result['valid'] is True
        assert len(validation_result['errors']) == 0
        
        # 无效配置
        invalid_config = {
            'llm': {
                'provider': 'openai'
                # 缺少 api_key
            },
            'database': {
                'type': 'sqlite'
                # 缺少 path
            }
        }
        
        validation_result = validate_config(invalid_config)
        assert validation_result['valid'] is False
        assert len(validation_result['errors']) > 0
    
    def test_default_settings(self):
        """测试默认设置"""
        assert 'llm' in DEFAULT_SETTINGS
        assert 'database' in DEFAULT_SETTINGS
        assert 'cache' in DEFAULT_SETTINGS
        assert 'agents' in DEFAULT_SETTINGS
        
        # 验证默认LLM设置
        default_llm = DEFAULT_SETTINGS['llm']
        assert 'provider' in default_llm
        assert 'model' in default_llm
        assert 'temperature' in default_llm
        
        # 验证默认数据库设置
        default_db = DEFAULT_SETTINGS['database']
        assert 'type' in default_db
        assert 'auto_create_tables' in default_db
        
        # 验证默认缓存设置
        default_cache = DEFAULT_SETTINGS['cache']
        assert 'enabled' in default_cache
        assert 'max_size' in default_cache
        assert 'ttl' in default_cache


if __name__ == "__main__":
    pytest.main([__file__])

class ConfigManager:
    def __init__(self):
        self._config = {}
    
    def get(self, key, default=None):
        return self._config.get(key, default)
    
    def set(self, key, value):
        self._config[key] = value
