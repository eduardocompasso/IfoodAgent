from semantic_kernel.functions import kernel_function

class MetricsPlugin:
    @kernel_function(name="query_metrics", description="Busca métricas atuais do restaurante")
    def query_metrics(self) -> dict:
        return {
            "restaurant_id": 1,
            "restaurant_name": "Pizzaria do Zé",
            "top_products": [
                {"name": "Pizza Calabresa", "sold": 120},
                {"name": "Pizza Portuguesa", "sold": 95},
                {"name": "Esfiha Carne", "sold": 60},
            ],
            "avg_prep_seconds": 600,
            "avg_prep_30d_seconds": 720,
        }

    @kernel_function(name="detect_anomalies", description="Detecta anomalias nas métricas")
    def detect_anomalies(self, metrics: dict) -> list:
        alerts = []
        if metrics["avg_prep_seconds"] > metrics["avg_prep_30d_seconds"] * 1.25:
            alerts.append("Tempo médio de preparo acima da média histórica (+25%).")
        for product in metrics["top_products"]:
            if product["sold"] < 50:
                alerts.append(f"Vendas do prato {product['name']} estão abaixo do esperado.")
        return alerts


