import React from 'react';

export default function AbstentionCard({ answer, currentUser, question }) {
  return (
    <div className="rounded-2xl border border-rose-800/60 bg-gradient-to-b from-rose-950/30 via-slate-900 to-slate-950 p-7 shadow-2xl space-y-6 text-left my-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shadow-inner">
            <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Access-Controlled Abstention
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                Zero-Leakage Policy
              </span>
            </div>
            <h2 className="text-base font-semibold text-slate-200 m-0">
              Response Withheld
            </h2>
          </div>
        </div>

        <div className="text-right">
          <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${currentUser.badgeColor}`}>
            Active Clearance: Level {currentUser.clearance} ({currentUser.role})
          </span>
        </div>
      </div>

      {/* Main Abstention Message */}
      <div className="p-5 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-2">
        <div className="text-lg font-bold text-slate-100 tracking-tight leading-snug">
          "{answer || 'Insufficient evidence in the sources you can access.'}"
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          The pipeline evaluated the corpus under role <strong className="text-slate-300">{currentUser.role}</strong> and clearance <strong className="text-slate-300">Level {currentUser.clearance}</strong>.
        </p>
      </div>

      {/* Governance & Information Protection Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-800/60 space-y-1">
          <div className="font-semibold text-slate-300 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
            Clearance Boundary Protection
          </div>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            Chunks exceeding your clearance level are excluded before reranking and before LLM generation. No metadata, citation, or title is leaked.
          </p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-800/60 space-y-1">
          <div className="font-semibold text-slate-300 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
            Uniform Abstention Guarantee
          </div>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            Identical abstention responses are issued whether a document is restricted or entirely absent, mitigating timing and inference attacks.
          </p>
        </div>
      </div>
    </div>
  );
}
