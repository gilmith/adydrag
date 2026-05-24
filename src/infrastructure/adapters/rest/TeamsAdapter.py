from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from botbuilder.core import ShowTypingMiddleware

import asyncio
from injector import inject
from loguru import logger

from src.infrastructure.config.Settings import Settings
from src.infrastructure.adapters.mongo.MongoService import MongoService
from src.infrastructure.adapters.ollama.OllamaService import OllamaService
from src.domain.service.ResponseFromRagService import ResponseFromRagService
from flask import request as flask_request


class TeamsAdapter:
    @inject
    def __init__(self, settings: Settings, ollama_service: OllamaService, mongo_service: MongoService,
                 response_service: ResponseFromRagService):
        self._settings = settings
        self._ollama_service = ollama_service
        self._mongo_service = mongo_service
        self._response_service = response_service

        # TODO: Recuerda poner aquí tus credenciales reales si vas a Teams en producción
        adapter_settings = BotFrameworkAdapterSettings('', '')
        self._adapter = BotFrameworkAdapter(adapter_settings)

        self._adapter.use(ShowTypingMiddleware(delay=0.5, period=2.0))

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

                #  SOLUCIÓN AL BLOQUEO DE OLLAMA/RAG:
                # Corremos la función síncrona en un hilo separado para que asyncio pueda
                # enviar el evento "typing" en paralelo mientras Ollama procesa.
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    self._response_service.execute_rag_service,
                    user_text
                )
                logger.info(response.get('output_text', ''))
                respuesta_final = (
                    f"{response.get('output_text')}\n\n"
                    f"**Metadatos del fragmento:**\n"
                    f"Alcance {response.get('metadata')}"
                )
                await turn_context.send_activity(respuesta_final)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._adapter.process_activity(activity, auth_header, logic))
            loop.close()

            return {"status": "sent"}, 201
        except Exception as e:
            print(f"Error al responder: {e}")
            return {"status": "error", "message": str(e)}, 500