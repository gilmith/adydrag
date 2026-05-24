from abc import ABC, abstractmethod


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