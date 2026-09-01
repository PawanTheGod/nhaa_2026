/**
 * API client for NHAA Central Case API.
 *
 * Connects to the FastAPI backend running at VITE_API_URL (default http://localhost:8000).
 * Falls back gracefully when the API is not reachable so the admin panels still render
 * with mock data during development.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${BASE_URL}/api`;

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const opts = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };
  const resp = await fetch(url, opts);
  if (!resp.ok) {
    const err = await resp.text().catch(() => '');
    throw new Error(`API ${resp.status}: ${err || resp.statusText}`);
  }
  return resp.json();
}

/**
 * POST /cases — create a case from any channel.
 * @param {object} caseData  { channel_of_origin, district, state, incident_description, ... }
 * @param {object} opts      { role, district, state } for audit
 */
export async function createCase(caseData, opts = {}) {
  const params = new URLSearchParams(opts).toString();
  const qs = params ? `?${params}` : '';
  return request(`/cases/${qs}`, { method: 'POST', body: JSON.stringify(caseData) });
}

/**
 * GET /cases — list cases, filterable by role/district/state.
 * @param {object} params { role, district, state, status, risk_tier, limit, offset }
 */
export async function listCases(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/cases/?${qs}`);
}

/**
 * GET /cases/{id} — full case detail including risk assessments.
 */
export async function getCase(caseId) {
  return request(`/cases/${caseId}`);
}

/**
 * PATCH /cases/{id} — update case status or assign officer.
 */
export async function updateCase(caseId, patchData, opts = {}) {
  const params = new URLSearchParams(opts).toString();
  const qs = params ? `?${params}` : '';
  return request(`/cases/${caseId}?${qs}`, {
    method: 'PATCH',
    body: JSON.stringify(patchData),
  });
}

/**
 * POST /risk-assessments — called by AI module.
 */
export async function createRiskAssessment(raData, actor = 'ai_module') {
  return request(`/risk-assessments/?actor=${encodeURIComponent(actor)}`, {
    method: 'POST',
    body: JSON.stringify(raData),
  });
}

/**
 * GET risk assessments for a case.
 */
export async function getRiskAssessments(caseId) {
  return request(`/risk-assessments/case/${caseId}`);
}

/**
 * WebSocket connection to /ws for real-time updates.
 */
export function connectWebSocket(onMessage) {
  const wsUrl = (BASE_URL.replace(/^http/, 'ws')) + '/ws';
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  ws.onerror = (err) => console.warn('WebSocket error:', err);
  ws.onclose = () => console.log('WebSocket disconnected');
  return ws;
}

/**
 * Fetch a single channel's cases from the API, with a simulated channel delay.
 * Used by the synchronization test on the frontend side.
 */
export async function simulateChannelCase(channel, district, state, description) {
  return createCase(
    {
      channel_of_origin: channel,
      district,
      state,
      incident_description: description,
      is_silent_signal: Math.random() > 0.7,
    },
    { role: 'operator', district, state }
  );
}

/**
 * GET /stats/cases — aggregate statistics for admin dashboards.
 */
export async function getCaseStats(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/stats/cases?${qs}`);
}

/**
 * GET /stats/trend — weekly trend of case volume and avg SVI.
 */
export async function getCaseTrend(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/stats/trend?${qs}`);
}

/**
 * GET /stats/districts — district-level comparison table.
 */
export async function getDistrictComparison(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/stats/districts?${qs}`);
}

/**
 * GET /stats/states — state-by-state comparison for the Ministry dashboard.
 */
export async function getStateComparison() {
  return request('/stats/states');
}

export { BASE_URL, API_BASE };