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
        self.mongo_full_index = os.getenv("MONGO_FULL_TEXT_INDEX")
        self.chat_history_collection = os.getenv("CHAT_HISTORY_COLECTION")
        self.chat_gpt_api_key = os.getenv("CHAT_GPT_4_API_KEY")
        self.chat_gpt_api_version = os.getenv("CHAT_GPT_4_API_VERSION")
        self.chat_gpt_endpoint = os.getenv("CHAT_GPT_4_ENDPOINT")
        self.chat_gpt_model = os.getenv("CHAT_GPT_MODEL")
        self.system_prompt = os.getenv("CHAT_GPT_4_SYSTEM_PROMPT")
        self.chat_gpt_temperature = os.getenv("CHAT_GPT_4_GPT_TEMPERATURE")
        self.chat_gpt_top_p = os.getenv("CHAT_GPT_4_GPT_TOP_P")
