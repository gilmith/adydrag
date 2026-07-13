from abc import ABC, abstractmethod


class GraphService(ABC):

    @abstractmethod
    def invoke_graph(self, query: str, conversation_id: str):
        pass