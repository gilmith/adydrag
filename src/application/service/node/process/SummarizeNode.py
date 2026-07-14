from injector import inject

from application.service.node.process.Node import Node
from src.domain.model.state.StateData import State
from src.infrastructure.adapters.ollama.OllamaService import OllamaService


class SummarizeNode(Node):

    @inject
    def __init__(self, llm_service: OllamaService):
        super().__init__()
        self.name = self.__class__.__name__
        self._llm_service = llm_service

    def execute(self, state: State) -> State:
        if state.states:
            documents = state.states[0].documents
            state.llm_response = self._llm_service.summarize_result(state.conversation_id, documents, state.user_query)
        return state
