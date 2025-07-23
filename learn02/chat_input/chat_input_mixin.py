from abc import abstractmethod, ABC

from openai.types.chat import ChatCompletionMessageParam, ChatCompletionUserMessageParam

from learn02.context.chat_context import ChatContext



class ChatInputMixin(ABC):
    def __init__(self,):
        pass
    @abstractmethod
    async def user_input(self) -> str:
        pass