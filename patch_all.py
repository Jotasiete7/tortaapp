import os

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

    def run_prediction(self, df_clean: pd.DataFrame) -> list:
        """ Executa o pipeline completo: pré-processamento e previsão. """
        df_ml_ready = self.preprocess_for_ml(df_clean)
        return self.predict_opportunities(df_ml_ready)
'''
with open('ml_predictor.py', 'w', encoding='utf-8') as f:
    f.write(ml_predictor_content)
print("ml_predictor.py updated")

# 3. Patch superpy_app.py
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

if old_block in content:
    new_content = content.replace(old_block, new_block)
    with open('superpy_app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("superpy_app.py patched")
else:
    print("Could not find block to replace in superpy_app.py")
    # Debug: print first 100 chars of old_block and content to see mismatch
    print(f"Old block start: {old_block[:100]}")
