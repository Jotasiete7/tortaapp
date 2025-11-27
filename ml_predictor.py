# ml_predictor.py
# Módulo de Preparação e Previsão de Machine Learning
# Responsável por:
# 1. Receber o DataFrame limpo do StatisticsEngine.
# 2. Realizar a Engenharia de Features necessária.
# 3. Gerar insights preditivos baseados em estatística (Z-Score/IQR).

import pandas as pd
import numpy as np

class MLPredictor:
    """
    Classe responsável por preparar os dados e gerar insights estatísticos/ML.
    """
    def __init__(self):
        print("MLPredictor inicializado.")

    def preprocess_for_ml(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara o DataFrame para análise.
        Foca em limpar dados nulos e garantir tipos numéricos corretos.

        :param df: DataFrame limpo do StatisticsEngine.
        :return: DataFrame pronto para análise.
        """
        if df.empty:
            return pd.DataFrame()

        # Trabalhar com uma cópia para não afetar o original
        df_ml = df.copy()

        # Garantir que temos colunas essenciais
        required_cols = ['price_s', 'main_item']
        for col in required_cols:
            if col not in df_ml.columns:
                return pd.DataFrame() # Falta dados essenciais

        # Converter preço para numérico se não for
        df_ml['price_s'] = pd.to_numeric(df_ml['price_s'], errors='coerce')
        
        # Remover linhas sem preço ou item
        df_ml.dropna(subset=['price_s', 'main_item'], inplace=True)

        return df_ml

    def predict_opportunities(self, df_ml_ready: pd.DataFrame) -> list:
        """
        Identifica oportunidades de mercado baseadas em anomalias de preço (Z-Score).
        
        :param df_ml_ready: DataFrame pré-processado.
        :return: Lista de dicionários com insights.
        """
        if df_ml_ready.empty:
            return [{"insight": "Dados insuficientes para análise."}]
        
        insights = []
        
        # Análise por Item (agrupado)
        # Calculamos média e desvio padrão por item para encontrar anomalias locais
        # Filtramos apenas itens com volume razoável para ter significância estatística
        
        item_stats = df_ml_ready.groupby('main_item')['price_s'].agg(['mean', 'std', 'count'])
        # Considerar apenas itens com pelo menos 5 transações
        significant_items = item_stats[item_stats['count'] >= 5]
        
        if significant_items.empty:
             return [{"insight": "Poucos dados por item para análise estatística robusta (min 5 trades)."}]

        # Iterar sobre itens significativos e buscar outliers nos dados originais
        # Isso pode ser lento se houver muitos itens, então vamos otimizar
        # Vamos calcular o Z-Score para cada transação RELATIVO ao seu item
        
        # Merge das estatísticas de volta ao dataframe original
        df_merged = df_ml_ready.merge(significant_items, on='main_item', suffixes=('', '_stats'))
        
        # Calcular Z-Score: (Preço - Média) / Std
        df_merged['z_score'] = (df_merged['price_s'] - df_merged['mean']) / df_merged['std']
        
        # Identificar anomalias: |Z-Score| > 2 (aprox 2 desvios padrão)
        # Z-Score < -2: Preço muito abaixo da média (Oportunidade de Compra?)
        # Z-Score > 2: Preço muito acima da média (Oportunidade de Venda?)
        
        anomalies = df_merged[df_merged['z_score'].abs() > 2].copy()
        
        # Ordenar por magnitude da anomalia
        anomalies.sort_values(by='z_score', key=abs, ascending=False, inplace=True)
        
        # Limitar a top 20 insights para não poluir a UI
        top_anomalies = anomalies.head(20)
        
        for _, row in top_anomalies.iterrows():
            item = row['main_item']
            price = row['price_s']
            mean_price = row['mean']
            z = row['z_score']
            
            if z < -2:
                tipo = "Preço Baixo (Compra)"
                desc = f"Está {abs(z):.1f}x desvios abaixo da média ({mean_price:.2f}s)."
            else:
                tipo = "Preço Alto (Venda)"
                desc = f"Está {z:.1f}x desvios acima da média ({mean_price:.2f}s)."
            
            insights.append({
                "Item": item,
                "Preço": f"{price:.2f}s",
                "Tipo": tipo,
                "Detalhe": desc,
                "Score": round(abs(z), 2)
            })
            
        if not insights:
            return [{"insight": "Nenhuma anomalia significativa detectada (Z-Score > 2)."}]
            
        return insights

    def run_prediction(self, df_clean: pd.DataFrame) -> list:
        """ Executa o pipeline completo: pré-processamento e previsão. """
        df_ml_ready = self.preprocess_for_ml(df_clean)
        return self.predict_opportunities(df_ml_ready)
