"""
Patch to initialize PriceManager in SuperPyGUI
"""
import os

def apply_init_patch():
    file_path = 'superpy_app.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if PriceManager is imported
    if 'from price_manager import PriceManager' not in content:
        content = content.replace(
            'from charts_engine import ChartsEngine',
            'from charts_engine import ChartsEngine\nfrom price_manager import PriceManager'
        )
        print("✓ Added PriceManager import")

    # Check if initialized
    if 'self.price_manager = PriceManager' not in content:
        # Add initialization after charts_engine
        content = content.replace(
            'self.charts_engine = ChartsEngine()',
            'self.charts_engine = ChartsEngine()\n        self.price_manager = PriceManager(PRICE_BASE_PATH)'
        )
        print("✓ Added PriceManager initialization")
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\n✅ PriceManager initialization fixed!")

if __name__ == '__main__':
    apply_init_patch()
