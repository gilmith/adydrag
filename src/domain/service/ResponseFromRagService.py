from abc import ABC, abstractmethod



class ResponseFromRagService(ABC):

    @abstractmethod
    def execute_rag_service(self, query: str):
        pass