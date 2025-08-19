#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM API接口模块
提供统一的LLM服务HTTP接口
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# from .llm.manager import get_llm_manager, LLMManager
# 暂时注释掉，使用简化的LLM客户端
from llm_client import get_llm_client
# from .llm.unified_interface import LLMProvider, LLMResponse
# 暂时注释掉，使用简化的实现
from auth import get_current_user
from database import get_db
from models.user import UserInDB as User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["LLM服务"])


# 请求模型
class GenerateRequest(BaseModel):
    """文本生成请求"""
    prompt: str = Field(..., description="输入提示词")
    model: Optional[str] = Field(None, description="模型名称")
    provider: Optional[str] = Field(None, description="提供商")
    max_tokens: Optional[int] = Field(None, description="最大token数")
    temperature: Optional[float] = Field(None, description="温度参数")
    stream: bool = Field(False, description="是否流式输出")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "请为高中数学函数章节设计一个学习计划",
                "model": "qwen-plus",
                "provider": "tongyi",
                "max_tokens": 2000,
                "temperature": 0.7,
                "stream": False
            }
        }


class ChatRequest(BaseModel):
    """对话请求"""
    messages: List[Dict[str, str]] = Field(..., description="对话消息列表")
    model: Optional[str] = Field(None, description="模型名称")
    provider: Optional[str] = Field(None, description="提供商")
    max_tokens: Optional[int] = Field(None, description="最大token数")
    temperature: Optional[float] = Field(None, description="温度参数")
    stream: bool = Field(False, description="是否流式输出")
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "你好，我是一名高中生，数学成绩不太好"}
                ],
                "model": "qwen-plus",
                "provider": "tongyi",
                "max_tokens": 2000,
                "temperature": 0.7,
                "stream": False
            }
        }


class TutoringPlanRequest(BaseModel):
    """辅导方案生成请求"""
    student_id: int = Field(..., description="学生ID")
    subject_id: Optional[int] = Field(None, description="科目ID")
    duration_days: int = Field(30, description="方案持续天数")
    plan_type: str = Field("comprehensive", description="方案类型")
    focus_areas: Optional[List[str]] = Field(None, description="重点关注领域")
    difficulty_level: Optional[str] = Field(None, description="难度等级")
    
    class Config:
        schema_extra = {
            "example": {
                "student_id": 1,
                "subject_id": 1,
                "duration_days": 30,
                "plan_type": "comprehensive",
                "focus_areas": ["函数", "导数"],
                "difficulty_level": "medium"
            }
        }


# 响应模型
class GenerateResponse(BaseModel):
    """生成响应"""
    success: bool
    content: str
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    request_id: Optional[str] = None
    latency: Optional[float] = None
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: float
    overall_health: Dict[str, Any]
    provider_health: Dict[str, Any]


class PerformanceResponse(BaseModel):
    """性能报告响应"""
    timestamp: str
    health_status: Dict[str, Any]
    overall_stats: Dict[str, Any]
    window_stats: Dict[str, Any]
    error_analysis: Dict[str, Any]


@router.post("/generate", response_model=GenerateResponse, summary="文本生成")
async def generate_text(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    # llm_manager: LLMManager = Depends(get_llm_manager)
# 暂时使用简化实现
):
    """生成文本"""
    try:
        # 暂时使用简化实现
        provider = request.provider
        
        # 暂时不支持流式响应
        if request.stream:
            raise HTTPException(status_code=501, detail="暂不支持流式响应")
        
        # 生成请求ID
        request_id = f"gen_{current_user.user_id}_{int(datetime.now().timestamp() * 1000)}"
        
        # 使用简化的LLM客户端
        import time
        start_time = time.time()
        
        llm_client = get_llm_client()
        response = await llm_client.generate_text(request.prompt)
        
        latency = time.time() - start_time
        
        return GenerateResponse(
            success=response.success,
            content=response.content,
            usage=response.usage.__dict__ if response.usage else None,
            model=response.model,
            provider=response.provider,
            request_id=request_id,
            latency=latency,
            error_message=response.error_message if not response.success else None
        )
        
    except Exception as e:
        logger.error(f"文本生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"文本生成失败: {str(e)}")


@router.post("/chat", response_model=GenerateResponse, summary="对话生成")
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
    # llm_manager: LLMManager = Depends(get_llm_manager)
):
    """对话生成"""
    try:
        # 转换提供商
        provider = None
        if request.provider:
            try:
                provider = LLMProvider(request.provider.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"不支持的提供商: {request.provider}")
        
        # 如果是流式请求，返回流式响应
        if request.stream:
            return StreamingResponse(
                _stream_chat(llm_manager, request, provider),
                media_type="text/plain"
            )
        
        # 生成请求ID
        request_id = f"chat_{current_user.user_id}_{int(datetime.now().timestamp() * 1000)}"
        
        # 调用LLM管理器
        import time
        start_time = time.time()
        
        response = await llm_manager.chat(
            messages=request.messages,
            model=request.model,
            provider=provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            request_id=request_id
        )
        
        latency = time.time() - start_time
        
        return GenerateResponse(
            success=response.success,
            content=response.content,
            usage=response.usage.__dict__ if response.usage else None,
            model=response.model,
            provider=response.provider,
            request_id=request_id,
            latency=latency,
            error_message=response.error_message if not response.success else None
        )
        
    except Exception as e:
        logger.error(f"对话生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"对话生成失败: {str(e)}")


@router.post("/tutoring-plan", response_model=GenerateResponse, summary="生成辅导方案")
async def generate_tutoring_plan(
    request: TutoringPlanRequest,
    current_user: User = Depends(get_current_user)
    # llm_manager: LLMManager = Depends(get_llm_manager)
):
    """生成个性化辅导方案"""
    try:
        from .tutoring_plan import TutoringPlanGenerator
        from .database import get_db
        
        # 获取数据库会话
        db = next(get_db())
        
        # 创建辅导方案生成器
        generator = TutoringPlanGenerator(db=db, llm_manager=llm_manager)
        
        # 生成辅导方案
        plan = generator.generate_tutoring_plan(
            student_id=request.student_id,
            subject_id=request.subject_id,
            duration_days=request.duration_days,
            plan_type=request.plan_type
        )
        
        return GenerateResponse(
            success=True,
            content=plan.plan_content,
            model="qwen-plus",
            provider="tongyi",
            request_id=f"tutoring_{request.student_id}_{plan.plan_id}"
        )
        
    except Exception as e:
        logger.error(f"生成辅导方案失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成辅导方案失败: {str(e)}")


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check(
    # llm_manager: LLMManager = Depends(get_llm_manager)
):
    """LLM服务健康检查"""
    try:
        health_status = await llm_manager.health_check()
        
        return HealthResponse(
            status=health_status['overall_health']['status'],
            timestamp=health_status['timestamp'],
            overall_health=health_status['overall_health'],
            provider_health=health_status['provider_health']
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.get("/performance", response_model=PerformanceResponse, summary="性能报告")
async def get_performance_report(
    current_user: User = Depends(get_current_user)
    # llm_manager: LLMManager = Depends(get_llm_manager)
):
    """获取LLM服务性能报告"""
    try:
        # 检查用户权限（只有管理员可以查看性能报告）
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="权限不足")
        
        performance_report = llm_manager.get_performance_report()
        
        return PerformanceResponse(**performance_report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取性能报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能报告失败: {str(e)}")


@router.get("/providers", summary="获取可用提供商")
async def get_available_providers(
    # llm_manager: LLMManager = Depends(get_llm_manager)
):
    """获取可用的LLM提供商列表"""
    try:
        providers = llm_manager.get_available_providers()
        models = llm_manager.get_available_models()
        
        return {
            "providers": providers,
            "models": models
        }
        
    except Exception as e:
        logger.error(f"获取提供商列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取提供商列表失败: {str(e)}")


# 流式生成辅助函数
async def _stream_generate(llm_manager, request: GenerateRequest, provider):
    """流式文本生成"""
    try:
        async for chunk in llm_manager.stream_generate(
            prompt=request.prompt,
            model=request.model,
            provider=provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        ):
            yield f"data: {chunk}\n\n"
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        yield f"data: [ERROR] {str(e)}\n\n"


async def _stream_chat(llm_manager, request: ChatRequest, provider):
    """流式对话生成"""
    try:
        async for chunk in llm_manager.stream_chat(
            messages=request.messages,
            model=request.model,
            provider=provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        ):
            yield f"data: {chunk}\n\n"
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        yield f"data: [ERROR] {str(e)}\n\n"


# 后台任务
@router.post("/background/warm-up", summary="预热LLM服务")
async def warm_up_llm_service(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
    # llm_manager: LLMManager = Depends(get_llm_manager)
):
    """预热LLM服务（后台任务）"""
    try:
        # 检查用户权限
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 添加后台任务
        background_tasks.add_task(_warm_up_llm_service, llm_manager)
        
        return {"message": "LLM服务预热任务已启动"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动预热任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动预热任务失败: {str(e)}")


async def _warm_up_llm_service(llm_manager):
    """预热LLM服务的后台任务"""
    try:
        logger.info("开始预热LLM服务...")
        
        # 发送简单的测试请求到各个提供商
        test_prompt = "你好，这是一个测试请求。"
        
        for provider in [LLMProvider.TONGYI, LLMProvider.OPENAI]:
            try:
                response = await llm_manager.generate(
                    prompt=test_prompt,
                    provider=provider,
                    max_tokens=10,
                    request_id=f"warmup_{provider.value}"
                )
                
                if response.success:
                    logger.info(f"预热{provider.value}成功")
                else:
                    logger.warning(f"预热{provider.value}失败: {response.error_message}")
                    
            except Exception as e:
                logger.warning(f"预热{provider.value}时出错: {e}")
        
        logger.info("LLM服务预热完成")
        
    except Exception as e:
        logger.error(f"预热LLM服务失败: {e}")