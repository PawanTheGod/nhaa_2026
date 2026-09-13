/**
 * Desk Clearance Scope — NHAA RBAC Hierarchy
 *
 * Each role maps to the set of admin route prefixes it is allowed to visit.
 * Higher roles include all lower desks they supervise.
 *
 * L-0    operator  → operator desk only
 * L-0.5  io        → io desk only
 * L-1    dsp/acp   → dsp, acp, io, operator
 * L-2    sp        → sp + all L-1 and below
 * L-3    ig        → ig + all L-2 and below
 * L-3+   director  → director + all police desks
 * L-4    judiciary → judiciary only (independent legal authority)
 * L-5    swo       → swo only (welfare desk, independent)
 * SYSTEM sysadmin  → ALL routes
 */

export const ROLE_CLEARANCE = {
  operator:  ['/admin/operator'],
  io:        ['/admin/io'],
  dsp:       ['/admin/dsp', '/admin/io', '/admin/operator'],
  acp:       ['/admin/acp', '/admin/dsp', '/admin/io', '/admin/operator'],
  sp:        ['/admin/sp', '/admin/acp', '/admin/dsp', '/admin/io', '/admin/operator'],
  ig:        ['/admin/ig', '/admin/sp', '/admin/acp', '/admin/dsp', '/admin/io', '/admin/operator'],
  director:  ['/admin/director', '/admin/ig', '/admin/sp', '/admin/acp', '/admin/dsp', '/admin/io', '/admin/operator'],
  judiciary: ['/admin/judiciary'],
  swo:       ['/admin/swo'],
  sysadmin:  ['*'], // wildcard — all routes
};

/**
 * Returns true if the given role is allowed to access the given pathname.
 * @param {string} role - The logged-in user's role
 * @param {string} pathname - The current route (e.g. '/admin/dsp')
 */
export function hasRouteAccess(role, pathname) {
  if (!role) return false;
  const allowed = ROLE_CLEARANCE[role];
  if (!allowed) return false;
  if (allowed.includes('*')) return true;
  return allowed.some((prefix) => pathname.startsWith(prefix));
}

/**
 * Returns the primary (home) route for a given role.
 * Used to redirect unauthorised access back to the user's own desk.
 */
export function getHomeRoute(role) {
  const clearance = ROLE_CLEARANCE[role];
  if (!clearance) return '/admin/login';
  if (clearance.includes('*')) return '/admin/sysadmin';
  return clearance[0];
}

/**
 * Roles that should NOT see the credential quick-select tiles on the login page.
 * Senior/independent roles must type their own departmental IDs.
 */
export const SENIOR_ROLES = new Set(['director', 'ig', 'judiciary', 'swo', 'sysadmin']);
