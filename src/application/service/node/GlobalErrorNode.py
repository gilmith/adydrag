from langchain_protocol import Command
from langgraph.errors import NodeError

from application.service.node.Node import Node
from domain.model.state.StateData import State


class GlobalErrorNode(Node):
    """
        Nodo de escape. Se ejecuta únicamente si algo falla.
        Su único propósito es formatear una respuesta de error controlada para el usuario.
        """

    def execute(self, state: State) -> State:
        # 1. Recuperamos el mensaje de error o usamos uno por defecto si no existe

        # 2. Definimos una respuesta amigable para el usuario de Teams
        state.llm_response = (
            "Lo siento, he tenido un problema al consultar los manuales de transporte. "
            "Por favor, inténtalo de nuevo en unos momentos."
        )

        # 3. Opcional: Si quieres registrar más contexto en tus logs internos
        # state.logs.append(...) ya se gestiona en el template_method de la clase base

        return state
