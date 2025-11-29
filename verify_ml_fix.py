import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from ml_predictor import MLPredictor
    from wurm_parser import parse_wurm_price, format_wurm_price
except ImportError:
    print(f"Current CWD: {os.getcwd()}")
    print("Files in CWD:", os.listdir())
    raise

def test_ml_predictor():
    print("Testing MLPredictor Refactor (Tail Fix)...")
    ml = MLPredictor()
    print("MLPredictor initialized.")
    
    # Test parse_wurm_price (now in wurm_parser)
    p1 = parse_wurm_price("1g 50s")
    print(f"1g 50s -> {p1}")
    assert p1 == 1500000, f"Expected 1500000, got {p1}"
    
    # Test format_wurm_price
    f1 = format_wurm_price(1500000)
    print(f"1500000 -> {f1}")
    assert f1 == "1g 50s", f"Expected '1g 50s', got '{f1}'"
    
    # Test detect_anomalies (mock data)
    # Using 'main_item' and testing Top N behavior
    
    items = [f'Item{i}' for i in range(60)]
    # Make Item0 very frequent (Top 1)
    data_items = ['Item0'] * 100
    # Add others less frequently
    for i in range(1, 60):
        data_items.extend([f'Item{i}'] * 2) # 2 occurrences each
        
    # Create DataFrame
    data = {
        'main_item': data_items,
        'price_iron': [10000] * len(data_items),
        'Timestamp': pd.to_datetime(['2023-01-01']*len(data_items))
    }
    df = pd.DataFrame(data)
    
    # Inject anomaly for Item0 (Top 1)
    # IMPORTANT: Must be at the END of Item0's data because logic uses tail(3)
    # Item0 is at indices 0 to 99.
    df.loc[99, 'price_iron'] = 50000 # Anomaly at the end of Item0 block
    
    # Preprocess
    print("Preprocessing...")
    df_ml = ml.preprocess_for_ml(df)
    
    print("Columns after preprocess (sample):", df_ml.columns.tolist()[:10])
    print(f"Total columns: {len(df_ml.columns)}")
    
    # Verify column count (should be around 50 + features, not 60+)
    # 50 top items + Other + price_iron + hour + dayofweek = ~54
    assert len(df_ml.columns) < 60, f"Too many columns! Top N encoding failed. Got {len(df_ml.columns)}"
    
    # Ensure Item0 is encoded (it's frequent)
    assert 'item_encoded_Item0' in df_ml.columns, "item_encoded_Item0 missing (should be in Top N)"
    
    print("Detecting anomalies...")
    insights = ml.detect_anomalies(df_ml)
    print("Insights:", insights)
    
    assert len(insights) > 0, "No insights found!"
    assert insights[0]['Item'] == 'Item0', f"Expected Item0, got {insights[0]['Item']}"
    assert "mediana" in insights[0]['Detalhe'].lower(), "Insight detail should mention median"
    
    # NEW TEST: Test empty return
    print("Testing empty return...")
    # Create data with no anomalies (all prices same)
    data_clean = {
        'main_item': ['ItemA'] * 10,
        'price_iron': [10000] * 10,
        'Timestamp': pd.to_datetime(['2023-01-01']*10)
    }
    df_clean = pd.DataFrame(data_clean)
    
    # Run prediction via run_prediction to test the fallback logic
    insights_clean = ml.run_prediction(df_clean)
    print("Clean Insights:", insights_clean)
    
    assert isinstance(insights_clean, list), "Should return a list"
    assert len(insights_clean) == 0, f"Should return empty list for no anomalies, got {insights_clean}"
    
    print("detect_anomalies passed.")
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_ml_predictor()
