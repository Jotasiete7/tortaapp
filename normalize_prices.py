def normalize_price(price_val):
    """
    Converte strings de preço (ex: '1g 50s', '1.5k', '100') para valor numérico em Copper Coins (float).
    Retorna 0.0 se o valor for inválido ou NaN.
    """
    import re
    import pandas as pd
    
    # 1. Trata NaN e valores vazios
    if pd.isna(price_val) or str(price_val).lower().strip() in ['nan', 'none', '']:
        return 0.0
        
    s = str(price_val).lower().strip()
    if not s:
        return 0.0
        
    # Remove vírgulas e espaços extras
    s = s.replace(',', '.')
    
    total_copper = 0.0
    
    # 2. Tenta conversão direta (assumindo que um número simples é Copper)
    try:
        # Se for um número simples (ex: "1500.5"), assume-se que é Copper
        return float(s)
    except ValueError:
        pass
        
    # 3. Parse complexo (g/s/c/i)
    # Regex para extrair partes: (valor) (unidade g, s, c, i)
    parts = re.findall(r'([\\d.]+)\\s*([gsci])', s)
    
    if parts:
        for val, unit in parts:
            try:
                v = float(val)
                if unit == 'g': total_copper += v * 10000.0  # Gold (10000 Copper)
                elif unit == 's': total_copper += v * 100.0    # Silver (100 Copper)
                elif unit == 'c': total_copper += v            # Copper
                elif unit == 'i': total_copper += v / 100.0    # Iron (1/100 de Copper)
            except:
                # Ignora partes mal formatadas
                pass
        
        # Retorna o total de Copper Coins (float)
        return total_copper
        
    # 4. Trata o caso de falha total no parsing (retorna 0.0)
    return 0.0
