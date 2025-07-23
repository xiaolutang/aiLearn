# message_adapter.py
from typing import List, Optional, Iterable
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallParam,
    ChatCompletionAssistantMessageParam
)


class MessageAdapter:
    """
    消息适配器类，用于在不同类型的消息格式之间进行转换
    """

    @staticmethod
    def tool_calls_to_param(
            tool_calls: Optional[List[ChatCompletionMessageToolCall]]
    ) -> Optional[Iterable[ChatCompletionMessageToolCallParam]]:
        """
        将 ChatCompletionMessageToolCall 列表转换为 ChatCompletionMessageToolCallParam 的可迭代对象

        :param tool_calls: 工具调用列表
        :return: 工具调用参数的可迭代对象
        """
        if not tool_calls:
            return None

        return [
            ChatCompletionMessageToolCallParam(
                id=tool_call.id,
                function={
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                },
                type=tool_call.type
            ) for tool_call in tool_calls
        ]

    @staticmethod
    def chat_completion_to_assistant_message(
            chat_completion: ChatCompletion
    ) -> ChatCompletionAssistantMessageParam:
        """
        将ChatCompletion对象转换为ChatCompletionAssistantMessageParam

        :param chat_completion: OpenAI的ChatCompletion响应对象
        :return: ChatCompletionAssistantMessageParam格式的消息
        """
        # 获取第一个choice的内容
        choice = chat_completion.choices[0]

        # 转换工具调用参数类型
        tool_calls_param = MessageAdapter.tool_calls_to_param(choice.message.tool_calls)

        # 创建助手消息参数
        assistant_message = ChatCompletionAssistantMessageParam(
            role="assistant",
            content=choice.message.content,
            tool_calls=tool_calls_param
        )

        return assistant_message

    @staticmethod
    def chat_completion_chunk_to_assistant_message(
            chat_completion_chunk: ChatCompletionChunk
    ) -> ChatCompletionAssistantMessageParam:
        """
        将ChatCompletionChunk对象转换为ChatCompletionAssistantMessageParam

        :param chat_completion_chunk: OpenAI的ChatCompletionChunk流式响应对象
        :return: ChatCompletionAssistantMessageParam格式的消息
        """
        # 获取第一个choice的内容
        choice = chat_completion_chunk.choices[0]

        # 转换工具调用参数类型
        tool_calls = None
        if hasattr(choice.delta, 'tool_calls'):
            tool_calls = choice.delta.tool_calls

        tool_calls_param = MessageAdapter.tool_calls_to_param(tool_calls)

        # 创建助手消息参数
        assistant_message = ChatCompletionAssistantMessageParam(
            role="assistant",
            content=choice.delta.content,
            tool_calls=tool_calls_param
        )

        return assistant_message

    @staticmethod
    def accumulate_chunks_to_assistant_message(
            chunks: List[ChatCompletionChunk]
    ) -> ChatCompletionAssistantMessageParam:
        """
        将多个ChatCompletionChunk累积成一个ChatCompletionAssistantMessageParam

        :param chunks: ChatCompletionChunk对象列表
        :return: ChatCompletionAssistantMessageParam格式的消息
        """
        if not chunks:
            return ChatCompletionAssistantMessageParam(role="assistant", content="")

        # 合并所有chunk的内容
        full_content = ""
        tool_calls = None

        for chunk in chunks:
            if chunk.choices and chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content

            # 如果有任何一个chunk包含tool_calls，则保留
            if chunk.choices and hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
                tool_calls = chunk.choices[0].delta.tool_calls

        # 转换工具调用参数类型
        tool_calls_param = MessageAdapter.tool_calls_to_param(tool_calls)

        return ChatCompletionAssistantMessageParam(
            role="assistant",
            content=full_content,
            tool_calls=tool_calls_param
        )
