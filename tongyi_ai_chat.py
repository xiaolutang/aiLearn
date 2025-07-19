# ai 入门搭建本地机器人
import asyncio
import platform

from httpx import stream
from openai import OpenAI
from dotenv import load_dotenv
import os
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam, ChatCompletionMessageParam,
)

# 加载 .env 文件
load_dotenv()  # 默认加载项目根目录的 .env 文件

system_prompt = ChatCompletionSystemMessageParam(
    role="system",
    content="""
你是一个专业的 AI 教师助手，专注于为学生提供完整、准确、易于理解的回答。
当学生提出问题时，你需要：
1. 使用中文回答。
2. 确保回答完整，覆盖问题的所有方面。
3. 使用清晰的结构，如分点说明、分步骤解释。
4. 如果涉及公式、定义或知识点，请尽量引用权威来源或标准解释。
5. 避免模糊、简略或不确定的回答。
6. 如果问题需要计算或推理，提供详细过程。
7. 对复杂问题进行分段，便于学生理解。
8.在准确解答的同时穿插搞笑表情包语言（比如[挠头emoji]）
9. 如果问题超出你的知识范围，请如实告知，并建议查阅相关资料或咨询老师。

请以专业、耐心、友好的态度回答学生的问题。
"""
)

messages: list[ChatCompletionMessageParam] = [system_prompt]

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


# 定义异步任务列表
async def task(question):
    print(f"Sending question: {question}")
    #将问题插入消息列表
    messages.append(ChatCompletionUserMessageParam(role="user", content=question))
    response = client.chat.completions.create(
        messages=messages,
        model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        stream=True,
    )
    full_response = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content
            print(content, end="")

    # print("\n完整回答：", full_response)
    print("\n")
    messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=full_response))


# 主异步函数
async def main():
    while True:
        question = input("请输入问题：")
        if question == "exit":
            break
        await task(question)


if __name__ == '__main__':
    # 设置事件循环策略
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # 运行主协程
    asyncio.run(main(), debug=False)
