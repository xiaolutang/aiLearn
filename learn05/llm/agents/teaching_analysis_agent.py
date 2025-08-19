# -*- coding: utf-8 -*-
"""
教材分析智能体模块
提供教材内容分析、知识点识别、重点难点分析等功能
"""

import json
import logging
from typing import Dict, List, Optional, Any
from .base_agent import BaseTeachingAgent, AgentType, AgentTask, AgentResponse

logger = logging.getLogger(__name__)


class TeachingAnalysisAgent(BaseTeachingAgent):
    """教材分析智能体"""
    
    def __init__(self, llm_client=None, config: Optional[Dict] = None):
        super().__init__(AgentType.TEACHING_ANALYSIS, llm_client, config)
        
        # 教材分析专用配置
        self.analysis_config = {
            "max_content_length": 10000,  # 最大内容长度
            "min_knowledge_points": 3,    # 最少知识点数量
            "analysis_depth": "detailed", # 分析深度: basic, detailed, comprehensive
            "include_examples": True,     # 是否包含示例
            "generate_questions": True    # 是否生成问题
        }
        
        self.analysis_config.update(config.get("analysis_config", {}) if config else {})
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证教材分析输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            bool: 验证是否通过
        """
        required_fields = ["content"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in input_data:
                logger.error(f"缺少必需字段: {field}")
                return False
        
        # 检查内容长度
        content = input_data.get("content", "")
        if len(content) > self.analysis_config["max_content_length"]:
            logger.error(f"内容长度超过限制: {len(content)} > {self.analysis_config['max_content_length']}")
            return False
        
        if len(content.strip()) < 10:
            logger.error("内容过短，无法进行有效分析")
            return False
        
        return True
    
    def get_prompt_template(self, task_type: str) -> str:
        """
        获取教材分析提示词模板
        
        Args:
            task_type: 任务类型
            
        Returns:
            str: 提示词模板
        """
        templates = {
            "content_analysis": """
你是一位资深的教育专家和教材分析师。请对以下教材内容进行深入分析：

教材信息：
- 学科：{subject}
- 年级：{grade}
- 章节：{chapter}

教材内容：
{content}

请按照以下要求进行分析：

1. **知识点识别**：
   - 识别并列出本章节的核心知识点
   - 按重要程度排序
   - 标注知识点的难度级别（基础/中等/困难）

2. **重点难点分析**：
   - 确定教学重点（学生必须掌握的核心内容）
   - 识别教学难点（学生容易混淆或理解困难的内容）
   - 分析重难点的原因

3. **知识结构梳理**：
   - 分析知识点之间的逻辑关系
   - 构建知识点的层次结构
   - 识别前置知识和后续知识的关联

4. **教学建议**：
   - 推荐适合的教学方法
   - 建议教学时间分配
   - 提供教学注意事项

5. **学习目标**：
   - 制定明确的学习目标
   - 按照认知层次（记忆、理解、应用、分析、综合、评价）分类

请以JSON格式返回分析结果，包含以下字段：
- knowledge_points: 知识点列表
- key_points: 重点内容
- difficult_points: 难点内容
- knowledge_structure: 知识结构
- teaching_suggestions: 教学建议
- learning_objectives: 学习目标
""",
            
            "knowledge_extraction": """
你是一位专业的知识工程师。请从以下教材内容中提取和整理知识点：

教材内容：
{content}

请完成以下任务：

1. **知识点提取**：
   - 识别所有重要的概念、定理、公式、方法等
   - 为每个知识点分配唯一标识符
   - 标注知识点类型（概念/定理/公式/方法/案例）

2. **知识点分类**：
   - 按主题进行分类
   - 按难度级别分类
   - 按重要程度分类

3. **关联关系**：
   - 识别知识点之间的依赖关系
   - 标注前置知识要求
   - 构建知识图谱

请以JSON格式返回结果。
""",
            
            "difficulty_analysis": """
你是一位经验丰富的教师。请分析以下教材内容的教学难点：

教材内容：
{content}
学生年级：{grade}
学科背景：{subject}

请分析：

1. **难点识别**：
   - 学生可能遇到的理解困难
   - 容易产生的错误概念
   - 抽象概念的具体化需求

2. **难点原因**：
   - 认知发展水平限制
   - 前置知识不足
   - 概念抽象程度高
   - 与日常经验差距大

3. **解决策略**：
   - 教学方法建议
   - 辅助工具推荐
   - 练习设计思路

请以JSON格式返回分析结果。
"""
        }
        
        return templates.get(task_type, templates["content_analysis"])
    
    def process_task(self, task: AgentTask) -> AgentResponse:
        """
        处理教材分析任务
        
        Args:
            task: 分析任务
            
        Returns:
            AgentResponse: 分析结果
        """
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            if task_type == "content_analysis":
                return self._analyze_content(input_data)
            elif task_type == "knowledge_extraction":
                return self._extract_knowledge_points(input_data)
            elif task_type == "difficulty_analysis":
                return self._analyze_difficulty(input_data)
            else:
                return AgentResponse(
                    success=False,
                    message=f"不支持的任务类型: {task_type}",
                    error_code="UNSUPPORTED_TASK_TYPE"
                )
                
        except Exception as e:
            logger.error(f"教材分析任务处理失败: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"任务处理失败: {str(e)}",
                error_code="PROCESSING_ERROR"
            )
    
    def _analyze_content(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        分析教材内容
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 分析结果
        """
        content = input_data["content"]
        subject = input_data.get("subject", "未指定")
        grade = input_data.get("grade", "未指定")
        chapter = input_data.get("chapter", "未指定")
        
        # 获取提示词模板
        template = self.get_prompt_template("content_analysis")
        
        # 格式化提示词
        prompt = self._format_prompt(
            template,
            content=content,
            subject=subject,
            grade=grade,
            chapter=chapter
        )
        
        # 调用大模型
        response_text = self._call_llm(prompt)
        
        # 解析响应
        try:
            # 尝试提取JSON部分
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # 如果没有代码块标记，尝试直接解析
                json_text = response_text.strip()
            
            analysis_result = json.loads(json_text)
            
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "content_analysis",
                    "input_info": {
                        "subject": subject,
                        "grade": grade,
                        "chapter": chapter,
                        "content_length": len(content)
                    },
                    "analysis_result": analysis_result
                },
                message="教材内容分析完成"
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            # 如果JSON解析失败，返回原始文本
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "content_analysis",
                    "raw_response": response_text,
                    "parse_error": str(e)
                },
                message="分析完成，但结果格式需要手动处理"
            )
    
    def _extract_knowledge_points(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        提取知识点
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 提取结果
        """
        content = input_data["content"]
        
        template = self.get_prompt_template("knowledge_extraction")
        prompt = self._format_prompt(template, content=content)
        
        response_text = self._call_llm(prompt)
        
        try:
            # 解析知识点
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()
            
            knowledge_points = json.loads(json_text)
            
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "knowledge_extraction",
                    "knowledge_points": knowledge_points,
                    "total_points": len(knowledge_points.get("points", []))
                },
                message="知识点提取完成"
            )
            
        except json.JSONDecodeError:
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "knowledge_extraction",
                    "raw_response": response_text
                },
                message="知识点提取完成，格式需要手动处理"
            )
    
    def _analyze_difficulty(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        分析教学难点
        
        Args:
            input_data: 输入数据
            
        Returns:
            AgentResponse: 分析结果
        """
        content = input_data["content"]
        grade = input_data.get("grade", "未指定")
        subject = input_data.get("subject", "未指定")
        
        template = self.get_prompt_template("difficulty_analysis")
        prompt = self._format_prompt(
            template,
            content=content,
            grade=grade,
            subject=subject
        )
        
        response_text = self._call_llm(prompt)
        
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()
            
            difficulty_analysis = json.loads(json_text)
            
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "difficulty_analysis",
                    "difficulty_analysis": difficulty_analysis
                },
                message="难点分析完成"
            )
            
        except json.JSONDecodeError:
            return AgentResponse(
                success=True,
                data={
                    "analysis_type": "difficulty_analysis",
                    "raw_response": response_text
                },
                message="难点分析完成，格式需要手动处理"
            )
    
    def analyze_textbook_chapter(self, content: str, subject: str = None, 
                                grade: str = None, chapter: str = None) -> Dict[str, Any]:
        """
        分析教材章节的便捷方法
        
        Args:
            content: 教材内容
            subject: 学科
            grade: 年级
            chapter: 章节
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        input_data = {
            "content": content,
            "subject": subject,
            "grade": grade,
            "chapter": chapter
        }
        
        response = self.execute_task("content_analysis", input_data)
        return response.data if response.success else {"error": response.message}
    
    def extract_knowledge_points(self, content: str) -> Dict[str, Any]:
        """
        提取知识点的便捷方法
        
        Args:
            content: 教材内容
            
        Returns:
            Dict[str, Any]: 知识点提取结果
        """
        input_data = {"content": content}
        response = self.execute_task("knowledge_extraction", input_data)
        return response.data if response.success else {"error": response.message}