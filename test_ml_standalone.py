import pandas as pd
import numpy as np
from ml_predictor import MLPredictor

def test_ml_logic():
    print("=== Testando ML Predictor (Standalone) ===")
    
    # 1. Criar dados de exemplo
    # Vamos criar um item 'Iron Ore' com preços normais e alguns outliers
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'main_item': ['Iron Ore'] * n_samples,
        'price_s': np.random.normal(loc=10.0, scale=1.0, size=n_samples), # Média 10, Desvio 1
        'date': pd.date_range(start='2025-01-01', periods=n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Adicionar anomalias manuais
    # Preço muito alto (Venda)
    df.loc[95, 'price_s'] = 15.0 # +5 sigma
    # Preço muito baixo (Compra)
    df.loc[96, 'price_s'] = 5.0  # -5 sigma
    
    print(f"Dados gerados: {len(df)} registros.")
    print(f"Média esperada: ~10.0. Desvio esperado: ~1.0")
    
    # 2. Inicializar Predictor
    predictor = MLPredictor()
    
    # 3. Rodar Previsão
    print("\nExecutando análise...")
    insights = predictor.run_prediction(df)
    
    # 4. Verificar Resultados
    print("\n=== Insights Gerados ===")
    for i in insights:
        print(i)
        
    # Validação simples
    has_high = any("Preço Alto" in i.get('Tipo', '') for i in insights)
    has_low = any("Preço Baixo" in i.get('Tipo', '') for i in insights)
    
    if has_high and has_low:
        print("\nSUCESSO: Anomalias de alta e baixa detectadas corretamente.")
    else:
        print("\nFALHA: Algumas anomalias não foram detectadas.")

if __name__ == "__main__":
    test_ml_logic()
