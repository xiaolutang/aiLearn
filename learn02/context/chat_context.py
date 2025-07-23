from typing import Optional, List, Union

from openai import Stream
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionMessageParam, ChatCompletion, \
    ChatCompletionChunk, ChatCompletionUserMessageParam

from learn02.chat_display.chat_display_mixIn import ChatDisplayMixIn
from learn02.chat_model.chat_model_mixin import ChatModelMixin
from learn02.chat_tools.chat_tool_mixin import ToolsProviderMixIn
from learn02.context.chat_context_interface import ChatContextInterface
from learn02.message_manager.message_manager import MessageManager

class ChatContext(ChatContextInterface):
    def __init__(self, *, stream: bool, chat_model: ChatModelMixin, display: Optional[ChatDisplayMixIn],
                 system_message: Optional[ChatCompletionSystemMessageParam] = None,
                 tools_provider: Optional[ToolsProviderMixIn] = None):
        super().__init__()
        self.chat_model = chat_model
        self.stream = stream
        self.display = display
        self.message_manager = MessageManager(system_message=system_message)
        self.message_manager.register_listener(listener=self.__on_message_change)
        self.tools_provider = tools_provider

    def __on_message_change(self, messages: List[ChatCompletionMessageParam | ChatCompletion]):
        message = messages[-1]

        print("助手：" +f"__on_message_change === ${message}")

        if self.tools_provider.message_match_tool(message):
            # 工具调用
            tools_response_message = self.tools_provider.tools_call(message)
            self.message_manager.add_tools_message(tools_response_message)
            return
        elif isinstance(message, ChatCompletion):
            self.display.on_message_change(messages)
            return
        elif isinstance(message, ChatCompletionChunk):
            self.display.on_message_change(messages)
            return
        role = message.get("role")
        if role == "assistant":
            print("助手：" + messages[-1].get("content"))
            self.display.on_message_change(messages)
        elif role == "tool":
            print("工具：" + "调用大模型")
            self.display.on_message_change(messages)
            self.__handle_llm_response(self.chat_model.chat_to_llm(self))
        elif role == "user":# 用户输入
            print("用户：调用大模型")
            self.display.on_message_change(messages)
            self.__handle_llm_response(self.chat_model.chat_to_llm(self))
        else:
            pass


    def __handle_llm_response(self, response: Union[ChatCompletion, Stream[ChatCompletionChunk]]):
        """
        处理响应，返回结构化结果
        :param response: 响应对象
        :return: 结构化结果
        """
        self.__handle_chat_message(response, self.stream)

    def input_string(self,question: str):
        """
        输入字符串
        :param question:
        :return:
        """
        message = ChatCompletionUserMessageParam(role="user", content=question)
        self.message_manager.add_message(message)

    def __handle_chat_message(self, response: Union[ChatCompletion, Stream[ChatCompletionChunk]], stream: bool = False):
        """
        处理响应，返回结构化结果
        :param response: 响应对象
        :param stream: 是否为流式响应
        :return: 包含 content、tool_calls 等字段的字典
        """
        if stream:
            self._handle_streaming_response(response)
        else:
            self._handle_non_streaming_response(response)

    def _handle_non_streaming_response(self, response: ChatCompletion):
        """
        处理非流式响应
        :param response: ChatCompletion 对象
        :return: 结构化结果
        """
        self.message_manager.add_message(response)

    def _handle_streaming_response(self, response: Stream[ChatCompletionChunk]):
        """
        处理流式响应，逐步读取并拼接内容
        :param response: ChatCompletionChunk 生成器
        :return: 包含完整内容的字典
        """
        for chunk in response:
            self.message_manager.add_c_message(chunk)

