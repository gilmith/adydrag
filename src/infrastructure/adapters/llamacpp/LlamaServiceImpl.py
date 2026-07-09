from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from src.domain.model.MultipleDocument import MultipleDocument
from src.infrastructure.config.Settings import Settings
from src.domain.service.llm.LLMService import LLMService
from langchain_ollama import OllamaEmbeddings

class LlamaServiceImpl(LLMService):

    def __init__(self, settings: Settings):

        self._embeddings_service = OllamaEmbeddings(
            base_url=settings.llama_url,
            model=settings.ollama_model
        )
        self._ollama_chat = ChatOpenAI(
            model="modelos/llama-2-7b-chat-hf",
            temperature=0.3,
            top_p=0.3,
            max_tokens=1000
        )

    def search_terms_in_user_query(self, query: str) -> list[str]:
        pass

    def create_user_embeddings(self, query: str) -> list[float]:
        pass

    def get_embeddings_model(self):
        pass

    def summarize_result(self, result: list[Document], input_query: str):
        pass

    def generate_classification_prompt(self, results: list[MultipleDocument], input_query: str):
        pass