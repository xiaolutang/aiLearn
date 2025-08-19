# -*- coding: utf-8 -*-
"""
分析服务模块

本模块实现了学习数据分析和统计功能，包括学习行为分析、成绩统计、效果评估等。
"""

import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

from .cache_service import CacheManager

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """分析类型"""
    LEARNING_BEHAVIOR = "learning_behavior"  # 学习行为分析
    PERFORMANCE_TREND = "performance_trend"  # 成绩趋势分析
    ENGAGEMENT_ANALYSIS = "engagement_analysis"  # 参与度分析
    KNOWLEDGE_MASTERY = "knowledge_mastery"  # 知识掌握度分析
    LEARNING_EFFICIENCY = "learning_efficiency"  # 学习效率分析
    COMPARATIVE_ANALYSIS = "comparative_analysis"  # 对比分析

class TimeGranularity(Enum):
    """时间粒度"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class MetricType(Enum):
    """指标类型"""
    SCORE = "score"  # 分数
    TIME_SPENT = "time_spent"  # 学习时间
    COMPLETION_RATE = "completion_rate"  # 完成率
    ACCURACY = "accuracy"  # 准确率
    ENGAGEMENT = "engagement"  # 参与度
    PROGRESS = "progress"  # 进度

@dataclass
class LearningSession:
    """学习会话"""
    session_id: str
    student_id: str
    subject: str
    start_time: datetime
    end_time: datetime
    duration: int  # 秒
    activities: List[Dict[str, Any]]
    score: Optional[float] = None
    completion_rate: float = 0.0
    engagement_score: float = 0.0
    
@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class AnalysisResult:
    """分析结果"""
    analysis_type: AnalysisType
    student_id: Optional[str]
    time_range: Tuple[datetime, datetime]
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    generated_at: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class AnalyticsService:
    """分析服务"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        
        # 分析阈值配置
        self.thresholds = {
            "low_engagement": 0.3,
            "high_engagement": 0.8,
            "low_performance": 0.6,
            "high_performance": 0.85,
            "significant_change": 0.15,
            "learning_efficiency_low": 0.4,
            "learning_efficiency_high": 0.8
        }
    
    async def analyze_learning_behavior(
        self,
        student_id: str,
        time_range: Tuple[datetime, datetime],
        granularity: TimeGranularity = TimeGranularity.DAILY
    ) -> AnalysisResult:
        """分析学习行为"""
        try:
            # 检查缓存
            cache_key = f"behavior_{student_id}_{time_range[0].date()}_{time_range[1].date()}_{granularity.value}"
            cached_result = await self.cache_manager.get("analytics", cache_key)
            if cached_result:
                return AnalysisResult(**cached_result)
            
            # 获取学习会话数据
            sessions = await self._get_learning_sessions(student_id, time_range)
            
            if not sessions:
                return self._create_empty_result(AnalysisType.LEARNING_BEHAVIOR, student_id, time_range)
            
            # 分析学习模式
            behavior_metrics = self._analyze_behavior_patterns(sessions, granularity)
            
            # 生成洞察和建议
            insights = self._generate_behavior_insights(behavior_metrics)
            recommendations = self._generate_behavior_recommendations(behavior_metrics)
            
            result = AnalysisResult(
                analysis_type=AnalysisType.LEARNING_BEHAVIOR,
                student_id=student_id,
                time_range=time_range,
                metrics=behavior_metrics,
                insights=insights,
                recommendations=recommendations,
                confidence_score=self._calculate_confidence_score(sessions),
                generated_at=datetime.now(),
                metadata={"granularity": granularity.value, "session_count": len(sessions)}
            )
            
            # 缓存结果
            await self.cache_manager.set("analytics", cache_key, asdict(result), 1800)
            
            return result
            
        except Exception as e:
            logger.error(f"Learning behavior analysis error: {str(e)}")
            raise
    
    async def analyze_performance_trend(
        self,
        student_id: str,
        subject: Optional[str],
        time_range: Tuple[datetime, datetime],
        granularity: TimeGranularity = TimeGranularity.WEEKLY
    ) -> AnalysisResult:
        """分析成绩趋势"""
        try:
            # 检查缓存
            cache_key = f"trend_{student_id}_{subject or 'all'}_{time_range[0].date()}_{time_range[1].date()}_{granularity.value}"
            cached_result = await self.cache_manager.get("analytics", cache_key)
            if cached_result:
                return AnalysisResult(**cached_result)
            
            # 获取性能数据
            performance_data = await self._get_performance_data(student_id, subject, time_range)
            
            if not performance_data:
                return self._create_empty_result(AnalysisType.PERFORMANCE_TREND, student_id, time_range)
            
            # 分析趋势
            trend_metrics = self._analyze_performance_trends(performance_data, granularity)
            
            # 生成洞察和建议
            insights = self._generate_trend_insights(trend_metrics)
            recommendations = self._generate_trend_recommendations(trend_metrics)
            
            result = AnalysisResult(
                analysis_type=AnalysisType.PERFORMANCE_TREND,
                student_id=student_id,
                time_range=time_range,
                metrics=trend_metrics,
                insights=insights,
                recommendations=recommendations,
                confidence_score=self._calculate_trend_confidence(performance_data),
                generated_at=datetime.now(),
                metadata={"subject": subject, "granularity": granularity.value}
            )
            
            # 缓存结果
            await self.cache_manager.set("analytics", cache_key, asdict(result), 1800)
            
            return result
            
        except Exception as e:
            logger.error(f"Performance trend analysis error: {str(e)}")
            raise
    
    async def analyze_class_engagement(
        self,
        class_id: str,
        time_range: Tuple[datetime, datetime]
    ) -> AnalysisResult:
        """分析班级参与度"""
        try:
            # 检查缓存
            cache_key = f"engagement_{class_id}_{time_range[0].date()}_{time_range[1].date()}"
            cached_result = await self.cache_manager.get("analytics", cache_key)
            if cached_result:
                return AnalysisResult(**cached_result)
            
            # 获取班级参与数据
            engagement_data = await self._get_class_engagement_data(class_id, time_range)
            
            if not engagement_data:
                return self._create_empty_result(AnalysisType.ENGAGEMENT_ANALYSIS, None, time_range)
            
            # 分析参与度
            engagement_metrics = self._analyze_engagement_patterns(engagement_data)
            
            # 生成洞察和建议
            insights = self._generate_engagement_insights(engagement_metrics)
            recommendations = self._generate_engagement_recommendations(engagement_metrics)
            
            result = AnalysisResult(
                analysis_type=AnalysisType.ENGAGEMENT_ANALYSIS,
                student_id=None,
                time_range=time_range,
                metrics=engagement_metrics,
                insights=insights,
                recommendations=recommendations,
                confidence_score=self._calculate_engagement_confidence(engagement_data),
                generated_at=datetime.now(),
                metadata={"class_id": class_id, "student_count": len(engagement_data)}
            )
            
            # 缓存结果
            await self.cache_manager.set("analytics", cache_key, asdict(result), 1800)
            
            return result
            
        except Exception as e:
            logger.error(f"Class engagement analysis error: {str(e)}")
            raise
    
    async def analyze_knowledge_mastery(
        self,
        student_id: str,
        subject: str,
        knowledge_points: List[str]
    ) -> AnalysisResult:
        """分析知识掌握度"""
        try:
            # 检查缓存
            cache_key = f"mastery_{student_id}_{subject}_{hash(str(knowledge_points))}"
            cached_result = await self.cache_manager.get("analytics", cache_key)
            if cached_result:
                return AnalysisResult(**cached_result)
            
            # 获取知识点掌握数据
            mastery_data = await self._get_knowledge_mastery_data(student_id, subject, knowledge_points)
            
            if not mastery_data:
                return self._create_empty_result(AnalysisType.KNOWLEDGE_MASTERY, student_id, 
                                               (datetime.now() - timedelta(days=30), datetime.now()))
            
            # 分析掌握度
            mastery_metrics = self._analyze_knowledge_mastery(mastery_data, knowledge_points)
            
            # 生成洞察和建议
            insights = self._generate_mastery_insights(mastery_metrics)
            recommendations = self._generate_mastery_recommendations(mastery_metrics)
            
            result = AnalysisResult(
                analysis_type=AnalysisType.KNOWLEDGE_MASTERY,
                student_id=student_id,
                time_range=(datetime.now() - timedelta(days=30), datetime.now()),
                metrics=mastery_metrics,
                insights=insights,
                recommendations=recommendations,
                confidence_score=self._calculate_mastery_confidence(mastery_data),
                generated_at=datetime.now(),
                metadata={"subject": subject, "knowledge_points": knowledge_points}
            )
            
            # 缓存结果
            await self.cache_manager.set("analytics", cache_key, asdict(result), 3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Knowledge mastery analysis error: {str(e)}")
            raise
    
    async def compare_student_performance(
        self,
        student_ids: List[str],
        subject: Optional[str],
        time_range: Tuple[datetime, datetime]
    ) -> AnalysisResult:
        """对比学生表现"""
        try:
            # 检查缓存
            cache_key = f"compare_{hash(str(student_ids))}_{subject or 'all'}_{time_range[0].date()}_{time_range[1].date()}"
            cached_result = await self.cache_manager.get("analytics", cache_key)
            if cached_result:
                return AnalysisResult(**cached_result)
            
            # 获取所有学生的表现数据
            comparison_data = {}
            for student_id in student_ids:
                performance_data = await self._get_performance_data(student_id, subject, time_range)
                comparison_data[student_id] = performance_data
            
            # 进行对比分析
            comparison_metrics = self._analyze_comparative_performance(comparison_data)
            
            # 生成洞察和建议
            insights = self._generate_comparison_insights(comparison_metrics)
            recommendations = self._generate_comparison_recommendations(comparison_metrics)
            
            result = AnalysisResult(
                analysis_type=AnalysisType.COMPARATIVE_ANALYSIS,
                student_id=None,
                time_range=time_range,
                metrics=comparison_metrics,
                insights=insights,
                recommendations=recommendations,
                confidence_score=self._calculate_comparison_confidence(comparison_data),
                generated_at=datetime.now(),
                metadata={"student_ids": student_ids, "subject": subject}
            )
            
            # 缓存结果
            await self.cache_manager.set("analytics", cache_key, asdict(result), 1800)
            
            return result
            
        except Exception as e:
            logger.error(f"Comparative analysis error: {str(e)}")
            raise
    
    async def generate_dashboard_metrics(
        self,
        user_id: str,
        user_role: str,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """生成仪表板指标"""
        try:
            # 检查缓存
            cache_key = f"dashboard_{user_id}_{user_role}_{time_range[0].date()}_{time_range[1].date()}"
            cached_metrics = await self.cache_manager.get("analytics", cache_key)
            if cached_metrics:
                return cached_metrics
            
            metrics = {}
            
            if user_role == "student":
                metrics = await self._generate_student_dashboard_metrics(user_id, time_range)
            elif user_role == "teacher":
                metrics = await self._generate_teacher_dashboard_metrics(user_id, time_range)
            elif user_role == "admin":
                metrics = await self._generate_admin_dashboard_metrics(time_range)
            
            # 缓存指标
            await self.cache_manager.set("analytics", cache_key, metrics, 900)  # 15分钟缓存
            
            return metrics
            
        except Exception as e:
            logger.error(f"Dashboard metrics generation error: {str(e)}")
            raise
    
    # 私有方法实现
    
    async def _get_learning_sessions(self, student_id: str, time_range: Tuple[datetime, datetime]) -> List[LearningSession]:
        """获取学习会话数据（模拟实现）"""
        # 这里应该从数据库获取真实数据
        sessions = []
        current_time = time_range[0]
        
        while current_time < time_range[1]:
            session = LearningSession(
                session_id=f"session_{current_time.timestamp()}",
                student_id=student_id,
                subject="数学",
                start_time=current_time,
                end_time=current_time + timedelta(minutes=45),
                duration=2700,  # 45分钟
                activities=[
                    {"type": "reading", "duration": 900},
                    {"type": "exercise", "duration": 1200},
                    {"type": "review", "duration": 600}
                ],
                score=75.5 + (current_time.day % 20),
                completion_rate=0.8 + (current_time.day % 10) * 0.02,
                engagement_score=0.6 + (current_time.day % 15) * 0.02
            )
            sessions.append(session)
            current_time += timedelta(days=1)
        
        return sessions
    
    async def _get_performance_data(self, student_id: str, subject: Optional[str], time_range: Tuple[datetime, datetime]) -> List[PerformanceMetric]:
        """获取性能数据（模拟实现）"""
        metrics = []
        current_time = time_range[0]
        
        while current_time < time_range[1]:
            # 模拟分数数据
            base_score = 70 + (current_time.day % 30)
            score_metric = PerformanceMetric(
                metric_type=MetricType.SCORE,
                value=base_score,
                timestamp=current_time,
                context={"subject": subject or "数学", "assessment_type": "quiz"}
            )
            metrics.append(score_metric)
            
            # 模拟学习时间数据
            time_metric = PerformanceMetric(
                metric_type=MetricType.TIME_SPENT,
                value=30 + (current_time.day % 60),
                timestamp=current_time,
                context={"subject": subject or "数学", "unit": "minutes"}
            )
            metrics.append(time_metric)
            
            current_time += timedelta(days=1)
        
        return metrics
    
    async def _get_class_engagement_data(self, class_id: str, time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """获取班级参与数据（模拟实现）"""
        engagement_data = []
        
        # 模拟30个学生的参与数据
        for i in range(30):
            student_data = {
                "student_id": f"student_{i+1}",
                "participation_rate": 0.4 + (i % 20) * 0.03,
                "question_count": i % 10 + 1,
                "answer_accuracy": 0.6 + (i % 15) * 0.02,
                "engagement_score": 0.5 + (i % 25) * 0.02,
                "attendance_rate": 0.8 + (i % 10) * 0.02
            }
            engagement_data.append(student_data)
        
        return engagement_data
    
    async def _get_knowledge_mastery_data(self, student_id: str, subject: str, knowledge_points: List[str]) -> Dict[str, Any]:
        """获取知识掌握数据（模拟实现）"""
        mastery_data = {}
        
        for i, point in enumerate(knowledge_points):
            mastery_data[point] = {
                "mastery_level": 0.3 + (i % 7) * 0.1,
                "practice_count": (i % 20) + 5,
                "correct_rate": 0.5 + (i % 10) * 0.05,
                "time_spent": (i % 30) + 10,  # 分钟
                "last_practiced": datetime.now() - timedelta(days=i % 7)
            }
        
        return mastery_data
    
    def _analyze_behavior_patterns(self, sessions: List[LearningSession], granularity: TimeGranularity) -> Dict[str, Any]:
        """分析行为模式"""
        if not sessions:
            return {}
        
        # 基本统计
        total_sessions = len(sessions)
        total_time = sum(session.duration for session in sessions)
        avg_session_duration = total_time / total_sessions
        
        # 学习时间分布
        time_distribution = self._analyze_time_distribution(sessions)
        
        # 参与度分析
        engagement_scores = [session.engagement_score for session in sessions]
        avg_engagement = statistics.mean(engagement_scores)
        
        # 完成率分析
        completion_rates = [session.completion_rate for session in sessions]
        avg_completion = statistics.mean(completion_rates)
        
        return {
            "total_sessions": total_sessions,
            "total_time_minutes": total_time / 60,
            "average_session_duration_minutes": avg_session_duration / 60,
            "average_engagement": avg_engagement,
            "average_completion_rate": avg_completion,
            "time_distribution": time_distribution,
            "consistency_score": self._calculate_consistency_score(sessions),
            "learning_velocity": self._calculate_learning_velocity(sessions)
        }
    
    def _analyze_time_distribution(self, sessions: List[LearningSession]) -> Dict[str, Any]:
        """分析时间分布"""
        hour_counts = defaultdict(int)
        weekday_counts = defaultdict(int)
        
        for session in sessions:
            hour_counts[session.start_time.hour] += 1
            weekday_counts[session.start_time.weekday()] += 1
        
        # 找出最活跃的时间段
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 0
        peak_weekday = max(weekday_counts.items(), key=lambda x: x[1])[0] if weekday_counts else 0
        
        return {
            "peak_hour": peak_hour,
            "peak_weekday": peak_weekday,
            "hour_distribution": dict(hour_counts),
            "weekday_distribution": dict(weekday_counts)
        }
    
    def _calculate_consistency_score(self, sessions: List[LearningSession]) -> float:
        """计算学习一致性分数"""
        if len(sessions) < 2:
            return 0.0
        
        # 计算会话间隔的标准差
        intervals = []
        for i in range(1, len(sessions)):
            interval = (sessions[i].start_time - sessions[i-1].start_time).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # 一致性分数：间隔越规律，分数越高
        std_dev = statistics.stdev(intervals) if len(intervals) > 1 else 0
        mean_interval = statistics.mean(intervals)
        
        # 归一化到0-1范围
        consistency = max(0, 1 - (std_dev / mean_interval)) if mean_interval > 0 else 0
        return min(1.0, consistency)
    
    def _calculate_learning_velocity(self, sessions: List[LearningSession]) -> float:
        """计算学习速度"""
        if not sessions:
            return 0.0
        
        # 基于完成率和时间的学习速度
        total_completion = sum(session.completion_rate for session in sessions)
        total_time_hours = sum(session.duration for session in sessions) / 3600
        
        return total_completion / total_time_hours if total_time_hours > 0 else 0
    
    def _analyze_performance_trends(self, performance_data: List[PerformanceMetric], granularity: TimeGranularity) -> Dict[str, Any]:
        """分析性能趋势"""
        if not performance_data:
            return {}
        
        # 按指标类型分组
        metrics_by_type = defaultdict(list)
        for metric in performance_data:
            metrics_by_type[metric.metric_type].append(metric)
        
        trends = {}
        
        for metric_type, metrics in metrics_by_type.items():
            if len(metrics) < 2:
                continue
            
            # 按时间排序
            metrics.sort(key=lambda x: x.timestamp)
            
            # 计算趋势
            values = [m.value for m in metrics]
            trend_direction = self._calculate_trend_direction(values)
            trend_strength = self._calculate_trend_strength(values)
            
            trends[metric_type.value] = {
                "direction": trend_direction,
                "strength": trend_strength,
                "current_value": values[-1],
                "change_rate": (values[-1] - values[0]) / values[0] if values[0] != 0 else 0,
                "volatility": statistics.stdev(values) if len(values) > 1 else 0
            }
        
        return trends
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_rate = (second_avg - first_avg) / first_avg if first_avg != 0 else 0
        
        if change_rate > 0.05:
            return "improving"
        elif change_rate < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """计算趋势强度"""
        if len(values) < 2:
            return 0.0
        
        # 使用线性回归的R²值作为趋势强度
        n = len(values)
        x = list(range(n))
        y = values
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # 计算R²
        y_pred = [slope * (x[i] - x_mean) + y_mean for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        return max(0, r_squared)
    
    def _analyze_engagement_patterns(self, engagement_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析参与度模式"""
        if not engagement_data:
            return {}
        
        # 基本统计
        participation_rates = [data["participation_rate"] for data in engagement_data]
        engagement_scores = [data["engagement_score"] for data in engagement_data]
        attendance_rates = [data["attendance_rate"] for data in engagement_data]
        
        # 分类学生
        high_engagement = len([score for score in engagement_scores if score > self.thresholds["high_engagement"]])
        low_engagement = len([score for score in engagement_scores if score < self.thresholds["low_engagement"]])
        
        return {
            "average_participation": statistics.mean(participation_rates),
            "average_engagement": statistics.mean(engagement_scores),
            "average_attendance": statistics.mean(attendance_rates),
            "high_engagement_count": high_engagement,
            "low_engagement_count": low_engagement,
            "engagement_distribution": self._calculate_distribution(engagement_scores),
            "participation_variance": statistics.variance(participation_rates) if len(participation_rates) > 1 else 0
        }
    
    def _calculate_distribution(self, values: List[float]) -> Dict[str, int]:
        """计算数值分布"""
        distribution = {"low": 0, "medium": 0, "high": 0}
        
        for value in values:
            if value < 0.4:
                distribution["low"] += 1
            elif value < 0.7:
                distribution["medium"] += 1
            else:
                distribution["high"] += 1
        
        return distribution
    
    def _analyze_knowledge_mastery(self, mastery_data: Dict[str, Any], knowledge_points: List[str]) -> Dict[str, Any]:
        """分析知识掌握度"""
        if not mastery_data:
            return {}
        
        mastery_levels = [data["mastery_level"] for data in mastery_data.values()]
        correct_rates = [data["correct_rate"] for data in mastery_data.values()]
        
        # 识别强项和弱项
        sorted_points = sorted(mastery_data.items(), key=lambda x: x[1]["mastery_level"], reverse=True)
        strengths = [point for point, data in sorted_points[:3] if data["mastery_level"] > 0.7]
        weaknesses = [point for point, data in sorted_points[-3:] if data["mastery_level"] < 0.5]
        
        return {
            "overall_mastery": statistics.mean(mastery_levels),
            "overall_accuracy": statistics.mean(correct_rates),
            "mastery_distribution": self._calculate_distribution(mastery_levels),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "knowledge_point_details": mastery_data
        }
    
    def _analyze_comparative_performance(self, comparison_data: Dict[str, List[PerformanceMetric]]) -> Dict[str, Any]:
        """分析对比表现"""
        if not comparison_data:
            return {}
        
        student_stats = {}
        
        for student_id, metrics in comparison_data.items():
            if not metrics:
                continue
            
            scores = [m.value for m in metrics if m.metric_type == MetricType.SCORE]
            if scores:
                student_stats[student_id] = {
                    "average_score": statistics.mean(scores),
                    "score_trend": self._calculate_trend_direction(scores),
                    "consistency": 1 - (statistics.stdev(scores) / statistics.mean(scores)) if statistics.mean(scores) > 0 else 0
                }
        
        if not student_stats:
            return {}
        
        # 排名和统计
        sorted_students = sorted(student_stats.items(), key=lambda x: x[1]["average_score"], reverse=True)
        
        return {
            "student_rankings": [(student_id, stats["average_score"]) for student_id, stats in sorted_students],
            "class_average": statistics.mean([stats["average_score"] for stats in student_stats.values()]),
            "performance_gap": max([stats["average_score"] for stats in student_stats.values()]) - min([stats["average_score"] for stats in student_stats.values()]),
            "improving_students": [student_id for student_id, stats in student_stats.items() if stats["score_trend"] == "improving"],
            "declining_students": [student_id for student_id, stats in student_stats.items() if stats["score_trend"] == "declining"]
        }
    
    # 洞察和建议生成方法
    
    def _generate_behavior_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """生成行为洞察"""
        insights = []
        
        avg_engagement = metrics.get("average_engagement", 0)
        consistency = metrics.get("consistency_score", 0)
        
        if avg_engagement > self.thresholds["high_engagement"]:
            insights.append("学生表现出很高的学习参与度")
        elif avg_engagement < self.thresholds["low_engagement"]:
            insights.append("学生的学习参与度较低，需要关注")
        
        if consistency > 0.7:
            insights.append("学生的学习习惯很规律")
        elif consistency < 0.3:
            insights.append("学生的学习时间不够规律")
        
        return insights
    
    def _generate_behavior_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """生成行为建议"""
        recommendations = []
        
        avg_engagement = metrics.get("average_engagement", 0)
        consistency = metrics.get("consistency_score", 0)
        
        if avg_engagement < self.thresholds["low_engagement"]:
            recommendations.append("建议增加互动性学习内容以提高参与度")
        
        if consistency < 0.3:
            recommendations.append("建议制定固定的学习时间表")
        
        return recommendations
    
    def _generate_trend_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """生成趋势洞察"""
        insights = []
        
        for metric_type, trend_data in metrics.items():
            direction = trend_data.get("direction", "stable")
            strength = trend_data.get("strength", 0)
            
            if direction == "improving" and strength > 0.5:
                insights.append(f"{metric_type}呈现明显的上升趋势")
            elif direction == "declining" and strength > 0.5:
                insights.append(f"{metric_type}呈现下降趋势，需要关注")
        
        return insights
    
    def _generate_trend_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """生成趋势建议"""
        recommendations = []
        
        for metric_type, trend_data in metrics.items():
            direction = trend_data.get("direction", "stable")
            
            if direction == "declining":
                recommendations.append(f"建议加强{metric_type}相关的练习")
            elif direction == "improving":
                recommendations.append(f"继续保持{metric_type}的良好趋势")
        
        return recommendations
    
    def _generate_engagement_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """生成参与度洞察"""
        insights = []
        
        avg_engagement = metrics.get("average_engagement", 0)
        low_engagement_count = metrics.get("low_engagement_count", 0)
        
        if avg_engagement > self.thresholds["high_engagement"]:
            insights.append("班级整体参与度很高")
        elif avg_engagement < self.thresholds["low_engagement"]:
            insights.append("班级整体参与度偏低")
        
        if low_engagement_count > 0:
            insights.append(f"有{low_engagement_count}名学生参与度较低")
        
        return insights
    
    def _generate_engagement_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """生成参与度建议"""
        recommendations = []
        
        low_engagement_count = metrics.get("low_engagement_count", 0)
        
        if low_engagement_count > 0:
            recommendations.append("建议对低参与度学生进行个别关注")
            recommendations.append("考虑调整教学方式以提高整体参与度")
        
        return recommendations
    
    def _generate_mastery_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """生成掌握度洞察"""
        insights = []
        
        overall_mastery = metrics.get("overall_mastery", 0)
        strengths = metrics.get("strengths", [])
        weaknesses = metrics.get("weaknesses", [])
        
        if overall_mastery > 0.8:
            insights.append("整体知识掌握度很好")
        elif overall_mastery < 0.5:
            insights.append("整体知识掌握度需要提高")
        
        if strengths:
            insights.append(f"在{', '.join(strengths)}方面表现突出")
        
        if weaknesses:
            insights.append(f"在{', '.join(weaknesses)}方面需要加强")
        
        return insights
    
    def _generate_mastery_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """生成掌握度建议"""
        recommendations = []
        
        weaknesses = metrics.get("weaknesses", [])
        
        if weaknesses:
            recommendations.append(f"建议重点复习{', '.join(weaknesses)}")
            recommendations.append("增加相关练习题的数量")
        
        return recommendations
    
    def _generate_comparison_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """生成对比洞察"""
        insights = []
        
        performance_gap = metrics.get("performance_gap", 0)
        improving_students = metrics.get("improving_students", [])
        declining_students = metrics.get("declining_students", [])
        
        if performance_gap > 20:
            insights.append("班级内学生表现差异较大")
        
        if improving_students:
            insights.append(f"有{len(improving_students)}名学生表现在改善")
        
        if declining_students:
            insights.append(f"有{len(declining_students)}名学生表现在下降")
        
        return insights
    
    def _generate_comparison_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """生成对比建议"""
        recommendations = []
        
        declining_students = metrics.get("declining_students", [])
        performance_gap = metrics.get("performance_gap", 0)
        
        if declining_students:
            recommendations.append("建议对表现下降的学生进行个别辅导")
        
        if performance_gap > 20:
            recommendations.append("建议实施分层教学以缩小差距")
        
        return recommendations
    
    # 置信度计算方法
    
    def _calculate_confidence_score(self, sessions: List[LearningSession]) -> float:
        """计算置信度分数"""
        if not sessions:
            return 0.0
        
        # 基于数据量和质量的置信度
        data_volume_score = min(1.0, len(sessions) / 30)  # 30个会话为满分
        data_quality_score = 1.0  # 假设数据质量良好
        
        return (data_volume_score + data_quality_score) / 2
    
    def _calculate_trend_confidence(self, performance_data: List[PerformanceMetric]) -> float:
        """计算趋势置信度"""
        if not performance_data:
            return 0.0
        
        return min(1.0, len(performance_data) / 20)  # 20个数据点为满分
    
    def _calculate_engagement_confidence(self, engagement_data: List[Dict[str, Any]]) -> float:
        """计算参与度置信度"""
        if not engagement_data:
            return 0.0
        
        return min(1.0, len(engagement_data) / 25)  # 25个学生为满分
    
    def _calculate_mastery_confidence(self, mastery_data: Dict[str, Any]) -> float:
        """计算掌握度置信度"""
        if not mastery_data:
            return 0.0
        
        return min(1.0, len(mastery_data) / 10)  # 10个知识点为满分
    
    def _calculate_comparison_confidence(self, comparison_data: Dict[str, List[PerformanceMetric]]) -> float:
        """计算对比置信度"""
        if not comparison_data:
            return 0.0
        
        total_data_points = sum(len(metrics) for metrics in comparison_data.values())
        return min(1.0, total_data_points / 100)  # 100个数据点为满分
    
    def _create_empty_result(self, analysis_type: AnalysisType, student_id: Optional[str], time_range: Tuple[datetime, datetime]) -> AnalysisResult:
        """创建空的分析结果"""
        return AnalysisResult(
            analysis_type=analysis_type,
            student_id=student_id,
            time_range=time_range,
            metrics={},
            insights=["暂无足够数据进行分析"],
            recommendations=["建议增加学习活动以获得更多数据"],
            confidence_score=0.0,
            generated_at=datetime.now()
        )
    
    # 仪表板指标生成方法
    
    async def _generate_student_dashboard_metrics(self, student_id: str, time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """生成学生仪表板指标"""
        # 获取学生数据
        sessions = await self._get_learning_sessions(student_id, time_range)
        performance_data = await self._get_performance_data(student_id, None, time_range)
        
        # 计算关键指标
        total_time = sum(session.duration for session in sessions) / 3600  # 小时
        avg_score = statistics.mean([m.value for m in performance_data if m.metric_type == MetricType.SCORE]) if performance_data else 0
        
        return {
            "total_learning_time": total_time,
            "average_score": avg_score,
            "completed_sessions": len(sessions),
            "current_streak": self._calculate_learning_streak(sessions),
            "progress_this_week": self._calculate_weekly_progress(sessions),
            "upcoming_deadlines": self._get_upcoming_deadlines(student_id)
        }
    
    async def _generate_teacher_dashboard_metrics(self, teacher_id: str, time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """生成教师仪表板指标"""
        # 模拟教师数据
        return {
            "total_students": 120,
            "active_classes": 5,
            "pending_assignments": 15,
            "average_class_performance": 78.5,
            "engagement_rate": 0.82,
            "recent_activities": self._get_recent_teacher_activities(teacher_id)
        }
    
    async def _generate_admin_dashboard_metrics(self, time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """生成管理员仪表板指标"""
        # 模拟管理员数据
        return {
            "total_users": 1500,
            "active_teachers": 45,
            "active_students": 1200,
            "system_usage": 0.75,
            "performance_overview": {
                "average_score": 76.8,
                "completion_rate": 0.89,
                "engagement_rate": 0.73
            }
        }
    
    def _calculate_learning_streak(self, sessions: List[LearningSession]) -> int:
        """计算学习连续天数"""
        if not sessions:
            return 0
        
        # 按日期排序
        sessions.sort(key=lambda x: x.start_time.date())
        
        # 计算连续天数
        streak = 1
        current_date = sessions[-1].start_time.date()
        
        for i in range(len(sessions) - 2, -1, -1):
            session_date = sessions[i].start_time.date()
            if (current_date - session_date).days == 1:
                streak += 1
                current_date = session_date
            else:
                break
        
        return streak
    
    def _calculate_weekly_progress(self, sessions: List[LearningSession]) -> float:
        """计算本周进度"""
        if not sessions:
            return 0.0
        
        # 获取本周的会话
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_sessions = [s for s in sessions if s.start_time >= week_start]
        
        if not week_sessions:
            return 0.0
        
        # 计算平均完成率
        return statistics.mean([s.completion_rate for s in week_sessions])
    
    def _get_upcoming_deadlines(self, student_id: str) -> List[Dict[str, Any]]:
        """获取即将到来的截止日期"""
        # 模拟数据
        return [
            {
                "assignment": "数学作业第5章",
                "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "subject": "数学"
            },
            {
                "assignment": "物理实验报告",
                "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "subject": "物理"
            }
        ]
    
    def _get_recent_teacher_activities(self, teacher_id: str) -> List[Dict[str, Any]]:
        """获取教师最近活动"""
        # 模拟数据
        return [
            {
                "type": "assignment_graded",
                "description": "批改了数学作业",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                "type": "class_created",
                "description": "创建了新的物理课程",
                "timestamp": (datetime.now() - timedelta(hours=5)).isoformat()
            }
        ]