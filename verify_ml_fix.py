import pandas as pd
import sys
import os

# Add current directory to path to ensure we can import ml_predictor
sys.path.append(os.getcwd())

try:
    from ml_predictor import MLPredictor
except ImportError:
    # Try to find where we are
    print(f"Current CWD: {os.getcwd()}")
    print("Files in CWD:", os.listdir())
    raise

def test_ml_predictor():
    print("Testing MLPredictor...")
    ml = MLPredictor()
    print("MLPredictor initialized.")
    
    # Test parse_wurm_price
    p1 = ml.parse_wurm_price("1g 50s")
    print(f"1g 50s -> {p1}")
    assert p1 == 1500000, f"Expected 1500000, got {p1}"
    
    p2 = ml.parse_wurm_price(100)
    print(f"100 -> {p2}")
    assert p2 == 10000, f"Expected 10000, got {p2}" # 100 copper = 10000 iron
    print("parse_wurm_price passed.")
    
    # Test format_wurm_price
    f1 = ml.format_wurm_price(1500000)
    print(f"1500000 -> {f1}")
    assert f1 == "1g 50s", f"Expected '1g 50s', got '{f1}'"
    print("format_wurm_price passed.")
    
    # Test detect_anomalies (mock data)
    # We need enough data points for Z-score (min 5 in code)
    data = {
        'Item Name': ['ItemA'] * 10,
        'Price WTS': [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 50000], # Last one is anomaly (5x mean)
        'Timestamp': pd.to_datetime(['2023-01-01']*10)
    }
    df = pd.DataFrame(data)
    
    # Preprocess
    print("Preprocessing...")
    df_ml = ml.preprocess_for_ml(df)
    
    print("Columns after preprocess:", df_ml.columns.tolist())
    
    print("Detecting anomalies...")
    insights = ml.detect_anomalies(df_ml)
    print("Insights:", insights)
    
    if not insights:
        print("No insights found. Debugging...")
        # Check if Price WTS is in df_ml
        if 'Price WTS' not in df_ml.columns:
            print("'Price WTS' missing from df_ml")
        
        # Check item columns
        item_cols = [c for c in df_ml.columns if c.startswith('item_')]
        print(f"Item columns: {item_cols}")
        
    assert len(insights) > 0, "No insights found!"
    assert insights[0]['Item'] == 'ItemA', f"Expected ItemA, got {insights[0]['Item']}"
    print("detect_anomalies passed.")
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_ml_predictor()
