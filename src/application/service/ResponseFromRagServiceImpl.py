from typing import Optional

from langchain_classic.retrievers import SelfQueryRetriever

from src.domain.service.ResponseFromRagService import ResponseFromRagService
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.config.Settings import Settings
from loguru import logger
class ResponseFromRagServiceImpl(ResponseFromRagService):

    def __init__(self, olla_service: Optional[OllamaService], mongo_service: MongoService, settings: Settings):
        self._olla_service = olla_service
        self._mongo_service = mongo_service
        self._settings = settings

    def execute_rag_service(self, query: str):
        if self._olla_service:
            embeddings = self._olla_service.create_user_embeddings(query)
            vector_response = self._mongo_service.max_marginal_relevance_search_by_vector(embeddings)
            for response in vector_response:
                name = response.metadata.get("name")
                summarize =  self._olla_service.summarize_result(vector_response, query)
                return {
                    "summary": summarize,
                    "metadata": response.metadata
        }

