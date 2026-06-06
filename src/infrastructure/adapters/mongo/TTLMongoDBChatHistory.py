import json
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, BaseMessage, message_to_dict
from langchain_mongodb import MongoDBChatMessageHistory


class TTLMongoDBChatHistory(MongoDBChatMessageHistory):

    def add_message(self, message: BaseMessage) -> None:
        self.collection.insert_one(
            {
                self.session_id_key: self.session_id,
                self.history_key: json.dumps(message_to_dict(message)),
                "created_at": datetime.now(timezone.utc),
            }
        )
