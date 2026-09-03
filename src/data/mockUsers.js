/**
 * Offline fallback credentials when POST /auth/login is unreachable.
 * Accepts both demo123 and the seed password Test@1234.
 */

const ACCEPTED_PASSWORDS = new Set(['demo123', 'Test@1234']);

const OFFICERS = [
  // ── Real Indian Police Hierarchy ──
  { username: 'operator', role: 'operator', name: 'Priya Sharma (Operator)', district: 'Central Delhi', state: 'Delhi' },
  { username: 'dsp', role: 'dsp', name: 'DSP Rajesh Kumar', district: 'Central Delhi', state: 'Delhi' },
  { username: 'sp', role: 'sp', name: 'SP Anand Singh', state: 'Delhi' },
  { username: 'ig', role: 'ig', name: 'IG Priya Mehta' },

  // Compatibility aliases
  { username: 'op_delhi_01', role: 'operator', name: 'Priya Sharma', district: 'Central Delhi', state: 'Delhi' },
  { username: 'dsp_delhi_01', role: 'dsp', name: 'DSP Rajesh Kumar', district: 'Central Delhi', state: 'Delhi' },
  { username: 'sp_delhi_01', role: 'sp', name: 'SP Anand Singh', state: 'Delhi' },
  { username: 'ig_01', role: 'ig', name: 'IG Priya Mehta' },
];

export const MOCK_USERS = OFFICERS.map((u) => ({ ...u, password: 'demo123' }));

export function authenticateMockUser(username, password) {
  if (!ACCEPTED_PASSWORDS.has(password)) return null;
  const user = OFFICERS.find((u) => u.username === username.trim().toLowerCase());
  if (!user) return null;
  return { ...user };
}
