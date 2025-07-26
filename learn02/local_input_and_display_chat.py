import asyncio
import os
import platform
import time
from typing import List

from openai.types.chat import ChatCompletionMessageParam, ChatCompletion, ChatCompletionSystemMessageParam

from learn02.ai_helper_prompt import ai_helper_prompt
from learn02.chat_display.chat_display_mixIn import ChatDisplayMixIn
from learn02.chat_input.chat_input_mixin import ChatInputMixin
from learn02.chat_model.ali_bai_lian_chat_model import AliBaiLianChatModel
from learn02.chat_tools.chat_tools import ChatTools
from learn02.context.chat_context import ChatContext


class LocalAiChatAndDisplay(ChatDisplayMixIn, ChatInputMixin):
    tag = "LocalAiChatAndDisplay"

    def __init__(self):
        super().__init__()
        # 创建日志文件，文件名包含当前时间
        self.log_file_name = f"ai助教-{time.strftime('%Y%m%d-%H%M%S')}.md"
        # 创建文件并写入初始内容
        with open(self.log_file_name, 'w', encoding='utf-8') as f:
            f.write(f"# AI助教对话记录\n\n")
            f.write(f"对话开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            # 强制刷新Python缓冲区
            f.flush()
            # 强制操作系统将数据写入磁盘
            os.fsync(f.fileno())

    async def user_input(self) -> str:
        question = input("请输入问题：")
        return question

    def on_message_change(self, messages: List[ChatCompletionMessageParam | ChatCompletion]) -> None:
        print(f"${self.tag}" + "--" * 20)
        print(messages[-1])
        print(f"${self.tag}" + "--" * 20)

        # 将消息内容写入日志文件
        self._write_message_to_log(messages[-1])

    def _write_message_to_log(self, message:ChatCompletionMessageParam | ChatCompletion):
        """
        将单条消息写入日志文件
        """
        with open(self.log_file_name, 'a', encoding='utf-8') as f:
            # 根据消息类型格式化内容
            if isinstance(message, ChatCompletion):
                role = message.choices[0].message.role
                content = message.choices[0].message.content
                function_call = message.choices[0].message.function_call
                f.write(f"## {role.capitalize()} 消息\n\n")
                if content:
                    f.write(f"{content}\n\n")
                if message.choices[0].finish_reason:
                    f.write(f"Finish Reason: {message.choices[0].finish_reason}\n\n")
                if function_call:
                    f.write(f"Function Call: {function_call}\n\n")
                f.write("---\n\n")
            else:
                role = message.get('role', 'unknown')
                content = message.get('content', '')
                f.write(f"## {role.capitalize()} 消息\n\n")
                if content:
                    f.write(f"{content}\n\n")
                f.write("---\n\n")
            # 强制刷新Python缓冲区
            f.flush()
            # 强制操作系统将数据写入磁盘
            os.fsync(f.fileno())

    async def start_local_chat(self, chat_context: ChatContext, user_input: ChatInputMixin):
        while True:
            question = await user_input.user_input()
            if question == "":
                continue
            if question == "exit":
                break
            chat_context.input_string(question)


async def start_local_chat():
    input_and_display = LocalAiChatAndDisplay()
    chat_context = ChatContext(
        chat_model=AliBaiLianChatModel(),
        stream=False,
        display=input_and_display,
        system_message=ChatCompletionSystemMessageParam(
            role="system",
            content=ai_helper_prompt
        ),
        tools_provider=ChatTools()
    )
    await input_and_display.start_local_chat(chat_context, input_and_display)


if __name__ == '__main__':
    # 设置事件循环策略
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # 运行主协程
    asyncio.run(start_local_chat(), debug=False)