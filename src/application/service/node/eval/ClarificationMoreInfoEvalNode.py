from injector import inject

from src.application.service.node.eval.EvalNode import EvalNode
from src.domain.model.state.StateData import State
from src.infrastructure.adapters.ollama.OllamaService import OllamaService


class ClarificationMoreInfoEvalNode(EvalNode):
    @inject
    def __init__(self, llm_service: OllamaService):
        self._llm_service = llm_service

    def evaluate(self, state: State) -> str:
        clarification_or_more_info = self._llm_service.is_clarification_more_info(state.user_query)
        if clarification_or_more_info.is_clarification:
            return "summarize"
        return "error_cleanup_node"