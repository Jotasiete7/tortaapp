import React, { useState, useEffect } from 'react';
import { supabase, TickerMessage } from '../services/supabase';
import { Megaphone } from 'lucide-react';
import { emojiService } from '../services/emojiService';

export const NewsTicker: React.FC = () => {
    const [messages, setMessages] = useState<TickerMessage[]>([]);
    const [emojisLoaded, setEmojisLoaded] = useState(false);

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

    const fetchMessages = async () => {
        const { data, error } = await supabase
            .from('ticker_messages')
            .select('*')
            .or(`expires_at.is.null,expires_at.gt.${new Date().toISOString()}`)
            .order('created_at', { ascending: false })
            .limit(20);

        if (!error && data) {
            setMessages(data);
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
                        {messages.map((msg, index) => (
                            <span key={msg.id} className="inline-flex items-center mx-6">
                                {msg.paid && (
                                    <span className="mr-2 px-2 py-0.5 bg-amber-500 text-black text-xs font-bold rounded">
                                        PAID
                                    </span>
                                )}
                                <span className={`${colorMap[msg.color]} font-medium text-sm flex items-center`}>
                                    {emojiService.parseText(msg.text).map((part, i) => (
                                        typeof part === 'string' ? (
                                            <span key={i}>{part}</span>
                                        ) : (
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
          0% { transform: translateX(0%); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
        .animate-marquee:hover {
          animation-play-state: paused;
        }
      `}</style>
        </div>
    );
};
