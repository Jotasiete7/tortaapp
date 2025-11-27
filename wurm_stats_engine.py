"""
Wurm Online Trade Analyzer - Statistics Engine
===============================================

Este módulo fornece a classe WurmStatsEngine para carregar e analisar
dados de trade do Wurm Online usando Pandas.

Autor: Senior Python Engineer
Data: 2025-11-26
"""

import pandas as pd
import json
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WurmStatsEngine:
    """
    Motor de estatísticas para análise de dados de trade do Wurm Online.
    
    Esta classe carrega dados de arquivos JSON Lines e fornece métodos
    para análise estatística avançada usando Pandas DataFrame.
    
    Attributes:
        data_path (Path): Caminho para o arquivo de dados
        df (pd.DataFrame): DataFrame principal com os dados de trade
        metadata (dict): Metadados sobre o dataset carregado
    """
    
    def __init__(self, data_path: Optional[Union[str, Path]] = None, 
                 sample_size: Optional[int] = None,
                 df: Optional[pd.DataFrame] = None) -> None:
        """
        Inicializa o WurmStatsEngine.
        
        Suporta Injeção de Dependência: pode receber um DataFrame já carregado
        ou um caminho para carregar os dados.
        
        Args:
            data_path: Caminho para o arquivo de dados JSON Lines (opcional se df for fornecido)
            sample_size: Número de linhas para carregar (None = todas).
            df: DataFrame injetado (opcional). Se fornecido, ignora data_path.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se nem data_path nem df forem fornecidos
        """
        self.data_path = Path(data_path) if data_path else None
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.sample_size = sample_size
        
        if df is not None:
            # Injeção de dependência: usa o DataFrame fornecido
            logger.info("Inicializando com DataFrame injetado.")
            self.df = df
            self._generate_metadata()
            logger.info(f"✔ Dados injetados: {len(self.df):,} registros")
        elif self.data_path:
            # Carregamento padrão
            if not self.data_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {self.data_path}")
            
            if not self.data_path.is_file():
                raise ValueError(f"O caminho não é um arquivo: {self.data_path}")
            
            logger.info(f"Iniciando carregamento de {self.data_path.name}...")
            self._load_data()
            self._generate_metadata()
            logger.info(f"✔ Dados carregados: {len(self.df):,} registros, {len(self.df.columns)} colunas")
        else:
            raise ValueError("É necessário fornecer 'data_path' ou 'df' para inicializar o engine.")
    
    def _load_data(self) -> None:
        """
        Carrega os dados usando o wurm_parser com suporte a cache inteligente.
        """
        try:
            import wurm_parser
            logger.info("Usando wurm_parser para carregamento inteligente...")
            
            # Passa o diretório pai do arquivo de dados para o parser
            data_dir = self.data_path.parent
            
            self.df = wurm_parser.load_data_and_build_cache(
                str(data_dir), 
                force_rebuild=False,
                sample_size=self.sample_size
            )
            
            if self.df.empty:
                raise ValueError("Nenhum dado retornado pelo parser")
                
            self._setup_index()
            
            logger.info(f"📋 Colunas carregadas: {', '.join(self.df.columns[:10])}...")
            
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar dados: {e}")

    def _setup_index(self) -> None:
        """Configura o índice do DataFrame para otimização."""
        if self.df is None: return
        
        # Garante que temos um índice temporal se possível
        if 'timestamp' in self.df.columns and not isinstance(self.df.index, pd.DatetimeIndex):
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df.set_index('timestamp', inplace=True)
            self.df.sort_index(inplace=True)

    def _generate_metadata(self) -> None:
        """Gera metadados básicos sobre o dataset."""
        if self.df is None: return
        
        self.metadata = {
            'total_records': len(self.df),
            'columns': list(self.df.columns),
            'memory_usage': self.df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
            'date_range': (
                self.df.index.min().isoformat() if not self.df.empty and isinstance(self.df.index, pd.DatetimeIndex) else None,
                self.df.index.max().isoformat() if not self.df.empty and isinstance(self.df.index, pd.DatetimeIndex) else None
            )
        }

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do dataset."""
        return self.metadata

    def filter_by_item(self, item_name: str) -> pd.DataFrame:
        """Retorna DataFrame filtrado por nome do item."""
        if self.df is None: return pd.DataFrame()
        return self.df[self.df['main_item'].str.contains(item_name, case=False, na=False)]
