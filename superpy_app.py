"""
SuperPy GUI (Tkinter) — minimal-retro modern

This is a single-file starter app for your SuperPy windowed tool.
It:
- extracts a provided ZIP of your scripts/data (default path set to the uploaded file)
- loads trade data lines into memory (lazy/indexed)
- provides a left panel with icons + text menu (Buscar, Avançado, Estatísticas, Gráficos, Plugins, Configs)
- implements an advanced search UI with "contains" and "not contains" and exact/fuzzy options
- includes a simple plugin loader that scans ./plugins for .py files and lists them in the UI
- keeps everything non-blocking (threaded loads) and ready to be extended

How to use (short):
- Put your plugins (if any) into a folder named "plugins" next to this file. Each plugin should
  define a function `run(data, params)` and optional `DESCRIPTION` string.
- By default this file expects the uploaded ZIP at: /mnt/data/python trade.zip
  (constant TRADE_ZIP_PATH). You can change that path or configure in the UI.
- Run: python superpy_app.py

Notes:
- This starter focuses on the GUI and integration points. Replace placeholder logic in
  load_trade_lines() and chart generation with your real parsers or adapted code from your
  existing scripts.

"""

import os
import threading
import zipfile
import tempfile
import shutil
import importlib.util
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import time
import sys
import subprocess
from wurm_stats_engine import WurmStatsEngine
from ml_predictor import MLPredictor
from threading_utils import AsyncDataLoader
import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd


# ------------------------------
# Configuration / Defaults
# ------------------------------
# Path to the ZIP you uploaded. Keep as-is if you want the GUI to try to extract it automatically.
TRADE_ZIP_PATH = r"wurm_trade_master_2025_clean.txt"
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")

# UI styling values (minimal-retro modern)
BG = "#1a1a1a"
PANEL_BG = "#2b2b2b"
ACCENT = "#1f6aa5"
TEXT = "#ffffff"
BUTTON_RADIUS = 4
FONT = ("Segoe UI", 10)
ICON_FONT = ("Segoe UI", 12)

# ------------------------------
# Utilities: data extraction + loading
# ------------------------------

def ensure_data_extracted(zip_path=TRADE_ZIP_PATH, extract_to=DEFAULT_DATA_DIR):
    """Extract zip file to extract_to if extract_to not exists. Return path where files are.
    If zip_path is not zip or not present, returns extract_to if it exists, else None.
    """
    if os.path.isdir(extract_to) and any(os.scandir(extract_to)):
        return extract_to

    if not os.path.exists(zip_path):
        return None

    if zipfile.is_zipfile(zip_path):
        try:
            os.makedirs(extract_to, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(extract_to)
            return extract_to
        except Exception as e:
            print("Error extracting zip:", e)
            return None
    else:
        # If the provided path is a folder containing files, return it
        if os.path.isdir(zip_path):
            return zip_path
        return None


class TradeData:
    """Simple container for loaded trade lines and index.
    Replace parsing logic with your project's parser for better performance.
    """
    def __init__(self):
        self.lines = []
        self.index_built = False
        self.loaded_path = None

    def load_from_dir(self, data_dir):
        """Load textual trade data from data_dir. Finds .txt files and loads lines.
        This is intentionally simple and conservative — adapt it to your file format.
        """
        self.lines = []
        self.loaded_path = data_dir
        files = []
        for root, _, filenames in os.walk(data_dir):
            for fn in filenames:
                if fn.lower().endswith('.txt') or fn.lower().endswith('.csv'):
                    files.append(os.path.join(root, fn))
        for f in files:
            try:
                with open(f, 'r', encoding='latin-1', errors='replace') as fh:
                    for ln in fh:
                        s = ln.strip()
                        if s:
                            self.lines.append(s)
            except Exception as e:
                print('Error reading', f, e)
        self.index_built = True

    def simple_search(self, text):
        q = text.strip().lower()
        if not q:
            return []
        return [l for l in self.lines if q in l.lower()]

    def advanced_search(self, must_text, not_text, exact=False, case_sensitive=False, fuzzy=False):
        """must_text: string with space-separated mandatory tokens
           not_text: string with space-separated forbidden tokens
           exact: if True, match exact phrase
        """
        must_tokens = [t for t in must_text.strip().split() if t] if must_text else []
        not_tokens = [t for t in not_text.strip().split() if t] if not_text else []

        results = []
        for line in self.lines:
            hay = line if case_sensitive else line.lower()

            if exact:
                target = must_text if case_sensitive else must_text.lower()
                if target not in hay:
                    continue
            else:
                ok = True
                for tk in must_tokens:
                    tks = tk if case_sensitive else tk.lower()
                    if tks not in hay:
                        ok = False
                        break
                if not ok:
                    continue

            bad = False
            for nk in not_tokens:
                nks = nk if case_sensitive else nk.lower()
                if nks in hay:
                    bad = True
                    break
            if bad:
                continue

            # TODO: add fuzzy matching if requested (Levenshtein or difflib)
            results.append(line)
        return results


# ------------------------------
# Plugin system
# ------------------------------

def discover_plugins(directory=PLUGINS_DIR):
    """Look for .py files in plugins dir, return dict name -> metadata and path"""
    plugins = {}
    if not os.path.isdir(directory):
        return plugins
    for fn in os.listdir(directory):
        if not fn.lower().endswith('.py'):
            continue
        path = os.path.join(directory, fn)
        plugins[fn] = {'path': path}
    return plugins


def load_plugin(path):
    """Dynamically load a plugin module from a file path.
    The plugin is expected to provide:
      - run(data, params) -> returns printable result (string or list)
      - optional DESCRIPTION string
    """
    name = Path(path).stem
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print('Error loading plugin', path, e)
        return None


# ------------------------------
# GUI
# ------------------------------

class SuperPyGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.async_loader = AsyncDataLoader()
        self.title('SuperPy — Wurm Trade Analyzer')
        self.geometry('1000x650')
        self.config(bg=BG)

        # data
        self.engine = None
        self.ml_predictor = MLPredictor()
        self.plugins_meta = {}
        self.plugins_modules = {}

        # building UI
        self._build_ui()

        # start background loading of data if possible
        self.after(200, self._background_load)

    def _build_ui(self):
        # main frames
        self.left_panel = tk.Frame(self, width=180, bg=PANEL_BG)
        self.left_panel.pack(side='left', fill='y')

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side='left', fill='both', expand=True)

        self.statusbar = tk.Label(self, text='Status: idle', anchor='w', bg='#EFEFEF')
        self.statusbar.pack(side='bottom', fill='x')

        # left menu with icons + text
        self.menu_buttons = {}
        menu = [
            ('🔍', 'Buscar', self.show_search),
            ('🧭', 'Avançado', self.show_advanced),
            ('📊', 'Estatísticas', self.show_stats),
            ('📈', 'Gráficos', self.show_charts),
            ('🔮', 'Insights', self.show_insights),
            ('🧩', 'Plugins', self.show_plugins),
            ('⚙️', 'Config', self.show_config),
            ('❓', 'Ajuda', self.show_help),
        ]
        for icon, text, cmd in menu:
            btn = tk.Button(self.left_panel, text=f"{icon}  {text}", anchor='w', width=20,
                            relief='flat', bg=PANEL_BG, font=FONT, command=cmd)
            btn.pack(pady=6, padx=8)
            self.menu_buttons[text] = btn

        # dynamic content frames
        self.frames = {}
        for name in ['search', 'advanced', 'stats', 'charts', 'insights', 'plugins', 'config', 'help']:
            f = tk.Frame(self.content, bg=BG)
            self.frames[name] = f

        self._build_search_frame()
        self._build_advanced_frame()
        self._build_stats_frame()
        self._build_charts_frame()
        self._build_insights_frame()
        self._build_plugins_frame()
        self._build_config_frame()
        self._build_help_frame()

        # start on search
        self.show_search()

    def set_status(self, text):
        self.statusbar.config(text=text)
    def log_message(self, message, is_error=False):
        """Log message to console and status bar"""
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {'ERROR' if is_error else 'INFO'}: {message}"
        
        # Update status bar
        self.set_status(message)
        
        # Write to log console if available
        if hasattr(self, 'log_console'):
            self.log_console.insert(tk.END, log_entry + '\n')
            self.log_console.see(tk.END)
            
            # Color code errors
            if is_error:
                start_idx = self.log_console.index("end-2l")
                end_idx = self.log_console.index("end-1l")
                self.log_console.tag_add("error", start_idx, end_idx)
                self.log_console.tag_config("error", foreground="red")


    # ------------------ build each view ------------------
    def _build_search_frame(self):
        f = self.frames['search']
        f.pack(fill='both', expand=True)

        top = tk.Frame(f, bg=BG)
        top.pack(fill='x', pady=8)

        tk.Label(top, text='Item:', bg=BG, font=FONT).pack(side='left', padx=6)
        self.search_entry = tk.Entry(top, font=FONT, width=40)
        self.search_entry.pack(side='left', padx=6)
        tk.Button(top, text='Buscar', command=self.on_search, font=FONT).pack(side='left', padx=6)

        # results (Treeview)
        tree_frame = tk.Frame(f, bg=BG)
        tree_frame.pack(fill='both', expand=True, padx=8, pady=6)
        
        cols = ('Date', 'Player', 'Op', 'Item', 'Qty', 'Price')
        self.search_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        
        for col in cols:
            self.search_tree.heading(col, text=col)
            
        self.search_tree.column('Date', width=120)
        self.search_tree.column('Player', width=100)
        self.search_tree.column('Op', width=50)
        self.search_tree.column('Item', width=300)
        self.search_tree.column('Qty', width=50)
        self.search_tree.column('Price', width=80)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=vsb.set)
        
        self.search_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

    def _build_advanced_frame(self):
        f = self.frames['advanced']
        pnl = tk.Frame(f, bg=BG)
        pnl.pack(fill='x', pady=8)

        # grid of inputs
        tk.Label(pnl, text='Contém (obrigatório):', bg=BG, font=FONT).grid(row=0, column=0, sticky='e', padx=6, pady=4)
        self.adv_must = tk.Entry(pnl, font=FONT, width=40)
        self.adv_must.grid(row=0, column=1, sticky='w')

        tk.Label(pnl, text='Não contém (opcional):', bg=BG, font=FONT).grid(row=1, column=0, sticky='e', padx=6, pady=4)
        self.adv_not = tk.Entry(pnl, font=FONT, width=40)
        self.adv_not.grid(row=1, column=1, sticky='w')

        self.exact_var = tk.BooleanVar(value=False)
        tk.Checkbutton(pnl, text='Combinação exata', variable=self.exact_var, bg=BG).grid(row=2, column=0, sticky='w', padx=6)
        self.case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(pnl, text='Case-sensitive', variable=self.case_var, bg=BG).grid(row=2, column=1, sticky='w')

        tk.Button(pnl, text='Buscar Avançado', command=self.on_advanced_search, font=FONT).grid(row=3, column=0, columnspan=2, pady=8)

        # results (Treeview)
        tree_frame = tk.Frame(f, bg=BG)
        tree_frame.pack(fill='both', expand=True, padx=8, pady=6)
        
        cols = ('Date', 'Player', 'Op', 'Item', 'Qty', 'Price')
        self.adv_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        
        for col in cols:
            self.adv_tree.heading(col, text=col)
            
        self.adv_tree.column('Date', width=120)
        self.adv_tree.column('Player', width=100)
        self.adv_tree.column('Op', width=50)
        self.adv_tree.column('Item', width=300)
        self.adv_tree.column('Qty', width=50)
        self.adv_tree.column('Price', width=80)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.adv_tree.yview)
        self.adv_tree.configure(yscrollcommand=vsb.set)
        
        self.adv_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

    def _build_stats_frame(self):
        f = self.frames['stats']
        
        # Toolbar
        top = tk.Frame(f, bg=BG)
        top.pack(fill='x', pady=8)
        tk.Button(top, text='Atualizar Estatísticas', command=self.refresh_stats).pack(side='left', padx=8)
        tk.Button(top, text='Exportar CSV', command=self.export_stats).pack(side='left', padx=8)

        # Split view: Text summary on top, Treeview on bottom
        paned = tk.PanedWindow(f, orient='vertical', bg=BG)
        paned.pack(fill='both', expand=True, padx=8, pady=6)
        
        self.stats_text = ScrolledText(paned, height=10, font=("Consolas", 10))
        paned.add(self.stats_text)
        
        # Treeview for top items
        tree_frame = tk.Frame(paned)
        self.stats_tree = ttk.Treeview(tree_frame, columns=('Item', 'Count'), show='headings')
        self.stats_tree.heading('Item', text='Item')
        self.stats_tree.heading('Count', text='Transações')
        self.stats_tree.column('Item', width=300)
        self.stats_tree.column('Count', width=100)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=vsb.set)
        
        self.stats_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        
        paned.add(tree_frame)

    def refresh_stats(self):
        if not self.engine:
            self.log_message('Engine não carregado. Carregue os dados primeiro.', is_error=True)
            return
            
        self.stats_text.delete('1.0', tk.END)
        # Clear tree
        for i in self.stats_tree.get_children():
            self.stats_tree.delete(i)
            
        try:
            # Text Summary
            self.stats_text.insert(tk.END, "=== RESUMO ESTATÍSTICO ===\n\n")
            self.stats_text.insert(tk.END, f"Total de Registros: {len(self.engine.df):,}\n")
            self.stats_text.insert(tk.END, f"Colunas: {len(self.engine.df.columns)}\n\n")
            
            # Basic info
            if 'date' in self.engine.df.columns:
                date_min = self.engine.df['date'].min()
                date_max = self.engine.df['date'].max()
                self.stats_text.insert(tk.END, f"Período: {date_min} até {date_max}\n\n")
            
            # Top Items to Treeview
            if 'main_item' in self.engine.df.columns:
                top_items = self.engine.df['main_item'].value_counts().head(50)
                for item, count in top_items.items():
                    self.stats_tree.insert('', 'end', values=(str(item), int(count)))
                self.stats_text.insert(tk.END, f"Top {len(top_items)} itens carregados na tabela abaixo.\n")
            else:
                self.stats_text.insert(tk.END, "Coluna 'main_item' não encontrada.\n")
                
            self.log_message('Estatísticas atualizadas com sucesso')
                
        except Exception as e:
            error_msg = f"Erro ao gerar estatísticas: {str(e)}"
            self.stats_text.insert(tk.END, error_msg)
            self.log_message(error_msg, is_error=True)

    def export_stats(self):
        if not self.engine:
            return
        try:
            f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if f:
                self.engine.df.to_csv(f, index=False)
                messagebox.showinfo("Exportar", f"Dados exportados para {f}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

    def _build_charts_frame(self):
        f = self.frames['charts']
        
        # Control panel
        controls = tk.Frame(f, bg=BG)
        controls.pack(fill='x', pady=8, padx=8)
        
        tk.Label(controls, text='Item:', bg=BG, font=FONT).pack(side='left')
        self.chart_item = tk.Entry(controls, font=FONT, width=20)
        self.chart_item.pack(side='left', padx=6)
        
        self.chart_type = tk.StringVar(value="Price History")
        tk.OptionMenu(controls, self.chart_type, "Price History", "Volume/Activity").pack(side='left', padx=6)
        
        tk.Button(controls, text='Gerar Gráfico', command=self.on_generate_chart, font=FONT).pack(side='left', padx=6)
        
        # Chart area
        self.chart_frame = tk.Frame(f, bg='white')
        self.chart_frame.pack(fill='both', expand=True, padx=8, pady=8)
        self.canvas = None

    def _build_insights_frame(self):
        f = self.frames['insights']
        
        # Header
        top = tk.Frame(f, bg=BG)
        top.pack(fill='x', pady=8, padx=8)
        
        tk.Label(top, text='Insights Preditivos (ML)', bg=BG, font=("Segoe UI", 14, "bold")).pack(side='left')
        tk.Button(top, text='Gerar Insights', command=self.on_generate_insights, font=FONT, bg=ACCENT, fg='white').pack(side='right', padx=8)

        # Description
        desc = tk.Label(f, text='O sistema analisará os dados carregados em busca de anomalias de preço e oportunidades de mercado.', 
                        bg=BG, fg='#aaaaaa', font=("Segoe UI", 9))
        desc.pack(fill='x', padx=8, pady=(0, 8))

        # Results Area (Treeview)
        tree_frame = tk.Frame(f, bg=BG)
        tree_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        self.insights_tree = ttk.Treeview(tree_frame, columns=('Item', 'Preço', 'Tipo', 'Detalhe', 'Score'), show='headings')
        self.insights_tree.heading('Item', text='Item')
        self.insights_tree.heading('Preço', text='Preço')
        self.insights_tree.heading('Tipo', text='Tipo')
        self.insights_tree.heading('Detalhe', text='Detalhe')
        self.insights_tree.heading('Score', text='Score (Z)')
        
        self.insights_tree.column('Item', width=150)
        self.insights_tree.column('Preço', width=80)
        self.insights_tree.column('Tipo', width=120)
        self.insights_tree.column('Detalhe', width=300)
        self.insights_tree.column('Score', width=60)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.insights_tree.yview)
        self.insights_tree.configure(yscrollcommand=vsb.set)
        
        self.insights_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

    def on_generate_insights(self):
        if not self.engine:
            messagebox.showerror('Erro', 'Dados não carregados.')
            return
            
        self.log_message('Iniciando análise preditiva (ML)...')
        self.set_status("Processando ML...")
        
        # Clear tree
        for i in self.insights_tree.get_children():
            self.insights_tree.delete(i)
            
        # Async execution
        def run_ml():
            return self.ml_predictor.run_prediction(self.engine.df)
            
        def on_success(results):
            self.log_message(f'Análise concluída. {len(results)} insights gerados.')
            self.set_status("Pronto")
            
            for res in results:
                if "insight" in res and len(res) == 1:
                     # Error or info message
                     self.insights_tree.insert('', 'end', values=('-', '-', 'Info', res['insight'], '-'))
                else:
                    self.insights_tree.insert('', 'end', values=(
                        res.get('Item', '?'),
                        res.get('Preço', '?'),
                        res.get('Tipo', '?'),
                        res.get('Detalhe', '?'),
                        res.get('Score', '?')
                    ))
                    
        def on_error(e):
            self.log_message(f'Erro na análise ML: {e}', is_error=True)
            self.set_status("Erro ML")
            
        checker = self.async_loader.load_async(run_ml, on_success, on_error)
        self._poll_loader(checker)

    def _build_plugins_frame(self):
        f = self.frames['plugins']
        top = tk.Frame(f, bg=BG)
        top.pack(fill='x', pady=8)
        tk.Button(top, text='Recarregar plugins', command=self.reload_plugins).pack(side='left', padx=8)
        tk.Button(top, text='Abrir pasta plugins', command=self.open_plugins_folder).pack(side='left', padx=8)

        self.plugins_listbox = tk.Listbox(f, height=12, font=FONT)
        self.plugins_listbox.pack(fill='x', padx=8, pady=6)
        self.plugin_run_btn = tk.Button(f, text='Executar plugin', command=self.run_selected_plugin)
        self.plugin_run_btn.pack(pady=6)

        self.plugin_output = ScrolledText(f, height=12, font=("Consolas", 10))
        self.plugin_output.pack(fill='both', expand=True, padx=8, pady=6)


    def _build_help_frame(self):
        f = self.frames['help']
        
        tk.Label(f, text='📚 Ajuda / Tutorial', bg=BG, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(pady=12)
        
        help_text = ScrolledText(f, height=30, font=("Segolas UI", 10), wrap='word', bg='#1e1e1e', fg='#d4d4d4')
        help_text.pack(fill='both', expand=True, padx=12, pady=8)
        
        tutorial = """
=== BEM-VINDO AO TORTA APP (WURM TRADE ANALYZER) ===

Este aplicativo analisa dados de trade do Wurm Online usando Pandas.

📌 COMO CARREGAR DADOS:
1. Vá na aba "Config"
2. Clique em "Selecionar" para escolher o arquivo de dados
3. Clique em "Aplicar e recarregar"
4. Aguarde a mensagem "Dados carregados" no Console de Log

🔍 BUSCAR:
- Digite o nome do item (ex: "iron", "log")
- A busca é case-insensitive e busca parcialmente
- Resultados aparecem no painel abaixo

🧭 BUSCA AVANÇADA:
- "Contém": termos obrigatórios (separados por espaço)
- "Não contém": termos a excluir
- Opções: Combinação exata / Case-sensitive

📊ESTATÍSTICAS:
- Mostra resumo dos dados carregados
- Top 50 itens mais negociados
- Clique em "Atualizar Estatísticas" para refresh
- Clique em "Exportar CSV" para salvar dados

📈 GRÁFICOS:
- Digite o nome do item
- Escolha tipo: "Price History" ou "Volume/Activity"
- Clique em "Gerar Gráfico"
- O gráfico aparece embed na janela
- Use zoom/pan do matplotlib para navegar

🧩 PLUGINS:
- Coloque arquivos .py na pasta "plugins"
- Clique em "Recarregar plugins" para atualizar lista
- Selecione um plugin e clique em "Executar plugin"

⚙️ CONFIG:
- Configure o caminho dos dados
- Veja o Console de Log para mensagens do sistema
- Erros aparecem em vermelho no console

💡 DICAS:
- O app usa tema escuro (CustomTkinter)
- Carregamento é assíncrono (não trava)
- Console de Log mostra timestamp de todas operações
- Encoding: latin-1 (compatível com logs do Wurm)

🚀 ANÁLISE AVANÇADA (APIs):
- engine.calculate_volatility(item, window=7)
- engine.calculate_mean_average(item, window=7)
- engine.otimizar_dataframe() - reduz uso de memória

===================================================
Criado por: Jotasiete7 | Versão: 2.0
===================================================
        """
        
        help_text.insert('1.0', tutorial)
        help_text.config(state='disabled')  # Read-only
        
    def show_help(self):
        self._hide_all_frames()
        self.frames['help'].pack(fill='both', expand=True)

    def _build_config_frame(self):
        f = self.frames['config']
        tk.Label(f, text='Configurações', bg=BG, font=("Segoe UI", 12)).pack(pady=8)
        cfg = tk.Frame(f, bg=BG)
        cfg.pack(pady=4)

        tk.Label(cfg, text='Caminho do ZIP/data:', bg=BG).grid(row=0, column=0, sticky='e')
        self.cfg_path = tk.Entry(cfg, width=50)
        self.cfg_path.insert(0, TRADE_ZIP_PATH)
        self.cfg_path.grid(row=0, column=1, padx=6)
        tk.Button(cfg, text='Selecionar', command=self.select_data_file).grid(row=0, column=2, padx=6)

        self.cache_var = tk.BooleanVar(value=True)
        tk.Checkbutton(cfg, text='Usar cache (não recarregar automaticamente)', variable=self.cache_var, bg=BG).grid(row=1, column=0, columnspan=3, sticky='w', pady=8)

        tk.Button(cfg, text='Aplicar e recarregar', command=self.apply_config).grid(row=2, column=0, columnspan=3, pady=6)
        
        # Log Console
        tk.Label(f, text='Console de Log', bg=BG, font=("Segoe UI", 12)).pack(pady=8)
        log_frame = tk.Frame(f, bg=BG)
        log_frame.pack(fill='both', expand=True, padx=8, pady=6)
        
        self.log_console = ScrolledText(log_frame, height=12, font=("Consolas", 9), bg='#1E1E1E', fg='#D4D4D4')
        self.log_console.pack(fill='both', expand=True)
        
        # Log initial message
        self.log_message("Console de log iniciado", is_error=False)

    # ------------------ view switching ------------------
    def _hide_all_frames(self):
        for f in self.frames.values():
            f.pack_forget()

    def show_search(self):
        self._hide_all_frames()
        self.frames['search'].pack(fill='both', expand=True)

    def show_advanced(self):
        self._hide_all_frames()
        self.frames['advanced'].pack(fill='both', expand=True)

    def show_stats(self):
        self._hide_all_frames()
        self.frames['stats'].pack(fill='both', expand=True)
        if hasattr(self, 'refresh_stats'):
            try:
                self.refresh_stats()
            except Exception as e:
                self.log_message(f'Erro ao atualizar estatísticas: {e}', is_error=True)

    def show_charts(self):
        self._hide_all_frames()
        self.frames['charts'].pack(fill='both', expand=True)

    def show_insights(self):
        self._hide_all_frames()
        self.frames['insights'].pack(fill='both', expand=True)

    def show_plugins(self):
        self._hide_all_frames()
        self.frames['plugins'].pack(fill='both', expand=True)

    def show_config(self):
        self._hide_all_frames()
        self.frames['config'].pack(fill='both', expand=True)

    # ------------------ actions ------------------
    def _background_load(self):
        """Attempt to extract and load data in background thread using AsyncDataLoader."""
        self.log_message('Iniciando carregamento de dados (Async)...')
        
        path = self.cfg_path.get() if hasattr(self, 'cfg_path') else TRADE_ZIP_PATH
        
        # Define the heavy lifting function
        def load_job():
            extracted = ensure_data_extracted(path, DEFAULT_DATA_DIR)
            if not extracted:
                raise FileNotFoundError("Nenhum dado encontrado ou falha na extração.")
            
            # Determine target file
            data_path = path
            if os.path.isdir(extracted):
                 target_file = os.path.join(extracted, "wurm_trade_master_2025_clean.txt")
                 if os.path.exists(target_file):
                     data_path = target_file
                 else:
                     for f in os.listdir(extracted):
                         if f.endswith('.txt'):
                             data_path = os.path.join(extracted, f)
                             break
            
            # Initialize engine
            return WurmStatsEngine(data_path)

        # Define success callback
        def on_success(engine):
            self.engine = engine
            self.log_message(f'Dados carregados com sucesso: {len(self.engine.df):,} registros.')
            self.reload_plugins()
            self.set_status("Pronto")

        # Define error callback
        def on_error(e):
            self.log_message(f'Erro fatal ao carregar dados: {e}', is_error=True)
            self.set_status("Erro no carregamento")

        # Start async operation
        checker = self.async_loader.load_async(load_job, on_success, on_error)
        
        # Start polling loop (50ms latency as requested)
        self._poll_loader(checker)

    def _poll_loader(self, checker):
        """Poll the async loader every 50ms."""
        if not checker():
            # If checker returns False, it means still loading
            self.after(50, lambda: self._poll_loader(checker))

    def on_search(self):
        q = self.search_entry.get()
        if not q.strip():
            messagebox.showinfo('Buscar', 'Digite algo para buscar')
            return
        if not self.engine:
            messagebox.showerror('Erro', 'Dados não carregados')
            return
            
        t0 = time.time()
        # Use engine filter
        try:
            df_res = self.engine.filter_by_item(q, exact=False)
            res = df_res.to_dict('records')
        except Exception as e:
            res = []
            print(e)

        dt = time.time() - t0
        
        # Clear tree
        for i in self.search_tree.get_children():
            self.search_tree.delete(i)
            
        self.set_status(f'Resultados: {len(res)} (took {dt:.3f}s)')
        
        for r in res[:2000]:
            # Map dict keys to columns
            # Keys might be: 'date', 'player', 'operation', 'main_item', 'main_qty', 'price_s'
            vals = (
                r.get('date', r.get('timestamp', '-')),
                r.get('player', '-'),
                r.get('operation', '-'),
                r.get('main_item', '-'),
                r.get('main_qty', '-'),
                r.get('price_s', '-')
            )
            self.search_tree.insert('', 'end', values=vals)

    def on_advanced_search(self):
        must = self.adv_must.get()
        if not self.engine:
            return
            
        t0 = time.time()
        df = self.engine.df
        if must:
            # Simple contains on raw_text if available, else main_item
            col = 'raw_text' if 'raw_text' in df.columns else 'main_item'
            mask = df[col].str.contains(must, case=not self.case_var.get(), na=False)
            df = df[mask]
        
        res = df.head(5000).to_dict('records')
        res = df.head(5000).to_dict('records')
        dt = time.time() - t0
        
        # Clear tree
        for i in self.adv_tree.get_children():
            self.adv_tree.delete(i)
            
        self.set_status(f'Resultados: {len(res)} (took {dt:.3f}s)')
        
        for r in res:
             # Map dict keys to columns
            vals = (
                r.get('date', r.get('timestamp', '-')),
                r.get('player', '-'),
                r.get('operation', '-'),
                r.get('main_item', '-'),
                r.get('main_qty', '-'),
                r.get('price_s', '-')
            )
            self.adv_tree.insert('', 'end', values=vals)

    def on_generate_chart(self):
        item = self.chart_item.get().strip()
        ctype = self.chart_type.get()
        
        if not self.engine:
            messagebox.showerror('Erro', 'Dados não carregados')
            return

        # Clear previous
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)

        try:
            if ctype == "Price History":
                if not item:
                    messagebox.showinfo('Aviso', 'Digite o nome do item para histórico de preços.')
                    return
                
                # Get data
                df = self.engine.filter_by_item(item)
                if df.empty:
                    messagebox.showinfo('Aviso', 'Nenhum dado encontrado para este item.')
                    return
                
                # Group by date and get mean price
                if 'date' in df.columns and 'price_s' in df.columns:
                    # Reset index to avoid ambiguity if date is both index and column
                    df_chart = df.reset_index(drop=True)
                    daily = df_chart.groupby('date')['price_s'].mean()
                    ax.plot(daily.index, daily.values, marker='o', linestyle='-')
                    ax.set_title(f'Histórico de Preço Médio: {item}')
                    ax.set_xlabel('Data')
                    ax.set_ylabel('Preço (s)')
                    fig.autofmt_xdate()
                else:
                    ax.text(0.5, 0.5, 'Dados insuficientes (falta data ou preço)', ha='center')

            elif ctype == "Volume/Activity":
                # If item is specified, filter by it, else global volume
                if item:
                    df = self.engine.filter_by_item(item)
                    title = f'Volume Diário: {item}'
                else:
                    df = self.engine.df
                    title = 'Volume Global de Trades'
                
                if 'date' in df.columns:
                    # Reset index to avoid ambiguity
                    df_chart = df.reset_index(drop=True)
                    daily_vol = df_chart.groupby('date').size()
                    ax.bar(daily_vol.index, daily_vol.values, color='skyblue')
                    ax.set_title(title)
                    ax.set_xlabel('Data')
                    ax.set_ylabel('Transações')
                    fig.autofmt_xdate()
                else:
                    ax.text(0.5, 0.5, 'Dados insuficientes (falta data)', ha='center')

            # Draw
            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao gerar gráfico: {e}')
            print(e)

    # ------------------ plugins ------------------
    def reload_plugins(self):
        self.plugins_meta = discover_plugins(PLUGINS_DIR)
        self.plugins_modules = {}
        self.plugins_listbox.delete(0, tk.END)
        for fn, meta in self.plugins_meta.items():
            self.plugins_listbox.insert(tk.END, fn)

    def open_plugins_folder(self):
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        if sys.platform.startswith('win'):
            os.startfile(PLUGINS_DIR)
        elif sys.platform == 'darwin':
            subprocess.run(['open', PLUGINS_DIR])
        else:
            try:
                subprocess.run(['xdg-open', PLUGINS_DIR])
            except Exception:
                messagebox.showinfo('Plugins', f'Plugins folder: {PLUGINS_DIR}')

    def run_selected_plugin(self):
        sel = self.plugins_listbox.curselection()
        if not sel:
            messagebox.showinfo('Plugins', 'Selecione um plugin para executar')
            return
        idx = sel[0]
        name = self.plugins_listbox.get(idx)
        meta = self.plugins_meta.get(name)
        path = meta['path']
        mod = load_plugin(path)
        if not mod:
            self.plugin_output.insert(tk.END, f'Falha ao carregar plugin {name}\n')
            return
        # try to call run
        try:
            params = {}
            result = None
            if hasattr(mod, 'run'):
                result = mod.run(self.engine, params)
            elif hasattr(mod, 'main'):
                result = mod.main(self.engine)
            else:
                result = 'Plugin não define run(data, params)'
            self.plugin_output.insert(tk.END, f'--- {name} output ---\n')
            if isinstance(result, (list, tuple)):
                for r in result:
                    self.plugin_output.insert(tk.END, str(r) + '\n')
            else:
                self.plugin_output.insert(tk.END, str(result) + '\n')
            self.plugin_output.insert(tk.END, '\n')
        except Exception as e:
            self.plugin_output.insert(tk.END, f'Erro executando plugin: {e}\n')

    # ------------------ config actions ------------------
    def select_data_file(self):
        p = filedialog.askopenfilename(title='Select ZIP or data folder', filetypes=[('Zip files', '*.zip'), ('All files', '*.*')])
        if p:
            self.cfg_path.delete(0, tk.END)
            self.cfg_path.insert(0, p)

    def apply_config(self):
        # re-run background loader with new path
        if not self.cache_var.get():
            # clear data folder to force reload
            try:
                if os.path.isdir(DEFAULT_DATA_DIR):
                    shutil.rmtree(DEFAULT_DATA_DIR)
            except Exception:
                pass
        self._background_load()


# ------------------------------
# Entry point
# ------------------------------

def main():
    # ensure plugins dir exists
    os.makedirs(PLUGINS_DIR, exist_ok=True)

    app = SuperPyGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
