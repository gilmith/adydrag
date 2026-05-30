from typing import Optional

from langchain_core.documents import Document

from src.domain.model.MultipleDocument import MultipleDocument
from src.domain.service.ResponseFromRagService import ResponseFromRagService
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.config.Settings import Settings
from loguru import logger
class ResponseFromRagServiceImpl(ResponseFromRagService):

    def execute_rag_service_score(self, query: str):
        if self._olla_service:
            vector_response = self._mongo_service.as_retriever(query, k=20, threshold=0.75)
            if len(vector_response) == 0:
                return {"output_text": "Lo siento, no pude encontrar información relevante para tu pregunta."}
            else:
                for response in vector_response:
                    summarize = self._olla_service.summarize_result(vector_response, query)
                    return {
                        "summary": summarize,
                        "metadata": response.metadata
                    }

    def __init__(self, olla_service: Optional[OllamaService], mongo_service: MongoService, settings: Settings):
        self._olla_service = olla_service
        self._mongo_service = mongo_service
        self._settings = settings

    def execute_rag_service(self, query: str):
        if self._olla_service:
            vector_response = self._mongo_service.hybrid_search(query)
            if len(vector_response) == 0:
                return {"output_text": "Lo siento, no pude encontrar información relevante para tu pregunta."}
            elif len(vector_response) == 1:
                logger.debug(self._show_query_result(vector_response))
                for response in vector_response:
                    summarize =  self._olla_service.summarize_result(vector_response, query)
                    return {
                        "summary": summarize
                    }
            else:
                logger.debug(self._show_query_result(vector_response))
                multiple_documents_data = self._generate_multiple_documents(vector_response)
                summarize = self._olla_service.generate_classification_prompt(multiple_documents_data, query)
                return {"summary": summarize}

    def execute_rag_service_max(self, query: str):
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

    def _show_query_result(self, documents: list[Document]) -> str:
        lineas = []
        for doc in documents:
            name = doc.metadata.get("name", "Sin nombre")
            score = doc.metadata.get("score", "N/A")
            rank = doc.metadata.get("rank", "N/A")
            lineas.append(f"{name}, score {score}, rank {rank}")

        # DEVOLVEMOS EL TEXTO, no lo logueamos aquí
        return "\n" + "\n".join(lineas)

    def _generate_multiple_documents(self, vector_response) -> list[MultipleDocument]:
        multiple_documents_data = [
            MultipleDocument(
                level=response.metadata.get("level", 0),
                rank=response.metadata.get("rank", 0),
                name=response.metadata.get("name", "Sin nombre"),
                full_text_score=response.metadata.get("fulltext_score", 0.0),
                vector_score=response.metadata.get("vector_score", 0.0)
            )
            for response in vector_response
        ]
        return multiple_documents_data
