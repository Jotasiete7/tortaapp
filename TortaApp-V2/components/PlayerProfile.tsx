import React, { useEffect, useState } from 'react';
import {
    Trophy, TrendingUp, User, Activity, Calendar,
    ShoppingCart, Tag, Hash, Clock, ArrowLeft, Server
} from 'lucide-react';
import { ServerIcon } from './ServerIcon';
import {
    IntelligenceService,
    PlayerStatsAdvanced,
    PlayerLog,
    ActivityPoint
} from '../services/intelligence';

interface PlayerProfileProps {
    nick: string;
    onBack: () => void;
}

export const PlayerProfile: React.FC<PlayerProfileProps> = ({ nick, onBack }) => {
    const [stats, setStats] = useState<PlayerStatsAdvanced | null>(null);
    const [logs, setLogs] = useState<PlayerLog[]>([]);
    const [activity, setActivity] = useState<ActivityPoint[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'history'>('overview');

    useEffect(() => {
        loadProfileData();
    }, [nick]);

    const loadProfileData = async () => {
        setLoading(true);
        try {
            const [statsData, logsData, activityData] = await Promise.all([
                IntelligenceService.getPlayerStatsAdvanced(nick),
                IntelligenceService.getPlayerLogs(nick, 20), // Last 20 logs
                IntelligenceService.getPlayerActivity(nick)
            ]);

            setStats(statsData);
            setLogs(logsData);
            setActivity(activityData);
        } catch (error) {
            console.error("Failed to load player profile", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
            </div>
        );
    }

    if (!stats) {
        return (
            <div className="text-center p-8 text-slate-400">
                <p>Player not found.</p>
                <button onClick={onBack} className="mt-4 text-amber-500 hover:underline">Go Back</button>
            </div>
        );
    }

    // Determine Prestige Title based on stats
    const getTitle = () => {
        if (stats.rank_position <= 3) return "Market Mogul";
        if (stats.total > 1000) return "Trade Veteran";
        if (stats.wts_count > stats.wtb_count * 2) return "Master Merchant";
        if (stats.wtb_count > stats.wts_count * 2) return "Big Spender";
        if (stats.pc_count > 50) return "Oracle of Prices";
        return "Adventurer";
    };

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header / Navigation */}
            <button
                onClick={onBack}
                className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-2"
            >
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
            </button>

            {/* 1. Prestige Section */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Trophy className="w-32 h-32 text-amber-500" />
                </div>

                <div className="flex flex-col md:flex-row items-start md:items-center gap-6 relative z-10">
                    <div className="w-20 h-20 rounded-full bg-slate-700 border-2 border-amber-500 flex items-center justify-center text-3xl font-bold text-amber-500">
                        {stats.nick.charAt(0).toUpperCase()}
                    </div>

                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                            <h1 className="text-3xl font-bold text-white capitalize">{stats.nick}</h1>
                            <span className="bg-amber-500/20 text-amber-500 text-xs px-2 py-1 rounded border border-amber-500/50 font-medium">
                                {getTitle()}
                            </span>
                        </div>

                        <div className="flex flex-wrap gap-4 text-sm text-slate-400">
                            <div className="flex items-center gap-1">
                                <ServerIcon server={stats.fav_server || 'Unknown'} className="text-base" />
                                <span className="font-bold ml-1">
                                    {(() => {
                                        const s = (stats.fav_server || '').toLowerCase();
                                        if (s.includes('har')) return 'Harmony';
                                        if (s.includes('mel')) return 'Melody';
                                        if (s.includes('cad')) return 'Cadence';
                                        return stats.fav_server || 'Unknown';
                                    })()}
                                </span>
                            </div>
                            <div className="flex items-center gap-1">
                                <Hash className="w-4 h-4 text-slate-500" />
                                Rank #{stats.rank_position}
                            </div>
                            <div className="flex items-center gap-1">
                                <Clock className="w-4 h-4 text-slate-500" />
                                Last seen {new Date(stats.last_seen).toLocaleDateString()}
                            </div>
                        </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="flex gap-4">
                        <div className="text-center p-3 bg-slate-900/50 rounded-lg border border-slate-700">
                            <p className="text-2xl font-bold text-white">{stats.total}</p>
                            <p className="text-xs text-slate-500 uppercase">Total Trades</p>
                        </div>
                        <div className="text-center p-3 bg-slate-900/50 rounded-lg border border-slate-700">
                            <p className="text-2xl font-bold text-emerald-400">{stats.wts_count}</p>
                            <p className="text-xs text-slate-500 uppercase">Sales</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-4 border-b border-slate-700">
                <button
                    onClick={() => setActiveTab('overview')}
                    className={`pb-3 px-1 text-sm font-medium transition-colors ${activeTab === 'overview'
                        ? 'text-amber-500 border-b-2 border-amber-500'
                        : 'text-slate-400 hover:text-white'
                        }`}
                >
                    Overview & Metrics
                </button>
                <button
                    onClick={() => setActiveTab('history')}
                    className={`pb-3 px-1 text-sm font-medium transition-colors ${activeTab === 'history'
                        ? 'text-amber-500 border-b-2 border-amber-500'
                        : 'text-slate-400 hover:text-white'
                        }`}
                >
                    Trade History
                </button>
            </div>

            {/* 2. Metrics Section */}
            {activeTab === 'overview' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Activity Card */}
                    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 col-span-2">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-blue-500" />
                            Activity Heatmap
                        </h3>
                        <div className="h-48 flex items-end gap-1 pb-2 border-b border-slate-700/50">
                            {(() => {
                                // Generate last 30 days
                                const days = Array.from({ length: 30 }, (_, i) => {
                                    const d = new Date();
                                    d.setDate(d.getDate() - (29 - i));
                                    d.setHours(0, 0, 0, 0);
                                    return d;
                                });

                                // Map activity to days
                                const chartData = days.map(day => {
                                    const point = activity.find(a => {
                                        const aDate = new Date(a.activity_date);
                                        // Fix timezone offset issues by comparing ISO strings prefix
                                        return aDate.toISOString().split('T')[0] === day.toISOString().split('T')[0];
                                    });
                                    return {
                                        date: day,
                                        count: point ? point.trade_count : 0
                                    };
                                });

                                const maxCount = Math.max(...chartData.map(d => d.count), 10); // Min max scale of 10

                                return chartData.map((point, i) => {
                                    const height = Math.max(4, (point.count / maxCount) * 100); // Min height 4%
                                    const isZero = point.count === 0;

                                    return (
                                        <div key={i} className="flex-1 flex flex-col justify-end group relative h-full">
                                            <div
                                                className={`
                                                    transition-all rounded-t-sm min-w-[2px] mx-0.5
                                                    ${isZero ? 'bg-slate-700/30 hover:bg-slate-700/50' : 'bg-blue-500 hover:bg-blue-400'}
                                                `}
                                                style={{ height: `${isZero ? 100 : height}%`, opacity: isZero ? 0.2 : 1 }}
                                            ></div>
                                            {/* Tooltip */}
                                            <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover:block bg-slate-900 text-xs text-white p-2 rounded border border-slate-700 whitespace-nowrap z-20 shadow-xl">
                                                <p className="font-bold">{point.date.toLocaleDateString()}</p>
                                                <p className="text-slate-400">{point.count} trades</p>
                                            </div>
                                        </div>
                                    );
                                });
                            })()}
                        </div>
                        <div className="flex justify-between text-xs text-slate-500 mt-2">
                            <span>30 days ago</span>
                            <span>Today</span>
                        </div>
                    </div>

                    {/* Breakdown Card */}
                    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Tag className="w-5 h-5 text-purple-500" />
                            Trade Breakdown
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-300">Selling (WTS)</span>
                                    <span className="text-white font-medium">
                                        {stats.total > 0 ? Math.round((stats.wts_count / stats.total) * 100) : 0}%
                                    </span>
                                </div>
                                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                    <div className="h-full bg-emerald-500" style={{ width: `${stats.total > 0 ? (stats.wts_count / stats.total) * 100 : 0}%` }}></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-300">Buying (WTB)</span>
                                    <span className="text-white font-medium">
                                        {stats.total > 0 ? Math.round((stats.wtb_count / stats.total) * 100) : 0}%
                                    </span>
                                </div>
                                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                    <div className="h-full bg-blue-500" style={{ width: `${stats.total > 0 ? (stats.wtb_count / stats.total) * 100 : 0}%` }}></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-300">Price Checks (PC)</span>
                                    <span className="text-white font-medium">
                                        {stats.total > 0 ? Math.round((stats.pc_count / stats.total) * 100) : 0}%
                                    </span>
                                </div>
                                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                    <div className="h-full bg-amber-500" style={{ width: `${stats.total > 0 ? (stats.pc_count / stats.total) * 100 : 0}%` }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* 3. History Section */}
            {activeTab === 'history' && (
                <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
                    <div className="p-4 border-b border-slate-700 bg-slate-900/30">
                        <h3 className="font-semibold text-white">Recent Logs</h3>
                    </div>
                    <div className="divide-y divide-slate-700/50">
                        {logs.map((log) => (
                            <div key={log.id} className="p-4 hover:bg-slate-700/30 transition-colors">
                                <div className="flex justify-between items-start mb-1">
                                    <span className={`
                                        text-xs font-bold px-2 py-0.5 rounded border
                                        ${log.trade_type === 'WTS' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' :
                                            log.trade_type === 'WTB' ? 'bg-blue-500/20 text-blue-400 border-blue-500/50' :
                                                'bg-amber-500/20 text-amber-400 border-amber-500/50'}
                                    `}>
                                        {log.trade_type}
                                    </span>
                                    <span className="text-xs text-slate-500">
                                        {new Date(log.trade_timestamp_utc).toLocaleString()}
                                    </span>
                                </div>
                                <p className="text-slate-300 text-sm mt-2 font-mono">{log.message}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

