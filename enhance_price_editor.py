"""
Patch to enhance Price Editor with Market Statistics
"""
import os

def apply_enhancement_patch():
    stats_engine_path = 'wurm_stats_engine.py'
    app_path = 'superpy_app.py'
    
    # 1. Update WurmStatsEngine with get_market_summary
    with open(stats_engine_path, 'r', encoding='utf-8') as f:
        stats_content = f.read()
        
    if 'def get_market_summary(self)' not in stats_content:
        new_method = """
    def get_market_summary(self) -> Dict[str, Dict[str, float]]:
        \"\"\"
        Retorna um resumo de mercado para todos os itens.
        Retorna: {item_name: {'avg_s': float, 'count': int}}
        \"\"\"
        if self.df is None or self.df.empty:
            return {}
            
        # Usa o dataframe limpo se disponível
        target_df = self.cleaned_df if hasattr(self, 'cleaned_df') and not self.cleaned_df.empty else self.df
        
        if 'main_item' not in target_df.columns or 'price_s' not in target_df.columns:
            return {}
            
        # Agrupa por item e calcula média de preço e contagem
        # Filtra apenas preços > 0 para evitar distorções com doações/erros
        valid_sales = target_df[target_df['price_s'] > 0]
        
        if valid_sales.empty:
            return {}
            
        summary = valid_sales.groupby('main_item', observed=True).agg({
            'price_s': 'mean',
            'main_qty': 'count' # Usamos count de linhas como volume de transações
        }).to_dict('index')
        
        # Renomeia chaves para facilitar uso
        result = {}
        for item, data in summary.items():
            result[str(item)] = {
                'avg_s': data['price_s'],
                'count': int(data['main_qty'])
            }
            
        return result
"""
        # Insert before run_optimized or at end of class
        if 'def run_optimized(self)' in stats_content:
            stats_content = stats_content.replace(
                'def run_optimized(self)',
                new_method + '\n    def run_optimized(self)'
            )
            print("✓ Added get_market_summary to WurmStatsEngine")
        else:
            # Append to end if run_optimized not found (fallback)
            stats_content += "\n" + new_method
            print("✓ Appended get_market_summary to WurmStatsEngine")
            
        with open(stats_engine_path, 'w', encoding='utf-8') as f:
            f.write(stats_content)

    # 2. Update SuperPyGUI to display stats
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()
        
    # Update _build_price_editor_frame columns
    if "cols = ('Item', 'Price')" in app_content:
        app_content = app_content.replace(
            "cols = ('Item', 'Price')",
            "cols = ('Item', 'Price', 'Mkt Avg', 'Vol')"
        )
        
        # Add column configs
        col_config = """
        self.price_tree.column('Item', width=300)
        self.price_tree.column('Price', width=100)
"""
        new_col_config = """
        self.price_tree.column('Item', width=250)
        self.price_tree.column('Price', width=100)
        self.price_tree.column('Mkt Avg', width=100)
        self.price_tree.column('Vol', width=60)
        
        self.price_tree.heading('Item', text='Item')
        self.price_tree.heading('Price', text='Ref Price (c)')
        self.price_tree.heading('Mkt Avg', text='Mkt Avg (c)')
        self.price_tree.heading('Vol', text='Vol')
"""
        # Replace the column config block
        # We need to be careful with matching. Let's match the heading part.
        if "self.price_tree.heading('Item', text='Item')" in app_content:
             # Find the block start
             start = app_content.find("self.price_tree.column('Item', width=300)")
             # Find the block end (approx)
             end = app_content.find("self.price_tree.heading('Price', text='Preço Unitário (c)')") + len("self.price_tree.heading('Price', text='Preço Unitário (c)')")
             
             if start != -1:
                 # We'll just replace the specific lines we know exist
                 app_content = app_content.replace("self.price_tree.column('Item', width=300)", "self.price_tree.column('Item', width=250)")
                 app_content = app_content.replace("self.price_tree.heading('Price', text='Preço Unitário (c)')", "self.price_tree.heading('Price', text='Ref Price (c)')")
                 
                 # Insert new columns after Price column config
                 insert_point = app_content.find("self.price_tree.column('Price', width=100)") + len("self.price_tree.column('Price', width=100)")
                 app_content = app_content[:insert_point] + "\n        self.price_tree.column('Mkt Avg', width=100)\n        self.price_tree.column('Vol', width=60)" + app_content[insert_point:]
                 
                 # Insert new headings after Price heading
                 insert_point_h = app_content.find("self.price_tree.heading('Price', text='Ref Price (c)')") + len("self.price_tree.heading('Price', text='Ref Price (c)')")
                 app_content = app_content[:insert_point_h] + "\n        self.price_tree.heading('Mkt Avg', text='Mkt Avg (c)')\n        self.price_tree.heading('Vol', text='Vol')" + app_content[insert_point_h:]
                 
        print("✓ Updated Price Editor columns")

    # Update refresh_price_list to populate new columns
    # We need to replace the loop
    old_loop_start = "for item_name, price in sorted(self.price_manager.prices.items()):"
    
    if old_loop_start in app_content:
        new_loop = """
        # Get market stats
        market_stats = {}
        if self.engine:
            market_stats = self.engine.get_market_summary()

        for item_name, price in sorted(self.price_manager.prices.items()):
            # Get stats
            stats = market_stats.get(item_name, {})
            avg_s = stats.get('avg_s', 0)
            count = stats.get('count', 0)
            
            # Convert avg to copper (1s = 100c)
            avg_c = avg_s * 100
            
            avg_str = f"{avg_c:.2f}" if count > 0 else "-"
            vol_str = str(count) if count > 0 else "-"
            
            self.price_tree.insert('', 'end', values=(item_name, f"{price:.2f}", avg_str, vol_str))
"""
        # We need to replace the whole loop body.
        # The old body is: self.price_tree.insert('', 'end', values=(item_name, f"{price:.2f}"))
        
        # Let's find the method and replace the content
        method_start = "def refresh_price_list(self):"
        if method_start in app_content:
            # Find the loop
            loop_idx = app_content.find(old_loop_start, app_content.find(method_start))
            if loop_idx != -1:
                # Find the insert line
                insert_line = "self.price_tree.insert('', 'end', values=(item_name, f\"{price:.2f}\"))"
                insert_idx = app_content.find(insert_line, loop_idx)
                
                if insert_idx != -1:
                    # Construct replacement
                    # We replace from loop start to end of insert line
                    end_replace = insert_idx + len(insert_line)
                    app_content = app_content[:loop_idx] + new_loop + app_content[end_replace:]
                    print("✓ Updated refresh_price_list logic")

    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
        
    print("\n✅ Price Editor enhanced successfully!")

if __name__ == '__main__':
    apply_enhancement_patch()
