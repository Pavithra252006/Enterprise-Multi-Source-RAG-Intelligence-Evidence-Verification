import React, { useState } from 'react';
import { uploadDocument } from '../api';

export default function UploadModal({ isOpen, onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [version, setVersion] = useState('1.0');
  const [docDate, setDocDate] = useState(new Date().toISOString().slice(0, 10));
  const [accessLevel, setAccessLevel] = useState(1);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      if (!title) {
        // Strip extension for a clean default title
        const cleanName = selected.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' ');
        setTitle(cleanName);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMsg('Please select a file to ingest.');
      return;
    }
    if (!title.trim()) {
      setErrorMsg('Please enter a document title.');
      return;
    }

    setIsUploading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title.trim());
    formData.append('version', version.trim() || '1.0');
    formData.append('doc_date', docDate);
    formData.append('access_level', parseInt(accessLevel, 10));

    try {
      const res = await uploadDocument(formData);
      setIsUploading(false);
      onSuccess(res);
      onClose();
    } catch (err) {
      setIsUploading(false);
      const detail = err.response?.data?.detail || err.message || 'Ingestion failed.';
      setErrorMsg(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div>
              <h2 className="text-base font-bold text-white m-0">Ingest New Document</h2>
              <p className="text-xs text-slate-400 m-0">Upload to vector index with clearance classification</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
              <svg className="w-4 h-4 shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{errorMsg}</span>
            </div>
          )}

          {/* File input dropzone */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Document File (.pdf, .xlsx, .csv, .html, .txt)
            </label>
            <div className="relative border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-4 text-center cursor-pointer transition-colors bg-slate-950/50">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.xlsx,.xls,.csv,.html,.htm,.txt"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div className="space-y-1">
                <svg className="w-8 h-8 mx-auto text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div className="text-xs text-slate-300 font-medium">
                  {file ? file.name : 'Click or drag file here'}
                </div>
                <div className="text-[10px] text-slate-500">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Maximum 50MB per file'}
                </div>
              </div>
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Document Title
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Acme Corp Travel Policy v3.0"
              className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {/* Version and Date */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Version
              </label>
              <input
                type="text"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                placeholder="1.0"
                className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Document Date
              </label>
              <input
                type="date"
                required
                value={docDate}
                onChange={(e) => setDocDate(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Access Level Classification */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Access Clearance Classification
            </label>
            <select
              value={accessLevel}
              onChange={(e) => setAccessLevel(Number(e.target.value))}
              className="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option value={1}>Level 1: Public (All Employees & External)</option>
              <option value={2}>Level 2: Internal (Analysts, Managers, Executives)</option>
              <option value={3}>Level 3: Confidential (Managers & Executives Only)</option>
              <option value={4}>Level 4: Restricted (Board & Executives Only)</option>
            </select>
            <p className="text-[10px] text-slate-500 mt-1">
              Strictly enforced before reranking and generation. Unauthorized tiers will receive no trace or citation of this file.
            </p>
          </div>

          {/* Modal Actions */}
          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              disabled={isUploading}
              className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isUploading}
              className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 rounded-lg shadow-md shadow-indigo-600/20 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {isUploading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  <span>Ingesting & Indexing...</span>
                </>
              ) : (
                <span>Ingest Document</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
