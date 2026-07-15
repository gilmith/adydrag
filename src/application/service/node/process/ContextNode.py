import uuid
from typing import Optional, Union

from injector import inject
from langgraph.store.base import BaseStore
from langgraph.store.mongodb import MongoDBStore
from langgraph.types import Command
from pymongo import MongoClient
from loguru import logger

from src.application.service.node.process.Node import Node
from src.infrastructure.adapters.mongo.MongoStore import MongoStore
from src.domain.model.state.StateData import State


class ContextNode(Node):
    def execute(self, state: State, mongo_store: Optional[BaseStore] = None) -> Union[State, Command]:
        if mongo_store is not None:
            value = mongo_store.search(
                ("context_history", state.conversation_id)
            )
            key_unica = f"trace_{uuid.uuid4().hex}"

            from datetime import datetime
            mongo_store.put(
                namespace=("context_history", state.conversation_id),
                key=key_unica,
                value={"query": state.user_query, "timestamp": datetime.now().isoformat()}
            )
            logger.info("value: " + str(value))
        return state

    @inject
    def __init__(self):
        super().__init__()



