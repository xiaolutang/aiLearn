from abc import ABC, abstractmethod
from typing import List, Callable

from openai.types.chat import ChatCompletionMessageParam, ChatCompletion


class ChatDisplayMixIn(ABC):
    def __init__(self,):
        pass

    @abstractmethod
    def on_message_change(self, messages: List[ChatCompletionMessageParam | ChatCompletion]) -> None:
        pass