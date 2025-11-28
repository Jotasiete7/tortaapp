"""
Patch to implement Z-Score Anomaly Detection and fix price parsing in MLPredictor
"""
import os

def apply_ml_patch():
    file_path = 'ml_predictor.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix parse_wurm_price to handle numeric input (already normalized to copper)
    if 'def parse_wurm_price(price_str):' in content:
        # We replace the method with a robust version
        old_method_sig = 'def parse_wurm_price(price_str):'
        
        new_method = """    @staticmethod
    def parse_wurm_price(price_val):
        \"\"\"
        Converte preço para Iron Coins.
        Aceita string (formato Wurm) ou numérico (Copper).
        \"\"\"
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
"""
        # We need to find the extent of the old method to replace it
        # It ends before 'def format_wurm_price'
        start_idx = content.find(old_method_sig)
        # We need to include the @staticmethod decorator if it was there, but our search string doesn't include it.
        # The file has @staticmethod before it.
        
        real_start_idx = content.rfind('@staticmethod', 0, start_idx)
        
        end_idx = content.find('@staticmethod', start_idx) # Find next static method
        
        if real_start_idx != -1 and end_idx != -1:
            content = content[:real_start_idx] + new_method + "\n" + content[end_idx:]
            print("✓ Fixed parse_wurm_price to handle numeric inputs")
        else:
            print("Could not find method boundaries for parse_wurm_price")

    # 2. Add detect_anomalies method
    if 'def detect_anomalies(self' not in content:
        anomaly_method = """
    def detect_anomalies(self, df_ml_ready: pd.DataFrame) -> list:
        \"\"\"
        Detecta anomalias de preço usando Z-Score.
        \"\"\"
        if df_ml_ready.empty or 'price_iron' not in df_ml_ready.columns:
            return []
            
        # Filtra preços válidos
        df_valid = df_ml_ready[df_ml_ready['price_iron'] > 0].copy()
        if df_valid.empty:
            return []
            
        insights = []
        
        # Agrupa por item
        grouped = df_valid.groupby('main_item')
        
        for item, group in grouped:
            if len(group) < 5: # Precisa de mínimo de dados para média confiável
                continue
                
            mean_price = group['price_iron'].mean()
            std_price = group['price_iron'].std()
            
            if std_price == 0:
                continue
                
            # Analisa as transações mais recentes (assumindo ordenação temporal ou pegando últimas)
            # Se não tiver timestamp, pega todas.
            # Vamos pegar as últimas 3 transações deste item
            recent_txs = group.tail(3)
            
            for idx, row in recent_txs.iterrows():
                price = row['price_iron']
                z_score = (price - mean_price) / std_price
                
                # Threshold de 2 sigmas (95% confiança)
                if abs(z_score) > 1.5: # 1.5 para ser mais sensível
                    
                    tipo = "OPORTUNIDADE (BARATO)" if z_score < 0 else "ALERTA (CARO)"
                    acao = "COMPRAR" if z_score < 0 else "VENDER"
                    
                    # Formata preços
                    price_str = self.format_wurm_price(int(price))
                    mean_str = self.format_wurm_price(int(mean_price))
                    
                    insight = {
                        "Item": item,
                        "Preço": price_str,
                        "Tipo": tipo,
                        "Detalhe": f"{acao}! Preço {abs(z_score):.1f}x sigma longe da média ({mean_str})",
                        "Score": f"Z={z_score:.1f}"
                    }
                    insights.append(insight)
                    
        # Ordena por magnitude do Z-Score (mais anômalo primeiro)
        insights.sort(key=lambda x: abs(float(x['Score'].replace('Z=', ''))), reverse=True)
        return insights
"""
        # Insert before run_prediction
        if 'def run_prediction' in content:
            content = content.replace(
                'def run_prediction',
                anomaly_method + '\n    def run_prediction'
            )
            print("✓ Added detect_anomalies method")

    # 3. Update run_prediction to use detect_anomalies
    # We want to replace the current implementation to call detect_anomalies
    
    new_run_prediction = """    def run_prediction(self, df_clean: pd.DataFrame, analysis_type: str = 'all') -> list:
        \"\"\"Executa o pipeline completo: pré-processamento e previsão.\"\"\"
        df_ml_ready = self.preprocess_for_ml(df_clean)
        
        insights = []
        
        # 1. Anomalias (Z-Score) - Prioridade Alta
        if analysis_type in ['all', 'anomalies']:
            anomalies = self.detect_anomalies(df_ml_ready)
            insights.extend(anomalies)
            
        # 2. Oportunidades Gerais (Lógica antiga)
        if not insights and analysis_type in ['all', 'general']:
            general = self.predict_opportunities(df_ml_ready)
            # Filtra mensagens de erro genéricas se já tivermos anomalias
            if not (len(general) == 1 and "insuficientes" in general[0].get('insight', '')):
                insights.extend(general)
                
        if not insights:
             return [{"insight": "Nenhum insight relevante encontrado."}]
             
        return insights
"""
    
    # Replace run_prediction method
    # Find start
    start_run = content.find('def run_prediction(self, df_clean: pd.DataFrame, analysis_type: str = \'all\') -> list:')
    if start_run != -1:
        # Assuming it's the last method, we replace until end of file or next class
        content = content[:start_run] + new_run_prediction
        print("✓ Updated run_prediction logic")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\n✅ ML Predictor patched successfully!")

if __name__ == '__main__':
    apply_ml_patch()
