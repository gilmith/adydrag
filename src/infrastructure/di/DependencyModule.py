from injector import Module, singleton, provider
from langchain_core.embeddings import Embeddings

from src.infrastructure.adapters.session.ChatHistoryRepositoryPortImpl import ChatHistoryRepositoryPortImpl
from src.application.service.session.ChatHistoryRepositoryService import ChatHistoryRepositoryService
from src.domain.service.ResponseFromRagService import ResponseFromRagService
from src.application.service.ResponseFromRagServiceImpl import ResponseFromRagServiceImpl
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.adapters.mongo.MongoServiceImpl import MongoServiceImpl
from src.infrastructure.adapters.ollama.OllamaServiceImpl import OllamaServiceImpl
from src.infrastructure.config.Settings import Settings


class DependencyModule(Module):
    @singleton
    @provider
    def provide_settings(self) -> Settings:
        return Settings()

    @singleton
    @provider
    def provide_embeddings(self, ollama_service: OllamaService) -> Embeddings:
        return ollama_service.get_embeddings_model()

    @singleton
    @provider
    def provide_db(self, settings: Settings, embeddings: Embeddings) -> MongoService:
        return MongoServiceImpl(settings, embeddings)

    @singleton
    @provider
    def provide_ollama(self, settings: Settings) -> OllamaService:
        if settings.ollama_url:
            return OllamaServiceImpl(settings)
        return None

    @singleton
    @provider
    def provide_chat_history(self) -> ChatHistoryRepositoryService:
        return ChatHistoryRepositoryPortImpl()

    @singleton
    @provider
    def provide_response(self, ollama_service: OllamaService, mongo_service: MongoService, settings: Settings,
                         chat_history : ChatHistoryRepositoryService) -> ResponseFromRagService:
        if ollama_service:
            return ResponseFromRagServiceImpl(ollama_service, mongo_service, settings, chat_history)
        return None