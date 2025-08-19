# -*- coding: utf-8 -*-
"""
上下文策略模块
实现不同的上下文管理策略
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import math

from .context_manager import Message, MessageRole

@dataclass
class StrategyConfig:
    """策略配置"""
    max_tokens: int = 4000
    preserve_system: bool = True
    preserve_recent: int = 5
    importance_threshold: float = 0.5

class ContextStrategy(ABC):
    """上下文策略抽象基类"""
    
    def __init__(self, config: Optional[StrategyConfig] = None):
        self.config = config or StrategyConfig()
    
    @abstractmethod
    def apply(self, messages: List[Message]) -> List[Message]:
        """应用策略，返回优化后的消息列表"""
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """估算文本的token数量"""
        # 简单的token估算：中文字符按1.5计算，英文单词按1计算
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'\b\w+\b', text))
        return int(chinese_chars * 1.5 + english_words)
    
    def calculate_message_importance(self, message: Message, context: List[Message]) -> float:
        """计算消息重要性"""
        importance = 0.0
        
        # 基于角色的重要性
        if message.role == MessageRole.SYSTEM:
            importance += 0.8
        elif message.role == MessageRole.USER:
            importance += 0.6
        elif message.role == MessageRole.ASSISTANT:
            importance += 0.4
        
        # 基于长度的重要性
        length_score = min(1.0, len(message.content) / 500)
        importance += length_score * 0.2
        
        # 基于关键词的重要性
        keywords = ['重要', '关键', '问题', '错误', '帮助', '学习', '成绩', '分析']
        keyword_count = sum(1 for keyword in keywords if keyword in message.content)
        importance += min(0.3, keyword_count * 0.1)
        
        # 基于时间的重要性（越新越重要）
        if context:
            latest_time = max(msg.timestamp for msg in context)
            time_diff = (latest_time - message.timestamp).total_seconds()
            time_score = math.exp(-time_diff / 3600)  # 1小时衰减
            importance += time_score * 0.2
        
        return min(1.0, importance)

class SlidingWindowStrategy(ContextStrategy):
    """滑动窗口策略"""
    
    def __init__(self, window_size: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.window_size = window_size
    
    def apply(self, messages: List[Message]) -> List[Message]:
        """保持最近N条消息"""
        if len(messages) <= self.window_size:
            return messages
        
        result = []
        
        # 保留系统消息
        if self.config.preserve_system:
            system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
            result.extend(system_messages)
        
        # 获取非系统消息
        non_system_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        # 保留最近的消息
        recent_messages = non_system_messages[-self.window_size:]
        result.extend(recent_messages)
        
        return result

class TokenLimitStrategy(ContextStrategy):
    """Token限制策略"""
    
    def __init__(self, max_tokens: int = 4000, **kwargs):
        super().__init__(**kwargs)
        self.max_tokens = max_tokens
    
    def apply(self, messages: List[Message]) -> List[Message]:
        """基于token数量限制上下文"""
        if not messages:
            return messages
        
        result = []
        total_tokens = 0
        
        # 首先添加系统消息
        if self.config.preserve_system:
            system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
            for msg in system_messages:
                tokens = self.estimate_tokens(msg.content)
                if total_tokens + tokens <= self.max_tokens:
                    result.append(msg)
                    total_tokens += tokens
        
        # 从最新消息开始添加
        non_system_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        for msg in reversed(non_system_messages):
            tokens = self.estimate_tokens(msg.content)
            if total_tokens + tokens <= self.max_tokens:
                result.insert(-len([m for m in result if m.role == MessageRole.SYSTEM]), msg)
                total_tokens += tokens
            else:
                break
        
        return result

class SemanticCompressionStrategy(ContextStrategy):
    """语义压缩策略"""
    
    def __init__(self, compression_ratio: float = 0.7, **kwargs):
        super().__init__(**kwargs)
        self.compression_ratio = compression_ratio
    
    def apply(self, messages: List[Message]) -> List[Message]:
        """基于语义重要性压缩上下文"""
        if not messages:
            return messages
        
        # 计算目标消息数量
        target_count = int(len(messages) * self.compression_ratio)
        if target_count >= len(messages):
            return messages
        
        result = []
        
        # 保留系统消息
        if self.config.preserve_system:
            system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
            result.extend(system_messages)
            target_count -= len(system_messages)
        
        # 获取非系统消息并计算重要性
        non_system_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        if target_count <= 0:
            return result
        
        # 计算每条消息的重要性分数
        message_scores = []
        for msg in non_system_messages:
            importance = self.calculate_message_importance(msg, messages)
            message_scores.append((msg, importance))
        
        # 按重要性排序
        message_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 保留最重要的消息
        selected_messages = [msg for msg, _ in message_scores[:target_count]]
        
        # 按时间顺序重新排列
        selected_messages.sort(key=lambda x: x.timestamp)
        
        result.extend(selected_messages)
        
        return result

class AdaptiveStrategy(ContextStrategy):
    """自适应策略"""
    
    def __init__(self, 
                 token_limit: int = 4000,
                 window_size: int = 20,
                 importance_threshold: float = 0.5,
                 **kwargs):
        super().__init__(**kwargs)
        self.token_limit = token_limit
        self.window_size = window_size
        self.importance_threshold = importance_threshold
        
        # 子策略
        self.token_strategy = TokenLimitStrategy(token_limit)
        self.window_strategy = SlidingWindowStrategy(window_size)
        self.semantic_strategy = SemanticCompressionStrategy()
    
    def apply(self, messages: List[Message]) -> List[Message]:
        """自适应选择最佳策略"""
        if not messages:
            return messages
        
        # 计算总token数
        total_tokens = sum(self.estimate_tokens(msg.content) for msg in messages)
        
        # 根据情况选择策略
        if total_tokens <= self.token_limit:
            # Token数量在限制内，使用滑动窗口
            return self.window_strategy.apply(messages)
        elif len(messages) <= self.window_size:
            # 消息数量较少但token超限，使用token限制策略
            return self.token_strategy.apply(messages)
        else:
            # 消息数量多且token超限，使用语义压缩
            return self.semantic_strategy.apply(messages)

class HierarchicalStrategy(ContextStrategy):
    """分层策略"""
    
    def __init__(self, 
                 recent_count: int = 5,
                 important_count: int = 3,
                 summary_count: int = 2,
                 **kwargs):
        super().__init__(**kwargs)
        self.recent_count = recent_count
        self.important_count = important_count
        self.summary_count = summary_count
    
    def apply(self, messages: List[Message]) -> List[Message]:
        """分层保留不同类型的消息"""
        if not messages:
            return messages
        
        result = []
        
        # 1. 保留系统消息
        if self.config.preserve_system:
            system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
            result.extend(system_messages)
        
        non_system_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        if not non_system_messages:
            return result
        
        # 2. 保留最近的消息
        recent_messages = non_system_messages[-self.recent_count:]
        result.extend(recent_messages)
        
        # 3. 保留重要的历史消息
        historical_messages = non_system_messages[:-self.recent_count]
        if historical_messages:
            # 计算重要性并选择
            message_scores = []
            for msg in historical_messages:
                importance = self.calculate_message_importance(msg, messages)
                if importance >= self.config.importance_threshold:
                    message_scores.append((msg, importance))
            
            # 按重要性排序并选择
            message_scores.sort(key=lambda x: x[1], reverse=True)
            important_messages = [msg for msg, _ in message_scores[:self.important_count]]
            
            # 按时间顺序插入到最近消息之前
            important_messages.sort(key=lambda x: x.timestamp)
            
            # 插入到结果中（在最近消息之前）
            insert_index = len(result) - len(recent_messages)
            for msg in important_messages:
                result.insert(insert_index, msg)
                insert_index += 1
        
        return result

class ConversationAwareStrategy(ContextStrategy):
    """对话感知策略"""
    
    def __init__(self, 
                 max_turns: int = 10,
                 preserve_context_switches: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.max_turns = max_turns
        self.preserve_context_switches = preserve_context_switches
    
    def apply(self, messages: List[Message]) -> List[Message]:
        """基于对话轮次的策略"""
        if not messages:
            return messages
        
        result = []
        
        # 保留系统消息
        if self.config.preserve_system:
            system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
            result.extend(system_messages)
        
        # 识别对话轮次
        turns = self._identify_conversation_turns(messages)
        
        # 保留最近的对话轮次
        recent_turns = turns[-self.max_turns:]
        
        # 展开轮次为消息
        for turn in recent_turns:
            result.extend(turn)
        
        return result
    
    def _identify_conversation_turns(self, messages: List[Message]) -> List[List[Message]]:
        """识别对话轮次"""
        turns = []
        current_turn = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                continue
            
            if msg.role == MessageRole.USER:
                # 新的用户消息开始新轮次
                if current_turn:
                    turns.append(current_turn)
                current_turn = [msg]
            else:
                # 助手消息添加到当前轮次
                current_turn.append(msg)
        
        # 添加最后一个轮次
        if current_turn:
            turns.append(current_turn)
        
        return turns

class DynamicStrategy(ContextStrategy):
    """动态策略"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.strategies = {
            'token_limit': TokenLimitStrategy(),
            'sliding_window': SlidingWindowStrategy(),
            'semantic_compression': SemanticCompressionStrategy(),
            'adaptive': AdaptiveStrategy(),
            'hierarchical': HierarchicalStrategy()
        }
        self.strategy_usage = {name: 0 for name in self.strategies.keys()}
        self.strategy_performance = {name: [] for name in self.strategies.keys()}
    
    def apply(self, messages: List[Message]) -> List[Message]:
        """动态选择最佳策略"""
        if not messages:
            return messages
        
        # 分析消息特征
        features = self._analyze_message_features(messages)
        
        # 选择最适合的策略
        strategy_name = self._select_best_strategy(features)
        strategy = self.strategies[strategy_name]
        
        # 应用策略
        result = strategy.apply(messages)
        
        # 记录使用情况
        self.strategy_usage[strategy_name] += 1
        
        return result
    
    def _analyze_message_features(self, messages: List[Message]) -> Dict[str, Any]:
        """分析消息特征"""
        total_messages = len(messages)
        total_tokens = sum(self.estimate_tokens(msg.content) for msg in messages)
        avg_message_length = sum(len(msg.content) for msg in messages) / total_messages if total_messages > 0 else 0
        
        # 角色分布
        role_counts = {}
        for msg in messages:
            role_counts[msg.role.value] = role_counts.get(msg.role.value, 0) + 1
        
        # 时间跨度
        if messages:
            time_span = (messages[-1].timestamp - messages[0].timestamp).total_seconds() / 3600  # 小时
        else:
            time_span = 0
        
        return {
            'total_messages': total_messages,
            'total_tokens': total_tokens,
            'avg_message_length': avg_message_length,
            'role_distribution': role_counts,
            'time_span_hours': time_span
        }
    
    def _select_best_strategy(self, features: Dict[str, Any]) -> str:
        """选择最佳策略"""
        total_tokens = features['total_tokens']
        total_messages = features['total_messages']
        time_span = features['time_span_hours']
        
        # 基于规则的策略选择
        if total_tokens > 8000:
            return 'semantic_compression'
        elif total_tokens > 4000:
            return 'token_limit'
        elif total_messages > 50:
            return 'hierarchical'
        elif time_span > 24:  # 超过24小时的长对话
            return 'adaptive'
        else:
            return 'sliding_window'
    
    def get_strategy_statistics(self) -> Dict[str, Any]:
        """获取策略使用统计"""
        total_usage = sum(self.strategy_usage.values())
        
        usage_percentages = {}
        for name, count in self.strategy_usage.items():
            usage_percentages[name] = (count / total_usage * 100) if total_usage > 0 else 0
        
        return {
            'usage_counts': self.strategy_usage,
            'usage_percentages': usage_percentages,
            'total_applications': total_usage
        }

# 策略工厂
class StrategyFactory:
    """策略工厂"""
    
    @staticmethod
    def create_strategy(strategy_name: str, **kwargs) -> ContextStrategy:
        """创建策略实例"""
        strategies = {
            'sliding_window': SlidingWindowStrategy,
            'token_limit': TokenLimitStrategy,
            'semantic_compression': SemanticCompressionStrategy,
            'adaptive': AdaptiveStrategy,
            'hierarchical': HierarchicalStrategy,
            'conversation_aware': ConversationAwareStrategy,
            'dynamic': DynamicStrategy
        }
        
        if strategy_name not in strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        return strategies[strategy_name](**kwargs)
    
    @staticmethod
    def get_available_strategies() -> List[str]:
        """获取可用策略列表"""
        return [
            'sliding_window',
            'token_limit', 
            'semantic_compression',
            'adaptive',
            'hierarchical',
            'conversation_aware',
            'dynamic'
        ]
    
    @staticmethod
    def get_strategy_description(strategy_name: str) -> str:
        """获取策略描述"""
        descriptions = {
            'sliding_window': '滑动窗口策略：保持最近N轮对话',
            'token_limit': 'Token限制策略：基于Token数量限制上下文长度',
            'semantic_compression': '语义压缩策略：基于语义重要性压缩历史对话',
            'adaptive': '自适应策略：根据上下文情况自动选择最佳策略',
            'hierarchical': '分层策略：分层保留不同重要性的消息',
            'conversation_aware': '对话感知策略：基于对话轮次管理上下文',
            'dynamic': '动态策略：动态选择最适合当前情况的策略'
        }
        
        return descriptions.get(strategy_name, '未知策略')