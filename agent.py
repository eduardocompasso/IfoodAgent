import asyncio
from config import gemini_model
from services.metrics_service import query_metrics
from services.anomaly_service import detect_anomalies
from services.notify_service import notify
from utils.prompt_utils import FORMAT_REPORT_PROMPT, render_prompt


async def run_agent():
    context = {}

    context = await query_metrics(context)
    context = await detect_anomalies(context)

    metrics = context["metrics"]
    prompt_text = render_prompt(
        FORMAT_REPORT_PROMPT,
        {
            "restaurant_name": metrics["restaurant_name"],
            "top_products": metrics["top_products"],
            "avg_prep": metrics["avg_prep_seconds"],
            "avg_prep_30d": metrics["avg_prep_30d_seconds"],
            "alerts": context["alerts"],
        },
    )
    response = await asyncio.to_thread(gemini_model.generate_content, prompt_text)
    context["report"] = response.text

    await notify(context)


async def chat_loop():
    print("\nDigite mensagens para o agente. Comandos disponíveis: /metrics, /anomalies, /report, /exit")
    context = {}
    while True:
        try:
            user_input = await asyncio.to_thread(input, "\nVocê: ")
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break

        if not user_input:
            continue
        if user_input.strip().lower() in {"/exit", ":q", "sair"}:
            print("Tchau!")
            break

        if user_input.strip().lower() == "/metrics":
            context = await query_metrics(context)
            print("Agente: métricas atualizadas.")
            continue

        if user_input.strip().lower() == "/anomalies":
            if "metrics" not in context:
                context = await query_metrics(context)
            context = await detect_anomalies(context)
            print(f"Agente: alertas -> {context.get('alerts', [])}")
            continue

        if user_input.strip().lower() == "/report":
            if "metrics" not in context:
                context = await query_metrics(context)
            if "alerts" not in context:
                context = await detect_anomalies(context)

            metrics = context["metrics"]
            prompt_text = render_prompt(
                FORMAT_REPORT_PROMPT,
                {
                    "restaurant_name": metrics["restaurant_name"],
                    "top_products": metrics["top_products"],
                    "avg_prep": metrics["avg_prep_seconds"],
                    "avg_prep_30d": metrics["avg_prep_30d_seconds"],
                    "alerts": context["alerts"],
                },
            )
            response = await asyncio.to_thread(gemini_model.generate_content, prompt_text)
            text = response.text if hasattr(response, "text") else str(response)
            print("\n=== Relatório ===\n" + text)
            continue

        response = await asyncio.to_thread(gemini_model.generate_content, user_input)
        text = response.text if hasattr(response, "text") else str(response)
        print(f"Agente: {text}")


