import os

ticker_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\NewsTicker.tsx"

with open(ticker_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Duplicate messages for seamless loop
old_map = "{messages.map((msg, index) => ("
new_map = "{[...messages, ...messages].map((msg, index) => ("

if old_map in content and new_map not in content:
    content = content.replace(old_map, new_map)
    print("Fixed message duplication for seamless loop")

# Fix 2: Adjust animation to start from right edge
old_keyframes = """@keyframes marquee {
          0% { transform: translateX(0%); }
          100% { transform: translateX(-50%); }
        }"""

new_keyframes = """@keyframes marquee {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }"""

if old_keyframes in content:
    content = content.replace(old_keyframes, new_keyframes)
    print("Fixed marquee animation keyframes")

with open(ticker_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Ticker animation fixed!")
