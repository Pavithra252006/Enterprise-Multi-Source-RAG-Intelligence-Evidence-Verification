import axios from 'axios';

const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE_URL = rawApiUrl.replace(/\/+$/, '');

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000,
});

const TOKEN_KEY = 'rag_token';
export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY));

client.interceptors.request.use((config) => {
  const t = getToken();
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

export async function login(accessCode) {
  const response = await client.post('/api/v1/auth/login', { access_code: accessCode });
  return response.data;
}

export async function fetchMe() {
  const response = await client.get('/api/v1/auth/me');
  return response.data;
}

export const USERS = [
  { id: 1, name: 'intern', label: 'Alex Chen', role: 'Intern', clearance: 1, clearanceLabel: 'Level 1: Public', badgeColor: 'bg-slate-700 text-slate-200' },
  { id: 2, name: 'analyst', label: 'Maya Patel', role: 'Analyst', clearance: 2, clearanceLabel: 'Level 2: Internal', badgeColor: 'bg-blue-900/60 text-blue-200 border border-blue-700/50' },
  { id: 3, name: 'manager', label: 'David Kim', role: 'Manager', clearance: 3, clearanceLabel: 'Level 3: Confidential', badgeColor: 'bg-purple-900/60 text-purple-200 border border-purple-700/50' },
  { id: 4, name: 'executive', label: 'Elena Rostova', role: 'Executive', clearance: 4, clearanceLabel: 'Level 4: Restricted', badgeColor: 'bg-rose-900/60 text-rose-200 border border-rose-700/50' },
];

export async function askQuestion(question, userId, topK = 6) {
  const response = await client.post(
    '/ask',
    { question, top_k: topK },
    {
      headers: {
        'X-User-Id': userId,
      },
    }
  );
  return response.data;
}

export async function getDocuments() {
  const response = await client.get('/documents');
  return response.data;
}

export async function uploadDocument(formData) {
  const response = await client.post('/ingest/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function checkHealth() {
  try {
    const response = await client.get('/health', { timeout: 3000 });
    return response.data;
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function getEvalResults() {
  const response = await client.get('/eval/results');
  return response.data;
}

export async function runEvaluation() {
  const response = await client.post('/eval/run');
  return response.data;
}

export async function fetchSimulationPresets() {
  const response = await client.get('/simulation/presets');
  return response.data;
}

export async function runPolicySimulation(scenario, userId = 'executive') {
  const response = await client.post(
    '/simulation/simulate',
    { scenario, user_id: userId },
    {
      headers: {
        'X-User-Id': userId,
      },
    }
  );
  return response.data;
}

