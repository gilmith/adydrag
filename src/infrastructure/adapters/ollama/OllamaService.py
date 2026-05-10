from abc import ABC, abstractmethod


class OllamaService(ABC):

    @abstractmethod
    def create_user_embeddings(self, query: str) -> list[float]:
        pass

    """
    # Ejemplo: Supongamos que 'docs' es tu lista de documentos de LangChain (del PDF)
# docs = text_splitter.split_documents(pdf_pages)

# Para probar con una lista de textos simple:
textos_ejemplo = [
    "El bardo falló su tirada de carisma y ahora el dragón está molesto.",
    "Las reglas de D&D 5e especifican que el daño de fuego es letal."
]

# Generar embeddings para una lista de textos
vectores = embeddings_service.embed_documents(textos_ejemplo)

print(f"Número de vectores generados: {len(vectores)}")
print(f"Dimensión de cada vector: {len(vectores[0])}")
    """