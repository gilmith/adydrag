from pydantic import BaseModel, Field


class MultipleDocument(BaseModel):
    level: int = Field(description="spell level")
    rank: int = Field(description="rank")
    name: str = Field(description="name")
    full_text_score: float = Field(description="full text score")
    vector_score: float = Field(description="vector score")
