const fs = require('fs');
const path = require('path');

function fixFile(filePath, replacements) {
    try {
        const fullPath = path.resolve(filePath);
        if (!fs.existsSync(fullPath)) {
            console.log(File not found: );
            return;
        }
        let content = fs.readFileSync(fullPath, 'utf8');
        let newContent = content;
        
        for (const [oldStr, newStr] of replacements) {
            newContent = newContent.replace(oldStr, newStr);
        }
        
        if (content !== newContent) {
            fs.writeFileSync(fullPath, newContent, 'utf8');
            console.log(Updated );
        } else {
            console.log(No changes needed for );
        }
    } catch (err) {
        console.error(Error processing :, err);
    }
}

const rankingsReplacements = [
    ["console.error('Error fetching active traders:', error);", "console.error('Error fetching active traders:', error?.message || error);"],
    ["console.error('Error fetching active sellers:', error);", "console.error('Error fetching active sellers:', error?.message || error);"],
    ["console.error('Error fetching active buyers:', error);", "console.error('Error fetching active buyers:', error?.message || error);"],
    ["console.error('Error fetching price checkers:', error);", "console.error('Error fetching price checkers:', error?.message || error);"]
];

fixFile('TortaApp-V2/services/rankings.ts', rankingsReplacements);

const emojiReplacements = [
    ["console.error('Failed to load emoji index:', error);", "console.error('Failed to load emoji index from /openmoji/openmoji-index.json:', error?.message || error);"]
];

fixFile('TortaApp-V2/services/emojiService.ts', emojiReplacements);
