const SESSION_KEY = 'nhaa_admin_session';

export const RESPONDER_ROLES = ['police', 'dlsa', 'medical', 'counselor', 'witness_protection'];

export const ROLE_LABELS = {
  operator: 'Call Centre Operator',
  police: 'Police (SHO / IO)',
  dlsa: 'District Legal Services Authority',
  medical: 'District Hospital / Medical Officer',
  counselor: 'Counsellor / One-Stop Centre',
  witness_protection: 'Witness Protection Cell',
  district: 'District Nodal Officer',
  state: 'State Nodal Officer',
  ministry: 'Ministry Oversight (MoSJE)',
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

export function getRedirectForRole(role) {
  const routes = {
    operator: '/admin/operator',
    police: '/admin/responder',
    dlsa: '/admin/responder',
    medical: '/admin/responder',
    counselor: '/admin/responder',
    witness_protection: '/admin/responder',
    district: '/admin/district',
    state: '/admin/state',
    ministry: '/admin/ministry',
  };
  return routes[role] || '/admin/login';
}
