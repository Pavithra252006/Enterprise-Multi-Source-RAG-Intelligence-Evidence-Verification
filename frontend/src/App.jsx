import React, { useState, useEffect } from 'react';
import TopBar from './components/TopBar';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import EvidenceDrawer from './components/EvidenceDrawer';
import UploadModal from './components/UploadModal';
import EvaluationTab from './components/EvaluationTab';
import LoginPage from './components/LoginPage';
import { USERS, askQuestion, getDocuments, checkHealth, fetchMe, getToken, setToken } from './api';

const toUiUser = (u) => {
  const base = USERS.find((x) => x.role === u.role) || USERS[0];
  return { ...base, name: u.name, label: u.full_name || base.label, employeeId: u.employee_id };
};

export default function App() {
  const [currentUser, setCurrentUser] = useState(null); // null => show login
  const [authChecked, setAuthChecked] = useState(!getToken());
  const [activeTab, setActiveTab] = useState('workspace'); // 'workspace' | 'evaluation'
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [isConnected, setIsConnected] = useState(true);

  // Modal and Drawer States
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedCitationId, setSelectedCitationId] = useState(null);
  const [activeCitations, setActiveCitations] = useState([]);

  // Query and Response States
  const [currentQuery, setCurrentQuery] = useState('');
  const [isLoadingQuery, setIsLoadingQuery] = useState(false);
  const [queryResponse, setQueryResponse] = useState(null);
  const [queryError, setQueryError] = useState(null);

  // Toast Notification
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Fetch initial documents and check backend health
  const refreshDocuments = async () => {
    setIsLoadingDocs(true);
    try {
      const data = await getDocuments();
      setDocuments(data);
      setIsConnected(true);
    } catch (err) {
      console.warn('Could not fetch documents:', err);
      setIsConnected(false);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  useEffect(() => {
    if (!getToken()) return;
    fetchMe()
      .then((u) => setCurrentUser(toUiUser(u)))
      .catch(() => setToken(null))
      .finally(() => setAuthChecked(true));
  }, []);

  useEffect(() => {
    if (!currentUser) return undefined;
    refreshDocuments();
    const interval = setInterval(async () => {
      const h = await checkHealth();
      setIsConnected(h.status === 'ok');
    }, 15000);
    return () => clearInterval(interval);
  }, [currentUser]);

  const handleLoggedIn = (data) => {
    setToken(data.token);
    const u = toUiUser(data.user);
    setCurrentUser(u);
    setActiveTab('workspace');
  };

  const handleLogout = () => {
    setToken(null);
    setCurrentUser(null);
    setQueryResponse(null);
    setCurrentQuery('');
    setActiveCitations([]);
    setIsDrawerOpen(false);
  };

  if (!authChecked) return <div className="min-h-screen bg-slate-950" />;
  if (!currentUser) return <LoginPage onLoggedIn={handleLoggedIn} />;

  // Role permissions
  const canUpload = currentUser.clearance >= 3;
  const canViewEval = currentUser.clearance >= 2;

  // Execute Question
  const handleAsk = async (questionText, userOverride = null) => {
    const userToUse = userOverride || currentUser;
    setCurrentQuery(questionText);
    setIsLoadingQuery(true);
    setQueryError(null);

    try {
      const res = await askQuestion(questionText, userToUse.name, 6);
      setQueryResponse(res);

      // Collect all citations for drawer
      const citations = [];
      const seen = new Set();
      (res.claims || []).forEach((cl) => {
        (cl.citations || []).forEach((cit) => {
          if (!seen.has(cit.id)) {
            seen.add(cit.id);
            citations.push(cit);
          }
        });
      });
      setActiveCitations(citations);
      if (citations.length > 0) {
        setSelectedCitationId(citations[0].id);
      }
    } catch (err) {
      console.error('Ask query error:', err);
      const detail = err.response?.data?.detail || err.message || 'Failed to communicate with RAG pipeline.';
      setQueryError(typeof detail === 'string' ? detail : JSON.stringify(detail));
    } finally {
      setIsLoadingQuery(false);
    }
  };


  // Open specific citation in drawer
  const handleOpenCitation = (citationId) => {
    setSelectedCitationId(citationId);
    setIsDrawerOpen(true);
  };

  const handleUploadSuccess = (result) => {
    showToast(`Ingested "${result.title}" successfully! Rebuilt indexes with ${result.total_indexed_chunks || result.chunks} chunks.`, 'success');
    refreshDocuments();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans select-none antialiased">
      {/* Toast Notification Banner */}
      {toast && (
        <div className="fixed top-4 right-4 z-50 animate-bounce">
          <div className={`px-4 py-3 rounded-xl border text-xs font-semibold shadow-2xl flex items-center gap-2.5 ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 text-emerald-200 border-emerald-700/80 shadow-emerald-950/50'
              : 'bg-indigo-950/90 text-indigo-200 border-indigo-700/80 shadow-indigo-950/50'
          }`}>
            <span className="w-2 h-2 rounded-full bg-current animate-ping" />
            <span>{toast.message}</span>
          </div>
        </div>
      )}

      {/* Top Bar with user switcher & tabs */}
      <TopBar
        currentUser={currentUser}
        onLogout={handleLogout}
        isConnected={isConnected}
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        canViewEval={canViewEval}
      />

      {/* Main Content Area */}
      {activeTab === 'evaluation' && canViewEval ? (
        <EvaluationTab />
      ) : (
        /* Main Workspace: Sidebar + Chat */
        <div className="flex-1 flex overflow-hidden">
          {/* Left Sidebar */}
          <Sidebar
            documents={documents}
            currentUser={currentUser}
            onOpenUpload={canUpload ? () => setIsUploadOpen(true) : null}
            isLoadingDocs={isLoadingDocs}
          />

          {/* Center Main Q&A Area */}
          <main className="flex-1 flex flex-col bg-slate-950/40 overflow-hidden">
            <ChatArea
              currentUser={currentUser}
              onAskQuestion={handleAsk}
              isLoading={isLoadingQuery}
              currentQuery={currentQuery}
              response={queryResponse}
              error={queryError}
              onOpenCitation={handleOpenCitation}
            />
          </main>
        </div>
      )}

      {/* Evidence Slide-Over Drawer */}
      <EvidenceDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        citations={activeCitations}
        selectedCitationId={selectedCitationId}
        onSelectCitation={setSelectedCitationId}
      />

      {/* Ingest Document Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onSuccess={handleUploadSuccess}
      />
    </div>
  );
}
