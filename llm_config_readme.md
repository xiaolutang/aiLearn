# LLM配置管理模块

## 设计背景

本模块旨在解决智能教学助手中大语言模型（LLM）配置的隔离问题，实现模型的灵活切换和统一管理。目前系统使用通义千问模型，但未来可能需要更换为其他模型（如OpenAI的GPT系列）。通过此模块，可以实现LLM配置与业务逻辑的解耦，便于后续扩展和维护。

## 设计思路

本模块采用了以下设计模式：

1. **策略模式**：定义了统一的`LLMInterface`接口，不同的LLM实现（如`TongYiLLM`、`OpenAILLM`）都实现这个接口，确保具有相同的方法签名。
2. **工厂模式**：通过`LLMCreator`工厂类创建不同类型的LLM实例，隐藏了具体实现的细节。
3. **单例模式**：`LLMConfig`类采用单例模式，确保全局只有一个配置实例，便于集中管理和访问。
4. **缓存机制**：为避免重复创建相同配置的LLM实例，实现了简单的缓存机制。

## 模块结构

```
├── llm_config.py          # 主要配置模块文件
├── test_llm_config.py     # 测试文件
└── llm_config_readme.md   # 说明文档
```

## 主要组件说明

### 1. LLMInterface

抽象基类，定义了与大语言模型交互的标准方法。所有具体的LLM实现都必须实现这个接口。

```python
class LLMInterface(ABC):
    @abstractmethod
    def generate_response(self, messages: list, model: str, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def stream_response(self, messages: list, model: str, **kwargs) -> Any:
        pass
```

### 2. 具体LLM实现

- **TongYiLLM**：通义千问大模型的实现
- **OpenAILLM**：OpenAI大模型的实现

这些实现类负责初始化对应的客户端，并提供与接口定义一致的方法。

### 3. LLMCreator

工厂类，负责创建不同类型的LLM实例。

```python
@staticmethod
def create_llm(llm_type: str, **kwargs) -> LLMInterface:
    llm_type = llm_type.lower()
    
    if llm_type == "tongyi":
        return TongYiLLM(**kwargs)
    elif llm_type == "openai":
        return OpenAILLM(**kwargs)
    else:
        raise ValueError(f"不支持的LLM类型: {llm_type}")
```

### 4. LLMConfig

配置管理类，采用单例模式，负责管理全局LLM设置和缓存LLM实例。

```python
class LLMConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
```

### 5. 工具函数

- **get_default_llm()**：获取默认的LLM实例
- **generate_llm_response()**：生成LLM响应的便捷函数

## 使用方法

### 1. 基本使用

```python
from llm_config import get_default_llm, generate_llm_response

# 获取默认LLM实例
llm = get_default_llm()

# 准备消息
messages = [
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "Hello!"}
]

# 获取流式响应
response = llm.stream_response(messages, model="qwen-plus")
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="")

# 或者使用便捷函数
response = generate_llm_response(
    messages=messages,
    model="qwen-plus",
    stream=True
)
```

### 2. 切换LLM模型

```python
from llm_config import global_llm_config

# 切换默认LLM为OpenAI
global_llm_config.set_default_llm("openai", "gpt-3.5-turbo")

# 之后获取的默认LLM就是OpenAI的实例了
llm = get_default_llm()
```

### 3. 临时使用特定LLM

```python
from llm_config import global_llm_config

# 临时使用特定配置的通义千问LLM
llm = global_llm_config.get_llm(
    "tongyi",
    api_key="temporary-api-key",
    base_url="https://custom-url.com"
)
```

### 4. 使用便捷函数

```python
from llm_config import generate_llm_response

# 使用便捷函数生成响应
response = generate_llm_response(
    messages=[{"role": "user", "content": "Hello!"}],
    model="qwen-plus",
    llm_type="tongyi",
    stream=True,
    temperature=0.7
)
```

## 配置环境变量

本模块支持通过环境变量进行配置：

- `TONG_YI_API_KEY`：通义千问的API密钥
- `OPENAI_API_KEY`：OpenAI的API密钥
- `DEFAULT_LLM_TYPE`：默认的LLM类型（如"tongyi"或"openai"）
- `DEFAULT_MODEL`：默认的模型名称（如"qwen-plus"或"gpt-3.5-turbo"）

## 扩展指南

### 添加新的LLM模型

要添加新的LLM模型，需要完成以下步骤：

1. 创建一个新的类，继承自`LLMInterface`接口
2. 实现`generate_response`和`stream_response`方法
3. 在`LLMCreator`类的`create_llm`方法中添加对新模型的支持

示例：

```python
# 1. 创建新的LLM实现类
class NewLLM(LLMInterface):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # 初始化代码
        pass
        
    def generate_response(self, messages: list, model: str, **kwargs) -> Any:
        # 实现代码
        pass
        
    def stream_response(self, messages: list, model: str, **kwargs) -> Any:
        # 实现代码
        pass

# 2. 在LLMCreator中添加支持
@staticmethod
def create_llm(llm_type: str, **kwargs) -> LLMInterface:
    llm_type = llm_type.lower()
    
    if llm_type == "tongyi":
        return TongYiLLM(**kwargs)
    elif llm_type == "openai":
        return OpenAILLM(**kwargs)
    elif llm_type == "new_llm":  # 添加新的支持
        return NewLLM(**kwargs)
    else:
        raise ValueError(f"不支持的LLM类型: {llm_type}")
```

### 自定义LLM配置

如果需要自定义LLM的配置逻辑，可以扩展`LLMConfig`类或直接修改现有的实现。

## 测试

本模块提供了完整的单元测试，可以通过以下命令运行：

```bash
python test_llm_config.py
```

测试涵盖了接口定义、具体实现、工厂类、配置管理和工具函数等各个方面，确保模块的功能正常工作。

## 注意事项

1. 使用前请确保已安装必要的依赖：`openai`、`python-dotenv`
2. 请妥善保管API密钥，避免泄露
3. 在生产环境中，建议使用环境变量或配置文件来管理敏感信息
4. 如遇问题，请检查日志输出或运行测试以定位问题

## 版本信息

- 版本：1.0
- 发布日期：2023-11-08
- 作者：智能教学助手研发团队