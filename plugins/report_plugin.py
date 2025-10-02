import json
from semantic_kernel.functions import kernel_function
from connectors.gemini_connector import GeminiChatService
from utils.prompt_utils import FORMAT_REPORT_PROMPT, render_prompt

class ReportPlugin:
    def __init__(self) -> None:
        self._chat = GeminiChatService()

    @kernel_function(name="generate_report", description="Gera relatório consolidado em JSON")
    async def generate_report(self, restaurant_name: str, top_products: list, avg_prep_seconds: int, avg_prep_today_seconds: int, avg_prep_30d_seconds: int, alerts: list) -> str:
        prompt_text = render_prompt(
            FORMAT_REPORT_PROMPT,
            {
                "restaurant_name": restaurant_name,
                "top_products": top_products,
                "avg_prep": avg_prep_seconds,
                "avg_prep_today": avg_prep_today_seconds,
                "avg_prep_30d": avg_prep_30d_seconds,
                "alerts": alerts,
            },
        )
        raw_response = await self._chat.complete(prompt_text)
        
        try:
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_string = raw_response[json_start:json_end]
                json.loads(json_string) 
                return json_string
            else:
                return '{"error": "A IA não retornou um JSON."}'
        except Exception:
            return f'{{"error": "Falha ao processar a resposta da IA.", "raw_response": "{raw_response}"}}'



