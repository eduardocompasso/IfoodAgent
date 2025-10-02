import json
from semantic_kernel.functions import kernel_function
from connectors.gemini_connector import GeminiChatService
from utils.prompt_utils import FORMAT_ANOMALIE_PROMPT, render_prompt

class AnomaliePlugin:
    def __init__(self) -> None:
        self._chat = GeminiChatService()

    @kernel_function(name="detect_anomalies_with_ai", description="Detecta anomalias nas métricas")
    async def detect_anomalies_with_ai(self, metrics: dict) -> str:

        metrics_json_str = json.dumps(metrics, indent=2, ensure_ascii=False)
        
        prompt_text = render_prompt(
            FORMAT_ANOMALIE_PROMPT,
            {
                "metrics_data": metrics_json_str,
            },
        )
        
        return await self._chat.complete(prompt_text)