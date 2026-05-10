from abc import ABC, abstractmethod


class MongoService(ABC):

    @abstractmethod
    def search_vector(self, query_vector: list, top_k: int) -> list:
        pass