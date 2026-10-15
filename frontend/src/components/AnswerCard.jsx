import React from 'react';
import ReactMarkdown from 'react-markdown';
import PipelineTrace from './PipelineTrace';

export default function AnswerCard({
  response,
  onOpenCitation,
}) {
  if (!response) return null;

  const {
    answer,
    confidence = 0.0,
    claims = [],
    retrieval_trace,
  } = response;

  // Confidence badge color mapping
  const getConfidenceBadge = (conf) => {
    if (conf >= 0.8) {
      return {
        label: `High Confidence (${(conf * 100).toFixed(0)}%)`,
        style: 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60 shadow-sm shadow-emerald-900/30',
        icon: (
          <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
          </svg>
        ),
      };
    }
    if (conf >= 0.6) {
      return {
        label: `Moderate Confidence (${(conf * 100).toFixed(0)}%)`,
        style: 'bg-amber-950/80 text-amber-300 border-amber-700/60 shadow-sm shadow-amber-900/30',
        icon: (
          <svg className="w-3.5 h-3.5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        ),
      };
    }
    return {
      label: `Low Confidence (${(conf * 100).toFixed(0)}%)`,
      style: 'bg-rose-950/80 text-rose-300 border-rose-700/60 shadow-sm shadow-rose-900/30',
      icon: (
        <svg className="w-3.5 h-3.5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
        </svg>
      ),
    };
  };

  const confBadge = getConfidenceBadge(confidence);

  // Extract all citations from claims for inline mapping
  const allCitations = [];
  const citationMap = {};
  claims.forEach((cl) => {
    (cl.citations || []).forEach((c) => {
      if (!citationMap[c.id]) {
        citationMap[c.id] = c;
        allCitations.push(c);
      }
    });
  });

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/90 shadow-2xl p-6 space-y-6 text-left my-4 animate-fade-in">
      {/* Answer Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h2 className="text-base font-bold text-white m-0 leading-tight">
              Grounded Intelligence Synthesis
            </h2>
            <p className="text-xs text-slate-400 m-0">Strictly backed by access-cleared evidence</p>
          </div>
        </div>

        {/* Confidence Badge */}
        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold ${confBadge.style}`}>
          {confBadge.icon}
          <span>{confBadge.label}</span>
        </div>
      </div>

      {/* Answer Text Body with Markdown & Inline Chips */}
      <div className="text-slate-100 text-sm leading-relaxed space-y-3 prose prose-invert max-w-none">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>

      {/* Quick Citation Chips Bar */}
      {allCitations.length > 0 && (
        <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 font-semibold flex items-center gap-1">
            <svg className="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" />
            </svg>
            Cited Sources:
          </span>
          {allCitations.map((cit) => (
            <button
              key={cit.id}
              onClick={() => onOpenCitation(cit.id)}
              className="px-2.5 py-1 rounded-lg bg-indigo-950/50 hover:bg-indigo-900/60 text-indigo-300 border border-indigo-700/50 hover:border-indigo-500 text-xs font-mono transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
              title={`Click to inspect verbatim passage from ${cit.title}`}
            >
              <span className="font-bold">[{cit.id}]</span>
              <span className="truncate max-w-[200px]">{cit.title}</span>
              {cit.location && <span className="text-indigo-400/70 text-[10px]">({cit.location})</span>}
            </button>
          ))}
        </div>
      )}

      {/* Claim Rows & Second-Judge Verdicts */}
      {claims.length > 0 && (
        <div className="space-y-3 pt-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider m-0 flex items-center gap-1.5">
              <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Second-Judge Claim Verification ({claims.length} claims)
            </h3>
            <span className="text-[10px] text-slate-500">Evaluated independently via strict Claude judge</span>
          </div>

          <div className="space-y-2.5">
            {claims.map((claim, idx) => {
              const isSupported = claim.verdict === 'SUPPORTED';
              const isPartial = claim.verdict === 'PARTIAL';

              const verdictStyle = isSupported
                ? 'bg-emerald-950/70 text-emerald-300 border-emerald-800'
                : isPartial
                ? 'bg-amber-950/70 text-amber-300 border-amber-800'
                : 'bg-rose-950/70 text-rose-300 border-rose-800';

              return (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2 text-xs"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="text-slate-100 font-medium leading-snug">
                      {claim.text}
                    </div>
                    {/* Verdict Icon Pill */}
                    <span className={`shrink-0 px-2.5 py-0.5 rounded-full border text-[10px] font-bold tracking-wider font-mono uppercase flex items-center gap-1 ${verdictStyle}`}>
                      {isSupported ? (
                        <>
                          <svg className="w-3 h-3 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                          SUPPORTED
                        </>
                      ) : isPartial ? (
                        <>
                          <svg className="w-3 h-3 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          PARTIAL
                        </>
                      ) : (
                        <>
                          <svg className="w-3 h-3 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          UNSUPPORTED
                        </>
                      )}
                    </span>
                  </div>

                  {/* Supporting quote span or reason */}
                  {claim.supporting_span && (
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 text-[11px] font-mono leading-relaxed">
                      <span className="text-slate-500 font-sans block text-[10px] uppercase font-bold">Supporting Quote Span:</span>
                      "{claim.supporting_span}"
                    </div>
                  )}

                  {/* Citations row */}
                  {claim.citations && claim.citations.length > 0 && (
                    <div className="flex flex-wrap items-center gap-2 pt-1">
                      <span className="text-[10px] text-slate-500">Cited:</span>
                      {claim.citations.map((c) => (
                        <button
                          key={c.id}
                          onClick={() => onOpenCitation(c.id)}
                          className="px-2 py-0.5 rounded bg-slate-900 hover:bg-slate-800 text-indigo-300 border border-slate-700 text-[11px] font-mono transition-colors cursor-pointer"
                        >
                          [{c.id}] {c.title?.slice(0, 24)}... {c.location && `(${c.location})`}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Collapsible Pipeline Trace */}
      <PipelineTrace trace={retrieval_trace} />
    </div>
  );
}
