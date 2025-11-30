
/**
 * PriceManager.ts
 * Service responsible for managing reference prices (Redheart) and calculating historical averages.
 */

import * as fs from 'fs';
import { TradeRecord } from './FileParser';

export interface PriceInsight {
    item_name: string;
    current_price: number;
    redheart_price: number | null;
    historical_avg: number | null;
    delta_redheart: number | null; // Percentage difference from Redheart
    delta_historical: number | null; // Percentage difference from History
    message: string;
    rating: 'GOOD' | 'BAD' | 'FAIR' | 'UNKNOWN';
}

export class PriceManager {
    private redheartPrices: Map<string, number> = new Map();

    /**
     * Loads Redheart prices from a CSV file.
     * Expected format: Nome_Item;Qtd_Lote;Preco_Medio_Copper
     * @param csvPath Path to the CSV file.
     */
    public loadRedheartPrices(csvPath: string): void {
        try {
            const content = fs.readFileSync(csvPath, 'utf-8');
            this.parseCSV(content);
        } catch (e) {
            console.error(`Failed to load Redheart prices from ${csvPath}:`, e);
        }
    }

    /**
     * Parses CSV content string.
     * @param content CSV string content.
     */
    public parseCSV(content: string): void {
        const lines = content.split(/\r?\n/);
        let count = 0;

        for (const line of lines) {
            const parts = line.split(';');
            if (parts.length < 3) continue;

            const name = parts[0].trim().replace(/"/g, ''); // Remove quotes if present
            const qtyStr = parts[1].trim().replace(/"/g, '');
            const priceStr = parts[2].trim().replace(/"/g, '');

            if (name === 'Nome_Item') continue; // Skip header

            const qty = parseFloat(qtyStr);
            const totalCopper = parseFloat(priceStr);

            if (!isNaN(qty) && !isNaN(totalCopper) && qty > 0) {
                const unitPrice = totalCopper / qty;
                this.redheartPrices.set(name.toLowerCase(), unitPrice);
                count++;
            }
        }
        console.log(`Loaded ${count} Redheart prices.`);
    }

    /**
     * Gets the Redheart reference price for an item.
     * @param itemName Item name.
     * @returns Unit price in Copper, or null if not found.
     */
    public getRedheartPrice(itemName: string): number | null {
        return this.redheartPrices.get(itemName.toLowerCase()) || null;
    }

    /**
     * Calculates the historical average price for an item from a list of trades.
     * Uses the last N trades (default 1000) or all available if less.
     * @param trades List of TradeRecords.
     * @param itemName Item name to filter by.
     * @param limit Max number of recent trades to consider.
     * @returns Average unit price in Copper, or null if no trades found.
     */
    public getHistoricalAverage(trades: TradeRecord[], itemName: string, limit: number = 1000): number | null {
        const itemTrades = trades
            .filter(t => t.item_name.toLowerCase() === itemName.toLowerCase() && t.price_copper > 0)
            .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()) // Sort desc by date
            .slice(0, limit);

        if (itemTrades.length === 0) return null;

        const total = itemTrades.reduce((sum, t) => sum + t.price_copper, 0);
        return total / itemTrades.length;
    }

    /**
     * Generates a price insight for a specific trade offer.
     * @param itemName Item name.
     * @param currentPrice Current unit price in Copper.
     * @param trades Historical trade records.
     */
    public generateInsight(itemName: string, currentPrice: number, trades: TradeRecord[]): PriceInsight {
        const redheartPrice = this.getRedheartPrice(itemName);
        const historicalAvg = this.getHistoricalAverage(trades, itemName);

        let deltaRedheart: number | null = null;
        let deltaHistorical: number | null = null;
        let message = "No reference data.";
        let rating: 'GOOD' | 'BAD' | 'FAIR' | 'UNKNOWN' = 'UNKNOWN';

        // Compare with Redheart (Primary Reference)
        if (redheartPrice !== null) {
            deltaRedheart = ((currentPrice - redheartPrice) / redheartPrice) * 100;
        }

        // Compare with History (Secondary Reference)
        if (historicalAvg !== null) {
            deltaHistorical = ((currentPrice - historicalAvg) / historicalAvg) * 100;
        }

        // Logic for Insight Message and Rating
        // Priority: Redheart > History
        const refPrice = redheartPrice ?? historicalAvg;
        const delta = deltaRedheart ?? deltaHistorical;

        if (refPrice !== null && delta !== null) {
            if (delta <= -15) {
                rating = 'GOOD';
                message = `Price is ${Math.abs(delta).toFixed(1)}% BELOW reference. Good buy!`;
            } else if (delta >= 15) {
                rating = 'BAD';
                message = `Price is ${delta.toFixed(1)}% ABOVE reference. Expensive.`;
            } else {
                rating = 'FAIR';
                message = `Price is fair (within 15% of reference).`;
            }
        }

        return {
            item_name: itemName,
            current_price: currentPrice,
            redheart_price: redheartPrice,
            historical_avg: historicalAvg,
            delta_redheart: deltaRedheart,
            delta_historical: deltaHistorical,
            message: message,
            rating: rating
        };
    }
}
