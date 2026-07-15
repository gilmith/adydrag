from typing import Optional, Union

from injector import inject
from langchain_core.documents import Document
from langgraph.store.base import BaseStore
from langgraph.store.mongodb import MongoDBStore
from langgraph.types import Command

from src.infrastructure.adapters.mongo.MongoStore import MongoStore
from src.application.service.exception.NodeException import NodeException
from src.domain.model.state.StateData import LogLevel, Metadata
from application.service.node.process.Node import Node
from src.domain.model.state.StateData import State, StateData
from src.infrastructure.adapters.mongo.MongoService import MongoService


class RetrieverNode(Node):
    @inject
    def __init__(self, mongo_service: MongoService):
        super().__init__()
        self.name = self.__class__.__name__
        self._mongo_service = mongo_service

    def execute(self, state: State, mongo_store: Optional[BaseStore] = None) -> Union[State, Command]:
        hybrid_search = self._mongo_service.hybrid_search(state.user_query)
        if len(self._has_text_score(hybrid_search)) == 0:
            exception = NodeException("No se encontraron resultados", LogLevel.WARNING)
            raise exception
        #TODO arreglar esto esta obviamente mal solo va a pescar el primero
        result = hybrid_search[0]
        metadata = Metadata(**result.metadata['metadata'])
        state_data = StateData(page_content=result.page_content, metadata=metadata, id=result.metadata['_id'], embedding=None, documents=hybrid_search)
        state.states = [state_data]
        return state

    @staticmethod
    def _has_text_score(retrieved_documents: list[Document]) -> list[Document]:
        has_text_score = lambda doc: doc.metadata['fulltext_score'] > 0
        return list(filter(has_text_score, retrieved_documents))