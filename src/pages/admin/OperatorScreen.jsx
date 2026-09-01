import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { listCases, connectWebSocket } from '../../services/api';
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
            // Empty API — use mock demo data (no test rows in database)
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

  const handleConfirmAction = (caseData) => {
    window.alert(
      `Critical action confirmation logged for NHAA-${caseData.id ?? caseData.case_id}. ` +
        'Aditya\'s decision endpoint will dispatch after human confirmation (Step 12).'
    );
  };

  return (
    <div style={{ marginTop: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <p style={{ margin: 0, fontSize: 13, color: '#475569' }} role="status" aria-live="polite">
          {useMock ? 'Showing mock data' : 'Live API'} · WebSocket: {wsConnected ? 'connected' : 'offline'}
        </p>
        <span style={{ fontSize: 12, fontWeight: 700, color: '#065F46', background: '#D1FAE5', padding: '4px 12px', borderRadius: 999 }}>
          {cases.length} cases in queue
        </span>
      </div>

      <CaseTable cases={cases} onViewCase={setSelected} />

      {selected && (
        <CaseDetailPanel
          caseData={selected}
          onClose={() => setSelected(null)}
          onConfirmAction={handleConfirmAction}
        />
      )}
    </div>
  );
}
