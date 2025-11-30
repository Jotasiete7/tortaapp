
/**
 * FileParser.ts
 * Service responsible for parsing and cleaning raw data from Wurm Online logs.
 */

export interface TradeRecord {
    timestamp: string;
    sender: string;
    raw_text: string;
    price_copper: number;
    item_name: string;
    // Add other fields as necessary
}

export class FileParser {

    // 1. CONSTANTE: Lista de Termos de Ruído (Stop Words)
    // Ported from Python project
    private static readonly NOISE_TERMS = [
        "You can disable receiving these messages",
        "View the full Trade Chat Etiquette",
        "Please PM the person if you",
        "This is the Trade channel",
        "Only messages starting with WTB, WTS",
        "You can also use @<name> to",
        "common",
        "rare",
        "null",
        "fragment",
        "casket",
        "clay",
    ];

    /**
     * Normalizes a price string into a numeric Copper value.
     * Conversion rates:
     * 1g = 10000c
     * 1s = 100c
     * 1c = 1c
     * 1i = 0.01c
     * 
     * @param priceVal The price string (e.g., "1g 50s", "10i") or number.
     * @returns The price in Copper Coins (float). Returns 0.0 if invalid.
     */
    public static normalizePrice(priceVal: string | number | null | undefined): number {
        if (priceVal === null || priceVal === undefined) {
            return 0.0;
        }

        const s = String(priceVal).toLowerCase().trim();
        if (!s || s === 'nan' || s === 'none') {
            return 0.0;
        }

        // Remove extra spaces and handle comma as decimal separator if present (though usually dot in logs)
        const cleanStr = s.replace(',', '.');

        // 2. Try direct numeric conversion (assuming simple number is Copper)
        const directVal = parseFloat(cleanStr);
        if (!isNaN(directVal) && /^-?\d*(\.\d+)?$/.test(cleanStr)) {
            return directVal;
        }

        // 3. Complex Parse (g/s/c/i)
        let totalCopper = 0.0;

        // Regex to extract parts: (value) (unit g, s, c, i)
        // Matches things like "1g", "50s", "10.5c"
        const regex = /([\d.]+)\s*([gsci])/g;
        let match;
        let foundMatch = false;

        while ((match = regex.exec(cleanStr)) !== null) {
            foundMatch = true;
            const val = parseFloat(match[1]);
            const unit = match[2];

            if (!isNaN(val)) {
                switch (unit) {
                    case 'g':
                        totalCopper += val * 10000.0;
                        break;
                    case 's':
                        totalCopper += val * 100.0;
                        break;
                    case 'c':
                        totalCopper += val;
                        break;
                    case 'i':
                        totalCopper += val / 100.0; // 1 Iron = 0.01 Copper
                        break;
                }
            }
        }

        if (foundMatch) {
            return totalCopper;
        }

        return 0.0;
    }

    /**
     * Checks if a text contains any of the defined noise terms.
     * @param text The text to check (e.g., raw log line or item name).
     * @returns True if the text contains noise, False otherwise.
     */
    public static isNoise(text: string): boolean {
        if (!text) return false;
        const lowerText = text.toLowerCase();

        return FileParser.NOISE_TERMS.some(term =>
            lowerText.includes(term.toLowerCase())
        );
    }

    /**
     * Parses a list of raw records, normalizing prices and filtering noise.
     * IMPORTANT: Normalization happens BEFORE filtering zero-prices (if any).
     * This function returns ALL valid parsed records, including those with 0 price.
     */
    public static parseRecords(rawRecords: any[]): TradeRecord[] {
        const parsedRecords: TradeRecord[] = [];

        for (const record of rawRecords) {
            // 1. Filter Noise first to avoid processing junk
            if (this.isNoise(record.raw_text) || this.isNoise(record.item_name)) {
                continue;
            }

            // 2. Normalize Price
            // We ensure this happens for every record
            const priceCopper = this.normalizePrice(record.price_str || record.price);

            // 3. Construct Record
            // We DO NOT filter by price > 0 here. That is a UI concern.
            parsedRecords.push({
                timestamp: record.timestamp,
                sender: record.sender,
                raw_text: record.raw_text,
                item_name: record.item_name,
                price_copper: priceCopper
            });
        }

        return parsedRecords;
    }
}
