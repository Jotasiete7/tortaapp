# tests/test_ml_predictor.py
"""
Testes unitários para MLPredictor
"""

import pytest
import pandas as pd
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_predictor import MLPredictor


@pytest.fixture
def sample_dataframe():
    """Cria um DataFrame de teste."""
    prices = [50, 52, 51, 53, 200, 49, 50, 51, 52, 50,  # iron (1 outlier)
              100, 102, 101, 103, 99, 100, 101, 102, 300, 100]  # silver (1 outlier)
    
    data = {
        'main_item': ['iron lump'] * 10 + ['silver lump'] * 10,
        'price_s': prices,
        'price_iron': [p * 100 for p in prices], # Added price_iron
        'date': pd.date_range('2025-01-01', periods=20)
    }
    return pd.DataFrame(data)


def test_predictor_initialization():
    """Testa inicialização do preditor."""
    predictor = MLPredictor()
    assert predictor is not None


def test_preprocess_for_ml(sample_dataframe):
    """Testa pré-processamento."""
    predictor = MLPredictor()
    processed = predictor.preprocess_for_ml(sample_dataframe)
    
    assert not processed.empty
    assert 'price_iron' in processed.columns # Changed from price_s check (or added)
    assert 'main_item' in processed.columns


def test_predict_opportunities_zscore(sample_dataframe):
    """Testa predição com Z-Score."""
    predictor = MLPredictor() # Removed use_isolation_forest arg if it was there, or kept it default
    results = predictor.run_prediction(sample_dataframe)
    
    assert isinstance(results, list)
    assert len(results) > 0
    # Check if insight contains "Copper"
    assert "Copper" in results[0]['Preço Anômalo (WTS)']


def test_empty_dataframe():
    """Testa com DataFrame vazio."""
    predictor = MLPredictor()
    empty_df = pd.DataFrame()
    
    results = predictor.run_prediction(empty_df)
    assert isinstance(results, list)
    assert len(results) == 1
    assert 'insight' in results[0]


def test_insufficient_data():
    """Testa com dados insuficientes."""
    predictor = MLPredictor()
    small_df = pd.DataFrame({
        'main_item': ['iron'] * 3,
        'price_s': [50, 51, 52],
        'price_iron': [5000, 5100, 5200]
    })
    
    results = predictor.run_prediction(small_df)
    assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
