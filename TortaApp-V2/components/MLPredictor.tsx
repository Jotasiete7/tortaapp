
import React, { useState, useMemo } from 'react';
import { BrainCircuit, Loader2, TrendingUp, TrendingDown, Info, AlertTriangle, Search, Filter, Layers } from 'lucide-react';
import { PredictionResult, MarketItem, BulkAnalysis } from '../types';
import { analyzePriceSet } from '../services/mlEngine';
import { formatWurmPrice } from '../services/priceUtils';
import { extractNameAndQty } from '../services/fileParser';

interface MLPredictorProps {
    data: MarketItem[];
}

// --- BULK ANALYSIS LOGIC ---
const analyzeBulks = (items: MarketItem[]): BulkAnalysis => {
    const bulkSizes = Array.from(new Set(items
        .filter(item => item.quantity > 1)
        .map(item => item.quantity)
    )).sort((a, b) => a - b);

    const hasBulks = bulkSizes.length > 0;

    // Calculate multipliers based on unit prices
    // (Avg Unit Price of Bulk X) / (Avg Unit Price of Single)
    const bulkMultipliers = bulkSizes.map(size => {
        const bulkItems = items.filter(item => item.quantity === size);
        const singleItems = items.filter(item => item.quantity === 1);

        // If we have no singles to compare against, assume no specific multiplier/discount logic can be derived strictly
        // but usually bulk is cheaper per unit.
        if (singleItems.length === 0) return 1;

        const avgBulkUnitPrice = bulkItems.reduce((sum, item) => sum + item.price, 0) / bulkItems.length;
        const avgSingleUnitPrice = singleItems.reduce((sum, item) => sum + item.price, 0) / singleItems.length;

        // Multiplier: < 1 means Bulk is cheaper per unit (Discount)
        return avgSingleUnitPrice > 0 ? avgBulkUnitPrice / avgSingleUnitPrice : 1;
    });

    // Recommend the bulk size with the best value (lowest multiplier)
    // If no singles exist, just pick the largest bulk as it's typically efficient.
    let recommendedBulkIdx = 0;
    if (hasBulks) {
        recommendedBulkIdx = bulkMultipliers.reduce((bestIdx, currentMult, currentIdx) => {
            return currentMult < bulkMultipliers[bestIdx] ? currentIdx : bestIdx;
        }, 0);
    }

    return {
        hasBulks,
        bulkSizes,
        bulkMultipliers,
        recommendedBulk: hasBulks ? bulkSizes[recommendedBulkIdx] : 1
    };
};

// --- COMPONENT: BULK SELECTOR ---
const BulkSelector: React.FC<{
    analysis: BulkAnalysis;
    selected: number;
    onSelect: (bulk: number) => void;
}> = ({ analysis, selected, onSelect }) => {
    return (
        <div className="space-y-3 p-4 bg-slate-800/50 rounded-lg border border-slate-700 mt-4 animate-fade-in">
            <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-purple-400" />
                    Bulk Quantity / Batch Size
                </label>
                <div className="text-xs text-slate-500 bg-slate-900 px-2 py-1 rounded">
                    {analysis.hasBulks ? `${analysis.bulkSizes.length} sizes found` : 'No bulk trades found'}
                </div>
            </div>

            <div className="flex flex-wrap gap-2">
                {/* Option: Single */}
                <button
                    onClick={() => onSelect(1)}
                    className={`px-3 py-2 rounded-lg border transition-all ${selected === 1
                        ? 'bg-purple-600 border-purple-500 text-white'
                        : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-600'
                        }`}
                >
                    Single (1x)
                </button>

                {/* Options: Bulks */}
                {analysis.bulkSizes.map((size, index) => {
                    const multiplier = analysis.bulkMultipliers[index];
                    const isBestValue = analysis.recommendedBulk === size;

                    return (
                        <button
                            key={size}
                            onClick={() => onSelect(size)}
                            className={`px-3 py-2 rounded-lg border transition-all relative group ${selected === size
                                ? 'bg-emerald-600 border-emerald-500 text-white'
                                : isBestValue
                                    ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 hover:border-amber-500'
                                    : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-600'
                                }`}
                        >
                            {size}x
                            {isBestValue && (
                                <div className="absolute -top-1 -right-1 w-2 h-2 bg-amber-400 rounded-full animate-pulse" title="Best Value"></div>
                            )}
                            <div className="text-xs opacity-70 flex gap-1 justify-center mt-1">
                                {multiplier < 0.95 ? '💸' : multiplier > 1.05 ? '⚠️' : '✓'}
                            </div>
                        </button>
                    );
                })}
            </div>

            {analysis.hasBulks && (
                <div className="text-xs text-slate-400 space-y-1 pt-1">
                    <div className="flex gap-3">
                        <span>💸 Better value</span>
                        <span>⚠️ Premium price</span>
                        <span>✓ Fair price</span>
                    </div>
                    {analysis.recommendedBulk > 1 && (
                        <div className="text-amber-400 font-medium">
                            Recommendation: Buy {analysis.recommendedBulk}x packs for best per-unit value.
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};


export const MLPredictor: React.FC<MLPredictorProps> = ({ data }) => {
    const [quality, setQuality] = useState(50);
    const [material, setMaterial] = useState('Any');
    const [itemName, setItemName] = useState('');

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<PredictionResult | null>(null);
    const [marketStats, setMarketStats] = useState<any>(null);
    const [relevantTrades, setRelevantTrades] = useState<MarketItem[]>([]);

    // Bulk State
    const [bulkAnalysis, setBulkAnalysis] = useState<BulkAnalysis | null>(null);
    const [selectedBulk, setSelectedBulk] = useState<number>(1);
    const [showBulks, setShowBulks] = useState(false);

    // 1. Extração Dinâmica de Materiais
    const availableMaterials = useMemo(() => {
        if (data.length === 0) return ['Iron', 'Wood', 'Cotton'];
        const mats = new Set<string>();
        data.forEach(d => {
            if (d.material && d.material !== 'Unknown') {
                const m = d.material.charAt(0).toUpperCase() + d.material.slice(1);
                mats.add(m);
            }
        });
        return Array.from(mats).sort();
    }, [data]);

    // 2. Extração Dinâmica de Nomes
    const availableItemNames = useMemo(() => {
        if (data.length === 0) return [];
        const names = new Set<string>();
        data.slice(0, 5000).forEach(d => {
            if (d.name && d.name !== 'Unknown') names.add(d.name);
        });
        return Array.from(names).sort();
    }, [data]);

    const handlePredict = async () => {
        setLoading(true);
        setMarketStats(null);
        setResult(null);
        setRelevantTrades([]);
        setBulkAnalysis(null);
        setSelectedBulk(1); // Reset to single by default
        setShowBulks(false);

        await new Promise(resolve => setTimeout(resolve, 500));

        try {
            // SMART SEARCH
            const searchExtraction = extractNameAndQty(itemName);
            const cleanSearchTerm = searchExtraction.cleanName.toLowerCase();

            // 1. Filtragem Inteligente
            const relevantItems = data.filter(item => {
                const matchMat = material === 'Any' || (item.material && item.material.toLowerCase() === material.toLowerCase());
                const matchName = cleanSearchTerm === '' || item.name.toLowerCase().includes(cleanSearchTerm);
                return matchMat && matchName && item.price > 0;
            });

            setRelevantTrades(relevantItems.slice(0, 20));

            if (relevantItems.length === 0) {
                setLoading(false);
                return;
            }

            // 2. Análise de Bulks
            const analysis = analyzeBulks(relevantItems);
            setBulkAnalysis(analysis);
            setShowBulks(analysis.hasBulks);

            // 3. Análise Estatística (Baseada em Unit Price inicialmente)
            const unitPrices = relevantItems.map(i => i.price);
            const stats = analyzePriceSet(unitPrices);
            setMarketStats(stats);

            // 4. Projeção Inicial (Unitário)
            const basePredictedPrice = stats.mean;

            let confidence = 0.9;
            if (stats.volatility > stats.mean * 0.5) confidence -= 0.2;
            if (stats.sampleSize < 10) confidence -= 0.3;

            setResult({
                predictedPrice: basePredictedPrice,
                confidence: Math.max(0.1, confidence),
                zScore: 0,
                trend: 'stable'
            });

        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Effect to update price when Bulk Selection changes

    // Derived display price
    const displayPrice = useMemo(() => {
        if (!result) return 0;

        // Base unit price (mean of market)
        let price = result.predictedPrice;

        // If we selected a bulk, we want the Total Price for that bulk.
        if (selectedBulk > 1) {
            price = price * selectedBulk;

            // Apply discount factor if available?
            // If 1000x items usually trade at 0.5 unit price of singles, 
            // and our mean is somewhat between, applying the factor might double count if mean is low.
            // Let's stick to linear for safety unless we split the dataset.
        }
        return price;
    }, [result, selectedBulk]);


    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in pb-12">
            <div className="text-center space-y-2">
                <div className="inline-flex p-4 bg-purple-500/10 rounded-full mb-2">
                    <BrainCircuit className="w-10 h-10 text-purple-400" />
                </div>
                <h2 className="text-3xl font-bold text-white">Price Predictor Engine</h2>
                <p className="text-slate-400">
                    Statistical inference based on <span className="text-emerald-400 font-mono">{data.length}</span> records.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Input Section */}
                <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Filter className="w-5 h-5 text-purple-400" />
                        <h3 className="text-xl font-semibold text-white">Prediction Context</h3>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Item Name</label>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <input
                                type="text"
                                list="item-suggestions"
                                placeholder="e.g., Stone Brick (ignores '1k')"
                                value={itemName}
                                onChange={(e) => setItemName(e.target.value)}
                                className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-3 py-3 text-white focus:ring-2 focus:ring-purple-500/50 outline-none placeholder:text-slate-600"
                            />
                            <datalist id="item-suggestions">
                                {availableItemNames.slice(0, 50).map((name, i) => (
                                    <option key={i} value={name} />
                                ))}
                            </datalist>
                        </div>
                        <p className="text-xs text-slate-500">Type to search existing items in your database.</p>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Material / Type</label>
                        <select
                            value={material}
                            onChange={(e) => setMaterial(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500/50 outline-none custom-select"
                        >
                            <option value="Any">Any Material</option>
                            {availableMaterials.map(m => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                    </div>

                    {/* BULK SELECTOR (New) */}
                    {showBulks && bulkAnalysis && (
                        <BulkSelector
                            analysis={bulkAnalysis}
                            selected={selectedBulk}
                            onSelect={setSelectedBulk}
                        />
                    )}

                    <div className="space-y-4 pt-2 border-t border-slate-700/50">
                        <div className="flex justify-between">
                            <label className="text-sm font-medium text-slate-300">Target Quality (QL)</label>
                            <span className="text-sm font-bold text-purple-400">{quality}ql</span>
                        </div>
                        <input
                            type="range"
                            min="1"
                            max="100"
                            value={quality}
                            onChange={(e) => setQuality(parseInt(e.target.value))}
                            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                        />
                    </div>

                    <button
                        onClick={handlePredict}
                        disabled={loading || data.length === 0}
                        className="w-full py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-purple-900/20"
                    >
                        {loading ? <Loader2 className="animate-spin w-5 h-5" /> : 'Calculate Fair Price'}
                    </button>
                </div>

                {/* Results Section */}
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-amber-600 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                    <div className="relative h-full bg-slate-900 border border-slate-700 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-6">
                        {!result && !loading && (
                            <div className="text-slate-500 space-y-4">
                                <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto mb-4 border border-slate-700">
                                    <TrendingUp className="w-8 h-8 opacity-20" />
                                </div>
                                <h4 className="text-lg font-medium text-slate-300">Ready to Predict</h4>
                                <p className="text-sm max-w-xs mx-auto">
                                    Select an item to analyze historical trends and calculate a fair market value.
                                </p>
                            </div>
                        )}

                        {loading && (
                            <div className="text-slate-500 space-y-4">
                                <Loader2 className="w-12 h-12 mx-auto animate-spin text-purple-500" />
                                <p className="animate-pulse">Analyzing {data.length.toLocaleString()} records...</p>
                            </div>
                        )}

                        {result && (
                            <>
                                <div className="space-y-2">
                                    <div className="text-xs text-purple-400 font-bold uppercase tracking-wider">
                                        {selectedBulk > 1 ? `Estimated Batch Value (${selectedBulk}x)` : 'Estimated Unit Value'}
                                    </div>
                                    <div className="text-5xl font-bold text-white tracking-tight flex items-baseline justify-center gap-2">
                                        <span dangerouslySetInnerHTML={{ __html: formatWurmPrice(displayPrice).replace(/([0-9]+)([gsc])/g, '<span class="text-white">$1</span><span class="text-slate-500 text-2xl ml-0.5 mr-2">$2</span>').replace(/(\d+)i/, '<span class="text-slate-300 text-3xl">$1i</span>') }} />
                                    </div>
                                    <div className="text-xs text-slate-500 bg-slate-800 py-1 px-3 rounded-full inline-block">
                                        Based on {marketStats?.sampleSize} similar trades
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 w-full mt-6">
                                    <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700 hover:border-slate-600 transition-colors">
                                        <div className="flex items-center justify-center gap-2 text-xs text-slate-400 mb-2">
                                            <TrendingUp className="w-3 h-3" /> Confidence
                                        </div>
                                        <div className={`text-xl font-bold ${result.confidence > 0.7 ? 'text-emerald-400' : 'text-amber-400'}`}>
                                            {(result.confidence * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                    <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700 hover:border-slate-600 transition-colors">
                                        <div className="flex items-center justify-center gap-2 text-xs text-slate-400 mb-2">
                                            <TrendingDown className="w-3 h-3" /> Volatility
                                        </div>
                                        <div className="text-xl font-bold text-slate-300">
                                            {marketStats ? formatWurmPrice(marketStats.volatility) : '-'}
                                        </div>
                                    </div>
                                </div>

                                {marketStats && (
                                    <div className="w-full pt-6 border-t border-slate-800/50 text-left space-y-3">
                                        <h5 className="text-xs font-semibold text-slate-500 uppercase">Historical Unit Range</h5>
                                        <div className="relative h-2 bg-slate-800 rounded-full w-full overflow-hidden">
                                            <div className="absolute top-0 bottom-0 bg-slate-600 rounded-full" style={{ left: '10%', right: '10%' }}></div>
                                            <div className="absolute top-0 bottom-0 bg-purple-500 w-1 h-2" style={{ left: '50%' }} title="Mean"></div>
                                        </div>
                                        <div className="flex justify-between text-xs font-mono text-slate-400">
                                            <span>{formatWurmPrice(marketStats.min)}</span>
                                            <span>{formatWurmPrice(marketStats.max)}</span>
                                        </div>
                                    </div>
                                )}

                                {marketStats?.sampleSize < 5 && (
                                    <div className="mt-4 flex items-start gap-3 text-left text-xs text-amber-400 bg-amber-900/20 p-3 rounded-lg border border-amber-900/30">
                                        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                                        <span>
                                            <b>Low Data Warning:</b> Only found {marketStats.sampleSize} records.
                                            Prediction accuracy may be low.
                                        </span>
                                    </div>
                                )}
                            </>
                        )}

                        {!result && !loading && marketStats === null && itemName && (
                            <div className="flex flex-col items-center gap-2 text-rose-400 text-sm mt-4 p-4 bg-rose-500/10 rounded-xl border border-rose-500/20">
                                <Search className="w-5 h-5" />
                                <span>No trades found for "<b>{itemName}</b>" with material "<b>{material}</b>".</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Relevant Trades Table */}
            {relevantTrades.length > 0 && (
                <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden mt-8">
                    <div className="p-4 bg-slate-800/80 border-b border-slate-700 flex justify-between items-center">
                        <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
                            <Layers className="w-4 h-4 text-purple-400" />
                            Analysis Source Data (Top 20)
                        </h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs">
                            <thead className="bg-slate-900 text-slate-500 uppercase tracking-wider">
                                <tr>
                                    <th className="p-3">Item</th>
                                    <th className="p-3 text-center">Qty (Bulk)</th>
                                    <th className="p-3">Unit Price</th>
                                    <th className="p-3">Bulk Price (1k)</th>
                                    <th className="p-3">Seller</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-700/50">
                                {relevantTrades.map(t => (
                                    <tr key={t.id} className="hover:bg-slate-700/30">
                                        <td className="p-3 text-white">{t.name}</td>
                                        <td className="p-3 text-center">
                                            {t.quantity > 1 ? (
                                                <div className="flex flex-col items-center gap-1">
                                                    <span className="bg-purple-500/10 text-purple-300 px-1.5 py-0.5 rounded border border-purple-500/20 font-mono">
                                                        {t.quantity}
                                                    </span>
                                                    <span className="text-[10px] text-slate-500">
                                                        {formatWurmPrice(t.price)}/u
                                                    </span>
                                                </div>
                                            ) : '-'}
                                        </td>
                                        <td className="p-3">
                                            <span dangerouslySetInnerHTML={{ __html: formatWurmPrice(t.price) }} />
                                        </td>
                                        <td className="p-3 font-mono text-emerald-400">
                                            {formatWurmPrice(t.price * 1000)}
                                        </td>
                                        <td className="p-3 text-slate-400">{t.seller}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};
