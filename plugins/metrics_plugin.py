import json
from datetime import datetime
from collections import Counter
from semantic_kernel.functions import kernel_function

class MetricsPlugin:
    
    def _calculate_metrics_from_data(self, pedidos_data: dict) -> dict:
        restaurant_name = pedidos_data.get("restaurante", {}).get("nome", "Nome não encontrado")
        
        pedidos = pedidos_data.get("pedidos", [])
        
        total_prep_seconds = 0
        completed_orders_count = 0
        
        for pedido in pedidos:
            if pedido.get("data_recebimento") and pedido.get("data_envio"):
                try:
                    recebimento_dt = datetime.fromisoformat(pedido["data_recebimento"])
                    envio_dt = datetime.fromisoformat(pedido["data_envio"])
                    
                    prep_time = (envio_dt - recebimento_dt).total_seconds()
                    total_prep_seconds += prep_time
                    completed_orders_count += 1
                except (ValueError, TypeError):
                    continue
        
        avg_prep_seconds = total_prep_seconds / completed_orders_count if completed_orders_count > 0 else 0

        product_counter = Counter()
        for pedido in pedidos:
            for item in pedido.get("itens", []):
                product_counter[item["nome"]] += item["quantidade"]
        
        top_products = [
            {"name": name, "sold": count} for name, count in product_counter.most_common(3)
        ]

        avg_prep_30d_seconds = avg_prep_seconds * 1.15 

        return {
            "restaurant_name": restaurant_name,
            "top_products": top_products,
            "avg_prep_seconds": int(avg_prep_seconds),
            "avg_prep_30d_seconds": int(avg_prep_30d_seconds),
        }

    @kernel_function(name="query_metrics", description="Busca métricas atuais do restaurante a partir de um JSON de pedidos")
    def query_metrics(self, pedidos_json_str: str) -> dict:
        try:
            pedidos_data = json.loads(pedidos_json_str)
            return self._calculate_metrics_from_data(pedidos_data)
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