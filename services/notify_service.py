async def notify(context):
    print("\n=== Relatório Gerado ===")
    print(context["report"])
    return context


