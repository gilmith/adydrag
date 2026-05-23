from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
import asyncio
from injector import inject

from src.infrastructure.config.Settings import Settings
from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.domain.service.ResponseFromRagService import ResponseFromRagService
from flask import request as flask_request


class TeamsAdapter:
    @inject
    def __init__(self, settings: Settings, ollama_service: OllamaService, mongo_service: MongoService, response_service: ResponseFromRagService):
        self._settings = settings
        self._ollama_service = ollama_service
        self._mongo_service = mongo_service
        self._response_service = response_service
        adapter_settings = BotFrameworkAdapterSettings('', '')
        self.adapter = BotFrameworkAdapter(adapter_settings)

    def process_message(self):
        body = flask_request.get_json(force=True, silent=True)

        if not body:
            return {"status": "error", "message": "Request body is empty or not valid JSON"}, 400

        activity = Activity.deserialize(body)
        if not activity:
            return {"status": "error", "message": "Could not deserialize Activity"}, 400

        auth_header = flask_request.headers.get("Authorization", "")

        async def logic(turn_context: TurnContext):
            if turn_context.activity.type == "message":
                user_text = turn_context.activity.text
                print(f"El usuario dice: {user_text}")
                response = self._response_service.execute_rag_service(user_text)
                await turn_context.send_activity(response)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.adapter.process_activity(activity, auth_header, logic))
            loop.close()

            return {"status": "sent"}, 201
        except Exception as e:
            print(f"Error al responder: {e}")
            return {"status": "error", "message": str(e)}, 500
