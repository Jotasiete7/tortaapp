-- =====================================================
-- 03_create_verification_system.sql
-- Complete nick verification system for TortaApp
-- =====================================================

-- =====================================================
-- 1. CREATE user_nicks TABLE
-- =====================================================
DROP TABLE IF EXISTS user_nicks CASCADE;

CREATE TABLE user_nicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    game_nick TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT false,
    verification_token TEXT,
    token_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint: one nick per user
    UNIQUE(user_id, game_nick)
);

-- Indexes for performance
CREATE INDEX idx_user_nicks_user_id ON user_nicks(user_id);
CREATE INDEX idx_user_nicks_game_nick ON user_nicks(LOWER(game_nick));
CREATE INDEX idx_user_nicks_token ON user_nicks(verification_token) WHERE verification_token IS NOT NULL;

-- Enable RLS
ALTER TABLE user_nicks ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own nicks"
    ON user_nicks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own nicks"
    ON user_nicks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own nicks"
    ON user_nicks FOR UPDATE
    USING (auth.uid() = user_id);

-- =====================================================
-- 2. CREATE generate_verification_token RPC
-- =====================================================
DROP FUNCTION IF EXISTS generate_verification_token(TEXT);

CREATE OR REPLACE FUNCTION generate_verification_token(target_nick TEXT)
RETURNS TEXT AS $$
DECLARE
    new_token TEXT;
    token_suffix TEXT;
BEGIN
    -- Generate random 5-character alphanumeric suffix
    token_suffix := UPPER(substring(md5(random()::text || clock_timestamp()::text) from 1 for 5));
    new_token := '@TORTA-' || token_suffix;
    
    -- Insert or update user_nicks
    INSERT INTO user_nicks (user_id, game_nick, verification_token, token_expires_at, is_verified)
    VALUES (
        auth.uid(),
        target_nick,
        new_token,
        NOW() + INTERVAL '1 hour',
        false
    )
    ON CONFLICT (user_id, game_nick) 
    DO UPDATE SET
        verification_token = new_token,
        token_expires_at = NOW() + INTERVAL '1 hour',
        is_verified = false,
        updated_at = NOW();
    
    RETURN new_token;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION generate_verification_token(TEXT) TO authenticated;

-- =====================================================
-- 3. CREATE TRIGGER for auto-verification
-- =====================================================

-- Trigger function
DROP FUNCTION IF EXISTS verify_nick_from_log() CASCADE;

CREATE OR REPLACE FUNCTION verify_nick_from_log()
RETURNS TRIGGER AS $$
DECLARE
    found_token TEXT;
    matched_record RECORD;
BEGIN
    -- Extract @TORTA-XXXXX token from message
    found_token := (regexp_matches(NEW.message, '@TORTA-[A-Z0-9]{5}', 'i'))[1];
    
    -- If no token found, skip
    IF found_token IS NULL THEN
        RETURN NEW;
    END IF;
    
    -- Find matching user_nick record
    SELECT * INTO matched_record
    FROM user_nicks
    WHERE verification_token = found_token
      AND LOWER(game_nick) = LOWER(NEW.nick)
      AND token_expires_at > NOW()
      AND is_verified = false
    LIMIT 1;
    
    -- If match found, verify the nick
    IF matched_record IS NOT NULL THEN
        UPDATE user_nicks
        SET is_verified = true,
            updated_at = NOW()
        WHERE id = matched_record.id;
        
        RAISE NOTICE 'Nick verified: % with token %', NEW.nick, found_token;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on trade_logs
DROP TRIGGER IF EXISTS verify_nick_on_log_insert ON trade_logs;

CREATE TRIGGER verify_nick_on_log_insert
    AFTER INSERT ON trade_logs
    FOR EACH ROW
    EXECUTE FUNCTION verify_nick_from_log();

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Nick verification system created successfully!';
    RAISE NOTICE '   - Table: user_nicks';
    RAISE NOTICE '   - RPC: generate_verification_token(nick)';
    RAISE NOTICE '   - Trigger: verify_nick_on_log_insert';
END $$;
