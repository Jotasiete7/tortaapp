# build_exe.py
# Script para construir executável do SuperPy usando PyInstaller

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

# Configurações
APP_NAME = "SuperPy"
MAIN_SCRIPT = "superpy_app.py"
ICON_FILE = None  # Adicione o caminho para um .ico se tiver

# Diretórios
BASE_DIR = Path(__file__).parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"

# Limpa builds anteriores
if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)
if BUILD_DIR.exists():
    shutil.rmtree(BUILD_DIR)

# Argumentos do PyInstaller
args = [
    str(BASE_DIR / MAIN_SCRIPT),
    '--name', APP_NAME,
    '--onefile',  # Cria um único executável
    '--windowed',  # Sem console (apenas GUI)
    '--clean',
    
    # Adiciona dados necessários
    '--add-data', f'{BASE_DIR / "data"};data',  # Inclui pasta de dados se existir
    
    # Hidden imports (módulos que PyInstaller pode não detectar)
    '--hidden-import', 'pandas',
    '--hidden-import', 'numpy',
    '--hidden-import', 'matplotlib',
    '--hidden-import', 'customtkinter',
    '--hidden-import', 'PIL',
    '--hidden-import', 'wurm_stats_engine',
    '--hidden-import', 'ml_predictor',
    '--hidden-import', 'threading_utils',
    '--hidden-import', 'wurm_parser',
    
    # Otimizações
    '--optimize', '2',
]

# Adiciona ícone se disponível
if ICON_FILE and os.path.exists(ICON_FILE):
    args.extend(['--icon', ICON_FILE])

# Executa PyInstaller
print(f"🔨 Construindo {APP_NAME}...")
PyInstaller.__main__.run(args)

print(f"\n✅ Build completo! Executável em: {DIST_DIR / APP_NAME}.exe")
print("\n📦 Para distribuir:")
print(f"   1. Copie o executável de: {DIST_DIR}")
print("   2. Inclua a pasta 'data' se necessário")
print("   3. Distribua junto com README.md")
