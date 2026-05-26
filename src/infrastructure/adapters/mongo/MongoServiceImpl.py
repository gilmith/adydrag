from typing import cast, Collection, Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.config.Settings import Settings
from loguru import logger

class MongoServiceImpl(MongoService):

    """
        este metodo no necesita pasar por un embedding inicial, ya lo tiene cargado. Le digo el numero de vecinos a
        examinar y con eso y un umbral de confianza tendria que dar una lista de documentos encontrados y de ahi tendre
        que pillar el de mas puntos
    """
    def as_retriever(self, query: str, k: int, threshold: float) -> list[Document]:
        retriever = self._vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": threshold,
                "k": k
            })
        return retriever.invoke(query)

    def similarity_search_by_vector_with_score(self, query_vector: list[float]):
        return self._vector_store.similarity_search_with_relevance_scores(
            embedding = query_vector,
            k = 5)

    def max_marginal_relevance_search_by_vector(self, query_vector: list[float]):
        """
        Este metodo es el que le pides 20 parecidos y te da el mas parecido de todos sin buscar el scorel, es decir
        , el que tiene la mayor relevancia marginal. Es útil para evitar resultados redundantes.
        con el multiplicador lambda_multi puedes ajustar el equilibrio entre relevancia y diversidad.
        No tiene un parametro de score para ver lo parecido que es el resultado y pasar el sumarize del llm.
        Puedes poner el hola y responder algo que no tiene nada que ver
        :param query_vector:
        :return:
        """
        return self._vector_store.max_marginal_relevance_search_by_vector(
            embedding = query_vector,
            k = 1,
            fetch_k = 20,
            lambda_multi = 0.1)


    def __init__(self, settings: Settings, embeddings_model : Embeddings):
       self._vector_store = MongoDBAtlasVectorSearch.from_connection_string(
           connection_string=settings.mongo_uri,
           namespace="adyd_rag."+settings.mongo_collection_name,
           index_name=settings.mongo_vector_index,
           embedding=embeddings_model,
           text_key="page_content"
       )

    def search_vector(self, query_vector: list[float], pre_filter: list[str]):
        pass
    # "nivel": 1,
    # }
    #
    #  results = self._vector_store.similarity_search_by_vector(
    #     embedding=query_vector,
    #     k=5        )
    # logger.info(f"Found {len(results)} results")
    # pipeline = [
    #     {
    #         "$vectorSearch": {
    #             "index": "vector_hechizos_index_2",
    #             "path": "embedding",  # ej: "embedding"
    #             "queryVector": query_vector,
    #             "numCandidates": 100,
    #             "limit": 5
    #         }
    #     }
    # ]
    # raw_results = list(self._collection.aggregate(pipeline))
    # print(f"DEBUG: Resultados directos de Mongo: {len(raw_results)}")

    def search_vector_without_pre_filter(self, query_vector: list[float]):
        return self._vector_store.similarity_search_by_vector(
                embedding=query_vector,
                k=5,
                limit=1
            )

