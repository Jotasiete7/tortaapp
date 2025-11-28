"""
Patch to implement Price Normalization in WurmParser (Robust)
"""
import os

def apply_price_normalization_patch():
    file_path = 'wurm_parser.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add normalize_price function (if not present)
    if 'def normalize_price(price_val):' not in content:
        norm_func = """
def normalize_price(price_val):
    \"\"\"
    Converte strings de preço (ex: '1g 50s', '1.5k', '100') para valor numérico em Copper.
    Retorna float ou None se falhar.
    \"\"\"
    if pd.isna(price_val):
        return None
        
    if isinstance(price_val, (int, float)):
        return float(price_val)
        
    s = str(price_val).lower().strip()
    if not s or s == 'nan':
        return None
        
    # Remove caracteres indesejados
    s = s.replace(',', '.')
    
    try:
        # Tenta conversão direta primeiro
        return float(s)
    except ValueError:
        pass
        
    # Parse complexo (1g 50s 20c)
    total_copper = 0.0
    
    # Regex para extrair partes
    import re
    
    # Se tiver 'k' (1.5k = 1500) - assumindo que k = 1000 unidades base (copper?) ou silver?
    # No Wurm, k geralmente é usado para quantidade, não preço. Mas se for preço:
    if 'k' in s:
        try:
            val = float(re.sub(r'[^\\d.]', '', s))
            return val * 1000
        except:
            pass
            
    # Parse g/s/c
    parts = re.findall(r'([\\d.]+)\\s*([gsc])', s)
    if parts:
        for val, unit in parts:
            try:
                v = float(val)
                if unit == 'g': total_copper += v * 10000
                elif unit == 's': total_copper += v * 100
                elif unit == 'c': total_copper += v
            except:
                pass
        return total_copper if total_copper > 0 else None
        
    return None
"""
        # Insert after imports
        if 'import logging' in content:
            content = content.replace(
                'import logging',
                'import logging\nimport re' + norm_func
            )
            print("✓ Added normalize_price function")

    # 2. Apply normalization in load_data_and_build_cache
    # We look for the numeric conversion loop
    
    # This is the block we want to replace
    # We'll use a unique part of it to find it
    unique_part = "numeric_cols = ['main_qty', 'main_ql', 'main_dmg', 'main_wt', 'price_s']"
    
    if unique_part in content:
        # Find the start of the block (comment before it)
        block_start_marker = "# Converte numéricos"
        start_idx = content.find(block_start_marker)
        
        if start_idx != -1:
            # Find the end of the loop
            # It ends after the loop body. The next block usually starts with "# Otimização"
            end_marker = "# Otimização de tipos"
            end_idx = content.find(end_marker)
            
            if end_idx != -1:
                # Construct the new block
                new_block = """# Converte numéricos
    numeric_cols = ['main_qty', 'main_ql', 'main_dmg', 'main_wt']
    for col in numeric_cols:
        if col in df_master.columns:
            df_master[col] = pd.to_numeric(df_master[col], errors='coerce')
            
    # Normalização de Preço Especial
    if 'price_s' in df_master.columns:
        logger.info("Normalizando preços...")
        # Aplica a função de normalização
        df_master['price_s'] = df_master['price_s'].apply(normalize_price)
        # Agora converte para numérico final
        df_master['price_s'] = pd.to_numeric(df_master['price_s'], errors='coerce')
        
    """
                # Replace
                content = content[:start_idx] + new_block + content[end_idx:]
                print("✓ Applied price normalization logic")
            else:
                print("Could not find end of block (# Otimização de tipos)")
        else:
            print("Could not find start of block (# Converte numéricos)")
    else:
        # Maybe it was already applied or modified?
        if "numeric_cols = ['main_qty', 'main_ql', 'main_dmg', 'main_wt']" in content:
            print("Price normalization logic seems to be already applied.")
        else:
            print("Could not find numeric_cols definition to replace")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\n✅ Price Normalization patch applied!")

if __name__ == '__main__':
    apply_price_normalization_patch()
