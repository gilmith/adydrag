from langchain_classic.chains.query_constructor.schema import AttributeInfo
from langchain_classic.retrievers import SelfQueryRetriever
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.infrastructure.config.Settings import Settings
from langchain_ollama import OllamaEmbeddings, ChatOllama


class OllamaServiceImpl(OllamaService):



    def search_terms_in_user_query(self, query: str, vector_store: VectorStore) -> list[Document]:
        metadata_field_info = [
            AttributeInfo(name="nivel", description="El nivel del conjuro (1-9)", type="integer"),
            AttributeInfo(name="clases", description="La clase que usa el conjuro", type="string"),
            AttributeInfo(name="nombre", description="El nombre del conjunto", type="string"),
            AttributeInfo(name="componentes", description="El componente del conjuro (verbal, somático, material)", type="string"),
            AttributeInfo(name="duracion", description="El duracion del conjunto", type="string"),
            AttributeInfo(name="tiempo_lanzamiento", description="El tiempo de lanzamiento del conjuro", type="integer")
        ]

        retriever = SelfQueryRetriever.from_llm(
            self._ollama_chat,
            vector_store,
            "Descripción de conjuros de rol",
            metadata_field_info,
        )

        return retriever.invoke(query)

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_ollama import ChatOllama

    def analizar_consulta(query):
        llm = ChatOllama(model="llama3.1:8b", format="json", temperature=0)

        prompt = ChatPromptTemplate.from_template("""
        Analiza la consulta de un jugador de rol y extrae:
        1. Filtros (nivel, clases, escuela)
        2. Términos de búsqueda (nombres propios o acciones)

        Consulta: "{query}"

        Respuesta en JSON:
        {{
            "filtros": {{ ... }},
            "terminos_busqueda": "..."
        }}
        """)

        chain = prompt | llm | JsonOutputParser()
        return chain.invoke({"query": query})

    def busqueda_hibrida_con_filtros(query_original, vector_store):
        # 1. Extraemos la "intención"
        analisis = analizar_consulta(query_original)
        filtros = analisis["filtros"]
        terminos = analisis["terminos_busqueda"]

        # 2. Ejecutamos la búsqueda híbrida con el pre_filter dinámico
        # Esto usa Embeddings + Texto + Filtros de Metadatos
        resultados = vector_store.similarity_search(
            query=terminos,  # Aquí va el texto clave (ej: "Proyectil Mágico")
            k=3,
            search_type="hybrid",
            pre_filter=filtros  # Aquí va el nivel, clase, etc.
        )

        return resultados

    def __init__(self, settings: Settings):
        self._embeddings_service = OllamaEmbeddings(
            base_url=settings.ollama_url,
            model=settings.ollama_model,
        )
        self._ollama_chat =  ChatOllama(
                model="deepseek-r1:1.5b",
                temperature=0
        )

    def create_user_embeddings(self, query: str) -> list[float]:
        return self._embeddings_service.embed_query(query)

