from langchain_community.llms.ollama import Ollama
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from loguru import logger
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
            base_url=settings.llama_cpp_url,
            model=settings.ollama_model_chat,
            temperature=0.3,
            top_p=0.3,
            api_key=SecretStr("none")
        )
        self._llm = Ollama(model=settings.ollama_model_chat, temperature=0.3)

    def search_terms_in_user_query(self, query: str) -> list[str]:
        pass

    def summarize_result(self, conversation_id: str, result: list[Document], input_query: str):
        context = "\n\n".join([doc.page_content for doc in result])

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Responde en español. Eres un dungeon master experimentado y tienes que responder las preguntas de un jugador respecto a los hechizos de mago y de sacerdote. Cíñete exclusivamente al contexto."),
            ("human", "Usando el siguiente contexto:\n\n{context}\n\nResponde a esta pregunta: {input_query}")
        ])
        #todo aqui es goloso de cambiar a pydanticparser
        chain = prompt | self._ollama_chat | StrOutputParser()

        result = chain.invoke({
            "context": context,
            "input_query": input_query
        })

        logger.info(result)
        return result

    def get_embeddings_model(self):
        return self._embeddings_service

    def generate_classification_prompt(self, results: list[MultipleDocument], input_query: str):
        pass

    def create_user_embeddings(self, query: str) -> list[float]:
        pass