def run(data, query=None, mode="partial"):
    """
    Busca refinada.
    - query: texto a procurar
    - mode: "exact", "partial" ou "fuzzy" (simplificado)
    """

    if query is None or query.strip() == "":
        return "Nenhuma busca realizada."

    entries = data.get("entries", [])
    query = query.lower()
    resultados = []

    for e in entries:
        item = e.get("item", "").lower()

        if mode == "exact":
            if item == query:
                resultados.append(e)

        elif mode == "partial":
            if query in item:
                resultados.append(e)

        elif mode == "fuzzy":
            # fuzzy extremamente simples: aceita se metade dos termos
            termos = query.split()
            score = sum(1 for t in termos if t in item)
            if score >= len(termos) / 2:
                resultados.append(e)

    if not resultados:
        return "Nenhum resultado encontrado."

    # Formata saída
    linhas = []
    for r in resultados[:200]:  # limite para não travar a janela
        linhas.append(f"{r.get('item')} — {r.get('price')}s")

    return "\n".join(linhas)
