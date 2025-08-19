# -*- coding: utf-8 -*-
"""
测试配置模块
提供测试环境配置和模拟数据
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 测试配置
TEST_CONFIG = {
    "llm": {
        "provider": "openai",
        "api_key": "test_api_key_12345",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 30
    },
    "database": {
        "type": "sqlite",
        "path": ":memory:",  # 使用内存数据库进行测试
        "auto_create_tables": True
    },
    "cache": {
        "enabled": True,
        "max_size": 100,  # 测试时使用较小的缓存
        "ttl": 300,
        "cleanup_interval": 60
    },
    "agents": {
        "teaching_analysis": {
            "enabled": True,
            "max_retries": 2,
            "timeout": 30
        },
        "learning_status": {
            "enabled": True,
            "max_retries": 2,
            "timeout": 30
        },
        "tutoring": {
            "enabled": True,
            "max_retries": 2,
            "timeout": 30
        },
        "classroom_ai": {
            "enabled": True,
            "max_retries": 2,
            "timeout": 15  # 课堂AI需要更快响应
        },
        "sql_agent": {
            "enabled": True,
            "max_retries": 1,
            "timeout": 20
        }
    }
}

# 模拟学生数据
MOCK_STUDENT_DATA = [
    {
        "student_id": "S001",
        "name": "张三",
        "class_name": "高一(1)班",
        "grade": "高一",
        "age": 16,
        "gender": "男"
    },
    {
        "student_id": "S002",
        "name": "李四",
        "class_name": "高一(1)班",
        "grade": "高一",
        "age": 15,
        "gender": "女"
    },
    {
        "student_id": "S003",
        "name": "王五",
        "class_name": "高一(2)班",
        "grade": "高一",
        "age": 16,
        "gender": "男"
    },
    {
        "student_id": "S004",
        "name": "赵六",
        "class_name": "高一(2)班",
        "grade": "高一",
        "age": 15,
        "gender": "女"
    }
]

# 模拟成绩数据
MOCK_GRADE_DATA = [
    {
        "grade_id": "G001",
        "student_id": "S001",
        "subject_id": "MATH001",
        "score": 85.5,
        "exam_type": "期中考试",
        "exam_date": "2024-01-15"
    },
    {
        "grade_id": "G002",
        "student_id": "S001",
        "subject_id": "ENG001",
        "score": 78.0,
        "exam_type": "期中考试",
        "exam_date": "2024-01-15"
    },
    {
        "grade_id": "G003",
        "student_id": "S002",
        "subject_id": "MATH001",
        "score": 92.0,
        "exam_type": "期中考试",
        "exam_date": "2024-01-15"
    },
    {
        "grade_id": "G004",
        "student_id": "S002",
        "subject_id": "ENG001",
        "score": 88.5,
        "exam_type": "期中考试",
        "exam_date": "2024-01-15"
    }
]

# 模拟科目数据
MOCK_SUBJECT_DATA = [
    {
        "subject_id": "MATH001",
        "subject_name": "数学",
        "grade": "高一",
        "description": "高中数学必修课程"
    },
    {
        "subject_id": "ENG001",
        "subject_name": "英语",
        "grade": "高一",
        "description": "高中英语必修课程"
    },
    {
        "subject_id": "PHY001",
        "subject_name": "物理",
        "grade": "高一",
        "description": "高中物理必修课程"
    },
    {
        "subject_id": "CHEM001",
        "subject_name": "化学",
        "grade": "高一",
        "description": "高中化学必修课程"
    }
]

# 模拟教材数据
MOCK_TEACHING_MATERIAL_DATA = [
    {
        "material_id": "TM001",
        "title": "高中数学必修一",
        "subject_id": "MATH001",
        "grade": "高一",
        "content": "第一章：集合与函数概念\n1.1 集合\n集合是数学中的基本概念...",
        "difficulty_level": "中等",
        "keywords": ["集合", "函数", "定义域", "值域"]
    },
    {
        "material_id": "TM002",
        "title": "高中英语必修一",
        "subject_id": "ENG001",
        "grade": "高一",
        "content": "Unit 1: Friendship\nAnne's Best Friend\nDo you want a friend whom you could tell everything to...",
        "difficulty_level": "中等",
        "keywords": ["friendship", "diary", "feelings", "communication"]
    }
]

# 模拟LLM响应数据
MOCK_LLM_RESPONSES = {
    "teaching_analysis": {
        "knowledge_points": [
            "集合的概念和表示方法",
            "集合间的基本关系",
            "集合的基本运算"
        ],
        "difficulty_analysis": {
            "level": "中等",
            "reasoning": "涉及抽象概念，需要逻辑思维能力"
        },
        "learning_objectives": [
            "理解集合的概念",
            "掌握集合的表示方法",
            "能够进行集合运算"
        ]
    },
    "learning_status": {
        "overall_performance": "良好",
        "strengths": ["数学逻辑思维较强", "基础知识扎实"],
        "weaknesses": ["英语词汇量需要提升", "解题速度有待提高"],
        "recommendations": [
            "加强英语词汇记忆",
            "多做数学练习题提高解题速度"
        ]
    },
    "tutoring_plan": {
        "study_plan": {
            "daily_tasks": [
                "复习今日课程内容30分钟",
                "完成课后练习题",
                "预习明日课程15分钟"
            ],
            "weekly_goals": [
                "掌握本周所学知识点",
                "完成单元测试"
            ]
        },
        "exercise_recommendations": [
            {
                "type": "基础练习",
                "content": "集合基本概念练习题",
                "difficulty": "简单"
            },
            {
                "type": "提高练习",
                "content": "集合运算综合题",
                "difficulty": "中等"
            }
        ]
    },
    "classroom_ai": {
        "answer": "集合是由确定的、互不相同的对象组成的整体。",
        "explanation": "集合中的对象称为集合的元素，具有确定性、互异性和无序性三个特征。",
        "examples": [
            "自然数集合 N = {0, 1, 2, 3, ...}",
            "小于10的正整数集合 {1, 2, 3, 4, 5, 6, 7, 8, 9}"
        ]
    },
    "sql_generation": {
        "sql_query": "SELECT s.name, AVG(g.score) as avg_score FROM students s JOIN grades g ON s.student_id = g.student_id WHERE s.class_name = '高一(1)班' GROUP BY s.student_id, s.name ORDER BY avg_score DESC",
        "explanation": "这个查询计算高一(1)班每个学生的平均成绩，并按平均成绩降序排列。"
    }
}

# 测试用例数据
TEST_CASES = {
    "valid_student_ids": ["S001", "S002", "S003", "S004"],
    "invalid_student_ids": ["S999", "INVALID", "", None],
    "valid_subject_ids": ["MATH001", "ENG001", "PHY001", "CHEM001"],
    "invalid_subject_ids": ["SUB999", "INVALID", "", None],
    "valid_class_names": ["高一(1)班", "高一(2)班"],
    "invalid_class_names": ["不存在的班级", "", None],
    "valid_scores": [85.5, 92.0, 78.0, 88.5],
    "invalid_scores": [-10, 150, "not_a_number", None],
    "valid_exam_types": ["期中考试", "期末考试", "月考", "单元测试"],
    "valid_difficulty_levels": ["简单", "中等", "困难"]
}

# 模拟LLM客户端
class MockLLMClient:
    """模拟LLM客户端"""
    
    def __init__(self, provider="openai"):
        self.provider = provider
        self.call_count = 0
        self.last_prompt = None
        self.last_messages = None
        self.last_kwargs = None
        self.responses = MOCK_LLM_RESPONSES.copy()
        self.should_fail = False
        self.fail_count = 0
        self.response_delay = 0
    
    def generate_response(self, prompt=None, messages=None, **kwargs):
        """生成模拟响应"""
        import time
        import json
        
        self.call_count += 1
        self.last_prompt = prompt
        self.last_messages = messages
        self.last_kwargs = kwargs
        
        # 模拟延迟
        if self.response_delay > 0:
            time.sleep(self.response_delay)
        
        # 模拟失败
        if self.should_fail:
            self.fail_count += 1
            raise Exception(f"模拟LLM错误 (失败次数: {self.fail_count})")
        
        # 处理消息列表格式
        if messages:
            content = messages[-1].get('content', '') if isinstance(messages[-1], dict) else str(messages[-1])
        else:
            content = prompt or ""
        
        # 根据内容返回相应的模拟响应
        if "教材分析" in content or "teaching_analysis" in content.lower():
            return json.dumps(self.responses["teaching_analysis"], ensure_ascii=False)
        elif "学情分析" in content or "learning_status" in content.lower():
            return json.dumps(self.responses["learning_status"], ensure_ascii=False)
        elif "辅导方案" in content or "tutoring" in content.lower():
            return json.dumps(self.responses["tutoring_plan"], ensure_ascii=False)
        elif "课堂" in content or "classroom" in content.lower():
            return json.dumps(self.responses["classroom_ai"], ensure_ascii=False)
        elif "sql" in content.lower() or "查询" in content:
            return json.dumps(self.responses["sql_generation"], ensure_ascii=False)
        elif "错误" in content or "error" in content.lower():
            raise Exception("模拟LLM错误")
        
        return "这是一个模拟的LLM响应"
    
    async def generate_response_async(self, prompt=None, messages=None, **kwargs):
        """异步生成模拟响应"""
        return self.generate_response(prompt, messages, **kwargs)
    
    def set_response(self, key, response):
        """设置特定的响应"""
        self.responses[key] = response
    
    def set_failure_mode(self, should_fail=True):
        """设置失败模式"""
        self.should_fail = should_fail
        if not should_fail:
            self.fail_count = 0
    
    def set_response_delay(self, delay_seconds):
        """设置响应延迟"""
        self.response_delay = delay_seconds
    
    def reset(self):
        """重置模拟客户端状态"""
        self.call_count = 0
        self.last_prompt = None
        self.last_messages = None
        self.last_kwargs = None
        self.should_fail = False
        self.fail_count = 0
        self.response_delay = 0
        self.responses = MOCK_LLM_RESPONSES.copy()

# 模拟数据库管理器
class MockMockDatabaseManager:
    """模拟数据库管理器"""
    
    def __init__(self):
        self.students = MOCK_STUDENT_DATA.copy()
        self.grades = MOCK_GRADE_DATA.copy()
        self.subjects = MOCK_SUBJECT_DATA.copy()
        self.teaching_materials = MOCK_TEACHING_MATERIAL_DATA.copy()
        self.query_count = 0
        self.last_query = None
        self.last_params = None
        self.should_fail = False
        self.fail_count = 0
        self.connection_error = False
        
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """模拟执行查询"""
        self.query_count += 1
        self.last_query = query
        self.last_params = params
        
        # 模拟连接错误
        if self.connection_error:
            raise Exception("数据库连接错误")
        
        # 模拟查询失败
        if self.should_fail:
            self.fail_count += 1
            raise Exception(f"数据库查询错误 (失败次数: {self.fail_count})")
        
        query_lower = query.lower()
        
        # 根据查询类型返回模拟数据
        if "students" in query_lower:
            if "where" in query_lower and params:
                # 简单的参数过滤
                return [s for s in self.students if any(str(p) in str(s.values()) for p in params)]
            return self.students
        elif "grades" in query_lower:
            if "where" in query_lower and params:
                return [g for g in self.grades if any(str(p) in str(g.values()) for p in params)]
            return self.grades
        elif "subjects" in query_lower:
            if "where" in query_lower and params:
                return [s for s in self.subjects if any(str(p) in str(s.values()) for p in params)]
            return self.subjects
        elif "teaching_materials" in query_lower:
            if "where" in query_lower and params:
                return [t for t in self.teaching_materials if any(str(p) in str(t.values()) for p in params)]
            return self.teaching_materials
        elif "avg" in query_lower or "count" in query_lower or "sum" in query_lower:
            # 模拟聚合查询结果
            return [{"result": 85.5, "count": 4}]
        
        return []
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取表结构"""
        schemas = {
            "students": {
                "columns": ["student_id", "name", "class_name", "grade", "age", "gender"],
                "types": ["TEXT", "TEXT", "TEXT", "TEXT", "INTEGER", "TEXT"],
                "primary_key": "student_id"
            },
            "grades": {
                "columns": ["grade_id", "student_id", "subject_id", "score", "exam_type", "exam_date"],
                "types": ["TEXT", "TEXT", "TEXT", "REAL", "TEXT", "TEXT"],
                "primary_key": "grade_id",
                "foreign_keys": ["student_id", "subject_id"]
            },
            "subjects": {
                "columns": ["subject_id", "subject_name", "grade", "description"],
                "types": ["TEXT", "TEXT", "TEXT", "TEXT"],
                "primary_key": "subject_id"
            },
            "teaching_materials": {
                "columns": ["material_id", "title", "subject_id", "grade", "content", "difficulty_level"],
                "types": ["TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT"],
                "primary_key": "material_id",
                "foreign_keys": ["subject_id"]
            }
        }
        return schemas.get(table_name, {})
    
    def get_all_tables(self) -> list[str]:
        """获取所有表名"""
        return ["students", "grades", "subjects", "teaching_materials"]
    
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """插入数据"""
        if self.should_fail:
            raise Exception("插入数据失败")
        
        if table_name == "students":
            self.students.append(data)
        elif table_name == "grades":
            self.grades.append(data)
        elif table_name == "subjects":
            self.subjects.append(data)
        elif table_name == "teaching_materials":
            self.teaching_materials.append(data)
        
        return True
    
    def update_data(self, table_name: str, data: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """更新数据"""
        if self.should_fail:
            raise Exception("更新数据失败")
        
        # 简单的更新逻辑
        return True
    
    def delete_data(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """删除数据"""
        if self.should_fail:
            raise Exception("删除数据失败")
        
        # 简单的删除逻辑
        return True
    
    def set_failure_mode(self, should_fail=True):
        """设置失败模式"""
        self.should_fail = should_fail
        if not should_fail:
            self.fail_count = 0
    
    def set_connection_error(self, error=True):
        """设置连接错误"""
        self.connection_error = error
    
    def reset(self):
        """重置数据库状态"""
        self.students = MOCK_STUDENT_DATA.copy()
        self.grades = MOCK_GRADE_DATA.copy()
        self.subjects = MOCK_SUBJECT_DATA.copy()
        self.teaching_materials = MOCK_TEACHING_MATERIAL_DATA.copy()
        self.query_count = 0
        self.last_query = None
        self.last_params = None
        self.should_fail = False
        self.fail_count = 0
        self.connection_error = False
    
    def get_table_info(self, tables: list[str] = None) -> str:
        """模拟获取表结构信息"""
        return """
        表结构信息:
        students: student_id, name, class_name, grade, age, gender
        grades: grade_id, student_id, subject_id, score, exam_type, exam_date
        subjects: subject_id, subject_name, grade, description
        teaching_materials: material_id, title, subject_id, grade, content, difficulty_level
        """

# 模拟缓存管理器
class MockCacheManager:
    """模拟缓存管理器"""
    
    def __init__(self, max_size=100, ttl=300):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
        self.should_fail = False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        self.access_count += 1
        
        if self.should_fail:
            raise Exception("缓存获取失败")
        
        if key in self.cache:
            self.hit_count += 1
            return self.cache[key]
        else:
            self.miss_count += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if self.should_fail:
            raise Exception("缓存设置失败")
        
        if len(self.cache) >= self.max_size:
            # 简单的LRU策略：删除第一个元素
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        self.cache[key] = value
        return True
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """清空缓存"""
        self.cache.clear()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "access_count": self.access_count,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.hit_count / self.access_count if self.access_count > 0 else 0
        }
    
    def set_failure_mode(self, should_fail=True):
        """设置失败模式"""
        self.should_fail = should_fail
    
    def reset(self):
        """重置缓存状态"""
        self.cache.clear()
        self.access_count = 0
        self.hit_count = 0
        self.miss_count = 0
        self.should_fail = False

# 模拟上下文管理器
class MockContextManager:
    """模拟上下文管理器"""
    
    def __init__(self):
        self.sessions = {}
        self.should_fail = False
    
    def create_session(self, session_id: str) -> bool:
        """创建会话"""
        if self.should_fail:
            raise Exception("创建会话失败")
        
        self.sessions[session_id] = {
            "messages": [],
            "metadata": {},
            "created_at": datetime.now(),
            "last_active": datetime.now()
        }
        return True
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """添加消息"""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now()
            })
            self.sessions[session_id]["last_active"] = datetime.now()
            return True
        return False
    
    def get_context(self, session_id: str, max_messages: int = 10) -> List[Dict[str, Any]]:
        """获取上下文"""
        if session_id in self.sessions:
            messages = self.sessions[session_id]["messages"]
            return messages[-max_messages:] if len(messages) > max_messages else messages
        return []
    
    def clear_session(self, session_id: str) -> bool:
        """清除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def set_failure_mode(self, should_fail=True):
        """设置失败模式"""
        self.should_fail = should_fail
    
    def reset(self):
        """重置状态"""
        self.sessions.clear()
        self.should_fail = False

# 测试数据
TEST_DATA = {
    "student_info": {
        "name": "张三",
        "grade": "高一",
        "class_name": "高一(1)班",
        "student_id": "2024001"
    },
    "grade_data": [
        {"subject": "数学", "score": 85, "full_score": 100},
        {"subject": "语文", "score": 78, "full_score": 100},
        {"subject": "英语", "score": 92, "full_score": 100}
    ],
    "teaching_content": """
    第一章 函数的概念
    1.1 函数的定义
    函数是一种特殊的对应关系，对于定义域内的每一个x值，都有唯一的y值与之对应。
    1.2 函数的表示方法
    函数可以用解析式、图像、表格等方式表示。
    """,
    "natural_language_queries": [
        "查询所有学生的数学成绩",
        "统计班级平均分",
        "找出成绩最好的学生"
    ],
    "llm_responses": {
        "教材分析": "这是一个关于函数概念的教材内容，主要介绍了函数的定义和表示方法。",
        "学情分析": "该学生数学成绩良好，语文需要加强，英语表现优秀。",
        "辅导方案": "建议加强语文阅读理解训练，保持数学和英语的优势。",
        "sql查询": "SELECT * FROM students WHERE grade = '高一'",
        "结果解释": "查询结果显示了所有高一年级的学生信息。"
    }
}

# 创建临时文件的辅助函数
def create_temp_file(content: str = "", suffix: str = ".txt") -> str:
    """创建临时文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name

# 清理临时文件的辅助函数
def cleanup_temp_file(file_path: str):
    """清理临时文件"""
    try:
        os.unlink(file_path)
    except FileNotFoundError:
        pass

# 创建模拟对象的工厂函数
def create_mock_llm_client(responses: Dict[str, str] = None) -> MockLLMClient:
    """创建模拟LLM客户端"""
    return MockLLMClient(responses or TEST_DATA["llm_responses"])

def create_mock_db_manager() -> MockMockDatabaseManager:
    """创建模拟数据库管理器"""
    return MockMockDatabaseManager()

def create_mock_cache_manager() -> MockCacheManager:
    """创建模拟缓存管理器"""
    return MockCacheManager()

def create_mock_context_manager() -> MockContextManager:
    """创建模拟上下文管理器"""
    return MockContextManager()

# 测试断言辅助函数
def assert_response_valid(response, expected_keys: list[str] = None):
    """验证响应格式是否正确"""
    assert response is not None, "响应不能为空"
    
    if expected_keys:
        if hasattr(response, '__dict__'):
            response_dict = response.__dict__
        elif isinstance(response, dict):
            response_dict = response
        else:
            raise AssertionError(f"响应类型不正确: {type(response)}")
            
        for key in expected_keys:
            assert key in response_dict, f"响应中缺少必需的键: {key}"

def assert_llm_called(mock_client: MockLLMClient, min_calls: int = 1):
    """验证LLM客户端是否被调用"""
    assert mock_client.call_count >= min_calls, f"LLM客户端调用次数不足，期望至少{min_calls}次，实际{mock_client.call_count}次"

def assert_db_called(mock_db: MockMockDatabaseManager, min_calls: int = 1):
    """验证数据库是否被调用"""
    assert mock_db.query_count >= min_calls, f"数据库调用次数不足，期望至少{min_calls}次，实际{mock_db.query_count}次"

def assert_cache_hit(mock_cache: MockCacheManager, expected_hits: int = None):
    """验证缓存命中情况"""
    if expected_hits is not None:
        assert mock_cache.hit_count == expected_hits, f"缓存命中次数不符，期望{expected_hits}次，实际{mock_cache.hit_count}次"
    else:
        assert mock_cache.hit_count > 0, "期望有缓存命中，但实际没有"

def assert_session_exists(mock_context: MockContextManager, session_id: str):
    """验证会话是否存在"""
    session = mock_context.get_session(session_id)
    assert session is not None, f"会话 {session_id} 不存在"

# 性能测试辅助函数
def measure_execution_time(func, *args, **kwargs):
    """测量函数执行时间"""
    import time
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time

def generate_large_dataset(size: int = 1000) -> List[Dict[str, Any]]:
    """生成大量测试数据"""
    import random
    import string

class MockDatabaseManager:
    """Mock数据库管理器"""
    def __init__(self, *args, **kwargs):
        pass
    
    def execute_query(self, query, params=None):
        return []
    
    def get_table_schema(self, table_name):
        return {}
    
    def get_all_tables(self):
        return []


def generate_test_data(size=10):
    """生成测试数据"""
    data = []
    for i in range(size):
        data.append({
            "id": f"ID{i:06d}",
            "name": ''.join(random.choices(string.ascii_letters, k=8)),
            "score": random.uniform(0, 100),
            "grade": random.choice(["高一", "高二", "高三"]),
            "subject": random.choice(["数学", "语文", "英语", "物理", "化学"])
        })
    return data

# 错误模拟辅助函数
def simulate_network_error():
    """模拟网络错误"""
    raise ConnectionError("网络连接失败")

def simulate_timeout_error():
    """模拟超时错误"""
    raise TimeoutError("请求超时")

def simulate_rate_limit_error():
    """模拟频率限制错误"""
    raise Exception("API调用频率超限")

# 环境变量设置辅助函数
def set_test_env_vars():
    """设置测试环境变量"""
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["DATABASE_URL"] = ":memory:"
    os.environ["CACHE_ENABLED"] = "true"

def cleanup_test_env_vars():
    """清理测试环境变量"""
    test_vars = ["TESTING", "LOG_LEVEL", "DATABASE_URL", "CACHE_ENABLED"]
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]