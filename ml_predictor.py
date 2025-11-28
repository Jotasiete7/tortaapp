import pandas as pd
# Importações futuras: from sklearn.cluster import KMeans
# from statsmodels.tsa.arima.model import ARIMA
import numpy as np
import re

class MLPredictor:
    """
    Classe responsável por preparar os dados para ML e gerar previsões.
    """
    def __init__(self):
        # Aqui, no futuro, carregaremos o modelo treinado.
        self.model = None 
        # Ex: self.model = load_model('kmeans_trade_clusters.pkl')
        print("MLPredictor inicializado. Modelo de ML não carregado (stub).")

    @staticmethod
    def parse_wurm_price(price_val):
        """
        Converte preço para Iron Coins.
        Aceita string (formato Wurm) ou numérico (Copper).
        """
        if pd.isna(price_val) or str(price_val).lower() in ['nan', 'none', '']:
            return 0
            
        # Se já for numérico (float/int), assume que é Copper (padrão do parser novo)
        if isinstance(price_val, (int, float)):
            return int(price_val * 100) # 1 Copper = 100 Iron
            
        price_str = str(price_val).lower().strip()
        
        # Tenta converter string numérica direta ("1500.0")
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

    @staticmethod
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

    def detect_anomalies(self, df_ml_ready: pd.DataFrame) -> list:
        """
        Detecta anomalias de preço usando Z-Score.
        """
        # Verifica se temos colunas de preço. O preprocessamento pode ter removido ou alterado nomes.
        # Assumindo que o df original tinha 'Price WTS' ou similar e foi mantido ou precisamos passar o df original também?
        # O preprocess_for_ml retorna apenas features numéricas.
        # Se 'Price WTS' estava no df original, ele deve estar em df_ml_ready se começar com 'Price'.
        
        # Vamos tentar identificar a coluna de preço.
        price_col = next((col for col in df_ml_ready.columns if 'Price' in col and 'WTS' in col), None)
        
        if df_ml_ready.empty or not price_col:
            return []
            
        # Filtra preços válidos
        df_valid = df_ml_ready[df_ml_ready[price_col] > 0].copy()
        if df_valid.empty:
            return []
            
        insights = []
        
        # Precisamos recuperar o nome do item. Como fizemos One-Hot, temos colunas item_NomeDoItem.
        # Isso é um pouco custoso de reverter, mas necessário para o insight.
        
        # Iterar sobre as colunas de item
        item_cols = [col for col in df_valid.columns if col.startswith('item_')]
        
        for item_col in item_cols:
            # Filtra linhas onde este item está presente (valor 1)
            item_data = df_valid[df_valid[item_col] == 1]
            
            if len(item_data) < 5: # Precisa de mínimo de dados para média confiável
                continue
                
            mean_price = item_data[price_col].mean()
            std_price = item_data[price_col].std()
            
            if std_price == 0:
                continue
                
            # Analisa as transações mais recentes (assumindo ordenação temporal ou pegando últimas)
            recent_txs = item_data.tail(3)
            
            for idx, row in recent_txs.iterrows():
                price = row[price_col]
                z_score = (price - mean_price) / std_price
                
                # Threshold de 1.5 sigmas
                if abs(z_score) > 1.5:
                    
                    tipo = "OPORTUNIDADE (BARATO)" if z_score < 0 else "ALERTA (CARO)"
                    acao = "COMPRAR" if z_score < 0 else "VENDER"
                    
                    # Formata preços (assumindo que estão em Copper ou similar, convertemos para Iron para formatar)
                    price_iron = int(price) 
                    mean_iron = int(mean_price)
                    
                    price_str = self.format_wurm_price(price_iron)
                    mean_str = self.format_wurm_price(mean_iron)
                    
                    item_name = item_col.replace('item_', '')
                    
                    insight = {
                        "Item": item_name,
                        "Preço": price_str,
                        "Tipo": tipo,
                        "Detalhe": f"{acao}! Preço {abs(z_score):.1f}x sigma longe da média ({mean_str})",
                        "Score": f"Z={z_score:.1f}"
                    }
                    insights.append(insight)
                    
        # Ordena por magnitude do Z-Score
        insights.sort(key=lambda x: abs(float(x['Score'].replace('Z=', ''))), reverse=True)
        return insights

    def predict_opportunities(self, df_ml_ready: pd.DataFrame) -> list:
        """
        Mantido para compatibilidade, mas a lógica principal foi movida para detect_anomalies.
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
            
        # 2. Oportunidades Gerais (Lógica antiga/stub)
        if not insights and analysis_type in ['all', 'general']:
            pass
                
        if not insights:
             return [{"insight": "Nenhum insight relevante encontrado."}]
             
        return insights
