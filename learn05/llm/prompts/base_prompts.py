# -*- coding: utf-8 -*-
"""
基础提示词模板类
定义提示词的基本结构和类型
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json

class PromptType(Enum):
    """提示词类型枚举"""
    SYSTEM = "system"  # 系统提示词
    USER = "user"      # 用户提示词
    ASSISTANT = "assistant"  # 助手提示词
    FUNCTION = "function"    # 功能提示词

@dataclass
class PromptTemplate:
    """提示词模板数据类"""
    name: str
    description: str
    template: str
    variables: List[str]
    prompt_type: PromptType
    category: str
    version: str = "1.0.0"
    tags: List[str] = None
    examples: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.examples is None:
            self.examples = []

class BasePromptTemplate(ABC):
    """基础提示词模板抽象类"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_templates()
    
    @abstractmethod
    def _load_templates(self):
        """加载提示词模板"""
        pass
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取指定名称的模板"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """列出所有模板名称"""
        return list(self.templates.keys())
    
    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """根据分类获取模板"""
        return [template for template in self.templates.values() 
                if template.category == category]
    
    def get_templates_by_tag(self, tag: str) -> List[PromptTemplate]:
        """根据标签获取模板"""
        return [template for template in self.templates.values() 
                if tag in template.tags]
    
    def format_template(self, name: str, **kwargs) -> str:
        """格式化模板"""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        
        # 检查必需的变量
        missing_vars = [var for var in template.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        try:
            return template.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Template formatting error: {e}")
    
    def validate_template(self, template: PromptTemplate) -> bool:
        """验证模板格式"""
        try:
            # 检查模板中的变量是否与声明的变量一致
            import re
            template_vars = re.findall(r'\{([^}]+)\}', template.template)
            declared_vars = set(template.variables)
            found_vars = set(template_vars)
            
            if found_vars != declared_vars:
                print(f"Warning: Template variables mismatch in '{template.name}'")
                print(f"Declared: {declared_vars}")
                print(f"Found: {found_vars}")
                return False
            
            return True
        except Exception as e:
            print(f"Template validation error: {e}")
            return False
    
    def add_template(self, template: PromptTemplate):
        """添加新模板"""
        if self.validate_template(template):
            self.templates[template.name] = template
        else:
            raise ValueError(f"Invalid template: {template.name}")
    
    def remove_template(self, name: str):
        """删除模板"""
        if name in self.templates:
            del self.templates[name]
        else:
            raise ValueError(f"Template '{name}' not found")
    
    def export_templates(self, file_path: str):
        """导出模板到文件"""
        templates_data = {}
        for name, template in self.templates.items():
            templates_data[name] = {
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
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(templates_data, f, ensure_ascii=False, indent=2)
    
    def import_templates(self, file_path: str):
        """从文件导入模板"""
        with open(file_path, 'r', encoding='utf-8') as f:
            templates_data = json.load(f)
        
        for name, data in templates_data.items():
            template = PromptTemplate(
                name=data['name'],
                description=data['description'],
                template=data['template'],
                variables=data['variables'],
                prompt_type=PromptType(data['prompt_type']),
                category=data['category'],
                version=data.get('version', '1.0.0'),
                tags=data.get('tags', []),
                examples=data.get('examples', [])
            )
            self.add_template(template)
    
    def get_template_info(self, name: str) -> Dict[str, Any]:
        """获取模板详细信息"""
        template = self.get_template(name)
        if not template:
            return {}
        
        return {
            'name': template.name,
            'description': template.description,
            'variables': template.variables,
            'prompt_type': template.prompt_type.value,
            'category': template.category,
            'version': template.version,
            'tags': template.tags,
            'examples_count': len(template.examples)
        }
    
    def search_templates(self, keyword: str) -> List[PromptTemplate]:
        """搜索模板"""
        keyword = keyword.lower()
        results = []
        
        for template in self.templates.values():
            if (keyword in template.name.lower() or 
                keyword in template.description.lower() or
                keyword in template.category.lower() or
                any(keyword in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results

class PromptBuilder:
    """提示词构建器"""
    
    def __init__(self):
        self.messages = []
    
    def add_system_message(self, content: str):
        """添加系统消息"""
        self.messages.append({
            "role": "system",
            "content": content
        })
        return self
    
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append({
            "role": "user",
            "content": content
        })
        return self
    
    def add_assistant_message(self, content: str):
        """添加助手消息"""
        self.messages.append({
            "role": "assistant",
            "content": content
        })
        return self
    
    def build(self) -> List[Dict[str, str]]:
        """构建消息列表"""
        return self.messages.copy()
    
    def clear(self):
        """清空消息"""
        self.messages.clear()
        return self
    
    def to_string(self, separator: str = "\n\n") -> str:
        """转换为字符串格式"""
        parts = []
        for msg in self.messages:
            role = msg["role"].upper()
            content = msg["content"]
            parts.append(f"[{role}]: {content}")
        return separator.join(parts)

class PromptValidator:
    """提示词验证器"""
    
    @staticmethod
    def validate_variables(template: str, variables: List[str]) -> bool:
        """验证模板变量"""
        import re
        template_vars = set(re.findall(r'\{([^}]+)\}', template))
        declared_vars = set(variables)
        return template_vars == declared_vars
    
    @staticmethod
    def validate_format(template: str, **kwargs) -> bool:
        """验证模板格式"""
        try:
            template.format(**kwargs)
            return True
        except (KeyError, ValueError):
            return False
    
    @staticmethod
    def check_template_length(template: str, max_length: int = 4000) -> bool:
        """检查模板长度"""
        return len(template) <= max_length
    
    @staticmethod
    def validate_json_format(content: str) -> bool:
        """验证JSON格式"""
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False