import os

path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\App.tsx"

with open(path, 'rb') as f:
    content = f.read()

# 1. Replace container div
target_div = b'<div className="flex items-center gap-2 mt-1">'
replace_div = b'<div className="flex items-center gap-2 mt-1 bg-slate-800/50 px-2 py-1 rounded border border-slate-700/50">'

if target_div in content:
    content = content.replace(target_div, replace_div)
    print("Container div replaced.")
else:
    print("Container div not found.")

# 2. Replace span class
target_span = b'<span className="text-xs text-slate-500">'
replace_span = b'<span className="text-xs text-slate-400 font-mono tracking-wide">'

if target_span in content:
    content = content.replace(target_span, replace_span)
    print("Span class replaced.")
else:
    print("Span class not found.")

# 3. Replace bullets (try to match the start of the expression)
# {showEmail ? user.email : 
target_expr = b'{showEmail ? user.email :'
# We want to replace the bullets part.
# Since we don't know the exact bytes of the bullets, we can't easily replace just them without regex or parsing.
# But we can try to find the closing `}` and replace everything in between.
# However, binary regex is not standard in python without `re` module on bytes.
# Let's try to use `re` on bytes.

import re
pattern = re.compile(rb'\{showEmail \? user\.email : [^\}]+\}')
replacement = b'{showEmail ? user.email : ' + b"'" + b'\\u2022'*16 + b"'" + b'}'
# Wait, \\u2022 in bytes will be literal backslash u... 
# If I want the actual bullet character in utf-8 bytes:
bullet_utf8 = b'\xe2\x80\xa2'
replacement = b'{showEmail ? user.email : ' + b"'" + bullet_utf8*16 + b"'" + b'}'

if pattern.search(content):
    content = pattern.sub(replacement, content)
    print("Bullets replaced.")
else:
    print("Bullets pattern not found.")

with open(path, 'wb') as f:
    f.write(content)
