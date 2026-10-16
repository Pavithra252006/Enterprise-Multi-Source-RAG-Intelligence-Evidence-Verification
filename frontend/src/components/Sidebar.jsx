import React, { useState } from 'react';

const LEVEL_COLORS = {
  1: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60',
  2: 'bg-blue-950/60 text-blue-300 border-blue-800/60',
  3: 'bg-purple-950/60 text-purple-300 border-purple-800/60',
  4: 'bg-rose-950/60 text-rose-300 border-rose-800/60',
};

const LEVEL_NAMES = {
  1: 'Public',
  2: 'Internal',
  3: 'Confidential',
  4: 'Restricted',
};

export default function Sidebar({
  documents = [],
  currentUser,
  onOpenUpload,
  onSelectDocument,
  isLoadingDocs,
}) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredDocs = documents.filter((doc) =>
    doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (doc.source && doc.source.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <aside className="w-80 shrink-0 bg-slate-900/60 border-r border-slate-800 flex flex-col h-[calc(100vh-65px)]">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider m-0">
              Corpus Sources
            </h2>
          </div>
          <span className="text-xs font-mono font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {documents.length} docs
          </span>
        </div>

        {/* Upload Trigger Button */}
        {onOpenUpload && <button
          onClick={onOpenUpload}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all cursor-pointer"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Ingest New Document</span>
        </button>}

        {/* Search Input */}
        <div className="relative">
          <input
            type="text"
            placeholder="Filter corpus files..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-1.5 pl-8 text-xs rounded-lg bg-slate-950 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
          />
          <svg className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Document Items List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {isLoadingDocs && documents.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs animate-pulse">
            Loading corpus documents...
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            No matching documents found.
          </div>
        ) : (
          filteredDocs.map((doc) => {
            const hasAccess = currentUser.clearance >= doc.access_level;
            const isSuperseded = doc.title.toLowerCase().includes('v1.0') || doc.title.toLowerCase().includes('outdated');

            return (
              <div
                key={doc.id}
                onClick={() => onSelectDocument && onSelectDocument(doc)}
                className={`p-3 rounded-xl border transition-all text-left cursor-pointer ${
                  hasAccess
                    ? 'bg-slate-950/70 hover:bg-slate-800/50 border-slate-800/80 hover:border-slate-700'
                    : 'bg-slate-950/30 border-slate-800/40 opacity-60 hover:opacity-80'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="font-medium text-xs text-slate-200 leading-snug line-clamp-2">
                    {doc.title}
                  </div>
                  {/* Access Status Icon */}
                  {hasAccess ? (
                    <span title="Accessible to your clearance level">
                      <svg className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </span>
                  ) : (
                    <span title={`Requires Clearance Level ${doc.access_level} (${LEVEL_NAMES[doc.access_level]})`}>
                      <svg className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </span>
                  )}
                </div>

                {/* Metadata Row */}
                <div className="flex flex-wrap items-center gap-1.5 mt-2 text-[10px]">
                  <span className={`px-1.5 py-0.5 rounded border font-mono font-medium ${LEVEL_COLORS[doc.access_level]}`}>
                    L{doc.access_level} {LEVEL_NAMES[doc.access_level]}
                  </span>

                  {doc.version && (
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                      v{doc.version}
                    </span>
                  )}

                  {doc.doc_date && (
                    <span className="text-slate-500">
                      {doc.doc_date}
                    </span>
                  )}

                  {isSuperseded && (
                    <span className="px-1 py-0.5 rounded bg-amber-950/70 text-amber-400 border border-amber-800/60 font-semibold text-[9px]">
                      SUPERSEDED
                    </span>
                  )}

                  <span className="ml-auto text-slate-500 font-mono">
                    {doc.chunk_count} chunks
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Sidebar Footer with current user clearance summary */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/60 text-[11px] text-slate-400 flex items-center justify-between">
        <span>Active Clearance:</span>
        <span className={`px-2 py-0.5 rounded font-mono font-semibold text-[10px] ${currentUser.badgeColor}`}>
          Level {currentUser.clearance} ({currentUser.role})
        </span>
      </div>
    </aside>
  );
}
