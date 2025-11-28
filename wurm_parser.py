import pandas as pd
import os
import glob
import json
import pickle
import logging
import re
def normalize_price(price_val):
    """
    Converte strings de preço (ex: '1g 50s', '1.5k', '100') para valor numérico em Copper.
    Retorna float ou None se falhar.
    """
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
            val = float(re.sub(r'[^\d.]', '', s))
            return val * 1000
        except:
            pass
            
    # Parse g/s/c
    parts = re.findall(r'([\d.]+)\s*([gsc])', s)
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

import re
def normalize_price(price_val):
    """
    Converte strings de preço (ex: '1g 50s', '1.5k', '100') para valor numérico em Copper.
    Retorna float ou None se falhar.
    """
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
            val = float(re.sub(r'[^\d.]', '', s))
            return val * 1000
        except:
            pass
            
    # Parse g/s/c
    parts = re.findall(r'([\d.]+)\s*([gsc])', s)
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
        logger.info("Normalizando preços...")
        # Aplica a função de normalização
        df_master['price_s'] = df_master['price_s'].apply(normalize_price)
        # Agora converte para numérico final
        df_master['price_s'] = pd.to_numeric(df_master['price_s'], errors='coerce')

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
