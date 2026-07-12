from injector import Module, singleton, provider
from langchain_core.embeddings import Embeddings
from loguru import logger
from pymongo import MongoClient

from application.service.node import SummarizeNode
from src.application.service.IAService import IAService
from src.application.service.ResponseFromRagServiceImpl import ResponseFromRagServiceImpl
from src.application.service.node.ContextNode import ContextNode
from src.application.service.node.Node import Node
from src.application.service.node.RetrieverNode import RetrieverNode
from src.application.service.session.ChatHistoryRepositoryService import ChatHistoryRepositoryService
from src.domain.service.ResponseFromRagService import ResponseFromRagService
from src.infrastructure.adapters.azure.IAServiceImpl import IAServiceImpl
from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.adapters.mongo.MongoServiceImpl import MongoServiceImpl
from src.infrastructure.adapters.ollama.LlamaCPPServiceImpl import LlamaCPPServiceImpl
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.adapters.session.ChatHistoryMongoRepositoryServiceImpl import \
    ChatHistoryMongoRepositoryServiceImpl
from src.infrastructure.config.Settings import Settings
from src.infrastructure.di.NodesModule import RetrieverNodeKey, ContextNodeKey, SummarizeNodeKey


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
            return LlamaCPPServiceImpl(settings)
        return None

    @singleton
    @provider
    def provide_azure(self, settings: Settings) -> IAService:
        return IAServiceImpl(settings)

    @singleton
    @provider
    def provide_chat_history(self, settings: Settings) -> ChatHistoryRepositoryService:
        return ChatHistoryMongoRepositoryServiceImpl(settings)


    @singleton
    @provider
    def provide_response(self,
                         ollama_service: OllamaService,
                         mongo_service: MongoService, settings: Settings,
                         chat_history : ChatHistoryRepositoryService,
                         azure_service: IAService,
                         retriever_node: RetrieverNodeKey,
                         context_node: ContextNodeKey,
                         summarize_node: SummarizeNodeKey) -> ResponseFromRagService:
        if ollama_service:
            return ResponseFromRagServiceImpl(ollama_service, mongo_service, settings, chat_history, azure_service, retriever_node, context_node, summarize_node)
        return None



    @singleton
    @provider
    def provide_mongo_client(self, settings: Settings) -> MongoClient:
        return MongoClient(settings.mongo_uri)

    @singleton
    @provider
    def provide_context_node(self, mongo_client: MongoClient) -> Node:
        logger.info("Context node")
        return ContextNode(mongo_client)

    @singleton
    @provider
    def provide_llama_cpp(self, settings: Settings) -> OllamaService:
        if settings.ollama_url:
            return LlamaCPPServiceImpl(settings)
        return None

    @singleton
    @provider
    def provide_retriever_node(self, mongo_service: MongoService) -> Node:
        return RetrieverNode(mongo_service)

