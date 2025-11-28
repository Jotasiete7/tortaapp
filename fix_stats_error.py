"""
Patch to add missing run_optimized method to WurmStatsEngine
"""
import os

def apply_stats_patch():
    file_path = 'wurm_stats_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def run_optimized(self)' not in content:
        new_method = """
    def run_optimized(self) -> str:
        \"\"\"
        Executa uma análise otimizada e retorna um resumo em texto.
        \"\"\"
        if self.df is None or self.df.empty:
            return "Nenhum dado carregado."
            
        stats = self.get_stats()
        
        summary = [
            "=== Estatísticas Gerais ===",
            f"Total de Registros: {stats.get('total_records', 0):,}",
            f"Uso de Memória: {stats.get('memory_usage', 0):.2f} MB",
            f"Período: {stats.get('date_range', ('N/A', 'N/A'))}",
            "",
            "=== Top Itens (Volume) ===",
        ]
        
        if 'main_item' in self.df.columns:
            top_items = self.df['main_item'].value_counts().head(10)
            for item, count in top_items.items():
                summary.append(f"{item}: {count:,}")
                
        return "\\n".join(summary)
"""
        # Append to the end of the class (indentation matters!)
        # We'll look for the last method and append after it.
        # Or just replace the last known method to append this one.
        
        if 'def filter_by_item(self, item_name: str) -> pd.DataFrame:' in content:
            content = content.replace(
                'return self.df[self.df[\'main_item\'].str.contains(item_name, case=False, na=False)]',
                'return self.df[self.df[\'main_item\'].str.contains(item_name, case=False, na=False)]\n' + new_method
            )
            print("✓ Added run_optimized method")
        else:
            print("Could not find insertion point (filter_by_item)")
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\n✅ Stats engine patched successfully!")

if __name__ == '__main__':
    apply_stats_patch()
