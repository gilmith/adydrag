from abc import ABC, abstractmethod

from langchain_core.documents import Document


class MongoService(ABC):

    @abstractmethod
    def search_vector(self, query_vector: list[float], pre_filter: list[str]):
        pass

    @abstractmethod
    def search_vector_without_pre_filter(self, query_vector :list[float]):
        pass

    @abstractmethod
    def max_marginal_relevance_search_by_vector(self, query_vector: list[float]):
        pass

    @abstractmethod
    def similarity_search_by_vector_with_score(self, query_vector: list[float]):
        pass

    @abstractmethod
    def as_retriever(self, query : str, k : int, threshold : float) -> list[Document]:
        pass

    @abstractmethod
    def hybrid_search(self, query: str):
        pass