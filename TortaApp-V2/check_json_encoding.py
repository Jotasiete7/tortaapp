import json
import os

file_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\public\openmoji\openmoji-index.json"

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find Antarctica flag
flag = next((e for e in data if e['hexcode'] == '1F1E6-1F1F6'), None)

if flag:
    print(f"Hexcode: {flag['hexcode']}")
    print(f"Emoji (repr): {repr(flag['emoji'])}")
    print(f"Emoji (hex): {[hex(ord(c)) for c in flag['emoji']]}")
else:
    print("Flag not found")
