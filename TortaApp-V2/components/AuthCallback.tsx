import React, { useEffect } from 'react';
import { supabase } from '../services/supabase';

export const AuthCallback: React.FC = () => {
    useEffect(() => {
        // Handle the OAuth callback
        const handleCallback = async () => {
            try {
                const { data: { session }, error } = await supabase.auth.getSession();

                if (error) throw error;

                if (session) {
                    // Login successful
                    // Clear the hash from the URL to clean up
                    window.history.replaceState(null, '', '/');
                    // Reload to ensure the app picks up the new session state cleanly
                    window.location.href = '/';
                } else {
                    // No session found, redirect to login
                    window.location.href = '/';
                }
            } catch (e) {
                console.error('Error during auth callback:', e);
                window.location.href = '/';
            }
        };

        handleCallback();
    }, []);

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900">
            <div className="flex flex-col items-center gap-4">
                <div className="animate-spin w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full"></div>
                <div className="text-white text-xl font-medium">Completing Sign In...</div>
                <div className="text-slate-500 text-sm">Please wait while we log you in</div>
            </div>
        </div>
    );
};
