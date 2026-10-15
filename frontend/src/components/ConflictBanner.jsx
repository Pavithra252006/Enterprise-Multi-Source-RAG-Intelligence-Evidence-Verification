import React from 'react';

export default function ConflictBanner({ conflicts = [] }) {
  if (!conflicts || conflicts.length === 0) return null;

  return (
    <div className="space-y-4 my-4 animate-fade-in">
      {conflicts.map((conflict, idx) => (
        <div
          key={idx}
          className="rounded-2xl border border-amber-500/40 bg-gradient-to-b from-amber-950/40 to-slate-900/90 shadow-xl shadow-amber-950/20 overflow-hidden"
        >
          {/* Banner Header */}
          <div className="px-5 py-3.5 bg-amber-500/10 border-b border-amber-500/30 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                  Contradiction Detected
                </span>
                <h3 className="text-sm font-semibold text-white m-0">
                  Topic: {conflict.topic}
                </h3>
              </div>
            </div>

            <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/30">
              {conflict.is_superseded ? 'Superseded Discrepancy' : 'Temporal Ambiguity'}
            </span>
          </div>

          {/* Side-by-Side Comparison */}
          <div className="p-5 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Source A */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 relative">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-300 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-indigo-400" />
                    Source A
                  </span>
                  <span className="font-mono text-[11px] px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300">
                    v{conflict.side_a.version || '1.0'}
                  </span>
                </div>

                <div className="text-lg font-bold text-amber-300 font-mono">
                  {conflict.side_a.value}
                </div>

                <div className="text-xs text-slate-400 space-y-1 pt-2 border-t border-slate-800/80">
                  <div className="truncate text-slate-300 font-medium">
                    {conflict.side_a.source}
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>Date: {conflict.side_a.date || 'N/A'}</span>
                    <span>Loc: {conflict.side_a.location || 'N/A'}</span>
                  </div>
                </div>
              </div>

              {/* Source B */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 relative">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-300 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-purple-400" />
                    Source B
                  </span>
                  <span className="font-mono text-[11px] px-1.5 py-0.5 rounded bg-slate-800 text-purple-300">
                    v{conflict.side_b.version || '1.0'}
                  </span>
                </div>

                <div className="text-lg font-bold text-amber-300 font-mono">
                  {conflict.side_b.value}
                </div>

                <div className="text-xs text-slate-400 space-y-1 pt-2 border-t border-slate-800/80">
                  <div className="truncate text-slate-300 font-medium">
                    {conflict.side_b.source}
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>Date: {conflict.side_b.date || 'N/A'}</span>
                    <span>Loc: {conflict.side_b.location || 'N/A'}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Resolution Box */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-amber-500/20 text-xs space-y-1.5">
              <div className="flex items-center gap-2 text-amber-400 font-semibold">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Pipeline Resolution</span>
              </div>
              <div className="text-slate-200 font-medium leading-relaxed">
                {conflict.resolution}
              </div>
              <div className="text-slate-400 text-[11px] leading-relaxed pt-1">
                {conflict.explanation}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
