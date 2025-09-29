from semantic_kernel.functions import kernel_function
from connectors.gemini_connector import GeminiChatService
from utils.prompt_utils import FORMAT_REPORT_PROMPT, render_prompt

class ReportPlugin:
    def __init__(self) -> None:
        self._chat = GeminiChatService()

    @kernel_function(name="generate_report", description="Gera relatório consolidado em JSON")
    async def generate_report(self, restaurant_name: str, top_products: list, avg_prep_seconds: int, avg_prep_30d_seconds: int, alerts: list) -> str:
        prompt_text = render_prompt(
            FORMAT_REPORT_PROMPT,
            {
                "restaurant_name": restaurant_name,
                "top_products": top_products,
                "avg_prep": avg_prep_seconds,
                "avg_prep_30d": avg_prep_30d_seconds,
                "alerts": alerts,
            },
        )
        return await self._chat.complete_json(prompt_text)


