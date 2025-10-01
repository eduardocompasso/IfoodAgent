import asyncio
import json
from plugins.metrics_plugin import MetricsPlugin
from plugins.report_plugin import ReportPlugin

try:
    with open('data/pedidos.json', 'r', encoding='utf-8') as f:
        PEDIDOS_JSON_STR = f.read()
except FileNotFoundError:
    print("Erro: Arquivo 'pedidos.json' não encontrado. As métricas não funcionarão.")
    PEDIDOS_JSON_STR = "{}"

async def run_agent():
    context = {}

    metrics_plugin = MetricsPlugin()
    report_plugin = ReportPlugin()


    metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
    alerts = metrics_plugin.detect_anomalies(metrics)

    report_text = await report_plugin.generate_report(
        restaurant_name=metrics["restaurant_name"],
        top_products=metrics["top_products"],
        avg_prep_seconds=metrics["avg_prep_seconds"],
        avg_prep_30d_seconds=metrics["avg_prep_30d_seconds"],
        alerts=alerts,
    )
    context["metrics"] = metrics
    context["clients_metrics"] = metrics
    context["alerts"] = alerts
    context["report"] = report_text


async def chat_loop():
    print("\nDigite mensagens para o agente. Comandos disponíveis: /metrics, /clients_metrics, /anomalies, /report, /exit")
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
            if "metrics" not in context:
                metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
            context["metrics"] = metrics

            print(f"Nome do Restaurante: {metrics.get('restaurant_name')}")
            print(f"Valor total vendido: {metrics.get('grand_total_sold')}")

            sales_month = metrics.get('sales_by_month', {})

            for month, month_data in sales_month.items():
                month_total = month_data.get('total_value_sold', 0.0)
                print(f"Mes: {month}")
                print(f"    Valor Vendido do mes: R$ {month_total:.2f}")
                
                days_data = month_data.get('sales_by_day', {})
                if not days_data:
                    print("     Nenhuma venda nesse mes")
                else:
                    print("     Pedidos por dia da semana:")
                    for day, count in sorted(days_data.items()):
                        print(f"        -{day}: {count} pedido(s)")

            print("TOP 3 produtos mais vendidos:")
            top_products = metrics.get('top_products', [])
            if not top_products:
                print("     Nenhum produto para exibir")
            else:
                for i, product in enumerate(top_products, 1):
                    print(f"    {i}. {product.get('name')} - {product.get('sold')} unidades")

            continue

        if user_input.strip().lower() == "/clients_metrics":
            if "clients_metrics" not in context:
                metrics = metrics_plugin.query_clients_metrics(PEDIDOS_JSON_STR)
            for name, values in metrics.items():
                print(f"{name} -> num_pedidos: {values['numero_de_pedidos']} | total_gasto: {values['valor_total_gasto']}")
            continue

        if user_input.strip().lower() == "/anomalies":
            if "metrics" not in context:
                context["metrics"] = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
            alerts = metrics_plugin.detect_anomalies(context["metrics"])
            context["alerts"] = alerts
            print(f"Agente: alertas -> {context.get('alerts', [])}")
            continue

        if user_input.strip().lower() == "/report":
            if "metrics" not in context:
                context["metrics"] = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
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


