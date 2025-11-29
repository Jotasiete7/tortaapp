import pandas as pd
# Importações futuras: from sklearn.cluster import KMeans
# from statsmodels.tsa.arima.model import ARIMA
import numpy as np
import re
from wurm_parser import format_wurm_price

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
        # CORREÇÃO DE MEMÓRIA: Usar Top N Encoding em vez de One-Hot Encoding total
        
        target_col = 'main_item' if 'main_item' in df.columns else 'Item Name'
        
        if target_col not in df.columns:
            print(f"Aviso: Coluna de item '{target_col}' não encontrada no DataFrame.")
            return pd.DataFrame()

        # Configuração do Top N
        TOP_N = 50
        
        # 1.1. Identificar os Top N Itens
        top_items = df[target_col].value_counts().head(TOP_N).index.tolist()
        
        # 1.2. Criar uma nova coluna categórica: 'item_encoded'
        # Se o item estiver no Top N, mantém o nome. Caso contrário, define como 'Other'.
        # Usamos uma cópia para não alterar o df original se ele for usado fora
        df_processed = df.copy()
        df_processed['item_encoded'] = df_processed[target_col].apply(lambda x: x if x in top_items else 'Other')
        
        # 1.3. Aplicar One-Hot Encoding APENAS na nova coluna 'item_encoded'
        # Isso criará apenas ~51 colunas (Top 50 + Other), em vez de milhares.
        # CORREÇÃO: dtype=int para garantir 0/1 em vez de False/True
        df_ml = pd.get_dummies(df_processed, columns=['item_encoded'], prefix='item_encoded', drop_first=False, dtype=int)
        
        # 2. Extração de Features Temporais (útil para Séries Temporais ou Previsão)
        if 'Timestamp' in df_ml.columns:
            df_ml['hour'] = df_ml['Timestamp'].dt.hour
            df_ml['dayofweek'] = df_ml['Timestamp'].dt.dayofweek
        
        # 3. Seleção de Features Numéricas para o Modelo
        # As features de preço e volume são geralmente usadas.
        # Inclui price_iron se disponível
        # O prefixo agora é 'item_encoded_'
        features = [col for col in df_ml.columns if col.startswith(('Price', 'Volume', 'item_encoded_', 'price_')) or col in ['hour', 'dayofweek']]
        
        # Remover colunas que possam causar vazamento de dados (e.g., Margem de Lucro calculada posteriormente)
        features_clean = [f for f in features if f not in ['Profit Margin', 'Risk Trend']] 
        
        return df_ml[features_clean]

    def detect_anomalies(self, df_ml_ready: pd.DataFrame) -> list:
        """
        Detecta anomalias de preço usando Z-Score baseado na Mediana (Robust Z-Score).
        """
        # Identifica a coluna de preço numérica (Iron Coins)
        price_col = 'price_iron'
        if price_col not in df_ml_ready.columns:
            # Tenta fallback para Price WTS se price_iron não existir (compatibilidade)
            price_col = next((col for col in df_ml_ready.columns if 'Price' in col and 'WTS' in col), None)
        
        if df_ml_ready.empty or not price_col:
            return []
            
        # Filtra preços válidos (> 0)
        df_valid = df_ml_ready[df_ml_ready[price_col] > 0].copy()
        if df_valid.empty:
            return []
            
        insights = []
        
        # Iterar sobre as colunas de item (One-Hot Encoded)
        # Agora o prefixo é 'item_encoded_'
        item_cols = [col for col in df_valid.columns if col.startswith('item_encoded_')]
        
        for item_col in item_cols:
            # Ignora a categoria 'Other' pois é uma mistura de itens
            if item_col == 'item_encoded_Other':
                continue
                
            # Filtra linhas onde este item está presente (valor 1)
            item_data = df_valid[df_valid[item_col] == 1]
            
            if len(item_data) < 5: # Precisa de mínimo de dados para estatística confiável
                continue
                
            # 1. Calcular a Mediana (mais robusta que a Média)
            median_price = item_data[price_col].median()
            
            # 2. Calcular o Desvio Padrão (STD)
            std_price = item_data[price_col].std()
            
            if std_price == 0:
                continue
                
            # Analisa as transações mais recentes
            recent_txs = item_data.tail(3)
            
            for idx, row in recent_txs.iterrows():
                price = row[price_col]
                
                # Z-Score baseado na Mediana
                z_score = (price - median_price) / std_price
                
                # Threshold de 1.5 sigmas
                if abs(z_score) > 1.5:
                    
                    tipo = "OPORTUNIDADE (BARATO)" if z_score < 0 else "ALERTA (CARO)"
                    acao = "COMPRAR" if z_score < 0 else "VENDER"
                    
                    # Formata preços (Iron Coins)
                    price_iron = int(price) 
                    median_iron = int(median_price)
                    
                    price_str = format_wurm_price(price_iron)
                    median_str = format_wurm_price(median_iron)
                    
                    # Extração robusta do nome do item
                    # item_col é 'item_encoded_NomeDoItem'
                    try:
                        # Remove 'item_encoded_' (13 caracteres)
                        item_name = item_col[13:]
                    except IndexError:
                        item_name = item_col
                    
                    insight = {
                        "Item": item_name,
                        "Preço": price_str,
                        "Tipo": tipo,
                        "Detalhe": f"{acao}! Preço {abs(z_score):.1f}x sigma longe da mediana ({median_str})",
                        "Score": f"Z={z_score:.1f}"
                    }
                    insights.append(insight)
                    
        # Ordena por magnitude do Z-Score
        insights.sort(key=lambda x: abs(float(x['Score'].replace('Z=', ''))), reverse=True)
        return insights

    def predict_opportunities(self, df_ml_ready: pd.DataFrame) -> list:
        """
        Mantido para compatibilidade.
        """
        return self.detect_anomalies(df_ml_ready)

    def run_prediction(self, df_clean: pd.DataFrame, analysis_type: str = 'all') -> list:
        """ Executa o pipeline completo: pré-processamento e previsão. """
        df_ml_ready = self.preprocess_for_ml(df_clean)
        
        insights = []
        
        # 1. Anomalias (Z-Score) - Prioridade Alta
        if analysis_type in ['all', 'anomalies']:
            anomalies = self.detect_anomalies(df_ml_ready)
            insights.extend(anomalies)
            
        # 2. Oportunidades Gerais
        if not insights and analysis_type in ['all', 'general']:
            pass
                
        # CORREÇÃO: Retorna lista vazia se não houver insights
        if not insights:
             return []
             
        return insights
