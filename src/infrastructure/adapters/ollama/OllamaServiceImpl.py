from langchain_classic.chains.summarize import load_summarize_chain
from langchain_community.llms.ollama import Ollama
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.domain.model.MultipleDocument import MultipleDocument
from src.domain.model.HechizoMetadata import HechizoMetadata
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.config.Settings import Settings
from langchain_ollama import OllamaEmbeddings, ChatOllama
from loguru import logger

class OllamaServiceImpl(OllamaService):

    def generate_classification_prompt(self, results: list[MultipleDocument], input_query: str):
        # Ordenar por rank y formatear las opciones
        sorted_results = sorted(results, key=lambda x: x.rank)

        options_text = "\n".join([
            f"{i + 1}. **{doc.name}** (rank: {doc.rank})\n "
            for i, doc in enumerate(sorted_results)
        ])

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             """Responde en español. Eres un dungeon master experimentado. 
             El jugador ha realizado una búsqueda que ha devuelto varias coincidencias.
             Preséntale las opciones de forma clara y amigable, numeradas, 
             y pídele que especifique cuál le interesa."""),
            ("human",
             """El jugador preguntó: {input_query}

             Se han encontrado las siguientes coincidencias ordenadas por relevancia:

             {options_text}

             Presenta estas opciones al jugador solo con el nombre que esta en el objeto options_test.name. """)
        ])

        chain = prompt | self._ollama_chat | StrOutputParser()

        result = chain.invoke({
            "input_query": input_query,
            "options_text": options_text
        })

        logger.info(result)
        return result

    #TODO cambiar para que añada los metadatos que ahora solo esta dando el resumen 
    def summarize_result(self, result: list[Document], input_query: str):
        context = "\n\n".join([doc.page_content for doc in result])

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Responde en español. Eres un dungeon master experimentado y tienes que responder las preguntas de un jugador respecto a los hechizos de mago y de sacerdote. Cíñete exclusivamente al contexto."),
            ("human", "Usando el siguiente contexto:\n\n{context}\n\nResponde a esta pregunta: {input_query}")
        ])

        chain = prompt | self._ollama_chat | StrOutputParser()

        result = chain.invoke({
            "context": context,
            "input_query": input_query
        })

        logger.info(result)
        return result


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
                temperature=0.3,
                top_p=0.3,
                top_k=50,
        )
        self._llm = Ollama(model=settings.ollama_model_chat, temperature=0.3)

    def create_user_embeddings(self, query: str) -> list[float]:
        return self._embeddings_service.embed_query(query)

