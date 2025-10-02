import asyncio
import json
from datetime import date, timedelta, datetime
from collections import Counter
from plugins.metrics_plugin import MetricsPlugin
from plugins.report_plugin import ReportPlugin

try:
    with open('data/pedidos.json', 'r', encoding='utf-8') as f:
        PEDIDOS_JSON_STR = f.read()
except FileNotFoundError:
    print("Erro: Arquivo 'data/pedidos.json' não encontrado. O agente não pode continuar.")
    PEDIDOS_JSON_STR = "{}"

async def run_agent():
    print("--- Executando agente em modo único ---")
    metrics_plugin = MetricsPlugin()
    
    metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
    clients_metrics = metrics_plugin.query_clients_metrics(PEDIDOS_JSON_STR)

    print("\n--- Métricas Gerais ---")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    
    print("\n--- Métricas de Clientes ---")
    print(json.dumps(clients_metrics, indent=2, ensure_ascii=False))


async def chat_loop():
    print("\nDigite mensagens para o agente. Comandos disponíveis: /metrics, /clients_metrics, /anomalies, /exit")
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
            metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
            context["metrics"] = metrics

            print("\n\n--- Métricas Gerais ---")
            print(f"Restaurante: {metrics.get('restaurant_name')}")

            grand_total = metrics.get('grand_total_sold', 0.0)
            print(f"Valor Total Vendido: R$ {grand_total:.2f}")

            print("\nAnálise de Tempo de Preparo:")
            
            avg_today_seconds = metrics.get('avg_prep_today_seconds', 0)
            if avg_today_seconds > 0:
                avg_today_minutes = avg_today_seconds / 60
                print(f"  Média (Hoje): {avg_today_minutes:.2f} minutos ({avg_today_seconds}s)")
            else:
                print("  Média (Hoje): Nenhum pedido concluído hoje.")

            avg_30d_seconds = metrics.get('avg_prep_last_30d_seconds', 0)
            if avg_30d_seconds > 0:
                avg_30d_minutes = avg_30d_seconds / 60
                print(f"  Média (Últimos 30 dias): {avg_30d_minutes:.2f} minutos ({avg_30d_seconds}s)")

            avg_overall_seconds = metrics.get('avg_prep_overall_seconds', 0)
            if avg_overall_seconds > 0:
                avg_overall_minutes = avg_overall_seconds / 60
                print(f"  Média (Geral): {avg_overall_minutes:.2f} minutos ({avg_overall_seconds}s)")
            
            avg_by_day = metrics.get('avg_prep_time_by_day_seconds', {})
            if avg_by_day:
                print("\n  Análise de Tempo por Dia da Semana (Média Geral):")
                for day, seconds in avg_by_day.items():
                    if seconds > 0:
                        minutes = seconds / 60
                        print(f"    - {day}: {minutes:.2f} min ({seconds}s)")

            sales_by_month = metrics.get('sales_by_month', {})
            print("\nAnálise Mensal de Vendas:")
            for month, month_data in sales_by_month.items():
                month_total = month_data.get('total_value_sold', 0.0)
                print(f"\n  --- Mês: {month} ---")
                print(f"    Valor Vendido no Mês: R$ {month_total:.2f}")
                days_data = month_data.get('sales_by_day', {})
                if days_data:
                    print("    Pedidos por Dia da Semana:")
                    for day, count in sorted(days_data.items()):
                        print(f"      - {day}: {count} pedido(s)")
            
            top_products = metrics.get('top_products', [])
            print("\nTop 3 Produtos Mais Vendidos:")
            for i, product in enumerate(top_products, 1):
                print(f"  {i}. {product.get('name')} - {product.get('sold')} unidades")
            
            print("\n-------------------------------------\n")
            continue

        if user_input.strip().lower() == "/clients_metrics":
            metrics = metrics_plugin.query_clients_metrics(PEDIDOS_JSON_STR)
            context["clients_metrics"] = metrics
            
            print("\n--- Métricas por Cliente ---")
            print(f"{'Cliente':<20} | {'Pedidos':<7} | {'Total Gasto':<15}")
            print("-" * 50)
            for name, values in metrics.items():
                total_gasto_str = f"R$ {values['valor_total_gasto']:.2f}"
                print(f"{name:<20} | {values['numero_de_pedidos']:<7} | {total_gasto_str:<15}")
            continue
        
        if user_input.strip().lower() == "/anomalies":
            print("\n🔎 Analisando métricas em busca de anomalias com a IA...")
            
            metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
            metrics_str = json.dumps(metrics, indent=2, ensure_ascii=False)

            anomaly_prompt = f"""
            Você é um analista de dados sênior especializado em operações de restaurantes.
            Sua tarefa é encontrar anomalias, padrões interessantes ou pontos de risco nos dados de métricas a seguir.
            Seja direto e aponte os achados em formato de lista (bullet points).
            Considere correlações entre os dados, como tempo de preparo em dias específicos, vendas de produtos em certos meses, etc.
            Se nada parecer fora do comum, apenas responda "Nenhuma anomalia significativa foi detectada.".

            Aqui estão os dados das métricas:
            {metrics_str}
            """

            response = await report_plugin._chat.complete(anomaly_prompt)
            
            print("\n--- Análise de Anomalias da IA ---")
            print(response)
            print("-------------------------------------\n")
            continue

        if user_input.strip().lower() == "/report":
            print("O comando /report está temporariamente desativado.")
            continue

        print("Agente: Comando não reconhecido. Use /metrics, /clients_metrics ou /anomalies.")

if __name__ == "__main__":
    try:
        asyncio.run(chat_loop())
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")