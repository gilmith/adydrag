from abc import abstractmethod, ABC

from langchain_core.documents import Document


class IAService(ABC):

    @abstractmethod
    def summarize_result(self, conversation_id: str, documents: list[Document], user_query: str) -> str:
        pass

    @abstractmethod
    def generate_classification_prompt(self, conversation_id: str, documents: list, user_query: str) -> str:
        pass