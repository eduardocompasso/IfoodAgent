import json
from datetime import datetime
from collections import Counter
from semantic_kernel.functions import kernel_function

class MetricsPlugin:

    def _calculate_clients_metrics_from_data(self, pedidos_data: dict) -> dict:
        client_metrics = {}
        pedidos = pedidos_data.get("pedidos", [])

        for pedido in pedidos:
            client_name = pedido["cliente"]["nome"]
            order_total = pedido["total"]

            if client_name not in client_metrics:
                client_metrics[client_name] = {
                    "numero_de_pedidos": 0,
                    "valor_total_gasto": 0.0
                }
            
            client_metrics[client_name]["numero_de_pedidos"] += 1
            client_metrics[client_name]["valor_total_gasto"] += order_total
            client_metrics[client_name]["valor_total_gasto"] = round(client_metrics[client_name]["valor_total_gasto"], 2)

        return client_metrics
    
    
    def _calculate_metrics_from_data(self, pedidos_data: dict) -> dict:
        
        restaurant_name = pedidos_data.get("restaurante", {}).get("nome", "Nome não encontrado")
        pedidos = pedidos_data.get("pedidos", [])
        
        grand_total_sold = 0.0
        sales_by_month = {}

        prep_time_by_day = {
            day: {'total_seconds': 0.0, 'count': 0} 
            for day in ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        }

        for pedido in pedidos:
            grand_total_sold += pedido["total"]

            try:
                pedido_dt = datetime.fromisoformat(pedido["data_pedido"])
                month_year = pedido_dt.strftime("%Y-%m")
                day_of_week = pedido["dia_semana"]

                if pedido.get("data_recebimento") and pedido.get("data_envio"):
                    recebimento_dt = datetime.fromisoformat(pedido["data_recebimento"])
                    envio_dt = datetime.fromisoformat(pedido["data_envio"])
                    
                    prep_time_delta = envio_dt - recebimento_dt
                    
                    prep_time_by_day[day_of_week]['total_seconds'] += prep_time_delta.total_seconds()
                    prep_time_by_day[day_of_week]['count'] += 1

            except (ValueError, TypeError, KeyError):
                continue

            if month_year not in sales_by_month:
                sales_by_month[month_year] = {
                    "total_value_sold": 0.0,
                    "sales_by_day": Counter()
                }
            
            sales_by_month[month_year]["total_value_sold"] += pedido["total"]
            sales_by_month[month_year]["sales_by_day"][day_of_week] += 1
        
        for month_data in sales_by_month.values():
            month_data["total_value_sold"] = round(month_data["total_value_sold"], 2)

        total_seconds_overall = sum(d['total_seconds'] for d in prep_time_by_day.values())
        total_orders_overall = sum(d['count'] for d in prep_time_by_day.values())
        
        average_prep_time_overall_seconds = total_seconds_overall / total_orders_overall if total_orders_overall > 0 else 0
        
        avg_prep_time_by_day_seconds = {
            day: int(data['total_seconds'] / data['count']) if data['count'] > 0 else 0
            for day, data in prep_time_by_day.items()
        }

        product_counter = Counter()
        for pedido in pedidos:
            for item in pedido.get("itens", []):
                product_counter[item["nome"]] += item["quantidade"]
        
        top_products = [
            {"name": name, "sold": count} for name, count in product_counter.most_common(3)
        ]

        return {
            "restaurant_name": restaurant_name,
            "grand_total_sold": round(grand_total_sold, 2),
            "average_preparation_time_seconds": int(average_prep_time_overall_seconds),
            "average_prep_time_by_day_seconds": avg_prep_time_by_day_seconds,
            "sales_by_month": sales_by_month,
            "top_products": top_products,
        }
    
    @kernel_function(name="query_metrics", description="Busca métricas atuais do restaurante a partir de um JSON de pedidos")
    def query_metrics(self, pedidos_json_str: str) -> dict:
        try:
            pedidos_data = json.loads(pedidos_json_str)
            return self._calculate_metrics_from_data(pedidos_data)
        except json.JSONDecodeError:
            return {"error": "JSON inválido"}
    
    @kernel_function(name="query_clients_metrics", description="Busca das metricas gerais dos clientes")
    def query_clients_metrics(self, pedidos_json_str: str) -> dict:
        try:
            pedidos_data = json.loads(pedidos_json_str)
            return self._calculate_clients_metrics_from_data(pedidos_data)
        except json.JSONDecodeError:
            return {"error": "JSON inválido"}

    @kernel_function(name="detect_anomalies", description="Detecta anomalias nas métricas")
    def detect_anomalies(self, metrics: dict) -> list:
        alerts = []
        if metrics["avg_prep_seconds"] > metrics["avg_prep_30d_seconds"] * 1.25:
            alerts.append("Tempo médio de preparo acima da média histórica (+25%).")
        for product in metrics["top_products"]:
            if product["sold"] < 50:
                alerts.append(f"Vendas do prato {product['name']} estão abaixo do esperado.")
        return alerts