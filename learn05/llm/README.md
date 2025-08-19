# 智能教学助手LLM系统

## 概述

智能教学助手LLM系统是一个专为教育场景设计的大语言模型集成框架，提供教材分析、学情分析、辅导方案生成、课堂AI助手等核心功能。系统采用模块化设计，支持多种大模型提供商，具备完善的上下文管理、性能优化和监控功能。

## 核心特性

### 🤖 智能体系统
- **教材分析智能体**: 自动解析教材内容，识别知识点，评估难度
- **学情分析智能体**: 基于成绩数据生成个性化学情报告
- **辅导方案智能体**: 提供个性化学习建议和练习推荐
- **课堂AI助手**: 实时学情分析和互动内容生成

### 🎯 提示词管理
- 丰富的提示词模板库
- 动态模板格式化
- 模板使用统计和优化
- 自定义模板支持

### 💬 上下文管理
- 多轮对话支持
- 会话状态保持
- 智能上下文压缩
- 记忆存储和检索

### ⚡ 性能优化
- 智能缓存机制
- 并发处理支持
- 实时性能监控
- 自动优化建议

### 🔌 多模型支持
- 阿里云通义千问
- OpenAI GPT系列
- 其他主流大模型
- 统一的API接口

## 系统架构

```
智能教学助手LLM系统
├── agents/                 # 智能体模块
│   ├── base_agent.py      # 智能体基类
│   ├── teaching_analysis.py # 教材分析智能体
│   ├── learning_status.py   # 学情分析智能体
│   ├── tutoring_plan.py     # 辅导方案智能体
│   ├── classroom_ai.py      # 课堂AI助手
│   └── agent_manager.py     # 智能体管理器
├── prompts/               # 提示词管理
│   ├── teaching_prompts.py # 教学提示词
│   ├── learning_prompts.py # 学情提示词
│   ├── tutoring_prompts.py # 辅导提示词
│   ├── classroom_prompts.py # 课堂提示词
│   └── prompt_manager.py   # 提示词管理器
├── context/               # 上下文管理
│   ├── context_manager.py # 上下文管理器
│   ├── session_manager.py # 会话管理器
│   ├── memory_store.py    # 记忆存储
│   └── context_strategies.py # 上下文策略
├── optimization/          # 性能优化
│   ├── cache_manager.py   # 缓存管理
│   ├── concurrent_processor.py # 并发处理
│   ├── performance_monitor.py # 性能监控
│   └── optimization_manager.py # 优化管理器
├── llm_client.py         # LLM客户端
├── config.py             # 配置管理
└── examples/             # 使用示例
    └── usage_examples.py # 完整示例
```

## 快速开始

### 1. 安装依赖

```bash
pip install openai dashscope psutil pandas numpy
```

### 2. 配置API密钥

```python
from service.llm.llm_client import LLMClient, LLMConfig

# 配置通义千问
config = LLMConfig(
    provider="tongyi",
    api_key="your-dashscope-api-key",
    model="qwen-plus"
)

# 或配置OpenAI
config = LLMConfig(
    provider="openai",
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo"
)

llm_client = LLMClient(config)
```

### 3. 基本使用

#### 教材分析

```python
from service.llm.agents import TeachingAnalysisAgent

# 创建教材分析智能体
teaching_agent = TeachingAnalysisAgent(llm_client)

# 分析教材
material = {
    "subject": "数学",
    "grade": "高一",
    "content": "函数的概念和性质"
}

result = await teaching_agent.analyze_material(material)
print(result)
```

#### 学情分析

```python
from service.llm.agents import LearningStatusAgent

# 创建学情分析智能体
learning_agent = LearningStatusAgent(llm_client)

# 分析学情
student_data = {
    "student_id": "S001",
    "subject_scores": {
        "数学": [85, 78, 92, 88, 90]
    }
}

result = await learning_agent.analyze_learning_status(student_data)
print(result)
```

#### 辅导方案生成

```python
from service.llm.agents import TutoringPlanAgent

# 创建辅导方案智能体
tutoring_agent = TutoringPlanAgent(llm_client)

# 生成辅导方案
request = {
    "student_info": {"grade": "高一"},
    "subject": "数学",
    "weak_areas": ["函数定义域"],
    "target_score": 95
}

result = await tutoring_agent.generate_plan(request)
print(result)
```

### 4. 使用智能体管理器

```python
from service.llm.agents import AgentManager

# 创建智能体管理器
agent_manager = AgentManager(llm_client)

# 获取智能体
teaching_agent = agent_manager.get_agent("teaching_analysis")
learning_agent = agent_manager.get_agent("learning_status")
tutoring_agent = agent_manager.get_agent("tutoring_plan")
classroom_agent = agent_manager.get_agent("classroom_ai")

# 使用智能体
result = await teaching_agent.analyze_material(material)
```

## 高级功能

### 性能优化

#### 使用缓存

```python
from service.llm.optimization import cached

@cached(key="teaching_analysis", ttl=3600)
async def analyze_teaching_material(material):
    # 教材分析逻辑
    return result
```

#### 并发处理

```python
from service.llm.optimization import concurrent

@concurrent
async def process_multiple_students(student_list):
    # 批量处理学生数据
    return results
```

#### 性能监控

```python
from service.llm.optimization import monitored

@monitored
async def generate_tutoring_plan(request):
    # 生成辅导方案
    return plan
```

### 上下文管理

```python
from service.llm.context import ContextManager, SessionManager

# 创建会话管理器
session_manager = SessionManager()
context_manager = ContextManager()

# 创建会话
session = session_manager.create_session(
    user_id="teacher_001",
    user_role="teacher"
)

# 创建上下文
context_id = context_manager.create_context(
    session_id=session.session_id,
    context_type="teaching_consultation"
)

# 添加对话
context_manager.add_message(context_id, "user", "请分析这道数学题")
context_manager.add_message(context_id, "assistant", "好的，我来分析...")

# 获取对话历史
history = context_manager.get_conversation_history(context_id)
```

### 提示词管理

```python
from service.llm.prompts import PromptManager

# 创建提示词管理器
prompt_manager = PromptManager()

# 获取模板
template = prompt_manager.get_template(
    "teaching_analysis", 
    "analyze_knowledge_points"
)

# 格式化模板
formatted_prompt = prompt_manager.format_template(
    "teaching_analysis",
    "analyze_knowledge_points",
    {
        "subject": "数学",
        "content": "函数概念",
        "grade_level": "高一"
    }
)
```

## 配置说明

### LLM配置

```python
from service.llm.llm_client import LLMConfig

config = LLMConfig(
    provider="tongyi",           # 提供商: tongyi, openai
    api_key="your-api-key",     # API密钥
    model="qwen-plus",          # 模型名称
    temperature=0.7,            # 温度参数
    max_tokens=2000,            # 最大token数
    timeout=30,                 # 超时时间
    max_retries=3,              # 最大重试次数
    retry_delay=1.0             # 重试延迟
)
```

### 优化配置

```python
from service.llm.optimization import OptimizationConfig, OptimizationStrategy

config = OptimizationConfig(
    strategy=OptimizationStrategy.BALANCED,  # 优化策略
    enable_cache=True,                       # 启用缓存
    cache_ttl=3600,                         # 缓存TTL
    enable_concurrent=True,                  # 启用并发
    max_workers=4,                          # 最大工作线程
    enable_monitoring=True,                  # 启用监控
    enable_auto_optimization=True           # 启用自动优化
)
```

## API参考

### 智能体接口

#### TeachingAnalysisAgent

```python
class TeachingAnalysisAgent:
    async def analyze_material(self, material: Dict) -> Dict:
        """分析教材内容"""
        pass
    
    async def extract_knowledge_points(self, content: str) -> List[str]:
        """提取知识点"""
        pass
    
    async def assess_difficulty(self, content: str, grade: str) -> str:
        """评估难度"""
        pass
```

#### LearningStatusAgent

```python
class LearningStatusAgent:
    async def analyze_learning_status(self, student_data: Dict) -> Dict:
        """分析学习状态"""
        pass
    
    async def identify_strengths_weaknesses(self, scores: Dict) -> Dict:
        """识别强项和弱项"""
        pass
    
    async def predict_performance(self, historical_data: List) -> Dict:
        """预测学习表现"""
        pass
```

#### TutoringPlanAgent

```python
class TutoringPlanAgent:
    async def generate_plan(self, request: Dict) -> Dict:
        """生成辅导方案"""
        pass
    
    async def recommend_exercises(self, weak_areas: List, level: str) -> List:
        """推荐练习"""
        pass
    
    async def create_study_schedule(self, plan: Dict, time_available: str) -> Dict:
        """创建学习计划"""
        pass
```

### 管理器接口

#### AgentManager

```python
class AgentManager:
    def get_agent(self, agent_type: str) -> BaseAgent:
        """获取智能体"""
        pass
    
    def register_agent(self, agent_type: str, agent: BaseAgent):
        """注册智能体"""
        pass
    
    async def process_request(self, agent_type: str, request: Dict) -> Dict:
        """处理请求"""
        pass
```

## 最佳实践

### 1. 错误处理

```python
try:
    result = await teaching_agent.analyze_material(material)
except Exception as e:
    logger.error(f"教材分析失败: {e}")
    # 处理错误
```

### 2. 资源管理

```python
# 使用上下文管理器
async with agent_manager:
    result = await agent_manager.process_request("teaching_analysis", request)

# 或手动清理
try:
    # 使用智能体
    pass
finally:
    agent_manager.cleanup()
```

### 3. 性能优化

```python
# 使用装饰器组合
@cached(key="analysis", ttl=1800)
@monitored
@concurrent
async def comprehensive_analysis(data):
    # 综合分析逻辑
    return result
```

### 4. 配置管理

```python
# 使用环境变量
import os

config = LLMConfig(
    provider=os.getenv("LLM_PROVIDER", "tongyi"),
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_MODEL", "qwen-plus")
)
```

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查API密钥是否正确
   - 确认API密钥权限

2. **网络连接问题**
   - 检查网络连接
   - 配置代理设置

3. **内存使用过高**
   - 启用缓存清理
   - 调整缓存大小
   - 使用内存优化策略

4. **响应时间过长**
   - 启用缓存
   - 使用并发处理
   - 优化提示词长度

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用性能监控
from service.llm.optimization import get_global_monitor
monitor = get_global_monitor()
stats = monitor.get_system_stats()
print(f"系统状态: {stats}")

# 检查缓存状态
cache_manager = optimization_manager.get_cache_manager()
if cache_manager:
    cache_stats = cache_manager.get_stats()
    print(f"缓存统计: {cache_stats}")
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。

---

**注意**: 使用前请确保已正确配置相应的API密钥和网络环境。