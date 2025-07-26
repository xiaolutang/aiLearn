from datetime import datetime
from typing import List

from openai.types.chat import ChatCompletionToolParam, ChatCompletion, ChatCompletionToolMessageParam, \
    ChatCompletionChunk

from learn02.chat_tools.chat_tool_mixin import ToolsProviderMixIn


class ChatTools(ToolsProviderMixIn):
    def __init__(self, ):
        super().__init__()
        self.calling_tools = {}

    def tools_call(self, message: ChatCompletion | ChatCompletionChunk) -> List[ChatCompletionToolMessageParam]:
        if isinstance(message, ChatCompletion):  # 可能是多个异步函数 当前先这样
            return self.dispatch_tool_call(message)
        if isinstance(message, ChatCompletionChunk):
            if self.calling_tools.get(message.id):
                if message.choices[0].finish_reason == "tool_calls":
                    self.calling_tools.pop(message.id)
                    return []
            else:
                self.calling_tools[message.id] = message
                return self.dispatch_tool_call(message)
            return []
        return []

    def dispatch_tool_call(self, message: ChatCompletion | ChatCompletionChunk):
        tool_response: List[ChatCompletionToolMessageParam] = []
        if isinstance(message, ChatCompletion):
            for tool_call in message.choices[0].message.tool_calls:
                if tool_call.function.name == "get_current_time":
                    current_time = self.get_current_time()
                    tool_response.append(
                        ChatCompletionToolMessageParam(role="tool", content=current_time, tool_call_id=tool_call.id))
        else:
            for tool_call in message.choices[0].delta.tool_calls:
                if tool_call.function.name == "get_current_time":
                    current_time = self.get_current_time()
                    tool_response.append(
                        ChatCompletionToolMessageParam(role="tool", content=current_time, tool_call_id=tool_call.id))
        return tool_response

    def get_current_time(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def message_match_tool(self, message: ChatCompletion | ChatCompletionChunk) -> bool:
        if isinstance(message, ChatCompletion):
            if message.choices[0].message.tool_calls:
                return True
        elif isinstance(message, ChatCompletionChunk):
            if message.choices[0].delta.tool_calls:
                return True
        return False

    def get_tools(self) -> List[ChatCompletionToolParam]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "获取当前时间",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]
