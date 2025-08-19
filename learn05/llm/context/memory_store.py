# -*- coding: utf-8 -*-
"""
内存存储模块
用于管理不同类型的记忆数据
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
from collections import defaultdict

class MemoryType(Enum):
    """记忆类型"""
    SHORT_TERM = "short_term"  # 短期记忆
    LONG_TERM = "long_term"  # 长期记忆
    WORKING = "working"  # 工作记忆
    EPISODIC = "episodic"  # 情节记忆
    SEMANTIC = "semantic"  # 语义记忆
    PROCEDURAL = "procedural"  # 程序记忆

class MemoryImportance(Enum):
    """记忆重要性"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MemoryItem:
    """记忆项"""
    memory_id: str
    content: str
    memory_type: MemoryType
    importance: MemoryImportance
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    decay_rate: float = 0.1  # 遗忘率
    strength: float = 1.0  # 记忆强度
    
    def access(self):
        """访问记忆，更新访问时间和次数"""
        self.last_accessed = datetime.now()
        self.access_count += 1
        # 增强记忆强度
        self.strength = min(1.0, self.strength + 0.1)
    
    def decay(self, time_passed: timedelta):
        """记忆衰减"""
        hours_passed = time_passed.total_seconds() / 3600
        decay_factor = self.decay_rate * hours_passed / 24  # 每天衰减
        self.strength = max(0.0, self.strength - decay_factor)
    
    def get_relevance_score(self, query: str) -> float:
        """计算与查询的相关性分数"""
        query_lower = query.lower()
        content_lower = self.content.lower()
        
        # 简单的相关性计算
        score = 0.0
        
        # 内容匹配
        if query_lower in content_lower:
            score += 0.5
        
        # 标签匹配
        for tag in self.tags:
            if query_lower in tag.lower():
                score += 0.3
        
        # 元数据匹配
        for value in self.metadata.values():
            if isinstance(value, str) and query_lower in value.lower():
                score += 0.2
        
        # 考虑记忆强度和重要性
        score *= self.strength
        score *= (self.importance.value / 4.0)
        
        return min(1.0, score)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'memory_id': self.memory_id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'importance': self.importance.value,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count,
            'metadata': self.metadata,
            'tags': self.tags,
            'related_memories': self.related_memories,
            'decay_rate': self.decay_rate,
            'strength': self.strength
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """从字典创建"""
        return cls(
            memory_id=data['memory_id'],
            content=data['content'],
            memory_type=MemoryType(data['memory_type']),
            importance=MemoryImportance(data['importance']),
            created_at=datetime.fromisoformat(data['created_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            access_count=data.get('access_count', 0),
            metadata=data.get('metadata', {}),
            tags=data.get('tags', []),
            related_memories=data.get('related_memories', []),
            decay_rate=data.get('decay_rate', 0.1),
            strength=data.get('strength', 1.0)
        )

class MemoryStore:
    """内存存储"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.memories: Dict[str, MemoryItem] = {}
        self.type_index: Dict[MemoryType, List[str]] = defaultdict(list)
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        self.user_memories: Dict[str, List[str]] = defaultdict(list)
        
        # 配置参数
        self.max_memories = self.config.get('max_memories', 10000)
        self.auto_decay = self.config.get('auto_decay', True)
        self.decay_interval = timedelta(hours=self.config.get('decay_interval_hours', 24))
        self.min_strength_threshold = self.config.get('min_strength_threshold', 0.1)
        
        # 统计信息
        self.last_decay_time = datetime.now()
        self.total_memories_created = 0
        self.total_memories_decayed = 0
    
    def add_memory(self, 
                  content: str,
                  memory_type: MemoryType,
                  importance: MemoryImportance,
                  user_id: Optional[str] = None,
                  metadata: Dict[str, Any] = None,
                  tags: List[str] = None) -> str:
        """添加记忆"""
        memory_id = str(uuid.uuid4())
        
        memory = MemoryItem(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {},
            tags=tags or []
        )
        
        self.memories[memory_id] = memory
        
        # 更新索引
        self.type_index[memory_type].append(memory_id)
        
        for tag in memory.tags:
            self.tag_index[tag].append(memory_id)
        
        if user_id:
            self.user_memories[user_id].append(memory_id)
        
        self.total_memories_created += 1
        
        # 检查内存限制
        if len(self.memories) > self.max_memories:
            self._cleanup_old_memories()
        
        # 自动衰减
        if self.auto_decay:
            self._auto_decay()
        
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """获取记忆"""
        memory = self.memories.get(memory_id)
        if memory:
            memory.access()
        return memory
    
    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """更新记忆"""
        memory = self.memories.get(memory_id)
        if not memory:
            return False
        
        # 更新索引（如果标签改变）
        old_tags = memory.tags.copy()
        
        for key, value in kwargs.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        # 重新索引标签
        if 'tags' in kwargs:
            # 移除旧标签索引
            for tag in old_tags:
                if memory_id in self.tag_index[tag]:
                    self.tag_index[tag].remove(memory_id)
            
            # 添加新标签索引
            for tag in memory.tags:
                if memory_id not in self.tag_index[tag]:
                    self.tag_index[tag].append(memory_id)
        
        memory.access()
        return True
    
    def remove_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        memory = self.memories.get(memory_id)
        if not memory:
            return False
        
        # 从索引中移除
        if memory_id in self.type_index[memory.memory_type]:
            self.type_index[memory.memory_type].remove(memory_id)
        
        for tag in memory.tags:
            if memory_id in self.tag_index[tag]:
                self.tag_index[tag].remove(memory_id)
        
        # 从用户记忆中移除
        for user_id, memory_ids in self.user_memories.items():
            if memory_id in memory_ids:
                memory_ids.remove(memory_id)
        
        # 删除记忆
        del self.memories[memory_id]
        return True
    
    def search_memories(self, 
                       query: str,
                       memory_type: Optional[MemoryType] = None,
                       user_id: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       min_importance: Optional[MemoryImportance] = None,
                       limit: int = 10) -> List[Tuple[MemoryItem, float]]:
        """搜索记忆"""
        candidates = []
        
        # 确定搜索范围
        if user_id:
            search_ids = self.user_memories.get(user_id, [])
        elif memory_type:
            search_ids = self.type_index.get(memory_type, [])
        else:
            search_ids = list(self.memories.keys())
        
        # 过滤和评分
        for memory_id in search_ids:
            memory = self.memories.get(memory_id)
            if not memory:
                continue
            
            # 类型过滤
            if memory_type and memory.memory_type != memory_type:
                continue
            
            # 重要性过滤
            if min_importance and memory.importance.value < min_importance.value:
                continue
            
            # 标签过滤
            if tags and not any(tag in memory.tags for tag in tags):
                continue
            
            # 计算相关性分数
            relevance_score = memory.get_relevance_score(query)
            
            if relevance_score > 0:
                candidates.append((memory, relevance_score))
        
        # 按相关性排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 访问找到的记忆
        for memory, _ in candidates[:limit]:
            memory.access()
        
        return candidates[:limit]
    
    def get_memories_by_type(self, memory_type: MemoryType) -> List[MemoryItem]:
        """按类型获取记忆"""
        memory_ids = self.type_index.get(memory_type, [])
        return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def get_memories_by_tags(self, tags: List[str]) -> List[MemoryItem]:
        """按标签获取记忆"""
        memory_ids = set()
        for tag in tags:
            memory_ids.update(self.tag_index.get(tag, []))
        
        return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def get_user_memories(self, user_id: str) -> List[MemoryItem]:
        """获取用户记忆"""
        memory_ids = self.user_memories.get(user_id, [])
        return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def add_memory_relation(self, memory_id1: str, memory_id2: str) -> bool:
        """添加记忆关联"""
        memory1 = self.memories.get(memory_id1)
        memory2 = self.memories.get(memory_id2)
        
        if not memory1 or not memory2:
            return False
        
        if memory_id2 not in memory1.related_memories:
            memory1.related_memories.append(memory_id2)
        
        if memory_id1 not in memory2.related_memories:
            memory2.related_memories.append(memory_id1)
        
        return True
    
    def get_related_memories(self, memory_id: str, depth: int = 1) -> List[MemoryItem]:
        """获取相关记忆"""
        if depth <= 0:
            return []
        
        memory = self.memories.get(memory_id)
        if not memory:
            return []
        
        related = []
        visited = {memory_id}
        
        def _get_related_recursive(mid: str, current_depth: int):
            if current_depth <= 0:
                return
            
            current_memory = self.memories.get(mid)
            if not current_memory:
                return
            
            for related_id in current_memory.related_memories:
                if related_id not in visited and related_id in self.memories:
                    visited.add(related_id)
                    related.append(self.memories[related_id])
                    _get_related_recursive(related_id, current_depth - 1)
        
        _get_related_recursive(memory_id, depth)
        return related
    
    def consolidate_memories(self, user_id: Optional[str] = None) -> int:
        """记忆整合"""
        memories_to_process = []
        
        if user_id:
            memory_ids = self.user_memories.get(user_id, [])
            memories_to_process = [self.memories[mid] for mid in memory_ids if mid in self.memories]
        else:
            memories_to_process = list(self.memories.values())
        
        consolidated_count = 0
        
        # 简单的记忆整合：合并相似内容
        for i, memory1 in enumerate(memories_to_process):
            for j, memory2 in enumerate(memories_to_process[i+1:], i+1):
                if self._are_memories_similar(memory1, memory2):
                    # 合并记忆
                    if self._merge_memories(memory1, memory2):
                        consolidated_count += 1
        
        return consolidated_count
    
    def decay_memories(self) -> int:
        """记忆衰减"""
        current_time = datetime.now()
        decayed_count = 0
        memories_to_remove = []
        
        for memory in self.memories.values():
            time_passed = current_time - memory.last_accessed
            memory.decay(time_passed)
            
            # 移除强度过低的记忆
            if memory.strength < self.min_strength_threshold:
                memories_to_remove.append(memory.memory_id)
                decayed_count += 1
        
        # 删除衰减的记忆
        for memory_id in memories_to_remove:
            self.remove_memory(memory_id)
        
        self.total_memories_decayed += decayed_count
        self.last_decay_time = current_time
        
        return decayed_count
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        total_memories = len(self.memories)
        
        # 按类型统计
        type_counts = {}
        for memory_type in MemoryType:
            type_counts[memory_type.value] = len(self.type_index.get(memory_type, []))
        
        # 按重要性统计
        importance_counts = {}
        for importance in MemoryImportance:
            count = sum(1 for m in self.memories.values() if m.importance == importance)
            importance_counts[importance.value] = count
        
        # 计算平均强度
        avg_strength = sum(m.strength for m in self.memories.values()) / total_memories if total_memories > 0 else 0
        
        return {
            'total_memories': total_memories,
            'type_distribution': type_counts,
            'importance_distribution': importance_counts,
            'average_strength': avg_strength,
            'total_users': len(self.user_memories),
            'total_tags': len(self.tag_index),
            'total_created': self.total_memories_created,
            'total_decayed': self.total_memories_decayed
        }
    
    def _cleanup_old_memories(self):
        """清理旧记忆"""
        # 按强度和最后访问时间排序
        memories_with_score = []
        for memory in self.memories.values():
            # 计算清理分数（强度 + 重要性 - 时间衰减）
            time_factor = (datetime.now() - memory.last_accessed).days
            score = memory.strength + (memory.importance.value / 4.0) - (time_factor * 0.1)
            memories_with_score.append((memory.memory_id, score))
        
        # 排序并删除分数最低的记忆
        memories_with_score.sort(key=lambda x: x[1])
        
        # 删除10%的记忆
        to_remove = int(len(memories_with_score) * 0.1)
        for memory_id, _ in memories_with_score[:to_remove]:
            self.remove_memory(memory_id)
    
    def _auto_decay(self):
        """自动衰减"""
        if datetime.now() - self.last_decay_time > self.decay_interval:
            self.decay_memories()
    
    def _are_memories_similar(self, memory1: MemoryItem, memory2: MemoryItem) -> bool:
        """判断两个记忆是否相似"""
        # 简单的相似性判断
        content1 = memory1.content.lower()
        content2 = memory2.content.lower()
        
        # 内容相似度
        common_words = set(content1.split()) & set(content2.split())
        similarity = len(common_words) / max(len(content1.split()), len(content2.split()))
        
        # 标签相似度
        common_tags = set(memory1.tags) & set(memory2.tags)
        tag_similarity = len(common_tags) / max(len(memory1.tags), len(memory2.tags)) if memory1.tags or memory2.tags else 0
        
        return similarity > 0.7 or tag_similarity > 0.5
    
    def _merge_memories(self, memory1: MemoryItem, memory2: MemoryItem) -> bool:
        """合并记忆"""
        try:
            # 合并内容
            merged_content = f"{memory1.content}\n{memory2.content}"
            
            # 合并标签
            merged_tags = list(set(memory1.tags + memory2.tags))
            
            # 合并元数据
            merged_metadata = {**memory1.metadata, **memory2.metadata}
            
            # 更新第一个记忆
            memory1.content = merged_content
            memory1.tags = merged_tags
            memory1.metadata = merged_metadata
            memory1.strength = max(memory1.strength, memory2.strength)
            memory1.importance = max(memory1.importance, memory2.importance)
            memory1.access_count += memory2.access_count
            
            # 删除第二个记忆
            self.remove_memory(memory2.memory_id)
            
            return True
        except Exception:
            return False
    
    def export_memories(self, file_path: str, user_id: Optional[str] = None):
        """导出记忆数据"""
        data = {
            'export_time': datetime.now().isoformat(),
            'memories': {},
            'statistics': self.get_memory_statistics()
        }
        
        memories_to_export = []
        if user_id:
            memory_ids = self.user_memories.get(user_id, [])
            memories_to_export = [self.memories[mid] for mid in memory_ids if mid in self.memories]
        else:
            memories_to_export = list(self.memories.values())
        
        for memory in memories_to_export:
            data['memories'][memory.memory_id] = memory.to_dict()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def import_memories(self, file_path: str) -> int:
        """导入记忆数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for memory_id, memory_data in data.get('memories', {}).items():
                try:
                    memory = MemoryItem.from_dict(memory_data)
                    self.memories[memory_id] = memory
                    
                    # 重建索引
                    self.type_index[memory.memory_type].append(memory_id)
                    for tag in memory.tags:
                        self.tag_index[tag].append(memory_id)
                    
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing memory {memory_id}: {e}")
            
            return imported_count
        except Exception as e:
            print(f"Error importing memories: {e}")
            return 0