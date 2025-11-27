"""
Wurm Online Trade Analyzer - Statistics Engine
===============================================

Este m?dulo fornece a classe WurmStatsEngine para carregar e analisar
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

# Configura??o de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WurmStatsEngine:
    """
    Motor de estat?sticas para an?lise de dados de trade do Wurm Online.
    
    Esta classe carrega dados de arquivos JSON Lines e fornece m?todos
    para an?lise estat?stica avan?ada usando Pandas DataFrame.
    
    Attributes:
        data_path (Path): Caminho para o arquivo de dados
        df (pd.DataFrame): DataFrame principal com os dados de trade
        metadata (dict): Metadados sobre o dataset carregado
    """
    
    def __init__(self, data_path: Union[str, Path], 
                 sample_size: Optional[int] = None):
        """
        Inicializa o WurmStatsEngine e carrega os dados de trade.
        
        Args:
            data_path: Caminho para o arquivo de dados JSON Lines
            sample_size: N?mero de linhas para carregar (None = todas). 
                        ?til para testes com arquivos grandes.
            
        Raises:
            FileNotFoundError: Se o arquivo n?o existir
            ValueError: Se o arquivo estiver vazio ou mal formatado
        """
        self.data_path = Path(data_path)
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.sample_size = sample_size
        
        # Valida??o do arquivo
        if not self.data_path.exists():
            raise FileNotFoundError(f"Arquivo n?o encontrado: {self.data_path}")
        
        if not self.data_path.is_file():
            raise ValueError(f"O caminho n?o ? um arquivo: {self.data_path}")
        
        # Carrega os dados
        logger.info(f"Iniciando carregamento de {self.data_path.name}...")
        self._load_data()
        
        # Gera metadados
        self._generate_metadata()
        
        logger.info(f"? Dados carregados: {len(self.df):,} registros, {len(self.df.columns)} colunas")
    
    def _load_data(self) -> None:
        """
        Carrega os dados do arquivo JSON Lines para um DataFrame.
        
        O arquivo ? esperado no formato JSON Lines (cada linha ? um objeto JSON).
        """
        try:
            # L? o arquivo JSON Lines
            logger.info("Lendo arquivo JSON Lines...")
            
            data_list = []
            with open(self.data_path, 'r', encoding='latin-1') as f:
                for i, line in enumerate(f):
                    if self.sample_size and i >= self.sample_size:
                        break
                    
                    try:
                        data_list.append(json.loads(line.strip()))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Linha {i+1} inv?lida, pulando: {e}")
                        continue
                    
                    # Log de progresso a cada 10k linhas
                    if (i + 1) % 10000 == 0:
                        logger.info(f"Processadas {i+1:,} linhas...")
            
            if not data_list:
                raise ValueError("Nenhum dado v?lido encontrado no arquivo")
            
            # Cria DataFrame
            logger.info(f"Criando DataFrame com {len(data_list):,} registros...")
            self.df = pd.DataFrame(data_list)
            
            # Limpeza inicial: remove linhas completamente vazias
            self.df.dropna(how='all', inplace=True)
            
            # Processa colunas de data
            self._process_dates()
            
            # Processa colunas num?ricas
            self._process_numeric_columns()
            
            # Configura ?ndice otimizado
            self._setup_index()
            
            logger.info(f"?? Colunas carregadas: {', '.join(self.df.columns[:10])}...")
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar dados: {e}")
    
    def _process_dates(self) -> None:
        """
        Processa e converte colunas de data para datetime.
        """
        date_columns = ['timestamp', 'date']
        
        for col in date_columns:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    logger.info(f"?? Coluna '{col}' convertida para datetime")
                except Exception as e:
                    logger.warning(f"Erro ao converter '{col}': {e}")
    
    def _process_numeric_columns(self) -> None:
        """
        Processa e converte colunas num?ricas.
        """
        numeric_columns = ['main_qty', 'main_ql', 'main_dmg', 'main_wt', 'price_s']
        
        for col in numeric_columns:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Erro ao converter '{col}' para num?rico: {e}")
    
    def _setup_index(self) -> None:
        """
        Configura ?ndices otimizados para consultas r?pidas.
        
        Cria um MultiIndex com 'main_item' e 'date' se dispon?veis.
        """
        if 'main_item' in self.df.columns and 'date' in self.df.columns:
            try:
                # Remove valores nulos antes de criar o ?ndice
                valid_data = self.df.dropna(subset=['main_item', 'date'])
                
                if len(valid_data) > 0:
                    # Cria uma c?pia do DataFrame com o novo ?ndice
                    self.df = valid_data.set_index(['main_item', 'date'], drop=False)
                    logger.info(f"?? MultiIndex criado: [main_item, date] ({len(self.df):,} registros)")
                    self.metadata['index_type'] = 'MultiIndex'
                    self.metadata['index_columns'] = ['main_item', 'date']
                else:
                    logger.warning("?? Nenhum registro v?lido para criar ?ndice")
            except Exception as e:
                logger.warning(f"?? N?o foi poss?vel criar MultiIndex: {e}")
        
        # Ordena por data para consultas temporais eficientes
        if 'timestamp' in self.df.columns:
            try:
                self.df.sort_values('timestamp', inplace=True)
                logger.info("?? DataFrame ordenado por timestamp")
            except Exception as e:
                logger.warning(f"Erro ao ordenar por timestamp: {e}")
    
    def _generate_metadata(self) -> None:
        """
        Gera metadados sobre o dataset carregado.
        """
        self.metadata.update({
            'file_path': str(self.data_path),
            'file_size_bytes': self.data_path.stat().st_size,
            'file_size_mb': round(self.data_path.stat().st_size / 1024**2, 2),
            'num_records': len(self.df),
            'num_columns': len(self.df.columns),
            'columns': list(self.df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / 1024**2, 2),
            'loaded_at': datetime.now().isoformat(),
            'sample_size': self.sample_size,
        })
        
        # Adiciona estat?sticas de datas se dispon?vel
        if 'date' in self.df.columns:
            self.metadata['date_range'] = {
                'min': str(self.df['date'].min()),
                'max': str(self.df['date'].max()),
            }
        
        # Adiciona contagem de opera??es
        if 'operation' in self.df.columns:
            self.metadata['operations_count'] = self.df['operation'].value_counts().to_dict()
    
    # ==================== M?todos de An?lise ====================
    
    def get_summary(self) -> pd.DataFrame:
        """
        Retorna um resumo estat?stico do DataFrame.
        
        Returns:
            DataFrame com estat?sticas descritivas
        """
        return self.df.describe(include='all')
    
    def get_info(self) -> str:
        """
        Retorna informa??es sobre o DataFrame.
        
        Returns:
            String com informa??es do DataFrame
        """
        import io
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        return buffer.getvalue()
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Retorna os metadados do dataset.
        
        Returns:
            Dicion?rio com metadados
        """
        return self.metadata.copy()
    
    def filter_by_operation(self, operation: str) -> pd.DataFrame:
        """
        Filtra dados por tipo de opera??o (WTS, WTB, WTT, PC).
        
        Args:
            operation: Tipo de opera??o (ex: 'WTS', 'WTB')
            
        Returns:
            DataFrame filtrado
        """
        if 'operation' not in self.df.columns:
            raise ValueError("Coluna 'operation' n?o encontrada")
        
        return self.df[self.df['operation'] == operation].copy()
    
    def filter_by_item(self, item_name: str, exact: bool = False) -> pd.DataFrame:
        """
        Filtra dados por nome do item.
        
        Args:
            item_name: Nome do item para buscar
            exact: Se True, busca exata. Se False, busca parcial (case-insensitive)
            
        Returns:
            DataFrame filtrado
        """
        if 'main_item' not in self.df.columns:
            raise ValueError("Coluna 'main_item' n?o encontrada")
        
        if exact:
            return self.df[self.df['main_item'] == item_name].copy()
        else:
            mask = self.df['main_item'].str.contains(item_name, case=False, na=False)
            return self.df[mask].copy()
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filtra dados por intervalo de datas.
        
        Args:
            start_date: Data inicial (formato: 'YYYY-MM-DD')
            end_date: Data final (formato: 'YYYY-MM-DD')
            
        Returns:
            DataFrame filtrado
        """
        if 'date' not in self.df.columns:
            raise ValueError("Coluna 'date' n?o encontrada")
        
        mask = (self.df['date'] >= start_date) & (self.df['date'] <= end_date)
        return self.df[mask].copy()
    
    def get_price_statistics(self, item_name: Optional[str] = None) -> pd.DataFrame:
        """
        Retorna estat?sticas de pre?o.
        
        Args:
            item_name: Nome do item (opcional). Se None, retorna para todos os itens.
            
        Returns:
            DataFrame com estat?sticas de pre?o
        """
        if 'price_s' not in self.df.columns:
            raise ValueError("Coluna 'price_s' n?o encontrada")
        
        df_filtered = self.df.copy()
        
        if item_name:
            df_filtered = self.filter_by_item(item_name)
        
        # Remove valores nulos de pre?o
        df_filtered = df_filtered[df_filtered['price_s'].notna()]
        
        if len(df_filtered) == 0:
            return pd.DataFrame()
        
        # FIX: Use column explicitly to avoid ambiguity with index
        if 'main_item' in df_filtered.columns:
             grouper = df_filtered['main_item']
        else:
             grouper = 'main_item'

        stats = df_filtered.groupby(grouper)['price_s'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('min', 'min'),
            ('max', 'max'),
            ('std', 'std')
        ]).round(2)
        
        return stats.sort_values('count', ascending=False)
    
    def get_top_items(self, n: int = 10, operation: Optional[str] = None) -> pd.DataFrame:
        """
        Retorna os itens mais negociados.
        
        Args:
            n: N?mero de itens para retornar
            operation: Filtrar por opera??o (opcional)
            
        Returns:
            DataFrame com top N itens
        """
        df_filtered = self.df.copy()
        
        if operation:
            df_filtered = self.filter_by_operation(operation)
        
        if 'main_item' not in df_filtered.columns:
            raise ValueError("Coluna 'main_item' n?o encontrada")
        
        top_items = df_filtered['main_item'].value_counts().head(n)
        return pd.DataFrame({
            'item': top_items.index,
            'count': top_items.values
        })
    
    def get_player_activity(self, player_name: Optional[str] = None) -> pd.DataFrame:
        """
        Retorna estat?sticas de atividade de jogadores.
        
        Args:
            player_name: Nome do jogador (opcional)
            
        Returns:
            DataFrame com estat?sticas de atividade
        """
        if 'player' not in self.df.columns:
            raise ValueError("Coluna 'player' n?o encontrada")
        
        df_filtered = self.df.copy()
        
        if player_name:
            df_filtered = df_filtered[df_filtered['player'] == player_name]
        
        activity = df_filtered.groupby('player').agg({
            'timestamp': 'count',
            'operation': lambda x: x.value_counts().to_dict()
        }).rename(columns={'timestamp': 'total_trades'})
        
        return activity.sort_values('total_trades', ascending=False)
    
    # ==================== M?todos Utilit?rios ====================
    


    def calculate_volatility(self, item_name: str, window: int = 7) -> pd.DataFrame:
        """
        Calcula a volatilidade de preço de um item.
        
        Args:
            item_name: Nome do item
            window: Janela para cálculo (dias)
            
        Returns:
            DataFrame com volatilidade por data
        """
        df_item = self.filter_by_item(item_name, exact=False)
        
        if 'date' not in df_item.columns or 'price_s' not in df_item.columns:
            raise ValueError("Colunas 'date' ou 'price_s' não encontradas")
        
        # Remove valores nulos
        df_item = df_item[df_item['price_s'].notna()].copy()
        
        if len(df_item) == 0:
            return pd.DataFrame()
        
        # Group by date and get mean price
        daily_prices = df_item.groupby('date')['price_s'].mean().sort_index()
        
        # Calculate rolling standard deviation (volatility)
        volatility = daily_prices.rolling(window=window).std()
        
        result = pd.DataFrame({
            'date': volatility.index,
            'price': daily_prices.values,
            'volatility': volatility.values
        })
        
        return result.dropna()
    
    def calculate_mean_average(self, item_name: str, window: int = 7) -> pd.DataFrame:
        """
        Calcula a média móvel de preço de um item.
        
        Args:
            item_name: Nome do item
            window: Janela para cálculo (dias)
            
        Returns:
            DataFrame com média móvel por data
        """
        df_item = self.filter_by_item(item_name, exact=False)
        
        if 'date' not in df_item.columns or 'price_s' not in df_item.columns:
            raise ValueError("Colunas 'date' ou 'price_s' não encontradas")
        
        # Remove valores nulos
        df_item = df_item[df_item['price_s'].notna()].copy()
        
        if len(df_item) == 0:
            return pd.DataFrame()
        
        # Group by date and get mean price
        daily_prices = df_item.groupby('date')['price_s'].mean().sort_index()
        
        # Calculate rolling mean
        moving_avg = daily_prices.rolling(window=window).mean()
        
        result = pd.DataFrame({
            'date': moving_avg.index,
            'price': daily_prices.values,
            'moving_average': moving_avg.values
        })
        
        return result.dropna()

    def otimizar_dataframe(self) -> None:
        """
        Otimiza o DataFrame para reduzir uso de memória.
        Converte strings para category e define índice otimizado.
        """
        logger.info("Otimizando DataFrame...")
        
        # Convert string columns to category
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                num_unique = self.df[col].nunique()
                num_total = len(self.df[col])
                
                # Only convert if cardinality is low enough
                if num_unique / num_total < 0.5:
                    self.df[col] = self.df[col].astype('category')
                    logger.info(f"Converted '{col}' to category")
        
        # Set optimized multi-index if possible
        if 'date' in self.df.columns and 'main_item' in self.df.columns:
            valid_data = self.df.dropna(subset=['date', 'main_item'])
            if len(valid_data) > 0:
                self.df = valid_data.set_index(['date', 'main_item'], drop=False).sort_index()
                logger.info("Set multi-index on [date, main_item]")
        
        memory_after = round(self.df.memory_usage(deep=True).sum() / 1024**2, 2)
        logger.info(f"Optimization complete. Memory usage: {memory_after}MB")

    def __repr__(self) -> str:
        """Representa??o string do objeto."""
        return (f"WurmStatsEngine(records={len(self.df):,}, "
                f"columns={len(self.df.columns)}, "
                f"file='{self.data_path.name}')")
    
    def __str__(self) -> str:
        """String amig?vel do objeto."""
        return f"Wurm Stats Engine: {len(self.df):,} registros de '{self.data_path.name}'"
    
    def __len__(self) -> int:
        """Retorna o n?mero de registros."""
        return len(self.df)


# ==================== Exemplo de Uso ====================


    def calculate_profit_margins(self, item_name: str) -> pd.DataFrame:
        """
        Calcula margens de lucro (WTS - WTB) para um item.
        Vectorized implementation.
        
        Args:
            item_name: Nome do item
            
        Returns:
            DataFrame com margens por data
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
        Calcula tendências de risco (Volatilidade + Média Móvel).
        Vectorized implementation.
        
        Args:
            item_name: Nome do item
            window: Janela de dias
            
        Returns:
            DataFrame com métricas de risco
        """
        # Reuse existing methods but ensure they return compatible DataFrames
        vol = self.calculate_volatility(item_name, window)
        ma = self.calculate_mean_average(item_name, window)
        
        if vol.empty or ma.empty:
            return pd.DataFrame()
            
        # Merge on date
        risk = pd.merge(vol[['date', 'volatility']], ma[['date', 'moving_average']], on='date', how='inner')
        risk['risk_score'] = risk['volatility'] / risk['moving_average']
        
        return risk.set_index('date').sort_index()


if __name__ == "__main__":
    print("=" * 70)
    print("Wurm Online Trade Analyzer - Statistics Engine")
    print("=" * 70)
    print("\n?? Exemplo de uso:\n")
    
    example_code = """
    # 1. Carregar dados (amostra de 1000 linhas para teste)
    engine = WurmStatsEngine('wurm_trade_master_2025_clean.txt', sample_size=1000)
    
    # 2. Ver informa??es b?sicas
    print(engine)
    print(f"Total de registros: {len(engine):,}")
    
    # 3. Ver metadados
    metadata = engine.get_metadata()
    print(f"Per?odo: {metadata['date_range']['min']} a {metadata['date_range']['max']}")
    
    # 4. Filtrar por opera??o
    wts_data = engine.filter_by_operation('WTS')
    print(f"Vendas (WTS): {len(wts_data):,} registros")
    
    # 5. Buscar item espec?fico
    rare_items = engine.filter_by_item('rare', exact=False)
    print(f"Itens raros: {len(rare_items):,} registros")
    
    # 6. Estat?sticas de pre?o
    price_stats = engine.get_price_statistics()
    print(price_stats.head())
    
    # 7. Top 10 itens mais negociados
    top_items = engine.get_top_items(n=10)
    print(top_items)
    
    # 8. Acessar DataFrame diretamente para an?lises customizadas
    df = engine.df
    # Agora voc? pode usar todo o poder do Pandas!
    """
    
    print(example_code)
    print("\n" + "=" * 70)
    print("? M?dulo pronto para uso!")
    print("=" * 70)
