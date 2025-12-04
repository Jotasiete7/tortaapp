import os

file_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\NewsTicker.tsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add state
if "const [emojisLoaded, setEmojisLoaded] = useState(false);" not in content:
    content = content.replace(
        "const [messages, setMessages] = useState<TickerMessage[]>([]);",
        "const [messages, setMessages] = useState<TickerMessage[]>([]);\n    const [emojisLoaded, setEmojisLoaded] = useState(false);"
    )

# Update useEffect
if "emojiService.loadEmojis().then(() => setEmojisLoaded(true));" not in content:
    content = content.replace(
        "// Load emojis\n        emojiService.loadEmojis();",
        "// Load emojis\n        emojiService.loadEmojis().then(() => setEmojisLoaded(true));"
    )

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("NewsTicker.tsx patched for async loading!")
