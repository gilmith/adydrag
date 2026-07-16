from typing import Optional

from injector import inject
from langgraph.graph import END
from langgraph.store.base import BaseStore
from langgraph.types import Command
from loguru import logger

from src.application.service.node.process.Node import Node
from src.domain.model.state.StateData import State


class GlobalErrorNode(Node):

    @inject
    def __init__(self):
        super().__init__()

    def execute(self, state: State, mongo_store: Optional[BaseStore] = None) -> Command:
        logger.info("Error en el nodo global")
        return Command(
            update={
                "llm_response": (
                    """Lo siento, he tenido un problema al consultar los grimorios y los papiros.
                        Reformula tu pregunta.
                    """
                )
            },
            goto=END  # Forzamos la finalización del grafo aquí
        )