"""
Patch to restore missing constants in superpy_app.py
"""
import os

def apply_constants_patch():
    file_path = 'superpy_app.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the lines to insert
    missing_lines = """EXTERNAL_DIR = os.path.join(os.path.dirname(__file__), "external")
PRICE_BASE_PATH = os.path.join(EXTERNAL_DIR, "lista preços fixos outubro 2024.csv")
APP_VERSION = "2.2.0"
"""
    
    # Check if they are already there
    if 'PRICE_BASE_PATH =' in content:
        print("PRICE_BASE_PATH already exists.")
    else:
        # Insert after PLUGINS_DIR
        target = 'PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")'
        if target in content:
            content = content.replace(target, target + '\n' + missing_lines)
            print("✓ Added missing constants")
        else:
            print("Could not find insertion point (PLUGINS_DIR)")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\n✅ Constants fixed successfully!")

if __name__ == '__main__':
    apply_constants_patch()
