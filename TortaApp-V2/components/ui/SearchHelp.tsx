import React, { useState } from 'react';
import { HelpCircle, X } from 'lucide-react';

export const SearchHelp: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-1.5 hover:bg-slate-700 rounded-full transition-colors text-slate-400 hover:text-amber-500"
        title="Search Help"
      >
        <HelpCircle className="w-4 h-4" />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black/20 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Popup */}
          <div className="absolute right-0 top-8 z-50 w-80 bg-slate-800 border border-slate-600 rounded-lg shadow-2xl p-4 animate-fade-in">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-amber-500" />
                Advanced Search Guide
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white"
              >
                <X className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              {/* Text Search */}
              <div>
                <div className="text-slate-400 font-semibold mb-1">📝 Text Search</div>
                <code className="block bg-slate-900 px-2 py-1 rounded text-emerald-400">stone</code>
                <p className="text-slate-500 mt-1">Finds items with "stone" in name, seller, or material</p>
              </div>

              {/* Quality Filter */}
              <div>
                <div className="text-slate-400 font-semibold mb-1">⭐ Quality Filter</div>
                <code className="block bg-slate-900 px-2 py-1 rounded text-emerald-400">stone ql&gt;90</code>
                <p className="text-slate-500 mt-1">Aliases: <span className="text-amber-400">ql, quality, q</span></p>
              </div>

              {/* Price Filter */}
              <div>
                <div className="text-slate-400 font-semibold mb-1">💰 Price Filter</div>
                <code className="block bg-slate-900 px-2 py-1 rounded text-emerald-400">brick price&lt;50</code>
                <p className="text-slate-500 mt-1">Aliases: <span className="text-amber-400">price, p</span></p>
              </div>

              {/* Quantity Filter */}
              <div>
                <div className="text-slate-400 font-semibold mb-1">📦 Quantity Filter</div>
                <code className="block bg-slate-900 px-2 py-1 rounded text-emerald-400">iron qty&gt;=1000</code>
                <p className="text-slate-500 mt-1">Aliases: <span className="text-amber-400">qty, quantity</span></p>
              </div>

              {/* Seller Filter */}
              <div>
                <div className="text-slate-400 font-semibold mb-1">👤 Seller Filter</div>
                <code className="block bg-slate-900 px-2 py-1 rounded text-emerald-400">seller=jota</code>
                <p className="text-slate-500 mt-1">Aliases: <span className="text-amber-400">seller, s</span></p>
              </div>

              {/* Combined */}
              <div className="border-t border-slate-700 pt-3">
                <div className="text-slate-400 font-semibold mb-1">🔥 Combined Search</div>
                <code className="block bg-slate-900 px-2 py-1 rounded text-purple-400">stone ql&gt;80 price&lt;100</code>
                <p className="text-slate-500 mt-1">Combine multiple filters for precise results</p>
              </div>

              {/* Operators */}
              <div className="bg-slate-900/50 p-2 rounded">
                <div className="text-slate-400 font-semibold mb-1">Operators</div>
                <div className="grid grid-cols-5 gap-1 text-center">
                  <code className="text-amber-400">&gt;</code>
                  <code className="text-amber-400">&lt;</code>
                  <code className="text-amber-400">=</code>
                  <code className="text-amber-400">&gt;=</code>
                  <code className="text-amber-400">&lt;=</code>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
