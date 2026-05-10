from pymongo import MongoClient

from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.config.Settings import Settings


class MongoServiceImpl(MongoService):

    def __init__(self, settings: Settings):
        self.client = MongoClient(settings.mongo_uri)
        self.db = self.client[settings.mongo_db_name]

    def search_vector(self, query_vector: list, top_k: int) -> list:
        pass