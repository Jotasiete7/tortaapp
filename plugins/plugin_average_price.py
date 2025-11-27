import json

def run(data):
    """
    Calcula o preço médio dos itens no arquivo carregado.
    Espera um dicionário com a chave "entries" contendo objetos
    que possuem "item" e "price".
    """
    entries = data.get("entries", [])
    if not entries:
        return "Nenhum dado carregado."

    soma = 0
    count = 0
    for e in entries:
        try:
            soma += float(e.get("price", 0))
            count += 1
        except:
            pass

    if count == 0:
        return "Nenhum preço válido encontrado."

    media = soma / count
    return f"Preço médio geral: {media:.4f}"
