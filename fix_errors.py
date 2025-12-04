import os

def fix_file(filepath, replacements):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for old, new in replacements:
            new_content = new_content.replace(old, new)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
        else:
            print(f"No changes needed for {filepath}")
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

# Fix rankings.ts
rankings_replacements = [
    ("console.error('Error fetching active traders:', error);", "console.error('Error fetching active traders:', error?.message || error);"),
    ("console.error('Error fetching active sellers:', error);", "console.error('Error fetching active sellers:', error?.message || error);"),
    ("console.error('Error fetching active buyers:', error);", "console.error('Error fetching active buyers:', error?.message || error);"),
    ("console.error('Error fetching price checkers:', error);", "console.error('Error fetching price checkers:', error?.message || error);")
]
fix_file('TortaApp-V2/services/rankings.ts', rankings_replacements)

# Fix emojiService.ts
emoji_replacements = [
    ("console.error('Failed to load emoji index:', error);", "console.error('Failed to load emoji index from /openmoji/openmoji-index.json:', error?.message || error);")
]
fix_file('TortaApp-V2/services/emojiService.ts', emoji_replacements)
