/**
 * API client for NHAA Central Case API.
 *
 * Connects to the FastAPI backend at VITE_API_URL (default http://localhost:8000).
 * Admin routes require Authorization: Bearer <JWT> from POST /auth/login.
 */

import { getAuthHeaders, clearSession } from '../utils/adminAuth';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${BASE_URL}/api`;

async function request(path, options = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const opts = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options.headers,
    },
  };
  const resp = await fetch(url, opts);
  if (resp.status === 401) {
    // Token expired / invalid — clear so LoginScreen can take over
    clearSession();
  }
  if (!resp.ok) {
    const err = await resp.text().catch(() => '');
    throw new Error(`API ${resp.status}: ${err || resp.statusText}`);
  }
  if (resp.status === 204) return null;
  return resp.json();
}

/**
 * POST /auth/login — live Supabase-backed officer auth.
 * Accepts JSON { username, password }; returns token + role claims.
 */
export async function loginOfficer(username, password) {
  const resp = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!resp.ok) {
    const err = await resp.text().catch(() => '');
    throw new Error(err || `Login failed (${resp.status})`);
  }
  return resp.json();
}

/**
 * POST /cases — create a case from any channel.
 */
export async function createCase(caseData, opts = {}) {
  const params = new URLSearchParams(opts).toString();
  const qs = params ? `?${params}` : '';
  return request(`/cases/${qs}`, { method: 'POST', body: JSON.stringify(caseData) });
}

/**
 * GET /api/cases — JWT-scoped list (Aditya admin_panel).
 * @param {object} params { status, risk_tier, district, state, limit, offset }
 */
export async function listCases(params = {}) {
  const cleaned = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== '')
  );
  const qs = new URLSearchParams(cleaned).toString();
  return request(`/cases${qs ? `?${qs}` : ''}`);
}

/**
 * GET /api/cases/{id} — case detail.
 */
export async function getCase(caseId) {
  return request(`/cases/${caseId}`);
}

/**
 * GET /api/cases/{id}/full — case + history timeline.
 */
export async function getFullCase(caseId) {
  return request(`/cases/${caseId}/full`);
}

/**
 * GET /api/cases/{id}/allowed-actions → { allowed_actions: string[] }
 */
export async function getAllowedActions(caseId) {
  return request(`/cases/${caseId}/allowed-actions`);
}

/**
 * POST /api/cases/{id}/action — submit engine action string
 * e.g. escalate_to_district, assign_operator, dispatch_police, resolve
 */
export async function postCaseAction(caseId, action, notes) {
  return request(`/cases/${caseId}/action`, {
    method: 'POST',
    body: JSON.stringify({ action, notes: notes || undefined }),
  });
}

/**
 * PATCH /api/decisions/{id}/actioned — responder mark actioned
 */
export async function markCaseActioned(caseId, payload = {}) {
  return request(`/decisions/${caseId}/actioned`, {
    method: 'PATCH',
    body: JSON.stringify({
      actioned: true,
      responder_type: payload.responder_type,
      notes: payload.notes,
    }),
  });
}

/**
 * PATCH /cases/{id} — update case status or assign officer.
 */
export async function updateCase(caseId, patchData, opts = {}) {
  const params = new URLSearchParams(opts).toString();
  const qs = params ? `?${params}` : '';
  return request(`/cases/${caseId}${qs}`, {
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
 * GET /cases/{id}/notifications — dispatch log for a case.
 */
export async function getCaseNotifications(caseId) {
  return request(`/cases/${caseId}/notifications`);
}

/**
 * POST /cases/{id}/officer-decision — Critical-tier notification gate (Pushp).
 */
export async function confirmOfficerDecision(caseId, confirmedBy) {
  return request(`/cases/${caseId}/officer-decision`, {
    method: 'POST',
    body: JSON.stringify({ confirmed_by: confirmedBy }),
  });
}

/**
 * WebSocket connection to /ws for real-time updates.
 */
export function connectWebSocket(onMessage) {
  const wsUrl = `${BASE_URL.replace(/^http/, 'ws')}/ws`;
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
 * SIH presentation helper: create labelled [DEMO] cases with nested flags,
 * then escalate one to district so judges see status + current_level.
 */
export async function restoreDemoData() {
  const { DEMO_CASES, DEMO_DISTRICT, DEMO_STATE } = await import('../data/demoPresentationCases');
  const created = [];

  for (const demo of DEMO_CASES) {
    const { ra, escalate_to: escalateTo, ...caseFields } = demo;
    const caseRow = await createCase(caseFields, {
      role: 'operator',
      district: DEMO_DISTRICT,
      state: DEMO_STATE,
    });
    const caseId = caseRow.id ?? caseRow.case_id;
    await createRiskAssessment(
      {
        case_id: caseId,
        svi_score: ra.svi_score,
        risk_tier: ra.risk_tier,
        flags: ra.flags,
        explanation_text: ra.explanation_text,
        model_version: ra.model_version,
        recommended_action: ra.recommended_action,
      },
      'demo_seed'
    );
    if (escalateTo) {
      try {
        await postCaseAction(caseId, escalateTo, 'SIH demo seed');
      } catch {
        // Escalate needs JWT; continue so other cases still load
      }
    }
    created.push(caseId);
  }

  return { count: created.length, caseIds: created };
}

export async function getCaseStats(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/stats/cases?${qs}`);
}

export async function getCaseTrend(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/stats/trend?${qs}`);
}

export async function getDistrictComparison(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/stats/districts?${qs}`);
}

export async function getStateComparison() {
  return request('/stats/states');
}

export { BASE_URL, API_BASE };
