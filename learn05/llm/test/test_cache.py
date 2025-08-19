# -*- coding: utf-8 -*-
"""
缓存系统单元测试
测试LLM缓存管理器和相关功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import time
import json
import hashlib

# from llm.cache.cache_manager import CacheManager
# from llm.cache import (
#     generate_cache_key,
#     CachedLLMWrapper,
#     cache_response
# )
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from test_config import (
    create_mock_llm_client,
    TEST_CONFIG,
    MOCK_LLM_RESPONSES,
    assert_response_valid
)


class TestCacheManager:
    """测试缓存管理器类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.cache_manager = CacheManager(
            max_size=100,
            ttl=3600,  # 1小时
            cleanup_interval=300  # 5分钟
        )
    
    def test_cache_manager_initialization(self):
        """测试缓存管理器初始化"""
        assert self.cache_manager.max_size == 100
        assert self.cache_manager.ttl == 3600
        assert self.cache_manager.cleanup_interval == 300
        assert isinstance(self.cache_manager.cache, dict)
        assert isinstance(self.cache_manager.access_times, dict)
        assert isinstance(self.cache_manager.hit_count, int)
        assert isinstance(self.cache_manager.miss_count, int)
    
    def test_set_and_get_cache(self):
        """测试设置和获取缓存"""
        key = "test_key_001"
        value = {"response": "这是一个测试响应", "metadata": {"type": "test"}}
        
        # 设置缓存
        self.cache_manager.set(key, value)
        
        # 获取缓存
        cached_value = self.cache_manager.get(key)
        
        assert cached_value is not None
        assert cached_value["response"] == "这是一个测试响应"
        assert cached_value["metadata"]["type"] == "test"
        
        # 检查统计信息
        assert self.cache_manager.hit_count == 1
        assert self.cache_manager.miss_count == 0
    
    def test_get_nonexistent_cache(self):
        """测试获取不存在的缓存"""
        nonexistent_value = self.cache_manager.get("nonexistent_key")
        
        assert nonexistent_value is None
        assert self.cache_manager.hit_count == 0
        assert self.cache_manager.miss_count == 1
    
    def test_cache_expiration(self):
        """测试缓存过期"""
        # 创建一个短TTL的缓存管理器
        short_ttl_manager = CacheManager(
            max_size=100,
            ttl=0.1,  # 0.1秒TTL
            cleanup_interval=300
        )
        
        key = "test_key_002"
        value = "测试值"
        
        # 设置缓存
        short_ttl_manager.set(key, value)
        
        # 立即获取应该成功
        cached_value = short_ttl_manager.get(key)
        assert cached_value == value
        
        # 等待过期
        time.sleep(0.2)
        
        # 再次获取应该失败
        expired_value = short_ttl_manager.get(key)
        assert expired_value is None
    
    def test_cache_size_limit(self):
        """测试缓存大小限制"""
        # 创建一个小容量的缓存管理器
        small_cache_manager = CacheManager(
            max_size=3,
            ttl=3600,
            cleanup_interval=300
        )
        
        # 添加超过容量的缓存项
        for i in range(5):
            key = f"test_key_{i:03d}"
            value = f"测试值 {i}"
            small_cache_manager.set(key, value)
        
        # 检查缓存大小
        assert len(small_cache_manager.cache) <= small_cache_manager.max_size
        
        # 最新的项应该存在
        assert small_cache_manager.get("test_key_004") is not None
        
        # 最旧的项可能被淘汰
        assert small_cache_manager.get("test_key_000") is None
    
    def test_cache_update(self):
        """测试缓存更新"""
        key = "test_key_003"
        original_value = "原始值"
        updated_value = "更新值"
        
        # 设置原始值
        self.cache_manager.set(key, original_value)
        assert self.cache_manager.get(key) == original_value
        
        # 更新值
        self.cache_manager.set(key, updated_value)
        assert self.cache_manager.get(key) == updated_value
    
    def test_cache_deletion(self):
        """测试缓存删除"""
        key = "test_key_004"
        value = "待删除的值"
        
        # 设置缓存
        self.cache_manager.set(key, value)
        assert self.cache_manager.get(key) == value
        
        # 删除缓存
        self.cache_manager.delete(key)
        assert self.cache_manager.get(key) is None
        
        # 删除不存在的键应该不报错
        self.cache_manager.delete("nonexistent_key")
    
    def test_cache_clear(self):
        """测试清空缓存"""
        # 添加多个缓存项
        for i in range(5):
            key = f"test_key_{i:03d}"
            value = f"测试值 {i}"
            self.cache_manager.set(key, value)
        
        # 确认缓存不为空
        assert len(self.cache_manager.cache) == 5
        
        # 清空缓存
        self.cache_manager.clear()
        
        # 确认缓存已清空
        assert len(self.cache_manager.cache) == 0
        assert len(self.cache_manager.access_times) == 0
    
    def test_cache_statistics(self):
        """测试缓存统计信息"""
        # 添加一些缓存项
        for i in range(3):
            key = f"test_key_{i:03d}"
            value = f"测试值 {i}"
            self.cache_manager.set(key, value)
        
        # 访问一些缓存项
        self.cache_manager.get("test_key_000")  # 命中
        self.cache_manager.get("test_key_001")  # 命中
        self.cache_manager.get("nonexistent")   # 未命中
        
        # 获取统计信息
        stats = self.cache_manager.get_statistics()
        
        assert stats["total_items"] == 3
        assert stats["hit_count"] == 2
        assert stats["miss_count"] == 1
        assert stats["hit_rate"] == 2/3
        assert stats["max_size"] == 100
    
    def test_cache_cleanup(self):
        """测试缓存清理"""
        # 创建一个短TTL的缓存管理器
        cleanup_manager = CacheManager(
            max_size=100,
            ttl=0.1,  # 0.1秒TTL
            cleanup_interval=300
        )
        
        # 添加缓存项
        for i in range(5):
            key = f"test_key_{i:03d}"
            value = f"测试值 {i}"
            cleanup_manager.set(key, value)
        
        # 确认缓存项存在
        assert len(cleanup_manager.cache) == 5
        
        # 等待过期
        time.sleep(0.2)
        
        # 手动清理
        cleaned_count = cleanup_manager.cleanup_expired()
        
        # 确认过期项被清理
        assert cleaned_count == 5
        assert len(cleanup_manager.cache) == 0
    
    def test_cache_contains(self):
        """测试缓存包含检查"""
        key = "test_key_005"
        value = "测试值"
        
        # 键不存在时
        assert not self.cache_manager.contains(key)
        
        # 设置缓存后
        self.cache_manager.set(key, value)
        assert self.cache_manager.contains(key)
        
        # 删除后
        self.cache_manager.delete(key)
        assert not self.cache_manager.contains(key)
    
    def test_cache_keys(self):
        """测试获取缓存键列表"""
        # 添加缓存项
        keys = ["key1", "key2", "key3"]
        for key in keys:
            self.cache_manager.set(key, f"value_{key}")
        
        # 获取所有键
        cached_keys = self.cache_manager.get_keys()
        
        assert len(cached_keys) == 3
        for key in keys:
            assert key in cached_keys


class TestCacheUtils:
    """测试缓存工具函数"""
    
    def test_generate_cache_key_simple(self):
        """测试简单缓存键生成"""
        prompt = "请解释什么是函数"
        model = "gpt-3.5-turbo"
        
        key = generate_cache_key(prompt, model)
        
        assert isinstance(key, str)
        assert len(key) > 0
        
        # 相同输入应该生成相同的键
        key2 = generate_cache_key(prompt, model)
        assert key == key2
        
        # 不同输入应该生成不同的键
        key3 = generate_cache_key("不同的提示", model)
        assert key != key3
    
    def test_generate_cache_key_with_parameters(self):
        """测试带参数的缓存键生成"""
        prompt = "请解释什么是函数"
        model = "gpt-3.5-turbo"
        parameters = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9
        }
        
        key = generate_cache_key(prompt, model, parameters)
        
        assert isinstance(key, str)
        assert len(key) > 0
        
        # 相同参数应该生成相同的键
        key2 = generate_cache_key(prompt, model, parameters)
        assert key == key2
        
        # 不同参数应该生成不同的键
        different_params = parameters.copy()
        different_params["temperature"] = 0.5
        key3 = generate_cache_key(prompt, model, different_params)
        assert key != key3
    
    def test_generate_cache_key_with_context(self):
        """测试带上下文的缓存键生成"""
        prompt = "继续解释"
        model = "gpt-3.5-turbo"
        context = [
            {"role": "user", "content": "什么是函数？"},
            {"role": "assistant", "content": "函数是一种数学关系..."}
        ]
        
        key = generate_cache_key(prompt, model, context=context)
        
        assert isinstance(key, str)
        assert len(key) > 0
        
        # 相同上下文应该生成相同的键
        key2 = generate_cache_key(prompt, model, context=context)
        assert key == key2
        
        # 不同上下文应该生成不同的键
        different_context = context + [{"role": "user", "content": "更多信息"}]
        key3 = generate_cache_key(prompt, model, context=different_context)
        assert key != key3
    
    def test_cache_response_decorator(self):
        """测试缓存响应装饰器"""
        cache_manager = CacheManager(max_size=10, ttl=3600)
        
        @cache_response(cache_manager)
        def mock_llm_call(prompt: str, model: str = "gpt-3.5-turbo") -> str:
            # 模拟LLM调用
            return f"响应: {prompt}"
        
        prompt = "测试提示"
        
        # 第一次调用
        response1 = mock_llm_call(prompt)
        assert response1 == "响应: 测试提示"
        assert cache_manager.hit_count == 0
        assert cache_manager.miss_count == 1
        
        # 第二次调用应该从缓存获取
        response2 = mock_llm_call(prompt)
        assert response2 == "响应: 测试提示"
        assert cache_manager.hit_count == 1
        assert cache_manager.miss_count == 1
        
        # 不同提示应该产生新的调用
        response3 = mock_llm_call("不同的提示")
        assert response3 == "响应: 不同的提示"
        assert cache_manager.hit_count == 1
        assert cache_manager.miss_count == 2


class TestCachedLLMWrapper:
    """测试缓存LLM包装器"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.cache_manager = CacheManager(max_size=50, ttl=3600)
        
        self.cached_wrapper = CachedLLMWrapper(
            llm_client=self.mock_llm_client,
            cache_manager=self.cache_manager,
            enable_cache=True
        )
    
    def test_wrapper_initialization(self):
        """测试包装器初始化"""
        assert self.cached_wrapper.llm_client == self.mock_llm_client
        assert self.cached_wrapper.cache_manager == self.cache_manager
        assert self.cached_wrapper.enable_cache is True
    
    def test_cached_generate_response(self):
        """测试缓存的响应生成"""
        self.mock_llm_client.generate_response.return_value = "这是一个测试响应"
        
        prompt = "请解释什么是函数"
        
        # 第一次调用
        response1 = self.cached_wrapper.generate_response(prompt)
        assert response1 == "这是一个测试响应"
        assert self.mock_llm_client.generate_response.call_count == 1
        assert self.cache_manager.hit_count == 0
        assert self.cache_manager.miss_count == 1
        
        # 第二次调用应该从缓存获取
        response2 = self.cached_wrapper.generate_response(prompt)
        assert response2 == "这是一个测试响应"
        assert self.mock_llm_client.generate_response.call_count == 1  # 没有新的调用
        assert self.cache_manager.hit_count == 1
        assert self.cache_manager.miss_count == 1
    
    def test_cached_generate_response_with_parameters(self):
        """测试带参数的缓存响应生成"""
        self.mock_llm_client.generate_response.return_value = "参数化响应"
        
        prompt = "解释函数概念"
        parameters = {"temperature": 0.7, "max_tokens": 500}
        
        # 第一次调用
        response1 = self.cached_wrapper.generate_response(
            prompt, 
            model="gpt-3.5-turbo",
            **parameters
        )
        assert response1 == "参数化响应"
        assert self.mock_llm_client.generate_response.call_count == 1
        
        # 相同参数的第二次调用应该从缓存获取
        response2 = self.cached_wrapper.generate_response(
            prompt,
            model="gpt-3.5-turbo", 
            **parameters
        )
        assert response2 == "参数化响应"
        assert self.mock_llm_client.generate_response.call_count == 1
        
        # 不同参数应该产生新的调用
        different_params = {"temperature": 0.5, "max_tokens": 500}
        self.mock_llm_client.generate_response.return_value = "不同参数响应"
        
        response3 = self.cached_wrapper.generate_response(
            prompt,
            model="gpt-3.5-turbo",
            **different_params
        )
        assert response3 == "不同参数响应"
        assert self.mock_llm_client.generate_response.call_count == 2
    
    def test_cached_generate_response_with_context(self):
        """测试带上下文的缓存响应生成"""
        self.mock_llm_client.generate_response.return_value = "上下文响应"
        
        messages = [
            {"role": "user", "content": "什么是函数？"},
            {"role": "assistant", "content": "函数是一种数学关系..."},
            {"role": "user", "content": "请举个例子"}
        ]
        
        # 第一次调用
        response1 = self.cached_wrapper.generate_response(
            messages=messages,
            model="gpt-3.5-turbo"
        )
        assert response1 == "上下文响应"
        assert self.mock_llm_client.generate_response.call_count == 1
        
        # 相同上下文的第二次调用应该从缓存获取
        response2 = self.cached_wrapper.generate_response(
            messages=messages,
            model="gpt-3.5-turbo"
        )
        assert response2 == "上下文响应"
        assert self.mock_llm_client.generate_response.call_count == 1
    
    def test_cache_disabled(self):
        """测试禁用缓存"""
        # 创建禁用缓存的包装器
        no_cache_wrapper = CachedLLMWrapper(
            llm_client=self.mock_llm_client,
            cache_manager=self.cache_manager,
            enable_cache=False
        )
        
        self.mock_llm_client.generate_response.return_value = "无缓存响应"
        
        prompt = "测试提示"
        
        # 第一次调用
        response1 = no_cache_wrapper.generate_response(prompt)
        assert response1 == "无缓存响应"
        assert self.mock_llm_client.generate_response.call_count == 1
        
        # 第二次调用应该再次调用LLM（不使用缓存）
        response2 = no_cache_wrapper.generate_response(prompt)
        assert response2 == "无缓存响应"
        assert self.mock_llm_client.generate_response.call_count == 2
        
        # 缓存统计应该没有变化
        assert self.cache_manager.hit_count == 0
        assert self.cache_manager.miss_count == 0
    
    def test_cache_error_handling(self):
        """测试缓存错误处理"""
        # 模拟缓存错误
        self.cache_manager.get = Mock(side_effect=Exception("缓存读取错误"))
        self.cache_manager.set = Mock(side_effect=Exception("缓存写入错误"))
        
        self.mock_llm_client.generate_response.return_value = "错误处理响应"
        
        prompt = "测试错误处理"
        
        # 即使缓存出错，也应该能正常调用LLM
        response = self.cached_wrapper.generate_response(prompt)
        assert response == "错误处理响应"
        assert self.mock_llm_client.generate_response.call_count == 1
    
    def test_cache_statistics_integration(self):
        """测试缓存统计信息集成"""
        self.mock_llm_client.generate_response.return_value = "统计测试响应"
        
        # 进行多次调用
        prompts = ["提示1", "提示2", "提示1", "提示3", "提示2"]
        
        for prompt in prompts:
            self.cached_wrapper.generate_response(prompt)
        
        # 检查统计信息
        stats = self.cache_manager.get_statistics()
        
        # 应该有3个唯一的缓存项
        assert stats["total_items"] == 3
        
        # 应该有2次缓存命中（提示1和提示2各重复一次）
        assert stats["hit_count"] == 2
        
        # 应该有3次缓存未命中（3个唯一提示的首次调用）
        assert stats["miss_count"] == 3
        
        # 命中率应该是 2/5 = 0.4
        assert abs(stats["hit_rate"] - 0.4) < 0.01
    
    def test_clear_cache(self):
        """测试清空缓存"""
        self.mock_llm_client.generate_response.return_value = "清空测试响应"
        
        prompt = "测试清空缓存"
        
        # 第一次调用
        response1 = self.cached_wrapper.generate_response(prompt)
        assert self.cache_manager.get_statistics()["total_items"] == 1
        
        # 清空缓存
        self.cached_wrapper.clear_cache()
        assert self.cache_manager.get_statistics()["total_items"] == 0
        
        # 再次调用应该重新调用LLM
        response2 = self.cached_wrapper.generate_response(prompt)
        assert self.mock_llm_client.generate_response.call_count == 2
    
    def test_cache_with_custom_key_generator(self):
        """测试自定义缓存键生成器"""
        def custom_key_generator(prompt, model, **kwargs):
            # 简单的自定义键生成器
            return f"custom_{hash(prompt)}_{model}"
        
        custom_wrapper = CachedLLMWrapper(
            llm_client=self.mock_llm_client,
            cache_manager=self.cache_manager,
            enable_cache=True,
            key_generator=custom_key_generator
        )
        
        self.mock_llm_client.generate_response.return_value = "自定义键响应"
        
        prompt = "测试自定义键"
        
        # 第一次调用
        response1 = custom_wrapper.generate_response(prompt)
        assert response1 == "自定义键响应"
        
        # 检查缓存键是否使用自定义格式
        keys = self.cache_manager.get_keys()
        assert len(keys) == 1
        assert keys[0].startswith("custom_")
        
        # 第二次调用应该从缓存获取
        response2 = custom_wrapper.generate_response(prompt)
        assert response2 == "自定义键响应"
        assert self.mock_llm_client.generate_response.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__])

class LLMCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value):
        self._cache[key] = value
