from abc import ABC, abstractmethod



class ResponseFromRagService(ABC):

    @abstractmethod
    def execute_rag_service_score(self, query: str):
        pass

    @abstractmethod
    def execute_rag_service_max(self, query: str):
        pass

    @abstractmethod
    def execute_rag_service(self, query: str, conversation_id: str):
        pass

    @abstractmethod
    def save_conversation(self, id: str, user_text:str):
        pass