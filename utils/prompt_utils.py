FORMAT_REPORT_PROMPT = """
Você é um analista de restaurantes. Gere um relatório curto e acionável para o restaurante {{restaurant_name}}.

Dados atuais:
- Top produtos: {{top_products}}
- Tempo médio de preparo hoje: {{avg_prep}} seg
- Média histórica (30d): {{avg_prep_30d}} seg
- Alertas: {{alerts}}

Responda em JSON no formato:
{
  "title": "...",
  "summary": "...",
  "top_products": [...],
  "avg_prep": ..., 
  "avg_prep_30d": ..., 
  "alerts": [...],
  "recommendations": [...]
}
"""


def render_prompt(template: str, values: dict) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    return rendered


