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

export interface PlayerStatsAdvanced extends PlayerStats {
    pc_count: number;
    first_seen: string;
    last_seen: string;
    rank_position: number;
}

export interface PlayerLog {
    id: string;
    trade_timestamp_utc: string;
    trade_type: string;
    message: string;
    server: string;
}

export interface ActivityPoint {
    activity_date: string;
    trade_count: number;
}

export interface GlobalStats {
    total_volume: number;
    items_indexed: number;
    avg_price: number;
    wts_count: number;
    wtb_count: number;
}

export const IntelligenceService = {
    /**
     * Fetches global stats for the dashboard.
     */
    getGlobalStats: async (): Promise<GlobalStats | null> => {
        const { data, error } = await supabase
            .rpc('get_global_stats');

        if (error) {
            console.error('Error fetching global stats:', error);
            return null;
        }

        // RPC returns an array of objects, we expect one row
        return data && data.length > 0 ? data[0] : null;
    },

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
     * Fetches detailed stats for a specific player (Basic Version).
     */
    getPlayerStats: async (nick: string): Promise<PlayerStats | null> => {
        const { data, error } = await supabase
            .rpc('get_player_stats', { player_nick: nick });

        if (error) {
            console.error('Error fetching player stats:', error);
            return null;
        }

        return data && data.length > 0 ? data[0] : null;
    },

    /**
     * Fetches advanced stats for the player profile page.
     */
    getPlayerStatsAdvanced: async (nick: string): Promise<PlayerStatsAdvanced | null> => {
        const { data, error } = await supabase
            .rpc('get_player_stats_advanced', { target_nick: nick });

        if (error) {
            console.error('Error fetching advanced player stats:', error);
            return null;
        }

        return data && data.length > 0 ? data[0] : null;
    },

    /**
     * Fetches paginated logs for a specific player.
     */
    getPlayerLogs: async (nick: string, limit: number = 50, offset: number = 0): Promise<PlayerLog[]> => {
        const { data, error } = await supabase
            .rpc('get_player_logs', { target_nick: nick, limit_count: limit, offset_count: offset });

        if (error) {
            console.error('Error fetching player logs:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Fetches daily activity data for charts.
     */
    getPlayerActivity: async (nick: string): Promise<ActivityPoint[]> => {
        const { data, error } = await supabase
            .rpc('get_player_activity_chart', { target_nick: nick });

        if (error) {
            console.error('Error fetching player activity:', error);
            return [];
        }

        return data || [];
    }
};
