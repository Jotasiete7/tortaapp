# ml_predictor.py
# Módulo de Preparação e Previsão de Machine Learning
# Responsável por:
# 1. Receber o DataFrame limpo do StatisticsEngine.
# 2. Realizar a Engenharia de Features necessária.
# 3. Gerar insights preditivos baseados em estatística (Z-Score/IQR).

import pandas as pd
import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Isolation Forest disabled.")

class MLPredictor:
    """
    Classe responsável por preparar os dados e gerar insights estatísticos/ML.
    """
    def __init__(self, use_isolation_forest=True):
        """
        Inicializa o MLPredictor.
        
        Args:
            use_isolation_forest: Se True, usa Isolation Forest além do Z-Score
        """
        self.use_isolation_forest = use_isolation_forest and SKLEARN_AVAILABLE
        self.model = None
        print(f"MLPredictor inicializado (Isolation Forest: {self.use_isolation_forest}).")

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

    def predict_with_isolation_forest(self, df_ml_ready: pd.DataFrame) -> list:
        """
        Usa Isolation Forest para detectar anomalias de forma não supervisionada.
        
        :param df_ml_ready: DataFrame pré-processado.
        :return: Lista de dicionários com insights.
        """
        if not SKLEARN_AVAILABLE:
            return [{"insight": "Isolation Forest não disponível. Instale scikit-learn."}]
            
        if df_ml_ready.empty or len(df_ml_ready) < 10:
            return [{"insight": "Dados insuficientes para Isolation Forest (min 10 registros)."}]
        
        insights = []
        
        # Prepara features para o modelo
        # Usamos preço e, se disponível, outras features numéricas
        feature_cols = ['price_s']
        
        # Adiciona outras features se disponíveis
        optional_features = ['main_qty', 'main_ql', 'main_dmg']
        for col in optional_features:
            if col in df_ml_ready.columns:
                df_ml_ready[col] = pd.to_numeric(df_ml_ready[col], errors='coerce')
                if df_ml_ready[col].notna().sum() > len(df_ml_ready) * 0.5:  # Se >50% válidos
                    feature_cols.append(col)
        
        # Prepara dados
        X = df_ml_ready[feature_cols].copy()
        X = X.dropna()
        
        if len(X) < 10:
            return [{"insight": "Dados insuficientes após limpeza."}]
        
        # Treina Isolation Forest
        # contamination: proporção esperada de outliers (5%)
        iso_forest = IsolationForest(
            contamination=0.05,
            random_state=42,
            n_estimators=100
        )
        
        # Prediz anomalias (-1 = anomalia, 1 = normal)
        predictions = iso_forest.fit_predict(X)
        scores = iso_forest.score_samples(X)  # Scores de anomalia (menor = mais anômalo)
        
        # Adiciona predições ao DataFrame
        X['anomaly'] = predictions
        X['anomaly_score'] = scores
        X['main_item'] = df_ml_ready.loc[X.index, 'main_item']
        X['price_s'] = df_ml_ready.loc[X.index, 'price_s']
        
        # Filtra apenas anomalias
        anomalies = X[X['anomaly'] == -1].copy()
        
        if anomalies.empty:
            return [{"insight": "Nenhuma anomalia detectada pelo Isolation Forest."}]
        
        # Ordena por score de anomalia (mais anômalo primeiro)
        anomalies = anomalies.sort_values('anomaly_score')
        
        # Pega top 20
        top_anomalies = anomalies.head(20)
        
        for idx, row in top_anomalies.iterrows():
            item = row['main_item']
            price = row['price_s']
            score = row['anomaly_score']
            
            # Determina se é preço alto ou baixo comparando com a média do item
            item_mean = df_ml_ready[df_ml_ready['main_item'] == item]['price_s'].mean()
            
            if price < item_mean:
                tipo = "Anomalia - Preço Baixo"
                desc = f"Detectado como outlier (score: {score:.3f}). Média: {item_mean:.2f}s"
            else:
                tipo = "Anomalia - Preço Alto"
                desc = f"Detectado como outlier (score: {score:.3f}). Média: {item_mean:.2f}s"
            
            insights.append({
                "Item": item,
                "Preço": f"{price:.2f}s",
                "Tipo": tipo,
                "Detalhe": desc,
                "Score": round(abs(score), 3)
            })
        
        return insights

    def run_prediction(self, df_clean: pd.DataFrame) -> list:
        """ 
        Executa o pipeline completo: pré-processamento e previsão.
        Usa Isolation Forest se disponível, senão usa Z-Score.
        """
        df_ml_ready = self.preprocess_for_ml(df_clean)
        
        if self.use_isolation_forest:
            return self.predict_with_isolation_forest(df_ml_ready)
        else:
            return self.predict_opportunities(df_ml_ready)
