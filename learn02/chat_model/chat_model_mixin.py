from abc import abstractmethod, ABC

from learn02.context.chat_context_interface import ChatContextInterface


class ChatModelMixin(ABC):
    def __init__(self, ):
        super(ChatModelMixin, self).__init__()

    @abstractmethod
    def chat_to_llm(self, chat_context: ChatContextInterface):
        pass
