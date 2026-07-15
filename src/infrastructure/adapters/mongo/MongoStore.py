from langgraph.store.base import TTLConfig
from langgraph.store.mongodb import MongoDBStore
from pymongo import MongoClient

from src.infrastructure.config.Settings import Settings


class MongoStore:

    def __init__(self, settings: Settings):
        self._client = MongoClient(settings.mongo_uri)
        db = self._client[settings.mongo_db_name]
        collection = db[settings.mongo_chat_history_collection]
        self._mongo_db_store = MongoDBStore(
            collection=collection,
            ttl_config=TTLConfig(
                refresh_on_read=False,
                default_ttl=120
            )
        )

    def get_store(self) -> MongoDBStore:
        return self._mongo_db_store

    def get_store(self):
        return self._mongo_db_store
