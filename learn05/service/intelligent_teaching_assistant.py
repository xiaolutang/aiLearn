# 智能教学助手模块，运用设计模式实现高内聚、低耦合
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
import sqlite3
import os
import logging
import bcrypt
import jwt
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(title="智能教学助手 API", description="智能教学助手后端API接口", version="1.0.0")

# 配置CORS中间件解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///student_database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 大模型配置
llm_config = {
    "model": os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
    "api_key": os.getenv('LLM_API_KEY', os.getenv('OPENAI_API_KEY')),
    "temperature": 0.1
}

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 抽象基类：语言模型接口，使用策略模式
class LLMInterface(ABC):
    @abstractmethod
    def generate_sql_and_response(self, question: str, context: str = "") -> Dict[str, str]:
        """
        根据自然语言问题生成SQL查询语句和对应的回答
        :param question: 自然语言问题
        :param context: 额外的上下文信息
        :return: 包含SQL查询语句和回答的字典
        """
        pass

# 具体语言模型实现类，使用策略模式
class SampleLLM(LLMInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_sql_and_response(self, question: str, context: str = "") -> Dict[str, str]:
        """
        示例实现，实际使用时需替换为真实API调用
        """
        # 根据常见查询类型提供模拟SQL
        if '成绩' in question and '数学' in question:
            sql_query = "SELECT s.student_name, g.score FROM grades g JOIN students s ON g.student_id = s.student_id JOIN subjects sub ON g.subject_id = sub.subject_id WHERE sub.subject_name = '数学' ORDER BY g.score DESC"
            response = "模拟数据显示学生的数学成绩情况"
        elif '成绩' in question:
            sql_query = "SELECT s.student_name, AVG(g.score) as average_score FROM grades g JOIN students s ON g.student_id = s.student_id GROUP BY s.student_name ORDER BY average_score DESC"
            response = "模拟数据显示学生的平均成绩排名"
        elif '出勤' in question:
            sql_query = "SELECT student_name, attendance_rate FROM students ORDER BY attendance_rate DESC"
            response = "模拟数据显示学生的出勤率情况"
        else:
            sql_query = "SELECT * FROM students LIMIT 10"
            response = "模拟数据显示学生基本信息"
        
        return {
            "sql_query": sql_query,
            "response": response
        }

# 抽象基类：数据库执行器接口，使用策略模式
class DatabaseExecutorInterface(ABC):
    @abstractmethod
    def execute_query(self, sql_query: str) -> Optional[List[tuple]]:
        """
        执行SQL查询并返回结果
        :param sql_query: SQL查询语句
        :return: 查询结果列表
        """
        pass

    @abstractmethod
    def close(self):
        """
        关闭数据库连接
        """
        pass

# 具体数据库执行器实现类，使用策略模式
class SQLiteExecutor(DatabaseExecutorInterface):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)

    def execute_query(self, sql_query: str) -> Optional[List[tuple]]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"执行查询时出错: {e}")
            return None

    def close(self):
        self.conn.close()

# 命令模式：处理用户问题的命令基类
class Command(ABC):
    @abstractmethod
    def execute(self, question: str, context: str = "") -> str:
        pass

# 具体命令类：处理教学助手问题
class TeachingAssistantCommand(Command):
    def __init__(self, llm: LLMInterface, db_executor: DatabaseExecutorInterface):
        self.llm = llm
        self.db_executor = db_executor

    def execute(self, question: str, context: str = "") -> str:
        result = self.llm.generate_sql_and_response(question, context)
        sql_query = result["sql_query"]
        response = result["response"]

        query_results = self.db_executor.execute_query(sql_query)
        if query_results:
            response += "\n以下是查询到的数据："
            for row in query_results:
                response += f"\n{row}"
        return response

# 数据模型定义
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    related_id = Column(Integer)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Student(Base):
    __tablename__ = "students"
    student_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    class_id = Column(Integer, ForeignKey('classes.class_id'))
    entrance_date = Column(DateTime)
    contact_info = Column(String)

class Class(Base):
    __tablename__ = "classes"
    class_id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String)
    grade = Column(Integer)
    head_teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'))

class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(Integer, primary_key=True, index=True)
    teacher_name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))

class Subject(Base):
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String)
    description = Column(String)

class Grade(Base):
    __tablename__ = "grades"
    grade_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    score = Column(Float)
    exam_date = Column(DateTime)
    exam_type = Column(String)

class TutoringPlan(Base):
    __tablename__ = "tutoring_plans"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    plan_content = Column(Text)
    resources = Column(Text)
    progress = Column(Integer, default=0)
    effect_evaluation = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Pydantic模型定义
class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    related_id: Optional[int] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class GradeCreate(BaseModel):
    student_id: int
    subject_id: int
    score: float
    exam_date: datetime
    exam_type: str

class GradeUpdate(BaseModel):
    score: Optional[float] = None
    exam_type: Optional[str] = None

# 认证相关功能
def get_password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request, db: SessionLocal = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = request.headers.get("Authorization")
        if token is None:
            raise credentials_exception
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# 用户认证接口
@app.post("/api/auth/register", response_model=Dict)
def register(user: UserCreate, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password=hashed_password,
        role=user.role,
        related_id=user.related_id,
        email=user.email,
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"code": 0, "message": "注册成功", "data": {"user_id": db_user.id}}

@app.post("/api/auth/login", response_model=Token)
def login(user: UserLogin, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role, "related_id": db_user.related_id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=Dict)
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"code": 0, "message": "成功", "data": {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "related_id": current_user.related_id,
        "email": current_user.email,
        "phone_number": current_user.phone_number
    }}

# 成绩管理接口
@app.get("/api/grades", response_model=Dict)
def get_grades(student_id: Optional[int] = None, subject_id: Optional[int] = None,
               start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
               page: int = 1, page_size: int = 10, db: SessionLocal = Depends(get_db)):
    query = db.query(Grade)
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    if start_date:
        query = query.filter(Grade.exam_date >= start_date)
    if end_date:
        query = query.filter(Grade.exam_date <= end_date)
    total = query.count()
    grades = query.offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for grade in grades:
        result.append({
            "grade_id": grade.grade_id,
            "student_id": grade.student_id,
            "subject_id": grade.subject_id,
            "score": grade.score,
            "exam_date": grade.exam_date,
            "exam_type": grade.exam_type
        })
    
    return {"code": 0, "message": "成功", "data": {
        "grades": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }}

@app.post("/api/grades", response_model=Dict)
def create_grade(grade: GradeCreate, db: SessionLocal = Depends(get_db)):
    db_grade = Grade(
        student_id=grade.student_id,
        subject_id=grade.subject_id,
        score=grade.score,
        exam_date=grade.exam_date,
        exam_type=grade.exam_type
    )
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return {"code": 0, "message": "创建成功", "data": {"grade_id": db_grade.grade_id}}

@app.post("/api/grades/batch-import", response_model=Dict)
async def batch_import_grades(file: UploadFile = File(...), db: SessionLocal = Depends(get_db)):
    try:
        # 读取Excel文件
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        
        # 数据校验和处理
        required_columns = ['student_id', 'subject_id', 'score', 'exam_date', 'exam_type']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"缺少必要的列: {col}")
        
        # 导入数据
        success_count = 0
        error_count = 0
        for _, row in df.iterrows():
            try:
                db_grade = Grade(
                    student_id=int(row['student_id']),
                    subject_id=int(row['subject_id']),
                    score=float(row['score']),
                    exam_date=pd.to_datetime(row['exam_date']),
                    exam_type=str(row['exam_type'])
                )
                db.add(db_grade)
                success_count += 1
            except Exception as e:
                logger.error(f"导入行数据失败: {e}")
                error_count += 1
        
        db.commit()
        return {"code": 0, "message": "批量导入完成", "data": {
            "total": len(df),
            "success": success_count,
            "error": error_count
        }}
    except Exception as e:
        logger.error(f"批量导入成绩失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")

@app.get("/api/grades/analysis/class/{class_id}", response_model=Dict)
def get_class_grade_analysis(class_id: int, subject_id: Optional[int] = None, 
                             start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                             db: SessionLocal = Depends(get_db)):
    try:
        # 获取班级学生
        students = db.query(Student).filter(Student.class_id == class_id).all()
        if not students:
            raise HTTPException(status_code=404, detail="班级不存在或没有学生")
        
        # 构建查询
        query = db.query(Grade)
        query = query.join(Student, Grade.student_id == Student.student_id)
        query = query.filter(Student.class_id == class_id)
        
        if subject_id:
            query = query.filter(Grade.subject_id == subject_id)
        if start_date:
            query = query.filter(Grade.exam_date >= start_date)
        if end_date:
            query = query.filter(Grade.exam_date <= end_date)
        
        # 执行查询
        grades = query.all()
        if not grades:
            return {"code": 0, "message": "没有找到成绩数据", "data": {}}
        
        # 计算统计数据
        scores = [grade.score for grade in grades]
        mean_score = np.mean(scores)
        median_score = np.median(scores)
        max_score = np.max(scores)
        min_score = np.min(scores)
        std_score = np.std(scores)
        
        # 计算各分数段分布
        score_ranges = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 101)]
        distribution = {}
        for start, end in score_ranges:
            count = len([s for s in scores if start <= s < end])
            distribution[f"{start}-{end-1}"] = count
        
        return {"code": 0, "message": "成功", "data": {
            "class_id": class_id,
            "student_count": len(students),
            "record_count": len(grades),
            "mean_score": round(mean_score, 2),
            "median_score": round(median_score, 2),
            "max_score": round(max_score, 2),
            "min_score": round(min_score, 2),
            "std_score": round(std_score, 2),
            "distribution": distribution
        }}
    except Exception as e:
        logger.error(f"班级成绩分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.get("/api/grades/analysis/student/{student_id}", response_model=Dict)
def get_student_grade_analysis(student_id: int, subject_id: Optional[int] = None, 
                               start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                               db: SessionLocal = Depends(get_db)):
    try:
        # 检查学生是否存在
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        
        # 构建查询
        query = db.query(Grade).filter(Grade.student_id == student_id)
        
        if subject_id:
            query = query.filter(Grade.subject_id == subject_id)
        if start_date:
            query = query.filter(Grade.exam_date >= start_date)
        if end_date:
            query = query.filter(Grade.exam_date <= end_date)
        
        # 按考试日期排序
        query = query.order_by(Grade.exam_date)
        
        # 执行查询
        grades = query.all()
        if not grades:
            return {"code": 0, "message": "没有找到成绩数据", "data": {}}
        
        # 计算统计数据
        scores = [grade.score for grade in grades]
        mean_score = np.mean(scores)
        max_score = np.max(scores)
        min_score = np.min(scores)
        std_score = np.std(scores)
        
        # 进步趋势数据
        trend_data = []
        for grade in grades:
            trend_data.append({
                "exam_date": grade.exam_date,
                "subject_id": grade.subject_id,
                "score": grade.score,
                "exam_type": grade.exam_type
            })
        
        return {"code": 0, "message": "成功", "data": {
            "student_id": student_id,
            "student_name": student.student_name,
            "record_count": len(grades),
            "mean_score": round(mean_score, 2),
            "max_score": round(max_score, 2),
            "min_score": round(min_score, 2),
            "std_score": round(std_score, 2),
            "trend_data": trend_data
        }}
    except Exception as e:
        logger.error(f"学生成绩分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

# 辅导方案接口
@app.post("/api/tutoring-plans/generate/{student_id}", response_model=Dict)
def generate_tutoring_plan(student_id: int, db: SessionLocal = Depends(get_db)):
    try:
        # 检查学生是否存在
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        
        # 获取学生成绩分析
        analysis_result = get_student_grade_analysis(student_id, db=db)
        if not analysis_result["data"]:
            raise HTTPException(status_code=400, detail="没有足够的成绩数据生成辅导方案")
        
        # 这里应该调用大模型生成辅导方案
        # 为了演示，我们生成一个简单的模拟方案
        student_data = analysis_result["data"]
        
        plan_content = f"""学生{student_data['student_name']}辅导方案：

1. 总体表现：
   - 平均成绩：{student_data['mean_score']}
   - 最高成绩：{student_data['max_score']}
   - 最低成绩：{student_data['min_score']}
   - 成绩稳定性：{'较高' if student_data['std_score'] < 10 else '一般' if student_data['std_score'] < 20 else '较低'}

2. 学习建议：
   - {'建议保持当前学习状态，继续巩固基础知识' if student_data['mean_score'] >= 85 else 
     '建议加强基础知识学习，多做练习题' if student_data['mean_score'] >= 60 else 
     '建议重点补习基础知识，寻求老师和同学的帮助'}
   - 根据成绩趋势，建议关注最近考试中表现较弱的科目

3. 学习计划：
   - 每周安排固定时间复习和预习
   - 建立错题本，定期回顾
   - 多与老师和同学交流学习经验"""
        
        # 创建辅导方案记录
        db_plan = TutoringPlan(
            student_id=student_id,
            plan_content=plan_content,
            resources=json.dumps(["推荐教材1", "推荐练习册1", "在线学习资源1"]),
            progress=0
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        
        return {"code": 0, "message": "辅导方案生成成功", "data": {
            "plan_id": db_plan.id,
            "plan_content": db_plan.plan_content,
            "resources": json.loads(db_plan.resources),
            "progress": db_plan.progress,
            "created_at": db_plan.created_at
        }}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"生成辅导方案失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

# 集成现有的查询接口
@app.post('/api/ai/query')
async def handle_query(request: Request):
    """
    处理客户端发送的查询请求（保留现有功能）
    """
    try:
        # 支持JSON和表单数据
        content_type = request.headers.get('Content-Type', '')
        if content_type.startswith('application/json'):
            data = await request.json()
            natural_language_query = data.get('query')
        else:
            data = await request.form()
            natural_language_query = data.get('query')

        if not natural_language_query:
            raise HTTPException(status_code=400, detail="未提供查询内容")

        logger.info(f"收到查询请求: {natural_language_query}")
        
        # 使用策略模式处理查询
        db_path = "student_database.db"
        llm_api_key = os.getenv('LLM_API_KEY', 'mock_key')
        llm = SampleLLM(llm_api_key)
        db_executor = SQLiteExecutor(db_path)
        
        command = TeachingAssistantCommand(llm, db_executor)
        response = command.execute(natural_language_query)
        
        # 获取生成的SQL查询
        sql_result = llm.generate_sql_and_response(natural_language_query)
        sql_query = sql_result["sql_query"]
        
        db_executor.close()
        
        return JSONResponse(
            content={"code": 0, "message": "成功", "data": {
                "result": response,
                "sql_query": sql_query
            }},
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
    except Exception as e:
        logger.error(f"查询时发生错误: {e}")
        return JSONResponse(
            content={"code": 1, "message": f"查询时发生错误: {str(e)}"},
            status_code=500,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )

@app.get("/api/performance")
async def get_performance(dimension: str, db: SessionLocal = Depends(get_db)):
    """
    获取学生表现数据（保留现有功能）
    """
    try:
        # 构建查询
        if dimension == "成绩":
            query = db.execute('''
                SELECT s.student_name as name, AVG(g.score) as score, 
                       RANK() OVER (ORDER BY AVG(g.score) DESC) as rank
                FROM students s
                JOIN grades g ON s.student_id = g.student_id
                GROUP BY s.student_id
                ORDER BY score DESC
                LIMIT 10
            ''')
        elif dimension == "出勤":
            query = db.execute('''
                SELECT s.student_name as name, 
                       (COUNT(CASE WHEN a.status = '出勤' THEN 1 END) * 100.0 / COUNT(*)) as attendance_rate, 
                       RANK() OVER (ORDER BY (COUNT(CASE WHEN a.status = '出勤' THEN 1 END) * 100.0 / COUNT(*)) DESC) as rank
                FROM students s
                JOIN attendance a ON s.student_id = a.student_id
                GROUP BY s.student_id
                ORDER BY attendance_rate DESC
                LIMIT 10
            ''')
        elif dimension == "课程参与":
            query = db.execute('''
                SELECT s.student_name as name, AVG(cp.participation_score) as participation_score, 
                       RANK() OVER (ORDER BY AVG(cp.participation_score) DESC) as rank
                FROM students s
                JOIN class_performance cp ON s.student_id = cp.student_id
                GROUP BY s.student_id
                ORDER BY participation_score DESC
                LIMIT 10
            ''')
        elif dimension == "进步趋势":
            query = db.execute('''
                SELECT s.student_name as name, 
                       ((latest.score - earliest.score) / earliest.score * 100) as improvement_rate, 
                       RANK() OVER (ORDER BY ((latest.score - earliest.score) / earliest.score * 100) DESC) as rank
                FROM students s
                JOIN (
                    SELECT student_id, MIN(exam_date) as earliest_date, MAX(exam_date) as latest_date
                    FROM grades
                    GROUP BY student_id
                ) dates ON s.student_id = dates.student_id
                JOIN grades earliest ON s.student_id = earliest.student_id AND earliest.exam_date = dates.earliest_date
                JOIN grades latest ON s.student_id = latest.student_id AND latest.exam_date = dates.latest_date
                ORDER BY improvement_rate DESC
                LIMIT 10
            ''')
        else:
            raise HTTPException(status_code=400, detail="不支持的查询维度")

        results = query.fetchall()
        
        # 格式化结果
        performance_data = []
        for row in results:
            if dimension == "成绩":
                value = round(row["score"], 2)
            elif dimension == "出勤":
                value = round(row["attendance_rate"], 2)
            elif dimension == "课程参与":
                value = round(row["participation_score"], 2)
            else:
                value = round(row["improvement_rate"], 2)
            performance_data.append({
                "name": row["name"],
                "value": value,
                "rank": row["rank"]
            })

        return JSONResponse(
            content={"code": 0, "message": "成功", "data": performance_data},
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"表现查询时发生错误: {e}")
        return JSONResponse(
            content={"code": 1, "message": f"查询时发生错误: {str(e)}"},
            status_code=500,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )

# 初始化数据库
@app.on_event("startup")
def startup_event():
    try:
        # 创建数据库表（如果不存在）
        Base.metadata.create_all(bind=engine)
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")

# 智能教学助手类，使用外观模式
class IntelligentTeachingAssistant:
    def __init__(self, llm: LLMInterface, db_executor: DatabaseExecutorInterface):
        self.command = TeachingAssistantCommand(llm, db_executor)

    def handle_question(self, question: str, context: str = "") -> str:
        return self.command.execute(question, context)

    def close(self):
        self.command.db_executor.close()

# 启动服务器
if __name__ == "__main__":
    # 设置环境变量确保JSON序列化正确处理中文
    os.environ['FASTAPI_SERVE_JSON_AS_UTF8'] = '1'
    uvicorn.run(
        "intelligent_teaching_assistant:app", 
        host='127.0.0.1', 
        port=5001, 
        reload=True,
        log_level='info'
    )