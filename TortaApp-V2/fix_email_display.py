# -*- coding: utf-8 -*-
import re

path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\App.tsx"

with open(path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find and replace the corrupted bullet string
# The pattern should match: {showEmail ? user.email : 'any characters here'}
pattern = r"\{showEmail \? user\.email : '[^']+'\}"
replacement = "{showEmail ? user.email : '••••••••••••••••'}"

new_content = re.sub(pattern, replacement, content)

if new_content != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Email display fixed.")
else:
    print("Pattern not found or already correct.")
