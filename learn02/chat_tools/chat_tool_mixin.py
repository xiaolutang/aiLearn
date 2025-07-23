from abc import abstractmethod, ABC
from typing import List

from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageParam, ChatCompletion, \
    ChatCompletionMessageToolCallParam, ChatCompletionToolMessageParam, ChatCompletionChunk


class ToolsProviderMixIn(ABC):
    def __init__(self, ):
        super().__init__()

    @abstractmethod
    def get_tools(self) -> List[ChatCompletionToolParam]:
        pass

    @abstractmethod
    def message_match_tool(self, message: ChatCompletion|ChatCompletionChunk) -> bool:
        pass

    @abstractmethod
    def tools_call(self, message: ChatCompletion) -> List[ChatCompletionToolMessageParam]:
        pass