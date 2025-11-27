# --------------------------------------------
# Pacote 1 — Estatísticas Básicas
# Todos os plugins abaixo devem ficar na pasta plugins/
# Cada função "run" recebe (data, **kwargs)
# --------------------------------------------

import statistics

# ---------------------------
# 1) Média de preço por item
# ---------------------------
def average_price(data, item=None):
    entries = data.get("entries", [])
    if item:
        entries = [e for e in entries if item.lower() in e.get("item", "").lower()]
    prices = [float(e.get("price", 0)) for e in entries]
    if not prices:
        return "Nenhum preço encontrado."
    return f"Média: {sum(prices)/len(prices):.4f}"

# ---------------------------
# 2) Preço mínimo por item
# ---------------------------
def min_price(data, item=None):
    entries = data.get("entries", [])
    if item:
        entries = [e for e in entries if item.lower() in e.get("item", "").lower()]
    prices = [float(e.get("price", 0)) for e in entries]
    if not prices:
        return "Nenhum preço encontrado."
    return f"Mínimo: {min(prices):.4f}"

# ---------------------------
# 3) Preço máximo por item
# ---------------------------
def max_price(data, item=None):
    entries = data.get("entries", [])
    if item:
        entries = [e for e in entries if item.lower() in e.get("item", "").lower()]
    prices = [float(e.get("price", 0)) for e in entries]
    if not prices:
        return "Nenhum preço encontrado."
    return f"Máximo: {max(prices):.4f}"

# ---------------------------
# 4) Mediana de preços
# ---------------------------
def median_price(data, item=None):
    entries = data.get("entries", [])
    if item:
        entries = [e for e in entries if item.lower() in e.get("item", "").lower()]
    prices = [float(e.get("price", 0)) for e in entries]
    if not prices:
        return "Nenhum preço encontrado."
    return f"Mediana: {statistics.median(prices):.4f}"

# ---------------------------
# 5) Moda de preços
# ---------------------------
def mode_price(data, item=None):
    entries = data.get("entries", [])
    if item:
        entries = [e for e in entries if item.lower() in e.get("item", "").lower()]
    prices = [float(e.get("price", 0)) for e in entries]
    if not prices:
        return "Nenhum preço encontrado."

    try:
        m = statistics.mode(prices)
        return f"Moda: {m:.4f}"
    except statistics.StatisticsError:
        return "Moda indefinida (múltiplos valores igualmente comuns)."

# ---------------------------
# 6) Contagem de vendas
# ---------------------------
def count_sales(data, item=None):
    entries = data.get("entries", [])
    if item:
        entries = [e for e in entries if item.lower() in e.get("item", "").lower()]
    return f"Total de vendas: {len(entries)}"

# ---------------------------
# 7) Soma total de moedas
# ---------------------------
def total_volume(data, item=None):
    entries = data.get("entries", [])
    if item:
        entries = [e for e in entries if item.lower() in e.get("item", "").lower()]
    total = sum(float(e.get("price", 0)) for e in entries)
    return f"Volume total: {total:.4f}"

# ---------------------------
# 8) Variação percentual
# ---------------------------
def variation(data, item=None):
    entries = data.get("entries", [])
    if item:
        entries = [e for e in entries if item.lower() in e.get("item", "").lower()]
    prices = [float(e.get("price", 0)) for e in entries]
    if len(prices) < 2:
        return "Dados insuficientes."
    start, end = prices[0], prices[-1]
    if start == 0:
        return "Variação não calculável (preço inicial é zero)."
    pct = ((end - start) / start) * 100
    return f"Variação: {pct:.2f}%"

# ---------------------------
# Plugin principal (agregado)
# ---------------------------
def run(data, item=None):
    return (
        average_price(data, item) + "\n" +
        min_price(data, item) + "\n" +
        max_price(data, item) + "\n" +
        median_price(data, item) + "\n" +
        mode_price(data, item) + "\n" +
        count_sales(data, item) + "\n" +
        total_volume(data, item) + "\n" +
        variation(data, item)
    )
