"""
charts_engine.py
Módulo responsável pela geração de gráficos usando Matplotlib
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)


class ChartsEngine:
    """Motor de geração de gráficos para análise de dados de trade."""
    
    def __init__(self):
        """Inicializa o motor de gráficos."""
        self.current_figure = None
        self.current_canvas = None
        
    def create_price_trend_chart(self, df: pd.DataFrame, item_name: str, 
                                  parent_frame=None) -> Figure:
        """
        Cria um gráfico de tendência de preço para um item específico.
        
        Args:
            df: DataFrame com os dados de trade
            item_name: Nome do item para filtrar
            parent_frame: Frame Tkinter para embedding (opcional)
            
        Returns:
            Figure do Matplotlib
        """
        try:
            # Reset index to avoid ambiguity with date
            df = df.reset_index(drop=True)
            
            # Filtra dados do item
            if 'main_item' not in df.columns:
                raise ValueError("Coluna 'main_item' não encontrada")
                
            item_df = df[df['main_item'].str.contains(item_name, case=False, na=False)].copy()
            
            if item_df.empty:
                raise ValueError(f"Nenhum dado encontrado para '{item_name}'")
            
            # Garante que temos colunas necessárias
            if 'date' not in item_df.columns or 'price_s' not in item_df.columns:
                raise ValueError("Colunas 'date' ou 'price_s' não encontradas")
            
            # Remove valores nulos
            item_df = item_df.dropna(subset=['date', 'price_s'])
            
            if item_df.empty:
                raise ValueError(f"Dados insuficientes para '{item_name}'")
            
            # Agrupa por data e calcula média de preço
            daily_avg = item_df.groupby('date')['price_s'].agg(['mean', 'count']).reset_index()
            daily_avg = daily_avg.sort_values('date')
            
            # Calcula média geral para linha de base
            overall_mean = daily_avg['mean'].mean()
            
            # Calcula limites do eixo Y com margem de 5%
            price_min = daily_avg['mean'].min()
            price_max = daily_avg['mean'].max()
            price_range = price_max - price_min
            margin = price_range * 0.05 if price_range > 0 else price_max * 0.1
            y_min = max(0, price_min - margin)  # Não deixa negativo
            y_max = price_max + margin
            
            # Cria figura
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            # Plot linha de tendência com marcadores mais evidentes
            ax.plot(daily_avg['date'], daily_avg['mean'], 
                   marker='o', linestyle='-', linewidth=2.5, markersize=8,
                   color='#2E86AB', label='Preço Médio Diário', 
                   markerfacecolor='#2E86AB', markeredgecolor='white', markeredgewidth=1.5)
            
            # Linha de base (média geral)
            ax.axhline(y=overall_mean, color='#E63946', linestyle='--', 
                      linewidth=2, alpha=0.7, label=f'Média Geral ({overall_mean:.2f}s)')
            
            # Configurações visuais
            ax.set_xlabel('Data', fontsize=11, fontweight='bold')
            ax.set_ylabel('Preço (silver)', fontsize=11, fontweight='bold')
            ax.set_title(f'Tendência de Preço: {item_name}', 
                        fontsize=13, fontweight='bold', pad=15)
            
            # Define limites do eixo Y (zoom focado)
            ax.set_ylim(y_min, y_max)
            
            # Grid mais sutil
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
            ax.legend(loc='best', framealpha=0.95, fontsize=9)
            
            # Rotaciona labels do eixo X
            fig.autofmt_xdate()
            
            # Ajusta layout
            fig.tight_layout()
            
            self.current_figure = fig
            
            logger.info(f"Gráfico criado para '{item_name}' com {len(daily_avg)} pontos")
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico: {e}")
            raise
    
    def create_volume_chart(self, df: pd.DataFrame, item_name: str) -> Figure:
        """
        Cria um gráfico de volume de transações.
        
        Args:
            df: DataFrame com os dados de trade
            item_name: Nome do item para filtrar
            
        Returns:
            Figure do Matplotlib
        """
        try:
            # Reset index to avoid ambiguity
            df = df.reset_index(drop=True)
            
            # Filtra dados do item
            item_df = df[df['main_item'].str.contains(item_name, case=False, na=False)].copy()
            
            if item_df.empty:
                raise ValueError(f"Nenhum dado encontrado para '{item_name}'")
            
            # Agrupa por data e conta transações
            daily_volume = item_df.groupby('date').size().reset_index(name='volume')
            daily_volume = daily_volume.sort_values('date')
            
            # Cria figura
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            # Plot barras
            ax.bar(daily_volume['date'], daily_volume['volume'], 
                  color='#A23B72', alpha=0.7, label='Volume de Transações')
            
            # Configurações visuais
            ax.set_xlabel('Data', fontsize=11, fontweight='bold')
            ax.set_ylabel('Número de Transações', fontsize=11, fontweight='bold')
            ax.set_title(f'Volume de Atividade: {item_name}', 
                        fontsize=13, fontweight='bold', pad=15)
            ax.grid(True, alpha=0.3, linestyle='--', axis='y')
            ax.legend(loc='best', framealpha=0.9)
            
            # Rotaciona labels
            fig.autofmt_xdate()
            
            # Ajusta layout
            fig.tight_layout()
            
            self.current_figure = fig
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de volume: {e}")
            raise
    
    def save_chart(self, filepath: str, dpi: int = 150):
        """
        Salva o gráfico atual em arquivo.
        
        Args:
            filepath: Caminho do arquivo (PNG, PDF, SVG suportados)
            dpi: Resolução (dots per inch)
        """
        if self.current_figure is None:
            raise ValueError("Nenhum gráfico para salvar")
        
        try:
            self.current_figure.savefig(filepath, dpi=dpi, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar gráfico: {e}")
            raise
    
    def clear(self):
        """Limpa o gráfico atual."""
        if self.current_figure:
            plt.close(self.current_figure)
            self.current_figure = None
            self.current_canvas = None
