
/**
 * MLPredictor.ts
 * Service responsible for Machine Learning calculations (Z-Score, Volatility).
 */

export interface PredictionResult {
    item_name: string;
    z_score: number;
    volatility: number;
    is_anomaly: boolean;
}

export class MLPredictor {

    /**
     * Calculates the Z-Score for a list of prices.
     * Z = (X - Mean) / StdDev
     * 
     * @param prices Array of prices (numbers).
     * @returns Array of Z-Scores corresponding to the input prices.
     */
    public static calculateZScore(prices: number[]): number[] {
        if (!prices || prices.length === 0) {
            return [];
        }

        const mean = this.calculateMean(prices);
        const stdDev = this.calculateStdDev(prices, mean);

        if (stdDev === 0) {
            // If standard deviation is 0, all values are the same. Z-score is 0.
            return prices.map(() => 0);
        }

        return prices.map(price => (price - mean) / stdDev);
    }

    /**
     * Calculates the Volatility (Standard Deviation) of a list of prices.
     * 
     * @param prices Array of prices.
     * @returns The standard deviation.
     */
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

    /**
     * Analyzes a set of records to find anomalies based on Z-Score.
     * @param records List of objects containing 'price_copper'.
     * @param threshold Z-Score threshold to consider an anomaly (default 2.0).
     */
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
