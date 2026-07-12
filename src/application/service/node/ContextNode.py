from injector import inject
from loguru import logger
from pymongo import MongoClient

from src.application.service.node.Node import Node
from src.domain.model.state.StateData import State


class ContextNode(Node):
    @inject
    def __init__(self, mono_client: MongoClient):
        super().__init__()
        self.name = self.__class__.__name__
        self._mongo_client = mono_client
        self._db_name = mono_client['adyd_rag']
        self._collection_name = self._db_name['chat_history']

    def execute(self, state: State) -> State:
        context_history = self._collection_name.find_one(state.conversation_id)
        if context_history:
            state.context_history = context_history['context_history']
        return state