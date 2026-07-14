from langgraph.types import Command
from langgraph.graph import END
from loguru import logger

from application.service.node.process.Node import Node
from src.domain.model.state.StateData import State


class GlobalErrorNode(Node):
    def __init__(self):
        super().__init__()

    def execute(self, state: State) -> Command:
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