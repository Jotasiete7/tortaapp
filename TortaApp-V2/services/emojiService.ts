interface Emoji {
    hexcode: string;
    emoji: string;
    name: string;
    category: string;
    path: string;
}

class EmojiService {
    private emojis: Emoji[] = [];
    private emojiMap: Map<string, Emoji> = new Map();
    private isLoaded = false;

    async loadEmojis() {
        if (this.isLoaded) return;

        try {
            const response = await fetch('/openmoji/openmoji-index.json');
            this.emojis = await response.json();
            
            // Criar mapa reverso para busca rápida por caractere emoji
            this.emojis.forEach(e => {
                this.emojiMap.set(e.emoji, e);
            });
            
            this.isLoaded = true;
        } catch (error) {
            console.error('Failed to load emoji index:', error);
        }
    }

    getEmoji(char: string): Emoji | undefined {
        return this.emojiMap.get(char);
    }

    // Parse text and replace emoji characters with OpenMoji SVGs
    parseText(text: string): (string | { type: 'emoji', path: string, alt: string })[] {
        if (!text) return [];
        
        // Regex para encontrar emojis (simplificado, pode precisar de ajustes para sequências complexas)
        // Esta regex cobre a maioria dos ranges de emoji
        const emojiRegex = /(\p{RI}\p{RI}|\p{Emoji}(\p{EMod}|\uFE0F\u20E3?|[\u{E0020}-\u{E007E}]+\u{E007F})?(\u200D\p{Emoji}(\p{EMod}|\uFE0F\u20E3?|[\u{E0020}-\u{E007E}]+\u{E007F})?)*)/gu;
        
        const parts: (string | { type: 'emoji', path: string, alt: string })[] = [];
        let lastIndex = 0;
        let match;

        while ((match = emojiRegex.exec(text)) !== null) {
            // Adicionar texto anterior ao emoji
            if (match.index > lastIndex) {
                parts.push(text.substring(lastIndex, match.index));
            }

            const emojiChar = match[0];
            const openMoji = this.getEmoji(emojiChar);

            if (openMoji) {
                parts.push({
                    type: 'emoji',
                    path: openMoji.path,
                    alt: emojiChar
                });
            } else {
                // Se não encontrar no índice OpenMoji, mantém o caractere original
                parts.push(emojiChar);
            }

            lastIndex = emojiRegex.lastIndex;
        }

        // Adicionar restante do texto
        if (lastIndex < text.length) {
            parts.push(text.substring(lastIndex));
        }

        return parts;
    }
}

export const emojiService = new EmojiService();
