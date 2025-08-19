# LLM模块单元测试

本目录包含智能教学助手LLM模块的完整单元测试套件，确保所有功能模块正常工作。

## 📁 测试文件结构

```
test/
├── README.md                          # 测试说明文档
├── test_config.py                      # 测试配置和模拟对象
├── run_tests.py                        # 测试运行器
├── test_suite.py                       # 测试套件管理
├── test_llm_client.py                  # LLM客户端测试
├── test_database_manager.py            # 数据库管理器测试
├── test_config_manager.py              # 配置管理器测试
├── test_cache.py                       # 缓存系统测试
├── test_context_management.py          # 上下文管理测试
├── test_prompts.py                     # 提示词模板测试
├── test_teaching_analysis_agent.py     # 教材分析智能体测试
├── test_learning_status_agent.py       # 学情分析智能体测试
├── test_tutoring_agent.py              # 辅导智能体测试
├── test_classroom_ai_agent.py          # 课堂AI智能体测试
├── test_sql_agent.py                   # SQL智能体测试
├── test_langgraph_sql_agent.py         # LangGraph SQL智能体测试
└── test_agent_manager.py               # 智能体管理器测试
```

## 🚀 快速开始

### 运行所有测试

```bash
# 使用测试运行器（推荐）
python test/run_tests.py

# 或使用Python unittest
python -m unittest discover test/ -v
```

### 运行特定测试套件

```bash
# 运行核心功能测试
python test/test_suite.py core

# 运行智能体测试
python test/test_suite.py agent

# 运行快速测试（核心功能）
python test/test_suite.py quick

# 运行冒烟测试（基本功能验证）
python test/test_suite.py smoke
```

### 运行特定测试文件

```bash
# 运行LLM客户端测试
python test/run_tests.py -t test_llm_client

# 运行数据库管理器测试
python test/run_tests.py -t test_database_manager

# 运行智能体管理器测试
python test/run_tests.py -t test_agent_manager
```

### 运行特定测试类

```bash
# 运行特定测试类
python test/run_tests.py -t test_llm_client.TestOpenAIClient

# 运行多个测试类
python test/run_tests.py -t test_llm_client.TestOpenAIClient test_database_manager.TestDatabaseManager
```

## 📊 测试套件说明

### 核心功能测试 (core)
- **LLM客户端**: OpenAI、通义千问客户端及工厂类
- **数据库管理**: 数据库连接、查询、事务管理
- **配置管理**: 配置加载、验证、环境变量处理

### 智能体测试 (agent)
- **教材分析智能体**: 教材内容解析、知识点提取
- **学情分析智能体**: 成绩分析、学习状态评估
- **辅导智能体**: 个性化辅导方案生成
- **课堂AI智能体**: 实时互动、问题回答
- **SQL智能体**: 自然语言转SQL、查询执行
- **智能体管理器**: 智能体调度、任务分发

### 工具类测试 (utility)
- **缓存系统**: 缓存管理、性能优化
- **上下文管理**: 会话管理、对话历史
- **提示词管理**: 模板管理、动态生成

### 集成测试 (integration)
- **端到端测试**: 完整业务流程验证
- **组件协作**: 多组件交互测试
- **数据流测试**: 数据在各组件间的流转

### 性能测试 (performance)
- **响应时间**: LLM调用、数据库查询性能
- **并发处理**: 多用户同时访问
- **内存使用**: 内存泄漏检测

### 错误处理测试 (error)
- **异常处理**: 各种异常情况的处理
- **容错机制**: 服务降级、重试机制
- **边界条件**: 极端输入的处理

## 🛠️ 高级用法

### 生成测试报告

```bash
# 生成HTML测试报告
python test/run_tests.py --report test_report.txt

# 运行性能测试
python test/run_tests.py --performance
```

### 自定义测试配置

```bash
# 设置详细输出级别
python test/run_tests.py -v 2

# 禁用彩色输出
python test/run_tests.py --no-color

# 使用自定义测试模式
python test/run_tests.py -p "test_agent_*.py"
```

### 查看可用测试套件

```bash
# 列出所有测试套件
python test/test_suite.py -l
```

## 🧪 测试数据说明

### 模拟数据
测试使用 `test_config.py` 中定义的模拟数据：

- **学生数据**: 4个模拟学生（张三、李四、王五、赵六）
- **成绩数据**: 各科目成绩记录
- **科目数据**: 数学、英语、物理、化学
- **教材数据**: 高中必修课程内容
- **LLM响应**: 预设的智能体响应模板

### 模拟对象
- **MockLLMClient**: 模拟LLM客户端，支持不同响应模式
- **MockDatabaseManager**: 模拟数据库管理器，支持CRUD操作
- **MockCacheManager**: 模拟缓存管理器，支持缓存策略
- **MockContextManager**: 模拟上下文管理器，支持会话管理

## 📈 测试覆盖率

### 核心组件覆盖率目标
- **LLM客户端**: 95%+
- **数据库管理**: 90%+
- **智能体**: 85%+
- **工具类**: 90%+

### 测试类型覆盖
- ✅ 单元测试 (Unit Tests)
- ✅ 集成测试 (Integration Tests)
- ✅ 性能测试 (Performance Tests)
- ✅ 错误处理测试 (Error Handling Tests)
- ✅ 边界条件测试 (Edge Case Tests)

## 🔧 故障排除

### 常见问题

1. **导入错误**
   ```bash
   # 确保在正确的目录运行测试
   cd /path/to/aiLearn/learn05/service/llm
   python test/run_tests.py
   ```

2. **模块未找到**
   ```bash
   # 检查Python路径
   export PYTHONPATH=$PYTHONPATH:/path/to/aiLearn/learn05/service
   ```

3. **测试失败**
   ```bash
   # 运行详细模式查看错误信息
   python test/run_tests.py -v 2
   ```

4. **性能测试超时**
   ```bash
   # 跳过性能测试
   python test/run_tests.py -t test_llm_client test_database_manager
   ```

### 调试技巧

1. **单独运行失败的测试**
   ```bash
   python -m unittest test.test_llm_client.TestOpenAIClient.test_generate_response -v
   ```

2. **使用调试模式**
   ```python
   import pdb; pdb.set_trace()  # 在测试代码中添加断点
   ```

3. **查看详细日志**
   ```bash
   export LOG_LEVEL=DEBUG
   python test/run_tests.py
   ```

## 📝 编写新测试

### 测试文件命名规范
- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头

### 测试模板

```python
import unittest
from test.test_config import (
    TEST_CONFIG, 
    MockLLMClient, 
    MockDatabaseManager,
    create_mock_llm_client,
    assert_response_valid
)

class TestNewFeature(unittest.TestCase):
    """新功能测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.mock_client = create_mock_llm_client()
        
    def tearDown(self):
        """测试后置清理"""
        self.mock_client.reset()
    
    def test_basic_functionality(self):
        """测试基本功能"""
        # 测试逻辑
        result = self.mock_client.generate_response("测试")
        assert_response_valid(result)
        
    def test_error_handling(self):
        """测试错误处理"""
        self.mock_client.set_failure_mode(True)
        with self.assertRaises(Exception):
            self.mock_client.generate_response("错误测试")

if __name__ == '__main__':
    unittest.main()
```

## 🤝 贡献指南

1. **添加新测试**
   - 为新功能编写对应的测试用例
   - 确保测试覆盖正常流程和异常情况
   - 更新测试套件配置

2. **修改现有测试**
   - 保持测试的独立性和可重复性
   - 更新相关文档和注释
   - 确保所有测试仍能通过

3. **性能优化**
   - 避免测试间的相互依赖
   - 使用模拟对象减少外部依赖
   - 合理设置测试超时时间

## 📞 支持

如果在运行测试过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查测试日志和错误信息
3. 确认环境配置是否正确
4. 联系开发团队获取支持

---

**注意**: 本测试套件设计用于开发和CI/CD环境，确保LLM模块的稳定性和可靠性。定期运行测试有助于及早发现和修复问题。