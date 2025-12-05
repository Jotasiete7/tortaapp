import React, { useEffect, useState } from 'react';
import { BadgeService } from '../../services/badgeService';
import { Badge } from '../../types';
import { Shield, Award, Star, Heart, TrendingUp, Gift, Beaker, X, Scroll, Calculator, Clock } from 'lucide-react';
import { emojiService } from '../../services/emojiService';

interface GamificationRulesProps {
    isOpen: boolean;
    onClose: () => void;
    userEarnedBadgeIds: string[]; // IDs of badges the user already has
}

// Reuse Icon Map
const IconMap: Record<string, React.ElementType> = {
    Shield, Award, Star, Heart, TrendingUp, Gift, Beaker
};

const BADGE_TO_EMOJI: Record<string, string> = {
    'Shield': '🛡️',
    'Award': '🎖️',
    'Star': '🌟',
    'Heart': '💜',
    'Gift': '🎁',
    'Beaker': '🧪',
    'TrendingUp': '📈',
    'Trophy': '🏆'
};

const LEVEL_TABLE = [
    { level: 1, name: 'Novice', range: '0 - 50 Trades' },
    { level: 2, name: 'Apprentice', range: '50 - 150 Trades' },
    { level: 3, name: 'Merchant', range: '150 - 500 Trades' },
    { level: 4, name: 'Veteran', range: '500 - 1,000 Trades' },
    { level: 5, name: 'Tycoon', range: '1,000+ Trades' }
];

const XP_ACTIONS = [
    { action: 'Sell Item (WTS)', xp: '+10 XP' },
    { action: 'Buy Item (WTB)', xp: '+10 XP' },
    { action: 'Price Check', xp: '+10 XP' },
    { action: 'Daily Login', xp: '+0 XP (Soon)' }
];

export const GamificationRules: React.FC<GamificationRulesProps> = ({ isOpen, onClose, userEarnedBadgeIds }) => {
    const [badges, setBadges] = useState<Badge[]>([]);
    const [loading, setLoading] = useState(true);
    const [emojisReady, setEmojisReady] = useState(false);

    useEffect(() => {
        if (isOpen) {
            loadData();
            emojiService.loadEmojis().then(() => setEmojisReady(true));
        }
    }, [isOpen]);

    const loadData = async () => {
        setLoading(true);
        const allBadges = await BadgeService.getAllBadges();
        setBadges(allBadges);
        setLoading(false);
    };

    const renderIcon = (iconName: string) => {
        const emojiChar = BADGE_TO_EMOJI[iconName];
        if (emojiChar && emojisReady) {
            const emojiData = emojiService.getEmoji(emojiChar);
            if (emojiData) {
                return <img src={emojiData.path} alt={iconName} className="w-8 h-8 object-contain" />;
            }
        }
        const Icon = IconMap[iconName] || Star;
        return <Icon className="w-8 h-8" />;
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fade-in">
            <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-4xl shadow-2xl flex flex-col max-h-[90vh]">
                
                {/* Header */}
                <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-950/50 rounded-t-xl">
                    <div>
                        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                            <Scroll className="w-6 h-6 text-amber-500" />
                            Rules & Compendium
                        </h2>
                        <p className="text-slate-400 text-sm mt-1">
                            Everything about XP, Levels, and Badges.
                        </p>
                    </div>
                    <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors p-2 hover:bg-slate-800 rounded-lg">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content - Scrollable */}
                <div className="flex-1 overflow-y-auto p-6 custom-scrollbar space-y-8">
                    
                    {/* SECTION 1: XP & LEVELS */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Level Table */}
                        <div className="bg-slate-800/50 rounded-xl p-5 border border-slate-700">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-emerald-400" />
                                Career Ladder
                            </h3>
                            <div className="overflow-hidden rounded-lg border border-slate-700/50">
                                <table className="w-full text-sm text-left">
                                    <thead className="bg-slate-900 text-slate-400 uppercase text-xs">
                                        <tr>
                                            <th className="px-4 py-3">Lvl</th>
                                            <th className="px-4 py-3">Title</th>
                                            <th className="px-4 py-3">Requirement</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-700/50">
                                        {LEVEL_TABLE.map((lvl) => (
                                            <tr key={lvl.level} className="hover:bg-slate-700/20 transition-colors">
                                                <td className="px-4 py-3 font-mono text-amber-500 font-bold">{lvl.level}</td>
                                                <td className="px-4 py-3 font-medium text-white">{lvl.name}</td>
                                                <td className="px-4 py-3 text-slate-300">{lvl.range}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* XP Actions */}
                        <div className="bg-slate-800/50 rounded-xl p-5 border border-slate-700">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <Calculator className="w-5 h-5 text-blue-400" />
                                Earning XP
                            </h3>
                            <div className="space-y-3">
                                {XP_ACTIONS.map((action, i) => (
                                    <div key={i} className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg border border-slate-700/30">
                                        <span className="text-slate-300">{action.action}</span>
                                        <span className="font-mono text-emerald-400 font-bold bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-500/20">
                                            {action.xp}
                                        </span>
                                    </div>
                                ))}
                                <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-200 mt-4 flex gap-2">
                                    <Clock className="w-4 h-4 flex-shrink-0" />
                                    xp updates are processed every ~5 minutes or on page refresh.
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* SECTION 2: BADGE COMPENDIUM */}
                    <div>
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2 border-b border-slate-700 pb-2">
                            <Award className="w-6 h-6 text-purple-400" />
                            Badge Compendium
                        </h3>
                        
                        {loading ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 animate-pulse">
                                {[1,2,3,4,5,6].map(i => (
                                    <div key={i} className="h-24 bg-slate-800 rounded-xl"></div>
                                ))}
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                {badges.map((badge) => {
                                    const isEarned = userEarnedBadgeIds.includes(badge.id);
                                    
                                    return (
                                        <div 
                                            key={badge.id}
                                            className={`
                                                relative p-4 rounded-xl border flex items-start gap-4 transition-all
                                                ${isEarned 
                                                    ? 'bg-slate-800 border-slate-600 shadow-lg' 
                                                    : 'bg-slate-900/50 border-slate-800 opacity-60 grayscale hover:grayscale-0 hover:opacity-100'}
                                            `}
                                        >
                                            <div className={`
                                                p-3 rounded-full flex-shrink-0
                                                ${isEarned ? `bg-${badge.color}-500/20 text-${badge.color}-400` : 'bg-slate-800 text-slate-600'}
                                            `}>
                                                {renderIcon(badge.icon_name)}
                                            </div>
                                            
                                            <div className="flex-1 min-w-0">
                                                <div className="flex justify-between items-start">
                                                    <h4 className={`font-bold truncate ${isEarned ? 'text-white' : 'text-slate-500'}`}>
                                                        {badge.name}
                                                    </h4>
                                                    {isEarned && (
                                                        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded font-bold uppercase tracking-wider">
                                                            Owned
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                                                    {badge.description}
                                                </p>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
};
