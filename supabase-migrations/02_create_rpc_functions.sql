-- =====================================================
-- 02_create_rpc_functions.sql
-- Creates all RPC functions required by intelligence.ts
-- =====================================================

-- =====================================================
-- FUNCTION: get_global_stats()
-- Returns aggregate statistics from trade_logs table
-- =====================================================
CREATE OR REPLACE FUNCTION get_global_stats()
RETURNS TABLE (
    total_volume BIGINT,
    items_indexed BIGINT,
    avg_price NUMERIC,
    wts_count BIGINT,
    wtb_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_volume,
        COUNT(DISTINCT message)::BIGINT AS items_indexed,
        0::NUMERIC AS avg_price,
        COUNT(*) FILTER (WHERE trade_type = 'WTS')::BIGINT AS wts_count,
        COUNT(*) FILTER (WHERE trade_type = 'WTB')::BIGINT AS wtb_count
    FROM trade_logs;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- FUNCTION: get_top_traders(limit_count)
-- Returns top traders by total trade volume
-- =====================================================
CREATE OR REPLACE FUNCTION get_top_traders(limit_count INT DEFAULT 10)
RETURNS TABLE (
    nick TEXT,
    total_trades BIGINT,
    last_seen TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.nick,
        COUNT(*)::BIGINT AS total_trades,
        MAX(t.trade_timestamp_utc) AS last_seen
    FROM trade_logs t
    GROUP BY t.nick
    ORDER BY total_trades DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- FUNCTION: get_player_stats(player_nick)
-- Returns basic statistics for a specific player
-- =====================================================
CREATE OR REPLACE FUNCTION get_player_stats(player_nick TEXT)
RETURNS TABLE (
    nick TEXT,
    wts BIGINT,
    wtb BIGINT,
    total BIGINT,
    fav_server TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        player_nick AS nick,
        COUNT(*) FILTER (WHERE trade_type = 'WTS')::BIGINT AS wts,
        COUNT(*) FILTER (WHERE trade_type = 'WTB')::BIGINT AS wtb,
        COUNT(*)::BIGINT AS total,
        (
            SELECT server
            FROM trade_logs
            WHERE LOWER(nick) = LOWER(player_nick)
            GROUP BY server
            ORDER BY COUNT(*) DESC
            LIMIT 1
        ) AS fav_server
    FROM trade_logs
    WHERE LOWER(nick) = LOWER(player_nick);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- FUNCTION: get_player_stats_advanced(target_nick)
-- Returns advanced statistics for player profile page
-- =====================================================
CREATE OR REPLACE FUNCTION get_player_stats_advanced(target_nick TEXT)
RETURNS TABLE (
    nick TEXT,
    wts BIGINT,
    wtb BIGINT,
    total BIGINT,
    fav_server TEXT,
    pc_count BIGINT,
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    rank_position INT
) AS $$
BEGIN
    RETURN QUERY
    WITH player_data AS (
        SELECT
            target_nick AS nick,
            COUNT(*) FILTER (WHERE trade_type = 'WTS')::BIGINT AS wts,
            COUNT(*) FILTER (WHERE trade_type = 'WTB')::BIGINT AS wtb,
            COUNT(*) FILTER (WHERE trade_type = 'PC')::BIGINT AS pc_count,
            COUNT(*)::BIGINT AS total,
            MIN(trade_timestamp_utc) AS first_seen,
            MAX(trade_timestamp_utc) AS last_seen,
            (
                SELECT server
                FROM trade_logs
                WHERE LOWER(nick) = LOWER(target_nick)
                GROUP BY server
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS fav_server
        FROM trade_logs
        WHERE LOWER(nick) = LOWER(target_nick)
    ),
    rankings AS (
        SELECT
            nick,
            ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rank
        FROM trade_logs
        GROUP BY nick
    )
    SELECT
        pd.nick,
        pd.wts,
        pd.wtb,
        pd.total,
        pd.fav_server,
        pd.pc_count,
        pd.first_seen,
        pd.last_seen,
        COALESCE(r.rank, 0)::INT AS rank_position
    FROM player_data pd
    LEFT JOIN rankings r ON LOWER(r.nick) = LOWER(pd.nick);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- FUNCTION: get_player_logs(target_nick, limit_count, offset_count)
-- Returns paginated trade logs for a specific player
-- =====================================================
CREATE OR REPLACE FUNCTION get_player_logs(
    target_nick TEXT,
    limit_count INT DEFAULT 50,
    offset_count INT DEFAULT 0
)
RETURNS TABLE (
    id TEXT,
    trade_timestamp_utc TIMESTAMPTZ,
    trade_type TEXT,
    message TEXT,
    server TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        log_hash AS id,
        t.trade_timestamp_utc,
        t.trade_type,
        t.message,
        t.server
    FROM trade_logs t
    WHERE LOWER(t.nick) = LOWER(target_nick)
    ORDER BY t.trade_timestamp_utc DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- FUNCTION: get_player_activity_chart(target_nick)
-- Returns daily activity data for charts
-- =====================================================
CREATE OR REPLACE FUNCTION get_player_activity_chart(target_nick TEXT)
RETURNS TABLE (
    activity_date DATE,
    trade_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE(trade_timestamp_utc) AS activity_date,
        COUNT(*)::BIGINT AS trade_count
    FROM trade_logs
    WHERE LOWER(nick) = LOWER(target_nick)
    GROUP BY DATE(trade_timestamp_utc)
    ORDER BY activity_date DESC
    LIMIT 90; -- Last 90 days
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION get_global_stats() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_top_traders(INT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_player_stats(TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_player_stats_advanced(TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_player_logs(TEXT, INT, INT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_player_activity_chart(TEXT) TO authenticated, anon;
