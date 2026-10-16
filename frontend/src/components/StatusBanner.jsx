import React from 'react';

/**
 * Big at-a-glance verdict banner so every outcome looks different:
 *  VERIFIED (green tick) | CONTRADICTION RESOLVED (amber) | PARTIAL (blue) | ABSTAINED (red lock)
 */
export function getOutcome(response) {
  const conflicts = response.conflicts?.length || 0;
  const conf = response.confidence ?? 0;
  if (response.abstained) return 'abstained';
  if (conflicts > 0) return 'contradiction';
  if (conf >= 0.99) return 'verified';
  return 'partial';
}

const THEMES = {
  verified: {
    wrap: 'border-emerald-500/60 bg-gradient-to-r from-emerald-950/80 via-emerald-900/30 to-slate-900/80 shadow-emerald-500/20 anim-glow-green',
    badge: 'bg-emerald-500 text-emerald-950',
    title: 'text-emerald-300',
    label: 'VERIFIED',
  },
  contradiction: {
    wrap: 'border-amber-500/60 bg-gradient-to-r from-amber-950/80 via-amber-900/20 to-slate-900/80 shadow-amber-500/20',
    badge: 'bg-amber-400 text-amber-950',
    title: 'text-amber-300',
    label: 'CONTRADICTION RESOLVED',
  },
  partial: {
    wrap: 'border-sky-500/60 bg-gradient-to-r from-sky-950/80 via-sky-900/20 to-slate-900/80 shadow-sky-500/20',
    badge: 'bg-sky-400 text-sky-950',
    title: 'text-sky-300',
    label: 'PARTIALLY VERIFIED',
  },
  abstained: {
    wrap: 'border-rose-500/60 bg-gradient-to-r from-rose-950/80 via-rose-900/20 to-slate-900/80 shadow-rose-500/20',
    badge: 'bg-rose-500 text-rose-950',
    title: 'text-rose-300',
    label: 'ABSTAINED',
  },
};

function Icon({ kind }) {
  if (kind === 'verified')
    return (
      <svg className="w-9 h-9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={3.2}>
        <path className="anim-draw" strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    );
  if (kind === 'contradiction')
    return (
      <svg className="w-9 h-9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.4}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 7h12M8 7l3-3M8 7l3 3M16 17H4m12 0l-3-3m3 3l-3 3" />
      </svg>
    );
  if (kind === 'partial')
    return (
      <svg className="w-9 h-9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v5m0 3h.01M10.3 3.9L2.4 18a2 2 0 001.7 3h15.8a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z" />
      </svg>
    );
  return (
    <svg className="w-9 h-9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.4}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>
  );
}

export default function StatusBanner({ response }) {
  const kind = getOutcome(response);
  const t = THEMES[kind];
  const conf = Math.round((response.confidence ?? 0) * 100);
  const conflicts = response.conflicts?.length || 0;
  const ms = response.retrieval_trace?.elapsed_ms;
  const cached = response.retrieval_trace?.cached;

  const subtitle = {
    verified: `Every claim is backed by cited evidence \u2014 ${conf}% evidence match, no conflicts.`,
    contradiction: `${conflicts} conflicting source${conflicts > 1 ? 's' : ''} found \u2014 the newest authoritative source was used.`,
    partial: `Some claims are only partly supported (${conf}% match). Review the citations.`,
    abstained: 'Not enough accessible evidence \u2014 the answer is withheld to protect restricted data.',
  }[kind];

  return (
    <div className={`anim-pop flex items-center gap-4 rounded-2xl border-2 px-5 py-4 shadow-xl ${t.wrap}`}>
      <div className={`shrink-0 w-14 h-14 rounded-full flex items-center justify-center ${t.badge} ${kind === 'verified' ? 'anim-ring' : ''}`}>
        <Icon kind={kind} />
      </div>
      <div className="flex-1 min-w-0">
        <div className={`text-lg font-extrabold tracking-wide ${t.title}`}>{t.label}</div>
        <div className="text-xs text-slate-300 leading-snug">{subtitle}</div>
      </div>
      <div className="shrink-0 text-right space-y-1">
        {!response.abstained && (
          <div className={`text-2xl font-black ${t.title}`}>{conf}%</div>
        )}
        {ms != null && (
          <div className="text-[11px] font-mono text-slate-400">
            {cached ? '\u26A1 instant \u00B7 ' : ''}{ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`}
          </div>
        )}
      </div>
    </div>
  );
}
