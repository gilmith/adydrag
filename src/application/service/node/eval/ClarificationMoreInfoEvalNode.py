from typing import Optional

from injector import inject
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.store.mongodb import MongoDBStore

from application.service.exception.NodeException import NodeException
from application.service.node.NodeList import NodeList
from src.application.service.node.eval.EvalNode import EvalNode
from src.domain.model.state.StateData import State, LogLevel
from src.infrastructure.adapters.ollama.OllamaService import OllamaService


class ClarificationMoreInfoEvalNode(EvalNode):
    @inject
    def __init__(self, llm_service: OllamaService):
        self._llm_service = llm_service

    def evaluate(self, state: State, config: RunnableConfig) -> str:
        if self._has_context(state.conversation_id, config.get("configurable")['custom_mongo_store']):
            clarification_or_more_info = self._llm_service.is_clarification_more_info(state.user_query)
            if clarification_or_more_info.is_clarification:
                return NodeList.REQUESTION
            elif clarification_or_more_info.is_more_info:
                return NodeList.K_NEAREST_NEIGHBORS
            else:
                return NodeList.RETRIEVER
        return NodeList.RETRIEVER

    def _has_context(self, conversation_id: str, mongo_store: MongoDBStore):
        if mongo_store:
            result = mongo_store.search(
                ("context_history", conversation_id),
                limit=1
            )
            return len(result) > 0
        else:
            raise NodeException("No se ha iniciado la base de datos", LogLevel.ERROR)
