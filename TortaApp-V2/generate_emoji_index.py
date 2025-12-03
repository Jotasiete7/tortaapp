# -*- coding: utf-8 -*-
import os
import json

# Caminho para os SVGs
svg_dir = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\public\openmoji"
output_file = os.path.join(svg_dir, "openmoji-index.json")

# Mapeamento básico de categorias (emojis mais comuns)
# Formato: hexcode -> (emoji_char, name, category, tags)
COMMON_EMOJIS = {
    # Smileys & Emotion
    "1F600": ("��", "grinning face", "smileys", ["happy", "smile"]),
    "1F603": ("😃", "grinning face with big eyes", "smileys", ["happy", "joy"]),
    "1F604": ("��", "grinning face with smiling eyes", "smileys", ["happy", "joy"]),
    "1F601": ("😁", "beaming face with smiling eyes", "smileys", ["grin"]),
    "1F606": ("😆", "grinning squinting face", "smileys", ["laugh", "happy"]),
    "1F605": ("😅", "grinning face with sweat", "smileys", ["hot", "happy"]),
    "1F602": ("😂", "face with tears of joy", "smileys", ["laugh", "cry"]),
    "1F923": ("🤣", "rolling on the floor laughing", "smileys", ["lol", "laugh"]),
    "1F60A": ("😊", "smiling face with smiling eyes", "smileys", ["blush", "happy"]),
    "1F607": ("😇", "smiling face with halo", "smileys", ["angel", "innocent"]),
    "1F609": ("😉", "winking face", "smileys", ["wink", "flirt"]),
    "1F60D": ("😍", "smiling face with heart-eyes", "smileys", ["love", "crush"]),
    "1F618": ("😘", "face blowing a kiss", "smileys", ["kiss", "love"]),
    "1F61B": ("😛", "face with tongue", "smileys", ["tongue", "playful"]),
    "1F61C": ("😜", "winking face with tongue", "smileys", ["wink", "tongue"]),
    "1F61D": ("😝", "squinting face with tongue", "smileys", ["tongue", "playful"]),
    "1F62D": ("😭", "loudly crying face", "smileys", ["cry", "sad"]),
    "1F622": ("😢", "crying face", "smileys", ["cry", "sad"]),
    "1F620": ("😠", "angry face", "smileys", ["angry", "mad"]),
    "1F621": ("😡", "pouting face", "smileys", ["angry", "mad"]),
    "1F44D": ("👍", "thumbs up", "people", ["like", "yes", "ok"]),
    "1F44E": ("👎", "thumbs down", "people", ["dislike", "no"]),
    "1F44F": ("👏", "clapping hands", "people", ["clap", "applause"]),
    "1F64F": ("🙏", "folded hands", "people", ["pray", "thanks"]),
    
    # Hearts
    "2764": ("❤️", "red heart", "hearts", ["love", "heart"]),
    "1F49B": ("💛", "yellow heart", "hearts", ["love", "heart"]),
    "1F49A": ("💚", "green heart", "hearts", ["love", "heart"]),
    "1F499": ("💙", "blue heart", "hearts", ["love", "heart"]),
    "1F49C": ("💜", "purple heart", "hearts", ["love", "heart"]),
    "1F5A4": ("🖤", "black heart", "hearts", ["love", "heart"]),
    
    # Animals & Nature
    "1F436": ("🐶", "dog face", "animals", ["dog", "pet"]),
    "1F431": ("🐱", "cat face", "animals", ["cat", "pet"]),
    "1F981": ("🦁", "lion", "animals", ["lion", "wild"]),
    "1F42F": ("🐯", "tiger face", "animals", ["tiger", "wild"]),
    "1F43B": ("🐻", "bear", "animals", ["bear", "wild"]),
    "1F437": ("🐷", "pig face", "animals", ["pig", "farm"]),
    "1F984": ("🦄", "unicorn", "animals", ["unicorn", "fantasy"]),
    "1F525": ("🔥", "fire", "nature", ["fire", "hot", "flame"]),
    "2B50": ("⭐", "star", "nature", ["star", "favorite"]),
    "1F31F": ("🌟", "glowing star", "nature", ["star", "sparkle"]),
    "26A1": ("⚡", "high voltage", "nature", ["lightning", "zap"]),
    "1F308": ("🌈", "rainbow", "nature", ["rainbow", "pride"]),
    
    # Food & Drink
    "1F355": ("��", "pizza", "food", ["pizza", "food"]),
    "1F354": ("🍔", "hamburger", "food", ["burger", "food"]),
    "1F35F": ("🍟", "french fries", "food", ["fries", "food"]),
    "1F32D": ("🌭", "hot dog", "food", ["hotdog", "food"]),
    "1F32E": ("🌮", "taco", "food", ["taco", "food"]),
    "1F32F": ("🌯", "burrito", "food", ["burrito", "food"]),
    "1F370": ("🍰", "shortcake", "food", ["cake", "dessert"]),
    "1F382": ("🎂", "birthday cake", "food", ["cake", "birthday"]),
    "1F36A": ("🍪", "cookie", "food", ["cookie", "dessert"]),
    "1F36B": ("🍫", "chocolate bar", "food", ["chocolate", "dessert"]),
    "1F369": ("🍩", "doughnut", "food", ["donut", "dessert"]),
    "2615": ("☕", "hot beverage", "drink", ["coffee", "tea"]),
    "1F37A": ("��", "beer mug", "drink", ["beer", "drink"]),
    "1F377": ("🍷", "wine glass", "drink", ["wine", "drink"]),
    
    # Activities & Sports
    "26BD": ("⚽", "soccer ball", "sports", ["soccer", "football"]),
    "1F3C0": ("🏀", "basketball", "sports", ["basketball"]),
    "1F3C8": ("🏈", "american football", "sports", ["football"]),
    "26BE": ("⚾", "baseball", "sports", ["baseball"]),
    "1F3BE": ("🎾", "tennis", "sports", ["tennis"]),
    "1F3AE": ("🎮", "video game", "activities", ["game", "gaming"]),
    "1F3B5": ("🎵", "musical note", "activities", ["music", "note"]),
    "1F3B8": ("🎸", "guitar", "activities", ["guitar", "music"]),
    
    # Travel & Places
    "1F697": ("🚗", "automobile", "travel", ["car", "vehicle"]),
    "1F695": ("🚕", "taxi", "travel", ["taxi", "car"]),
    "1F68C": ("🚌", "bus", "travel", ["bus", "vehicle"]),
    "2708": ("✈️", "airplane", "travel", ["plane", "flight"]),
    "1F680": ("🚀", "rocket", "travel", ["rocket", "space"]),
    "1F3E0": ("🏠", "house", "places", ["home", "house"]),
    "1F3E2": ("🏢", "office building", "places", ["office", "building"]),
    "1F3EB": ("🏫", "school", "places", ["school", "education"]),
    
    # Objects
    "1F4F1": ("📱", "mobile phone", "objects", ["phone", "mobile"]),
    "1F4BB": ("💻", "laptop", "objects", ["computer", "laptop"]),
    "2328": ("⌨️", "keyboard", "objects", ["keyboard"]),
    "1F5A5": ("🖥️", "desktop computer", "objects", ["computer", "desktop"]),
    "1F4A1": ("💡", "light bulb", "objects", ["idea", "light"]),
    "1F4DA": ("📚", "books", "objects", ["books", "education"]),
    "1F4B0": ("💰", "money bag", "objects", ["money", "cash"]),
    "1F4B8": ("💸", "money with wings", "objects", ["money", "cash"]),
    "1F381": ("🎁", "wrapped gift", "objects", ["gift", "present"]),
    "1F389": ("🎉", "party popper", "objects", ["party", "celebration"]),
    "1F38A": ("🎊", "confetti ball", "objects", ["party", "celebration"]),
    
    # Symbols
    "2705": ("✅", "check mark button", "symbols", ["check", "yes", "done"]),
    "274C": ("❌", "cross mark", "symbols", ["x", "no", "cancel"]),
    "2757": ("❗", "exclamation mark", "symbols", ["!", "warning"]),
    "2753": ("❓", "question mark", "symbols", ["?", "question"]),
    "1F4AF": ("💯", "hundred points", "symbols", ["100", "perfect"]),
    "1F525": ("🔥", "fire", "symbols", ["fire", "hot"]),
}

# Gerar índice
emoji_index = []
for hexcode, (emoji, name, category, tags) in COMMON_EMOJIS.items():
    emoji_index.append({
        "hexcode": hexcode,
        "emoji": emoji,
        "name": name,
        "category": category,
        "tags": tags,
        "path": f"/openmoji/{hexcode}.svg"
    })

# Salvar JSON
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(emoji_index, f, ensure_ascii=False, indent=2)

print(f"Índice criado com {len(emoji_index)} emojis em: {output_file}")
