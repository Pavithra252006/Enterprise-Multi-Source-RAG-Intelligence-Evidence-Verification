import React from 'react';

const LEVEL_COLORS = {
  1: 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60',
  2: 'bg-blue-950/80 text-blue-300 border-blue-700/60',
  3: 'bg-purple-950/80 text-purple-300 border-purple-700/60',
  4: 'bg-rose-950/80 text-rose-300 border-rose-700/60',
};

export default function EvidenceDrawer({
  isOpen,
  onClose,
  citations = [],
  selectedCitationId,
  onSelectCitation,
}) {
  if (!isOpen) return null;

  const activeCitation = citations.find((c) => c.id === selectedCitationId) || citations[0];

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-xs animate-fade-in">
      <div className="w-full max-w-xl bg-slate-900 border-l border-slate-800 h-full shadow-2xl flex flex-col transform transition-transform duration-300 ease-out">
        {/* Drawer Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-sm font-bold text-white m-0">Evidence Inspector</h2>
              <p className="text-xs text-slate-400 m-0">Strictly grounded citation passages</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Citation Selector Tabs if multiple citations */}
        {citations.length > 1 && (
          <div className="px-6 py-2.5 border-b border-slate-800 bg-slate-950/30 flex items-center gap-2 overflow-x-auto">
            <span className="text-xs text-slate-400 font-semibold mr-1">Citations:</span>
            {citations.map((c) => {
              const isSelected = activeCitation && activeCitation.id === c.id;
              return (
                <button
                  key={c.id}
                  onClick={() => onSelectCitation(c.id)}
                  className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold transition-all ${
                    isSelected
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  [{c.id}] {c.title?.slice(0, 18)}...
                </button>
              );
            })}
          </div>
        )}

        {/* Drawer Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeCitation ? (
            <div className="space-y-4">
              {/* Document Metadata Card */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    Evidence [{activeCitation.id}]
                  </span>

                  {/* Outdated / Superseded Badge */}
                  {(activeCitation.title?.includes('v1.0') || activeCitation.title?.includes('2021') || activeCitation.title?.includes('Outdated')) && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1">
                      <svg className="w-3 h-3 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      Outdated / Superseded
                    </span>
                  )}
                </div>

                <div className="text-sm font-semibold text-white leading-snug">
                  {activeCitation.title}
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 pt-1 border-t border-slate-800/80">
                  <div>
                    <span className="text-slate-500">Version: </span>
                    <span className="font-mono text-slate-300 font-medium">v{activeCitation.version || '1.0'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Date: </span>
                    <span className="font-mono text-slate-300">{activeCitation.date || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Location: </span>
                    <span className="font-mono text-slate-300">{activeCitation.location || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Security: </span>
                    <span className="font-mono text-emerald-400">Verified Clearance</span>
                  </div>
                </div>
              </div>

              {/* Exact Verbatim Snippet Passages */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider m-0">
                    Verbatim Document Passage
                  </h3>
                  <span className="text-[10px] text-slate-500">Exact ground truth</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono leading-relaxed text-slate-200 whitespace-pre-wrap select-text">
                  {activeCitation.snippet}
                </div>
              </div>

              {/* Verification Context Alert */}
              <div className="p-3 rounded-lg bg-indigo-950/30 border border-indigo-900/40 text-indigo-300 text-xs flex items-start gap-2.5">
                <svg className="w-4 h-4 shrink-0 text-indigo-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="space-y-1">
                  <div className="font-semibold text-slate-200">Grounded Citation Rule</div>
                  <div className="text-[11px] text-slate-400">
                    This passage passed strict clearance gating prior to cross-encoder reranking. Claims generated from this document were validated by the independent second judge.
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-500 text-xs py-12">
              No evidence selected. Click an inline citation chip [E1] to inspect.
            </div>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs text-slate-400">
          <span>{citations.length} cited sources total</span>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-medium transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
