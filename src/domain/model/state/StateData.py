import operator
from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

from langchain_core.documents import Document
from pydantic import BaseModel, Field


class Metadata(BaseModel):
    name: str
    player_class: str
    level: int
    spell_family: str
    range: str
    components: list[str]
    duration: str
    time_to_cast: str
    area: str
    salvation_throw: str
    model_config = {"from_attributes": True, "extra": "ignore"}


class StateData(BaseModel):
    page_content: str
    embedding: Optional[list[float]]
    metadata: Metadata
    id: str
    documents: list[Document] = Field(default_factory=list)

class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class LogMeta(BaseModel):
    info: str | None = None
    node_name: str
    level: LogLevel | None = None
    start_time: datetime
    end_time: datetime | None = None


class State(BaseModel):
    user_query: str
    conversation_id: str
    user_embedding: Optional[list[float]] = None
    states: Optional[list[StateData]] = None
    logs: Annotated[list[LogMeta], operator.add] = Field(default_factory=list)
    conversation_history: list[str] = Field(default_factory=list)
    llm_response: str | None = None


    def __hash__(self):
        return hash((self.user_query, tuple(self.user_embedding or ()), tuple(self.states or ()), tuple(self.logs or ())))

    def __eq__(self, other):
        if isinstance(other, State):
            return (self.user_query == other.user_query and
                    self.user_embedding == other.user_embedding and
                    self.states == other.states and
                    self.logs == other.logs)
        return False