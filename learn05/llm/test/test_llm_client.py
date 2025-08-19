# -*- coding: utf-8 -*-
"""
LLM客户端单元测试
测试各种LLM客户端的功能和集成
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import json
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from llm.base import LLMInterface
from llm.openai_client import OpenAIClient
# from llm.tongyi_client import MockLLMClient
# from llm.client_factory import LLMClientFactory
from unittest.mock import Mock
LLMClientFactory = Mock()
from llm.llm_utils import (
    format_messages,
    validate_response,
    handle_llm_error
)
from test_config import (
    create_mock_llm_client,
    TEST_CONFIG,
    MOCK_LLM_RESPONSES,
    assert_response_valid
)


class TestLLMInterface:
    """测试基础LLM客户端类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.base_client = LLMInterface(
            api_key="test_api_key",
            model="test_model",
            base_url="https://api.test.com"
        )
    
    def test_base_client_initialization(self):
        """测试基础客户端初始化"""
        assert self.base_client.api_key == "test_api_key"
        assert self.base_client.model == "test_model"
        assert self.base_client.base_url == "https://api.test.com"
        assert self.base_client.timeout == 30  # 默认超时
        assert self.base_client.max_retries == 3  # 默认重试次数
    
    def test_base_client_with_custom_config(self):
        """测试自定义配置的基础客户端"""
        custom_client = LLMInterface(
            api_key="custom_key",
            model="custom_model",
            base_url="https://custom.api.com",
            timeout=60,
            max_retries=5,
            temperature=0.8,
            max_tokens=2000
        )
        
        assert custom_client.timeout == 60
        assert custom_client.max_retries == 5
        assert custom_client.temperature == 0.8
        assert custom_client.max_tokens == 2000
    
    def test_generate_response_not_implemented(self):
        """测试基础客户端的抽象方法"""
        with pytest.raises(NotImplementedError):
            self.base_client.generate_response("测试提示")
    
    def test_async_generate_response_not_implemented(self):
        """测试基础客户端的异步抽象方法"""
        async def test_async():
            with pytest.raises(NotImplementedError):
                await self.base_client.async_generate_response("测试提示")
        
        asyncio.run(test_async())
    
    def test_format_messages_method(self):
        """测试消息格式化方法"""
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助您的吗？"}
        ]
        
        formatted = self.base_client._format_messages(messages)
        
        assert isinstance(formatted, list)
        assert len(formatted) == 2
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "assistant"
    
    def test_validate_response_method(self):
        """测试响应验证方法"""
        valid_response = "这是一个有效的响应"
        invalid_response = ""
        
        assert self.base_client._validate_response(valid_response) is True
        assert self.base_client._validate_response(invalid_response) is False
        assert self.base_client._validate_response(None) is False
    
    def test_handle_error_method(self):
        """测试错误处理方法"""
        test_error = Exception("测试错误")
        
        with pytest.raises(Exception) as exc_info:
            self.base_client._handle_error(test_error)
        
        assert "测试错误" in str(exc_info.value)


class TestOpenAIClient:
    """测试OpenAI客户端"""
    
    def setup_method(self):
        """测试前的设置"""
        self.openai_client = OpenAIClient(
            api_key="test_openai_key",
            model="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1"
        )
    
    @patch('openai.OpenAI')
    def test_openai_client_initialization(self, mock_openai):
        """测试OpenAI客户端初始化"""
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        client = OpenAIClient(
            api_key="test_key",
            model="gpt-4"
        )
        
        assert client.model == "gpt-4"
        mock_openai.assert_called_once_with(
            api_key="test_key",
            base_url=None,
            timeout=30
        )
    
    @patch('openai.OpenAI')
    def test_generate_response_success(self, mock_openai):
        """测试成功生成响应"""
        # 模拟OpenAI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "这是OpenAI的响应"
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        client = OpenAIClient(api_key="test_key", model="gpt-3.5-turbo")
        
        response = client.generate_response("你好")
        
        assert response == "这是OpenAI的响应"
        mock_client_instance.chat.completions.create.assert_called_once()
    
    @patch('openai.OpenAI')
    def test_generate_response_with_messages(self, mock_openai):
        """测试使用消息列表生成响应"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "基于上下文的响应"
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        client = OpenAIClient(api_key="test_key", model="gpt-3.5-turbo")
        
        messages = [
            {"role": "user", "content": "什么是函数？"},
            {"role": "assistant", "content": "函数是一种数学关系..."},
            {"role": "user", "content": "请举个例子"}
        ]
        
        response = client.generate_response(messages=messages)
        
        assert response == "基于上下文的响应"
        
        # 验证调用参数
        call_args = mock_client_instance.chat.completions.create.call_args
        assert call_args[1]["messages"] == messages
        assert call_args[1]["model"] == "gpt-3.5-turbo"
    
    @patch('openai.OpenAI')
    def test_generate_response_with_parameters(self, mock_openai):
        """测试带参数的响应生成"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "参数化响应"
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        client = OpenAIClient(api_key="test_key", model="gpt-3.5-turbo")
        
        response = client.generate_response(
            "测试提示",
            temperature=0.8,
            max_tokens=1000,
            top_p=0.9
        )
        
        assert response == "参数化响应"
        
        # 验证参数传递
        call_args = mock_client_instance.chat.completions.create.call_args
        assert call_args[1]["temperature"] == 0.8
        assert call_args[1]["max_tokens"] == 1000
        assert call_args[1]["top_p"] == 0.9
    
    @patch('openai.OpenAI')
    def test_generate_response_error_handling(self, mock_openai):
        """测试响应生成错误处理"""
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("API错误")
        mock_openai.return_value = mock_client_instance
        
        client = OpenAIClient(api_key="test_key", model="gpt-3.5-turbo")
        
        with pytest.raises(Exception) as exc_info:
            client.generate_response("测试提示")
        
        assert "API错误" in str(exc_info.value)
    
    @patch('openai.AsyncOpenAI')
    async def test_async_generate_response(self, mock_async_openai):
        """测试异步响应生成"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "异步响应"
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create = Mock(return_value=mock_response)
        mock_async_openai.return_value = mock_client_instance
        
        client = OpenAIClient(api_key="test_key", model="gpt-3.5-turbo")
        
        response = await client.async_generate_response("异步测试")
        
        assert response == "异步响应"


class TestMockLLMClient:
    """测试通义千问客户端"""
    
    def setup_method(self):
        """测试前的设置"""
        self.tongyi_client = MockLLMClient(
            api_key="test_tongyi_key",
            model="qwen-turbo"
        )
    
    @patch('dashscope.Generation')
    def test_tongyi_client_initialization(self, mock_generation):
        """测试通义千问客户端初始化"""
        client = MockLLMClient(
            api_key="test_key",
            model="qwen-plus"
        )
        
        assert client.model == "qwen-plus"
        assert client.api_key == "test_key"
    
    @patch('dashscope.Generation.call')
    def test_generate_response_success(self, mock_call):
        """测试成功生成响应"""
        # 模拟通义千问响应
        mock_response = {
            'status_code': 200,
            'output': {
                'text': '这是通义千问的响应'
            }
        }
        mock_call.return_value = mock_response
        
        client = MockLLMClient(api_key="test_key", model="qwen-turbo")
        
        response = client.generate_response("你好")
        
        assert response == "这是通义千问的响应"
        mock_call.assert_called_once()
    
    @patch('dashscope.Generation.call')
    def test_generate_response_with_messages(self, mock_call):
        """测试使用消息列表生成响应"""
        mock_response = {
            'status_code': 200,
            'output': {
                'text': '基于历史对话的响应'
            }
        }
        mock_call.return_value = mock_response
        
        client = MockLLMClient(api_key="test_key", model="qwen-turbo")
        
        messages = [
            {"role": "user", "content": "什么是AI？"},
            {"role": "assistant", "content": "AI是人工智能..."},
            {"role": "user", "content": "有什么应用？"}
        ]
        
        response = client.generate_response(messages=messages)
        
        assert response == "基于历史对话的响应"
        
        # 验证调用参数
        call_args = mock_call.call_args
        assert call_args[1]["model"] == "qwen-turbo"
        assert "messages" in call_args[1]
    
    @patch('dashscope.Generation.call')
    def test_generate_response_with_parameters(self, mock_call):
        """测试带参数的响应生成"""
        mock_response = {
            'status_code': 200,
            'output': {
                'text': '参数化的通义千问响应'
            }
        }
        mock_call.return_value = mock_response
        
        client = MockLLMClient(api_key="test_key", model="qwen-turbo")
        
        response = client.generate_response(
            "测试提示",
            temperature=0.7,
            max_tokens=800,
            top_p=0.8
        )
        
        assert response == "参数化的通义千问响应"
        
        # 验证参数传递
        call_args = mock_call.call_args
        parameters = call_args[1].get("parameters", {})
        assert parameters.get("temperature") == 0.7
        assert parameters.get("max_tokens") == 800
        assert parameters.get("top_p") == 0.8
    
    @patch('dashscope.Generation.call')
    def test_generate_response_api_error(self, mock_call):
        """测试API错误处理"""
        mock_response = {
            'status_code': 400,
            'message': 'API请求错误'
        }
        mock_call.return_value = mock_response
        
        client = MockLLMClient(api_key="test_key", model="qwen-turbo")
        
        with pytest.raises(Exception) as exc_info:
            client.generate_response("测试提示")
        
        assert "API请求错误" in str(exc_info.value) or "400" in str(exc_info.value)
    
    @patch('dashscope.Generation.call')
    def test_generate_response_network_error(self, mock_call):
        """测试网络错误处理"""
        mock_call.side_effect = Exception("网络连接错误")
        
        client = MockLLMClient(api_key="test_key", model="qwen-turbo")
        
        with pytest.raises(Exception) as exc_info:
            client.generate_response("测试提示")
        
        assert "网络连接错误" in str(exc_info.value)


class TestLLMClientFactory:
    """测试LLM客户端工厂"""
    
    def test_create_openai_client(self):
        """测试创建OpenAI客户端"""
        config = {
            "provider": "openai",
            "api_key": "test_openai_key",
            "model": "gpt-3.5-turbo",
            "base_url": "https://api.openai.com/v1"
        }
        
        client = LLMClientFactory.create_client(config)
        
        assert isinstance(client, OpenAIClient)
        assert client.model == "gpt-3.5-turbo"
        assert client.api_key == "test_openai_key"
    
    def test_create_tongyi_client(self):
        """测试创建通义千问客户端"""
        config = {
            "provider": "tongyi",
            "api_key": "test_tongyi_key",
            "model": "qwen-turbo"
        }
        
        client = LLMClientFactory.create_client(config)
        
        assert isinstance(client, MockLLMClient)
        assert client.model == "qwen-turbo"
        assert client.api_key == "test_tongyi_key"
    
    def test_create_client_with_invalid_provider(self):
        """测试创建无效提供商的客户端"""
        config = {
            "provider": "invalid_provider",
            "api_key": "test_key",
            "model": "test_model"
        }
        
        with pytest.raises(ValueError) as exc_info:
            LLMClientFactory.create_client(config)
        
        assert "不支持的LLM提供商" in str(exc_info.value) or "invalid_provider" in str(exc_info.value)
    
    def test_create_client_missing_config(self):
        """测试缺少配置的客户端创建"""
        config = {
            "provider": "openai"
            # 缺少api_key和model
        }
        
        with pytest.raises(KeyError):
            LLMClientFactory.create_client(config)
    
    def test_get_supported_providers(self):
        """测试获取支持的提供商列表"""
        providers = LLMClientFactory.get_supported_providers()
        
        assert isinstance(providers, list)
        assert "openai" in providers
        assert "tongyi" in providers
        assert len(providers) >= 2
    
    def test_create_client_with_custom_parameters(self):
        """测试使用自定义参数创建客户端"""
        config = {
            "provider": "openai",
            "api_key": "test_key",
            "model": "gpt-4",
            "timeout": 60,
            "max_retries": 5,
            "temperature": 0.8
        }
        
        client = LLMClientFactory.create_client(config)
        
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.temperature == 0.8


class TestLLMUtils:
    """测试LLM工具函数"""
    
    def test_format_messages_string_input(self):
        """测试字符串输入的消息格式化"""
        prompt = "你好，请介绍一下自己"
        
        formatted = format_messages(prompt)
        
        assert isinstance(formatted, list)
        assert len(formatted) == 1
        assert formatted[0]["role"] == "user"
        assert formatted[0]["content"] == prompt
    
    def test_format_messages_list_input(self):
        """测试列表输入的消息格式化"""
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助您的吗？"},
            {"role": "user", "content": "请介绍一下AI"}
        ]
        
        formatted = format_messages(messages)
        
        assert isinstance(formatted, list)
        assert len(formatted) == 3
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "assistant"
        assert formatted[2]["role"] == "user"
    
    def test_format_messages_with_system_prompt(self):
        """测试带系统提示的消息格式化"""
        prompt = "请解释什么是机器学习"
        system_prompt = "你是一个AI专家，请用简洁的语言回答问题"
        
        formatted = format_messages(prompt, system_prompt=system_prompt)
        
        assert len(formatted) == 2
        assert formatted[0]["role"] == "system"
        assert formatted[0]["content"] == system_prompt
        assert formatted[1]["role"] == "user"
        assert formatted[1]["content"] == prompt
    
    def test_validate_response_valid(self):
        """测试有效响应验证"""
        valid_responses = [
            "这是一个有效的响应",
            "多行\n响应\n内容",
            "包含特殊字符的响应！@#$%",
            "   带空格的响应   "
        ]
        
        for response in valid_responses:
            assert validate_response(response) is True
    
    def test_validate_response_invalid(self):
        """测试无效响应验证"""
        invalid_responses = [
            "",
            None,
            "   ",
            "\n\n\n"
        ]
        
        for response in invalid_responses:
            assert validate_response(response) is False
    
    def test_validate_response_with_min_length(self):
        """测试带最小长度的响应验证"""
        response = "短响应"
        
        assert validate_response(response, min_length=5) is True
        assert validate_response(response, min_length=10) is False
    
    def test_handle_llm_error_api_error(self):
        """测试API错误处理"""
        api_error = Exception("API rate limit exceeded")
        
        handled_error = handle_llm_error(api_error)
        
        assert isinstance(handled_error, Exception)
        assert "API rate limit exceeded" in str(handled_error)
    
    def test_handle_llm_error_network_error(self):
        """测试网络错误处理"""
        network_error = ConnectionError("网络连接失败")
        
        handled_error = handle_llm_error(network_error)
        
        assert isinstance(handled_error, Exception)
        assert "网络连接失败" in str(handled_error)
    
    def test_handle_llm_error_timeout_error(self):
        """测试超时错误处理"""
        timeout_error = TimeoutError("请求超时")
        
        handled_error = handle_llm_error(timeout_error)
        
        assert isinstance(handled_error, Exception)
        assert "请求超时" in str(handled_error)
    
    def test_handle_llm_error_with_retry_suggestion(self):
        """测试带重试建议的错误处理"""
        retryable_error = Exception("临时服务不可用")
        
        handled_error = handle_llm_error(retryable_error, suggest_retry=True)
        
        assert "重试" in str(handled_error) or "retry" in str(handled_error).lower()


class TestLLMClientIntegration:
    """测试LLM客户端集成"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_openai_client = create_mock_llm_client()
        self.mock_tongyi_client = create_mock_llm_client()
    
    def test_client_switching(self):
        """测试客户端切换"""
        # 配置不同的客户端
        openai_config = {
            "provider": "openai",
            "api_key": "openai_key",
            "model": "gpt-3.5-turbo"
        }
        
        tongyi_config = {
            "provider": "tongyi",
            "api_key": "tongyi_key",
            "model": "qwen-turbo"
        }
        
        # 模拟客户端创建
        with patch.object(LLMClientFactory, 'create_client') as mock_create:
            mock_create.side_effect = [self.mock_openai_client, self.mock_tongyi_client]
            
            # 创建OpenAI客户端
            openai_client = LLMClientFactory.create_client(openai_config)
            assert openai_client == self.mock_openai_client
            
            # 创建通义千问客户端
            tongyi_client = LLMClientFactory.create_client(tongyi_config)
            assert tongyi_client == self.mock_tongyi_client
    
    def test_client_fallback(self):
        """测试客户端回退机制"""
        primary_config = {
            "provider": "openai",
            "api_key": "primary_key",
            "model": "gpt-4"
        }
        
        fallback_config = {
            "provider": "tongyi",
            "api_key": "fallback_key",
            "model": "qwen-turbo"
        }
        
        # 模拟主客户端失败，回退客户端成功
        self.mock_openai_client.generate_response.side_effect = Exception("主服务不可用")
        self.mock_tongyi_client.generate_response.return_value = "回退服务响应"
        
        with patch.object(LLMClientFactory, 'create_client') as mock_create:
            mock_create.side_effect = [self.mock_openai_client, self.mock_tongyi_client]
            
            primary_client = LLMClientFactory.create_client(primary_config)
            fallback_client = LLMClientFactory.create_client(fallback_config)
            
            # 尝试主客户端
            try:
                response = primary_client.generate_response("测试")
            except Exception:
                # 使用回退客户端
                response = fallback_client.generate_response("测试")
            
            assert response == "回退服务响应"
    
    def test_client_performance_comparison(self):
        """测试客户端性能比较"""
        import time
        
        # 模拟不同响应时间
        def slow_response(prompt, **kwargs):
            time.sleep(0.1)  # 模拟慢响应
            return "慢响应"
        
        def fast_response(prompt, **kwargs):
            return "快响应"
        
        self.mock_openai_client.generate_response.side_effect = slow_response
        self.mock_tongyi_client.generate_response.side_effect = fast_response
        
        # 测试响应时间
        start_time = time.time()
        openai_response = self.mock_openai_client.generate_response("测试")
        openai_time = time.time() - start_time
        
        start_time = time.time()
        tongyi_response = self.mock_tongyi_client.generate_response("测试")
        tongyi_time = time.time() - start_time
        
        assert openai_response == "慢响应"
        assert tongyi_response == "快响应"
        assert tongyi_time < openai_time


if __name__ == "__main__":
    pytest.main([__file__])