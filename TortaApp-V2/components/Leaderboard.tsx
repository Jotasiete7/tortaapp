import React, { useEffect, useState } from 'react';
import { Trophy, TrendingUp, User, Activity } from 'lucide-react';
import { IntelligenceService, TraderProfile } from '../services/intelligence';

interface LeaderboardProps {
    onPlayerSelect?: (nick: string) => void;
}

export const Leaderboard: React.FC<LeaderboardProps> = ({ onPlayerSelect }) => {
    const [traders, setTraders] = useState<TraderProfile[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadLeaderboard();
    }, []);

    const loadLeaderboard = async () => {
        try {
            const data = await IntelligenceService.getTopTraders(5);
            setTraders(data);
        } catch (error) {
            console.error("Failed to load leaderboard", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="p-4 text-slate-400 text-sm animate-pulse">Loading market intelligence...</div>;
    }

    if (traders.length === 0) {
        return <div className="p-4 text-slate-500 text-sm">No market data available yet. Upload logs to see rankings.</div>;
    }

    return (
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-900/50">
                <h3 className="font-bold text-white flex items-center gap-2">
                    <Trophy className="w-4 h-4 text-amber-500" />
                    Top Market Movers
                </h3>
                <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded border border-slate-700">
                    Live Data
                </span>
            </div>

            <div className="divide-y divide-slate-700/50">
                {traders.map((trader, index) => (
                    <div
                        key={trader.nick}
                        onClick={() => onPlayerSelect && onPlayerSelect(trader.nick)}
                        className={`
                            p-4 flex items-center justify-between transition-colors group
                            ${onPlayerSelect ? 'cursor-pointer hover:bg-slate-700/50' : ''}
                        `}
                    >
                        <div className="flex items-center gap-3">
                            <div className={`
                                w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm
                                ${index === 0 ? 'bg-amber-500/20 text-amber-500 border border-amber-500/50' :
                                    index === 1 ? 'bg-slate-400/20 text-slate-300 border border-slate-400/50' :
                                        index === 2 ? 'bg-orange-700/20 text-orange-400 border border-orange-700/50' :
                                            'bg-slate-800 text-slate-500'}
                            `}>
                                {index + 1}
                            </div>
                            <div>
                                <p className="text-sm font-medium text-slate-200 group-hover:text-white transition-colors flex items-center gap-2">
                                    {trader.nick.charAt(0).toUpperCase() + trader.nick.slice(1)}
                                    {onPlayerSelect && <User className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity text-amber-500" />}
                                </p>
                                <p className="text-xs text-slate-500 flex items-center gap-1">
                                    <Activity className="w-3 h-3" />
                                    Last seen {new Date(trader.last_seen).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-sm font-bold text-emerald-400">
                                {trader.total_trades.toLocaleString()}
                            </p>
                            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Trades</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
