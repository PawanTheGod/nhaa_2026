/**
 * Mock officer credentials for admin login (Step 7).
 * Replace with Aditya's JWT login endpoint in Step 12.
 *
 * Shape: { username, password, role, name, district?, state? }
 */
export const MOCK_USERS = [
  { username: 'operator', password: 'demo123', role: 'operator', name: 'Priya Sharma', district: 'Central Delhi', state: 'Delhi' },
  { username: 'police', password: 'demo123', role: 'police', name: 'Insp. Rajesh Kumar', district: 'Central Delhi', state: 'Delhi' },
  { username: 'dlsa', password: 'demo123', role: 'dlsa', name: 'Adv. Meena Devi', district: 'Central Delhi', state: 'Delhi' },
  { username: 'medical', password: 'demo123', role: 'medical', name: 'Dr. Anil Verma', district: 'Central Delhi', state: 'Delhi' },
  { username: 'counselor', password: 'demo123', role: 'counselor', name: 'Ms. Kavita Nair', district: 'Central Delhi', state: 'Delhi' },
  { username: 'witness', password: 'demo123', role: 'witness_protection', name: 'Col. Suresh Rao', district: 'Central Delhi', state: 'Delhi' },
  { username: 'district', password: 'demo123', role: 'district', name: 'District Nodal Officer', district: 'Central Delhi', state: 'Delhi' },
  { username: 'state', password: 'demo123', role: 'state', name: 'State Nodal Officer', state: 'Delhi' },
  { username: 'ministry', password: 'demo123', role: 'ministry', name: 'Ministry Official' },
];

export function authenticateMockUser(username, password) {
  const user = MOCK_USERS.find(
    (u) => u.username === username.trim().toLowerCase() && u.password === password
  );
  if (!user) return null;
  const { password: _, ...safeUser } = user;
  return safeUser;
}
