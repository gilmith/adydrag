import pickle
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from pymongo import MongoClient


class MongoCustomRawSaver(BaseCheckpointSaver):
    def __init__(self, client: MongoClient, db_name: str = "jellyfish", collection_name: str = "checkpoints_raw"):
        super().__init__()
        self.client = client
        self.collection = client[db_name][collection_name]
        self.collection.create_index([("thread_id", 1), ("checkpoint_id", -1)])

    def put(self, config: RunnableConfig, checkpoint: Checkpoint, metadata: CheckpointMetadata,
            new_versions: dict[str, bytes]) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]

        # 1. Extraemos las variables de tu State (channel_values)
        valores_estado = checkpoint.get("channel_values", {})

        # 2. Creamos un diccionario con datos en RAW (Texto plano para MongoDB)
        state_raw = {}
        for clave, valor in valores_estado.items():
            # Si el dato es simple (str, int, dict, list), lo guardamos tal cual en RAW
            if isinstance(valor, (str, int, float, bool, list, dict)):
                state_raw[clave] = valor
            else:
                # Si es un objeto complejo (ej. Document de LangChain), guardamos una traza legible
                state_raw[clave] = f"[Objeto Complejo: {type(valor).__name__}] -> {str(valor)}"

        # 3. Construimos el documento para MongoDB
        documento = {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint["id"],
            "parent_checkpoint_id": config["configurable"].get("checkpoint_id"),
            "created_at": datetime.now(timezone.utc).isoformat(),

            # 🔥 AQUÍ ESTÁ TU LOG EN RAW PARA CONSULTAR EN MONGODB:
            "datos_visibles": state_raw,

            # 📦 Y AQUÍ EL BINARIO COMPLETO QUE ENTIENDE LANGGRAPH (Caja negra)
            "checkpoint_completo_binario": self.serde.dumps(checkpoint),
            "metadata_binaria": self.serde.dumps(metadata)
        }

        self.collection.update_one(
            {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]},
            {"$set": documento},
            upsert=True
        )
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]}}

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"].get("checkpoint_id")

        query = {"thread_id": thread_id}
        if checkpoint_id:
            query["checkpoint_id"] = checkpoint_id

        doc = self.collection.find_one(query, sort=[("checkpoint_id", -1)])
        if not doc:
            return None

        # 🔥 LA MAGIA: Reconstruimos el objeto original desde el binario guardado.
        # LangGraph recupera su estado 100% intacto, ignorando que añadiste campos en RAW.
        checkpoint = self.serde.loads(doc["checkpoint_completo_binario"])
        metadata = self.serde.loads(doc["metadata_binaria"])

        return CheckpointTuple(
            config={"configurable": {"thread_id": thread_id, "checkpoint_id": doc["checkpoint_id"]}},
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config={
                "configurable": {"thread_id": thread_id, "checkpoint_id": doc["parent_checkpoint_id"]}} if doc.get(
                "parent_checkpoint_id") else None
        )

    # Nota: Tendrías que implementar también el método obligatorio `list` siguiendo la misma lógica de lectura binaria.