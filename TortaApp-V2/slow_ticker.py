import os

ticker_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\NewsTicker.tsx"

with open(ticker_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Change animation duration from 30s to 60s
old_duration = "animation: marquee 30s linear infinite;"
new_duration = "animation: marquee 60s linear infinite;"

if old_duration in content:
    content = content.replace(old_duration, new_duration)
    print("Ticker speed reduced to 60s (half speed)")
    
    with open(ticker_path, 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("Duration not found or already changed")
