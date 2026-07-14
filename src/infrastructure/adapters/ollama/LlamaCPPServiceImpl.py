from langchain_community.llms.ollama import Ollama
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic.types import SecretStr

from src.domain.model.ClarificationOrMoreInfo import ClarificationOrMoreInfo
from src.domain.model.MultipleDocument import MultipleDocument
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.config.Settings import Settings


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


    def is_clarification_more_info(self, user_query: str, last_ai_response="") -> ClarificationOrMoreInfo:
        system_message = SystemMessagePromptTemplate.from_template("""
                                          tienes como objetivo ver si la query del usuario es una peticion de mas informacion 
                                          o una aclaracion sobre una respuesta anterior.
                                          Solo tienes como objetivo identificar la intencion del usuario 
                                          con la query para determinar si es una aclaracion o una peticion 
                                          de mas informacion. Tu ultima respuesta a evaluar es {last_ai_response}
                                          """)
        human_message = HumanMessagePromptTemplate.from_template("{input_query}")
        prompt = ChatPromptTemplate.from_messages([
            system_message,human_message])
        # Ahora el formateo sí aplicará la sustitución en ambos mensajes
        formatted_messages = prompt.format_messages(
            input_query=user_query,
            last_ai_response=last_ai_response
        )
        logger.debug("--- PROMPT ENVIADO AL LLM ---")
        for message in formatted_messages:
            logger.debug(f"[{message.type.upper()}]: {message.content}")
        logger.debug("-----------------------------")
        # todo aqui es goloso de cambiar a pydanticparser
        try:
            chain = prompt | self._ollama_chat.with_structured_output(schema=ClarificationOrMoreInfo)
            result = chain.invoke({
            "input_query": user_query,
            "last_ai_response": ""
            })
        except Exception as e:
            logger.error(f"Error invoking chain: {e}")
        logger.debug(f"Raw response from chain.invoke: {result}")

        return result