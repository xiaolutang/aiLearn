# -*- coding: utf-8 -*-
"""
通知系统模块
提供消息通知和提醒功能
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from .database import get_db, Notification, User, Student


class NotificationManager:
    """通知管理器"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def create_notification(self, user_id: int, title: str, content: str, notification_type: str = "info", priority: str = "normal", related_id: int = None, related_type: str = None) -> Notification:
        """创建通知"""
        # 验证用户是否存在
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        # 创建通知记录
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type,
            priority=priority,
            is_read=False,
            created_at=datetime.now(),
            related_id=related_id,
            related_type=related_type
        )
        
        # 保存到数据库
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def get_notifications(self, user_id: int, limit: int = 20, offset: int = 0, is_read: Optional[bool] = None, notification_type: Optional[str] = None) -> List[Notification]:
        """获取用户的通知列表"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        # 筛选条件
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        
        # 按创建时间倒序排列
        notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
        
        return notifications
    
    def get_notification(self, notification_id: int) -> Optional[Notification]:
        """获取单条通知详情"""
        return self.db.query(Notification).filter(Notification.id == notification_id).first()
    
    def update_notification(self, notification_id: int, is_read: Optional[bool] = None, title: Optional[str] = None, content: Optional[str] = None) -> Optional[Notification]:
        """更新通知"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            return None
        
        if is_read is not None:
            notification.is_read = is_read
        if title:
            notification.title = title
        if content:
            notification.content = content
        
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def delete_notification(self, notification_id: int) -> bool:
        """删除通知"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            return False
        
        self.db.delete(notification)
        self.db.commit()
        
        return True
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """将用户的所有通知标记为已读"""
        notifications = self.db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).all()
        for notification in notifications:
            notification.is_read = True
        
        self.db.commit()
        
        return True
    
    def batch_create_notifications(self, user_ids: List[int], title: str, content: str, notification_type: str = "system", priority: str = "normal", related_id: int = None, related_type: str = None) -> List[Notification]:
        """批量创建通知"""
        notifications = []
        
        for user_id in user_ids:
            try:
                notification = self.create_notification(
                    user_id=user_id,
                    title=title,
                    content=content,
                    notification_type=notification_type,
                    priority=priority,
                    related_id=related_id,
                    related_type=related_type
                )
                notifications.append(notification)
            except Exception as e:
                print(f"发送通知给用户 {user_id} 失败: {str(e)}")
        
        return notifications


class ReminderManager:
    """提醒管理器"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.notification_manager = NotificationManager(db)
    
    def create_reminder(self, user_id: int, title: str, content: str, reminder_time: datetime, reminder_type: str = "task", priority: str = "normal", related_id: int = None, related_type: str = None) -> Dict[str, Any]:
        """创建提醒"""
        # 计算提醒提前时间（默认为15分钟）
        提前_minutes = 15
        notification_time = reminder_time - timedelta(minutes=提前_minutes)
        
        # 创建提醒数据（实际项目中可能需要存储提醒配置）
        reminder_data = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "reminder_time": reminder_time.isoformat(),
            "notification_time": notification_time.isoformat(),
            "reminder_type": reminder_type,
            "priority": priority,
            "related_id": related_id,
            "related_type": related_type,
            "created_at": datetime.now().isoformat()
        }
        
        # 这里可以实现定时任务调度，在指定时间发送通知
        # 目前仅作为示例，实际项目中需要使用定时任务系统
        print(f"创建提醒: {title} 在 {reminder_time} 提醒用户 {user_id}")
        
        # 可以在这里使用任务调度系统，如APScheduler等
        # 例如：schedule_reminder(reminder_data)
        
        return reminder_data
    
    def send_grade_reminder(self, student_id: int, subject_id: int, exam_date: str) -> Optional[Notification]:
        """发送成绩提醒"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return None
        
        # 这里假设学生的用户ID是学生ID（实际项目中可能需要不同的映射关系）
        user_id = student_id  # 假设学生ID和用户ID相同
        
        # 创建成绩提醒通知
        notification = self.notification_manager.create_notification(
            user_id=user_id,
            title="成绩已发布",
            content=f"您的{exam_date}考试成绩已发布，请及时查看。",
            notification_type="grade",
            priority="normal",
            related_id=subject_id,
            related_type="subject"
        )
        
        return notification
    
    def send_plan_reminder(self, student_id: int, plan_id: int, reminder_time: datetime) -> Dict[str, Any]:
        """发送辅导计划提醒"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise ValueError(f"学生不存在: {student_id}")
        
        # 这里假设学生的用户ID是学生ID（实际项目中可能需要不同的映射关系）
        user_id = student_id  # 假设学生ID和用户ID相同
        
        # 创建辅导计划提醒
        reminder_data = self.create_reminder(
            user_id=user_id,
            title="辅导计划提醒",
            content="您有一个辅导计划即将开始，请做好准备。",
            reminder_time=reminder_time,
            reminder_type="plan",
            priority="normal",
            related_id=plan_id,
            related_type="plan"
        )
        
        return reminder_data
    
    def send_progress_reminder(self, student_id: int, plan_id: int, progress: float) -> Optional[Notification]:
        """发送学习进度提醒"""
        # 获取学生信息
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return None
        
        # 这里假设学生的用户ID是学生ID（实际项目中可能需要不同的映射关系）
        user_id = student_id  # 假设学生ID和用户ID相同
        
        # 根据进度生成不同的提醒内容
        if progress < 30:
            content = "您的学习计划进度较慢，请加油！"
            priority = "warning"
        elif progress < 70:
            content = f"您的学习计划已完成{progress}%，继续保持！"
            priority = "normal"
        else:
            content = f"您的学习计划已完成{progress}%，即将完成，太棒了！"
            priority = "info"
        
        # 创建学习进度提醒通知
        notification = self.notification_manager.create_notification(
            user_id=user_id,
            title="学习进度提醒",
            content=content,
            notification_type="progress",
            priority=priority,
            related_id=plan_id,
            related_type="plan"
        )
        
        return notification


# 便捷函数

def send_system_notification(user_id: int, title: str, content: str, priority: str = "normal") -> Notification:
    """发送系统通知"""
    manager = NotificationManager()
    return manager.create_notification(
        user_id=user_id,
        title=title,
        content=content,
        notification_type="system",
        priority=priority
    )

def send_class_notification(class_id: int, title: str, content: str, priority: str = "normal") -> List[Notification]:
    """发送班级通知"""
    db = next(get_db())
    # 查询班级中的所有学生
    students = db.query(Student).filter(Student.class_id == class_id).all()
    user_ids = [student.student_id for student in students]  # 假设学生ID和用户ID相同
    
    manager = NotificationManager(db)
    return manager.batch_create_notifications(
        user_ids=user_ids,
        title=title,
        content=content,
        notification_type="class",
        priority=priority,
        related_id=class_id,
        related_type="class"
    )

def get_unread_notifications(user_id: int, limit: int = 20) -> List[Notification]:
    """获取未读通知列表"""
    manager = NotificationManager()
    return manager.get_notifications(
        user_id=user_id,
        limit=limit,
        is_read=False
    )

def get_all_notifications(user_id: int, limit: int = 20, offset: int = 0) -> List[Notification]:
    """获取所有通知列表"""
    manager = NotificationManager()
    return manager.get_notifications(
        user_id=user_id,
        limit=limit,
        offset=offset
    )

def mark_notification_as_read(notification_id: int) -> Optional[Notification]:
    """将通知标记为已读"""
    manager = NotificationManager()
    return manager.update_notification(
        notification_id=notification_id,
        is_read=True
    )


def schedule_grade_reminders(exam_date: str, subject_ids: List[int] = None) -> List[Dict[str, Any]]:
    """批量调度成绩提醒"""
    db = next(get_db())
    reminders = []
    
    # 获取所有学生
    students = db.query(Student).all()
    
    # 如果没有指定科目ID，获取所有科目
    if not subject_ids:
        from database import Subject
        subjects = db.query(Subject).all()
        subject_ids = [subject.subject_id for subject in subjects]
    
    # 为每个学生创建提醒
    manager = ReminderManager(db)
    for student in students:
        for subject_id in subject_ids:
            try:
                # 创建成绩提醒，设置提醒时间为当前时间
                reminder = manager.send_grade_reminder(
                    student_id=student.student_id,
                    subject_id=subject_id,
                    exam_date=exam_date
                )
                reminders.append({
                    "student_id": student.student_id,
                    "subject_id": subject_id,
                    "notification_id": reminder.id if reminder else None,
                    "status": "success" if reminder else "failed"
                })
            except Exception as e:
                reminders.append({
                    "student_id": student.student_id,
                    "subject_id": subject_id,
                    "status": "failed",
                    "error": str(e)
                })
    
    return reminders