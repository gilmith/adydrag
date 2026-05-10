from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
import asyncio
from flask import request

from src.infrastructure.config.Settings import Settings
from src.infrastructure.adapters.mongo.MongoServiceImpl import MongoServiceImpl
from src.infrastructure.adapters.ollama.OllamaServiceImpl import OllamaServiceImpl
from src.application.service.ResponseFromRagServiceImpl import ResponseFromRagServiceImpl

# Inicialización única al arrancar (equivalente a singleton)
_settings = Settings()
_mongo = MongoServiceImpl(_settings)
_ollama = OllamaServiceImpl(_settings) if _settings.ollama_url else None
_rag_service = ResponseFromRagServiceImpl(_ollama, _mongo, _settings)

# Configuración del adaptador de Teams
settings = BotFrameworkAdapterSettings(_settings.chatbot_id, _settings.chatbot_password, _settings.chatbot_tenant_id)
adapter = BotFrameworkAdapter(settings)

def process_message(body):
    """
    Recibe el body desde Connexion y delega la lógica RAG al servicio.
    """
    response = _rag_service.execute_rag_service(body['message'])

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def logic(turn_context: TurnContext):
        if turn_context.activity.type == "message":
            user_text = turn_context.activity.text
            print(f"El usuario dice: {user_text}")
            await turn_context.send_activity(response)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(adapter.process_activity(activity, auth_header, logic))
        loop.close()

        return {"status": "sent"}, 201
    except Exception as e:
        print(f"Error al responder: {e}")
        return {"status": "error", "message": str(e)}, 500