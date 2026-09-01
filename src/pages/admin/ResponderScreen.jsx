import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { responderMockCases } from '../../data/responderMockCases';
import { getSession, RESPONDER_ROLES, ROLE_LABELS } from '../../utils/adminAuth';
import ResponderTaskCard from '../../components/admin/ResponderTaskCard';

export default function ResponderScreen() {
  const session = getSession();
  const [tasks, setTasks] = useState(responderMockCases);

  if (!session) return <Navigate to="/admin/login" replace />;
  if (!RESPONDER_ROLES.includes(session.role)) {
    return <Navigate to="/admin/login" replace />;
  }

  const filtered = tasks.filter((t) => t.responder_type === session.role);
  const pending = filtered.filter((t) => !t.actioned).length;

  const handleMarkActioned = (caseId) => {
    setTasks((prev) =>
      prev.map((t) =>
        t.case_id === caseId && t.responder_type === session.role ? { ...t, actioned: true } : t
      )
    );
  };

  return (
    <div style={{ marginTop: 24 }}>
      <div
        role="region"
        aria-labelledby="responder-summary-heading"
        style={{
          background: '#EEF2FF',
          border: '1px solid #CBD5E1',
          borderRadius: 12,
          padding: '16px 20px',
          marginBottom: 24,
        }}
      >
        <h2 id="responder-summary-heading" style={{ margin: '0 0 6px', fontSize: 18, fontWeight: 800, color: '#003366' }}>
          {ROLE_LABELS[session.role]} — Assigned Cases
        </h2>
        <p style={{ margin: 0, fontSize: 13, color: '#475569' }} aria-live="polite">
          Showing only cases assigned to your responder role · {pending} pending · {filtered.length} total
        </p>
      </div>

      {filtered.length === 0 ? (
        <p style={{ fontSize: 14, color: '#475569', textAlign: 'center', padding: 40 }} role="status">
          No cases assigned to {ROLE_LABELS[session.role]} at this time.
        </p>
      ) : (
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 16 }} aria-label="Assigned responder tasks">
          {filtered.map((task) => (
            <li key={`${task.case_id}-${task.responder_type}`}>
              <ResponderTaskCard
                task={task}
                onMarkActioned={handleMarkActioned}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
