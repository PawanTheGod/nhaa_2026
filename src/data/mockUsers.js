/**
 * Offline fallback credentials when POST /auth/login is unreachable.
 * Accepts both demo123 and the seed password Test@1234 so UI hints always work.
 *
 * Shape: { username, password?, role, name, district?, state? }
 * password is optional on entries — authenticateMockUser checks ACCEPTED_PASSWORDS.
 */

const ACCEPTED_PASSWORDS = new Set(['demo123', 'Test@1234']);

const OFFICERS = [
  { username: 'operator', role: 'operator', name: 'Priya Sharma', district: 'Central Delhi', state: 'Delhi' },
  { username: 'op_delhi_01', role: 'operator', name: 'Priya Sharma (seed)', district: 'Central Delhi', state: 'Delhi' },
  { username: 'police', role: 'police', name: 'Insp. Rajesh Kumar', district: 'Central Delhi', state: 'Delhi' },
  { username: 'police_delhi_01', role: 'police', name: 'Inspector Ramesh', district: 'Central Delhi', state: 'Delhi' },
  { username: 'dlsa', role: 'dlsa', name: 'Adv. Meena Devi', district: 'Central Delhi', state: 'Delhi' },
  { username: 'dlsa_delhi_01', role: 'dlsa', name: 'Advocate Neha Gupta', district: 'Central Delhi', state: 'Delhi' },
  { username: 'medical', role: 'medical', name: 'Dr. Anil Verma', district: 'Central Delhi', state: 'Delhi' },
  { username: 'medical_delhi_01', role: 'medical', name: 'Dr. Kavita Rao', district: 'Central Delhi', state: 'Delhi' },
  { username: 'counselor', role: 'counselor', name: 'Ms. Kavita Nair', district: 'Central Delhi', state: 'Delhi' },
  { username: 'counselor_delhi_01', role: 'counselor', name: 'Counselor Deepa Nair', district: 'Central Delhi', state: 'Delhi' },
  { username: 'witness', role: 'witness_protection', name: 'Col. Suresh Rao', district: 'Central Delhi', state: 'Delhi' },
  { username: 'witness_protection', role: 'witness_protection', name: 'Major Vikram', district: 'Central Delhi', state: 'Delhi' },
  { username: 'district', role: 'district', name: 'District Nodal Officer', district: 'Central Delhi', state: 'Delhi' },
  { username: 'dist_delhi_01', role: 'district', name: 'District Nodal (seed)', district: 'Central Delhi', state: 'Delhi' },
  { username: 'state', role: 'state', name: 'State Nodal Officer', state: 'Delhi' },
  { username: 'state_delhi_01', role: 'state', name: 'State Nodal (seed)', state: 'Delhi' },
  { username: 'ministry', role: 'ministry', name: 'Ministry Official' },
  { username: 'ministry_01', role: 'ministry', name: 'Ministry Official (seed)' },
];

/** @deprecated Prefer authenticateMockUser — kept for any old imports */
export const MOCK_USERS = OFFICERS.map((u) => ({ ...u, password: 'demo123' }));

export function authenticateMockUser(username, password) {
  if (!ACCEPTED_PASSWORDS.has(password)) return null;
  const user = OFFICERS.find((u) => u.username === username.trim().toLowerCase());
  if (!user) return null;
  return { ...user };
}
