import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { processLogFile } from '../../services/logProcessing';
import { CleanedLog } from '../../services/logProcessing/types';

interface LogUploaderProps {
    onProcessingComplete?: (records: CleanedLog[]) => void;
}

export const LogUploader: React.FC<LogUploaderProps> = ({ onProcessingComplete }) => {
    <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
        <div>
            <p className="text-sm font-medium text-red-400">Processing Error</p>
            <p className="text-xs text-red-400/80 mt-1">{error}</p>
        </div>
    </div>
            )}

{
    stats && (
        <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-4 h-4 text-slate-400" />
                    <span className="text-xs font-medium text-slate-400 uppercase">Total Lines</span>
                </div>
                <span className="text-2xl font-bold text-white">{stats.total.toLocaleString()}</span>
            </div>

            <div className="p-4 bg-emerald-950/30 rounded-lg border border-emerald-500/20">
                <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    <span className="text-xs font-medium text-emerald-400 uppercase">Valid Trades</span>
                </div>
                <span className="text-2xl font-bold text-emerald-400">{stats.valid.toLocaleString()}</span>
            </div>

            <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                    <XCircle className="w-4 h-4 text-slate-500" />
                    <span className="text-xs font-medium text-slate-500 uppercase">Ignored</span>
                </div>
                <span className="text-2xl font-bold text-slate-400">{stats.ignored.toLocaleString()}</span>
            </div>
        </div>
    )
}
        </div >
    );
};
