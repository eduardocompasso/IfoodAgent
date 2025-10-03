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
  "avg_prep_today": ..., 
  "avg_prep_30d": ..., 
  "alerts": [...],
  "recommendations": [...]
}
"""

FORMAT_ANOMALIE_PROMPT = """
Você é um analista de dados sênior especializado em operações de restaurantes.
Sua tarefa é encontrar anomalias, padrões interessantes ou pontos de risco nos dados de métricas a seguir.

Seja direto e aponte os achados em formato de lista (bullet points).
Se nada parecer fora do comum, apenas responda "Nenhuma anomalia significativa foi detectada.".

Aqui estão os dados das métricas em formato JSON:
{{metrics_data}}
"""

FORMAT_ROUTER_PROMPT = """
Você é um assistente de IA especializado em rotear a entrada de um usuário para a função correta.
Analise a entrada e determine qual função de qual plugin deve ser chamada.

As funções disponíveis são:
- Plugin 'MetricsPlugin', função 'query_metrics': Para obter métricas gerais (vendas, tempo de preparo, produtos mais vendidos).
- Plugin 'MetricsPlugin', função 'query_clients_metrics': Para obter dados sobre os clientes (quem mais comprou, total gasto).
- Plugin 'AnomaliePlugin', função 'detect_anomalies_with_ai': Para encontrar anomalias e padrões incomuns nos dados.
- Plugin 'ReportPlugin', função 'generate_report': Para criar um relatório completo e estruturado.

--- EXEMPLOS ---
Entrada do usuário: "me mostre o resumo de performance"
Resposta:
{
  "plugin": "ReportPlugin",
  "function": "generate_report"
}

Entrada do usuário: "quais os principais dados?"
Resposta:
{
  "plugin": "MetricsPlugin",
  "function": "query_metrics"
}

Entrada do usuário: "quem são meus melhores clientes?"
Resposta:
{
  "plugin": "MetricsPlugin",
  "function": "query_clients_metrics"
}

Entrada do usuário: "veja se tem algo de errado nos números"
Resposta:
{
  "plugin": "AnomaliePlugin",
  "function": "detect_anomalies_with_ai"
}

Entrada do usuário: "olá, tudo bem?"
Resposta:
{
  "plugin": null,
  "function": null
}
--- FIM DOS EXEMPLOS ---

Agora, analise a seguinte entrada do usuário e forneça sua resposta SOMENTE em formato JSON.

Entrada do usuário: "{{user_input}}"
Resposta:
"""

def render_prompt(template: str, values: dict) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    return rendered


