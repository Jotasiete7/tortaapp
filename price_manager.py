import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class PriceManager:
    def __init__(self, csv_path=None):
        self.prices = {}
        self.csv_path = csv_path
        if csv_path and os.path.exists(csv_path):
            self.load_from_csv(csv_path)

    def load_from_csv(self, path):
        try:
            df = pd.read_csv(path, sep=';')
            df.columns = [c.strip() for c in df.columns]
            count = 0
            for _, row in df.iterrows():
                try:
                    name = str(row['Nome_Item']).strip().lower()
                    qty = float(row['Qtd_Lote'])
                    total_price = float(row['Preco_Medio_Copper'])
                    if qty > 0:
                        unit_price = total_price / qty
                        self.prices[name] = unit_price
                        count += 1
                except:
                    continue
            logger.info(f'Loaded {count} base prices')
        except Exception as e:
            logger.error(f'Failed to load CSV: {e}')

    def get_reference_price(self, item_name):
        if not item_name: return None
        return self.prices.get(item_name.lower().strip())

    def evaluate_trade(self, item_name, price_copper, quantity=1):
        ref_price = self.get_reference_price(item_name)
        if ref_price is None or quantity <= 0 or price_copper is None:
            return {'rating': 'UNKNOWN', 'delta_percent': 0.0}
        
        trade_unit_price = price_copper / quantity
        if ref_price == 0: return {'rating': 'UNKNOWN', 'delta_percent': 0.0}
        
        delta = ((trade_unit_price - ref_price) / ref_price) * 100
        rating = 'FAIR'
        if delta <= -10: rating = 'GOOD'
        elif delta >= 10: rating = 'BAD'
        
        return {
            'reference_unit_price': ref_price,
            'trade_unit_price': trade_unit_price,
            'delta_percent': delta,
            'rating': rating
        }
