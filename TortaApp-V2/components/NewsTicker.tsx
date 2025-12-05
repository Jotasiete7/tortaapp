import React, { useState, useEffect } from 'react';
import { supabase } from '../services/supabase';
import { Megaphone, Shield, Award, Star, Heart, TrendingUp, Gift, Beaker } from 'lucide-react';
import { emojiService } from '../services/emojiService';

// Tipos estendidos para incluir novos campos
interface TickerMessageExtended {
    id: string;
    text: string;
    color: 'green' | 'red' | 'yellow' | 'cyan' | 'purple';
    paid: boolean;
    created_at: string;
    expires_at?: string | null;
    created_by?: string | null;
    created_by_nick?: string | null;
    user_first_badge_id?: string | null;
}

// Map de ícones de badges
const BadgeIconMap: Record<string, React.ElementType> = {
    Shield, Award, Star, Heart, TrendingUp, Gift, Beaker
};

// Helper para renderizar texto com links
const renderMessageWithLinks = (text: string): React.ReactNode[] => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const parts = text.split(urlRegex);

    return parts.map((part, index) => {
        if (part.match(urlRegex)) {
            return (
                <a
                    key={index}
                    href={part}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 underline transition-colors"
                    onClick={(e) => e.stopPropagation()}
                >
                    {part}
                </a>
            );
        }
        return <span key={index}>{part}</span>;
    });
};

export const NewsTicker: React.FC = () => {
    const [messages, setMessages] = useState<TickerMessageExtended[]>([]);
    const [emojisLoaded, setEmojisLoaded] = useState(false);
    const [speed, setSpeed] = useState<number>(() => {
        const saved = localStorage.getItem('ticker_speed');
        return saved ? parseFloat(saved) : 1;
    });

    useEffect(() => {
        // Load emojis
        emojiService.loadEmojis().then(() => setEmojisLoaded(true));

        // Fetch initial messages
        fetchMessages();

        // Subscribe to realtime updates
        const channel = supabase
            .channel('ticker-updates')
            .on(
                'postgres_changes',
                {
                    event: '*',
                    schema: 'public',
                    table: 'ticker_messages'
                },
                () => {
                    fetchMessages();
                }
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, []);

    // Listen for speed changes from localStorage (cross-tab sync)
    useEffect(() => {
        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === 'ticker_speed' && e.newValue) {
                setSpeed(parseFloat(e.newValue));
            }
        };
        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, []);

    const fetchMessages = async () => {
        // CORREÇÃO: Removemos o filtro .or() complexo da query que poderia causar problemas
        // Trazemos as últimas 20 mensagens e filtramos no cliente
        const { data, error } = await supabase
            .from('ticker_messages')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(20);

        if (!error && data) {
            // Filtro Client-Side (Mais robusto contra timezones)
            const now = new Date();
            const validMessages = data.filter(msg => {
                // Se não tem expires_at, é permanente (true)
                if (!msg.expires_at) return true;

                // Se tem, verifica se a data de expiração é maior que agora
                return new Date(msg.expires_at) > now;
            });

            setMessages(validMessages);
        }
    };

    // Wait for emojis to load before rendering
    if (!emojisLoaded) {
        return null;
    }

    if (messages.length === 0) {
        return null;
    }

    const colorMap = {
        green: 'text-emerald-400',
        red: 'text-rose-400',
        yellow: 'text-yellow-400',
        cyan: 'text-cyan-400',
        purple: 'text-purple-400'
    };

    return (
        <div className="fixed top-0 left-0 right-0 h-8 bg-black border-b border-slate-800 z-50 overflow-hidden">
            <div className="flex items-center h-full">
                <div className="flex-shrink-0 px-3 bg-amber-600 h-full flex items-center">
                    <Megaphone className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1 overflow-hidden relative">
                    <div className="animate-marquee whitespace-nowrap inline-block">
                        {[...messages, ...messages].map((msg, index) => (
                            <span key={`${msg.id}-${index}`} className="inline-flex items-center mx-6">
                                {/* Badge/Label - DIFERENTE para Admin vs Shout Comunitário */}
                                {msg.paid && (
                                    msg.created_by_nick ? (
                                        // SHOUT COMUNITÁRIO - Mostra Nick + Badge em CYAN
                                        <span className="mr-2 px-2 py-0.5 bg-cyan-500/10 border border-cyan-500/50 text-cyan-400 text-xs font-bold rounded flex items-center gap-1">
                                            {msg.user_first_badge_id && (
                                                <Award className="w-3 h-3" />
                                            )}
                                            {msg.created_by_nick}
                                        </span>
                                    ) : (
                                        // ANÚNCIO ADMIN - Badge PAID amarela tradicional
                                        <span className="mr-2 px-2 py-0.5 bg-amber-500 text-black text-xs font-bold rounded">
                                            PAID
                                        </span>
                                    )
                                )}

                                {/* Mensagem com Links Clicáveis */}
                                <span className={`${colorMap[msg.color]} font-medium text-sm flex items-center gap-1`}>
                                    {emojiService.parseText(msg.text).map((part, i) => (
                                        typeof part === 'string' ? (
                                            // Renderizar texto com links clicáveis
                                            <span key={i} className="inline-flex items-center gap-1">
                                                {renderMessageWithLinks(part)}
                                            </span>
                                        ) : (
                                            // Renderizar emoji
                                            <img
                                                key={i}
                                                src={part.path}
                                                alt={part.alt}
                                                className="w-5 h-5 inline-block mx-0.5 align-text-bottom"
                                                loading="eager"
                                            />
                                        )
                                    ))}
                                </span>

                                {index < messages.length - 1 && (
                                    <span className="mx-4 text-slate-600">•</span>
                                )}
                            </span>
                        ))}
                    </div>
                </div>
            </div>

            <style>{`
        @keyframes marquee {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
        .animate-marquee {
          animation: marquee ${60 / speed}s linear infinite;
        }
        .animate-marquee:hover {
          animation-play-state: paused;
        }
      `}</style>
        </div>
    );
};
