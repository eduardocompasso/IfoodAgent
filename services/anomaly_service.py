async def detect_anomalies(context):
    metrics = context["metrics"]
    alerts = []

    if metrics["avg_prep_seconds"] > metrics["avg_prep_30d_seconds"] * 1.25:
        alerts.append("Tempo médio de preparo acima da média histórica (+25%).")

    for product in metrics["top_products"]:
        if product["sold"] < 50:
            alerts.append(f"Vendas do prato {product['name']} estão abaixo do esperado.")

    context["alerts"] = alerts
    return context


