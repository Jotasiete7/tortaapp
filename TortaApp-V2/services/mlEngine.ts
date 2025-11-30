
/**
 * mlEngine.ts
 * Service responsible for Machine Learning calculations (Z-Score, Volatility).
 */

export interface PredictionResult {
    item_name: string;
    z_score: number;
    volatility: number;
    is_anomaly: boolean;
}

export class MLEngine {

    public static calculateZScore(prices: number[]): number[] {
        if (!prices || prices.length === 0) {
            return [];
        }

        const mean = this.calculateMean(prices);
        const stdDev = this.calculateStdDev(prices, mean);

        if (stdDev === 0) {
            return prices.map(() => 0);
        }

        return prices.map(price => (price - mean) / stdDev);
    }

    public static calculateVolatility(prices: number[]): number {
        if (!prices || prices.length === 0) {
            return 0;
        }
        const mean = this.calculateMean(prices);
        return this.calculateStdDev(prices, mean);
    }

    private static calculateMean(data: number[]): number {
        const sum = data.reduce((a, b) => a + b, 0);
        return sum / data.length;
    }

    private static calculateStdDev(data: number[], mean: number): number {
        const squareDiffs = data.map(value => Math.pow(value - mean, 2));
        const avgSquareDiff = this.calculateMean(squareDiffs);
        return Math.sqrt(avgSquareDiff);
    }

    public static analyzeAnomalies(records: any[], threshold: number = 2.0): PredictionResult[] {
        const prices = records.map(r => r.price_copper);
        const zScores = this.calculateZScore(prices);
        const volatility = this.calculateVolatility(prices);

        return records.map((record, index) => ({
            item_name: record.item_name,
            z_score: zScores[index],
            volatility: volatility,
            is_anomaly: Math.abs(zScores[index]) > threshold
        }));
    }
}

// --- EXPORTED FUNCTIONS FOR APP COMPATIBILITY ---

export const analyzePriceSet = (prices: number[]): { mean: number, volatility: number, min: number, max: number, sampleSize: number } => {
    if (!prices || prices.length === 0) {
        return { mean: 0, volatility: 0, min: 0, max: 0, sampleSize: 0 };
    }

    const sum = prices.reduce((a, b) => a + b, 0);
    const mean = sum / prices.length;
    const volatility = MLEngine.calculateVolatility(prices);
    const min = Math.min(...prices);
    const max = Math.max(...prices);

    return {
        mean,
        volatility,
        min,
        max,
        sampleSize: prices.length
    };
};
