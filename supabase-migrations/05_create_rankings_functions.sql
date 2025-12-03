-- Function to get most active traders (by total volume of WTS + WTB)
CREATE OR REPLACE FUNCTION get_most_active_traders(limit_count INT DEFAULT 5, period TEXT DEFAULT 'all_time')
RETURNS TABLE (
    nick TEXT,
    wts_count BIGINT,
    wtb_count BIGINT,
    total_count BIGINT,
    rank BIGINT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.nick,
        COUNT(*) FILTER (WHERE t.trade_type = 'WTS') as wts_count,
        COUNT(*) FILTER (WHERE t.trade_type = 'WTB') as wtb_count,
        COUNT(*) as total_count,
        RANK() OVER (ORDER BY COUNT(*) DESC) as rank
    FROM trade_logs t
    WHERE 
        (period = 'all_time') OR
        (period = 'monthly' AND t.trade_timestamp_utc >= NOW() - INTERVAL '30 days') OR
        (period = 'weekly' AND t.trade_timestamp_utc >= NOW() - INTERVAL '7 days')
    GROUP BY t.nick
    ORDER BY total_count DESC
    LIMIT limit_count;
END;
$$;

-- Function to get most active sellers (WTS only)
CREATE OR REPLACE FUNCTION get_most_active_sellers(limit_count INT DEFAULT 5)
RETURNS TABLE (
    nick TEXT,
    wts_count BIGINT,
    rank BIGINT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.nick,
        COUNT(*) as wts_count,
        RANK() OVER (ORDER BY COUNT(*) DESC) as rank
    FROM trade_logs t
    WHERE t.trade_type = 'WTS'
    AND t.trade_timestamp_utc >= NOW() - INTERVAL '30 days' -- Default to monthly for 'Top Sellers'
    GROUP BY t.nick
    ORDER BY wts_count DESC
    LIMIT limit_count;
END;
$$;

-- Function to get most active buyers (WTB only)
CREATE OR REPLACE FUNCTION get_most_active_buyers(limit_count INT DEFAULT 5)
RETURNS TABLE (
    nick TEXT,
    wtb_count BIGINT,
    rank BIGINT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.nick,
        COUNT(*) as wtb_count,
        RANK() OVER (ORDER BY COUNT(*) DESC) as rank
    FROM trade_logs t
    WHERE t.trade_type = 'WTB'
    AND t.trade_timestamp_utc >= NOW() - INTERVAL '30 days' -- Default to monthly for 'Top Buyers'
    GROUP BY t.nick
    ORDER BY wtb_count DESC
    LIMIT limit_count;
END;
$$;

-- Function to get top price checkers (PC only)
CREATE OR REPLACE FUNCTION get_top_price_checkers(limit_count INT DEFAULT 5)
RETURNS TABLE (
    nick TEXT,
    pc_count BIGINT,
    rank BIGINT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.nick,
        COUNT(*) as pc_count,
        RANK() OVER (ORDER BY COUNT(*) DESC) as rank
    FROM trade_logs t
    WHERE t.trade_type = 'PC'
    AND t.trade_timestamp_utc >= NOW() - INTERVAL '7 days' -- Default to weekly for 'Top Appraisers'
    GROUP BY t.nick
    ORDER BY pc_count DESC
    LIMIT limit_count;
END;
$$;
