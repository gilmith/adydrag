from typing import cast, Collection, Any

from langchain_core.embeddings import Embeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.config.Settings import Settings
from loguru import logger

class MongoServiceImpl(MongoService):

    def search_vector(self, query_vector: list[float], pre_filter: list[str]):
        pre_filter = {
            "nivel": 1,
        }

        results = self._vector_store.similarity_search_by_vector(
            embedding=query_vector,
            k=5        )
        logger.info(f"Found {len(results)} results")
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_hechizos_index_2",
                    "path": "embedding",  # ej: "embedding"
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": 5
                }
            }
        ]
        raw_results = list(self._collection.aggregate(pipeline))
        print(f"DEBUG: Resultados directos de Mongo: {len(raw_results)}")


    def __init__(self, settings: Settings, embeddings_model : Embeddings):
        client = MongoClient(settings.mongo_uri)
        db = client[settings.mongo_db_name]
        self._col = cast(Collection[dict[str, Any]], db[settings.mongo_collection_name])
        self._vector_store =  MongoDBAtlasVectorSearch(
            collection=self._col,
            embedding=embeddings_model,  # El que usas para calcular "a parte"
            index_name=settings.mongo_vector_index,  # Nombre del índice en Atlas
            relevance_score_fn="cosine"
        )

        # 2. Acceder a la DB
        self._db = client[settings.mongo_db_name]
        # 3. Acceder a la COLECCIÓN (Este es el objeto que tiene .aggregate)
        self._collection = self._db[settings.mongo_collection_name]

