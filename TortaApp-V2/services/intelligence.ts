import { supabase } from './supabase';

export interface TraderProfile {
    nick: string;
    total_trades: number;
    last_seen: string;
}

export interface PlayerStats {
    nick: string;
    wts: number;
    wtb: number;
    total: number;
    fav_server: string;
}

export const IntelligenceService = {
    /**
     * Fetches the top traders based on volume.
     */
    getTopTraders: async (limit: number = 10): Promise<TraderProfile[]> => {
        const { data, error } = await supabase
            .rpc('get_top_traders', { limit_count: limit });

        if (error) {
            console.error('Error fetching top traders:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Fetches detailed stats for a specific player.
     */
    getPlayerStats: async (nick: string): Promise<PlayerStats | null> => {
        const { data, error } = await supabase
            .rpc('get_player_stats', { player_nick: nick });

        if (error) {
            console.error('Error fetching player stats:', error);
            return null;
        }

        return data && data.length > 0 ? data[0] : null;
    }
};
