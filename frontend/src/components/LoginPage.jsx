import React, { useState } from 'react';
import { login, checkHealth } from '../api';

export default function LoginPage({ onLoggedIn }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;
    setLoading(true);
    setError('');
    try {
      const data = await login(code.trim());
      onLoggedIn(data);
    } catch (err) {
      if (!err.response) {
        const h = await checkHealth();
        setError(h.status === 'ok' ? 'Unexpected error.' : 'Cannot reach the server. Is the backend running on port 8000?');
      } else {
        setError(err.response?.data?.detail || 'Login failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100 px-4 relative overflow-hidden">
      <div className="absolute -top-40 -left-40 w-[28rem] h-[28rem] rounded-full bg-indigo-600/20 blur-3xl" />
      <div className="absolute -bottom-40 -right-40 w-[28rem] h-[28rem] rounded-full bg-pink-600/10 blur-3xl" />

      <form
        onSubmit={submit}
        className="relative w-full max-w-md bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-2xl p-8 shadow-2xl"
      >
        <div className="flex flex-col items-center text-center mb-7">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/20 mb-4">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
              <svg className="w-7 h-7 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0-1.1.9-2 2-2s2 .9 2 2v1h-4v-1zM7 12h10v7H7z M9 12V8a3 3 0 016 0v4" />
              </svg>
            </div>
          </div>
          <h1 className="text-xl font-bold text-white m-0">Enterprise Intelligence Portal</h1>
          <p className="text-xs text-slate-400 mt-1.5">Sign in with the access code issued by your company.</p>
        </div>

        <label htmlFor="access-code" className="block text-xs font-semibold text-slate-300 mb-1.5">
          Employee access code
        </label>
        <input
          id="access-code"
          type="password"
          autoFocus
          autoComplete="off"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Enter your access code"
          className="w-full px-3.5 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
        />

        {error && (
          <div className="mt-3 text-xs text-rose-300 bg-rose-950/50 border border-rose-800/60 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        <button
          id="login-submit"
          type="submit"
          disabled={loading || !code.trim()}
          className="mt-5 w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold shadow-md shadow-indigo-600/20 transition-all"
        >
          {loading ? 'Verifying…' : 'Sign in'}
        </button>

        <p className="text-[11px] text-slate-500 text-center mt-5 mb-0">
          No account? Contact your administrator — self-registration is disabled.
        </p>

        <details className="mt-4 text-[11px] text-slate-500">
          <summary className="cursor-pointer text-slate-400 hover:text-slate-300">Prototype demo codes (one per employee)</summary>
          <ul className="mt-2 space-y-1 font-mono list-none p-0">
            <li>AC-7Q4M-2K9X — Alex Chen, Intern</li>
            <li>MP-9T2L-5H7B — Maya Patel, Analyst</li>
            <li>DK-1R5Y-7Z2G — David Kim, Manager</li>
            <li>ER-6X1A-9M5T — Elena Rostova, Executive</li>
          </ul>
        </details>
      </form>
    </div>
  );
}
