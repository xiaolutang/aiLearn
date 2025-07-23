# 函数调用和增强搜索
# ai 入门搭建本地机器人
import asyncio
import os
import platform
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionToolParam, )

from learn02.ai_helper_prompt import ai_helper_prompt
from learn02.chat_tools.chat_tools import ChatTools
from learn02.message_manager.message_manager import MessageManager

# 加载 .env 文件
load_dotenv()  # 默认加载项目根目录的 .env 文件

try:
    # 初始化客户端（默认从环境变量 OPENAI_API_KEY 读取密钥）
    # api key
    client = OpenAI(
        # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("TONG_YI_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
except Exception as e:
    print(e)

system_prompt = ChatCompletionSystemMessageParam(
    role="system",
    content=ai_helper_prompt
)

messageManager = MessageManager(system_message=system_prompt,tools=ChatTools())
def on_message_change(messages: List[ChatCompletionMessageParam]):
    latest = messages[-1]
    print(f"XXXX：信息变化  ${latest}")
    content = latest.get("content", "")
    role = latest.get("role", "")
    tool_calls = latest.get("tool_calls")
    if role == "user":
        print("用户：" + content)
    elif role == "assistant" and content:
        print("助手：" + content)
    elif role == "assistant" and tool_calls:
        print("助手：" + "函数调用")
    else:
        print(f"未知角色：${content}")


messageManager.register_listener(on_message_change)

# 定义获取当前时间的函数
def get_current_time():
    print(f"get_current_time called at {datetime.now()}")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 定义工具（函数）的描述
tools: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间。",
            "parameters": {}
        }
    }
]

async def chat_to_llm(message:ChatCompletionMessageParam):
    messageManager.add_message(message)
    open_stream = False
    response = client.chat.completions.create(
        messages=messageManager.get_chat_to_llm_message(),
        model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        stream=open_stream,  # 是否流式输出 流式输出时 会将模型的输出流式返回，非流式输出时 会将完整的输出返回（有较长的等待期）不同的输出 结果处理方式会不同
        tools=tools,
        tool_choice="required",
    )
    messageManager.handle_chat_message(response, stream=open_stream)
# 定义异步任务列表
async def user_input(question):
    messageManager.add_message(ChatCompletionUserMessageParam(role="user", content=question))
    await chat_to_llm(ChatCompletionUserMessageParam(role="user", content=question))


# 主异步函数
async def main():
    while True:
        question = input("请输入问题：")
        if question == "exit":
            break
        await user_input(question)


if __name__ == '__main__':
    # 设置事件循环策略
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # 运行主协程
    asyncio.run(main(), debug=False)
