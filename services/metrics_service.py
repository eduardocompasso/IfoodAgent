async def query_metrics(context):
    context["metrics"] = {
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
    return context


