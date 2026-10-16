import React, { useState } from 'react';
import AnswerCard from './AnswerCard';
import AbstentionCard from './AbstentionCard';
import ConflictBanner from './ConflictBanner';
import StatusBanner from './StatusBanner';

export const SAMPLE_QUESTIONS = [
  {
    id: 'remote-work',
    category: 'Contradiction',
    tagColor: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    text: 'How many days per week can Acme Corp employees work remotely?',
    hint: 'Tests v1.0 (2 days) vs v2.0 (3 days) conflict resolution',
  },
  {
    id: 'exec-comp',
    category: 'Restricted (Level 4)',
    tagColor: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
    text: 'What is the executive compensation package and base salary for 2024?',
    hint: 'Intern/Analyst/Manager will abstain; Executive receives verified base salary',
  },
  {
    id: 'headcount',
    category: 'Temporal Conflict',
    tagColor: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
    text: "What is Acme Corp's current workforce headcount?",
    hint: 'Tests outdated 2021 report (290) vs current 2024 count (312)',
  },
  {
    id: 'out-of-scope',
    category: 'Abstention',
    tagColor: 'bg-slate-700 text-slate-300 border-slate-600',
    text: 'What is the capital city of Mars and its atmospheric temperature?',
    hint: 'Ungrounded query triggers zero-leakage uniform abstention',
  },
];

export default function ChatArea({
  currentUser,
  onAskQuestion,
  isLoading,
  currentQuery,
  response,
  error,
  onOpenCitation,
}) {
  const [inputText, setInputText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onAskQuestion(inputText.trim());
  };

  const handleSelectSample = (sampleText) => {
    setInputText(sampleText);
    onAskQuestion(sampleText);
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-65px)] overflow-y-auto p-6 max-w-5xl mx-auto w-full">
      {/* Sample Questions Pills */}
      <div className="mb-6 space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Benchmark Verification Scenarios
          </span>
          <span className="text-[11px] text-slate-500">Click to run against pipeline</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {SAMPLE_QUESTIONS.map((q) => (
            <button
              key={q.id}
              onClick={() => handleSelectSample(q.text)}
              disabled={isLoading}
              className="p-3 rounded-xl bg-slate-900/80 hover:bg-slate-800/80 active:bg-slate-800 border border-slate-800 hover:border-slate-700 text-left transition-all group disabled:opacity-50 cursor-pointer shadow-sm hover:shadow-md"
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border font-mono ${q.tagColor}`}>
                  {q.category}
                </span>
                <svg className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </div>
              <div className="text-xs font-semibold text-slate-200 group-hover:text-white line-clamp-1">
                {q.text}
              </div>
              <div className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                {q.hint}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Query Input Box */}
      <form onSubmit={handleSubmit} className="relative mb-6">
        <div className="relative flex items-center bg-slate-900 border border-slate-800 rounded-2xl shadow-xl focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all p-1.5">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isLoading}
            placeholder={`Ask a question under ${currentUser.role} clearance (Level ${currentUser.clearance})...`}
            className="w-full px-4 py-3 bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer shrink-0"
          >
            {isLoading ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                <span>Evaluating</span>
              </>
            ) : (
              <>
                <span>Verify & Ask</span>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Loading State with Exact Prompt Requirement */}
      {isLoading && (
        <div className="p-8 rounded-2xl border border-indigo-500/30 bg-slate-900/60 backdrop-blur-md shadow-xl text-center space-y-4 my-4 animate-pulse">
          <div className="w-12 h-12 mx-auto rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center">
            <svg className="w-6 h-6 text-indigo-400 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">
              Retrieving, reranking, verifying...
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Executing dense & lexical hybrid search • Filtering to clearance L{currentUser.clearance} • Running BGE reranker & second judge
            </p>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && !isLoading && (
        <div className="p-4 rounded-xl bg-rose-950/70 border border-rose-800 text-rose-200 text-xs flex items-start gap-3 my-4">
          <svg className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="space-y-1">
            <div className="font-semibold text-rose-100">Pipeline Communication Error</div>
            <p className="text-rose-300 leading-relaxed">{error}</p>
          </div>
        </div>
      )}

      {/* Results View */}
      {response && !isLoading && (
        <div className="space-y-4">
          {/* Active Query Pill */}
          <div className="flex items-center gap-2 text-xs text-slate-400 px-1">
            <span className="font-semibold text-slate-500">Query:</span>
            <span className="text-slate-200 font-medium">"{response.question || currentQuery}"</span>
          </div>

          {/* At-a-glance outcome */}
          <StatusBanner response={response} />

          {/* Conflict Banner if detected */}
          {response.conflicts && response.conflicts.length > 0 && (
            <ConflictBanner conflicts={response.conflicts} />
          )}

          {/* Abstention Card OR Answer Card */}
          {response.abstained ? (
            <AbstentionCard
              answer={response.answer}
              currentUser={currentUser}
              question={response.question || currentQuery}
            />
          ) : (
            <AnswerCard
              response={response}
              onOpenCitation={onOpenCitation}
            />
          )}
        </div>
      )}

      {/* Empty State when no query run yet */}
      {!response && !isLoading && !error && (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-500">
          <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-3 shadow-inner">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 className="text-sm font-semibold text-slate-300">Ready for Evidence-Grounded Q&A</h3>
          <p className="text-xs text-slate-500 max-w-md mt-1">
            Choose a benchmark scenario above or type a custom question to inspect hybrid retrieval, version contradiction detection, and clearance-governed abstention.
          </p>
        </div>
      )}
    </div>
  );
}
