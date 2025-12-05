import { supabase } from './supabase';
import { ShoutBalance } from '../types';

export const ShoutService = {
    /**
     * Fetches the user's current shout balance.
     */
    async getShoutBalance(userId: string): Promise<ShoutBalance | null> {
        const { data, error } = await supabase
            .from('user_shout_balance')
            .select('*')
            .eq('user_id', userId)
            .single();

        if (error) {
            // It's possible the row doesn't exist yet if they haven't used a shout
            // In that case, the UI should assume default (3/10) or handle null
            console.warn('Error fetching shout balance (may be empty):', error);
            return null;
        }
        return data;
    },

    /**
     * Uses a free shout.
     * Calls the RPC function 'use_free_shout'.
     */
    async useFreeShout(message: string, color: string = 'green'): Promise<{ success: boolean; error?: string; remaining_weekly?: number }> {
        const { data, error } = await supabase
            .rpc('use_free_shout', { 
                message_text: message,
                message_color: color 
            });

        if (error) {
            console.error('Error using shout:', error);
            return { success: false, error: error.message };
        }

        // RPC returns JSONB: { success: boolean, error?: string, ... }
        return data;
    }
};
