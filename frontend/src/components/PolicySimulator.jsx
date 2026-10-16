import React, { useState, useEffect } from 'react';
import { fetchSimulationPresets, runPolicySimulation } from '../api';

const SEVERITY_CONFIG = {
  CRITICAL: {
    bg: 'bg-rose-950/70',
    border: 'border-rose-700/80',
    text: 'text-rose-300',
    badge: 'bg-rose-900/60 text-rose-200 border-rose-600',
    iconColor: 'text-rose-400',
  },
  HIGH: {
    bg: 'bg-amber-950/70',
    border: 'border-amber-700/80',
    text: 'text-amber-300',
    badge: 'bg-amber-900/60 text-amber-200 border-amber-600',
    iconColor: 'text-amber-400',
  },
  MEDIUM: {
    bg: 'bg-yellow-950/60',
    border: 'border-yellow-700/70',
    text: 'text-yellow-300',
    badge: 'bg-yellow-900/50 text-yellow-200 border-yellow-600',
    iconColor: 'text-yellow-400',
  },
  LOW: {
    bg: 'bg-emerald-950/60',
    border: 'border-emerald-700/70',
    text: 'text-emerald-300',
    badge: 'bg-emerald-900/50 text-emerald-200 border-emerald-600',
    iconColor: 'text-emerald-400',
  },
};

export default function PolicySimulator({ currentUser }) {
  const [presets, setPresets] = useState([]);
  const [scenarioInput, setScenarioInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeDetailTab, setActiveDetailTab] = useState('conflicts'); // 'conflicts' | 'docs' | 'ops' | 'amendments' | 'roles'

  useEffect(() => {
    fetchSimulationPresets()
      .then((data) => {
        setPresets(data);
        if (data && data.length > 0) {
          // Default to the first preset for immediate preview
          setScenarioInput(data[0].scenario_text);
        }
      })
      .catch((err) => console.warn('Could not load presets:', err));
  }, []);

  const handleSelectPreset = (p) => {
    setScenarioInput(p.scenario_text);
    executeSimulation(p.scenario_text);
  };

  const executeSimulation = async (scenarioToRun) => {
    const text = scenarioToRun || scenarioInput;
    if (!text || !text.trim()) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await runPolicySimulation(text.trim(), currentUser?.name || 'executive');
      setResult(data);
    } catch (err) {
      console.error('Simulation error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to execute counterfactual simulation.');
    } finally {
      setIsLoading(false);
    }
  };

  const severityStyle = result?.severity ? SEVERITY_CONFIG[result.severity] || SEVERITY_CONFIG.MEDIUM : SEVERITY_CONFIG.MEDIUM;

  return (
    <div className="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-950 text-slate-100 flex flex-col gap-6">
      {/* Top Banner */}
      <div className="rounded-2xl border border-indigo-900/50 bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-slate-900/80 p-6 shadow-2xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Counterfactual Engine
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Clearance: {currentUser?.clearanceLabel || 'Level 4: Executive'}
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white mt-2">
              What-If Corporate Policy Simulator
            </h2>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Test hypothetical policy shifts, vendor cancellations, and headcount adjustments before enacting them.
              The engine traversals institutional rules to forecast downstream contradictions, operational shifts, and required amendments.
            </p>
          </div>

          <div className="flex items-center gap-3 self-start md:self-auto">
            <button
              onClick={() => executeSimulation()}
              disabled={isLoading || !scenarioInput.trim()}
              className="px-5 py-2.5 rounded-xl font-semibold text-xs tracking-wide uppercase transition flex items-center gap-2 shadow-lg bg-gradient-to-r from-purple-600 via-indigo-600 to-indigo-700 hover:from-purple-500 hover:to-indigo-600 text-white disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {isLoading ? (
                <>
                  <svg className="w-4 h-4 animate-spin text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  <span>Simulating...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>Run Simulation</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preset Clickable Scenario Pills */}
        <div className="mt-5 pt-4 border-t border-slate-800/80">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span>Preset Enterprise Scenarios (Click to test):</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {presets.map((p) => {
              const isSelected = scenarioInput === p.scenario_text;
              return (
                <button
                  key={p.id}
                  onClick={() => handleSelectPreset(p)}
                  className={`text-left p-3 rounded-xl border text-xs transition relative overflow-hidden group cursor-pointer ${
                    isSelected
                      ? 'bg-purple-950/80 border-purple-500/80 text-purple-200 shadow-md shadow-purple-950/40'
                      : 'bg-slate-900/70 border-slate-800/80 text-slate-300 hover:bg-slate-800/70 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-[12px] group-hover:text-purple-300 transition">
                      {p.title}
                    </span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono">
                      {p.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                    {p.short_desc}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Scenario Input Box */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 shadow-xl">
        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
          <span>Hypothetical Policy Scenario</span>
          <span className="text-[11px] font-normal text-slate-500">Edit or enter any custom scenario</span>
        </label>
        <div className="relative">
          <textarea
            value={scenarioInput}
            onChange={(e) => setScenarioInput(e.target.value)}
            rows={2}
            placeholder="e.g. What if we reduce the domestic travel daily expense reimbursement limit from $200 to $100 per day?"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500/80 focus:ring-1 focus:ring-purple-500/80 transition"
          />
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl border border-rose-800/80 bg-rose-950/40 text-rose-300 text-xs flex items-center gap-3">
          <svg className="w-5 h-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <div className="font-bold">Simulation Error</div>
            <div>{error}</div>
          </div>
        </div>
      )}

      {/* Loading state skeleton */}
      {isLoading && (
        <div className="p-12 text-center flex flex-col items-center justify-center gap-3 bg-slate-900/40 rounded-2xl border border-slate-800">
          <div className="w-12 h-12 rounded-full border-4 border-purple-500/20 border-t-purple-500 animate-spin" />
          <div className="text-sm font-semibold text-white">Traversing Multi-Source Document Dependency Trees...</div>
          <div className="text-xs text-slate-400 max-w-md">
            Scanning Handbook v1 & v2, IT Security Policy, Active Contracts, and Headcount models for downstream friction points.
          </div>
        </div>
      )}

      {/* Result Dashboard */}
      {!isLoading && result && (
        <div className="flex flex-col gap-6">
          {/* Executive Briefing Card */}
          <div className={`p-6 rounded-2xl border ${severityStyle.border} ${severityStyle.bg} shadow-2xl relative overflow-hidden`}>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider border ${severityStyle.badge}`}>
                  {result.severity} Risk
                </span>
                <h3 className="text-lg font-bold text-white m-0">
                  {result.scenario_title}
                </h3>
              </div>
              <span className="text-xs font-mono text-slate-400">
                Forensic Impact Analysis
              </span>
            </div>

            <p className="text-sm text-slate-200 mt-3 leading-relaxed max-w-4xl">
              {result.summary}
            </p>

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-4 border-t border-slate-800/60">
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                <div className="text-[10px] font-semibold text-slate-400 uppercase">Impacted Sources</div>
                <div className="text-xl font-bold text-white mt-0.5">{result.affected_documents?.length || 0}</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                <div className="text-[10px] font-semibold text-slate-400 uppercase">Ripple Conflicts</div>
                <div className="text-xl font-bold text-rose-400 mt-0.5">{result.ripple_conflicts?.length || 0}</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                <div className="text-[10px] font-semibold text-slate-400 uppercase">Operational Shifts</div>
                <div className="text-xl font-bold text-amber-400 mt-0.5">{result.operational_impacts?.length || 0}</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                <div className="text-[10px] font-semibold text-slate-400 uppercase">Policy Amendments</div>
                <div className="text-xl font-bold text-indigo-400 mt-0.5">{result.recommended_amendments?.length || 0}</div>
              </div>
            </div>
          </div>

          {/* Interactive Navigation Tabs */}
          <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
            {[
              { id: 'conflicts', label: 'Downstream Conflicts', icon: '⚡', count: result.ripple_conflicts?.length },
              { id: 'docs', label: 'Impacted Documents', icon: '📑', count: result.affected_documents?.length },
              { id: 'ops', label: 'Operational & Financial Impact', icon: '📊', count: result.operational_impacts?.length },
              { id: 'amendments', label: 'Recommended Amendments', icon: '✍️', count: result.recommended_amendments?.length },
              { id: 'roles', label: 'Role & Clearance Matrix', icon: '👥', count: result.role_impact_matrix?.length },
            ].map((tab) => {
              const isActive = activeDetailTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveDetailTab(tab.id)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-2 cursor-pointer ${
                    isActive
                      ? 'bg-purple-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent hover:border-slate-800'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                  {tab.count !== undefined && (
                    <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${isActive ? 'bg-purple-800 text-purple-200' : 'bg-slate-800 text-slate-400'}`}>
                      {tab.count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Detail Tab 1: Conflicts */}
          {activeDetailTab === 'conflicts' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(result.ripple_conflicts || []).map((c, i) => (
                <div key={i} className="p-5 rounded-2xl border border-rose-900/50 bg-slate-900/70 flex flex-col justify-between shadow-lg">
                  <div>
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-white text-sm">{c.conflict_title}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full border border-rose-800 bg-rose-950/80 text-rose-300">
                        {c.severity}
                      </span>
                    </div>
                    <div className="text-[11px] font-semibold text-purple-400 mt-2">
                      Target: {c.target_doc}
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-300 mt-2 font-mono">
                      <span className="text-slate-500">Current Rule: </span>{c.conflicting_rule}
                    </div>
                    <p className="text-xs text-slate-300 mt-3 leading-relaxed">
                      <span className="font-semibold text-rose-300">Downstream Impact: </span>{c.hypothetical_impact}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Detail Tab 2: Affected Documents */}
          {activeDetailTab === 'docs' && (
            <div className="grid grid-cols-1 gap-3">
              {(result.affected_documents || []).map((d, i) => (
                <div key={i} className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-white text-sm">{d.title}</span>
                      {d.version && <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">v{d.version}</span>}
                      {d.doc_date && <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">{d.doc_date}</span>}
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
                        Level {d.access_level}
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/70 text-xs text-slate-300 mt-2.5 font-mono">
                      "{d.clause_excerpt}"
                    </div>
                  </div>
                  <div className="shrink-0">
                    <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider border ${
                      d.impact_level === 'CRITICAL' ? 'bg-rose-950 text-rose-300 border-rose-800' : 'bg-amber-950 text-amber-300 border-amber-800'
                    }`}>
                      {d.impact_level} Impact
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Detail Tab 3: Operational Impact */}
          {activeDetailTab === 'ops' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {(result.operational_impacts || []).map((op, i) => (
                <div key={i} className="p-5 rounded-2xl border border-slate-800 bg-slate-900/70 flex flex-col justify-between shadow-lg">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-purple-950/80 text-purple-300 border border-purple-800/80">
                      {op.category}
                    </span>
                    {op.metric_delta && (
                      <div className="text-lg font-mono font-bold text-emerald-400 mt-3">
                        {op.metric_delta}
                      </div>
                    )}
                    <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                      {op.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Detail Tab 4: Amendments */}
          {activeDetailTab === 'amendments' && (
            <div className="grid grid-cols-1 gap-4">
              {(result.recommended_amendments || []).map((am, i) => (
                <div key={i} className="p-5 rounded-2xl border border-indigo-900/40 bg-slate-900/80 shadow-lg">
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <span className="font-bold text-white text-sm">{am.doc_name}</span>
                      <span className="text-xs text-indigo-400 font-mono ml-2">({am.section})</span>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
                      {am.priority} Priority
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                    <div className="p-3 rounded-xl bg-slate-950/90 border border-rose-950/60">
                      <div className="text-[10px] font-bold text-rose-400 uppercase tracking-wider mb-1">Current Clause</div>
                      <div className="text-xs text-slate-300 font-mono leading-relaxed">{am.current_clause}</div>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/90 border border-emerald-950/60">
                      <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-1">Proposed Revision</div>
                      <div className="text-xs text-slate-200 font-mono leading-relaxed">{am.proposed_clause}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Detail Tab 5: Role Impact Matrix */}
          {activeDetailTab === 'roles' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {(result.role_impact_matrix || []).map((r, i) => (
                <div key={i} className="p-4 rounded-xl border border-slate-800 bg-slate-900/70 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">{r.role}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                        Level {r.clearance}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-2.5 leading-relaxed">
                      {r.impact_summary}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
