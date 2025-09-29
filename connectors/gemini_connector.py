import asyncio
from typing import Any, Dict

from config import gemini_model

class GeminiChatService:
    def __init__(self) -> None:
        self._model = gemini_model

    async def complete(self, prompt: str) -> str:
        response = await asyncio.to_thread(self._model.generate_content, prompt)
        return response.text if hasattr(response, "text") else str(response)

    async def complete_json(self, prompt: str) -> str:
        return await self.complete(prompt)


