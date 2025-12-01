/**
 * supabaseIngestor.ts
 * Handles batch submission of cleaned logs to Supabase
 */

import { supabase } from '../../supabase';
import { CleanedLog } from './types';

export interface TradeLogEntry {
    trade_timestamp_utc: string;
    log_hash: string;
    nick: string;
    trade_type: string;
    message: string;
    server: string;
}

/**
 * Submits logs in batches to optimize network usage and avoid timeouts.
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

        // Map to database schema
        const entries: TradeLogEntry[] = batch.map(log => ({
            trade_timestamp_utc: log.trade_timestamp_utc,
            log_hash: log.content_hash,
            nick: log.game_nick,
            trade_type: log.trade_type || 'UNKNOWN',
            message: log.message_clean,
            server: log.server_code
        }));

        try {
            const { data, error } = await supabase
                .from('trade_logs')
                .insert(entries)
                .select();

            if (error) {
                // Error 23505 = duplicate key value violates unique constraint
                if (error.code === '23505') {
                    // If batch fails due to duplicates, we might want to try inserting one by one 
                    // or just count them as duplicates if we assume the whole batch failed due to one.
                    // However, Supabase batch insert fails completely on one error by default.
                    // To handle partial success/duplicates properly with `insert`, we can use `upsert` 
                    // with `onConflict` if we wanted to update, or `ignoreDuplicates: true`.

                    // Let's retry with ignoreDuplicates to count real successes
                    const { data: retryData, error: retryError } = await supabase
                        .from('trade_logs')
                        .upsert(entries, { onConflict: 'trade_timestamp_utc,log_hash', ignoreDuplicates: true })
                        .select();

                    if (!retryError) {
                        const insertedCount = retryData?.length || 0;
                        success += insertedCount;
                        duplicates += (entries.length - insertedCount);
                    } else {
                        console.error('Retry error:', retryError);
                        errors += entries.length;
                    }

                } else {
                    console.error('Batch error:', error);
                    errors += entries.length;
                }
            } else {
                success += data?.length || 0;
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
