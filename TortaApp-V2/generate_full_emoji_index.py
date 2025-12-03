# -*- coding: utf-8 -*-
import os
import json

svg_dir = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\public\openmoji"
output_file = os.path.join(svg_dir, "openmoji-index.json")

def categorize_emoji(hexcode):
    first_code = hexcode.split('-')[0]
    try:
        code_int = int(first_code, 16)
    except:
        return "symbols"
    
    if 0x1F600 <= code_int <= 0x1F64F:
        return "smileys"
    elif 0x1F680 <= code_int <= 0x1F6FF:
        return "travel"
    elif 0x1F300 <= code_int <= 0x1F5FF:
        return "nature"
    elif 0x1F400 <= code_int <= 0x1F4FF:
        return "animals"
    elif 0x1F950 <= code_int <= 0x1F9FF:
        return "food"
    elif 0x1F3A0 <= code_int <= 0x1F3FF:
        return "activities"
    elif 0x2600 <= code_int <= 0x26FF:
        return "symbols"
    elif 0x1F1E6 <= code_int <= 0x1F1FF:
        return "flags"
    else:
        return "objects"

emoji_index = []
svg_files = [f for f in os.listdir(svg_dir) if f.endswith('.svg')]

print(f"Processando {len(svg_files)} emojis...")

for svg_file in svg_files:
    hexcode = svg_file.replace('.svg', '')
    
    try:
        if '-' not in hexcode:
            emoji_char = chr(int(hexcode, 16))
        else:
            parts = hexcode.split('-')
            emoji_char = ''.join([chr(int(p, 16)) for p in parts if p and p != 'FE0F'])
    except:
        emoji_char = "?"
    
    category = categorize_emoji(hexcode)
    name = hexcode.replace('-', ' ').lower()
    
    emoji_index.append({
        "hexcode": hexcode,
        "emoji": emoji_char,
        "name": name,
        "category": category,
        "path": f"/openmoji/{hexcode}.svg"
    })

emoji_index.sort(key=lambda x: (x['category'], x['hexcode']))

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(emoji_index, f, ensure_ascii=False, indent=2)

print(f"Indice completo criado com {len(emoji_index)} emojis!")

categories = {}
for emoji in emoji_index:
    cat = emoji['category']
    categories[cat] = categories.get(cat, 0) + 1

print("\nEmojis por categoria:")
for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}")
