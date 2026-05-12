from abc import ABC, abstractmethod


class MongoService(ABC):

    @abstractmethod
    def search_vector(self, query_vector: list[float], pre_filter: list[str]):
        pass