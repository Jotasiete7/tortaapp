import { useState, useEffect } from 'react';

type Language = 'en' | 'pt';

interface Translations {
    [key: string]: {
        en: string;
        pt: string;
    };
}

export const chartsTranslations: Translations = {
    // Header & General
    'charts_engine': { en: 'Charts Engine', pt: 'Charts Engine' },
    'market_trends': { en: 'Market Trends', pt: 'Tendências de Mercado' },
    'analyze_text': { en: 'Analyze price history and supply distribution per item.', pt: 'Analise histórico de preços e distribuição de supply por item.' },
    'select_item': { en: 'Select Item to Analyze...', pt: 'Selecione um Item para Analisar...' },
    'search_placeholder': { en: 'Search items... (fuzzy search enabled)', pt: 'Buscar itens... (busca inteligente)' },

    // Help & Guide
    'user_guide': { en: 'User Guide', pt: 'Guia do Usuário' },
    'help': { en: 'Help', pt: 'Ajuda' },
    'guide_intro_title': { en: 'Welcome to Charts Engine', pt: 'Bem-vindo ao Charts Engine' },
    'guide_intro_desc': { en: 'Your professional market intelligence platform.', pt: 'Sua plataforma profissional de inteligência de mercado.' },

    // Volatility
    'volatility': { en: 'Volatility', pt: 'Volatilidade' },
    'vol_score': { en: 'Volatility Score', pt: 'Score de Volatilidade' },
    'stable': { en: 'Stable', pt: 'Estável' },
    'moderate': { en: 'Moderate', pt: 'Moderada' },
    'volatile': { en: 'Volatile', pt: 'Volátil' },
    'rising': { en: 'Rising', pt: 'Subindo' },
    'falling': { en: 'Falling', pt: 'Caindo' },

    // Charts
    'line_chart': { en: 'Line Chart', pt: 'Gráfico de Linha' },
    'candlestick': { en: 'Candlestick', pt: 'Candlestick' },
    'heatmap': { en: 'Supply Heatmap', pt: 'Mapa de Calor' },
    'price_history': { en: 'Price History', pt: 'Histórico de Preços' },
    'supply_density': { en: 'Supply Density', pt: 'Densidade de Supply' },

    // Market Health
    'market_health': { en: 'Market Health', pt: 'Saúde do Mercado' },
    'volume_24h': { en: '24h Volume', pt: 'Volume 24h' },
    'volume_7d': { en: '7d Volume', pt: 'Volume 7d' },
    'change_7d': { en: '7d Change', pt: 'Var. 7d' },
    'top_gainers': { en: 'Top Gainers', pt: 'Maiores Altas' },
    'top_losers': { en: 'Top Losers', pt: 'Maiores Baixas' },
    'most_active': { en: 'Most Active', pt: 'Mais Ativos' },
    'market_pulse': { en: 'Market Pulse', pt: 'Pulso do Mercado' },

    // Seller Insights
    'seller_insights': { en: 'Seller Insights', pt: 'Análise de Vendedores' },
    'top_sellers': { en: 'Top Sellers', pt: 'Top Vendedores' },
    'market_share': { en: 'Market Share', pt: 'Fatia de Mercado' },
    'activity_score': { en: 'Activity Score', pt: 'Pontuação de Atividade' },
    'concentration': { en: 'Concentration', pt: 'Concentração' },
    'strategy': { en: 'Strategy', pt: 'Estratégia' },

    // Prediction
    'price_forecast': { en: 'Price Forecast', pt: 'Previsão de Preço' },
    'predicted': { en: 'Predicted', pt: 'Previsto' },
    'current': { en: 'Current', pt: 'Atual' },
    'confidence': { en: 'Confidence', pt: 'Confiança' },
    'trend': { en: 'Trend', pt: 'Tendência' },
    'forecast_disclaimer': { en: 'Predictions based on historical data.', pt: 'Previsões baseadas em dados históricos.' },

    // Search
    'recent_searches': { en: 'Recent Searches', pt: 'Buscas Recentes' },
    'popular_items': { en: 'Popular Items', pt: 'Itens Populares' },
    'no_results': { en: 'No items found', pt: 'Nenhum item encontrado' },
    'try_different': { en: 'Try a different search term', pt: 'Tente outro termo' },
    'clear': { en: 'Clear', pt: 'Limpar' },
    'search_results': { en: 'Search Results', pt: 'Resultados da Busca' },

    // Categories
    'cat_bricks': { en: 'Bricks', pt: 'Tijolos' },
    'cat_wood': { en: 'Wood', pt: 'Madeira' },
    'cat_metals': { en: 'Metals', pt: 'Metais' },
    'cat_stone': { en: 'Stone', pt: 'Pedra' },
    'cat_hardware': { en: 'Hardware', pt: 'Ferragens' },
    'cat_tools': { en: 'Tools', pt: 'Ferramentas' },
    'cat_ores': { en: 'Ores', pt: 'Minérios' },
    'cat_clay': { en: 'Clay', pt: 'Argila' },
    'cat_other': { en: 'Other', pt: 'Outros' }
};

export const useChartsTranslation = () => {
    // Default to 'en' but try to detect from context or localStorage
    const [language, setLanguage] = useState<Language>('pt'); // Defaulting to PT as requested

    const t = (key: string): string => {
        const entry = chartsTranslations[key];
        if (!entry) return key;
        return entry[language] || entry['en'];
    };

    const toggleLanguage = () => {
        setLanguage(prev => prev === 'en' ? 'pt' : 'en');
    };

    return { t, language, setLanguage, toggleLanguage };
};

export const InfoTooltip = ({ text }: { text: string }) => {
    // Implementation placeholder - handled by main component
    return null;
};
