import os

file_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\NewsTicker.tsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
if "import { emojiService } from '../services/emojiService';" not in content:
    content = content.replace(
        "import { Megaphone } from 'lucide-react';",
        "import { Megaphone } from 'lucide-react';\nimport { emojiService } from '../services/emojiService';"
    )

# 2. Load Emojis
if "emojiService.loadEmojis();" not in content:
    content = content.replace(
        "    useEffect(() => {\n        // Fetch initial messages",
        "    useEffect(() => {\n        // Load emojis\n        emojiService.loadEmojis();\n\n        // Fetch initial messages"
    )

# 3. Render Emojis
target_render = """                                <span className={`${colorMap[msg.color]} font-medium text-sm`}>
                                    {msg.text}
                                </span>"""

replacement_render = """                                <span className={`${colorMap[msg.color]} font-medium text-sm flex items-center`}>
                                    {emojiService.parseText(msg.text).map((part, i) => (
                                        typeof part === 'string' ? (
                                            <span key={i}>{part}</span>
                                        ) : (
                                            <img 
                                                key={i} 
                                                src={part.path} 
                                                alt={part.alt} 
                                                className="w-5 h-5 inline-block mx-0.5 align-text-bottom"
                                                loading="eager"
                                            />
                                        )
                                    ))}
                                </span>"""

if target_render in content:
    content = content.replace(target_render, replacement_render)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("NewsTicker.tsx patched successfully!")
