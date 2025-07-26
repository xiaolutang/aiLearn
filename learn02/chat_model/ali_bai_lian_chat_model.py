import os

from dotenv import load_dotenv
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from learn02.chat_model.chat_model_mixin import ChatModelMixin
from learn02.context.chat_context import ChatContext


class AliBaiLianChatModel(ChatModelMixin):
    __client:OpenAI
    def __init__(self,):
        super().__init__()
        # 加载 .env 文件
        load_dotenv()  # 默认加载项目根目录的 .env 文件
        try:
            # 初始化客户端（默认从环境变量 OPENAI_API_KEY 读取密钥）
            # api key
            self.__client = OpenAI(
                # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
                api_key=os.getenv("TONG_YI_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
        except Exception as e:
            print(e)

    def chat_to_llm(self,chat_context:ChatContext)-> ChatCompletion | Stream[ChatCompletionChunk]:
        return self.__client.chat.completions.create(
            messages=chat_context.message_manager.get_chat_to_llm_message(),
            model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            stream=chat_context.stream,  # 是否流式输出 流式输出时 会将模型的输出流式返回，非流式输出时 会将完整的输出返回（有较长的等待期）不同的输出 结果处理方式会不同
            tools=chat_context.tools_provider.get_tools(),
            tool_choice="required",
            parallel_tool_calls=1,
        )