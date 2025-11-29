import pandas as pd
import os
import glob
import json
import pickle
import logging
import re

def parse_wurm_price(price_val):
    """
    Converte preço para Iron Coins.
    Aceita string (formato Wurm) ou numérico (Copper/Iron).
    Retorna int (Iron Coins).
    """
    if pd.isna(price_val) or str(price_val).lower() in ['nan', 'none', '']:
        return 0
        
    # Se já for numérico (float/int), assume que é Copper (padrão antigo) e converte para Iron
    if isinstance(price_val, (int, float)):
        return int(price_val * 100) # 1 Copper = 100 Iron
        
    price_str = str(price_val).lower().strip()
    
    # Tenta converter string numérica direta ("1500.0") -> Assume Copper
    try:
        val = float(price_str)
        return int(val * 100)
    except ValueError:
        pass
        
    total_iron = 0
    
    # Parse gold (1g = 100s = 10000c = 1000000i)
    gold_match = re.search(r'(\d+)g', price_str)
    if gold_match:
        total_iron += int(gold_match.group(1)) * 1000000
    
    # Parse silver (1s = 100c = 10000i)
    silver_match = re.search(r'(\d+)s', price_str)
    if silver_match:
        total_iron += int(silver_match.group(1)) * 10000
    
    # Parse copper (1c = 100i)
    copper_match = re.search(r'(\d+)c', price_str)
    if copper_match:
        total_iron += int(copper_match.group(1)) * 100
    
    # Parse iron
    iron_match = re.search(r'(\d+)i', price_str)
    if iron_match:
        total_iron += int(iron_match.group(1))
    
    return total_iron

def format_wurm_price(iron_val):
    """
    Converte valor em Iron Coins de volta para string formatada (1g 50s 25c).
    """
    if not isinstance(iron_val, (int, float)):
        return "0i"
        
    iron_val = int(iron_val)
    if iron_val == 0:
        return "0i"
        
    g = iron_val // 1000000
    rem = iron_val % 1000000
    s = rem // 10000
    rem = rem % 10000
    c = rem // 100
    i = rem % 100
    
    parts = []
    if g > 0: parts.append(f"{g}g")
    if s > 0: parts.append(f"{s}s")
    if c > 0: parts.append(f"{c}c")
    if i > 0: parts.append(f"{i}i")
    
    return " ".join(parts)

from pathlib import Path

# Configuração de logging
logger = logging.getLogger(__name__)

# O diretório 'data' onde o cache será armazenado
# Assume que este arquivo está na raiz do app ou em uma subpasta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "data")
CACHE_FILE = os.path.join(CACHE_DIR, "trade_data_cache.parquet")
CACHE_FILE_PKL = os.path.join(CACHE_DIR, "trade_data_cache.pkl")

def _get_latest_data_timestamp(data_dir: str) -> float:
    """Encontra o timestamp de modificação mais recente de qualquer arquivo de dados na pasta."""
    latest_time = 0.0
    # Busca arquivos txt e json (formatos prováveis)
    search_patterns = ['*.txt', '*.json', '*.log']
    
    for pattern in search_patterns:
        for file_path in glob.glob(os.path.join(data_dir, '**', pattern), recursive=True):
            # Ignora arquivos de cache ou diretório de dados do app se estiver dentro
            if 'trade_data_cache' in file_path:
                continue
                
            try:
                latest_time = max(latest_time, os.path.getmtime(file_path))
            except OSError:
                continue
    return latest_time

def load_data_and_build_cache(data_dir: str, force_rebuild: bool = False, sample_size: int = None) -> pd.DataFrame:
    """
    Carrega dados de trade, utilizando cache se disponível e atualizado.
    
    Args:
        data_dir (str): Diretório contendo os arquivos de dados brutos.
        force_rebuild (bool): Se True, força a reconstrução do cache.
        sample_size (int): Limite de linhas para leitura (apenas para raw loading).
        
    Returns:
        pd.DataFrame: DataFrame com os dados carregados.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 1. Checa a validade do cache
    cache_exists = os.path.exists(CACHE_FILE) or os.path.exists(CACHE_FILE_PKL)
    
    # Se data_dir for um arquivo, pega o diretório pai
    if os.path.isfile(data_dir):
        data_dir = os.path.dirname(data_dir)
        
    latest_data_mtime = _get_latest_data_timestamp(data_dir)
    
    if not force_rebuild and cache_exists:
        try:
            # Tenta carregar o cache e verifica se é mais novo que a fonte
            cache_file_to_use = CACHE_FILE if os.path.exists(CACHE_FILE) else CACHE_FILE_PKL
            
            cache_mtime = os.path.getmtime(cache_file_to_use)
            
            # Se o cache for mais novo que os dados (ou se não achou dados recentes), usa o cache
            if cache_mtime > latest_data_mtime or latest_data_mtime == 0:
                logger.info(f"Cache encontrado em {cache_file_to_use}. Carregando cache...")
                if cache_file_to_use.endswith('.parquet'):
                    return pd.read_parquet(cache_file_to_use)
                else:
                    with open(cache_file_to_use, 'rb') as f:
                        return pickle.load(f)
            else:
                logger.info("Cache desatualizado. Reconstruindo...")
        except Exception as e:
            logger.warning(f"Erro ao carregar cache ({cache_file_to_use}): {e}. Reconstruindo...")

    # 2. Reconstrução do cache
    logger.info(f"Processando arquivos brutos em {data_dir}...")
    
    data_list = []
    
    # Busca arquivos .txt (assumindo formato JSON Lines conforme WurmStatsEngine original)
    data_files = glob.glob(os.path.join(data_dir, '**', '*.txt'), recursive=True)
    
    if not data_files:
        logger.warning("Nenhum arquivo .txt encontrado no diretório de dados.")
        return pd.DataFrame()
        
    for file_path in data_files:
        try:
            logger.info(f"Lendo {os.path.basename(file_path)}...")
            with open(file_path, 'r', encoding='latin-1') as f:
                for i, line in enumerate(f):
                    if sample_size and i >= sample_size:
                        break
                    try:
                        data_list.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file_path}: {e}")

    if not data_list:
        return pd.DataFrame()

    df_master = pd.DataFrame(data_list)
    
    # 3. Limpeza e Processamento Final
    logger.info("Processando DataFrame...")
    
    # Remove linhas vazias
    df_master.dropna(how='all', inplace=True)
    
    # Converte datas
    for col in ['timestamp', 'date']:
        if col in df_master.columns:
            df_master[col] = pd.to_datetime(df_master[col], errors='coerce')
            
    # Converte numéricos
    numeric_cols = ['main_qty', 'main_ql', 'main_dmg', 'main_wt']
    for col in numeric_cols:
        if col in df_master.columns:
            df_master[col] = pd.to_numeric(df_master[col], errors='coerce')
            
    # Normalização de Preço Especial
    if 'price_s' in df_master.columns:
        logger.info("Normalizando preços (Iron Coins)...")
        # Cria coluna price_iron usando o novo parser
        df_master['price_iron'] = df_master['price_s'].apply(parse_wurm_price)
        
        # Mantém compatibilidade: price_s como float (Copper)
        # Iron / 100 = Copper
        df_master['price_s'] = df_master['price_iron'] / 100.0

    # Otimização de tipos (Categorias)
    if 'main_item' in df_master.columns:
        df_master['main_item'] = df_master['main_item'].astype('category')
        
    if 'operation' in df_master.columns:
        df_master['operation'] = df_master['operation'].astype('category')

    # 4. Salva o cache
    try:
        # Tenta salvar no formato Parquet
        df_master.to_parquet(CACHE_FILE, index=False)
        logger.info(f"Cache salvo com sucesso em {CACHE_FILE}.")
        
        # Remove cache antigo PKL se existir
        if os.path.exists(CACHE_FILE_PKL):
             os.remove(CACHE_FILE_PKL)
             
    except Exception as e:
        logger.warning(f"Falha ao salvar cache Parquet ({e}). Salvando em Pickle...")
        try:
            with open(CACHE_FILE_PKL, 'wb') as f:
                 pickle.dump(df_master, f)
        except Exception as pkl_e:
            logger.error(f"Falha ao salvar cache Pickle: {pkl_e}")
        
    return df_master
