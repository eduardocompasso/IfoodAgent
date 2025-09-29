import asyncio
from plugins.metrics_plugin import MetricsPlugin
from plugins.report_plugin import ReportPlugin

async def run_agent():
    context = {}

    metrics_plugin = MetricsPlugin()
    report_plugin = ReportPlugin()

    metrics = metrics_plugin.query_metrics()
    alerts = metrics_plugin.detect_anomalies(metrics)

    report_text = await report_plugin.generate_report(
        restaurant_name=metrics["restaurant_name"],
        top_products=metrics["top_products"],
        avg_prep_seconds=metrics["avg_prep_seconds"],
        avg_prep_30d_seconds=metrics["avg_prep_30d_seconds"],
        alerts=alerts,
    )
    context["metrics"] = metrics
    context["alerts"] = alerts
    context["report"] = report_text


async def chat_loop():
    print("\nDigite mensagens para o agente. Comandos disponíveis: /metrics, /anomalies, /report, /exit")
    context = {}
    metrics_plugin = MetricsPlugin()
    report_plugin = ReportPlugin()
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
            metrics = metrics_plugin.query_metrics()
            context["metrics"] = metrics
            print("Agente: métricas atualizadas.")
            continue

        if user_input.strip().lower() == "/anomalies":
            if "metrics" not in context:
                context["metrics"] = metrics_plugin.query_metrics()
            alerts = metrics_plugin.detect_anomalies(context["metrics"])
            context["alerts"] = alerts
            print(f"Agente: alertas -> {context.get('alerts', [])}")
            continue

        if user_input.strip().lower() == "/report":
            if "metrics" not in context:
                context["metrics"] = metrics_plugin.query_metrics()
            if "alerts" not in context:
                context["alerts"] = metrics_plugin.detect_anomalies(context["metrics"])

            m = context["metrics"]
            text = await report_plugin.generate_report(
                restaurant_name=m["restaurant_name"],
                top_products=m["top_products"],
                avg_prep_seconds=m["avg_prep_seconds"],
                avg_prep_30d_seconds=m["avg_prep_30d_seconds"],
                alerts=context["alerts"],
            )
            print("\n=== Relatório ===\n" + text)
            continue

        # Fallback: gerar resposta livre do Gemini via conector do plugin de relatório
        text = await report_plugin._chat.complete(user_input)
        print(f"Agente: {text}")


