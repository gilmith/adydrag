from abc import ABC, abstractmethod

from langgraph.types import Command

from src.domain.model.state.StateData import State


class EvalNode(ABC):

    def route(self, state: State) -> str:
            return self.evaluate(state)

    @abstractmethod
    def evaluate(self, state: State) -> str:
        return self.route(state)
