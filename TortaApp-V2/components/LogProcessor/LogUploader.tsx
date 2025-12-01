import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { processLogFile } from '../../services/logProcessing';
import { CleanedLog } from '../../services/logProcessing/types';

interface LogUploaderProps {
    onProcessingComplete?: (records: CleanedLog[]) => void;
}

export const LogUploader: React.FC<LogUploaderProps> = ({ onProcessingComplete }) => {
    const [isProcessing, setIsProcessing] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [progress, setProgress] = useState<{ current: number; total: number } | null>(null);
    const [stats, setStats] = useState<{ total: number; valid: number; ignored: number } | null>(null);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = async (file: File) => {
        if (!file) return;

        setIsProcessing(true);
        setError(null);
        setStats(null);
        setProgress(null);

        try {
            // Read file content
            const text = await file.text();

            // Process file
            // Note: For very large files, we might want to chunk this.
            // For now, processing 124MB in memory is usually fine in modern browsers,
            // but blocking the UI is a risk.

            // Using setTimeout to allow UI to update before heavy processing
            setTimeout(() => {
                try {
                    const result = processLogFile(text, new Date());

                    setStats(result.stats);
                    setIsProcessing(false);

                    if (onProcessingComplete) {
                        onProcessingComplete(result.records);
                    }
                } catch (err) {
                    console.error("Processing error:", err);
                    setError("Failed to process log file. Please check the console.");
                    setIsProcessing(false);
                }
            }, 100);

        } catch (err) {
            console.error("File reading error:", err);
            setError("Failed to read file.");
            setIsProcessing(false);
        }
    };

    const onFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) handleFileChange(file);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) handleFileChange(file);
    };

    const triggerFileInput = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6 bg-slate-900/50 border border-slate-800 rounded-xl">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <FileText className="w-5 h-5 text-amber-500" />
                        RAW Log Processor
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                        Upload raw Wurm Online logs (text files) to process trade data.
                    </p>
                </div>
            </div>

            <div
                onClick={triggerFileInput}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
                    border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
                    ${isProcessing
                        ? 'border-slate-700 bg-slate-800/50 cursor-wait'
                        : isDragging
                            ? 'border-amber-500 bg-amber-500/10 scale-[1.02]'
                            : 'border-slate-700 hover:border-amber-500/50 hover:bg-slate-800/50'
                    }
                `}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={onFileInputChange}
                    accept=".txt"
                    className="hidden"
                    disabled={isProcessing}
                />

                {isProcessing ? (
                    <div className="flex flex-col items-center py-4">
                        <Loader2 className="w-10 h-10 text-amber-500 animate-spin mb-4" />
                        <p className="text-slate-300 font-medium">Processing log file...</p>
                        <p className="text-xs text-slate-500 mt-2">This may take a moment for large files</p>
                    </div>
                ) : (
                    <div className="flex flex-col items-center py-4">
                        <div className={`
                            w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors
                            ${isDragging ? 'bg-amber-500/20' : 'bg-slate-800 group-hover:bg-slate-700'}
                        `}>
                            <Upload className={`
                                w-8 h-8 transition-colors
                                ${isDragging ? 'text-amber-500' : 'text-slate-400 group-hover:text-amber-500'}
                            `} />
                        </div>
                        <p className="text-slate-200 font-medium mb-1">
                            {isDragging ? 'Drop file here' : 'Click or drag file to upload'}
                        </p>
                        <p className="text-xs text-slate-500">Supports .txt files (Wurm Online logs)</p>
                    </div>
                )}
            </div>

            {error && (
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                    <div>
                        <p className="text-sm font-medium text-red-400">Processing Error</p>
                        <p className="text-xs text-red-400/80 mt-1">{error}</p>
                    </div>
                </div>
            )}

            {stats && (
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
            )}
        </div>
    );
};
