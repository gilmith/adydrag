from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.domain.model.HechizoMetadata import HechizoMetadata
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.config.Settings import Settings
from langchain_ollama import OllamaEmbeddings, ChatOllama
from loguru import logger

class OllamaServiceImpl(OllamaService):


    """reconocimiento de entidad nombradas"""

    def get_embeddings_model(self):
        return self._embeddings_service

    def search_terms_in_user_query(self, query: str) -> list[str]:
        parser = JsonOutputParser(pydantic_object=HechizoMetadata)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extrae la información del hechizo. \n{format_instructions}"),
            ("human", "{query}")
        ])

        chain = prompt | self._ollama_chat | parser

        respuesta = chain.invoke({
            "query": query,
            "format_instructions": parser.get_format_instructions()
        })
        logger.info(respuesta)
        return respuesta

    def __init__(self, settings: Settings):
        self._embeddings_service = OllamaEmbeddings(
            base_url=settings.ollama_url,
            model=settings.ollama_model,
        )
        self._ollama_chat = ChatOllama(
                model=settings.ollama_model_chat,
                temperature=0
        )

    def create_user_embeddings(self, query: str) -> list[float]:
        return self._embeddings_service.embed_query(query)

