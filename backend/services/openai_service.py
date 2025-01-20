from openai import AsyncAzureOpenAI
import os
from typing import List
from ..config import settings

class OpenAIService:
    # set in the .env file
    AZURE_OPENAI_ENDPOINT = settings.AOAI_API_BASE
    AZURE_OPENAI_KEY = settings.AOAI_API_KEY
    GPT_4O_MINI = settings.AOAI_GPT4O_MINI_MODEL
    TTS = settings.TTS_MODEL_NAME
    WHISPER = settings.WHISPER_MODEL_NAME
    API_VERSION = settings.AOAI_API_VERSION

    # Initialize AsyncAzureOpenAI client
    async def get_openai_client(self):
        return AsyncAzureOpenAI(
            api_key=self.AZURE_OPENAI_KEY,
            api_version=self.API_VERSION,
            azure_endpoint=self.AZURE_OPENAI_ENDPOINT
        )
    async def get_chat_completion(self, messages: List[dict]) -> str:
        try:
            client = await self.get_openai_client()
            response = await client.chat.completions.create(
                model=self.GPT_4O_MINI,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error in Azure OpenAI API call: {str(e)}")

    async def get_self_service_response(self, messages: List[dict]) -> str:
        # Similar to get_chat_completion but with specific prompts for self-service
        pass