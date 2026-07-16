from abc import ABC, abstractmethod

from langchain_core.runnables import RunnableConfig
from loguru import logger

from application.service.exception.NodeException import NodeException
from application.service.node.NodeList import NodeList
from src.domain.model.state.StateData import State


class EvalNode(ABC):

    def template_method(self, state, config: RunnableConfig):
        logger.info(f"Executing eval node {self.__class__.__name__}")
        try:
            return self.evaluate(state, config)
        except NodeException as e:
            logger.error(e)
            return NodeList.GLOBAL_ERROR


    def route(self, state: State, config: RunnableConfig) -> str:
        return self.template_method(state, config)

    @abstractmethod
    def evaluate(self, state: State, config: RunnableConfig) -> str:
        return self.route(state, config)
