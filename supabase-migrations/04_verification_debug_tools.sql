-- =====================================================
-- 04_verification_debug_tools.sql
-- Debug and testing tools for nick verification
-- =====================================================

-- =====================================================
-- 1. DEBUG: Check verification status
-- =====================================================
DROP FUNCTION IF EXISTS debug_verification_status(TEXT);

CREATE OR REPLACE FUNCTION debug_verification_status(target_nick TEXT)
RETURNS TABLE (
    nick TEXT,
    is_verified BOOLEAN,
    verification_token TEXT,
    token_expires_at TIMESTAMPTZ,
    token_expired BOOLEAN,
    recent_logs_count BIGINT,
    recent_logs_with_token TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        un.game_nick,
        un.is_verified,
        un.verification_token,
        un.token_expires_at,
        (un.token_expires_at < NOW()) AS token_expired,
        (
            SELECT COUNT(*)
            FROM trade_logs tl
            WHERE LOWER(tl.nick) = LOWER(target_nick)
        ) AS recent_logs_count,
        (
            SELECT ARRAY_AGG(tl.message)
            FROM trade_logs tl
            WHERE LOWER(tl.nick) = LOWER(target_nick)
              AND tl.message LIKE '%@TORTA-%'
            ORDER BY tl.trade_timestamp_utc DESC
            LIMIT 5
        ) AS recent_logs_with_token
    FROM user_nicks un
    WHERE LOWER(un.game_nick) = LOWER(target_nick)
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION debug_verification_status(TEXT) TO authenticated, anon;

-- =====================================================
-- 2. DEBUG: Simulate log upload with token
-- =====================================================
DROP FUNCTION IF EXISTS debug_simulate_log_upload(TEXT, TEXT);

CREATE OR REPLACE FUNCTION debug_simulate_log_upload(
    target_nick TEXT,
    token TEXT
)
RETURNS TEXT AS $$
DECLARE
    result TEXT;
BEGIN
    -- Insert a fake log entry with the token
    INSERT INTO trade_logs (
        trade_timestamp_utc,
        log_hash,
        nick,
        trade_type,
        message,
        server
    ) VALUES (
        NOW(),
        md5(random()::text),
        target_nick,
        'PC',
        token,
        'Debug'
    );
    
    -- Check if verification happened
    IF EXISTS (
        SELECT 1 FROM user_nicks
        WHERE LOWER(game_nick) = LOWER(target_nick)
          AND is_verified = true
    ) THEN
        result := '✅ SUCCESS: Nick verified!';
    ELSE
        result := '❌ FAILED: Nick not verified. Check token and expiration.';
    END IF;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION debug_simulate_log_upload(TEXT, TEXT) TO authenticated;

-- =====================================================
-- 3. DEBUG: List all verifications (admin only)
-- =====================================================
DROP FUNCTION IF EXISTS debug_list_all_verifications();

CREATE OR REPLACE FUNCTION debug_list_all_verifications()
RETURNS TABLE (
    user_email TEXT,
    game_nick TEXT,
    is_verified BOOLEAN,
    verification_token TEXT,
    token_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    -- Check if user is admin
    IF NOT EXISTS (
        SELECT 1 FROM profiles
        WHERE id = auth.uid()
          AND role = 'admin'
    ) THEN
        RAISE EXCEPTION 'Access denied: Admin only';
    END IF;
    
    RETURN QUERY
    SELECT
        au.email,
        un.game_nick,
        un.is_verified,
        un.verification_token,
        un.token_expires_at,
        un.created_at
    FROM user_nicks un
    JOIN auth.users au ON au.id = un.user_id
    ORDER BY un.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION debug_list_all_verifications() TO authenticated;

-- =====================================================
-- 4. DEBUG: Force verify a nick (admin only)
-- =====================================================
DROP FUNCTION IF EXISTS debug_force_verify_nick(TEXT);

CREATE OR REPLACE FUNCTION debug_force_verify_nick(target_nick TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Check if user is admin
    IF NOT EXISTS (
        SELECT 1 FROM profiles
        WHERE id = auth.uid()
          AND role = 'admin'
    ) THEN
        RAISE EXCEPTION 'Access denied: Admin only';
    END IF;
    
    -- Force verify
    UPDATE user_nicks
    SET is_verified = true,
        updated_at = NOW()
    WHERE LOWER(game_nick) = LOWER(target_nick);
    
    IF FOUND THEN
        RETURN '✅ Nick ' || target_nick || ' force-verified successfully';
    ELSE
        RETURN '❌ Nick ' || target_nick || ' not found in user_nicks';
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION debug_force_verify_nick(TEXT) TO authenticated;

-- =====================================================
-- 5. DEBUG: Check if trigger is working
-- =====================================================
DROP FUNCTION IF EXISTS debug_test_trigger();

CREATE OR REPLACE FUNCTION debug_test_trigger()
RETURNS TEXT AS $$
DECLARE
    test_token TEXT := '@TORTA-TEST1';
    test_nick TEXT := 'TestNick123';
    result TEXT;
BEGIN
    -- Create a test user_nick entry
    INSERT INTO user_nicks (user_id, game_nick, verification_token, token_expires_at, is_verified)
    VALUES (auth.uid(), test_nick, test_token, NOW() + INTERVAL '1 hour', false)
    ON CONFLICT (user_id, game_nick) 
    DO UPDATE SET
        verification_token = test_token,
        token_expires_at = NOW() + INTERVAL '1 hour',
        is_verified = false;
    
    -- Insert a log with the token (should trigger verification)
    INSERT INTO trade_logs (
        trade_timestamp_utc,
        log_hash,
        nick,
        trade_type,
        message,
        server
    ) VALUES (
        NOW(),
        md5(random()::text),
        test_nick,
        'PC',
        test_token,
        'Debug'
    );
    
    -- Check if it was verified
    SELECT CASE 
        WHEN is_verified THEN '✅ TRIGGER WORKING: Test nick was auto-verified!'
        ELSE '❌ TRIGGER NOT WORKING: Test nick was NOT verified'
    END INTO result
    FROM user_nicks
    WHERE LOWER(game_nick) = LOWER(test_nick)
      AND user_id = auth.uid();
    
    -- Cleanup
    DELETE FROM trade_logs WHERE nick = test_nick;
    DELETE FROM user_nicks WHERE LOWER(game_nick) = LOWER(test_nick) AND user_id = auth.uid();
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION debug_test_trigger() TO authenticated;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Debug tools created successfully!';
    RAISE NOTICE '   - debug_verification_status(nick)';
    RAISE NOTICE '   - debug_simulate_log_upload(nick, token)';
    RAISE NOTICE '   - debug_list_all_verifications() [admin]';
    RAISE NOTICE '   - debug_force_verify_nick(nick) [admin]';
    RAISE NOTICE '   - debug_test_trigger()';
END $$;
