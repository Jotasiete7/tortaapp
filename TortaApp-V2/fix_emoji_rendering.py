import os

# Fix emojiService to add debug logging
service_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\services\emojiService.ts"
with open(service_path, 'r', encoding='utf-8') as f:
    service_content = f.read()

# Add console.log to parseText
if "console.log('Parsing emoji:', emojiChar);" not in service_content:
    target = "const emojiChar = match[0];"
    replacement = """const emojiChar = match[0];
            console.log('Parsing emoji:', emojiChar, 'Codes:', Array.from(emojiChar).map(c => c.charCodeAt(0).toString(16)));"""
    service_content = service_content.replace(target, replacement)

# Add console.log to getEmoji
if "console.log('Looking up emoji in map');" not in service_content:
    target = "const openMoji = this.getEmoji(emojiChar);"
    replacement = """const openMoji = this.getEmoji(emojiChar);
            console.log('Lookup result:', openMoji ? openMoji.hexcode : 'NOT FOUND');"""
    service_content = service_content.replace(target, replacement)

with open(service_path, 'w', encoding='utf-8') as f:
    f.write(service_content)

print("Added debug logging to emojiService.ts")

# Also ensure the NewsTicker waits for emojis to load
ticker_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\NewsTicker.tsx"
with open(ticker_path, 'r', encoding='utf-8') as f:
    ticker_content = f.read()

# Add early return if emojis not loaded
if "if (!emojisLoaded) return null;" not in ticker_content:
    # Find the line "if (messages.length === 0) {"
    target = "if (messages.length === 0) {"
    replacement = """// Wait for emojis to load before rendering
    if (!emojisLoaded) {
        return null;
    }

    if (messages.length === 0) {"""
    ticker_content = ticker_content.replace(target, replacement)
    
    with open(ticker_path, 'w', encoding='utf-8') as f:
        f.write(ticker_content)
    print("Added emoji loading check to NewsTicker.tsx")
else:
    print("NewsTicker.tsx already has loading check")
