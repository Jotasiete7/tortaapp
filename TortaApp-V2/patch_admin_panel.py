import os

file_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\AdminPanel.tsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
if "import { EmojiPicker } from './EmojiPicker';" not in content:
    content = content.replace(
        "import { Megaphone, Plus, Trash2, Clock, Database } from 'lucide-react';",
        "import { Megaphone, Plus, Trash2, Clock, Database, Smile } from 'lucide-react';\nimport { EmojiPicker } from './EmojiPicker';"
    )

# 2. State
if "const [showEmojiPicker, setShowEmojiPicker] = useState(false);" not in content:
    content = content.replace(
        "const [loading, setLoading] = useState(false);",
        "const [loading, setLoading] = useState(false);\n    const [showEmojiPicker, setShowEmojiPicker] = useState(false);"
    )

# 3. Emoji Button & Picker
if "<Smile className=\"w-5 h-5\" />" not in content:
    target_input = 'className="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder:text-slate-600 focus:ring-2 focus:ring-amber-500/50 outline-none"'
    replacement = 'className="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder:text-slate-600 focus:ring-2 focus:ring-amber-500/50 outline-none pr-10"'
    
    content = content.replace(target_input, replacement)
    
    # Add button and picker after input
    picker_code = """
                        <button
                            type="button"
                            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                            className="absolute right-2 top-9 p-1.5 text-slate-400 hover:text-amber-400 hover:bg-slate-800 rounded-lg transition-colors"
                        >
                            <Smile className="w-5 h-5" />
                        </button>
                        {showEmojiPicker && (
                            <div className="absolute right-0 top-full mt-2 z-50">
                                <EmojiPicker
                                    onSelect={(emoji) => {
                                        setNewMessage(prev => prev + emoji.emoji);
                                        setShowEmojiPicker(false);
                                    }}
                                    onClose={() => setShowEmojiPicker(false)}
                                />
                            </div>
                        )}"""
    
    # Insert after the input element (need to find a good anchor)
    # The input ends with /> so we can look for that context
    anchor = 'outline-none pr-10"\n                        />'
    if anchor in content:
        content = content.replace(anchor, anchor + picker_code)

# 4. Relative positioning for parent div
if '<div className="space-y-2 relative">' not in content:
    content = content.replace(
        '<div className="space-y-2">\n                        <label className="text-sm font-medium text-slate-300">Message Text</label>',
        '<div className="space-y-2 relative">\n                        <label className="text-sm font-medium text-slate-300">Message Text</label>'
    )

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("AdminPanel.tsx patched successfully!")
