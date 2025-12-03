import React from 'react';

interface ServerIconProps {
    server: string;
    className?: string;
}

export const ServerIcon: React.FC<ServerIconProps> = ({ server, className = '' }) => {
    const normalized = (server || '').toLowerCase();
    
    // Icons requested: Harmony | Melody | Cadence
    // Relaxed matching to handle truncated names like "Har", "Mel", "Cad"
    
    if (normalized.includes('har')) {
        return <span title='Harmony' className={`cursor-help text-emerald-400 font-bold ${className}`}>H</span>;
    }
    if (normalized.includes('mel')) {
        return <span title='Melody' className={`cursor-help text-blue-400 font-bold ${className}`}>M</span>;
    }
    if (normalized.includes('cad')) {
        return <span title='Cadence' className={`cursor-help text-amber-400 font-bold ${className}`}>C</span>;
    }
    
    // Fallback
    return <span title={server} className={`text-slate-500 ${className}`}>?</span>;
};
