# -*- coding: utf-8 -*-
import os

print("Starting patch process...")

# 1. Write threading_utils.py
threading_utils_content = r'''"""
Threading Utils - Async Data Loader
====================================
Handles heavy operations outside the GUI thread
"""

import threading
import queue
from typing import Callable


class AsyncDataLoader:
    """Async data loader using threading and queue."""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.is_loading = False
        
    def load_async(self, operation: Callable, callback: Callable, error_callback: Callable = None, *args, **kwargs):
        """
        Execute operation in background thread.
        
        Args:
            operation: Function to run in background
            callback: Function to call on success (receives result)
            error_callback: Function to call on error (receives exception)
            *args, **kwargs: Arguments for operation
            
        Returns:
            Callable: A checker function to be called periodically (e.g. via root.after)
        """
        def worker():
            try:
                result = operation(*args, **kwargs)
                self.queue.put(('success', result))
            except Exception as e:
                self.queue.put(('error', e))
                
        self.is_loading = True
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
        return lambda: self._check_queue(callback, error_callback)
    
    def _check_queue(self, callback, error_callback):
        """Check queue for results. Returns True if finished, False if still running."""
        try:
            status, data = self.queue.get_nowait()
            self.is_loading = False
            
            if status == 'success':
                if callback:
                    callback(data)
            elif status == 'error':
                if error_callback:
                    error_callback(data)
                else:
                    # Fallback if no error callback provided
                    print(f"Async Error: {data}")
            return True
        except queue.Empty:
            return False
'''
with open('threading_utils.py', 'w', encoding='utf-8') as f:
    f.write(threading_utils_content)
print("threading_utils.py updated")

# 2. Write ml_predictor.py
ml_predictor_content = r'''# ml_predictor.py
# Módulo de Preparação e Previsão de Machine Learning
# Responsável por:
# 1. Receber o DataFrame limpo do StatisticsEngine.
# 2. Realizar a Engenharia de Features necessária (e.g., One-Hot Encoding).
# 3. Carregar um modelo de ML pré-treinado (ou iniciar o processo de treinamento).
# 4. Gerar insights preditivos para a GUI.

import pandas as pd
# Importações futuras: from sklearn.cluster import KMeans
# from statsmodels.tsa.arima.model import ARIMA
import numpy as np

class MLPredictor:
    """
    Classe responsável por preparar os dados para ML e gerar previsões.
    """
    def __init__(self):
        # Aqui, no futuro, carregaremos o modelo treinado.
        self.model = None 
        # Ex: self.model = load_model('kmeans_trade_clusters.pkl')
        print("MLPredictor inicializado. Modelo de ML não carregado (stub).")

    def preprocess_for_ml(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ação A4: Projeta a sanitização e conversão de features categóricas para numéricas.
        Esta etapa é crucial para alimentar algoritmos como K-Means ou Regressão.

        :param df: DataFrame limpo do StatisticsEngine.
        :return: DataFrame pronto para o consumo do modelo de ML.
        """
        if df.empty:
            return pd.DataFrame()

        # 1. Feature Engineering: Conversão de Item Name (variável categórica)
        # O One-Hot Encoding cria colunas binárias para cada item.
        # Isto é essencial para que o modelo de ML possa processar o nome do item.
        df_ml = pd.get_dummies(df, columns=['Item Name'], prefix='item', drop_first=False)
        
        # 2. Extração de Features Temporais (útil para Séries Temporais ou Previsão)
        if 'Timestamp' in df.columns:
            df_ml['hour'] = df['Timestamp'].dt.hour
            df_ml['dayofweek'] = df['Timestamp'].dt.dayofweek
        
        # 3. Seleção de Features Numéricas para o Modelo
        # As features de preço e volume são geralmente usadas.
        features = [col for col in df_ml.columns if col.startswith(('Price', 'Volume', 'item_')) or col in ['hour', 'dayofweek']]
        
        # Remover colunas que possam causar vazamento de dados (e.g., Margem de Lucro calculada posteriormente)
        features_clean = [f for f in features if f not in ['Profit Margin', 'Risk Trend']] 
        
        return df_ml[features_clean]

    def predict_opportunities(self, df_ml_ready: pd.DataFrame) -> list:
        """
        Simula a execução de um modelo de ML para identificar oportunidades.
        Na FASE 5, este método será a espinha dorsal da aba "Insights Preditivos".
        
        :param df_ml_ready: DataFrame após o pré-processamento.
        :return: Lista de dicionários com insights (Item, Preço Anômalo, Sugestão).
        """
        if df_ml_ready.empty:
            return [{"insight": "Dados insuficientes para análise preditiva."}]
        
        # --- Lógica de Simulação (Para ser substituída na FASE 5) ---
        # Simula a detecção de preços anômalos (outliers)
        
        # Para fins de stub, calculamos o Z-Score para o preço de venda
        if 'Price WTS' in df_ml_ready.columns:
            mean_price = df_ml_ready['Price WTS'].mean()
            std_price = df_ml_ready['Price WTS'].std()
            
            # Identifica trades onde o preço está 2 desvios padrão acima da média
            df_anomalies = df_ml_ready[df_ml_ready['Price WTS'] > (mean_price + 2 * std_price)].head(3)
            
            insights = []
            for index, row in df_anomalies.iterrows():
                # Reverte o One-Hot Encoding para obter o nome do item original (simplificado)
                item_name_cols = [col for col in row.index if col.startswith('item_') and row[col] == 1]
                item_name = item_name_cols[0].replace('item_', '') if item_name_cols else 'UNKNOWN ITEM'

                insights.append({
                    "Item": item_name,
                    "Preço Anômalo (WTS)": f"R${row['Price WTS']:.2f}",
                    "Sugestão": "Venda Rápida (Preço acima da tendência).",
                    "Score de Risco": f"{np.random.rand():.2f}"
                })
            
            if not insights:
                return [{"insight": "Nenhuma anomalia de preço detectada neste conjunto de dados."}]
            
            return insights

        return [{"insight": "Coluna de preço não encontrada após pré-processamento."}]

    def run_prediction(self, df_clean: pd.DataFrame, analysis_type: str = 'all') -> list:
        """ Executa o pipeline completo: pré-processamento e previsão. """
        df_ml_ready = self.preprocess_for_ml(df_clean)
        # For now we just pass it through or ignore it as the logic is stubbed
        return self.predict_opportunities(df_ml_ready)
'''
with open('ml_predictor.py', 'w', encoding='utf-8') as f:
    f.write(ml_predictor_content)
print("ml_predictor.py updated")

# 3. Write wurm_stats_engine.py (Full overwrite)
wurm_stats_engine_content = r'''"""
Wurm Online Trade Analyzer - Statistics Engine
===============================================

Este módulo fornece a classe WurmStatsEngine para carregar e analisar
dados de trade do Wurm Online usando Pandas.

Autor: Senior Python Engineer
Data: 2025-11-26
"""

import pandas as pd
import json
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WurmStatsEngine:
    """
    Motor de estatísticas para análise de dados de trade do Wurm Online.
    
    Esta classe carrega dados de arquivos JSON Lines e fornece métodos
    para análise estatística avançada usando Pandas DataFrame.
    
    Attributes:
        data_path (Path): Caminho para o arquivo de dados
        df (pd.DataFrame): DataFrame principal com os dados de trade
        metadata (dict): Metadados sobre o dataset carregado
    """
    
    def __init__(self, data_path: Optional[Union[str, Path]] = None, 
                 sample_size: Optional[int] = None,
                 df: Optional[pd.DataFrame] = None) -> None:
        """
        Inicializa o WurmStatsEngine.
        
        Suporta Injeção de Dependência: pode receber um DataFrame já carregado
        ou um caminho para carregar os dados.
        
        Args:
            data_path: Caminho para o arquivo de dados JSON Lines (opcional se df for fornecido)
            sample_size: Número de linhas para carregar (None = todas).
            df: DataFrame injetado (opcional). Se fornecido, ignora data_path.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se nem data_path nem df forem fornecidos
        """
        self.data_path = Path(data_path) if data_path else None
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.sample_size = sample_size
        
        if df is not None:
            # Injeção de dependência: usa o DataFrame fornecido
            logger.info("Inicializando com DataFrame injetado.")
            self.df = df
            self._generate_metadata()
            logger.info(f"✔ Dados injetados: {len(self.df):,} registros")
        elif self.data_path:
            # Carregamento padrão
            if not self.data_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {self.data_path}")
            
            if not self.data_path.is_file():
                raise ValueError(f"O caminho não é um arquivo: {self.data_path}")
            
            logger.info(f"Iniciando carregamento de {self.data_path.name}...")
            self._load_data()
            self._generate_metadata()
            logger.info(f"✔ Dados carregados: {len(self.df):,} registros, {len(self.df.columns)} colunas")
        else:
            raise ValueError("É necessário fornecer 'data_path' ou 'df' para inicializar o engine.")
    
    def _load_data(self) -> None:
        """
        Carrega os dados usando o wurm_parser com suporte a cache inteligente.
        """
        try:
            import wurm_parser
            logger.info("Usando wurm_parser para carregamento inteligente...")
            
            # Passa o diretório pai do arquivo de dados para o parser
            data_dir = self.data_path.parent
            
            self.df = wurm_parser.load_data_and_build_cache(
                str(data_dir), 
                force_rebuild=False,
                sample_size=self.sample_size
            )
            
            if self.df.empty:
                raise ValueError("Nenhum dado retornado pelo parser")
                
            self._setup_index()
            
            logger.info(f"📋 Colunas carregadas: {', '.join(self.df.columns[:10])}...")
            
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar dados: {e}")

    def _setup_index(self) -> None:
        """Configura o índice do DataFrame para otimização."""
        if self.df is None: return
        
        # Garante que temos um índice temporal se possível
        if 'timestamp' in self.df.columns and not isinstance(self.df.index, pd.DatetimeIndex):
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df.set_index('timestamp', inplace=True)
            self.df.sort_index(inplace=True)

    def _generate_metadata(self) -> None:
        """Gera metadados básicos sobre o dataset."""
        if self.df is None: return
        
        self.metadata = {
            'total_records': len(self.df),
            'columns': list(self.df.columns),
            'memory_usage': self.df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
            'date_range': (
                self.df.index.min().isoformat() if not self.df.empty and isinstance(self.df.index, pd.DatetimeIndex) else None,
                self.df.index.max().isoformat() if not self.df.empty and isinstance(self.df.index, pd.DatetimeIndex) else None
            )
        }

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do dataset."""
        return self.metadata

    def filter_by_item(self, item_name: str, exact: bool = False) -> pd.DataFrame:
        """Retorna DataFrame filtrado por nome do item."""
        if self.df is None: return pd.DataFrame()
        if exact:
            return self.df[self.df['main_item'].str.fullmatch(item_name, case=False, na=False)]
        return self.df[self.df['main_item'].str.contains(item_name, case=False, na=False)]

    def calculate_volatility(self, item_name: str, window: int = 7) -> pd.DataFrame:
        """Calcula a volatilidade (desvio padrão) do preço."""
        df_item = self.filter_by_item(item_name)
        if df_item.empty or 'price_s' not in df_item.columns:
            return pd.DataFrame()
        
        # Group by date and take mean price
        daily_price = df_item.groupby('date')['price_s'].mean()
        volatility = daily_price.rolling(window=window).std()
        return volatility.reset_index(name='volatility')

    def calculate_mean_average(self, item_name: str, window: int = 7) -> pd.DataFrame:
        """Calcula a média móvel do preço."""
        df_item = self.filter_by_item(item_name)
        if df_item.empty or 'price_s' not in df_item.columns:
            return pd.DataFrame()
            
        daily_price = df_item.groupby('date')['price_s'].mean()
        ma = daily_price.rolling(window=window).mean()
        return ma.reset_index(name='moving_average')

    def calculate_profit_margins(self, item_name: str) -> pd.DataFrame:
        """
        Calcula margens de lucro (WTS - WTB) para um item.
        """
        df_item = self.filter_by_item(item_name, exact=False)
        
        if 'operation' not in df_item.columns or 'price_s' not in df_item.columns or 'date' not in df_item.columns:
            return pd.DataFrame()
            
        # Separate WTS and WTB
        wts = df_item[df_item['operation'] == 'WTS'].groupby('date')['price_s'].min()
        wtb = df_item[df_item['operation'] == 'WTB'].groupby('date')['price_s'].max()
        
        # Merge and calculate spread
        margins = pd.DataFrame({'min_wts': wts, 'max_wtb': wtb})
        margins['spread'] = margins['min_wts'] - margins['max_wtb']
        margins['margin_pct'] = (margins['spread'] / margins['max_wtb']) * 100
        
        return margins.dropna().sort_index()

    def calculate_risk_trends(self, item_name: str, window: int = 7) -> pd.DataFrame:
        """
        Calcula tendências de risco (Volatilidade + Média Móvel).
        """
        # Reuse existing methods but ensure they return compatible DataFrames
        vol = self.calculate_volatility(item_name, window)
        ma = self.calculate_mean_average(item_name, window)
        
        if vol.empty or ma.empty:
            return pd.DataFrame()
            
        # Merge on date
        risk = pd.merge(vol, ma, on='date', how='inner')
        risk['risk_score'] = risk['volatility'] / risk['moving_average']
        
        return risk.set_index('date').sort_index()

    def run_optimized(self) -> str:
        """
        Executa otimizações de memória e retorna um resumo.
        """
        if self.df is None: return "Sem dados."
        
        start_mem = self.df.memory_usage(deep=True).sum()
        
        # Downcast numeric columns
        for col in self.df.select_dtypes(include=['float']).columns:
            self.df[col] = pd.to_numeric(self.df[col], downcast='float')
        for col in self.df.select_dtypes(include=['int']).columns:
            self.df[col] = pd.to_numeric(self.df[col], downcast='integer')
            
        # Convert object to category where appropriate
        for col in self.df.select_dtypes(include=['object']).columns:
            if self.df[col].nunique() / len(self.df) < 0.5:
                self.df[col] = self.df[col].astype('category')
                
        end_mem = self.df.memory_usage(deep=True).sum()
        saved = (start_mem - end_mem) / 1024 / 1024
        
        return f"Otimização concluída. Economia de {saved:.2f} MB."

if __name__ == "__main__":
    # Teste rápido
    try:
        engine = WurmStatsEngine(data_path="data/wurm_trade_master_2025_clean.txt", sample_size=1000)
        print(engine.get_stats())
        
        # Teste de novos métodos
        print("\nTeste de Volatilidade:")
        print(engine.calculate_volatility("iron", window=3).head())
        
    except Exception as e:
        print(f"Erro no teste: {e}")
'''
with open('wurm_stats_engine.py', 'w', encoding='utf-8') as f:
    f.write(wurm_stats_engine_content)
print("wurm_stats_engine.py updated")

# 4. Patch superpy_app.py
with open('superpy_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = r'''    def _background_load(self):
        """Attempt to extract and load data in background thread."""
        def job():
            self.log_message('Carregando dados...')
            path = self.cfg_path.get() if hasattr(self, 'cfg_path') else TRADE_ZIP_PATH
            extracted = ensure_data_extracted(path, DEFAULT_DATA_DIR)
            if not extracted:
                self.log_message('Nenhum dado encontrado. Configure o caminho na aba Configs.', is_error=True)
                return
            
            # Load data using WurmStatsEngine
            data_path = path
            if os.path.isdir(extracted):
                 target_file = os.path.join(extracted, "wurm_trade_master_2025_clean.txt")
                 if os.path.exists(target_file):
                     data_path = target_file
                 else:
                     for f in os.listdir(extracted):
                         if f.endswith('.txt'):
                             data_path = os.path.join(extracted, f)
                             break
            
            try:
                self.engine = WurmStatsEngine(data_path)
                self.log_message(f'Dados carregados: {len(self.engine.df)} registros de {data_path}')
                self.reload_plugins()
            except Exception as e:
                self.log_message(f'Erro ao carregar dados: {e}', is_error=True)
                print(f"Error loading data: {e}")

        t = threading.Thread(target=job, daemon=True)
        t.start()'''

new_block = r'''    def _background_load(self):
        """Attempt to extract and load data in background thread using AsyncDataLoader."""
        self.log_message('Iniciando carregamento de dados (Async)...')
        
        path = self.cfg_path.get() if hasattr(self, 'cfg_path') else TRADE_ZIP_PATH
        
        # Define the heavy lifting function
        def load_job():
            extracted = ensure_data_extracted(path, DEFAULT_DATA_DIR)
            if not extracted:
                raise FileNotFoundError("Nenhum dado encontrado ou falha na extração.")
            
            # Determine target file
            data_path = path
            if os.path.isdir(extracted):
                 target_file = os.path.join(extracted, "wurm_trade_master_2025_clean.txt")
                 if os.path.exists(target_file):
                     data_path = target_file
                 else:
                     for f in os.listdir(extracted):
                         if f.endswith('.txt'):
                             data_path = os.path.join(extracted, f)
                             break
            
            # Initialize engine
            return WurmStatsEngine(data_path)

        # Define success callback
        def on_success(engine):
            self.engine = engine
            self.log_message(f'Dados carregados com sucesso: {len(self.engine.df):,} registros.')
            self.reload_plugins()
            self.set_status("Pronto")

        # Define error callback
        def on_error(e):
            self.log_message(f'Erro fatal ao carregar dados: {e}', is_error=True)
            self.set_status("Erro no carregamento")

        # Start async operation
        checker = self.async_loader.load_async(load_job, on_success, on_error)
        
        # Start polling loop (50ms latency as requested)
        self._poll_loader(checker)

    def _poll_loader(self, checker):
        """Poll the async loader every 50ms."""
        if not checker():
            # If checker returns False, it means still loading
            self.after(50, lambda: self._poll_loader(checker))'''

if new_block in content:
    print("superpy_app.py is already patched.")
elif old_block in content:
    new_content = content.replace(old_block, new_block)
    with open('superpy_app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("superpy_app.py patched")
else:
    print("Could not find block to replace in superpy_app.py (and it's not already patched).")
