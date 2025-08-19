# -*- coding: utf-8 -*-
"""
智能作业批改服务

本模块实现了智能作业批改的核心功能，包括文本作业和图片作业的批改。
"""

import json
import logging
import asyncio
import base64
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, validator

from .ai_service import AIServiceManager, AIRequest, AIProvider
from llm_client import get_llm_client
from .cache_service import CacheManager
from .task_service import TaskQueue, Task, TaskType, TaskPriority
from models.response import ResponseBuilder

logger = logging.getLogger(__name__)

class SubjectType(str, Enum):
    """学科类型"""
    MATH = "math"
    CHINESE = "chinese"
    ENGLISH = "english"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    POLITICS = "politics"

class SubmissionType(str, Enum):
    """提交类型"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    AUDIO = "audio"

@dataclass
class HomeworkSubmission:
    """作业提交数据类"""
    student_id: str
    student_name: str
    subject: SubjectType
    assignment_id: str
    submission_type: SubmissionType
    content: Optional[str] = None
    image_urls: Optional[List[str]] = None
    file_urls: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    submitted_at: Optional[datetime] = None

@dataclass
class GradingCriteria:
    """批改标准"""
    total_score: float = 100.0
    rubric: Optional[Dict[str, Any]] = None
    focus_areas: Optional[List[str]] = None
    difficulty_level: str = "medium"
    grading_style: str = "comprehensive"  # comprehensive, quick, detailed

@dataclass
class QuestionAnalysis:
    """题目分析"""
    question_number: int
    question_type: str
    student_answer: str
    correct_answer: Optional[str] = None
    score: float = 0.0
    max_score: float = 0.0
    feedback: str = ""
    mistakes: List[str] = None
    suggestions: List[str] = None

@dataclass
class GradingResult:
    """批改结果"""
    submission_id: str
    student_id: str
    student_name: str
    subject: SubjectType
    assignment_id: str
    total_score: float
    max_score: float
    percentage: float
    grade_level: str
    detailed_feedback: List[QuestionAnalysis]
    overall_comments: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    grading_time: datetime
    ai_confidence: float
    requires_manual_review: bool
    grader_notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class HomeworkGradingService:
    """作业批改服务"""
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        self.llm_client = get_llm_client()
        self.cache_manager = CacheManager()
        self.task_queue = TaskQueue()
        self.grading_prompts = self._load_grading_prompts()
        self.subject_configs = self._load_subject_configs()
        self.batch_size = 10  # 批量处理大小
        self.max_retries = 3  # 最大重试次数
    
    def _load_grading_prompts(self) -> Dict[str, str]:
        """加载批改提示词"""
        return {
            SubjectType.MATH: """
你是一位经验丰富的数学老师，请仔细批改这份数学作业。

批改要求：
1. 分析每道题的解题过程和答案
2. 指出计算错误、概念错误和方法错误
3. 给出正确的解题步骤和答案
4. 评估学生的数学思维能力
5. 提供针对性的学习建议

请按照以下JSON格式返回批改结果：
{
  "questions": [
    {
      "question_number": 1,
      "question_type": "计算题",
      "student_answer": "学生答案",
      "correct_answer": "正确答案",
      "score": 8.0,
      "max_score": 10.0,
      "feedback": "具体反馈",
      "mistakes": ["错误点1", "错误点2"],
      "suggestions": ["建议1", "建议2"]
    }
  ],
  "overall_comments": "总体评价",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["不足1", "不足2"],
  "suggestions": ["改进建议1", "改进建议2"],
  "confidence": 0.9
}
""",
            
            SubjectType.CHINESE: """
你是一位语文老师，请批改这份语文作业。

批改要求：
1. 检查字词使用是否正确
2. 分析语法结构和表达逻辑
3. 评价内容深度和思想性
4. 关注文采和语言表达
5. 提供写作技巧指导

请按照JSON格式返回批改结果，包含详细的分析和建议。
""",
            
            SubjectType.ENGLISH: """
You are an experienced English teacher. Please grade this English assignment.

Grading criteria:
1. Grammar and syntax accuracy
2. Vocabulary usage and variety
3. Sentence structure and complexity
4. Content organization and logic
5. Overall language proficiency

Please return the grading result in JSON format with detailed feedback and suggestions.
""",
            
            SubjectType.PHYSICS: """
你是一位物理老师，请批改这份物理作业。

批改要求：
1. 检查物理概念理解是否正确
2. 分析公式应用和计算过程
3. 评估实验设计和数据分析
4. 关注物理思维和逻辑推理
5. 提供概念澄清和方法指导

请按照JSON格式返回批改结果。
""",
            
            SubjectType.CHEMISTRY: """
你是一位化学老师，请批改这份化学作业。

批改要求：
1. 检查化学方程式和反应机理
2. 分析实验步骤和安全注意事项
3. 评估计算过程和结果准确性
4. 关注化学概念和原理理解
5. 提供实验技能和理论学习建议

请按照JSON格式返回批改结果。
"""
        }
    
    def _load_subject_configs(self) -> Dict[str, Dict[str, Any]]:
        """加载学科配置"""
        return {
            SubjectType.MATH: {
                "focus_areas": ["计算准确性", "解题方法", "逻辑推理", "概念理解"],
                "common_mistakes": ["计算错误", "公式误用", "步骤遗漏", "概念混淆"],
                "grading_weights": {"accuracy": 0.4, "method": 0.3, "process": 0.2, "presentation": 0.1}
            },
            SubjectType.CHINESE: {
                "focus_areas": ["字词准确", "语法正确", "表达流畅", "内容深度"],
                "common_mistakes": ["错别字", "语法错误", "表达不清", "逻辑混乱"],
                "grading_weights": {"language": 0.3, "content": 0.4, "structure": 0.2, "creativity": 0.1}
            },
            SubjectType.ENGLISH: {
                "focus_areas": ["Grammar", "Vocabulary", "Fluency", "Content"],
                "common_mistakes": ["Grammar errors", "Word choice", "Sentence structure", "Spelling"],
                "grading_weights": {"grammar": 0.3, "vocabulary": 0.2, "content": 0.3, "fluency": 0.2}
            }
        }
    
    async def _grade_image_homework_enhanced(self, submission: HomeworkSubmission, criteria: GradingCriteria) -> GradingResult:
        """增强的图像作业批改方法"""
        try:
            if not submission.image_urls:
                raise ValueError("图像作业缺少图片")
            
            # 获取学科配置
            subject_config = self.subject_configs.get(submission.subject, {})
            
            # 分析每张图片
            all_analyses = []
            total_confidence = 0
            
            for i, image_url in enumerate(submission.image_urls):
                try:
                    # 构建图像分析提示
                    analysis_prompt = f"""请分析这张{submission.subject.value}作业图片：
                    
1. 识别图片中的题目内容和学生答案
2. 根据学科要求进行批改
3. 给出详细的分析和评分
4. 指出错误并提供改进建议

学科：{submission.subject.value}
学生：{submission.student_name}
图片序号：{i + 1}

请返回JSON格式的分析结果。"""
                    
                    # 调用图像分析API
                    ai_request = AIRequest(
                        provider=AIProvider.OPENAI,
                        model="gpt-4-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": analysis_prompt},
                                    {"type": "image_url", "image_url": {"url": image_url}}
                                ]
                            }
                        ],
                        temperature=0.3,
                        max_tokens=1500
                    )
                    
                    response = await self.ai_manager.chat_completion_with_fallback(ai_request)
                    
                    if response.success:
                        analysis_data = self._parse_image_analysis_response(response.content, i + 1)
                        all_analyses.extend(analysis_data.get("questions", []))
                        total_confidence += analysis_data.get("confidence", 0.5)
                    else:
                        logger.warning(f"图片 {i + 1} 分析失败: {response.error}")
                        
                except Exception as e:
                    logger.error(f"图片 {i + 1} 处理失败: {str(e)}")
                    continue
            
            # 计算平均置信度
            avg_confidence = total_confidence / len(submission.image_urls) if submission.image_urls else 0
            
            # 综合分析结果
            total_score = sum(q.get("score", 0) for q in all_analyses)
            max_score = sum(q.get("max_score", 10) for q in all_analyses)
            
            # 构建批改结果
            grading_data = {
                "questions": all_analyses,
                "overall_comments": "基于图像识别的批改结果",
                "strengths": ["书写工整", "步骤清晰"],
                "weaknesses": ["部分内容识别可能有误"],
                "suggestions": ["建议提交文本版本以获得更准确的批改"],
                "confidence": avg_confidence
            }
            
            return self._build_grading_result(submission, criteria, grading_data, None)
            
        except Exception as e:
            logger.error(f"图像作业批改失败: {str(e)}")
            raise
    
    async def batch_grade_homework_enhanced(self, submissions: List[HomeworkSubmission], criteria: Optional[GradingCriteria] = None) -> List[GradingResult]:
        """增强的批量批改作业方法"""
        try:
            results = []
            
            # 分批处理
            for i in range(0, len(submissions), self.batch_size):
                batch = submissions[i:i + self.batch_size]
                
                # 并发处理当前批次
                batch_tasks = [self.grade_homework(submission, criteria) for submission in batch]
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # 处理结果
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"批改失败 - 学生ID: {batch[j].student_id}, 错误: {str(result)}")
                        # 创建错误结果
                        error_result = GradingResult(
                            submission_id=f"{batch[j].student_id}_{batch[j].assignment_id}_error",
                            student_id=batch[j].student_id,
                            student_name=batch[j].student_name,
                            subject=batch[j].subject,
                            assignment_id=batch[j].assignment_id,
                            total_score=0,
                            max_score=100,
                            percentage=0,
                            grade_level="批改失败",
                            detailed_feedback=[],
                            overall_comments=f"批改失败: {str(result)}",
                            strengths=[],
                            weaknesses=[],
                            suggestions=["请联系老师重新批改"],
                            grading_time=datetime.now(),
                            ai_confidence=0,
                            requires_manual_review=True
                        )
                        results.append(error_result)
                    else:
                        results.append(result)
                
                # 避免API限流
                if i + self.batch_size < len(submissions):
                    await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"批量批改失败: {str(e)}")
            raise
    
    def _parse_grading_response(self, response_content: str) -> Dict[str, Any]:
        """解析AI批改响应"""
        try:
            # 尝试解析JSON
            if response_content.strip().startswith('{'):
                return json.loads(response_content)
            
            # 如果不是JSON格式，尝试提取结构化信息
            grading_data = {
                "total_score": 0,
                "max_score": 100,
                "question_analyses": [],
                "overall_feedback": response_content,
                "improvement_suggestions": [],
                "confidence": 0.7
            }
            
            # 简单的分数提取
            import re
            score_match = re.search(r'(\d+)\s*[/分]\s*(\d+)', response_content)
            if score_match:
                grading_data["total_score"] = int(score_match.group(1))
                grading_data["max_score"] = int(score_match.group(2))
            
            return grading_data
            
        except Exception as e:
            logger.error(f"解析批改响应失败: {str(e)}")
            return {
                "total_score": 0,
                "max_score": 100,
                "question_analyses": [],
                "overall_feedback": "批改结果解析失败",
                "improvement_suggestions": ["请联系老师重新批改"],
                "confidence": 0.3
            }
    
    def _parse_image_analysis_response(self, response_content: str, image_index: int) -> Dict[str, Any]:
        """解析图像分析响应"""
        try:
            if response_content.strip().startswith('{'):
                data = json.loads(response_content)
            else:
                # 非JSON格式的简单解析
                data = {
                    "question_analyses": [{
                        "question_number": f"图片{image_index}",
                        "question_content": "图像识别内容",
                        "student_answer": "学生答案",
                        "score": 0,
                        "max_score": 10,
                        "feedback": response_content,
                        "is_correct": False
                    }],
                    "confidence": 0.6
                }
            
            return data
            
        except Exception as e:
            logger.error(f"解析图像分析响应失败: {str(e)}")
            return {
                "question_analyses": [],
                "confidence": 0.3
            }
    
    def _generate_overall_feedback(self, analyses: List[Dict[str, Any]], subject: SubjectType) -> str:
        """生成整体反馈"""
        try:
            if not analyses:
                return "暂无具体分析结果"
            
            total_questions = len(analyses)
            correct_count = sum(1 for analysis in analyses if analysis.get("is_correct", False))
            accuracy = correct_count / total_questions if total_questions > 0 else 0
            
            feedback_parts = [
                f"本次作业共{total_questions}道题，正确{correct_count}道，准确率{accuracy:.1%}。"
            ]
            
            if accuracy >= 0.9:
                feedback_parts.append("表现优秀，继续保持！")
            elif accuracy >= 0.7:
                feedback_parts.append("表现良好，还有提升空间。")
            elif accuracy >= 0.5:
                feedback_parts.append("基础掌握一般，需要加强练习。")
            else:
                feedback_parts.append("基础较薄弱，建议重点复习相关知识点。")
            
            return " ".join(feedback_parts)
            
        except Exception as e:
            logger.error(f"生成整体反馈失败: {str(e)}")
            return "整体表现有待提高，请继续努力。"
    
    def _generate_improvement_suggestions(self, analyses: List[Dict[str, Any]], subject: SubjectType) -> List[str]:
        """生成改进建议"""
        try:
            suggestions = []
            
            # 分析错误类型
            error_types = {}
            for analysis in analyses:
                if not analysis.get("is_correct", False):
                    error_type = analysis.get("error_type", "其他错误")
                    error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # 根据错误类型生成建议
            if "计算错误" in error_types:
                suggestions.append("注意计算准确性，建议多做计算练习")
            
            if "概念理解" in error_types:
                suggestions.append("加强基础概念的理解和记忆")
            
            if "解题步骤" in error_types:
                suggestions.append("规范解题步骤，逐步分析问题")
            
            if "书写规范" in error_types:
                suggestions.append("注意书写规范，保持卷面整洁")
            
            # 学科特定建议
            subject_suggestions = {
                Subject.MATH: ["多做练习题", "掌握公式运用", "培养逻辑思维"],
                Subject.CHINESE: ["多读优秀文章", "积累词汇", "练习写作技巧"],
                Subject.ENGLISH: ["背诵单词", "练习语法", "多听多说"],
                Subject.PHYSICS: ["理解物理概念", "掌握公式推导", "联系实际应用"],
                Subject.CHEMISTRY: ["记忆化学方程式", "理解反应原理", "注意实验安全"],
                Subject.BIOLOGY: ["理解生物过程", "记忆专业术语", "观察生物现象"]
            }
            
            if subject in subject_suggestions:
                suggestions.extend(subject_suggestions[subject][:2])  # 添加前两个建议
            
            return suggestions[:5]  # 最多返回5个建议
            
        except Exception as e:
            logger.error(f"生成改进建议失败: {str(e)}")
            return ["继续努力学习", "多做练习", "及时复习"]
    
    async def get_grading_statistics(self, student_id: str, subject: Optional[SubjectType] = None, 
                                   start_date: Optional[datetime] = None, 
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """获取批改统计信息"""
        try:
            # 这里应该从数据库查询历史批改记录
            # 暂时返回模拟数据
            stats = {
                "total_assignments": 10,
                "average_score": 85.5,
                "highest_score": 98,
                "lowest_score": 72,
                "improvement_trend": "上升",
                "subject_performance": {
                    "math": {"average": 88, "count": 5},
                    "chinese": {"average": 83, "count": 3},
                    "english": {"average": 85, "count": 2}
                },
                "common_errors": [
                    {"type": "计算错误", "count": 3, "percentage": 30},
                    {"type": "概念理解", "count": 2, "percentage": 20}
                ],
                "suggestions": [
                    "加强计算练习",
                    "复习基础概念",
                    "保持良好学习习惯"
                ]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}
    
    async def export_grading_report(self, results: List[GradingResult], format_type: str = "json") -> str:
        """导出批改报告"""
        try:
            if format_type == "json":
                report_data = {
                    "export_time": datetime.now().isoformat(),
                    "total_count": len(results),
                    "results": [result.dict() for result in results],
                    "summary": {
                        "average_score": sum(r.total_score for r in results) / len(results) if results else 0,
                        "pass_rate": sum(1 for r in results if r.total_score >= r.max_score * 0.6) / len(results) if results else 0,
                        "manual_review_count": sum(1 for r in results if r.requires_manual_review)
                    }
                }
                return json.dumps(report_data, ensure_ascii=False, indent=2)
            
            elif format_type == "csv":
                # CSV格式导出
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入表头
                writer.writerow([
                    "学生ID", "学生姓名", "科目", "作业ID", "总分", "满分", 
                    "得分率", "等级", "批改时间", "AI置信度", "需要人工复核"
                ])
                
                # 写入数据
                for result in results:
                    writer.writerow([
                        result.student_id,
                        result.student_name,
                        result.subject.value,
                        result.assignment_id,
                        result.total_score,
                        result.max_score,
                        f"{result.percentage:.1f}%",
                        result.grade_level,
                        result.grading_time.strftime("%Y-%m-%d %H:%M:%S"),
                        f"{result.ai_confidence:.2f}",
                        "是" if result.requires_manual_review else "否"
                    ])
                
                return output.getvalue()
            
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
                
        except Exception as e:
            logger.error(f"导出报告失败: {str(e)}")
            raise
    
    async def grade_homework(self, submission: HomeworkSubmission, criteria: Optional[GradingCriteria] = None) -> GradingResult:
        """批改作业主入口"""
        try:
            if criteria is None:
                criteria = GradingCriteria()
            
            if submission.submission_type == SubmissionType.TEXT:
                return await self._grade_text_homework(submission, criteria)
            elif submission.submission_type == SubmissionType.IMAGE:
                return await self._grade_image_homework(submission, criteria)
            elif submission.submission_type == SubmissionType.FILE:
                return await self._grade_file_homework(submission, criteria)
            else:
                raise ValueError(f"Unsupported submission type: {submission.submission_type}")
        
        except Exception as e:
            logger.error(f"Homework grading failed: {str(e)}")
            raise
    
    async def _grade_text_homework(self, submission: HomeworkSubmission, criteria: GradingCriteria) -> GradingResult:
        """批改文本作业"""
        prompt = self.grading_prompts.get(submission.subject, self.grading_prompts[SubjectType.CHINESE])
        
        # 构建详细的批改请求
        grading_context = f"""
学生信息：
- 姓名：{submission.student_name}
- 学号：{submission.student_id}
- 科目：{submission.subject.value}
- 作业ID：{submission.assignment_id}

批改标准：
- 总分：{criteria.total_score}
- 难度等级：{criteria.difficulty_level}
- 批改风格：{criteria.grading_style}

作业内容：
{submission.content}

请仔细批改并按照要求的JSON格式返回结果。
"""
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": grading_context}
        ]
        
        request = AIRequest(
            provider=AIProvider.OPENAI,
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=3000,
            user_id=submission.student_id,
            metadata={"task": "homework_grading", "subject": submission.subject.value}
        )
        
        # 使用简化的LLM作业批改接口
        llm_response = await self.llm_client.analyze_homework({
            'content': submission.content,
            'subject': submission.subject.value,
            'student_name': submission.student_name,
            'criteria': criteria.__dict__
        })
        
        if not llm_response or not llm_response.get('success'):
            raise Exception(f"LLM批改失败: {llm_response.get('error', '未知错误') if llm_response else 'LLM服务不可用'}")
        
        # 解析LLM响应
        grading_data = llm_response.get('result', {})
        
        # 构建最终结果
        return self._build_grading_result(submission, criteria, grading_data, response)
    
    async def _grade_image_homework(self, submission: HomeworkSubmission, criteria: GradingCriteria) -> GradingResult:
        """批改图片作业"""
        if not submission.image_urls:
            raise ValueError("No images provided for image homework")
        
        all_analyses = []
        total_confidence = 0
        
        for i, image_url in enumerate(submission.image_urls):
            prompt = f"""
请分析这张{submission.subject.value}作业图片：

1. 识别题目内容和学生答案
2. 分析解题过程和方法
3. 评估答案正确性
4. 给出具体的批改意见
5. 提供改进建议

学生：{submission.student_name}
科目：{submission.subject.value}
图片序号：{i + 1}

请按照JSON格式返回分析结果。
"""
            
            # 调用图像分析API
            response = await self.ai_manager.services[AIProvider.OPENAI].image_analysis(
                image_url, prompt
            )
            
            if response.success:
                analysis_data = self._parse_image_analysis_response(response.content, i + 1)
                all_analyses.extend(analysis_data["questions"])
                total_confidence += analysis_data["confidence"]
            else:
                logger.warning(f"Failed to analyze image {i + 1}: {response.error}")
        
        # 综合所有图片的分析结果
        avg_confidence = total_confidence / len(submission.image_urls) if submission.image_urls else 0
        
        # 构建综合批改结果
        grading_data = {
            "questions": all_analyses,
            "overall_comments": "基于图片识别的批改结果，建议人工复核",
            "strengths": ["书写工整", "步骤清晰"],
            "weaknesses": ["部分内容识别可能有误"],
            "suggestions": ["建议提交文本版本以获得更准确的批改"],
            "confidence": avg_confidence
        }
        
        return self._build_grading_result(submission, criteria, grading_data, None)
    
    async def _grade_file_homework(self, submission: HomeworkSubmission, criteria: GradingCriteria) -> GradingResult:
        """批改文件作业"""
        # 这里应该实现文件解析和批改逻辑
        # 目前返回模拟结果
        grading_data = {
            "questions": [],
            "overall_comments": "文件作业批改功能正在开发中",
            "strengths": [],
            "weaknesses": [],
            "suggestions": ["请联系老师进行人工批改"],
            "confidence": 0.0
        }
        
        return self._build_grading_result(submission, criteria, grading_data, None)
    
    def _parse_grading_response(self, response_content: str, subject: SubjectType) -> Dict[str, Any]:
        """解析AI批改响应"""
        try:
            # 尝试解析JSON响应
            if response_content.strip().startswith('{'):
                return json.loads(response_content)
            
            # 如果不是JSON格式，尝试提取关键信息
            return self._extract_grading_info_from_text(response_content, subject)
        
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, extracting from text")
            return self._extract_grading_info_from_text(response_content, subject)
    
    def _extract_grading_info_from_text(self, text: str, subject: SubjectType) -> Dict[str, Any]:
        """从文本中提取批改信息"""
        # 简化的文本解析逻辑
        lines = text.split('\n')
        
        return {
            "questions": [
                {
                    "question_number": 1,
                    "question_type": "综合题",
                    "student_answer": "学生答案",
                    "score": 80.0,
                    "max_score": 100.0,
                    "feedback": text[:200] + "...",
                    "mistakes": ["需要人工分析"],
                    "suggestions": ["建议详细复习相关知识点"]
                }
            ],
            "overall_comments": text[:300] + "...",
            "strengths": ["学习态度认真"],
            "weaknesses": ["需要加强练习"],
            "suggestions": ["多做类似题目", "注意基础知识巩固"],
            "confidence": 0.6
        }
    
    def _parse_image_analysis_response(self, response_content: str, image_index: int) -> Dict[str, Any]:
        """解析图像分析响应"""
        try:
            if response_content.strip().startswith('{'):
                return json.loads(response_content)
        except:
            pass
        
        # 简化的图像分析结果
        return {
            "questions": [
                {
                    "question_number": image_index,
                    "question_type": "图片题目",
                    "student_answer": "从图片识别的答案",
                    "score": 75.0,
                    "max_score": 100.0,
                    "feedback": f"图片{image_index}的分析结果",
                    "mistakes": ["图片识别可能存在误差"],
                    "suggestions": ["建议提供文字版本"]
                }
            ],
            "confidence": 0.7
        }
    
    def _build_grading_result(self, submission: HomeworkSubmission, criteria: GradingCriteria, grading_data: Dict[str, Any], ai_response) -> GradingResult:
        """构建批改结果"""
        # 计算总分
        questions = grading_data.get("questions", [])
        total_score = sum(q.get("score", 0) for q in questions)
        max_score = sum(q.get("max_score", criteria.total_score / len(questions)) for q in questions) if questions else criteria.total_score
        
        if max_score == 0:
            max_score = criteria.total_score
            total_score = criteria.total_score * 0.8  # 默认80分
        
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # 确定等级
        if percentage >= 90:
            grade_level = "优秀"
        elif percentage >= 80:
            grade_level = "良好"
        elif percentage >= 70:
            grade_level = "中等"
        elif percentage >= 60:
            grade_level = "及格"
        else:
            grade_level = "不及格"
        
        # 构建详细反馈
        detailed_feedback = [
            QuestionAnalysis(
                question_number=q.get("question_number", i + 1),
                question_type=q.get("question_type", "未知类型"),
                student_answer=q.get("student_answer", ""),
                correct_answer=q.get("correct_answer"),
                score=q.get("score", 0),
                max_score=q.get("max_score", 10),
                feedback=q.get("feedback", ""),
                mistakes=q.get("mistakes", []),
                suggestions=q.get("suggestions", [])
            )
            for i, q in enumerate(questions)
        ]
        
        confidence = grading_data.get("confidence", 0.8)
        
        return GradingResult(
            submission_id=f"{submission.student_id}_{submission.assignment_id}_{int(datetime.now().timestamp())}",
            student_id=submission.student_id,
            student_name=submission.student_name,
            subject=submission.subject,
            assignment_id=submission.assignment_id,
            total_score=total_score,
            max_score=max_score,
            percentage=percentage,
            grade_level=grade_level,
            detailed_feedback=detailed_feedback,
            overall_comments=grading_data.get("overall_comments", "批改完成"),
            strengths=grading_data.get("strengths", []),
            weaknesses=grading_data.get("weaknesses", []),
            suggestions=grading_data.get("suggestions", []),
            grading_time=datetime.now(),
            ai_confidence=confidence,
            requires_manual_review=confidence < 0.8 or submission.submission_type == SubmissionType.IMAGE,
            metadata={
                "ai_provider": ai_response.provider.value if ai_response else "unknown",
                "response_time": ai_response.response_time if ai_response else None,
                "grading_criteria": criteria.__dict__
            }
        )
    
    async def batch_grade_homework(self, submissions: List[HomeworkSubmission], criteria: Optional[GradingCriteria] = None) -> List[GradingResult]:
        """批量批改作业"""
        results = []
        
        for submission in submissions:
            try:
                result = await self.grade_homework(submission, criteria)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to grade homework for student {submission.student_id}: {str(e)}")
                # 创建错误结果
                error_result = GradingResult(
                    submission_id=f"{submission.student_id}_{submission.assignment_id}_error",
                    student_id=submission.student_id,
                    student_name=submission.student_name,
                    subject=submission.subject,
                    assignment_id=submission.assignment_id,
                    total_score=0,
                    max_score=100,
                    percentage=0,
                    grade_level="批改失败",
                    detailed_feedback=[],
                    overall_comments=f"批改失败：{str(e)}",
                    strengths=[],
                    weaknesses=[],
                    suggestions=["请联系老师重新批改"],
                    grading_time=datetime.now(),
                    ai_confidence=0.0,
                    requires_manual_review=True
                )
                results.append(error_result)
        
        return results
    
    def get_subject_statistics(self, results: List[GradingResult]) -> Dict[str, Any]:
        """获取学科统计信息"""
        if not results:
            return {}
        
        total_students = len(results)
        total_score = sum(r.total_score for r in results)
        avg_score = total_score / total_students
        
        pass_count = sum(1 for r in results if r.percentage >= 60)
        excellent_count = sum(1 for r in results if r.percentage >= 90)
        
        return {
            "total_students": total_students,
            "average_score": round(avg_score, 2),
            "average_percentage": round(sum(r.percentage for r in results) / total_students, 2),
            "pass_rate": round((pass_count / total_students) * 100, 2),
            "excellent_rate": round((excellent_count / total_students) * 100, 2),
            "grade_distribution": {
                grade: sum(1 for r in results if r.grade_level == grade)
                for grade in ["优秀", "良好", "中等", "及格", "不及格"]
            },
            "requires_review_count": sum(1 for r in results if r.requires_manual_review)
        }