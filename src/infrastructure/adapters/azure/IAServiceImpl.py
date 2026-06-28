import json
from typing import List

from langchain_core.documents import Document
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.domain.model.MultipleDocument import MultipleDocument
from src.application.service.IAService import IAService
from src.domain.model.HechizoMetadata import HechizoMetadata
from src.infrastructure.config.Settings import Settings


class IAServiceImpl(IAService):



    def __init__(self, settings: Settings):
        self._azure_client = AzureOpenAI(
            api_key=settings.chat_gpt_api_key,
            api_version=settings.chat_gpt_api_version,
            azure_endpoint=settings.chat_gpt_endpoint,
        )
        self._model = settings.chat_gpt_model
        self._chat_gpt_temperature = settings.chat_gpt_temperature
        self._chat_gpt_top_p = settings.chat_gpt_top_p
        self._system_prompt = settings.system_prompt



    def summarize_result(self, conversation_id: str, documents: list, user_query: str) -> str | None:

        payload_messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._build_system_prompt(documents)},
            {"role": "user", "content": user_query}
        ]

        chat_completions_response = self._azure_client.chat.completions.create(
            model=self._model,
            messages=payload_messages,
            temperature=self._chat_gpt_temperature,
            top_p=self._chat_gpt_top_p,
            max_tokens=100
        )
        if len(chat_completions_response.choices) == 0:
            return "No he encontrado nada para reponder"
        return chat_completions_response.choices[0].message.content

    def _build_system_prompt(self, documents: list[Document]) -> str:
        context = []
        for doc in documents:
            metadata = HechizoMetadata(**doc.metadata)

            full_spell = {
                "informacion_general": metadata.model_dump(),  # Convierte el Pydantic a dict {}
                "descripcion": doc.page_content
            }
            context.append(full_spell)

        json_context = json.dumps(context, ensure_ascii=False, indent=2)

        system_prompt = (
            f"{self._system_prompt} \n {json_context}"
        )

    def generate_classification_prompt(self, conversation_id: str, documents: list[MultipleDocument], user_query: str) -> str:
        sorted_results = sorted(documents, key=lambda x: x.rank)

        options_text = "\n".join([
            f"{i + 1}. **{doc.name}** (rank: {doc.rank})\n "
            for i, doc in enumerate(sorted_results)
        ])

        self.summarize_result(conversation_id, sorted_results, user_query)