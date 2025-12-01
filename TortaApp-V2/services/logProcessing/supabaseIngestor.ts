/**
 * supabaseIngestor.ts
 * Handles batch submission of cleaned logs to Supabase
 */

import { supabase } from '../supabase';
import { CleanedLog } from './types';

export interface TradeLogEntry {
    trade_timestamp_utc: string;
    log_hash: string;
    nick: string;
    trade_type: string;
    message: string;
    server: string;
    item_category?: string | null;
}

/**
 * Submits logs in batches to optimize network usage and avoid timeouts.
 * Uses UPSERT to handle deduplication automatically.
 */
export async function submitLogsBatch(
    logs: CleanedLog[],
    onProgress?: (current: number, total: number) => void
): Promise<{ success: number; duplicates: number; errors: number }> {
    const BATCH_SIZE = 500;
    let success = 0;
    let duplicates = 0;
    let errors = 0;

    // Filter out invalid logs before processing
    const validLogs = logs.filter(log => log.trade_type !== null);

    for (let i = 0; i < validLogs.length; i += BATCH_SIZE) {
        const batch = validLogs.slice(i, i + BATCH_SIZE);

        // Map to database schema (Canonical Adapter Logic)
        const entries: TradeLogEntry[] = batch.map(log => ({
            trade_timestamp_utc: log.trade_timestamp_utc,
            log_hash: log.content_hash,
            nick: log.game_nick,
            trade_type: log.trade_type || 'UNKNOWN',
            message: log.message_clean,
            server: log.server_code,
            item_category: null // Placeholder for future categorization logic
        }));

        try {
            // 2. INGESTÃO OTIMIZADA COM DEDUPLICAÇÃO:
            // Usamos 'upsert' com 'ignoreDuplicates: true' e 'onConflict'
            const { data, error } = await supabase
                .from('trade_logs')
                .upsert(entries, {
                    onConflict: 'trade_timestamp_utc,log_hash',
                    ignoreDuplicates: true
                })
                .select();

            if (error) {
                console.error('Batch error:', error);
                errors += entries.length;
            } else {
                // Supabase upsert with ignoreDuplicates returns null for duplicates if they are not updated.
                // However, if we select(), it might return only inserted rows or all rows depending on config.
                // With ignoreDuplicates: true, it usually returns only the rows that were actually inserted/updated.
                // If data is null/empty but no error, it means all were duplicates.

                const insertedCount = data?.length || 0;
                success += insertedCount;
                duplicates += (entries.length - insertedCount);
            }
        } catch (err) {
            console.error('Unexpected error:', err);
            errors += entries.length;
        }

        // Progress callback
        if (onProgress) {
            onProgress(Math.min(i + BATCH_SIZE, validLogs.length), validLogs.length);
        }
    }

    return { success, duplicates, errors };
}
