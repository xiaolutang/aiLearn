# -*- coding: utf-8 -*-
"""
上下文管理单元测试
测试上下文管理器和相关工具的功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import time

from llm.context.context_manager import ContextManager
from llm.utils.context_management import (
    get_conversation_summary,
    ContextAwareLLMWrapper
)
from test_config import (
    create_mock_llm_client,
    TEST_CONFIG,
    MOCK_LLM_RESPONSES,
    assert_response_valid
)


class TestContextManager:
    """测试上下文管理器类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.context_manager = ContextManager(
            max_context_length=1000,
            max_sessions=100,
            session_timeout=3600  # 1小时
        )
    
    def test_context_manager_initialization(self):
        """测试上下文管理器初始化"""
        assert self.context_manager.max_context_length == 1000
        assert self.context_manager.max_sessions == 100
        assert self.context_manager.session_timeout == 3600
        assert isinstance(self.context_manager.sessions, dict)
        assert isinstance(self.context_manager.contexts, dict)
    
    def test_create_session(self):
        """测试创建会话"""
        session_id = "test_session_001"
        user_id = "user_123"
        
        session = self.context_manager.create_session(
            session_id=session_id,
            user_id=user_id,
            metadata={"subject": "数学", "grade": "高一"}
        )
        
        assert session["session_id"] == session_id
        assert session["user_id"] == user_id
        assert session["metadata"]["subject"] == "数学"
        assert session["metadata"]["grade"] == "高一"
        assert "created_at" in session
        assert "last_activity" in session
        
        # 检查会话是否被存储
        assert session_id in self.context_manager.sessions
        assert session_id in self.context_manager.contexts
    
    def test_get_session(self):
        """测试获取会话"""
        session_id = "test_session_002"
        user_id = "user_456"
        
        # 创建会话
        created_session = self.context_manager.create_session(
            session_id=session_id,
            user_id=user_id
        )
        
        # 获取会话
        retrieved_session = self.context_manager.get_session(session_id)
        
        assert retrieved_session is not None
        assert retrieved_session["session_id"] == session_id
        assert retrieved_session["user_id"] == user_id
    
    def test_get_nonexistent_session(self):
        """测试获取不存在的会话"""
        nonexistent_session = self.context_manager.get_session("nonexistent_session")
        assert nonexistent_session is None
    
    def test_add_context(self):
        """测试添加上下文"""
        session_id = "test_session_003"
        self.context_manager.create_session(session_id, "user_789")
        
        # 添加用户消息
        self.context_manager.add_context(
            session_id=session_id,
            role="user",
            content="请帮我分析这道数学题",
            metadata={"subject": "数学", "type": "问题"}
        )
        
        # 添加助手回复
        self.context_manager.add_context(
            session_id=session_id,
            role="assistant",
            content="好的，我来帮您分析这道数学题",
            metadata={"type": "回复"}
        )
        
        # 检查上下文
        context = self.context_manager.get_context(session_id)
        assert len(context) == 2
        
        assert context[0]["role"] == "user"
        assert context[0]["content"] == "请帮我分析这道数学题"
        assert context[0]["metadata"]["subject"] == "数学"
        
        assert context[1]["role"] == "assistant"
        assert context[1]["content"] == "好的，我来帮您分析这道数学题"
    
    def test_get_context(self):
        """测试获取上下文"""
        session_id = "test_session_004"
        self.context_manager.create_session(session_id, "user_101")
        
        # 添加多条上下文
        messages = [
            {"role": "user", "content": "第一条消息"},
            {"role": "assistant", "content": "第一条回复"},
            {"role": "user", "content": "第二条消息"},
            {"role": "assistant", "content": "第二条回复"}
        ]
        
        for msg in messages:
            self.context_manager.add_context(
                session_id=session_id,
                role=msg["role"],
                content=msg["content"]
            )
        
        # 获取完整上下文
        full_context = self.context_manager.get_context(session_id)
        assert len(full_context) == 4
        
        # 获取限制数量的上下文
        limited_context = self.context_manager.get_context(session_id, limit=2)
        assert len(limited_context) == 2
        # 应该返回最新的2条消息
        assert limited_context[0]["content"] == "第二条消息"
        assert limited_context[1]["content"] == "第二条回复"
    
    def test_get_context_for_llm(self):
        """测试获取LLM格式的上下文"""
        session_id = "test_session_005"
        self.context_manager.create_session(session_id, "user_202")
        
        # 添加上下文
        self.context_manager.add_context(
            session_id=session_id,
            role="user",
            content="你好"
        )
        
        self.context_manager.add_context(
            session_id=session_id,
            role="assistant",
            content="你好！有什么可以帮助您的吗？"
        )
        
        # 获取LLM格式的上下文
        llm_context = self.context_manager.get_context_for_llm(session_id)
        
        assert isinstance(llm_context, list)
        assert len(llm_context) == 2
        
        # 检查格式
        for msg in llm_context:
            assert "role" in msg
            assert "content" in msg
            assert msg["role"] in ["user", "assistant", "system"]
    
    def test_clear_context(self):
        """测试清除上下文"""
        session_id = "test_session_006"
        self.context_manager.create_session(session_id, "user_303")
        
        # 添加上下文
        self.context_manager.add_context(session_id, "user", "测试消息")
        assert len(self.context_manager.get_context(session_id)) == 1
        
        # 清除上下文
        self.context_manager.clear_context(session_id)
        assert len(self.context_manager.get_context(session_id)) == 0
    
    def test_update_session_activity(self):
        """测试更新会话活动时间"""
        session_id = "test_session_007"
        session = self.context_manager.create_session(session_id, "user_404")
        
        original_activity = session["last_activity"]
        
        # 等待一小段时间
        time.sleep(0.1)
        
        # 更新活动时间
        self.context_manager.update_session_activity(session_id)
        
        updated_session = self.context_manager.get_session(session_id)
        assert updated_session["last_activity"] > original_activity
    
    def test_delete_session(self):
        """测试删除会话"""
        session_id = "test_session_008"
        self.context_manager.create_session(session_id, "user_505")
        
        # 确认会话存在
        assert self.context_manager.get_session(session_id) is not None
        
        # 删除会话
        self.context_manager.delete_session(session_id)
        
        # 确认会话已删除
        assert self.context_manager.get_session(session_id) is None
        assert session_id not in self.context_manager.sessions
        assert session_id not in self.context_manager.contexts
    
    def test_cleanup_expired_sessions(self):
        """测试清理过期会话"""
        # 创建一个短超时时间的管理器
        short_timeout_manager = ContextManager(
            max_context_length=1000,
            max_sessions=100,
            session_timeout=0.1  # 0.1秒超时
        )
        
        session_id = "test_session_009"
        short_timeout_manager.create_session(session_id, "user_606")
        
        # 确认会话存在
        assert short_timeout_manager.get_session(session_id) is not None
        
        # 等待超时
        time.sleep(0.2)
        
        # 清理过期会话
        cleaned_count = short_timeout_manager.cleanup_expired_sessions()
        
        # 确认会话已被清理
        assert cleaned_count >= 1
        assert short_timeout_manager.get_session(session_id) is None
    
    def test_context_length_limit(self):
        """测试上下文长度限制"""
        # 创建一个小容量的管理器
        small_manager = ContextManager(
            max_context_length=100,  # 100字符限制
            max_sessions=10,
            session_timeout=3600
        )
        
        session_id = "test_session_010"
        small_manager.create_session(session_id, "user_707")
        
        # 添加长消息
        long_message = "这是一条很长的消息，" * 20  # 超过100字符
        
        small_manager.add_context(
            session_id=session_id,
            role="user",
            content=long_message
        )
        
        # 添加更多消息
        for i in range(5):
            small_manager.add_context(
                session_id=session_id,
                role="assistant",
                content=f"回复消息 {i}"
            )
        
        # 检查上下文是否被截断
        context = small_manager.get_context(session_id)
        total_length = sum(len(msg["content"]) for msg in context)
        
        # 总长度应该在限制范围内
        assert total_length <= small_manager.max_context_length * 1.2  # 允许一些缓冲
    
    def test_session_metadata_update(self):
        """测试会话元数据更新"""
        session_id = "test_session_011"
        self.context_manager.create_session(
            session_id=session_id,
            user_id="user_808",
            metadata={"subject": "数学", "grade": "高一"}
        )
        
        # 更新元数据
        new_metadata = {"subject": "物理", "grade": "高二", "difficulty": "中等"}
        self.context_manager.update_session_metadata(session_id, new_metadata)
        
        # 检查更新
        session = self.context_manager.get_session(session_id)
        assert session["metadata"]["subject"] == "物理"
        assert session["metadata"]["grade"] == "高二"
        assert session["metadata"]["difficulty"] == "中等"
    
    def test_get_session_statistics(self):
        """测试获取会话统计信息"""
        session_id = "test_session_012"
        self.context_manager.create_session(session_id, "user_909")
        
        # 添加一些上下文
        for i in range(10):
            self.context_manager.add_context(
                session_id=session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"消息 {i}"
            )
        
        # 获取统计信息
        stats = self.context_manager.get_session_statistics(session_id)
        
        assert stats["message_count"] == 10
        assert stats["user_messages"] == 5
        assert stats["assistant_messages"] == 5
        assert "total_characters" in stats
        assert "average_message_length" in stats
        assert "session_duration" in stats


class TestContextManagementUtils:
    """测试上下文管理工具函数"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
    
    def test_get_conversation_summary(self):
        """测试获取对话摘要"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["conversation_summary"]
        
        conversation_history = [
            {"role": "user", "content": "请帮我解释一下二次函数"},
            {"role": "assistant", "content": "二次函数是形如 f(x) = ax² + bx + c 的函数"},
            {"role": "user", "content": "那顶点公式是什么？"},
            {"role": "assistant", "content": "顶点公式是 x = -b/(2a)"}
        ]
        
        summary = get_conversation_summary(
            conversation_history=conversation_history,
            llm_client=self.mock_llm_client,
            max_length=200
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "二次函数" in summary
        
        # 验证LLM客户端被调用
        self.mock_llm_client.generate_response.assert_called_once()
    
    def test_get_conversation_summary_empty_history(self):
        """测试空对话历史的摘要"""
        summary = get_conversation_summary(
            conversation_history=[],
            llm_client=self.mock_llm_client
        )
        
        assert summary == "暂无对话内容"
        # 空历史不应该调用LLM
        self.mock_llm_client.generate_response.assert_not_called()
    
    def test_get_conversation_summary_single_message(self):
        """测试单条消息的摘要"""
        conversation_history = [
            {"role": "user", "content": "你好"}
        ]
        
        summary = get_conversation_summary(
            conversation_history=conversation_history,
            llm_client=self.mock_llm_client
        )
        
        # 单条消息应该直接返回内容
        assert "你好" in summary
    
    def test_get_conversation_summary_with_error(self):
        """测试摘要生成错误处理"""
        self.mock_llm_client.generate_response.side_effect = Exception("LLM服务不可用")
        
        conversation_history = [
            {"role": "user", "content": "测试消息"},
            {"role": "assistant", "content": "测试回复"}
        ]
        
        summary = get_conversation_summary(
            conversation_history=conversation_history,
            llm_client=self.mock_llm_client
        )
        
        # 错误时应该返回默认摘要
        assert "对话摘要生成失败" in summary or "无法生成摘要" in summary


class TestContextAwareLLMWrapper:
    """测试上下文感知的LLM包装器"""
    
    def setup_method(self):
        """测试前的设置"""
        self.mock_llm_client = create_mock_llm_client()
        self.context_manager = ContextManager()
        
        self.wrapper = ContextAwareLLMWrapper(
            llm_client=self.mock_llm_client,
            context_manager=self.context_manager,
            max_context_messages=10
        )
    
    def test_wrapper_initialization(self):
        """测试包装器初始化"""
        assert self.wrapper.llm_client == self.mock_llm_client
        assert self.wrapper.context_manager == self.context_manager
        assert self.wrapper.max_context_messages == 10
    
    def test_generate_response_with_context(self):
        """测试带上下文的响应生成"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["context_aware_response"]
        
        session_id = "test_session_013"
        self.context_manager.create_session(session_id, "user_1010")
        
        # 添加历史上下文
        self.context_manager.add_context(
            session_id=session_id,
            role="user",
            content="我想学习数学"
        )
        
        self.context_manager.add_context(
            session_id=session_id,
            role="assistant",
            content="好的，我可以帮助您学习数学"
        )
        
        # 生成新的响应
        response = self.wrapper.generate_response(
            session_id=session_id,
            user_message="请解释一下二次函数",
            system_prompt="你是一个数学老师"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        # 验证LLM客户端被调用
        self.mock_llm_client.generate_response.assert_called_once()
        
        # 检查上下文是否被更新
        context = self.context_manager.get_context(session_id)
        assert len(context) == 4  # 原有2条 + 新的用户消息 + 助手回复
        assert context[-2]["content"] == "请解释一下二次函数"
        assert context[-1]["content"] == response
    
    def test_generate_response_new_session(self):
        """测试新会话的响应生成"""
        self.mock_llm_client.generate_response.return_value = "你好！我是AI助手。"
        
        session_id = "new_session_001"
        
        response = self.wrapper.generate_response(
            session_id=session_id,
            user_message="你好",
            user_id="user_1111"
        )
        
        assert response == "你好！我是AI助手。"
        
        # 检查会话是否被创建
        session = self.context_manager.get_session(session_id)
        assert session is not None
        assert session["user_id"] == "user_1111"
        
        # 检查上下文是否被添加
        context = self.context_manager.get_context(session_id)
        assert len(context) == 2
        assert context[0]["content"] == "你好"
        assert context[1]["content"] == "你好！我是AI助手。"
    
    def test_generate_response_with_context_limit(self):
        """测试上下文长度限制"""
        self.mock_llm_client.generate_response.return_value = "回复消息"
        
        # 创建一个限制上下文的包装器
        limited_wrapper = ContextAwareLLMWrapper(
            llm_client=self.mock_llm_client,
            context_manager=self.context_manager,
            max_context_messages=3  # 只保留3条消息
        )
        
        session_id = "test_session_014"
        self.context_manager.create_session(session_id, "user_1212")
        
        # 添加多条历史消息
        for i in range(10):
            self.context_manager.add_context(
                session_id=session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"消息 {i}"
            )
        
        # 生成响应
        response = limited_wrapper.generate_response(
            session_id=session_id,
            user_message="新消息"
        )
        
        # 验证LLM调用时只使用了限制数量的上下文
        call_args = self.mock_llm_client.generate_response.call_args
        messages = call_args[1]["messages"] if "messages" in call_args[1] else call_args[0][0]
        
        # 应该包含：系统消息(可选) + 最近3条历史消息 + 新用户消息
        assert len(messages) <= 5  # 最多5条消息
    
    def test_generate_response_with_metadata(self):
        """测试带元数据的响应生成"""
        self.mock_llm_client.generate_response.return_value = "基于您的数学学习需求，我来解释..."
        
        session_id = "test_session_015"
        
        response = self.wrapper.generate_response(
            session_id=session_id,
            user_message="请解释函数概念",
            user_id="user_1313",
            metadata={
                "subject": "数学",
                "grade": "高一",
                "difficulty": "基础"
            }
        )
        
        # 检查会话元数据
        session = self.context_manager.get_session(session_id)
        assert session["metadata"]["subject"] == "数学"
        assert session["metadata"]["grade"] == "高一"
        assert session["metadata"]["difficulty"] == "基础"
    
    def test_generate_response_error_handling(self):
        """测试响应生成错误处理"""
        self.mock_llm_client.generate_response.side_effect = Exception("LLM服务错误")
        
        session_id = "test_session_016"
        
        with pytest.raises(Exception) as exc_info:
            self.wrapper.generate_response(
                session_id=session_id,
                user_message="测试消息",
                user_id="user_1414"
            )
        
        assert "LLM服务错误" in str(exc_info.value)
        
        # 即使出错，用户消息也应该被记录
        context = self.context_manager.get_context(session_id)
        assert len(context) >= 1
        assert context[-1]["content"] == "测试消息"
    
    def test_get_context_summary(self):
        """测试获取上下文摘要"""
        self.mock_llm_client.generate_response.return_value = MOCK_LLM_RESPONSES["conversation_summary"]
        
        session_id = "test_session_017"
        self.context_manager.create_session(session_id, "user_1515")
        
        # 添加对话历史
        messages = [
            "请帮我学习数学",
            "好的，我来帮助您学习数学",
            "什么是函数？",
            "函数是一种数学关系..."
        ]
        
        for i, msg in enumerate(messages):
            self.context_manager.add_context(
                session_id=session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=msg
            )
        
        # 获取摘要
        summary = self.wrapper.get_context_summary(session_id)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "数学" in summary
    
    def test_clear_session_context(self):
        """测试清除会话上下文"""
        session_id = "test_session_018"
        self.context_manager.create_session(session_id, "user_1616")
        
        # 添加上下文
        self.context_manager.add_context(session_id, "user", "测试消息")
        assert len(self.context_manager.get_context(session_id)) == 1
        
        # 清除上下文
        self.wrapper.clear_session_context(session_id)
        assert len(self.context_manager.get_context(session_id)) == 0


if __name__ == "__main__":
    pytest.main([__file__])