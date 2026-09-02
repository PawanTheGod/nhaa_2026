const SESSION_KEY = 'nhaa_admin_session';

/** Five agency roles that share /admin/responder (filtered by session.role). */
export const RESPONDER_ROLES = ['police', 'dlsa', 'medical', 'counselor', 'witness_protection'];

/**
 * All 9 officer_role enum values (Vinit schema).
 * operator | district | state | ministry | police | dlsa | medical | counselor | witness_protection
 */
export const ALL_ROLES = [
  'operator',
  'district',
  'state',
  'ministry',
  'police',
  'dlsa',
  'medical',
  'counselor',
  'witness_protection',
];

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

/** Explicit post-login redirect for every role value. */
export const ROLE_REDIRECTS = {
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

export function getSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setSession(user) {
  // Persist role so Responder can filter assigned cases by session.role
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

export function getRedirectForRole(role) {
  return ROLE_REDIRECTS[role] || '/admin/login';
}
