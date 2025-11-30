
/**
 * test_migration.ts
 * Simple script to verify the logic of FileParser, MLPredictor, and PriceManager.
 * Usage: npx ts-node test_migration.ts
 */

import { FileParser } from './services/FileParser';
import { MLPredictor } from './services/MLPredictor';
import { PriceManager } from './services/PriceManager';
import * as fs from 'fs';
import * as path from 'path';

function assert(condition: boolean, message: string) {
    if (!condition) {
        console.error(`❌ FAILED: ${message}`);
        process.exit(1);
    } else {
        console.log(`✅ PASSED: ${message}`);
    }
}

function testPriceNormalization() {
    console.log('\n--- Testing Price Normalization ---');
    assert(FileParser.normalizePrice("1g") === 10000, "1g should be 10000c");
    assert(FileParser.normalizePrice("1s") === 100, "1s should be 100c");
    assert(FileParser.normalizePrice("1c") === 1, "1c should be 1c");
    assert(FileParser.normalizePrice("1g 50s") === 15000, "1g 50s should be 15000c");
}

function testStopWords() {
    console.log('\n--- Testing Stop Words ---');
    assert(FileParser.isNoise("This is the Trade channel"), "Should detect 'This is the Trade channel'");
    assert(!FileParser.isNoise("WTB Iron Ore"), "Should NOT detect 'WTB' (Signal)");
}

function testMLPredictor() {
    console.log('\n--- Testing ML Predictor ---');
    const prices = [10, 12, 10, 12, 11];
    const zScores = MLPredictor.calculateZScore(prices);
    assert(Math.abs(zScores[4]) < 0.0001, "Mean value should have Z-Score 0");
}

function testPriceManager() {
    console.log('\n--- Testing Price Manager ---');

    // 1. Create a dummy CSV
    const csvContent = `Nome_Item;Qtd_Lote;Preco_Medio_Copper
Stone bricks;1000;175
Iron Lump;1;50
Rare Sword;1;10000`;

    const tempCsvPath = path.join(__dirname, 'temp_prices.csv');
    fs.writeFileSync(tempCsvPath, csvContent);

    const pm = new PriceManager();
    pm.loadRedheartPrices(tempCsvPath);

    // Test Redheart Lookup
    // Stone bricks: 175 / 1000 = 0.175
    assert(Math.abs(pm.getRedheartPrice("Stone bricks")! - 0.175) < 0.0001, "Stone bricks price should be 0.175");
    assert(pm.getRedheartPrice("Iron Lump") === 50, "Iron Lump price should be 50");
    assert(pm.getRedheartPrice("Unknown") === null, "Unknown item should be null");

    // Test Historical Average
    const trades = [
        { timestamp: '2023-01-01', sender: 'A', raw_text: '', item_name: 'Iron Lump', price_copper: 40 },
        { timestamp: '2023-01-02', sender: 'B', raw_text: '', item_name: 'Iron Lump', price_copper: 60 },
        { timestamp: '2023-01-03', sender: 'C', raw_text: '', item_name: 'Other', price_copper: 100 },
    ];

    const avg = pm.getHistoricalAverage(trades, 'Iron Lump');
    assert(avg === 50, "Historical average for Iron Lump should be 50");

    // Test Insight Generation
    // Current: 40, Redheart: 50, History: 50
    // Delta Redheart: (40-50)/50 = -0.2 (-20%) -> GOOD
    const insight = pm.generateInsight('Iron Lump', 40, trades);
    console.log('Insight:', insight);

    assert(insight.rating === 'GOOD', "Price 20% below reference should be GOOD");
    assert(insight.redheart_price === 50, "Insight should contain Redheart price");

    // Cleanup
    fs.unlinkSync(tempCsvPath);
}

// Run tests
try {
    testPriceNormalization();
    testStopWords();
    testMLPredictor();
    testPriceManager();
    console.log('\n🎉 ALL TESTS PASSED!');
} catch (e) {
    console.error(e);
}
