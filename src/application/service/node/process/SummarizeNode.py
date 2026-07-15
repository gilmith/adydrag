from typing import Optional, Union

from injector import inject
from langgraph.store.base import BaseStore
from langgraph.store.mongodb import MongoDBStore
from langgraph.types import Command

from src.application.service.node.process.Node import Node
from src.infrastructure.adapters.mongo.MongoStore import MongoStore
from src.domain.model.state.StateData import State
from src.infrastructure.adapters.ollama.OllamaService import OllamaService


class SummarizeNode(Node):

    @inject
    def __init__(self, llm_service: OllamaService):
        super().__init__()
        self.name = self.__class__.__name__
        self._llm_service = llm_service

    def execute(self, state: State, mongo_store: Optional[BaseStore] = None) -> Union[State, Command]:
        if state.states:
            documents = state.states[0].documents
            state.llm_response = self._llm_service.summarize_result(state.conversation_id, documents, state.user_query)
        return state
