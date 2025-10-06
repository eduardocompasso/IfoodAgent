import json
from connectors.gemini_connector import GeminiChatService
from utils.prompt_utils import FORMAT_ROUTER_PROMPT, render_prompt

class AIIntentRouter:
    def __init__(self, chat_service: GeminiChatService):
        self._chat = chat_service

    async def route_intent_async(self, user_input: str) -> dict:
        """ 
        Usa a IA para determinar qual plugin/função chamar com base na entrada do usuário.
        """
        
        prompt = render_prompt(FORMAT_ROUTER_PROMPT, {"user_input":user_input})

        raw_response = await self._chat.complete(prompt)

        try:
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_string = raw_response[json_start:json_end]
                intent_data = json.loads(json_string)
                # Valida se os campos esperados existem
                if "plugin" in intent_data and "function" in intent_data:
                    return intent_data
        except (json.JSONDecodeError, IndexError):
            # Se falhar, retorna uma intenção nula para o tratamento de fallback
            pass

        return {"plugin": None, "function": None}