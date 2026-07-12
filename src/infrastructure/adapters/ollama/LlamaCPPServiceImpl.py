from langchain_community.llms.ollama import Ollama
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from pydantic.types import SecretType, SecretStr

from src.infrastructure.config.Settings import Settings
from src.domain.model.MultipleDocument import MultipleDocument
from src.infrastructure.adapters.ollama.OllamaService import OllamaService


class LlamaCPPServiceImpl(OllamaService):

    def __init__(self, settings: Settings):
        from langchain_openai import OpenAIEmbeddings
        self._embeddings_service = OpenAIEmbeddings(
            base_url=settings.llama_cpp_url ,
            model=settings.ollama_model,
            api_key=SecretStr("none")
        )
        self._ollama_chat = ChatOpenAI(
            model=settings.ollama_model_chat,
            temperature=0.3,
            top_p=0.3,
            api_key=SecretStr("none")
        )
        self._llm = Ollama(model=settings.ollama_model_chat, temperature=0.3)

    def search_terms_in_user_query(self, query: str) -> list[str]:
        pass

    def summarize_result(self, result: list[Document], input_query: str):
        pass

    def get_embeddings_model(self):
        return self._embeddings_service

    def generate_classification_prompt(self, results: list[MultipleDocument], input_query: str):
        pass

    def create_user_embeddings(self, query: str) -> list[float]:
        pass