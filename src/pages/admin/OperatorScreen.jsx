import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import {
  listCases,
  connectWebSocket,
  getCaseNotifications,
  confirmOfficerDecision,
} from '../../services/api';
import { operatorMockCases } from '../../data/operatorMockCases';
import { getSession } from '../../utils/adminAuth';
import CaseTable from '../../components/admin/CaseTable';
import CaseDetailPanel from '../../components/admin/CaseDetailPanel';

function apiToCase(row) {
  const ra = row.risk_assessments?.[0];
  return {
    ...row,
    id: row.id,
    case_id: row.id,
    svi_score: row.svi_score ?? ra?.svi_score,
    risk_tier: row.risk_tier ?? ra?.risk_tier,
    explanation_text: ra?.explanation_text,
    flags: ra?.flags,
    recommended_action: row.recommended_action,
    notifications: [],
  };
}

export default function OperatorScreen() {
  const session = getSession();
  const [cases, setCases] = useState(operatorMockCases);
  const [selected, setSelected] = useState(null);
  const [useMock, setUseMock] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [confirmStatus, setConfirmStatus] = useState(null); // { caseId, state: 'sending'|'done'|'error' }

  useEffect(() => {
    if (!session || session.role !== 'operator') return undefined;

    let ws;
    let cancelled = false;

    const load = async () => {
      try {
        const data = await listCases({
          role: 'operator',
          district: session.district || 'Central Delhi',
          state: session.state || 'Delhi',
          limit: 100,
        });
        if (!cancelled) {
          if (data?.length) {
            setCases(data.map(apiToCase));
            setUseMock(false);
          } else {
            // Empty API ΓÇö use mock demo data (no test rows in database)
            setCases(operatorMockCases);
            setUseMock(true);
          }
        }
      } catch {
        if (!cancelled) {
          setCases(operatorMockCases);
          setUseMock(true);
        }
      }
    };

    load();

    try {
      ws = connectWebSocket((msg) => {
        if (cancelled) return;
        if (msg.event === 'case_created') {
          setCases((prev) => [apiToCase(msg.data), ...prev]);
        }
        if (msg.event === 'case_updated' || msg.event === 'risk_assessment_created') {
          setCases((prev) =>
            prev.map((c) => {
              const id = c.id ?? c.case_id;
              if (id === msg.data.id || id === msg.data.case_id) {
                return { ...c, ...apiToCase(msg.data) };
              }
              return c;
            })
          );
        }
        // Notification service events (Pushp): refresh the notification log
        // for whichever case is currently open, live, no manual refresh.
        if (msg.event === 'notifications_created' || msg.event === 'notifications_dispatched') {
          const affectedCaseId = msg.data?.case_id;
          setSelected((prev) => {
            const prevId = prev?.id ?? prev?.case_id;
            if (!prev || prevId !== affectedCaseId) return prev;
            getCaseNotifications(affectedCaseId)
              .then((notifs) => {
                setSelected((cur) => (cur ? { ...cur, notifications: notifs } : cur));
              })
              .catch(() => {});
            return prev;
          });
        }
      });
      ws.onopen = () => setWsConnected(true);
    } catch {
      setWsConnected(false);
    }

    return () => {
      cancelled = true;
      ws?.close();
    };
  }, [session]);

  if (!session) return <Navigate to="/admin/login" replace />;
  if (session.role !== 'operator') return <Navigate to="/admin/login" replace />;

  // Opens the case detail panel and, if we're on the live API (not mock
  // data), fetches the real notification log so the panel shows actual
  // pending/sent rows instead of an empty list.
  const handleViewCase = async (caseData) => {
    setSelected(caseData);
    if (useMock) return;
    const id = caseData.id ?? caseData.case_id;
    try {
      const notifications = await getCaseNotifications(id);
      setSelected((cur) => (cur && (cur.id ?? cur.case_id) === id ? { ...cur, notifications } : cur));
    } catch {
      // Notifications endpoint unreachable ΓÇö panel just shows "no agencies
      // notified yet", which is a safe fallback, not a crash.
    }
  };

  // The human-confirmation gate. This is the ONLY thing that can move a
  // Critical-tier notification from pending -> sent. Calls the real
  // POST /api/cases/{id}/officer-decision endpoint (Pushp's hard gate).
  const handleConfirmAction = async (caseData) => {
    const id = caseData.id ?? caseData.case_id;
    const confirmedBy = session?.name || session?.username || `${session?.role || 'operator'}_${session?.district || 'unknown'}`;

    setConfirmStatus({ caseId: id, state: 'sending' });
    try {
      const dispatched = await confirmOfficerDecision(id, confirmedBy);
      setConfirmStatus({ caseId: id, state: 'done', count: dispatched.length });

      // Refresh the notification log in place so the officer sees the
      // pending rows flip to "sent" without closing the panel.
      setSelected((cur) => (cur && (cur.id ?? cur.case_id) === id ? { ...cur, notifications: dispatched } : cur));
    } catch (err) {
      setConfirmStatus({ caseId: id, state: 'error', message: err.message });
    }
  };

  return (
    <div style={{ marginTop: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <p style={{ margin: 0, fontSize: 13, color: '#475569' }} role="status" aria-live="polite">
          {useMock ? 'Showing mock data' : 'Live API'} ┬╖ WebSocket: {wsConnected ? 'connected' : 'offline'}
        </p>
        <span style={{ fontSize: 12, fontWeight: 700, color: '#065F46', background: '#D1FAE5', padding: '4px 12px', borderRadius: 999 }}>
          {cases.length} cases in queue
        </span>
      </div>

      <CaseTable cases={cases} onViewCase={handleViewCase} />

      {selected && (
        <CaseDetailPanel
          caseData={selected}
          onClose={() => {
            setSelected(null);
            setConfirmStatus(null);
          }}
          onConfirmAction={handleConfirmAction}
        />
      )}

      {confirmStatus?.state === 'sending' && (
        <div role="status" aria-live="polite" style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 300, background: '#1E293B', color: '#fff', padding: '10px 16px', borderRadius: 8, fontSize: 13 }}>
          Confirming actionΓÇª
        </div>
      )}
      {confirmStatus?.state === 'done' && (
        <div role="status" aria-live="polite" style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 300, background: '#065F46', color: '#fff', padding: '10px 16px', borderRadius: 8, fontSize: 13 }}>
          Action confirmed ΓÇö {confirmStatus.count} agencies notified.
        </div>
      )}
      {confirmStatus?.state === 'error' && (
        <div role="alert" style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 300, background: '#991B1B', color: '#fff', padding: '10px 16px', borderRadius: 8, fontSize: 13 }}>
          Could not confirm: {confirmStatus.message}
        </div>
      )}
    </div>
  );
}
