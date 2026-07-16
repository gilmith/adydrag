from langchain_community.llms.ollama import Ollama
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic.types import SecretStr

from application.service.exception.NodeException import NodeException
from domain.model.state.StateData import LogLevel
from src.domain.model.ClarificationOrMoreInfo import ClarificationOrMoreInfo
from src.domain.model.MultipleDocument import MultipleDocument
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.config.Settings import Settings


class LlamaCPPServiceImpl(OllamaService):

    def __init__(self, settings: Settings):
        from langchain_openai import OpenAIEmbeddings
        self._embeddings_service = OpenAIEmbeddings(
            base_url=settings.llama_cpp_url,
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
        # todo aqui es goloso de cambiar a pydanticparser
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
            Eres un módulo clasificador experto en análisis de intenciones para un sistema conversacional. 
            Tu única tarea es analizar el último mensaje del usuario (`USER_REPLY`) en relación con la última respuesta que le dio la inteligencia artificial (`LAST_AI_RESPONSE`) 
            para evaluar si se cumplen los criterios de clarificación o de ampliación de información.

            Criterios de Evaluación Obligatorios:

            1. Evalúa `is_clarification`:
                - Asígnale `True` únicamente si el usuario indica de forma directa o implícita que NO ha entendido la respuesta anterior de la IA, si muestra confusión, o pide que se le explique de forma más sencilla, clara o con otras palabras.
                - Ejemplos clave: 'No te entiendo', '¿A qué te refieres?', 'Explícamelo más fácil', 'No me queda claro'.

            2. Evalúa `is_more_info`:
                - Asígnale `True` únicamente si el usuario sí entendió la respuesta anterior pero quiere profundizar, pide más detalles, o quiere ampliar la información con más ejemplos o datos adicionales sobre el mismo tema.
                - Ejemplos clave: 'Cuéntame más sobre eso', 'Dame un ejemplo de lo segundo', '¿Puedes ampliar este punto?'.

            Nota: Si el usuario realiza un cambio radical de tema, saluda, agradece o cierra la conversación sin hacer referencia ni continuidad a la respuesta anterior, o si el contexto `LAST_AI_RESPONSE` es vacio ambos campos deben permanecer en `False`.

            Contexto de la conversación anterior:
            <LAST_AI_RESPONSE>
                {last_ai_response}
            </LAST_AI_RESPONSE>
            """)
        human_message = HumanMessagePromptTemplate.from_template("{input_query}")
        prompt = ChatPromptTemplate.from_messages([
            system_message, human_message])
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
            logger.error(f"Error invoking chain")
            raise NodeException(f"Error invoking chain: {e}", log_level=LogLevel.ERROR)
        logger.debug(f"Raw response from chain.invoke: {result}")

        return result
