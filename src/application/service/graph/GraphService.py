from abc import ABC, abstractmethod

from langchain_core.runnables import RunnableConfig


class GraphService(ABC):

    @abstractmethod
    def invoke_graph(self, query: str, conversation_id: str):
        pass