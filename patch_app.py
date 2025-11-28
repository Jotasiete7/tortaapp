import os
import pandas as pd

file_path = 'superpy_app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'from price_manager import PriceManager' not in content:
    content = content.replace('from charts_engine import ChartsEngine', 'from charts_engine import ChartsEngine\nfrom price_manager import PriceManager')

if 'PRICE_BASE_PATH' not in content:
    content = content.replace('PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")', 
                              'PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")\nEXTERNAL_DIR = os.path.join(os.path.dirname(__file__), "external")\nPRICE_BASE_PATH = os.path.join(EXTERNAL_DIR, "lista preços fixos outubro 2024.csv")')

if 'self.price_manager = PriceManager' not in content:
    content = content.replace('self.charts_engine = ChartsEngine()', 'self.charts_engine = ChartsEngine()\n        self.price_manager = PriceManager(PRICE_BASE_PATH)')

search_cols_old = "cols = ('Date', 'Player', 'Op', 'Item', 'Qty', 'Price')"
search_cols_new = "cols = ('Date', 'Player', 'Op', 'Item', 'Qty', 'Price', 'Ref', 'Delta')"

if search_cols_old in content:
    content = content.replace(search_cols_old, search_cols_new)
    search_col_conf = "self.search_tree.column('Price', width=80)"
    search_col_conf_new = "self.search_tree.column('Price', width=80)\n        self.search_tree.column('Ref', width=60)\n        self.search_tree.column('Delta', width=60)\n        self.search_tree.tag_configure('good_deal', background='#C6EFCE')\n        self.search_tree.tag_configure('bad_deal', background='#FFC7CE')"
    content = content.replace(search_col_conf, search_col_conf_new)

adv_col_conf = "self.adv_tree.column('Price', width=80)"
adv_col_conf_new = "self.adv_tree.column('Price', width=80)\n        self.adv_tree.column('Ref', width=60)\n        self.adv_tree.column('Delta', width=60)\n        self.adv_tree.tag_configure('good_deal', background='#C6EFCE')\n        self.adv_tree.tag_configure('bad_deal', background='#FFC7CE')"
content = content.replace(adv_col_conf, adv_col_conf_new)

search_loop_start = "        for r in res[:2000]:"
search_loop_block_new = """        for r in res[:2000]:
            # Evaluate Deal
            item_name = r.get('main_item', '')
            qty = r.get('main_qty', 1)
            if pd.isna(qty): qty = 1
            
            price_val = r.get('price_s')
            if pd.isna(price_val) or isinstance(price_val, str):
                 price_val = 0
            
            eval_res = self.price_manager.evaluate_trade(str(item_name), price_val, float(qty))
            
            rating = eval_res.get('rating', 'UNKNOWN')
            delta = eval_res.get('delta_percent', 0)
            ref_price = eval_res.get('reference_unit_price', 0)
            
            delta_str = f"{delta:+.0f}%" if rating != 'UNKNOWN' else "-"
            ref_str = f"{ref_price:.2f}" if ref_price else "-"
            
            tag = ''
            if rating == 'GOOD': tag = 'good_deal'
            elif rating == 'BAD': tag = 'bad_deal'

            vals = (
                r.get('date', r.get('timestamp', '-')),
                r.get('player', '-'),
                r.get('operation', '-'),
                r.get('main_item', '-'),
                r.get('main_qty', '-'),
                r.get('price_s', '-'),
                ref_str,
                delta_str
            )
            self.search_tree.insert('', 'end', values=vals, tags=(tag,))"""

if search_loop_start in content and 'self.price_manager.evaluate_trade' not in content:
    orig_block = """        for r in res[:2000]:
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
            self.search_tree.insert('', 'end', values=vals)"""
    content = content.replace(orig_block, search_loop_block_new)

adv_loop_block_new = """        for r in res:
            # Evaluate Deal
            item_name = r.get('main_item', '')
            qty = r.get('main_qty', 1)
            if pd.isna(qty): qty = 1
            
            price_val = r.get('price_s')
            if pd.isna(price_val) or isinstance(price_val, str):
                 price_val = 0
            
            eval_res = self.price_manager.evaluate_trade(str(item_name), price_val, float(qty))
            
            rating = eval_res.get('rating', 'UNKNOWN')
            delta = eval_res.get('delta_percent', 0)
            ref_price = eval_res.get('reference_unit_price', 0)
            
            delta_str = f"{delta:+.0f}%" if rating != 'UNKNOWN' else "-"
            ref_str = f"{ref_price:.2f}" if ref_price else "-"
            
            tag = ''
            if rating == 'GOOD': tag = 'good_deal'
            elif rating == 'BAD': tag = 'bad_deal'

            vals = (
                r.get('date', r.get('timestamp', '-')),
                r.get('player', '-'),
                r.get('operation', '-'),
                r.get('main_item', '-'),
                r.get('main_qty', '-'),
                r.get('price_s', '-'),
                ref_str,
                delta_str
            )
            self.adv_tree.insert('', 'end', values=vals, tags=(tag,))"""

orig_adv_block = """        for r in res:
             # Map dict keys to columns
            vals = (
                r.get('date', r.get('timestamp', '-')),
                r.get('player', '-'),
                r.get('operation', '-'),
                r.get('main_item', '-'),
                r.get('main_qty', '-'),
                r.get('price_s', '-')
            )
            self.adv_tree.insert('', 'end', values=vals)"""

if orig_adv_block in content:
    content = content.replace(orig_adv_block, adv_loop_block_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch applied successfully.")
