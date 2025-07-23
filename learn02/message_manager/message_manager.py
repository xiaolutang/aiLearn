import json
from typing import List, Optional, Callable, Union, Dict, Any, Iterable

from openai.types.chat import ChatCompletionAssistantMessageParam
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, ChatCompletion, \
    ChatCompletionChunk, ChatCompletionMessageToolCallParam, ChatCompletionToolMessageParam

from learn02.message_manager.message_adapter import MessageAdapter


class MessageManager:
    def __init__(self, *, system_message: Optional[ChatCompletionSystemMessageParam] = None):
        """
        初始化消息管理器
        :param system_message: 可选的系统消息，若未提供则使用默认系统提示
        """
        self.__messages: List[ChatCompletionMessageParam | ChatCompletion | ChatCompletionChunk] = []

        # 设置默认系统提示（可替换）
        default_system = ChatCompletionSystemMessageParam(
            role="system",
            content="你是一个有用的助手。"
        )

        self.__messages.append(system_message if system_message else default_system)

        # 保存监听回调函数列表
        self.__listeners: List[Callable[[List[ChatCompletionMessageParam | ChatCompletion]], None]] = []

    def add_message(self, message: ChatCompletionMessageParam | ChatCompletion):
        """
        添加用户消息
        :param message: 用户输入内容/
        """
        self.__messages.append(message)
        self.__notify_listeners()

    def add_c_message(self, message: ChatCompletionChunk):
        """
        添加用户消息
        :param message: 用户输入内容/
        """

        if self.__messages and len(self.__messages) > 0:
            last_message = self.__messages[-1]
            if isinstance(last_message, ChatCompletionChunk):
                messages = self.merge_chat_completion_chunks(last_message, message)
                self.__messages.extend(messages)
            else:
                self.__messages.append(message)
        else:
            self.__messages.append(message)
        self.__notify_listeners()

    from typing import List
    from openai.types.chat import ChatCompletionChunk

    @staticmethod
    def merge_chat_completion_chunks(
            chunk1: ChatCompletionChunk, chunk2: ChatCompletionChunk
    ) -> List[ChatCompletionChunk]:
        """
        如果两个 ChatCompletionChunk 的 id 相同，则合并成一个新的 ChatCompletionChunk；
        否则直接将两个对象放入列表中返回。
        """
        if chunk1.id == chunk2.id:
            # 合并两个 chunk，优先取非空字段
            def choose_non_empty(a, b):
                return a if a is not None else b

            # 合并 choices 字段
            merged_choices = []
            for c1, c2 in zip(chunk1.choices, chunk2.choices):
                # 获取两个delta的字典表示
                delta1_dict = c1.delta.model_dump()
                delta2_dict = c2.delta.model_dump()

                # 创建更新字典
                update_dict = {}
                for k, v in delta1_dict.items():
                    # 特别处理content字段，进行拼接
                    if k == 'content' and v is not None and delta2_dict.get(k) is not None:
                        update_dict[k] = (v or '') + (delta2_dict[k] or '')
                    else:
                        # 其他字段使用原有的choose_non_empty逻辑
                        update_dict[k] = choose_non_empty(v, delta2_dict.get(k))

                # 应用更新创建新的delta
                delta = c1.delta.model_copy(update=update_dict)
                merged_choice = c1.model_copy(update={"delta": delta})
                merged_choices.append(merged_choice)

            merged_chunk = ChatCompletionChunk(
                id=choose_non_empty(chunk1.id, chunk2.id),
                choices=merged_choices,
                created=choose_non_empty(chunk1.created, chunk2.created),
                model=choose_non_empty(chunk1.model, chunk2.model),
                object=choose_non_empty(chunk1.object, chunk2.object),
                system_fingerprint=choose_non_empty(chunk1.system_fingerprint, chunk2.system_fingerprint),
            )
            return [merged_chunk]
        else:
            # id 不相同，直接返回两个对象
            return [chunk1, chunk2]

    def add_tools_message(self, tools_messages: List[ChatCompletionToolMessageParam], ):
        """
        工具调用结果消息
        :param tools_messages:
        """
        if len(tools_messages) == 0:
            return
        self.__messages.extend(tools_messages)
        self.__notify_listeners()

    def add_assistant_message(self, content: Optional[str] = None,
                              tool_calls: Optional[Iterable[ChatCompletionMessageToolCallParam]] = None):
        """
        添加助手消息
        :param tool_calls:
        :param content: 助手回复内容
        """
        self.add_message(ChatCompletionAssistantMessageParam(role="assistant", content=content, tool_calls=tool_calls))

    def get_messages(self) -> List[ChatCompletionMessageParam]:
        """
        获取当前消息列表（只读副本）
        :return: 消息列表
        """
        return self.__messages.copy()

    def get_chat_to_llm_message(self) -> List[ChatCompletionMessageParam]:
        """
        获取当前传递给大模型消息列表（只读副本）
        :return: 消息列表
        """
        result: List[ChatCompletionMessageParam] = []

        for message in self.__messages:
            # 对于字典类型的对象，通过role字段判断
            if isinstance(message, dict):
                role = message.get('role')
                # 只添加有效的消息类型
                if role in ['user', 'system', 'assistant']:
                    result.append(message)
                elif role == 'tool':
                    # 检查前一条消息是否包含tool_calls，只有在这种情况下才添加tool消息
                    if (len(result) > 0 and
                            isinstance(result[-1], dict) and
                            result[-1].get('role') == 'assistant' and
                            'tool_calls' in result[-1] and
                            result[-1]['tool_calls']):
                        result.append(message)
                    # 如果前一条消息不是对应的tool_calls响应，则跳过该tool消息
            elif isinstance(message, ChatCompletion):
                # ChatCompletion 转换为 ChatCompletionAssistantMessageParam
                assistant_message = MessageAdapter.chat_completion_to_assistant_message(message)
                result.append(assistant_message)
            elif isinstance(message, ChatCompletionChunk):
                # ChatCompletionChunk 转换为 ChatCompletionAssistantMessageParam
                assistant_message = MessageAdapter.chat_completion_chunk_to_assistant_message(message)
                result.append(assistant_message)

        return result

    def register_listener(self, listener: Callable[[List[ChatCompletionMessageParam | ChatCompletion]], None]):
        """
        注册监听器，当消息变化时调用
        :param listener: 回调函数，接收当前消息列表作为参数
        """
        self.__listeners.append(listener)

    def unregister_listener(self, listener: Callable[[List[ChatCompletionMessageParam | ChatCompletion]], None]):
        """
        注销监听器
        :param listener: 回调函数
        """
        self.__listeners.remove(listener)

    def __notify_listeners(self):
        """
        当消息变化时通知所有监听者
        """
        for listener in self.__listeners:
            listener(self.__messages)

    def clear_messages(self):
        """
        清除所有消息（保留系统消息）
        """
        system_message = self.__messages[0]
        self.__messages.clear()
        self.__messages.append(system_message)
        self.__notify_listeners()

