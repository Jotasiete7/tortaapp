-- =====================================================
-- 01_create_ticker_messages.sql
-- Creates the ticker_messages table for NewsTicker component
-- =====================================================

-- Drop table if exists (for clean reinstall)
DROP TABLE IF EXISTS ticker_messages CASCADE;

-- Create ticker_messages table
CREATE TABLE ticker_messages (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    color TEXT NOT NULL CHECK (color IN ('green', 'red', 'yellow', 'cyan', 'purple')),
    paid BOOLEAN DEFAULT false,
    expires_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_ticker_expires ON ticker_messages(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_ticker_created ON ticker_messages(created_at DESC);

-- Enable Row Level Security
ALTER TABLE ticker_messages ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Anyone can read active ticker messages
CREATE POLICY "Public read access for active tickers"
    ON ticker_messages
    FOR SELECT
    USING (
        expires_at IS NULL OR expires_at > NOW()
    );

-- RLS Policy: Only admins can insert ticker messages
CREATE POLICY "Admin insert access"
    ON ticker_messages
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'admin'
        )
    );

-- RLS Policy: Only admins can update ticker messages
CREATE POLICY "Admin update access"
    ON ticker_messages
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'admin'
        )
    );

-- RLS Policy: Only admins can delete ticker messages
CREATE POLICY "Admin delete access"
    ON ticker_messages
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'admin'
        )
    );

-- Insert sample ticker messages
INSERT INTO ticker_messages (text, color, paid, expires_at) VALUES
    ('🎉 Welcome to TortaApp! Your Wurm Online market intelligence platform.', 'cyan', false, NULL),
    ('📊 Real-time market data powered by community contributions.', 'green', false, NULL),
    ('🔥 New feature: Player profiles with advanced statistics!', 'purple', false, NULL);
