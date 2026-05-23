import os
from dotenv import load_dotenv

# Cargamos al inicio de este módulo para asegurar disponibilidad
load_dotenv()

class Settings:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.azure_app_id = os.getenv("AZURE_APP_ID")
        self.azure_password = os.getenv("AZURE_PASSWORD")
        self.mongo_db_name = os.getenv("MONGO_DB_NAME")
        self.mongo_collection_name = os.getenv("MONGO_COLLECTION_NAME")
        self.ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
        self.ollama_model = os.getenv("OLLAMA_MODEL")
        self.chatbot_id = os.getenv("CHATBOT_ID")
        self.chatbot_password = os.getenv("CHATBOT_PASSWORD")
        self.chatbot_tenant_id = os.getenv("CHATBOT_TENANT_ID")
        self.ollama_model_chat = os.getenv("OLLAMA_MODEL_CHAT")
        self.mongo_vector_index = os.getenv("MONGO_VECTOR_INDEX")