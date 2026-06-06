from typing import Optional

import numpy as np
from injector import inject
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from src.application.service.IAService import IAService
from src.application.service.session.ChatHistoryRepositoryService import ChatHistoryRepositoryService
from src.domain.model.MultipleDocument import MultipleDocument
from src.domain.service.ResponseFromRagService import ResponseFromRagService
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.config.Settings import Settings
from loguru import logger
class ResponseFromRagServiceImpl(ResponseFromRagService):

    @inject
    def __init__(self, olla_service: Optional[OllamaService], mongo_service: MongoService, settings: Settings,
                 chat_history_repository: ChatHistoryRepositoryService, ia_service: IAService):
        self._olla_service = olla_service
        self._mongo_service = mongo_service
        self._settings = settings
        self._chat_history_repository = chat_history_repository
        self._ia_service = ia_service


    """
        servicio de guardado de id de conversaciones para ver si lo tiene en el historial
        y no bajar a la bbdd y poder responder sobre el contexto de la conversacion
    """
    def save_conversation(self, conversation_id: str, user_text: str):
        self._chat_history_repository.add_message(conversation_id, user_text)
        pass




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



    def execute_rag_service(self, query: str, conversation_id: str):
        if len(self._chat_history_repository.get_history(conversation_id)) > 0:
            full_history = self._chat_history_repository.get_history(conversation_id)
            logger.info("iterando sobre la conversacion anterior para buscar el termino que ha elegido el usuario, si no tiene suficiente similitud, busca en base de datos")
            #ejecuta el comparador semantico sobre el campo name de la conversacion anterior, si encuentra una similitud mayor al 0.75, devuelve el resultado de esa conversacion, sino ejecuta la consulta a mongo
            user_option_selected = self._compare_name_embeddings(full_history, query)
            #TODO si no encuentra nada parecido en el hsitorial lo que tiene que hacer es cambiar y ejecutar el otro ollama service
            summarize = self._olla_service.summarize_result([user_option_selected], query)
            return {
                "summary": summarize
            }
        if self._olla_service:
            self.save_conversation(conversation_id, query)
            vector_response = self._mongo_service.hybrid_search(query)
            if len(vector_response) == 0:
                return {"output_text": "Lo siento, no pude encontrar información relevante para tu pregunta."}
            elif len(vector_response) == 1:
                logger.debug(self._show_query_result(vector_response))
                for response in vector_response:
                    summarize =  self._ia_service.summarize_result(conversation_id, vector_response, query)
                    return {
                        "summary": summarize
                    }
            else:
                logger.debug(self._show_query_result(vector_response))
                multiple_documents_data = self._generate_multiple_documents(vector_response)
                self._chat_history_repository.add_ai_message(conversation_id, vector_response)
                summarize = self._ia_service.generate_classification_prompt(conversation_id, multiple_documents_data, query)
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

    def _compare_name_embeddings(self, full_history, query) -> Document:
        user_embedding = self._olla_service.create_user_embeddings(query)
        for message in full_history.messages:
            if isinstance(message, AIMessage):
                for mongo_document in message.additional_kwargs.get("mongo_documents_raw", []):
                    name_embedding = self._olla_service.create_user_embeddings(mongo_document.metadata.get("name"))
                    similarity = self._calculate_cosine_similarity(user_embedding, name_embedding)
                    logger.info(f"similarity: {similarity} for user query: {query}")
                    if similarity > 0.85:
                        return mongo_document
        return None

        pass

    def _calculate_cosine_similarity(self, user_embedding, name_embedding):
            """Devuelve un valor entre -1 y 1 (donde 1 es semánticamente idéntico)."""
            dot_product = np.dot(user_embedding, name_embedding)
            norm_a = np.linalg.norm(user_embedding)
            norm_b = np.linalg.norm(name_embedding)
            return float(dot_product / (norm_a * norm_b))

