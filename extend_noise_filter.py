"""
Patch to extend Noise Filter to multiple columns in WurmStatsEngine
"""
import os

def apply_extended_noise_filter():
    file_path = 'wurm_stats_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add COLUMNS_TO_CHECK constant
    if 'COLUMNS_TO_CHECK =' not in content:
        columns_const = """
    # Lista de colunas onde o ruído deve ser verificado
    COLUMNS_TO_CHECK = ['main_item', 'raw_text', 'description']
"""
        # Insert after NOISE_TERMS
        if 'NOISE_TERMS = [' in content:
            # Find the end of NOISE_TERMS list
            idx = content.find('NOISE_TERMS = [')
            end_idx = content.find(']', idx)
            if end_idx != -1:
                content = content[:end_idx+1] + columns_const + content[end_idx+1:]
                print("✓ Added COLUMNS_TO_CHECK")

    # 2. Replace _preprocess_data method with extended version
    new_preprocess = """
    def _preprocess_data(self) -> pd.DataFrame:
        \"\"\"
        Limpa o DataFrame removendo entradas de chat e ruído em múltiplas colunas.
        \"\"\"
        if self.df is None or self.df.empty:
            return pd.DataFrame()
            
        df = self.df.copy()
        
        # 1. Criar a expressão regular de filtro
        noise_regex = '|'.join(map(re.escape, self.NOISE_TERMS))
        
        # 2. Inicializar a máscara de filtro combinada (False = não é ruído)
        combined_noise_mask = pd.Series([False] * len(df), index=df.index)
        
        # 3. Iterar sobre as colunas e construir a máscara de ruído
        for col in self.COLUMNS_TO_CHECK:
            if col in df.columns:
                try:
                    # Máscara de ruído para a coluna atual: True se a coluna CONTÉM ruído
                    current_noise_mask = df[col].astype(str).str.contains(
                        noise_regex, 
                        case=False, 
                        na=False, 
                        regex=True
                    )
                    
                    # Combinar a máscara atual com a máscara combinada usando OR (|)
                    combined_noise_mask = combined_noise_mask | current_noise_mask
                except Exception as e:
                    logger.warning(f"Erro ao filtrar coluna {col}: {e}")
            else:
                # logger.debug(f"Coluna '{col}' não encontrada no DataFrame.")
                pass

        # 4. Aplicar o filtro final
        # O '~' inverte a máscara: seleciona o que NÃO é ruído.
        try:
            final_filter_mask = ~combined_noise_mask
            df_cleaned = df[final_filter_mask]
            
            removed_count = len(df) - len(df_cleaned)
            if removed_count > 0:
                logger.info(f"Pré-processamento: {removed_count} linhas de ruído removidas (filtro multicamada).")
            
            return df_cleaned
        except Exception as e:
            logger.error(f"Erro no pré-processamento final: {e}")
            return df
"""

    # We need to find the existing _preprocess_data method and replace it
    if 'def _preprocess_data(self) -> pd.DataFrame:' in content:
        # Simple string replacement might be tricky if indentation varies, but let's try to match the signature
        # and replace until the next method definition
        
        start_marker = '    def _preprocess_data(self) -> pd.DataFrame:'
        end_marker = '    def _load_data(self) -> None:' # Assuming this is the next method
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            content = content[:start_idx] + new_preprocess + '\n' + content[end_idx:]
            print("✓ Replaced _preprocess_data with extended version")
        else:
            print("Could not find method boundaries for replacement")
    else:
        print("Could not find _preprocess_data method to replace")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\n✅ Extended noise filter applied successfully!")

if __name__ == '__main__':
    apply_extended_noise_filter()
