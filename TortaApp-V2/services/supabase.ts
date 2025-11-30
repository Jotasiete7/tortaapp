import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://cvghrtmluamzwxpynxpo.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2Z2hydG1sdWFtend4cHlueHBvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5ODk0NTUsImV4cCI6MjA0ODU2NTQ1NX0.QIk5iJnQH_BBbue1mPXYwA_pBLvzEwaYXOJMvbGKfhQ';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
    }
});

// Types for our tables
export interface Profile {
    id: string;
    role: 'guest' | 'user' | 'admin' | 'moderator';
    created_at?: string;
}

export interface TickerMessage {
    id: number;
    text: string;
    color: 'green' | 'red' | 'yellow' | 'cyan' | 'purple';
    paid: boolean;
    expires_at?: string;
    created_by: string;
    created_at: string;
}
