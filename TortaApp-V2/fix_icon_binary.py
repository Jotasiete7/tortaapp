# -*- coding: utf-8 -*-
import os

path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\ServerIcon.tsx"

content = """import React from 'react';

interface ServerIconProps {
    server: string;
    className?: string;
}

export const ServerIcon: React.FC<ServerIconProps> = ({ server, className = '' }) => {
    const s = (server || '').toLowerCase();

    let emoji = '❓';
    let title = server;

    if (s.includes('har')) {
        emoji = '🏞️';
        title = 'Harmony';
    } else if (s.includes('mel')) {
        emoji = '⛰️';
        title = 'Melody';
    } else if (s.includes('cad')) {
        emoji = '🌊';
        title = 'Cadence';
    }

    return (
        <span 
            title={title} 
            className={`select-none inline-flex items-center justify-center ${className}`} 
            role="img" 
            aria-label={title}
        >
            {emoji}
        </span>
    );
};
"""

try:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("ServerIcon.tsx written successfully.")
except Exception as e:
    print(f"Error writing ServerIcon.tsx: {e}")
