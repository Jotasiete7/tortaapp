# tests/test_wurm_stats_engine.py
"""
Testes unitários para WurmStatsEngine
"""

import pytest
import pandas as pd
import tempfile
import json
import os
from pathlib import Path

# Assume que wurm_stats_engine está no diretório pai
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from wurm_stats_engine import WurmStatsEngine


@pytest.fixture
def sample_data_file():
    """Cria um arquivo temporário com dados de teste."""
    data = [
        {"timestamp": "2025-01-01 10:00:00", "date": "2025-01-01", "main_item": "iron lump", "price_s": 50, "operation": "WTS"},
        {"timestamp": "2025-01-01 11:00:00", "date": "2025-01-01", "main_item": "iron lump", "price_s": 55, "operation": "WTB"},
        {"timestamp": "2025-01-02 10:00:00", "date": "2025-01-02", "main_item": "silver lump", "price_s": 100, "operation": "WTS"},
        {"timestamp": "2025-01-02 11:00:00", "date": "2025-01-02", "main_item": "silver lump", "price_s": 105, "operation": "WTB"},
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for record in data:
            f.write(json.dumps(record) + '\n')
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


def test_engine_initialization(sample_data_file):
    """Testa inicialização do engine."""
    engine = WurmStatsEngine(sample_data_file)
    assert engine is not None
    assert len(engine.df) > 0


def test_filter_by_item(sample_data_file):
    """Testa filtragem por item."""
    engine = WurmStatsEngine(sample_data_file)
    
    iron_data = engine.filter_by_item("iron lump", exact=True)
    assert len(iron_data) == 2
    assert all(iron_data['main_item'] == 'iron lump')


def test_filter_by_operation(sample_data_file):
    """Testa filtragem por operação."""
    engine = WurmStatsEngine(sample_data_file)
    
    wts_data = engine.filter_by_operation("WTS")
    assert len(wts_data) == 2
    assert all(wts_data['operation'] == 'WTS')


def test_get_price_statistics(sample_data_file):
    """Testa estatísticas de preço."""
    engine = WurmStatsEngine(sample_data_file)
    
    stats = engine.get_price_statistics()
    assert not stats.empty
    assert 'mean' in stats.columns
    assert 'count' in stats.columns


def test_empty_filter(sample_data_file):
    """Testa filtro que não retorna resultados."""
    engine = WurmStatsEngine(sample_data_file)
    
    result = engine.filter_by_item("nonexistent item", exact=True)
    assert result.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
