# -*- coding: utf-8 -*-
"""
并发处理模块
实现多线程和异步处理功能
"""

import asyncio
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Callable, Union, Awaitable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, as_completed
import logging
import queue
import multiprocessing

# 配置日志
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[Exception] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.start_time and self.end_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'result': self.result,
            'error': str(self.error) if self.error else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_time': self.execution_time,
            'metadata': self.metadata
        }

@dataclass
class ProcessingConfig:
    """处理配置"""
    max_workers: int = 4
    timeout: Optional[float] = None
    retry_count: int = 0
    retry_delay: float = 1.0
    enable_logging: bool = True
    queue_size: int = 1000
    batch_size: int = 10
    use_process_pool: bool = False

class ConcurrentProcessor(ABC):
    """并发处理器抽象基类"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        self._tasks: Dict[str, TaskResult] = {}
        self._lock = threading.RLock()
        self._shutdown = False
    
    @abstractmethod
    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """提交任务"""
        pass
    
    @abstractmethod
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> TaskResult:
        """获取任务结果"""
        pass
    
    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        pass
    
    @abstractmethod
    def shutdown(self, wait: bool = True):
        """关闭处理器"""
        pass
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return str(uuid.uuid4())
    
    def _create_task_result(self, task_id: str, status: TaskStatus = TaskStatus.PENDING) -> TaskResult:
        """创建任务结果"""
        return TaskResult(
            task_id=task_id,
            status=status,
            start_time=datetime.now() if status == TaskStatus.RUNNING else None
        )
    
    def _update_task_result(self, task_id: str, status: TaskStatus, 
                           result: Any = None, error: Exception = None):
        """更新任务结果"""
        with self._lock:
            if task_id in self._tasks:
                task_result = self._tasks[task_id]
                task_result.status = status
                task_result.result = result
                task_result.error = error
                
                if status == TaskStatus.RUNNING and task_result.start_time is None:
                    task_result.start_time = datetime.now()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    task_result.end_time = datetime.now()
                    if task_result.start_time:
                        task_result.execution_time = (
                            task_result.end_time - task_result.start_time
                        ).total_seconds()
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        with self._lock:
            task_result = self._tasks.get(task_id)
            return task_result.status if task_result else None
    
    def list_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[TaskResult]:
        """列出任务"""
        with self._lock:
            tasks = list(self._tasks.values())
            if status_filter:
                tasks = [task for task in tasks if task.status == status_filter]
            return tasks
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            total_tasks = len(self._tasks)
            status_counts = {}
            total_execution_time = 0
            
            for task in self._tasks.values():
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if task.execution_time:
                    total_execution_time += task.execution_time
            
            avg_execution_time = (
                total_execution_time / total_tasks if total_tasks > 0 else 0
            )
            
            return {
                'total_tasks': total_tasks,
                'status_counts': status_counts,
                'avg_execution_time': avg_execution_time,
                'total_execution_time': total_execution_time
            }

class ThreadPoolProcessor(ConcurrentProcessor):
    """线程池处理器"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        
        if self.config.use_process_pool:
            self._executor = ProcessPoolExecutor(max_workers=self.config.max_workers)
        else:
            self._executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
        self._futures: Dict[str, Future] = {}
    
    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """提交任务"""
        if self._shutdown:
            raise RuntimeError("处理器已关闭")
        
        task_id = self._generate_task_id()
        
        with self._lock:
            # 创建任务结果
            task_result = self._create_task_result(task_id)
            self._tasks[task_id] = task_result
            
            # 提交任务
            future = self._executor.submit(self._execute_with_retry, task_id, func, *args, **kwargs)
            self._futures[task_id] = future
            
            # 添加完成回调
            future.add_done_callback(lambda f: self._handle_task_completion(task_id, f))
        
        if self.config.enable_logging:
            logger.info(f"任务 {task_id} 已提交")
        
        return task_id
    
    def _execute_with_retry(self, task_id: str, func: Callable, *args, **kwargs) -> Any:
        """带重试的执行"""
        self._update_task_result(task_id, TaskStatus.RUNNING)
        
        last_error = None
        
        for attempt in range(self.config.retry_count + 1):
            try:
                if self.config.enable_logging and attempt > 0:
                    logger.info(f"任务 {task_id} 第 {attempt + 1} 次尝试")
                
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                last_error = e
                
                if self.config.enable_logging:
                    logger.warning(f"任务 {task_id} 第 {attempt + 1} 次尝试失败: {e}")
                
                if attempt < self.config.retry_count:
                    time.sleep(self.config.retry_delay)
                else:
                    raise e
        
        raise last_error
    
    def _handle_task_completion(self, task_id: str, future: Future):
        """处理任务完成"""
        try:
            if future.cancelled():
                self._update_task_result(task_id, TaskStatus.CANCELLED)
            elif future.exception():
                self._update_task_result(task_id, TaskStatus.FAILED, error=future.exception())
            else:
                self._update_task_result(task_id, TaskStatus.COMPLETED, result=future.result())
        except Exception as e:
            self._update_task_result(task_id, TaskStatus.FAILED, error=e)
        finally:
            # 清理future引用
            with self._lock:
                self._futures.pop(task_id, None)
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> TaskResult:
        """获取任务结果"""
        with self._lock:
            if task_id not in self._tasks:
                raise ValueError(f"任务 {task_id} 不存在")
            
            task_result = self._tasks[task_id]
            future = self._futures.get(task_id)
        
        # 如果任务还在运行，等待完成
        if future and not future.done():
            try:
                future.result(timeout=timeout or self.config.timeout)
            except Exception:
                pass  # 错误已在回调中处理
        
        return task_result
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            future = self._futures.get(task_id)
            if future:
                cancelled = future.cancel()
                if cancelled:
                    self._update_task_result(task_id, TaskStatus.CANCELLED)
                return cancelled
            return False
    
    def shutdown(self, wait: bool = True):
        """关闭处理器"""
        self._shutdown = True
        
        # 取消所有待处理的任务
        with self._lock:
            for task_id, future in list(self._futures.items()):
                if not future.done():
                    future.cancel()
                    self._update_task_result(task_id, TaskStatus.CANCELLED)
        
        self._executor.shutdown(wait=wait)
        
        if self.config.enable_logging:
            logger.info("线程池处理器已关闭")
    
    def submit_batch(self, tasks: List[tuple]) -> List[str]:
        """批量提交任务"""
        task_ids = []
        
        for task in tasks:
            if len(task) >= 2:
                func = task[0]
                args = task[1] if len(task) > 1 else ()
                kwargs = task[2] if len(task) > 2 else {}
                
                if not isinstance(args, (list, tuple)):
                    args = (args,)
                
                task_id = self.submit_task(func, *args, **kwargs)
                task_ids.append(task_id)
        
        return task_ids
    
    def wait_for_completion(self, task_ids: List[str], timeout: Optional[float] = None) -> List[TaskResult]:
        """等待任务完成"""
        results = []
        
        for task_id in task_ids:
            result = self.get_result(task_id, timeout)
            results.append(result)
        
        return results

class AsyncProcessor(ConcurrentProcessor):
    """异步处理器"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self._loop = None
        self._async_tasks: Dict[str, asyncio.Task] = {}
        self._semaphore = None
    
    def _ensure_loop(self):
        """确保事件循环存在"""
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.config.max_workers)
    
    def submit_task(self, func: Union[Callable, Awaitable], *args, **kwargs) -> str:
        """提交异步任务"""
        if self._shutdown:
            raise RuntimeError("处理器已关闭")
        
        self._ensure_loop()
        
        task_id = self._generate_task_id()
        
        with self._lock:
            # 创建任务结果
            task_result = self._create_task_result(task_id)
            self._tasks[task_id] = task_result
            
            # 创建异步任务
            if asyncio.iscoroutinefunction(func):
                coro = self._execute_async_with_retry(task_id, func, *args, **kwargs)
            else:
                coro = self._execute_sync_in_async(task_id, func, *args, **kwargs)
            
            task = self._loop.create_task(coro)
            self._async_tasks[task_id] = task
            
            # 添加完成回调
            task.add_done_callback(lambda t: self._handle_async_task_completion(task_id, t))
        
        if self.config.enable_logging:
            logger.info(f"异步任务 {task_id} 已提交")
        
        return task_id
    
    async def _execute_async_with_retry(self, task_id: str, func: Callable, *args, **kwargs) -> Any:
        """带重试的异步执行"""
        async with self._semaphore:
            self._update_task_result(task_id, TaskStatus.RUNNING)
            
            last_error = None
            
            for attempt in range(self.config.retry_count + 1):
                try:
                    if self.config.enable_logging and attempt > 0:
                        logger.info(f"异步任务 {task_id} 第 {attempt + 1} 次尝试")
                    
                    if self.config.timeout:
                        result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
                    else:
                        result = await func(*args, **kwargs)
                    
                    return result
                    
                except Exception as e:
                    last_error = e
                    
                    if self.config.enable_logging:
                        logger.warning(f"异步任务 {task_id} 第 {attempt + 1} 次尝试失败: {e}")
                    
                    if attempt < self.config.retry_count:
                        await asyncio.sleep(self.config.retry_delay)
                    else:
                        raise e
            
            raise last_error
    
    async def _execute_sync_in_async(self, task_id: str, func: Callable, *args, **kwargs) -> Any:
        """在异步环境中执行同步函数"""
        async with self._semaphore:
            self._update_task_result(task_id, TaskStatus.RUNNING)
            
            loop = asyncio.get_event_loop()
            
            try:
                if self.config.timeout:
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, func, *args),
                        timeout=self.config.timeout
                    )
                else:
                    result = await loop.run_in_executor(None, func, *args)
                
                return result
                
            except Exception as e:
                raise e
    
    def _handle_async_task_completion(self, task_id: str, task: asyncio.Task):
        """处理异步任务完成"""
        try:
            if task.cancelled():
                self._update_task_result(task_id, TaskStatus.CANCELLED)
            elif task.exception():
                self._update_task_result(task_id, TaskStatus.FAILED, error=task.exception())
            else:
                self._update_task_result(task_id, TaskStatus.COMPLETED, result=task.result())
        except Exception as e:
            self._update_task_result(task_id, TaskStatus.FAILED, error=e)
        finally:
            # 清理任务引用
            with self._lock:
                self._async_tasks.pop(task_id, None)
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> TaskResult:
        """获取任务结果"""
        with self._lock:
            if task_id not in self._tasks:
                raise ValueError(f"任务 {task_id} 不存在")
            
            task_result = self._tasks[task_id]
            async_task = self._async_tasks.get(task_id)
        
        # 如果任务还在运行，等待完成
        if async_task and not async_task.done():
            try:
                self._ensure_loop()
                if self._loop.is_running():
                    # 如果循环正在运行，创建一个新的任务来等待
                    async def wait_task():
                        try:
                            await asyncio.wait_for(async_task, timeout=timeout or self.config.timeout)
                        except Exception:
                            pass
                    
                    # 在新线程中运行等待
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, wait_task())
                        future.result(timeout=timeout or self.config.timeout)
                else:
                    # 如果循环未运行，直接运行
                    async def wait_task():
                        try:
                            await asyncio.wait_for(async_task, timeout=timeout or self.config.timeout)
                        except Exception:
                            pass
                    
                    self._loop.run_until_complete(wait_task())
            except Exception:
                pass  # 错误已在回调中处理
        
        return task_result
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            async_task = self._async_tasks.get(task_id)
            if async_task:
                cancelled = async_task.cancel()
                if cancelled:
                    self._update_task_result(task_id, TaskStatus.CANCELLED)
                return cancelled
            return False
    
    def shutdown(self, wait: bool = True):
        """关闭处理器"""
        self._shutdown = True
        
        # 取消所有待处理的任务
        with self._lock:
            for task_id, async_task in list(self._async_tasks.items()):
                if not async_task.done():
                    async_task.cancel()
                    self._update_task_result(task_id, TaskStatus.CANCELLED)
        
        if self.config.enable_logging:
            logger.info("异步处理器已关闭")

class BatchProcessor:
    """批处理器"""
    
    def __init__(self, processor: ConcurrentProcessor, batch_size: int = 10):
        self.processor = processor
        self.batch_size = batch_size
        self._batch_queue = queue.Queue()
        self._processing_thread = None
        self._stop_event = threading.Event()
    
    def start(self):
        """启动批处理"""
        if self._processing_thread is None or not self._processing_thread.is_alive():
            self._stop_event.clear()
            self._processing_thread = threading.Thread(target=self._process_batches)
            self._processing_thread.start()
    
    def stop(self):
        """停止批处理"""
        self._stop_event.set()
        if self._processing_thread:
            self._processing_thread.join()
    
    def add_task(self, func: Callable, *args, **kwargs) -> str:
        """添加任务到批处理队列"""
        task_data = (func, args, kwargs)
        self._batch_queue.put(task_data)
        return self.processor._generate_task_id()
    
    def _process_batches(self):
        """处理批次"""
        batch = []
        
        while not self._stop_event.is_set():
            try:
                # 收集批次
                while len(batch) < self.batch_size and not self._stop_event.is_set():
                    try:
                        task_data = self._batch_queue.get(timeout=1.0)
                        batch.append(task_data)
                    except queue.Empty:
                        break
                
                # 处理批次
                if batch:
                    task_ids = self.processor.submit_batch(batch)
                    logger.info(f"批处理提交了 {len(task_ids)} 个任务")
                    batch.clear()
                
            except Exception as e:
                logger.error(f"批处理错误: {e}")

# 工厂函数
def create_thread_pool_processor(max_workers: int = 4, **kwargs) -> ThreadPoolProcessor:
    """创建线程池处理器"""
    config = ProcessingConfig(max_workers=max_workers, **kwargs)
    return ThreadPoolProcessor(config)

def create_async_processor(max_workers: int = 4, **kwargs) -> AsyncProcessor:
    """创建异步处理器"""
    config = ProcessingConfig(max_workers=max_workers, **kwargs)
    return AsyncProcessor(config)

def create_process_pool_processor(max_workers: int = None, **kwargs) -> ThreadPoolProcessor:
    """创建进程池处理器"""
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()
    
    config = ProcessingConfig(max_workers=max_workers, use_process_pool=True, **kwargs)
    return ThreadPoolProcessor(config)

# 装饰器
def concurrent_task(processor: ConcurrentProcessor, timeout: Optional[float] = None):
    """并发任务装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            task_id = processor.submit_task(func, *args, **kwargs)
            result = processor.get_result(task_id, timeout)
            
            if result.status == TaskStatus.COMPLETED:
                return result.result
            elif result.status == TaskStatus.FAILED:
                raise result.error
            else:
                raise RuntimeError(f"任务 {task_id} 状态异常: {result.status}")
        
        return wrapper
    return decorator

def async_task(processor: AsyncProcessor, timeout: Optional[float] = None):
    """异步任务装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            task_id = processor.submit_task(func, *args, **kwargs)
            result = processor.get_result(task_id, timeout)
            
            if result.status == TaskStatus.COMPLETED:
                return result.result
            elif result.status == TaskStatus.FAILED:
                raise result.error
            else:
                raise RuntimeError(f"任务 {task_id} 状态异常: {result.status}")
        
        return wrapper
    return decorator