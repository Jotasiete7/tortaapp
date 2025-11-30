import React, { useState, useEffect } from 'react';
import { supabase, TickerMessage } from '../services/supabase';
import { useAuth } from '../contexts/AuthContext';
import { ProtectedAdmin } from '../components/ProtectedAdmin';
import { Megaphone, Plus, Trash2, Clock } from 'lucide-react';

export const AdminPanel: React.FC = () => {
    return (
        <ProtectedAdmin>
            <AdminPanelContent />
        </ProtectedAdmin>
    );
};

const AdminPanelContent: React.FC = () => {
    const { user } = useAuth();
    const [messages, setMessages] = useState<TickerMessage[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [color, setColor] = useState<'green' | 'red' | 'yellow' | 'cyan' | 'purple'>('green');
    const [isPaid, setIsPaid] = useState(false);
    const [expiresIn, setExpiresIn] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchMessages();

        // Realtime subscription
        const channel = supabase
            .channel('admin-ticker-updates')
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
            .order('created_at', { ascending: false });

        if (!error && data) {
            setMessages(data);
        }
    };

    const handleAddMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newMessage.trim() || !user) return;

        setLoading(true);
        try {
            const expiresAt = expiresIn
                ? new Date(Date.now() + expiresIn * 24 * 60 * 60 * 1000).toISOString()
                : null;

            const { error } = await supabase
                .from('ticker_messages')
                .insert({
                    text: newMessage.trim(),
                    color,
                    paid: isPaid,
                    expires_at: expiresAt,
                    created_by: user.id
                });

            if (error) throw error;

            // Reset form
            setNewMessage('');
            setColor('green');
            setIsPaid(false);
            setExpiresIn(null);
        } catch (err: any) {
            alert('Error adding message: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteMessage = async (id: number) => {
        if (!confirm('Delete this message?')) return;

        const { error } = await supabase
            .from('ticker_messages')
            .delete()
            .eq('id', id);

        if (error) {
            alert('Error deleting message: ' + error.message);
        }
    };

    const colorOptions = [
        { value: 'green', label: 'Green', class: 'bg-emerald-500' },
        { value: 'red', label: 'Red', class: 'bg-rose-500' },
        { value: 'yellow', label: 'Yellow', class: 'bg-yellow-500' },
        { value: 'cyan', label: 'Cyan', class: 'bg-cyan-500' },
        { value: 'purple', label: 'Purple', class: 'bg-purple-500' }
    ];

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
            {/* Header */}
            <div className="text-center space-y-2">
                <div className="inline-flex p-4 bg-amber-500/10 rounded-full mb-2">
                    <Megaphone className="w-10 h-10 text-amber-400" />
                </div>
                <h2 className="text-3xl font-bold text-white">News Ticker Admin</h2>
                <p className="text-slate-400">Manage global news ticker messages</p>
            </div>

            {/* Add Message Form */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Plus className="w-5 h-5 text-amber-400" />
                    Add New Message
                </h3>

                <form onSubmit={handleAddMessage} className="space-y-4">
                    {/* Message Text */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Message Text</label>
                        <input
                            type="text"
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            placeholder="Enter ticker message..."
                            required
                            maxLength={200}
                            className="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder:text-slate-600 focus:ring-2 focus:ring-amber-500/50 outline-none"
                        />
                        <div className="text-xs text-slate-500 text-right">
                            {newMessage.length}/200 characters
                        </div>
                    </div>

                    {/* Color Selection */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-300">Color</label>
                        <div className="grid grid-cols-5 gap-2">
                            {colorOptions.map((opt) => (
                                <button
                                    key={opt.value}
                                    type="button"
                                    onClick={() => setColor(opt.value as any)}
                                    className={`p-3 rounded-lg border-2 transition-all ${color === opt.value
                                            ? 'border-amber-500 scale-105'
                                            : 'border-slate-700 hover:border-slate-600'
                                        }`}
                                >
                                    <div className={`w-full h-8 ${opt.class} rounded`}></div>
                                    <div className="text-xs text-slate-400 mt-1">{opt.label}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Paid & Expires */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={isPaid}
                                    onChange={(e) => setIsPaid(e.target.checked)}
                                    className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-amber-600 focus:ring-amber-500/50"
                                />
                                <span className="text-sm font-medium text-slate-300">Paid Announcement</span>
                            </label>
                            <p className="text-xs text-slate-500">Shows "PAID" badge</p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                Expires In (days)
                            </label>
                            <input
                                type="number"
                                value={expiresIn || ''}
                                onChange={(e) => setExpiresIn(e.target.value ? parseInt(e.target.value) : null)}
                                placeholder="Never"
                                min="1"
                                max="365"
                                className="w-full p-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder:text-slate-600 focus:ring-2 focus:ring-amber-500/50 outline-none"
                            />
                        </div>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading || !newMessage.trim()}
                        className="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-amber-900/20"
                    >
                        {loading ? 'Adding...' : 'Add to Global Ticker'}
                    </button>
                </form>
            </div>

            {/* Messages List */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">
                    Active Messages ({messages.length})
                </h3>

                {messages.length === 0 ? (
                    <div className="text-center py-12 text-slate-500">
                        <Megaphone className="w-12 h-12 mx-auto mb-2 opacity-20" />
                        <p>No messages yet. Add your first one above!</p>
                    </div>
                ) : (
                    <div className="space-y-2">
                        {messages.map((msg) => {
                            const isExpired = msg.expires_at && new Date(msg.expires_at) < new Date();
                            const colorClass = {
                                green: 'text-emerald-400',
                                red: 'text-rose-400',
                                yellow: 'text-yellow-400',
                                cyan: 'text-cyan-400',
                                purple: 'text-purple-400'
                            }[msg.color];

                            return (
                                <div
                                    key={msg.id}
                                    className={`p-4 bg-slate-900 rounded-lg border ${isExpired ? 'border-slate-800 opacity-50' : 'border-slate-700'
                                        } flex items-start justify-between gap-4`}
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            {msg.paid && (
                                                <span className="px-2 py-0.5 bg-amber-500 text-black text-xs font-bold rounded">
                                                    PAID
                                                </span>
                                            )}
                                            {isExpired && (
                                                <span className="px-2 py-0.5 bg-slate-700 text-slate-400 text-xs font-bold rounded">
                                                    EXPIRED
                                                </span>
                                            )}
                                        </div>
                                        <p className={`${colorClass} font-medium mb-2`}>{msg.text}</p>
                                        <div className="flex items-center gap-4 text-xs text-slate-500">
                                            <span>ID: {msg.id}</span>
                                            <span>Created: {new Date(msg.created_at).toLocaleDateString()}</span>
                                            {msg.expires_at && (
                                                <span>Expires: {new Date(msg.expires_at).toLocaleDateString()}</span>
                                            )}
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleDeleteMessage(msg.id)}
                                        className="p-2 text-rose-400 hover:bg-rose-500/10 rounded-lg transition"
                                        title="Delete message"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};
