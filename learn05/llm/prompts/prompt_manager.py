# -*- coding: utf-8 -*-
"""
提示词管理器
统一管理和调度各类提示词模板
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import json
import os
from datetime import datetime

from .base_prompts import BasePromptTemplate, PromptTemplate, PromptType, PromptBuilder
from .teaching_prompts import TeachingPrompts
from .learning_prompts import LearningPrompts
from .tutoring_prompts import TutoringPrompts
from .classroom_prompts import ClassroomPrompts

@dataclass
class PromptUsageStats:
    """提示词使用统计"""
    template_name: str
    usage_count: int
    last_used: datetime
    average_response_time: float
    success_rate: float
    user_ratings: List[int]

class PromptManager:
    """提示词管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.prompt_providers: Dict[str, BasePromptTemplate] = {}
        self.usage_stats: Dict[str, PromptUsageStats] = {}
        self.custom_templates: Dict[str, PromptTemplate] = {}
        
        # 初始化各类提示词提供者
        self._initialize_providers()
        
        # 加载使用统计
        self._load_usage_stats()
    
    def _initialize_providers(self):
        """初始化提示词提供者"""
        self.prompt_providers = {
            'teaching': TeachingPrompts(),
            'learning': LearningPrompts(),
            'tutoring': TutoringPrompts(),
            'classroom': ClassroomPrompts()
        }
    
    def get_template(self, category: str, template_name: str) -> Optional[PromptTemplate]:
        """获取指定分类和名称的模板"""
        # 首先检查自定义模板
        full_name = f"{category}.{template_name}"
        if full_name in self.custom_templates:
            return self.custom_templates[full_name]
        
        # 然后检查标准模板
        if category in self.prompt_providers:
            return self.prompt_providers[category].get_template(template_name)
        
        return None
    
    def format_prompt(self, category: str, template_name: str, **kwargs) -> str:
        """格式化提示词"""
        template = self.get_template(category, template_name)
        if not template:
            raise ValueError(f"Template '{category}.{template_name}' not found")
        
        try:
            formatted_prompt = template.template.format(**kwargs)
            
            # 记录使用统计
            self._record_usage(f"{category}.{template_name}")
            
            return formatted_prompt
        except KeyError as e:
            raise ValueError(f"Missing required variable: {e}")
    
    def build_conversation(self, category: str, template_name: str, **kwargs) -> List[Dict[str, str]]:
        """构建对话格式的提示词"""
        formatted_prompt = self.format_prompt(category, template_name, **kwargs)
        
        builder = PromptBuilder()
        builder.add_user_message(formatted_prompt)
        
        return builder.build()
    
    def list_templates(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """列出所有模板"""
        if category:
            if category in self.prompt_providers:
                return {category: self.prompt_providers[category].list_templates()}
            else:
                return {}
        
        result = {}
        for cat, provider in self.prompt_providers.items():
            result[cat] = provider.list_templates()
        
        # 添加自定义模板
        custom_by_category = {}
        for full_name in self.custom_templates.keys():
            cat, name = full_name.split('.', 1)
            if cat not in custom_by_category:
                custom_by_category[cat] = []
            custom_by_category[cat].append(name)
        
        for cat, templates in custom_by_category.items():
            if cat in result:
                result[cat].extend(templates)
            else:
                result[cat] = templates
        
        return result
    
    def search_templates(self, keyword: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索模板"""
        results = []
        
        providers_to_search = [category] if category else self.prompt_providers.keys()
        
        for cat in providers_to_search:
            if cat in self.prompt_providers:
                templates = self.prompt_providers[cat].search_templates(keyword)
                for template in templates:
                    results.append({
                        'category': cat,
                        'template': template,
                        'full_name': f"{cat}.{template.name}"
                    })
        
        # 搜索自定义模板
        keyword_lower = keyword.lower()
        for full_name, template in self.custom_templates.items():
            cat, name = full_name.split('.', 1)
            if (not category or cat == category) and (
                keyword_lower in template.name.lower() or
                keyword_lower in template.description.lower() or
                any(keyword_lower in tag.lower() for tag in template.tags)
            ):
                results.append({
                    'category': cat,
                    'template': template,
                    'full_name': full_name
                })
        
        return results
    
    def add_custom_template(self, category: str, template: PromptTemplate):
        """添加自定义模板"""
        full_name = f"{category}.{template.name}"
        
        # 验证模板
        if category in self.prompt_providers:
            provider = self.prompt_providers[category]
            if not provider.validate_template(template):
                raise ValueError(f"Invalid template: {template.name}")
        
        self.custom_templates[full_name] = template
        
        # 保存到文件
        self._save_custom_templates()
    
    def remove_custom_template(self, category: str, template_name: str):
        """删除自定义模板"""
        full_name = f"{category}.{template_name}"
        if full_name in self.custom_templates:
            del self.custom_templates[full_name]
            self._save_custom_templates()
        else:
            raise ValueError(f"Custom template '{full_name}' not found")
    
    def get_template_info(self, category: str, template_name: str) -> Dict[str, Any]:
        """获取模板详细信息"""
        template = self.get_template(category, template_name)
        if not template:
            return {}
        
        full_name = f"{category}.{template_name}"
        info = {
            'name': template.name,
            'description': template.description,
            'variables': template.variables,
            'prompt_type': template.prompt_type.value,
            'category': template.category,
            'version': template.version,
            'tags': template.tags,
            'examples_count': len(template.examples),
            'is_custom': full_name in self.custom_templates
        }
        
        # 添加使用统计
        if full_name in self.usage_stats:
            stats = self.usage_stats[full_name]
            info.update({
                'usage_count': stats.usage_count,
                'last_used': stats.last_used.isoformat(),
                'average_response_time': stats.average_response_time,
                'success_rate': stats.success_rate,
                'average_rating': sum(stats.user_ratings) / len(stats.user_ratings) if stats.user_ratings else 0
            })
        
        return info
    
    def get_popular_templates(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门模板"""
        # 按使用次数排序
        sorted_stats = sorted(
            self.usage_stats.items(),
            key=lambda x: x[1].usage_count,
            reverse=True
        )
        
        results = []
        for full_name, stats in sorted_stats[:limit]:
            cat, name = full_name.split('.', 1)
            if category and cat != category:
                continue
            
            template = self.get_template(cat, name)
            if template:
                results.append({
                    'category': cat,
                    'name': name,
                    'usage_count': stats.usage_count,
                    'success_rate': stats.success_rate,
                    'average_rating': sum(stats.user_ratings) / len(stats.user_ratings) if stats.user_ratings else 0,
                    'description': template.description
                })
        
        return results
    
    def validate_template_variables(self, category: str, template_name: str, **kwargs) -> Dict[str, Any]:
        """验证模板变量"""
        template = self.get_template(category, template_name)
        if not template:
            return {'valid': False, 'error': 'Template not found'}
        
        missing_vars = [var for var in template.variables if var not in kwargs]
        extra_vars = [var for var in kwargs.keys() if var not in template.variables]
        
        return {
            'valid': len(missing_vars) == 0,
            'missing_variables': missing_vars,
            'extra_variables': extra_vars,
            'required_variables': template.variables
        }
    
    def get_template_suggestions(self, category: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据上下文推荐合适的模板"""
        if category not in self.prompt_providers:
            return []
        
        provider = self.prompt_providers[category]
        all_templates = [provider.get_template(name) for name in provider.list_templates()]
        
        suggestions = []
        for template in all_templates:
            if not template:
                continue
            
            # 简单的匹配逻辑，可以根据需要扩展
            score = 0
            
            # 基于标签匹配
            for tag in template.tags:
                if any(tag.lower() in str(v).lower() for v in context.values()):
                    score += 1
            
            # 基于描述匹配
            for value in context.values():
                if str(value).lower() in template.description.lower():
                    score += 1
            
            if score > 0:
                suggestions.append({
                    'template': template,
                    'score': score,
                    'category': category
                })
        
        # 按分数排序
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        return suggestions[:5]  # 返回前5个建议
    
    def export_templates(self, file_path: str, category: Optional[str] = None):
        """导出模板到文件"""
        export_data = {
            'export_time': datetime.now().isoformat(),
            'categories': {}
        }
        
        categories_to_export = [category] if category else self.prompt_providers.keys()
        
        for cat in categories_to_export:
            if cat in self.prompt_providers:
                provider = self.prompt_providers[cat]
                export_data['categories'][cat] = {}
                
                for template_name in provider.list_templates():
                    template = provider.get_template(template_name)
                    if template:
                        export_data['categories'][cat][template_name] = {
                            'name': template.name,
                            'description': template.description,
                            'template': template.template,
                            'variables': template.variables,
                            'prompt_type': template.prompt_type.value,
                            'category': template.category,
                            'version': template.version,
                            'tags': template.tags,
                            'examples': template.examples
                        }
        
        # 添加自定义模板
        for full_name, template in self.custom_templates.items():
            cat, name = full_name.split('.', 1)
            if not category or cat == category:
                if cat not in export_data['categories']:
                    export_data['categories'][cat] = {}
                
                export_data['categories'][cat][name] = {
                    'name': template.name,
                    'description': template.description,
                    'template': template.template,
                    'variables': template.variables,
                    'prompt_type': template.prompt_type.value,
                    'category': template.category,
                    'version': template.version,
                    'tags': template.tags,
                    'examples': template.examples,
                    'is_custom': True
                }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def _record_usage(self, full_name: str, response_time: float = 0, success: bool = True):
        """记录使用统计"""
        if full_name not in self.usage_stats:
            self.usage_stats[full_name] = PromptUsageStats(
                template_name=full_name,
                usage_count=0,
                last_used=datetime.now(),
                average_response_time=0,
                success_rate=1.0,
                user_ratings=[]
            )
        
        stats = self.usage_stats[full_name]
        stats.usage_count += 1
        stats.last_used = datetime.now()
        
        if response_time > 0:
            # 更新平均响应时间
            total_time = stats.average_response_time * (stats.usage_count - 1) + response_time
            stats.average_response_time = total_time / stats.usage_count
        
        # 更新成功率
        if stats.usage_count == 1:
            stats.success_rate = 1.0 if success else 0.0
        else:
            # 简化的成功率计算
            stats.success_rate = (stats.success_rate * 0.9) + (0.1 if success else 0)
    
    def add_user_rating(self, category: str, template_name: str, rating: int):
        """添加用户评分"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        full_name = f"{category}.{template_name}"
        if full_name not in self.usage_stats:
            self._record_usage(full_name)
        
        self.usage_stats[full_name].user_ratings.append(rating)
        
        # 保持最近100个评分
        if len(self.usage_stats[full_name].user_ratings) > 100:
            self.usage_stats[full_name].user_ratings = self.usage_stats[full_name].user_ratings[-100:]
    
    def _load_usage_stats(self):
        """加载使用统计"""
        stats_file = self.config.get('stats_file', 'prompt_usage_stats.json')
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for full_name, stats_data in data.items():
                    self.usage_stats[full_name] = PromptUsageStats(
                        template_name=full_name,
                        usage_count=stats_data['usage_count'],
                        last_used=datetime.fromisoformat(stats_data['last_used']),
                        average_response_time=stats_data['average_response_time'],
                        success_rate=stats_data['success_rate'],
                        user_ratings=stats_data['user_ratings']
                    )
            except Exception as e:
                print(f"Error loading usage stats: {e}")
    
    def _save_usage_stats(self):
        """保存使用统计"""
        stats_file = self.config.get('stats_file', 'prompt_usage_stats.json')
        data = {}
        
        for full_name, stats in self.usage_stats.items():
            data[full_name] = {
                'usage_count': stats.usage_count,
                'last_used': stats.last_used.isoformat(),
                'average_response_time': stats.average_response_time,
                'success_rate': stats.success_rate,
                'user_ratings': stats.user_ratings
            }
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving usage stats: {e}")
    
    def _save_custom_templates(self):
        """保存自定义模板"""
        custom_file = self.config.get('custom_templates_file', 'custom_templates.json')
        data = {}
        
        for full_name, template in self.custom_templates.items():
            data[full_name] = {
                'name': template.name,
                'description': template.description,
                'template': template.template,
                'variables': template.variables,
                'prompt_type': template.prompt_type.value,
                'category': template.category,
                'version': template.version,
                'tags': template.tags,
                'examples': template.examples
            }
        
        try:
            with open(custom_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving custom templates: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取整体统计信息"""
        total_templates = sum(len(provider.list_templates()) for provider in self.prompt_providers.values())
        total_custom = len(self.custom_templates)
        total_usage = sum(stats.usage_count for stats in self.usage_stats.values())
        
        category_stats = {}
        for category, provider in self.prompt_providers.items():
            templates = provider.list_templates()
            category_usage = sum(
                stats.usage_count for full_name, stats in self.usage_stats.items()
                if full_name.startswith(f"{category}.")
            )
            
            category_stats[category] = {
                'template_count': len(templates),
                'usage_count': category_usage
            }
        
        return {
            'total_templates': total_templates,
            'custom_templates': total_custom,
            'total_usage': total_usage,
            'category_statistics': category_stats,
            'most_used_template': max(self.usage_stats.items(), key=lambda x: x[1].usage_count)[0] if self.usage_stats else None
        }