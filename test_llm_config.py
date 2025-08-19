#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM配置模块测试文件
该文件用于验证llm_config.py模块的功能是否正常工作
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_config import (
    LLMInterface,
    TongYiLLM,
    OpenAILLM,
    LLMCreator,
    LLMConfig,
    global_llm_config,
    get_default_llm,
    generate_llm_response
)


class TestLLMInterface(unittest.TestCase):
    """测试LLM接口的基本功能"""
    
    def test_interface_methods(self):
        """测试LLM接口是否定义了必要的方法"""
        # 验证接口包含必要的方法
        self.assertTrue(hasattr(LLMInterface, 'generate_response'))
        self.assertTrue(hasattr(LLMInterface, 'stream_response'))


class TestTongYiLLM(unittest.TestCase):
    """测试通义千问LLM实现"""
    
    @patch('llm_config.OpenAI')
    def test_initialization(self, mock_openai):
        """测试通义千问LLM的初始化"""
        # 模拟环境变量
        with patch.dict('os.environ', {'TONG_YI_API_KEY': 'test-api-key'}):
            llm = TongYiLLM()
            # 验证OpenAI客户端是否正确初始化
            mock_openai.assert_called_once_with(
                api_key='test-api-key',
                base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
            )
    
    @patch('llm_config.OpenAI')
    def test_custom_params(self, mock_openai):
        """测试使用自定义参数初始化"""
        llm = TongYiLLM(api_key='custom-key', base_url='custom-url')
        # 验证使用了自定义参数
        mock_openai.assert_called_once_with(
            api_key='custom-key',
            base_url='custom-url'
        )
    
    @patch('llm_config.OpenAI')
    def test_generate_response(self, mock_openai):
        """测试生成响应方法"""
        # 配置mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        
        # 调用方法
        llm = TongYiLLM()
        messages = [{"role": "user", "content": "Hello"}]
        result = llm.generate_response(messages, model="qwen-plus", temperature=0.7)
        
        # 验证调用
        mock_client.chat.completions.create.assert_called_once_with(
            messages=messages,
            model="qwen-plus",
            temperature=0.7
        )
        self.assertEqual(result, mock_response)
    
    @patch('llm_config.OpenAI')
    def test_stream_response(self, mock_openai):
        """测试流式响应方法"""
        # 配置mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        
        # 调用方法
        llm = TongYiLLM()
        messages = [{"role": "user", "content": "Hello"}]
        result = llm.stream_response(messages, model="qwen-plus")
        
        # 验证调用
        mock_client.chat.completions.create.assert_called_once_with(
            messages=messages,
            model="qwen-plus",
            stream=True
        )
        self.assertEqual(result, mock_response)


class TestOpenAILLM(unittest.TestCase):
    """测试OpenAI LLM实现"""
    
    @patch('llm_config.OpenAI')
    def test_initialization(self, mock_openai):
        """测试OpenAI LLM的初始化"""
        # 模拟环境变量
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-api-key'}):
            llm = OpenAILLM()
            # 验证OpenAI客户端是否正确初始化
            mock_openai.assert_called_once_with(
                api_key='test-api-key',
                base_url='https://api.openai.com/v1'
            )


class TestLLMCreator(unittest.TestCase):
    """测试LLM工厂类"""
    
    def test_create_tongyi(self):
        """测试创建通义千问LLM实例"""
        with patch('llm_config.TongYiLLM') as mock_tongyi:
            LLMCreator.create_llm("tongyi", api_key="test-key")
            mock_tongyi.assert_called_once_with(api_key="test-key")
    
    def test_create_openai(self):
        """测试创建OpenAI LLM实例"""
        with patch('llm_config.OpenAILLM') as mock_openai:
            LLMCreator.create_llm("openai", api_key="test-key")
            mock_openai.assert_called_once_with(api_key="test-key")
    
    def test_unsupported_type(self):
        """测试不支持的LLM类型"""
        with self.assertRaises(ValueError):
            LLMCreator.create_llm("unsupported_type")


class TestLLMConfig(unittest.TestCase):
    """测试LLM配置类"""
    
    def setUp(self):
        # 保存原始的全局配置实例
        self.original_config = global_llm_config
        # 创建新的测试实例
        LLMConfig._instance = None
    
    def tearDown(self):
        # 恢复原始的全局配置实例
        LLMConfig._instance = self.original_config
    
    @patch('llm_config.LLMCreator.create_llm')
    def test_singleton_pattern(self, mock_create_llm):
        """测试单例模式"""
        config1 = LLMConfig()
        config2 = LLMConfig()
        self.assertIs(config1, config2)
    
    @patch('llm_config.LLMCreator')
    def test_get_llm_caches_instances(self, mock_creator):
        """测试获取LLM实例时会缓存实例"""
        # 配置mock
        mock_llm = MagicMock()
        mock_creator.create_llm.return_value = mock_llm
        
        # 两次获取相同类型的LLM
        config = LLMConfig()
        llm1 = config.get_llm("tongyi", api_key="test-key")
        llm2 = config.get_llm("tongyi", api_key="test-key")
        
        # 验证只创建了一次实例
        mock_creator.create_llm.assert_called_once()
        # 验证返回的是同一个实例
        self.assertIs(llm1, llm2)
    
    @patch('llm_config.LLMCreator')
    def test_get_llm_different_params(self, mock_creator):
        """测试使用不同参数获取LLM实例"""
        # 配置mock
        mock_llm1 = MagicMock()
        mock_llm2 = MagicMock()
        mock_creator.create_llm.side_effect = [mock_llm1, mock_llm2]
        
        # 使用不同参数获取LLM
        config = LLMConfig()
        llm1 = config.get_llm("tongyi", api_key="key1")
        llm2 = config.get_llm("tongyi", api_key="key2")
        
        # 验证创建了两个不同的实例
        self.assertEqual(mock_creator.create_llm.call_count, 2)
        # 验证返回的是不同的实例
        self.assertIsNot(llm1, llm2)
    
    def test_set_default_llm(self):
        """测试设置默认LLM"""
        config = LLMConfig()
        config.set_default_llm("openai", "gpt-4")
        self.assertEqual(config.default_llm_type, "openai")
        self.assertEqual(config.default_model, "gpt-4")
        
        # 验证清除了缓存的实例
        self.assertEqual(len(config.llm_instances), 0)


class TestUtilityFunctions(unittest.TestCase):
    """测试工具函数"""
    
    @patch('llm_config.global_llm_config')
    def test_get_default_llm(self, mock_config):
        """测试获取默认LLM实例"""
        mock_llm = MagicMock()
        mock_config.get_llm.return_value = mock_llm
        
        llm = get_default_llm()
        
        mock_config.get_llm.assert_called_once()
        self.assertEqual(llm, mock_llm)
    
    @patch('llm_config.global_llm_config')
    def test_generate_llm_response(self, mock_config):
        """测试生成LLM响应的工具函数"""
        # 配置mock
        mock_llm = MagicMock()
        mock_config.get_llm.return_value = mock_llm
        mock_config.default_model = "default-model"
        mock_response = MagicMock()
        mock_llm.generate_response.return_value = mock_response
        
        # 调用函数
        messages = [{"role": "user", "content": "Hello"}]
        result = generate_llm_response(
            messages=messages,
            model="custom-model",
            llm_type="tongyi",
            temperature=0.7
        )
        
        # 验证调用
        mock_config.get_llm.assert_called_once_with("tongyi")
        mock_llm.generate_response.assert_called_once_with(
            messages=messages,
            model="custom-model",
            temperature=0.7
        )
        self.assertEqual(result, mock_response)
    
    @patch('llm_config.global_llm_config')
    def test_generate_llm_response_stream(self, mock_config):
        """测试生成流式LLM响应"""
        # 配置mock
        mock_llm = MagicMock()
        mock_config.get_llm.return_value = mock_llm
        mock_config.default_model = "default-model"
        mock_response = MagicMock()
        mock_llm.stream_response.return_value = mock_response
        
        # 调用函数
        messages = [{"role": "user", "content": "Hello"}]
        result = generate_llm_response(
            messages=messages,
            stream=True
        )
        
        # 验证调用
        mock_config.get_llm.assert_called_once_with(None)
        mock_llm.stream_response.assert_called_once_with(
            messages=messages,
            model="default-model"
        )
        self.assertEqual(result, mock_response)


class TestLLMSwitchExample(unittest.TestCase):
    """测试LLM切换示例"""
    
    def test_llm_switch_example(self):
        """演示如何切换不同的LLM模型"""
        # 获取配置实例
        config = LLMConfig()
        
        # 示例1：使用默认LLM（通义千问）
        print("示例1：使用默认LLM（通义千问）")
        with patch('llm_config.LLMCreator.create_llm', return_value=MagicMock()):
            llm1 = config.get_llm()
            print(f"  获取到的LLM实例类型: {type(llm1).__name__}")
        
        # 示例2：切换到OpenAI
        print("示例2：切换到OpenAI")
        config.set_default_llm("openai", "gpt-3.5-turbo")
        with patch('llm_config.LLMCreator.create_llm', return_value=MagicMock()):
            llm2 = config.get_llm()
            print(f"  获取到的LLM实例类型: {type(llm2).__name__}")
        
        # 示例3：临时使用特定LLM
        print("示例3：临时使用特定LLM")
        with patch('llm_config.LLMCreator.create_llm', return_value=MagicMock()):
            llm3 = config.get_llm("tongyi", api_key="temporary-key")
            print(f"  临时使用通义千问LLM，API Key: temporary-key")
        
        # 示例4：使用工具函数
        print("示例4：使用工具函数")
        with patch('llm_config.generate_llm_response', return_value="模拟响应"):
            response = generate_llm_response(
                messages=[{"role": "user", "content": "Hello"}],
                llm_type="openai",
                stream=True
            )
            print(f"  工具函数返回: {response}")


if __name__ == '__main__':
    unittest.main()