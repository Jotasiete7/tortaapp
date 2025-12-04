const fs = require('fs');
const path = require('path');

const indexPath = path.join(__dirname, 'public', 'openmoji', 'openmoji-index.json');

try {
    const rawData = fs.readFileSync(indexPath, 'utf8');
    const emojis = JSON.parse(rawData);
    
    console.log(`Loaded ${emojis.length} emojis.`);

    const emojiMap = new Map();
    emojis.forEach(e => {
        emojiMap.set(e.emoji, e);
    });

    // Test case: Antarctica Flag
    // Hex: 1F1E6 1F1F6
    const flagChar = "\uD83C\uDDE6\uD83C\uDDF6"; // 🇦🇶
    
    console.log(`Testing flag: ${flagChar}`);
    console.log(`Flag in map? ${emojiMap.has(flagChar)}`);
    
    if (emojiMap.has(flagChar)) {
        console.log("Found in map:", emojiMap.get(flagChar).hexcode);
    } else {
        console.log("NOT found in map.");
        // Debugging: print codes of keys in map that look like flags
        const flagKeys = Array.from(emojiMap.keys()).filter(k => k.includes("\uD83C\uDDE6"));
        console.log("Similar keys in map:", flagKeys.length);
        flagKeys.forEach(k => {
            console.log(`Key: ${k} Codes: ${k.split('').map(c => c.charCodeAt(0).toString(16))}`);
        });
    }

    // Regex Test
    // Note: Node.js might not support \p{RI} without the --harmony flag or in older versions, 
    // but let's try a simpler regex that covers flags manually if needed.
    // The regex from emojiService.ts:
    const emojiRegex = /(\p{RI}\p{RI}|\p{Emoji}(\p{EMod}|\uFE0F\u20E3?|[\u{E0020}-\u{E007E}]+\u{E007F})?(\u200D\p{Emoji}(\p{EMod}|\uFE0F\u20E3?|[\u{E0020}-\u{E007E}]+\u{E007F})?)*)/gu;
    
    const text = "Hello 🇦🇶 World";
    let match;
    console.log(`\nTesting regex on: "${text}"`);
    
    while ((match = emojiRegex.exec(text)) !== null) {
        console.log(`Match: ${match[0]} at index ${match.index}`);
        const found = emojiMap.get(match[0]);
        console.log(`Lookup result: ${found ? found.hexcode : 'undefined'}`);
    }

} catch (err) {
    console.error(err);
}
