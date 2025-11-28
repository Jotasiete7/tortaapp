"""
Complete patch to add Price Editor tab to SuperPy
"""
import os
import re

def apply_price_editor_patch():
    file_path = 'superpy_app.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add APP_VERSION constant
    if 'APP_VERSION =' not in content:
        content = content.replace(
            'PRICE_BASE_PATH = os.path.join(EXTERNAL_DIR, "lista preços fixos outubro 2024.csv")',
            'PRICE_BASE_PATH = os.path.join(EXTERNAL_DIR, "lista preços fixos outubro 2024.csv")\nAPP_VERSION = "2.2.0"'
        )
        print("✓ Added APP_VERSION constant")
    
    # 2. Add Price Editor to menu
    if "'Price Editor'" not in content:
        old_menu = """        menu = [
            ('🔍', 'Buscar', self.show_search),
            ('🧭', 'Avançado', self.show_advanced),
            ('📊', 'Estatísticas', self.show_stats),
            ('📈', 'Gráficos', self.show_charts),
            ('🔮', 'Insights', self.show_insights),
            ('🧩', 'Plugins', self.show_plugins),
            ('⚙️', 'Config', self.show_config),
            ('❓', 'Ajuda', self.show_help),
        ]"""
        
        new_menu = """        menu = [
            ('🔍', 'Buscar', self.show_search),
            ('🧭', 'Avançado', self.show_advanced),
            ('📊', 'Estatísticas', self.show_stats),
            ('📈', 'Gráficos', self.show_charts),
            ('🔮', 'Insights', self.show_insights),
            ('💰', 'Price Editor', self.show_price_editor),
            ('🧩', 'Plugins', self.show_plugins),
            ('⚙️', 'Config', self.show_config),
            ('❓', 'Ajuda', self.show_help),
        ]"""
        
        content = content.replace(old_menu, new_menu)
        print("✓ Added Price Editor to menu")
    
    # 3. Add price_editor to frames list
    if "'price_editor'" not in content:
        content = content.replace(
            "for name in ['search', 'advanced', 'stats', 'charts', 'insights', 'plugins', 'config', 'help']:",
            "for name in ['search', 'advanced', 'stats', 'charts', 'insights', 'price_editor', 'plugins', 'config', 'help']:"
        )
        print("✓ Added price_editor to frames list")
    
    # 4. Add build call for price editor frame
    if '_build_price_editor_frame()' not in content:
        old_build = """        self._build_search_frame()
        self._build_advanced_frame()
        self._build_stats_frame()
        self._build_charts_frame()
        self._build_insights_frame()
        self._build_plugins_frame()"""
        
        new_build = """        self._build_search_frame()
        self._build_advanced_frame()
        self._build_stats_frame()
        self._build_charts_frame()
        self._build_insights_frame()
        self._build_price_editor_frame()
        self._build_plugins_frame()"""
        
        content = content.replace(old_build, new_build)
        print("✓ Added _build_price_editor_frame() call")
    
    # 5. Add show_price_editor method (before show_plugins)
    if 'def show_price_editor(self):' not in content:
        show_method = """
    def show_price_editor(self):
        self._hide_all_frames()
        self.frames['price_editor'].pack(fill='both', expand=True)
        self.refresh_price_list()

"""
        # Insert before show_plugins
        content = content.replace(
            '    def show_plugins(self):',
            show_method + '    def show_plugins(self):'
        )
        print("✓ Added show_price_editor() method")
    
    # 6. Add the complete _build_price_editor_frame method (before _build_plugins_frame)
    if 'def _build_price_editor_frame(self):' not in content:
        price_editor_frame = """
    def _build_price_editor_frame(self):
        f = self.frames['price_editor']
        
        # Header
        top = tk.Frame(f, bg=BG)
        top.pack(fill='x', pady=8, padx=8)
        tk.Label(top, text='💰 Editor de Preços Base', bg=BG, font=("Segoe UI", 14, "bold")).pack(side='left')
        tk.Button(top, text='Salvar Alterações', command=self.save_prices, font=FONT, bg=ACCENT, fg='white').pack(side='right', padx=8)
        
        # Controls
        controls = tk.Frame(f, bg=BG)
        controls.pack(fill='x', pady=8, padx=8)
        
        tk.Label(controls, text='Item:', bg=BG, font=FONT).grid(row=0, column=0, sticky='e', padx=6, pady=4)
        self.price_item_entry = tk.Entry(controls, font=FONT, width=30)
        self.price_item_entry.grid(row=0, column=1, sticky='w', padx=6)
        
        tk.Label(controls, text='Preço (copper):', bg=BG, font=FONT).grid(row=0, column=2, sticky='e', padx=6, pady=4)
        self.price_value_entry = tk.Entry(controls, font=FONT, width=15)
        self.price_value_entry.grid(row=0, column=3, sticky='w', padx=6)
        
        tk.Button(controls, text='Adicionar/Atualizar', command=self.add_update_price, font=FONT).grid(row=0, column=4, padx=6)
        tk.Button(controls, text='Deletar Selecionado', command=self.delete_selected_price, font=FONT).grid(row=0, column=5, padx=6)
        
        # Price list
        tree_frame = tk.Frame(f, bg=BG)
        tree_frame.pack(fill='both', expand=True, padx=8, pady=6)
        
        cols = ('Item', 'Preço Unitário (c)')
        self.price_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        
        self.price_tree.heading('Item', text='Item')
        self.price_tree.heading('Preço Unitário (c)', text='Preço Unitário (c)')
        
        self.price_tree.column('Item', width=400)
        self.price_tree.column('Preço Unitário (c)', width=150)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.price_tree.yview)
        self.price_tree.configure(yscrollcommand=vsb.set)
        
        self.price_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        
        # Bind double-click to edit
        self.price_tree.bind('<Double-1>', self.on_price_double_click)

    def refresh_price_list(self):
        \"\"\"Refresh the price list from PriceManager\"\"\"
        # Clear tree
        for i in self.price_tree.get_children():
            self.price_tree.delete(i)
        
        # Populate
        for item_name, price in sorted(self.price_manager.prices.items()):
            self.price_tree.insert('', 'end', values=(item_name.capitalize(), f'{price:.2f}'))
        
        self.set_status(f'Loaded {len(self.price_manager.prices)} prices')
    
    def add_update_price(self):
        \"\"\"Add or update a price\"\"\"
        item = self.price_item_entry.get().strip()
        price_str = self.price_value_entry.get().strip()
        
        if not item or not price_str:
            messagebox.showwarning('Aviso', 'Preencha Item e Preço')
            return
        
        try:
            price = float(price_str)
            self.price_manager.add_price(item, price)
            self.refresh_price_list()
            self.price_item_entry.delete(0, tk.END)
            self.price_value_entry.delete(0, tk.END)
            self.log_message(f'Preço adicionado/atualizado: {item} = {price}c')
        except ValueError:
            messagebox.showerror('Erro', 'Preço inválido')
    
    def delete_selected_price(self):
        \"\"\"Delete selected price\"\"\"
        selection = self.price_tree.selection()
        if not selection:
            messagebox.showwarning('Aviso', 'Selecione um item para deletar')
            return
        
        item_id = selection[0]
        values = self.price_tree.item(item_id)['values']
        item_name = values[0]
        
        if messagebox.askyesno('Confirmar', f'Deletar preço de \"{item_name}\"?'):
            self.price_manager.delete_price(item_name)
            self.refresh_price_list()
            self.log_message(f'Preço deletado: {item_name}')
    
    def save_prices(self):
        \"\"\"Save prices to CSV\"\"\"
        if self.price_manager.save_to_csv():
            messagebox.showinfo('Sucesso', 'Preços salvos com sucesso!')
            self.log_message('Preços salvos no CSV')
        else:
            messagebox.showerror('Erro', 'Falha ao salvar preços')
    
    def on_price_double_click(self, event):
        \"\"\"Load selected price into edit fields\"\"\"
        selection = self.price_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        values = self.price_tree.item(item_id)['values']
        
        self.price_item_entry.delete(0, tk.END)
        self.price_item_entry.insert(0, values[0])
        
        self.price_value_entry.delete(0, tk.END)
        self.price_value_entry.insert(0, values[1])

"""
        # Insert before _build_plugins_frame
        content = content.replace(
            '    def _build_plugins_frame(self):',
            price_editor_frame + '    def _build_plugins_frame(self):'
        )
        print("✓ Added _build_price_editor_frame() and related methods")
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Patch aplicado com sucesso!")
    print("Execute: python superpy_app.py")

if __name__ == '__main__':
    apply_price_editor_patch()
