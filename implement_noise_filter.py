"""
Patch to implement Noise Filter in WurmStatsEngine
"""
import os

def apply_noise_filter_patch():
    file_path = 'wurm_stats_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add 'import re'
    if 'import re' not in content:
        content = content.replace('import pandas as pd', 'import pandas as pd\nimport re')
        print("✓ Added 'import re'")

    # 2. Add NOISE_TERMS constant to class
    if 'NOISE_TERMS =' not in content:
        noise_terms = """
    # 1. CONSTANTE: Lista de Termos de Ruído (Stop Words)
    NOISE_TERMS = [
        "You can disable receiving these messages",
        "View the full Trade Chat Etiquette",
        "Please PM the person if you",
        "This is the Trade channel",
        "Only messages starting with WTB, WTS",
        "You can also use @<name> to",
        "common", 
        "rare",   
        "null",   
        "fragment",
        "casket",
        "clay",
    ]
"""
        # Insert after class definition
        content = content.replace(
            'class WurmStatsEngine:',
            'class WurmStatsEngine:' + noise_terms
        )
        print("✓ Added NOISE_TERMS")

    # 3. Update __init__ to call _preprocess_data
    if 'self.cleaned_df = self._preprocess_data()' not in content:
        # We need to add it after self.df is set.
        # There are two places where self.df is set: injection and loading.
        # Let's add it at the end of __init__ if self.df is not None
        
        # Or better, just add the call at the end of __init__
        # But we need to make sure cleaned_df is initialized
        
        init_end_marker = 'raise ValueError("É necessário fornecer \'data_path\' ou \'df\' para inicializar o engine.")'
        if init_end_marker in content:
            content = content.replace(
                init_end_marker,
                init_end_marker + '\n        \n        # Inicializa cleaned_df\n        self.cleaned_df = self._preprocess_data() if self.df is not None else pd.DataFrame()'
            )
            print("✓ Updated __init__ to call _preprocess_data")
            
    # 4. Add _preprocess_data method
    if 'def _preprocess_data(self)' not in content:
        preprocess_method = """
    def _preprocess_data(self) -> pd.DataFrame:
        \"\"\"
        Limpa o DataFrame removendo entradas de chat e ruído da coluna 'main_item'.
        \"\"\"
        if self.df is None or self.df.empty:
            return pd.DataFrame()
            
        df = self.df.copy()
        
        # 1. Garantir que a coluna 'main_item' exista
        if 'main_item' not in df.columns:
            logger.warning("Aviso: Coluna 'main_item' não encontrada. Pulando pré-processamento de ruído.")
            return df
        
        # 2. Criar a expressão regular de filtro
        noise_regex = '|'.join(map(re.escape, self.NOISE_TERMS))
        
        # 3. Filtrar as linhas que CONTÊM os termos de ruído
        try:
            filter_mask = ~df['main_item'].astype(str).str.contains(
                noise_regex, 
                case=False, 
                na=False,   
                regex=True
            )
            
            # 4. Aplicar o filtro
            df_cleaned = df[filter_mask]
            
            removed_count = len(df) - len(df_cleaned)
            if removed_count > 0:
                logger.info(f"Pré-processamento: {removed_count} linhas de ruído removidas.")
            
            return df_cleaned
        except Exception as e:
            logger.error(f"Erro no pré-processamento: {e}")
            return df
"""
        # Insert before _load_data
        content = content.replace(
            '    def _load_data(self) -> None:',
            preprocess_method + '\n    def _load_data(self) -> None:'
        )
        print("✓ Added _preprocess_data method")

    # 5. Update run_optimized to use cleaned_df
    # We need to replace the line: top_items = self.df['main_item'].value_counts().head(10)
    # with: top_items = self.cleaned_df['main_item'].value_counts().head(10)
    
    if "top_items = self.df['main_item'].value_counts().head(10)" in content:
        content = content.replace(
            "top_items = self.df['main_item'].value_counts().head(10)",
            "top_items = self.cleaned_df['main_item'].value_counts().head(10) if hasattr(self, 'cleaned_df') and not self.cleaned_df.empty else self.df['main_item'].value_counts().head(10)"
        )
        print("✓ Updated run_optimized to use cleaned_df")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\n✅ Noise filter implemented successfully!")

if __name__ == '__main__':
    apply_noise_filter_patch()
