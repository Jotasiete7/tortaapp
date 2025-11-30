
import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { MarketTable } from './components/MarketTable';
import { ChartsView } from './components/ChartsView';
import { MLPredictor } from './components/MLPredictor';
import { PriceManager } from './components/PriceManager';
import { ViewState, MarketItem, ChartDataPoint, Language } from './types';
import { parseTradeFile } from './services/fileParser';
import { generateChartDataFromHistory } from './services/dataUtils';
import { parsePriceCSV, loadPricesFromStorage, savePricesToStorage } from './services/priceUtils';
import { DEFAULT_PRICES_CSV } from './services/defaultPrices';
import { translations } from './services/i18n';
import { Globe } from 'lucide-react';

const App: React.FC = () => {
    const [currentView, setCurrentView] = useState<ViewState>(ViewState.DASHBOARD);
    const [marketData, setMarketData] = useState<MarketItem[]>([]);
    const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
    const [referencePrices, setReferencePrices] = useState<Record<string, number>>({});
    const [loading, setLoading] = useState(false);
    const [language, setLanguage] = useState<Language>('en');

    const [isProcessingFile, setIsProcessingFile] = useState(false);
    const [dataSource, setDataSource] = useState<'NONE' | 'FILE'>('NONE');

    // Load Prices on Mount (Storage -> Default)
    useEffect(() => {
        try {
            const stored = loadPricesFromStorage();
            if (stored && Object.keys(stored).length > 0) {
                setReferencePrices(stored);
                console.log(`Loaded ${Object.keys(stored).length} prices from LocalStorage.`);
            } else {
                const defaults = parsePriceCSV(DEFAULT_PRICES_CSV);
                setReferencePrices(defaults);
                console.log(`Loaded ${Object.keys(defaults).length} default prices.`);
            }
        } catch (e) {
            console.error("Failed to load prices", e);
        }
    }, []);

    // Wrapper to update prices AND save to storage
    const handleUpdatePrices = (newPrices: Record<string, number>) => {
        setReferencePrices(newPrices);
        savePricesToStorage(newPrices);
    };

    const handleFileUpload = async (file: File) => {
        // RESET STATE before processing new file to clear any "bad" cache
        setMarketData([]);
        setChartData([]);

        setIsProcessingFile(true);
        setLoading(true);
        try {
            // 1. Parse File
            const parsedData = await parseTradeFile(file);

            if (parsedData.length > 0) {
                setMarketData(parsedData);
                setDataSource('FILE');

                // 2. Generate Charts from Real Data
                const realCharts = generateChartDataFromHistory(parsedData);
                setChartData(realCharts);

                // Switch to market view to see the data immediately
                setCurrentView(ViewState.MARKET);
                alert(`Successfully imported ${parsedData.length.toLocaleString()} trade records.`);
            } else {
                alert("File appears empty or unrecognized format.");
            }
        } catch (error) {
            console.error("Failed to parse file:", error);
            alert("Error parsing file. See console for details.");
        } finally {
            setIsProcessingFile(false);
            setLoading(false);
        }
    };

    const renderContent = () => {
        const t = translations[language];

        if (loading) {
            return (
                <div className="flex h-[80vh] items-center justify-center flex-col gap-4">
                    <div className="w-16 h-16 border-4 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                    <div className="text-slate-400 animate-pulse">{t.processing}</div>
                </div>
            )
        }

        switch (currentView) {
            case ViewState.DASHBOARD:
                return (
                    <Dashboard
                        onFileUpload={handleFileUpload}
                        isProcessing={isProcessingFile}
                        marketData={marketData}
                        language={language}
                    />
                );
            case ViewState.MARKET:
                return <MarketTable data={marketData} referencePrices={referencePrices} />;
            case ViewState.ANALYTICS:
                // Pass raw marketData for the new granular charts
                return <ChartsView data={chartData} rawItems={marketData} />;
            case ViewState.PREDICTOR:
                return <MLPredictor data={marketData} />;
            case ViewState.PRICEMANAGER:
                return <PriceManager prices={referencePrices} onUpdatePrices={handleUpdatePrices} />;
            case ViewState.SETTINGS:
                return (
                    <div className="flex flex-col items-center justify-start h-full text-slate-500 pt-12 animate-fade-in">
                        <div className="bg-slate-800 p-8 rounded-xl border border-slate-700 w-full max-w-md shadow-lg">
                            <div className="text-center mb-8">
                                <h2 className="text-2xl font-bold text-white mb-2">{t.appSettings}</h2>
                                <div className="text-sm font-mono text-slate-600">v2.2.0</div>
                            </div>

                            <div className="space-y-6">
                                {/* Language Switcher */}
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                                        <Globe className="w-4 h-4 text-amber-500" />
                                        {t.language}
                                    </label>
                                    <div className="grid grid-cols-2 gap-2 bg-slate-900 p-1 rounded-lg border border-slate-700">
                                        <button
                                            onClick={() => setLanguage('en')}
                                            className={`py-2 text-sm font-medium rounded-md transition-all ${language === 'en' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
                                        >
                                            English
                                        </button>
                                        <button
                                            onClick={() => setLanguage('pt')}
                                            className={`py-2 text-sm font-medium rounded-md transition-all ${language === 'pt' ? 'bg-amber-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
                                        >
                                            Português
                                        </button>
                                    </div>
                                </div>

                                <div className="pt-6 border-t border-slate-700 space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span>{t.dataSource}:</span>
                                        <span className={`font-mono font-bold ${dataSource === 'FILE' ? 'text-emerald-400' : 'text-slate-400'}`}>
                                            {dataSource}
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span>{t.version}:</span>
                                        <span className="text-slate-400">2.2.0</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                );
            default:
                return (
                    <Dashboard
                        onFileUpload={handleFileUpload}
                        isProcessing={isProcessingFile}
                        marketData={marketData}
                        language={language}
                    />
                );
        }
    };

    return (
        <div className="min-h-screen bg-slate-900 text-slate-200 font-sans">
            <Sidebar currentView={currentView} onNavigate={setCurrentView} language={language} />

            <main className="ml-64 p-8 min-h-screen transition-all duration-300">
                <header className="flex justify-between items-center mb-8 pb-6 border-b border-slate-800">
                    <div className="flex items-center gap-4">
                        {dataSource === 'FILE' ? (
                            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-bold rounded-full border border-emerald-500/30 animate-fade-in">
                                LIVE FILE DATA
                            </span>
                        ) : (
                            <span className="px-3 py-1 bg-slate-700 text-slate-400 text-xs font-bold rounded-full border border-slate-600">
                                NO DATA LOADED
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="text-right hidden sm:block">
                            <div className="text-sm font-medium text-white">Admin User</div>
                            <div className="text-xs text-slate-400">Connected to Localhost:8000</div>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-sm font-bold text-white shadow-md">
                            AU
                        </div>
                    </div>
                </header>

                {renderContent()}
            </main>
        </div>
    );
};

export default App;
