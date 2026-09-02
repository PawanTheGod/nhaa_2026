import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { responderMockCases } from '../../data/responderMockCases';
import { getSession, RESPONDER_ROLES, ROLE_LABELS } from '../../utils/adminAuth';
import ResponderTaskCard from '../../components/admin/ResponderTaskCard';
import CaseDetailPanel from '../../components/admin/CaseDetailPanel';

export default function ResponderScreen() {
  const session = getSession();
  const [tasks, setTasks] = useState(responderMockCases);
  const [selected, setSelected] = useState(null);

  if (!session) return <Navigate to="/admin/login" replace />;
  if (!RESPONDER_ROLES.includes(session.role)) {
    return <Navigate to="/admin/login" replace />;
  }

  const filtered = tasks.filter((t) => t.role === session.role);
  const pending = filtered.filter((t) => !t.actioned).length;

  const handleMarkActioned = (caseData) => {
    const caseId = caseData.case_id ?? caseData.id;
    setTasks((prev) =>
      prev.map((t) =>
        t.case_id === caseId && t.role === session.role ? { ...t, actioned: true } : t
      )
    );
    setSelected((cur) =>
      cur && (cur.case_id ?? cur.id) === caseId ? { ...cur, actioned: true } : cur
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
          Open a case file to review SVI, AI flags, and checklist — then mark actioned · {pending} pending · {filtered.length} total
        </p>
      </div>

      {filtered.length === 0 ? (
        <p style={{ fontSize: 14, color: '#475569', textAlign: 'center', padding: 40 }} role="status">
          No cases assigned to {ROLE_LABELS[session.role]} at this time.
        </p>
      ) : (
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 16 }} aria-label="Assigned responder tasks">
          {filtered.map((task) => (
            <li key={`${task.case_id}-${task.role}`}>
              <ResponderTaskCard task={task} onOpenCase={setSelected} />
            </li>
          ))}
        </ul>
      )}

      {selected && (
        <CaseDetailPanel
          caseData={selected}
          mode="responder"
          onClose={() => setSelected(null)}
          onMarkActioned={handleMarkActioned}
        />
      )}
    </div>
  );
}
