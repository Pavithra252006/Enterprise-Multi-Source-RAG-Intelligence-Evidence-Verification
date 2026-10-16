import React from 'react';

export default function TopBar({ currentUser, onLogout, isConnected, activeTab, onSelectTab, canViewEval = true, onQuickSwitch }) {
  return (
    <header className="sticky top-0 z-30 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
      {/* Brand & Title */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/20">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold tracking-tight text-white m-0 p-0 leading-tight">
              Enterprise Intelligence & Evidence Verification
            </h1>
            <span className="text-[11px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              PS-019 RAG
            </span>
          </div>
          <p className="text-xs text-slate-400 m-0 p-0 mt-0.5">
            Clearance-Gated Retrieval • Cross-Encoder Rerank • Contradiction Resolution
          </p>
        </div>
      </div>

      {/* Center Tab Navigation */}
      <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => onSelectTab('workspace')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeTab === 'workspace'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span>Q&A Workspace</span>
        </button>

        {canViewEval && (
          <button
            onClick={() => onSelectTab('simulation')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'simulation'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <svg className="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            <span className="flex items-center gap-1.5">
              <span>Policy Simulator</span>
              <span className="px-1.5 py-0.2 text-[9px] font-bold bg-purple-400/20 text-purple-300 border border-purple-400/30 rounded">NEW</span>
            </span>
          </button>
        )}

        {canViewEval && <button
          onClick={() => onSelectTab('evaluation')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeTab === 'evaluation'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span>Evaluation</span>
        </button>}
      </div>

      {/* User Switcher & Status */}
      <div className="flex items-center gap-4">
        {/* Backend health status pill */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-rose-400 shadow-sm shadow-rose-400/50'} animate-pulse`} />
          <span className="text-slate-300 font-medium">{isConnected ? 'Backend 8000' : 'Connecting...'}</span>
        </div>

        {/* Quick Clearance Switcher */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <span className="text-[10px] uppercase font-bold text-slate-500 px-2 tracking-wider">Clearance:</span>
          {[
            { code: 'EMP-1001', role: 'Intern', lvl: 1, label: 'L1: Intern', activeBg: 'bg-slate-700 text-white' },
            { code: 'EMP-2001', role: 'Analyst', lvl: 2, label: 'L2: Analyst', activeBg: 'bg-blue-600 text-white' },
            { code: 'EMP-3001', role: 'Manager', lvl: 3, label: 'L3: Manager', activeBg: 'bg-purple-600 text-white' },
            { code: 'EMP-4001', role: 'Executive', lvl: 4, label: 'L4: Exec', activeBg: 'bg-rose-600 text-white' },
          ].map((p) => {
            const isActive = currentUser.clearance === p.lvl;
            return (
              <button
                key={p.code}
                onClick={() => onQuickSwitch && onQuickSwitch(p.code)}
                title={`Switch clearance to ${p.role} (${p.code})`}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition cursor-pointer ${
                  isActive
                    ? `${p.activeBg} shadow-sm font-bold scale-105`
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
                }`}
              >
                {p.label}
              </button>
            );
          })}
        </div>

        {/* Logged-in user badge & logout */}
        <div className="flex items-center gap-2 bg-slate-950 p-1 pl-3 rounded-xl border border-slate-800">
          <div className="flex flex-col leading-tight">
            <span className="text-xs font-semibold text-slate-200">{currentUser.label}</span>
            <span className="text-[10px] text-slate-500">{currentUser.employeeId ? `${currentUser.employeeId} · ` : ''}{currentUser.clearanceLabel}</span>
          </div>
          <button
            id="logout-btn"
            onClick={onLogout}
            title="Log out"
            className="px-2.5 py-1 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-rose-600/80 transition cursor-pointer"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
