# src/application/ports/outbound/chat_history_repository_port.py
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage


class ChatHistoryRepositoryService(ABC):

    @abstractmethod
    def get_history(self, conversation_id: str) -> list[BaseMessage] | None:
        """Recupera el objeto de historial de chat asociado a la sesión."""
        pass

    @abstractmethod
    def add_message(self, conversation_id: str, message: Any):
        """Añade un nuevo mensaje al historial de la sesión. en cuanto el usuario le da intro tiene que recoger el dato
        de teams con el conversation_id"""
        pass

    @abstractmethod
    def add_ai_message(self, conversation_id: str, message: list[Document]):
        """
        Metodo para almacenar el contexto de la ia para tener preguntas y respuestas
        :param conversation_id:
        :param message:
        :return:
        """
        pass

    @abstractmethod
    def clear_history(self, conversation_id: str):
        """Elimina por completo el historial de esa sesión."""
        pass
