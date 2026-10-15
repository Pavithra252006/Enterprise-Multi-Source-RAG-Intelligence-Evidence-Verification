import React, { useState } from 'react';

export default function PipelineTrace({ trace }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!trace) return null;

  const rounds = trace.scores_per_round || [];
  const rewritesTriggered = trace.rewrites_triggered || false;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/60 overflow-hidden my-4 text-left">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          <svg className={`w-4 h-4 text-indigo-400 transition-transform ${isOpen ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span>Pipeline Retrieval & Verification Trace</span>
          <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            {rounds.length} round{rounds.length !== 1 ? 's' : ''}
          </span>
          {rewritesTriggered && (
            <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Reformulated
            </span>
          )}
        </div>
        <span className="text-[11px] text-slate-500 font-normal">
          {isOpen ? 'Click to collapse' : 'Click to inspect cross-encoder scoring'}
        </span>
      </button>

      {isOpen && (
        <div className="p-4 border-t border-slate-800 space-y-4 text-xs font-mono bg-slate-950">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
            <div className="p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block">Rounds:</span>
              <span className="text-slate-200 font-semibold">{trace.rounds_executed || 1} / {trace.max_rounds || 2}</span>
            </div>
            <div className="p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block">Threshold:</span>
              <span className="text-slate-200 font-semibold">{trace.threshold !== undefined ? trace.threshold : 0.40}</span>
            </div>
            <div className="p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block">Reformulated:</span>
              <span className={rewritesTriggered ? 'text-amber-400 font-semibold' : 'text-slate-400 font-semibold'}>
                {rewritesTriggered ? 'Yes (Adaptive)' : 'No (Direct hit)'}
              </span>
            </div>
            <div className="p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block">Unique Queries:</span>
              <span className="text-slate-200 font-semibold">{trace.queries?.length || 1}</span>
            </div>
          </div>

          {/* Round-by-round breakdown */}
          <div className="space-y-3 pt-2">
            {rounds.map((round, rIdx) => (
              <div key={rIdx} className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-indigo-400 font-bold">Round {round.round + 1}</span>
                  <span className="text-slate-400">
                    Candidates: <span className="text-slate-200">{round.candidates_found}</span> | Best Score:{' '}
                    <span className="text-emerald-400 font-bold font-mono">
                      {round.best_score?.toFixed(4) || 'N/A'}
                    </span>
                  </span>
                </div>

                <div className="text-slate-300 text-[11px]">
                  <span className="text-slate-500">Query: </span>"{round.query}"
                </div>

                {round.scores && round.scores.length > 0 && (
                  <div>
                    <span className="text-slate-500 text-[10px] block mb-1">Rerank Scores (Top {round.scores.length}):</span>
                    <div className="flex flex-wrap gap-1">
                      {round.scores.slice(0, 8).map((sc, scIdx) => (
                        <span
                          key={scIdx}
                          className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                            sc >= 0.40
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {sc.toFixed(4)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
