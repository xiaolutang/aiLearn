#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI LLM客户端实现
"""

import asyncio
import time
import json
import os
from typing import Dict, List, Optional, Any, AsyncIterator
import logging

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unified_interface import (
    UnifiedLLMInterface, LLMRequest, LLMResponse, LLMProvider, LLMUsage,
    LLMNetworkException, LLMAuthenticationException, LLMRateLimitException, 
    LLMModelException, LLMTimeoutException, LLMQuotaExceededException
)

logger = logging.getLogger(__name__)


class OpenAILLMClient(UnifiedLLMInterface):
    """OpenAI LLM客户端"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(LLMProvider.OPENAI, config)
        
        # 配置参数
        self.api_key = self.config.get('api_key') or os.environ.get('OPENAI_API_KEY')
        self.base_url = self.config.get('base_url') or os.environ.get('OPENAI_BASE_URL', 
            'https://api.openai.com/v1')
        self.default_model = self.config.get('default_model') or os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        if not self.api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        # 初始化客户端
        if AsyncOpenAI:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        else:
            self.client = None
            logger.warning("AsyncOpenAI未安装，将使用HTTP客户端")
        
        # 模型配置
        self.model_configs = {
            'gpt-3.5-turbo': {'max_tokens': 4096, 'context_length': 4096},
            'gpt-3.5-turbo-16k': {'max_tokens': 16384, 'context_length': 16384},
            'gpt-4': {'max_tokens': 8192, 'context_length': 8192},
            'gpt-4-32k': {'max_tokens': 32768, 'context_length': 32768},
            'gpt-4-turbo': {'max_tokens': 128000, 'context_length': 128000},
            'gpt-4o': {'max_tokens': 128000, 'context_length': 128000},
            'gpt-4o-mini': {'max_tokens': 128000, 'context_length': 128000}
        }
        
        # 速率限制配置
        self.rate_limit = {
            'requests_per_minute': self.config.get('requests_per_minute', 60),
            'tokens_per_minute': self.config.get('tokens_per_minute', 90000),
            'last_request_time': 0,
            'request_count': 0,
            'token_count': 0,
            'window_start': time.time()
        }
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """生成文本响应"""
        start_time = time.time()
        
        try:
            # 检查速率限制
            await self._check_rate_limit()
            
            # 准备请求参数
            model = request.model or self.default_model
            
            if request.prompt:
                messages = [{'role': 'user', 'content': request.prompt}]
            else:
                messages = request.messages or []
            
            # 调用API
            if self.client:
                response = await self._call_openai_api(model, messages, request)
            else:
                response = await self._call_http_api(model, messages, request)
            
            latency = time.time() - start_time
            
            # 更新速率限制计数
            self._update_rate_limit(response.usage.total_tokens)
            
            return self._create_success_response(
                content=response.content,
                model=model,
                usage=response.usage,
                latency=latency,
                request_id=getattr(response, 'request_id', None)
            )
            
        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"OpenAI生成失败: {e}")
            return self._create_error_response(request, e, latency)
    
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """进行对话"""
        # chat和generate使用相同的实现
        return await self.generate(request)
    
    async def stream_generate(self, request: LLMRequest) -> AsyncIterator[str]:
        """流式生成文本"""
        try:
            await self._check_rate_limit()
            
            model = request.model or self.default_model
            
            if request.prompt:
                messages = [{'role': 'user', 'content': request.prompt}]
            else:
                messages = request.messages or []
            
            if self.client:
                async for chunk in self._stream_openai_api(model, messages, request):
                    yield chunk
            else:
                async for chunk in self._stream_http_api(model, messages, request):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"OpenAI流式生成失败: {e}")
            yield f"错误: {str(e)}"
    
    async def stream_chat(self, request: LLMRequest) -> AsyncIterator[str]:
        """流式对话"""
        async for chunk in self.stream_generate(request):
            yield chunk
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self.model_configs.keys())
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            test_request = LLMRequest(
                prompt="Hello",
                model=self.default_model,
                max_tokens=10
            )
            response = await self.generate(test_request)
            return response.success
        except Exception as e:
            logger.error(f"OpenAI健康检查失败: {e}")
            return False
    
    async def _call_openai_api(self, model: str, messages: List[Dict], 
                              request: LLMRequest) -> LLMResponse:
        """使用OpenAI客户端调用API"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty,
                stop=request.stop,
                stream=False
            )
            
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            return type('Response', (), {
                'content': response.choices[0].message.content,
                'usage': usage,
                'request_id': getattr(response, 'id', None)
            })()
            
        except Exception as e:
            self._handle_api_error(e)
    
    async def _call_http_api(self, model: str, messages: List[Dict],
                           request: LLMRequest) -> LLMResponse:
        """使用HTTP客户端调用API"""
        if not aiohttp:
            raise ImportError("需要安装aiohttp库")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': messages,
            'temperature': request.temperature,
            'stream': False
        }
        
        if request.max_tokens:
            data['max_tokens'] = request.max_tokens
        if request.top_p != 1.0:
            data['top_p'] = request.top_p
        if request.frequency_penalty != 0.0:
            data['frequency_penalty'] = request.frequency_penalty
        if request.presence_penalty != 0.0:
            data['presence_penalty'] = request.presence_penalty
        if request.stop:
            data['stop'] = request.stop
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/chat/completions", 
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        usage = LLMUsage(
                            prompt_tokens=result['usage']['prompt_tokens'],
                            completion_tokens=result['usage']['completion_tokens'],
                            total_tokens=result['usage']['total_tokens']
                        )
                        
                        return type('Response', (), {
                            'content': result['choices'][0]['message']['content'],
                            'usage': usage,
                            'request_id': result.get('id')
                        })()
                    else:
                        error_text = await response.text()
                        self._handle_http_error(response.status, error_text)
                        
        except asyncio.TimeoutError:
            raise TimeoutException("请求超时", LLMProvider.OPENAI)
        except aiohttp.ClientError as e:
            raise NetworkException(f"网络错误: {e}", LLMProvider.OPENAI)
    
    async def _stream_openai_api(self, model: str, messages: List[Dict],
                               request: LLMRequest) -> AsyncIterator[str]:
        """使用OpenAI客户端进行流式调用"""
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty,
                stop=request.stop,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self._handle_api_error(e)
    
    async def _stream_http_api(self, model: str, messages: List[Dict],
                             request: LLMRequest) -> AsyncIterator[str]:
        """使用HTTP客户端进行流式调用"""
        if not aiohttp:
            raise ImportError("需要安装aiohttp库")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': messages,
            'temperature': request.temperature,
            'stream': True
        }
        
        if request.max_tokens:
            data['max_tokens'] = request.max_tokens
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/chat/completions",
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                data_str = line[6:]
                                if data_str == '[DONE]':
                                    break
                                try:
                                    chunk_data = json.loads(data_str)
                                    if 'choices' in chunk_data and chunk_data['choices']:
                                        delta = chunk_data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                    else:
                        error_text = await response.text()
                        self._handle_http_error(response.status, error_text)
                        
        except asyncio.TimeoutError:
            raise TimeoutException("流式请求超时", LLMProvider.OPENAI)
        except aiohttp.ClientError as e:
            raise NetworkException(f"流式网络错误: {e}", LLMProvider.OPENAI)
    
    async def _check_rate_limit(self):
        """检查速率限制"""
        current_time = time.time()
        
        # 重置窗口
        if current_time - self.rate_limit['window_start'] >= 60:
            self.rate_limit['request_count'] = 0
            self.rate_limit['token_count'] = 0
            self.rate_limit['window_start'] = current_time
        
        # 检查请求频率
        if self.rate_limit['request_count'] >= self.rate_limit['requests_per_minute']:
            wait_time = 60 - (current_time - self.rate_limit['window_start'])
            if wait_time > 0:
                raise RateLimitException(f"请求频率超限，需等待{wait_time:.1f}秒", 
                                       LLMProvider.OPENAI, int(wait_time))
        
        # 检查Token频率
        if self.rate_limit['token_count'] >= self.rate_limit['tokens_per_minute']:
            wait_time = 60 - (current_time - self.rate_limit['window_start'])
            if wait_time > 0:
                raise RateLimitException(f"Token使用超限，需等待{wait_time:.1f}秒",
                                       LLMProvider.OPENAI, int(wait_time))
        
        # 请求间隔控制
        time_since_last = current_time - self.rate_limit['last_request_time']
        min_interval = 60 / self.rate_limit['requests_per_minute']
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self.rate_limit['last_request_time'] = time.time()
        self.rate_limit['request_count'] += 1
    
    def _update_rate_limit(self, tokens_used: int):
        """更新速率限制计数"""
        self.rate_limit['token_count'] += tokens_used
    
    def _handle_api_error(self, error: Exception):
        """处理API错误"""
        error_str = str(error).lower()
        
        if 'unauthorized' in error_str or 'invalid api key' in error_str:
            raise LLMAuthenticationException("API密钥无效", LLMProvider.OPENAI)
        elif 'rate limit' in error_str:
            raise LLMRateLimitException("请求频率超限", LLMProvider.OPENAI)
        elif 'quota' in error_str or 'insufficient' in error_str:
            raise LLMQuotaExceededException("配额不足", LLMProvider.OPENAI)
        elif 'timeout' in error_str:
            raise LLMTimeoutException("请求超时", LLMProvider.OPENAI)
        elif 'model' in error_str and 'not found' in error_str:
            raise LLMModelException("模型不存在", LLMProvider.OPENAI)
        else:
            raise LLMNetworkException(f"API调用失败: {error}", LLMProvider.OPENAI)
    
    def _handle_http_error(self, status_code: int, error_text: str):
        """处理HTTP错误"""
        if status_code == 401:
            raise LLMAuthenticationException("认证失败", LLMProvider.OPENAI)
        elif status_code == 429:
            raise LLMRateLimitException("请求频率超限", LLMProvider.OPENAI)
        elif status_code == 402:
            raise LLMQuotaExceededException("配额不足", LLMProvider.OPENAI)
        elif status_code == 404:
            raise LLMModelException("模型不存在", LLMProvider.OPENAI)
        elif status_code >= 500:
            raise LLMNetworkException(f"服务器错误: {status_code}", LLMProvider.OPENAI)
        else:
            raise LLMNetworkException(f"HTTP错误 {status_code}: {error_text}", LLMProvider.OPENAI)