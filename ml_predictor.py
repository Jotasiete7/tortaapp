# ml_predictor.py
# Módulo de Preparação e Previsão de Machine Learning
# Responsável por:
# 1. Receber o DataFrame limpo do StatisticsEngine.
# 2. Realizar a Engenharia de Features necessária (e.g., One-Hot Encoding).
# 3. Carregar um modelo de ML pré-treinado (ou iniciar o processo de treinamento).
# 4. Gerar insights preditivos para a GUI.

import pandas as pd
import numpy as np
import re

class MLPredictor:
    """
    Classe responsável por preparar os dados para ML e gerar previsões.
    """
    def __init__(self):
        self.model = None 
        print("MLPredictor inicializado. Modelo de ML não carregado (stub).")

    @staticmethod
    def parse_wurm_price(price_str):
        """
        Parse Wurm currency format to iron coins (smallest unit).
        
        Wurm currency system:
        - 100 iron (i) = 1 copper (c)
        - 100 copper (c) = 1 silver (s)  
        - 100 silver (s) = 1 gold (g)
        
        Examples:
        - "1s50c" -> 15000 iron
        - "2g" -> 20000000 iron
        - "50c" -> 5000 iron
        
        :param price_str: Price string (e.g., "1s50c", "2g", "100i")
        :return: Total value in iron coins
        """
        if pd.isna(price_str) or str(price_str).lower() in ['nan', 'none', '']:
            return 0
        
        price_str = str(price_str).lower().strip()
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
    def format_wurm_price(iron_value):
        """
        Format iron coins back to Wurm currency string.
        
        :param iron_value: Total value in iron coins
        :return: Formatted string (e.g., "1s50c")
        """
        if iron_value == 0:
            return "0i"
        
        gold = iron_value // 1000000
        remainder = iron_value % 1000000
        
        silver = remainder // 10000
        remainder = remainder % 10000
        
        copper = remainder // 100
        iron = remainder % 100
        
        parts = []
        if gold > 0:
            parts.append(f"{gold}g")
        if silver > 0:
            parts.append(f"{silver}s")
        if copper > 0:
            parts.append(f"{copper}c")
        if iron > 0:
            parts.append(f"{iron}i")
        
        return "".join(parts) if parts else "0i"

    def preprocess_for_ml(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados para ML com parsing de preços do Wurm.
        
        :param df: DataFrame limpo do StatisticsEngine.
        :return: DataFrame pronto para análise.
        """
        if df.empty:
            return pd.DataFrame()

        df_work = df.copy()
        
        # Parse price_s to numeric (iron coins)
        if 'price_s' in df_work.columns:
            df_work['price_iron'] = df_work['price_s'].apply(self.parse_wurm_price)
        else:
            df_work['price_iron'] = 0
        
        # Extract temporal features
        if 'timestamp' in df_work.columns:
            if not isinstance(df_work.index, pd.DatetimeIndex):
                df_work['timestamp'] = pd.to_datetime(df_work['timestamp'], errors='coerce')
            df_work['hour'] = df_work['timestamp'].dt.hour
            df_work['dayofweek'] = df_work['timestamp'].dt.dayofweek
        
        # Keep relevant columns for analysis
        analysis_cols = ['main_item', 'price_iron', 'operation', 'main_qty']
        if 'hour' in df_work.columns:
            analysis_cols.extend(['hour', 'dayofweek'])
        
        # Filter to existing columns
        analysis_cols = [col for col in analysis_cols if col in df_work.columns]
        
        return df_work[analysis_cols]

    def predict_opportunities(self, df_ml_ready: pd.DataFrame) -> list:
        """
        Gera insights baseados em análise de dados reais.
        
        :param df_ml_ready: DataFrame após pré-processamento.
        :return: Lista de dicionários com insights.
        """
        if df_ml_ready.empty or 'price_iron' not in df_ml_ready.columns:
            return [{"insight": "Dados insuficientes para análise preditiva."}]
        
        insights = []
        
        # Filter valid prices
        df_valid = df_ml_ready[df_ml_ready['price_iron'] > 0].copy()
        
        if df_valid.empty:
            return [{"insight": "Nenhum preço válido encontrado nos dados."}]
        
        # Group by item
        item_stats = df_valid.groupby('main_item').agg({
            'price_iron': ['mean', 'std', 'count', 'min', 'max']
        }).reset_index()
        
        item_stats.columns = ['item', 'price_mean', 'price_std', 'count', 'price_min', 'price_max']
        
        # Filter items with enough data
        item_stats = item_stats[item_stats['count'] >= 3].copy()
        
        if item_stats.empty:
            return [{"insight": "Dados insuficientes para análise estatística."}]
        
        # Sort by transaction count
        item_stats = item_stats.sort_values('count', ascending=False)
        
        # Generate insights for top items
        for idx, row in item_stats.head(10).iterrows():
            item_name = row['item']
            avg_price = row['price_mean']
            std_price = row['price_std']
            count = int(row['count'])
            min_price = row['price_min']
            max_price = row['price_max']
            
            # Calculate volatility
            volatility = (std_price / avg_price * 100) if avg_price > 0 else 0
            
            # Determine insight type
            if volatility > 50:
                tipo = "ALTA VOLATILIDADE"
                detalhe = f"Preço varia muito ({self.format_wurm_price(int(min_price))} - {self.format_wurm_price(int(max_price))})"
                score = f"{volatility:.0f}%"
            elif count > item_stats['count'].median():
                tipo = "ALTO VOLUME"
                detalhe = f"{count} transações registradas"
                score = f"Top {int((idx+1)/len(item_stats)*100)}%"
            else:
                tipo = "ESTÁVEL"
                detalhe = f"Preço médio consistente"
                score = f"{volatility:.0f}%"
            
            insights.append({
                "Item": item_name[:30],  # Limit length
                "Preço": self.format_wurm_price(int(avg_price)),
                "Tipo": tipo,
                "Detalhe": detalhe,
                "Score": score
            })
        
        if not insights:
            return [{"insight": "Nenhum insight gerado com os dados disponíveis."}]
        
        return insights

    def run_prediction(self, df_clean: pd.DataFrame, analysis_type: str = 'all') -> list:
        """Executa o pipeline completo: pré-processamento e previsão."""
        df_ml_ready = self.preprocess_for_ml(df_clean)
        return self.predict_opportunities(df_ml_ready)
