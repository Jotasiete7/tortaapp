"""
Wurm Online Trade Analyzer - Statistics Engine
===============================================

Este mÃ³dulo fornece a classe WurmStatsEngine para carregar e analisar
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

# ConfiguraÃ§Ã£o de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WurmStatsEngine:
    """
    Motor de estatÃ­sticas para anÃ¡lise de dados de trade do Wurm Online.
    
    Esta classe carrega dados de arquivos JSON Lines e fornece mÃ©todos
    para anÃ¡lise estatÃ­stica avanÃ§ada usando Pandas DataFrame.
    
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
        
        Suporta InjeÃ§Ã£o de DependÃªncia: pode receber um DataFrame jÃ¡ carregado
        ou um caminho para carregar os dados.
        
        Args:
            data_path: Caminho para o arquivo de dados JSON Lines (opcional se df for fornecido)
            sample_size: NÃºmero de linhas para carregar (None = todas).
            df: DataFrame injetado (opcional). Se fornecido, ignora data_path.
            
        Raises:
            FileNotFoundError: Se o arquivo nÃ£o existir
            ValueError: Se nem data_path nem df forem fornecidos
        """
        self.data_path = Path(data_path) if data_path else None
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.sample_size = sample_size
        
        if df is not None:
            # InjeÃ§Ã£o de dependÃªncia: usa o DataFrame fornecido
            logger.info("Inicializando com DataFrame injetado.")
            self.df = df
            self._generate_metadata()
            logger.info(f"âœ” Dados injetados: {len(self.df):,} registros")
        elif self.data_path:
            # Carregamento padrÃ£o
            if not self.data_path.exists():
                raise FileNotFoundError(f"Arquivo nÃ£o encontrado: {self.data_path}")
            
            if not self.data_path.is_file():
                raise ValueError(f"O caminho nÃ£o Ã© um arquivo: {self.data_path}")
            
            logger.info(f"Iniciando carregamento de {self.data_path.name}...")
            self._load_data()
            self._generate_metadata()
            logger.info(f"âœ” Dados carregados: {len(self.df):,} registros, {len(self.df.columns)} colunas")
        else:
            raise ValueError("Ã‰ necessÃ¡rio fornecer 'data_path' ou 'df' para inicializar o engine.")
    
    def _load_data(self) -> None:
        """
        Carrega os dados usando o wurm_parser com suporte a cache inteligente.
        """
        try:
            import wurm_parser
            logger.info("Usando wurm_parser para carregamento inteligente...")
            
            # Passa o diretÃ³rio pai do arquivo de dados para o parser
            data_dir = self.data_path.parent
            
            self.df = wurm_parser.load_data_and_build_cache(
                str(data_dir), 
                force_rebuild=False,
                sample_size=self.sample_size
            )
            
            if self.df.empty:
                raise ValueError("Nenhum dado retornado pelo parser")
                
            self._setup_index()
            
            logger.info(f"ðŸ“‹ Colunas carregadas: {', '.join(self.df.columns[:10])}...")
            
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar dados: {e}")

    def _setup_index(self) -> None:
        """Configura o Ã­ndice do DataFrame para otimizaÃ§Ã£o."""
        if self.df is None: return
        
        # Garante que temos um Ã­ndice temporal se possÃ­vel
        if 'timestamp' in self.df.columns and not isinstance(self.df.index, pd.DatetimeIndex):
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df.set_index('timestamp', inplace=True)
            self.df.sort_index(inplace=True)

    def _generate_metadata(self) -> None:
        """Gera metadados bÃ¡sicos sobre o dataset."""
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
        """Retorna estatÃ­sticas gerais do dataset."""
        return self.metadata

    def filter_by_item(self, item_name: str, exact: bool = False) -> pd.DataFrame:
        """Retorna DataFrame filtrado por nome do item."""
        if self.df is None: return pd.DataFrame()
        if exact:
            return self.df[self.df['main_item'].str.fullmatch(item_name, case=False, na=False)]
        return self.df[self.df['main_item'].str.contains(item_name, case=False, na=False)]

    def calculate_volatility(self, item_name: str, window: int = 7) -> pd.DataFrame:
        """Calcula a volatilidade (desvio padrÃ£o) do preÃ§o."""
        df_item = self.filter_by_item(item_name)
        if df_item.empty or 'price_s' not in df_item.columns:
            return pd.DataFrame()
        
        # Group by date and take mean price
        daily_price = df_item.groupby('date')['price_s'].mean()
        volatility = daily_price.rolling(window=window).std()
        return volatility.reset_index(name='volatility')

    def calculate_mean_average(self, item_name: str, window: int = 7) -> pd.DataFrame:
        """Calcula a mÃ©dia mÃ³vel do preÃ§o."""
        df_item = self.filter_by_item(item_name)
        if df_item.empty or 'price_s' not in df_item.columns:
            return pd.DataFrame()
            
        daily_price = df_item.groupby('date')['price_s'].mean()
        ma = daily_price.rolling(window=window).mean()
        return ma.reset_index(name='moving_average')

    def calculate_profit_margins(self, item_name: str) -> pd.DataFrame:
        """
        Calcula margens de lucro (WTS - WTB) para um item.
        """
        df_item = self.filter_by_item(item_name, exact=False)
        
        if 'operation' not in df_item.columns or 'price_s' not in df_item.columns or 'date' not in df_item.columns:
            return pd.DataFrame()
            
        # Separate WTS and WTB
        wts = df_item[df_item['operation'] == 'WTS'].groupby('date')['price_s'].min()
        wtb = df_item[df_item['operation'] == 'WTB'].groupby('date')['price_s'].max()
        
        # Merge and calculate spread
        margins = pd.DataFrame({'min_wts': wts, 'max_wtb': wtb})
        margins['spread'] = margins['min_wts'] - margins['max_wtb']
        margins['margin_pct'] = (margins['spread'] / margins['max_wtb']) * 100
        
        return margins.dropna().sort_index()

    def calculate_risk_trends(self, item_name: str, window: int = 7) -> pd.DataFrame:
        """
        Calcula tendÃªncias de risco (Volatilidade + MÃ©dia MÃ³vel).
        """
        # Reuse existing methods but ensure they return compatible DataFrames
        vol = self.calculate_volatility(item_name, window)
        ma = self.calculate_mean_average(item_name, window)
        
        if vol.empty or ma.empty:
            return pd.DataFrame()
            
        # Merge on date
        risk = pd.merge(vol, ma, on='date', how='inner')
        risk['risk_score'] = risk['volatility'] / risk['moving_average']
        
        return risk.set_index('date').sort_index()

    def run_optimized(self) -> str:
        """
        Executa otimizaÃ§Ãµes de memÃ³ria e retorna um resumo.
        """
        if self.df is None: return "Sem dados."
        
        start_mem = self.df.memory_usage(deep=True).sum()
        
        # Downcast numeric columns
        for col in self.df.select_dtypes(include=['float']).columns:
            self.df[col] = pd.to_numeric(self.df[col], downcast='float')
        for col in self.df.select_dtypes(include=['int']).columns:
            self.df[col] = pd.to_numeric(self.df[col], downcast='integer')
            
        # Convert object to category where appropriate
        for col in self.df.select_dtypes(include=['object']).columns:
            if self.df[col].nunique() / len(self.df) < 0.5:
                self.df[col] = self.df[col].astype('category')
                
        end_mem = self.df.memory_usage(deep=True).sum()
        saved = (start_mem - end_mem) / 1024 / 1024
        
        return f"OtimizaÃ§Ã£o concluÃ­da. Economia de {saved:.2f} MB."

if __name__ == "__main__":
    # Teste rÃ¡pido
    try:
        test_file = Path("data/wurm_trade_master_2025_clean.txt")`r`n        if test_file.exists():`r`n            engine = WurmStatsEngine(data_path=test_file, sample_size=1000)
        print(engine.get_stats())
        
        # Teste de novos mÃ©todos
        print("\nTeste de Volatilidade:")
        print(engine.calculate_volatility("iron", window=3).head())
        
    except Exception as e:
        print(f"Erro no teste: {e}")

