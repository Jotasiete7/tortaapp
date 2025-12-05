import React from 'react';

interface ServerIconProps {
    server: string;
    className?: string;
}

export const ServerIcon: React.FC<ServerIconProps> = ({ server, className = '' }) => {
    const s = (server || '').toLowerCase();

    let emoji = '?';
    let title = server;

    if (s.includes('har')) {
        emoji = '???';
        title = 'Harmony';
    } else if (s.includes('mel')) {
        emoji = '??';
        title = 'Melody';
    } else if (s.includes('cad')) {
        emoji = '??';
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
