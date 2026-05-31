from typing import Any

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage

from src.application.service.session.ChatHistoryRepositoryService import ChatHistoryRepositoryService
from langchain_core.chat_history import InMemoryChatMessageHistory

class ChatHistoryRepositoryPortImpl(ChatHistoryRepositoryService):

    """
        inicio una libreria de langchain para almacenar en memoria, si fuera necesario se puede pasar a un redis para muchos
        usuarios solo cambiando la clase. Solo tengo que mantener un hashmap de sessiones y la cache en memoria para recuperar
        lo que me ha dicho el usuario
    """
    def __init__(self) -> None:
        self._store: dict[str, InMemoryChatMessageHistory] = {}


    def get_history(self, conversation_id: str) -> Any:
        return self._store.get(conversation_id)

    def add_message(self, conversation_id: str, message: str):
        history = self.get_history(conversation_id)
        if history is None:
            history = InMemoryChatMessageHistory()
            history.add_message(HumanMessage(content=message))
            self._store[conversation_id] = history
        else:
            history.add_message(HumanMessage(content=message))
    def add_ai_message(self, conversation_id: str, documents: list[Document]) -> None:
        history = self.get_history(conversation_id)
        history.add_message(AIMessage(content="Respuesta de mongo db con los documentos encontrados",
                                      additional_kwargs={
                                          "mongo_documents_raw": documents
                                      }
                                      ))

    def clear_history(self, conversation_id: str) -> None:
        if conversation_id in self._store:
            self._store[conversation_id].clear()


