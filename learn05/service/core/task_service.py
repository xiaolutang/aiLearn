# -*- coding: utf-8 -*-
"""
任务管理服务模块

本模块实现了异步任务处理功能，包括作业批改、报告生成等长时间运行的任务。
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading
import time

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"  # 超时

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class TaskType(Enum):
    """任务类型"""
    HOMEWORK_GRADING = "homework_grading"  # 作业批改
    BATCH_GRADING = "batch_grading"  # 批量批改
    REPORT_GENERATION = "report_generation"  # 报告生成
    DATA_ANALYSIS = "data_analysis"  # 数据分析
    FILE_PROCESSING = "file_processing"  # 文件处理
    AI_TRAINING = "ai_training"  # AI训练
    SYSTEM_MAINTENANCE = "system_maintenance"  # 系统维护

@dataclass
class TaskResult:
    """任务结果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Task:
    """任务定义"""
    id: str
    type: TaskType
    name: str
    func: Callable
    args: tuple = ()
    kwargs: Dict[str, Any] = None
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[int] = None  # 超时时间（秒）
    retry_count: int = 0  # 重试次数
    max_retries: int = 3  # 最大重试次数
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    progress: float = 0.0  # 进度百分比
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 处理不能序列化的字段
        data.pop('func', None)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        if self.result:
            data['result'] = self.result.to_dict()
        return data

class TaskQueue:
    """任务队列"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queue = asyncio.PriorityQueue(maxsize=max_size)
        self._tasks = {}  # task_id -> Task
        self._lock = asyncio.Lock()
    
    async def put(self, task: Task) -> bool:
        """添加任务到队列"""
        try:
            async with self._lock:
                if len(self._tasks) >= self.max_size:
                    return False
                
                # 优先级队列：数字越小优先级越高
                priority = -task.priority.value
                await self._queue.put((priority, task.created_at.timestamp(), task))
                self._tasks[task.id] = task
                return True
        except Exception as e:
            logger.error(f"Failed to add task to queue: {str(e)}")
            return False
    
    async def get(self) -> Optional[Task]:
        """从队列获取任务"""
        try:
            _, _, task = await self._queue.get()
            return task
        except Exception as e:
            logger.error(f"Failed to get task from queue: {str(e)}")
            return None
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        async with self._lock:
            return self._tasks.get(task_id)
    
    async def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False
    
    async def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        async with self._lock:
            return list(self._tasks.values())
    
    async def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """根据状态获取任务"""
        async with self._lock:
            return [task for task in self._tasks.values() if task.status == status]
    
    def qsize(self) -> int:
        """队列大小"""
        return self._queue.qsize()
    
    def task_count(self) -> int:
        """任务总数"""
        return len(self._tasks)

class TaskWorker:
    """任务执行器"""
    
    def __init__(self, worker_id: str, task_queue: TaskQueue):
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.is_running = False
        self.current_task: Optional[Task] = None
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"worker-{worker_id}")
    
    async def start(self):
        """启动工作器"""
        self.is_running = True
        logger.info(f"Task worker {self.worker_id} started")
        
        while self.is_running:
            try:
                # 获取任务
                task = await self.task_queue.get()
                if task is None:
                    await asyncio.sleep(0.1)
                    continue
                
                self.current_task = task
                await self._execute_task(task)
                self.current_task = None
                
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {str(e)}")
                await asyncio.sleep(1)
    
    async def stop(self):
        """停止工作器"""
        self.is_running = False
        if self.current_task:
            self.current_task.status = TaskStatus.CANCELLED
        self.executor.shutdown(wait=True)
        logger.info(f"Task worker {self.worker_id} stopped")
    
    async def _execute_task(self, task: Task):
        """执行任务"""
        start_time = time.time()
        
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            logger.info(f"Worker {self.worker_id} executing task {task.id} ({task.name})")
            
            # 执行任务
            if asyncio.iscoroutinefunction(task.func):
                # 异步函数
                if task.timeout:
                    result = await asyncio.wait_for(
                        task.func(*task.args, **task.kwargs),
                        timeout=task.timeout
                    )
                else:
                    result = await task.func(*task.args, **task.kwargs)
            else:
                # 同步函数，在线程池中执行
                loop = asyncio.get_event_loop()
                if task.timeout:
                    result = await asyncio.wait_for(
                        loop.run_in_executor(
                            self.executor,
                            lambda: task.func(*task.args, **task.kwargs)
                        ),
                        timeout=task.timeout
                    )
                else:
                    result = await loop.run_in_executor(
                        self.executor,
                        lambda: task.func(*task.args, **task.kwargs)
                    )
            
            # 任务成功完成
            execution_time = time.time() - start_time
            task.result = TaskResult(
                success=True,
                data=result if isinstance(result, dict) else {"result": result},
                execution_time=execution_time
            )
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 100.0
            
            logger.info(f"Task {task.id} completed in {execution_time:.2f}s")
            
        except asyncio.TimeoutError:
            # 任务超时
            task.status = TaskStatus.TIMEOUT
            task.result = TaskResult(
                success=False,
                error=f"Task timeout after {task.timeout} seconds",
                execution_time=time.time() - start_time
            )
            task.completed_at = datetime.now()
            logger.warning(f"Task {task.id} timeout")
            
        except Exception as e:
            # 任务执行失败
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            task.result = TaskResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            
            # 检查是否需要重试
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                
                # 重新加入队列
                await self.task_queue.put(task)
                logger.info(f"Task {task.id} failed, retrying ({task.retry_count}/{task.max_retries})")
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                logger.error(f"Task {task.id} failed permanently: {error_msg}")

class TaskManager:
    """任务管理器"""
    
    def __init__(self, max_workers: int = 4, queue_size: int = 1000):
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.task_queue = TaskQueue(max_size=queue_size)
        self.workers: List[TaskWorker] = []
        self.is_running = False
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """启动任务管理器"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 创建并启动工作器
        for i in range(self.max_workers):
            worker = TaskWorker(f"worker-{i}", self.task_queue)
            self.workers.append(worker)
            asyncio.create_task(worker.start())
        
        # 启动清理任务
        self._cleanup_task = asyncio.create_task(self._cleanup_completed_tasks())
        
        logger.info(f"Task manager started with {self.max_workers} workers")
    
    async def stop(self):
        """停止任务管理器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 停止所有工作器
        for worker in self.workers:
            await worker.stop()
        
        # 停止清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Task manager stopped")
    
    async def submit_task(
        self,
        task_type: TaskType,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            type=task_type,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            metadata=metadata or {}
        )
        
        success = await self.task_queue.put(task)
        if not success:
            raise Exception("Task queue is full")
        
        logger.info(f"Task {task_id} ({name}) submitted")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = await self.task_queue.get_task(task_id)
        if task:
            return task.to_dict()
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = await self.task_queue.get_task(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            return True
        return False
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        all_tasks = await self.task_queue.get_all_tasks()
        
        stats = {
            "total_tasks": len(all_tasks),
            "queue_size": self.task_queue.qsize(),
            "max_queue_size": self.queue_size,
            "active_workers": len([w for w in self.workers if w.current_task]),
            "total_workers": len(self.workers),
            "status_counts": {},
            "type_counts": {},
            "priority_counts": {}
        }
        
        # 统计各状态任务数量
        for status in TaskStatus:
            count = len([t for t in all_tasks if t.status == status])
            stats["status_counts"][status.value] = count
        
        # 统计各类型任务数量
        for task_type in TaskType:
            count = len([t for t in all_tasks if t.type == task_type])
            stats["type_counts"][task_type.value] = count
        
        # 统计各优先级任务数量
        for priority in TaskPriority:
            count = len([t for t in all_tasks if t.priority == priority])
            stats["priority_counts"][priority.value] = count
        
        return stats
    
    async def get_tasks_by_type(self, task_type: TaskType) -> List[Dict[str, Any]]:
        """根据类型获取任务"""
        all_tasks = await self.task_queue.get_all_tasks()
        filtered_tasks = [t for t in all_tasks if t.type == task_type]
        return [task.to_dict() for task in filtered_tasks]
    
    async def get_tasks_by_status(self, status: TaskStatus) -> List[Dict[str, Any]]:
        """根据状态获取任务"""
        tasks = await self.task_queue.get_tasks_by_status(status)
        return [task.to_dict() for task in tasks]
    
    async def _cleanup_completed_tasks(self):
        """清理已完成的任务"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                
                all_tasks = await self.task_queue.get_all_tasks()
                cutoff_time = datetime.now() - timedelta(hours=24)  # 保留24小时内的任务
                
                cleanup_count = 0
                for task in all_tasks:
                    if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                        task.completed_at and task.completed_at < cutoff_time):
                        await self.task_queue.remove_task(task.id)
                        cleanup_count += 1
                
                if cleanup_count > 0:
                    logger.info(f"Cleaned up {cleanup_count} old tasks")
                    
            except Exception as e:
                logger.error(f"Task cleanup error: {str(e)}")
                await asyncio.sleep(60)

# 全局任务管理器实例
task_manager = None

def get_task_manager() -> TaskManager:
    """获取全局任务管理器实例"""
    global task_manager
    if task_manager is None:
        task_manager = TaskManager()
    return task_manager

async def init_task_manager(max_workers: int = 4, queue_size: int = 1000) -> TaskManager:
    """初始化任务管理器"""
    global task_manager
    task_manager = TaskManager(max_workers, queue_size)
    await task_manager.start()
    return task_manager

async def close_task_manager():
    """关闭任务管理器"""
    global task_manager
    if task_manager:
        await task_manager.stop()
        task_manager = None

# 常用任务函数
async def batch_grade_homework(homework_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """批量批改作业任务"""
    results = []
    for homework_data in homework_batch:
        # 模拟批改过程
        await asyncio.sleep(0.1)  # 模拟处理时间
        results.append({
            'submission_id': homework_data.get('student_id', 'unknown'),
            'status': 'completed',
            'score': 85.5,
            'feedback': '作业完成质量良好，建议加强基础概念理解。'
        })
    
    return {
        'status': 'completed',
        'total_processed': len(homework_batch),
        'results': results,
        'summary': {
            'average_score': sum(r['score'] for r in results) / len(results),
            'completion_rate': 100.0
        }
    }

async def generate_teaching_report(teacher_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
    """生成教学报告任务"""
    # 模拟报告生成过程
    await asyncio.sleep(2)  # 模拟处理时间
    
    report_data = {
        'teacher_id': teacher_id,
        'date_range': date_range,
        'report_url': f'/reports/{teacher_id}_{datetime.now().strftime("%Y%m%d")}.pdf',
        'statistics': {
            'total_classes': 15,
            'total_students': 450,
            'average_attendance': 92.5,
            'average_score': 78.3
        },
        'generated_at': datetime.now().isoformat()
    }
    
    return {
        'status': 'completed',
        'report_data': report_data
    }

def analyze_student_performance(student_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析学生表现任务（同步函数示例）"""
    # 模拟数据分析
    time.sleep(1)  # 模拟处理时间
    
    total_students = len(student_data)
    if total_students == 0:
        return {'status': 'no_data'}
    
    scores = [s.get('score', 0) for s in student_data]
    
    analysis = {
        'total_students': total_students,
        'average_score': sum(scores) / len(scores),
        'max_score': max(scores),
        'min_score': min(scores),
        'pass_rate': len([s for s in scores if s >= 60]) / len(scores) * 100,
        'grade_distribution': {
            'A': len([s for s in scores if s >= 90]),
            'B': len([s for s in scores if 80 <= s < 90]),
            'C': len([s for s in scores if 70 <= s < 80]),
            'D': len([s for s in scores if 60 <= s < 70]),
            'F': len([s for s in scores if s < 60])
        }
    }
    
    return {
        'status': 'completed',
        'analysis': analysis
    }