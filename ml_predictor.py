# ml_predictor.py
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
        return self.predict_opportunities(df_ml_ready)

