import React from 'react';

interface ServerIconProps {
    server: string;
    className?: string;
}

export const ServerIcon: React.FC<ServerIconProps> = ({ server, className = '' }) => {
    const normalized = (server || '').toLowerCase();
    
    // Icons requested: ??? Harmony | ?? Melody | ?? Cadence
    
    if (normalized.includes('harmony')) {
        return <span title='Harmony' className={\cursor-help \\}>???</span>;
    }
    if (normalized.includes('melody')) {
        return <span title='Melody' className={\cursor-help \\}>??</span>;
    }
    if (normalized.includes('cadence')) {
        return <span title='Cadence' className={\cursor-help \\}>??</span>;
    }
    
    // Fallback
    return <span title={server} className={\	ext-slate-500 \\}>???</span>;
};
