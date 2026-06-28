from datetime import timezone, datetime
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_mongodb import MongoDBChatMessageHistory
from pymongo import MongoClient

from src.infrastructure.adapters.mongo.TTLMongoDBChatHistory import TTLMongoDBChatHistory
from src.application.service.session.ChatHistoryRepositoryService import ChatHistoryRepositoryService
from src.infrastructure.config.Settings import Settings


class ChatHistoryMongoRepositoryServiceImpl(ChatHistoryRepositoryService):

    def __init__(self, settings: Settings):
        self._client = MongoClient(settings.mongo_uri)
        self._collection_name = settings.chat_history_collection
        self._db_name = settings.mongo_db_name
        self._native_collection = self._client[self._db_name][self._collection_name]

    def _build_history_connection(self, conversation_id: str) -> MongoDBChatMessageHistory:
        return TTLMongoDBChatHistory(
            connection_string="",  # Vacío porque pasamos el cliente ya conectado
            collection_name=self._collection_name,
            database_name=self._db_name,
            session_id=conversation_id,
            history_size=10,  # LangChain ya se encarga de truncar a 10 automáticamente
            client=self._client
        )

    def get_history(self, conversation_id: str) -> list[BaseMessage]:
        mongo_history = self._build_history_connection(conversation_id)
        return mongo_history.messages

    def clear_history(self, conversation_id: str):
        mongo_history = self._build_history_connection(conversation_id)
        mongo_history.clear()

    def add_message(self, conversation_id: str, message: str) -> None:
        mongo_history = self._build_history_connection(conversation_id)
        mongo_history.add_user_message(message)

    def add_ai_message(self, conversation_id: str, message: list[Document]) -> None:
        mongo_history = self._build_history_connection(conversation_id)
        docs_serializables = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in message
        ]
        mongo_history.add_message(
            AIMessage(
                content="Respuesta de mongo db con los documentos encontrados",
                additional_kwargs={"mongo_documents_raw": docs_serializables}
            )
        )

