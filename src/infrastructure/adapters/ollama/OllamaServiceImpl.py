from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.config.Settings import Settings
from langchain_ollama import OllamaEmbeddings

class OllamaServiceImpl(OllamaService):

    def create_user_embeddings(self, query: str) -> list[float]:
        return self._embeddings_service.embed_query(query)

    def __init__(self, settings: Settings):
        self._embeddings_service = OllamaEmbeddings(
            base_url=settings.ollama_url,
            model=settings.ollama_model,
        )