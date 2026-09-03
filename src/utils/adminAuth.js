const SESSION_KEY = 'nhaa_admin_session';

/** No separate responder roles — all roles are in the police hierarchy. */
export const RESPONDER_ROLES = [];

/**
 * Real Indian Police hierarchy:
 * operator (Call Centre) → dsp (Dy. SP) → sp (Superintendent) → ig (Inspector General)
 */
export const ALL_ROLES = ['operator', 'dsp', 'sp', 'ig'];

export const ROLE_LABELS = {
  operator: 'Call Centre Operator',
  dsp: 'DSP (Dy. Superintendent of Police)',
  sp: 'SP (Superintendent of Police)',
  ig: 'IG (Inspector General of Police)',
};

export const ROLE_REDIRECTS = {
  operator: '/admin/operator',
  dsp: '/admin/dsp',
  sp: '/admin/sp',
  ig: '/admin/ig',
};

export function getSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setSession(user) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

export function getToken() {
  return getSession()?.token || null;
}

export function getAuthHeaders() {
  const token = getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export function getRedirectForRole(role) {
  return ROLE_REDIRECTS[role] || '/admin/login';
}
