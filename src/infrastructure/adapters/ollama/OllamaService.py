from abc import ABC, abstractmethod

from langchain_core.documents import Document

from src.domain.model.ClarificationOrMoreInfo import ClarificationOrMoreInfo
from src.domain.model.MultipleDocument import MultipleDocument


class OllamaService(ABC):

    @abstractmethod
    def create_user_embeddings(self, query: str) -> list[float]:
        pass

    @abstractmethod
    def search_terms_in_user_query(self, query: str) -> list[str]:
        pass

    @abstractmethod
    def get_embeddings_model(self):
        pass

    @abstractmethod
    def summarize_result(self, conversation_id: str, result : list[Document], input_query: str):
        pass

    @abstractmethod
    def generate_classification_prompt(self, results: list[MultipleDocument], input_query: str):
        pass

    @abstractmethod
    def is_clarification_more_info(self, user_query: str) -> ClarificationOrMoreInfo:
        pass