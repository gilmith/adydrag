from langchain_classic.chains.summarize import load_summarize_chain
from langchain_community.llms.ollama import Ollama
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.domain.model.HechizoMetadata import HechizoMetadata
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.config.Settings import Settings
from langchain_ollama import OllamaEmbeddings, ChatOllama
from loguru import logger

class OllamaServiceImpl(OllamaService):


    """reconocimiento de entidad nombradas"""

    def summarize_result(self, result: list[Document], input_query: str):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un dungeon master experimentado y tienes que responder las preguntas de un jugador respecto a los hechizos de mago y de sacerdote. Responde siempre en español."),
            ("human", "Usando el siguiente contexto:\n\n{text}\n\nResponde a esta pregunta: {input_query}")
        ])

        chain = load_summarize_chain(
            llm=self._ollama_chat,
            chain_type="stuff",
            prompt=prompt,
            document_variable_name="text"
        )

        summarize_result = chain.invoke({"input_documents": result, "input_query": input_query})
        logger.info(summarize_result)
        return summarize_result.get('output_text', '')


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
                temperature=0.3
        )
        self._llm = Ollama(model=settings.ollama_model_chat, temperature=0.3)

    def create_user_embeddings(self, query: str) -> list[float]:
        return self._embeddings_service.embed_query(query)

