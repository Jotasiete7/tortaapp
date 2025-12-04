import os

# Fix EmojiPicker.tsx
picker_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\EmojiPicker.tsx"
with open(picker_path, 'r', encoding='utf-8') as f:
    picker_content = f.read()

# Add type="button" to close button
if 'onClick={onClose}' in picker_content and 'type="button"' not in picker_content.split('onClick={onClose}')[0].split('<button')[-1]:
    picker_content = picker_content.replace(
        'onClick={onClose}',
        'type="button"\n                    onClick={onClose}'
    )

# Add type="button" to category buttons
if 'onClick={() => setCategory(cat.id)}' in picker_content and 'type="button"' not in picker_content.split('onClick={() => setCategory(cat.id)}')[0].split('<button')[-1]:
    picker_content = picker_content.replace(
        'onClick={() => setCategory(cat.id)}',
        'type="button"\n                        onClick={() => setCategory(cat.id)}'
    )

# Add type="button" to emoji buttons
if 'onClick={() => onSelect(emoji)}' in picker_content and 'type="button"' not in picker_content.split('onClick={() => onSelect(emoji)}')[0].split('<button')[-1]:
    picker_content = picker_content.replace(
        'onClick={() => onSelect(emoji)}',
        'type="button"\n                        onClick={() => onSelect(emoji)}'
    )

with open(picker_path, 'w', encoding='utf-8') as f:
    f.write(picker_content)
print("EmojiPicker.tsx patched!")

# Fix emojiService.ts
service_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\services\emojiService.ts"
with open(service_path, 'r', encoding='utf-8') as f:
    service_content = f.read()

# Update regex
old_regex = r"const emojiRegex = /(\p{Emoji_Presentation}|\p{Extended_Pictographic})/gu;"
new_regex = r"const emojiRegex = /(\p{RI}\p{RI}|\p{Emoji}(\p{EMod}|\uFE0F\u20E3?|[\u{E0020}-\u{E007E}]+\u{E007F})?(\u200D\p{Emoji}(\p{EMod}|\uFE0F\u20E3?|[\u{E0020}-\u{E007E}]+\u{E007F})?)*)/gu;"

if old_regex in service_content:
    service_content = service_content.replace(old_regex, new_regex)
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(service_content)
    print("emojiService.ts patched!")
else:
    print("Regex not found in emojiService.ts")
