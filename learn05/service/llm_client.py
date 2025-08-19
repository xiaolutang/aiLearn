#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能教学助手后端 - LLM服务客户端
专门用于对接内部LLM服务，简化集成复杂度
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import dataclass
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class LLMRequest:
    """LLM请求数据模型"""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

@dataclass
class LLMResponse:
    """LLM响应数据模型"""
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request_id: Optional[str] = None

class LLMServiceClient:
    """LLM服务客户端 - 专门对接内部LLM服务"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        初始化LLM服务客户端
        
        Args:
            base_url: LLM服务的基础URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发起HTTP请求"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"LLM服务请求失败: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"LLM服务请求异常: {e}")
            raise
    
    async def close(self):
        """关闭客户端连接"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    # ==================== 教学相关AI服务 ====================
    
    async def analyze_homework(self, homework_content: str, subject: str, grade: str) -> LLMResponse:
        """作业分析服务"""
        try:
            data = {
                "content": homework_content,
                "subject": subject,
                "grade": grade,
                "analysis_type": "homework_grading",
                "request_id": f"hw_{datetime.now().timestamp()}"
            }
            
            response = await self._make_request("/api/v1/lesson-prep/analyze-material", data)
            
            return LLMResponse(
                success=response.get("success", False),
                content=response.get("data", {}).get("analysis", ""),
                metadata=response.get("data", {}),
                request_id=response.get("request_id")
            )
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    async def generate_tutoring_plan(self, student_info: Dict[str, Any], subject: str) -> LLMResponse:
        """生成个性化辅导方案"""
        try:
            data = {
                "student_info": student_info,
                "subject": subject,
                "current_level": student_info.get("level", "beginner"),
                "target_level": student_info.get("target", "intermediate"),
                "available_time": student_info.get("time", 2),
                "request_id": f"plan_{datetime.now().timestamp()}"
            }
            
            response = await self._make_request("/api/v1/grades/tutoring-plan", data)
            
            return LLMResponse(
                success=response.get("success", False),
                content=response.get("data", {}).get("plan", ""),
                metadata=response.get("data", {}),
                request_id=response.get("request_id")
            )
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    async def analyze_grades(self, grades_data: List[Dict[str, Any]], analysis_type: str = "comprehensive") -> LLMResponse:
        """成绩分析服务"""
        try:
            data = {
                "grades": grades_data,
                "analysis_type": analysis_type,
                "period": "本学期",
                "request_id": f"grade_{datetime.now().timestamp()}"
            }
            
            response = await self._make_request("/api/v1/grades/analyze", data)
            
            return LLMResponse(
                success=response.get("success", False),
                content=response.get("data", {}).get("analysis", ""),
                metadata=response.get("data", {}),
                request_id=response.get("request_id")
            )
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    async def generate_personalized_guidance(self, student_profile: Dict[str, Any], grade_analysis: Dict[str, Any]) -> LLMResponse:
        """生成个性化学习指导"""
        try:
            data = {
                "student_profile": student_profile,
                "grade_analysis": grade_analysis,
                "learning_preferences": student_profile.get("preferences", {}),
                "request_id": f"guidance_{datetime.now().timestamp()}"
            }
            
            response = await self._make_request("/api/v1/grades/personalized-guidance", data)
            
            return LLMResponse(
                success=response.get("success", False),
                content=response.get("data", {}).get("guidance", ""),
                metadata=response.get("data", {}),
                request_id=response.get("request_id")
            )
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    async def analyze_classroom_data(self, classroom_data: Dict[str, Any]) -> LLMResponse:
        """课堂数据实时分析"""
        try:
            data = {
                "classroom_data": classroom_data,
                "analysis_type": "real_time",
                "student_interactions": classroom_data.get("interactions", []),
                "request_id": f"classroom_{datetime.now().timestamp()}"
            }
            
            response = await self._make_request("/api/v1/classroom/real-time-analysis", data)
            
            return LLMResponse(
                success=response.get("success", False),
                content=response.get("data", {}).get("analysis", ""),
                metadata=response.get("data", {}),
                request_id=response.get("request_id")
            )
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    # ==================== 通用AI服务 ====================
    
    async def generate_text(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """通用文本生成服务"""
        try:
            # 根据上下文选择合适的API端点
            if context and context.get("type") == "lesson_prep":
                endpoint = "/api/v1/lesson-prep/analyze-material"
                data = {
                    "content": prompt,
                    "subject": context.get("subject", "通用"),
                    "grade": context.get("grade", "通用"),
                    "analysis_type": "general"
                }
            else:
                # 使用健康检查端点作为默认的文本生成
                endpoint = "/api/v1/health"
                data = {"prompt": prompt}
            
            response = await self._make_request(endpoint, data)
            
            return LLMResponse(
                success=response.get("success", False),
                content=str(response.get("data", response.get("message", ""))),
                metadata=response.get("data", {})
            )
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    async def health_check(self) -> bool:
        """检查LLM服务健康状态"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/api/v1/health"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("status") == "healthy"
                return False
        except Exception as e:
            logger.error(f"LLM服务健康检查失败: {e}")
            return False

# 全局LLM客户端实例
_llm_client = None

def get_llm_client(base_url: str = "http://localhost:8000") -> LLMServiceClient:
    """获取LLM服务客户端实例（单例模式）"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMServiceClient(base_url)
    return _llm_client

async def analyze_grades_simple(grade_data: List[Dict[str, Any]]) -> str:
    """简化的成绩分析接口"""
    client = get_llm_client()
    response = await client.analyze_grades(grade_data)
    return response.content if response.success else f"分析失败: {response.error}"

async def close_llm_client():
    """关闭LLM客户端连接"""
    global _llm_client
    if _llm_client:
        await _llm_client.close()
        _llm_client = None

# ==================== 便捷函数 ====================

async def analyze_homework_simple(homework_content: str, subject: str, grade: str) -> str:
    """简化的作业分析接口"""
    client = get_llm_client()
    response = await client.analyze_homework(homework_content, subject, grade)
    return response.content if response.success else f"分析失败: {response.error}"

async def generate_tutoring_plan_simple(student_info: Dict[str, Any], subject: str) -> str:
    """简化的辅导方案生成接口"""
    client = get_llm_client()
    response = await client.generate_tutoring_plan(student_info, subject)
    return response.content if response.success else f"生成失败: {response.error}"

async def analyze_grades_simple(grades_data: List[Dict[str, Any]]) -> str:
    """简化的成绩分析接口"""
    client = get_llm_client()
    response = await client.analyze_grades(grades_data)
    return response.content if response.success else f"分析失败: {response.error}"