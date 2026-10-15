import React from 'react';
import { USERS } from '../api';

export default function TopBar({ currentUser, onSelectUser, isConnected }) {
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

      {/* User Switcher & Status */}
      <div className="flex items-center gap-4">
        {/* Backend health status pill */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-rose-400 shadow-sm shadow-rose-400/50'} animate-pulse`} />
          <span className="text-slate-300 font-medium">{isConnected ? 'Backend 8000' : 'Connecting...'}</span>
        </div>

        {/* User clearance switcher */}
        <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <div className="flex items-center gap-1.5 pl-2 pr-1 text-xs text-slate-400">
            <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="font-semibold text-slate-300">Identity:</span>
          </div>

          <div className="flex gap-1">
            {USERS.map((user) => {
              const active = currentUser.name === user.name;
              return (
                <button
                  key={user.name}
                  onClick={() => onSelectUser(user)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                    active
                      ? `${user.badgeColor} shadow-md`
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                  title={`${user.label} (${user.role}) - Clearance Level ${user.clearance}`}
                >
                  <span>{user.role}</span>
                  <span className={`text-[10px] px-1 py-0.2 rounded font-mono ${active ? 'bg-black/30' : 'bg-slate-800 text-slate-400'}`}>
                    L{user.clearance}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </header>
  );
}
