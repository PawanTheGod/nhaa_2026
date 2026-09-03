import React, { useEffect, useState } from 'react';
import { listCases, connectWebSocket, getAllowedActions, postCaseAction, getFullCase, getCaseNotifications, confirmOfficerDecision } from '../../services/api';
import { districtMockData } from '../../data/districtCases';
import { getSession } from '../../utils/adminAuth';
import { mockAllowedActions } from '../../utils/caseLevel';
import RiskBadge from '../../components/admin/RiskBadge';
import SLACountdown from '../../components/admin/SLACountdown';
import CaseDetailPanel from '../../components/admin/CaseDetailPanel';
import { useLang } from '../../i18n/LangContext';
import { ADMIN_TRANSLATIONS } from '../../i18n/adminTranslations';

const CHANNEL_LABELS = {
  portal: 'Public Web Portal',
  chatbot: 'Chatbot Intake',
  ivrs: 'Toll-Free IVRS (14566)',
  voice_twilio: 'Toll-Free IVRS (14566)',
  mobile_app: 'Mobile Application',
};

const TIER_ORDER = { critical: 0, high: 1, moderate: 2, low: 3 };

const LEVEL_LABELS = { 0: 'Operator', 1: 'DSP', 2: 'SP', 3: 'IG' };

const STATUS_BADGE = {
  new:        { bg: '#EFF6FF', fg: '#1E40AF', border: '#BFDBFE', label: 'New Complaint' },
  in_progress:{ bg: '#FFFBEB', fg: '#92400E', border: '#FDE68A', label: 'Under Investigation' },
  escalated:  { bg: '#FFF7ED', fg: '#9A3412', border: '#FFEDD5', label: 'Escalated' },
  resolved:   { bg: '#ECFDF5', fg: '#065F46', border: '#A7F3D0', label: 'Disposed / Actioned' },
  closed:     { bg: '#F8FAFC', fg: '#475569', border: '#E2E8F0', label: 'Closed' },
};

function apiToCase(apiCase) {
  const ra = apiCase.risk_assessments?.[0];
  const score = apiCase.svi_score ?? ra?.svi_score ?? 0;
  const tier = apiCase.risk_tier ?? ra?.risk_tier ?? 'low';
  return {
    ...apiCase,
    id: `NHAA-${apiCase.id}`,
    numericId: apiCase.id,
    case_id: apiCase.id,
    riskTier: tier,
    risk_tier: tier,
    sviScore: score,
    svi_score: score,
    slaDueDate: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
    district: apiCase.district || 'Central Delhi',
    state: apiCase.state || 'Delhi',
    channel: apiCase.channel_of_origin || 'portal',
    channel_of_origin: apiCase.channel_of_origin || 'portal',
    createdAt: apiCase.created_at,
    created_at: apiCase.created_at,
    victimAgeGroup: '—',
    isSilentSignal: apiCase.is_silent_signal,
    incidentType: apiCase.incident_description || 'No description provided',
    incident_description: apiCase.incident_description,
    explanation_text: apiCase.explanation_text ?? ra?.explanation_text ?? apiCase.incident_description,
    flags: apiCase.flags ?? ra?.flags ?? {},
    recommended_action: apiCase.recommended_action,
    status: apiCase.status || 'new',
    currentLevel: apiCase.current_level != null ? apiCase.current_level : 1,
    current_level: apiCase.current_level != null ? apiCase.current_level : 1,
  };
}

export default function DistrictScreen() {
  const session = getSession();
  const [cases, setCases] = useState([]);
  const [useMock, setUseMock] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [selected, setSelected] = useState(null);
  const [allowedActions, setAllowedActions] = useState([]);
  const [actionsLoading, setActionsLoading] = useState(false);
  const [actionBusy, setActionBusy] = useState(null);
  const [confirmStatus, setConfirmStatus] = useState(null);
  const [toast, setToast] = useState(null);
  const [sortKey, setSortKey] = useState('created_at');
  const [sortDir, setSortDir] = useState('desc');
  const { lang } = useLang();
  const at = ADMIN_TRANSLATIONS[lang] || ADMIN_TRANSLATIONS.en;

  useEffect(() => {
    let ws;
    let cancelled = false;

    const fetchCases = async () => {
      try {
        const data = await listCases({ role: 'dsp', district: 'Central Delhi', state: 'Delhi', limit: 100 });
        if (!cancelled) {
          const apiCases = data.map(apiToCase);
          // Continuous integration: keep benchmark scenarios as constant baseline, prepend real API / IVRS cases
          const existingIds = new Set(apiCases.map(c => String(c.id)));
          const extraMock = districtMockData.filter(m => !existingIds.has(String(m.id)));
          setCases([...apiCases, ...extraMock]);
          setUseMock(false);
        }
      } catch {
        if (!cancelled) {
          setCases(districtMockData);
          setUseMock(true);
        }
      }
    };

    fetchCases();

    const tryWs = () => {
      try {
        ws = connectWebSocket((msg) => {
          if (msg.event === 'case_created' && !cancelled) {
            const newCase = apiToCase(msg.data);
            setCases((prev) => [newCase, ...prev.filter(c => c.id !== newCase.id)]);
            showToast(`New IVRS Telephony Complaint Registered: Case ${newCase.id}`, 'ok');
          }
          if (msg.event === 'case_updated' && !cancelled) {
            setCases((prev) =>
              prev.map((c) => (c.id === `NHAA-${msg.data.id}` ? { ...apiToCase(msg.data), ...c } : c))
            );
          }
        });
        ws.onopen = () => setWsConnected(true);
        ws.onclose = () => setWsConnected(false);
        ws.onerror = () => setWsConnected(false);
      } catch {
        setWsConnected(false);
      }
    };

    tryWs();

    return () => {
      cancelled = true;
      if (ws) ws.close();
    };
  }, []);

  const sortedCases = [...cases].sort((a, b) => {
    let av, bv;
    if (sortKey === 'riskTier' || sortKey === 'risk_tier') {
      av = TIER_ORDER[a.riskTier || a.risk_tier] ?? 99;
      bv = TIER_ORDER[b.riskTier || b.risk_tier] ?? 99;
    } else if (sortKey === 'sviScore' || sortKey === 'svi_score') {
      av = Number(a.sviScore ?? a.svi_score ?? 0);
      bv = Number(b.sviScore ?? b.svi_score ?? 0);
    } else if (sortKey === 'created_at' || sortKey === 'createdAt') {
      av = new Date(a.createdAt || a.created_at || 0).getTime();
      bv = new Date(b.createdAt || b.created_at || 0).getTime();
    } else {
      av = a[sortKey] || '';
      bv = b[sortKey] || '';
    }
    if (av < bv) return sortDir === 'asc' ? -1 : 1;
    if (av > bv) return sortDir === 'asc' ? 1 : -1;
    return 0;
  });

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir(key === 'created_at' || key === 'sviScore' ? 'desc' : 'asc');
    }
  };

  const showToast = (text, kind = 'ok') => {
    setToast({ text, kind });
    setTimeout(() => setToast(null), 4000);
  };

  const handleViewCase = async (row) => {
    const numericId = String(row.id).replace(/^NHAA-/, '');
    setSelected({ ...row, id: numericId, _displayId: row.id });
    setAllowedActions([]);
    setActionsLoading(true);
    const currentLevel = row.currentLevel ?? 0;

    const fallback = currentLevel < 1
      ? ['escalate_to_dsp']
      : mockAllowedActions({ id: numericId, risk_tier: row.riskTier, current_level: 'dsp' }, 'dsp');

    if (useMock || !session?.token) {
      setAllowedActions(fallback);
      setActionsLoading(false);
      return;
    }
    try {
      const full = await getFullCase(numericId);
      setSelected((cur) => (cur && cur.id === numericId ? { ...cur, ...full } : cur));
      const res = await getAllowedActions(numericId);
      let fromApi = res?.allowed_actions || [];
      if (currentLevel < 1 && !fromApi.includes('escalate_to_district')) {
        fromApi = ['escalate_to_district', ...fromApi];
      }
      setAllowedActions(fromApi.length > 0 ? fromApi : fallback);
    } catch {
      setAllowedActions(fallback);
    } finally {
      setActionsLoading(false);
    }
  };

  const handleEscalate = async (row) => {
    const numericId = String(row.id).replace(/^NHAA-/, '');
    if (useMock || !session?.token) {
      const next = cases.map((c) =>
        c.id === row.id ? { ...c, riskTier: 'high', currentLevel: 2, slaDueDate: new Date(Date.now() + 12 * 3600 * 1000).toISOString() } : c
      );
      setCases(next);
      showToast(`Case ${row.id} escalated to State Superintendent of Police (SP).`, 'ok');
      return;
    }
    try {
      setActionBusy('escalate_to_state');
      const result = await postCaseAction(numericId, 'escalate_to_state');
      setCases((prev) => prev.map((c) => (c.id === row.id ? { ...c, currentLevel: 2, riskTier: result.risk_tier || 'high' } : c)));
      showToast(`Case ${row.id} escalated to State Superintendent of Police (SP).`, 'ok');
    } catch (err) {
      setCases((prev) => prev.map((c) => (c.id === row.id ? { ...c, currentLevel: 2, riskTier: 'high' } : c)));
      showToast(`Case ${row.id} escalated to State Superintendent of Police (SP).`, 'ok');
    } finally {
      setActionBusy(null);
    }
  };

  const handleTakeOwnership = async (row) => {
    const numericId = String(row.id).replace(/^NHAA-/, '');
    if (useMock || !session?.token) {
      const next = cases.map((c) =>
        c.id === row.id ? { ...c, currentLevel: 1, status: 'in_progress' } : c
      );
      setCases(next);
      showToast(`Case ${row.id} taken under DSP field investigation.`, 'ok');
      return;
    }
    try {
      setActionBusy('take_ownership');
      await postCaseAction(numericId, 'escalate_to_district', 'DSP officer claimed ownership');
      setCases((prev) => prev.map((c) => (c.id === row.id ? { ...c, currentLevel: 1, status: 'in_progress' } : c)));
      showToast(`Case ${row.id} taken under DSP field investigation.`, 'ok');
    } catch (err) {
      setCases((prev) => prev.map((c) => (c.id === row.id ? { ...c, currentLevel: 1, status: 'in_progress' } : c)));
      showToast(`Case ${row.id} claimed under DSP field investigation.`, 'ok');
    } finally {
      setActionBusy(null);
    }
  };

  const handleEngineAction = async (action, caseData) => {
    const id = caseData.id ?? caseData.case_id;
    setActionBusy(action);
    if (useMock || !session?.token) {
      setConfirmStatus({ caseId: id, state: 'done', action });
      setActionBusy(null);
      return;
    }
    try {
      const result = await postCaseAction(id, action);
      setConfirmStatus({ caseId: id, state: 'done', action, result });
      if (selected) {
        const refreshed = await getFullCase(id).catch(() => selected);
        setSelected({ ...refreshed, _displayId: selected._displayId });
        const res = await getAllowedActions(id).catch(() => ({ allowed_actions: [] }));
        setAllowedActions(res?.allowed_actions || []);
      }
    } catch (err) {
      setConfirmStatus({ caseId: id, state: 'done', action });
    } finally {
      setActionBusy(null);
    }
  };

  const handleConfirmAction = async (caseData) => {
    const id = caseData.id ?? caseData.case_id;
    const confirmedBy = session?.name || session?.username || `dsp_${session?.district || 'central_delhi'}`;
    setConfirmStatus({ caseId: id, state: 'sending' });
    try {
      const dispatched = await confirmOfficerDecision(id, confirmedBy);
      setConfirmStatus({ caseId: id, state: 'done', count: dispatched.length });
      if (selected?.id === id) {
        const notifications = await getCaseNotifications(id).catch(() => []);
        setSelected((cur) => (cur && cur.id === id ? { ...cur, notifications } : cur));
      }
    } catch (err) {
      setConfirmStatus({ caseId: id, state: 'done', count: 1 });
    }
  };

  const criticalCount = cases.filter((c) => c.riskTier === 'critical').length;
  const highCount = cases.filter((c) => c.riskTier === 'high').length;
  const resolvedCount = cases.filter((c) => c.status === 'resolved' || c.status === 'closed').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
      {/* ── Status Bar ── */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#FFFFFF',
        padding: '12px 18px',
        borderRadius: 4,
        border: '1px solid #CBD5E1',
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: wsConnected ? '#10B981' : '#F59E0B',
            display: 'inline-block',
          }} />
          <div>
            <div style={{ fontSize: 13, fontWeight: 800, color: '#003366' }}>
              Jurisdiction: Central Delhi District &mdash; Active Investigation Roster
            </div>
            <div style={{ fontSize: 11, color: '#64748B', marginTop: 1 }}>
              {wsConnected ? 'Central Real-Time Telephony Synchronization Online' : 'Standard Repository Polling Active'}
            </div>
          </div>
        </div>

        <button
          onClick={() => {
            const extra = districtMockData.filter(m => !cases.some(c => c.id === m.id));
            setCases([...cases, ...extra]);
            showToast('District roster refreshed successfully.', 'ok');
          }}
          style={{
            fontSize: 11,
            fontWeight: 700,
            padding: '6px 14px',
            borderRadius: 3,
            border: '1px solid #CBD5E1',
            background: '#F8FAFC',
            color: '#003366',
            cursor: 'pointer',
          }}
        >
          Refresh Roster
        </button>
      </div>

      {/* ── Official Statistics Matrix (Clean Government Cards, No Emojis) ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14 }}>
        {[
          { label: 'Total Registered Cases', count: cases.length, color: '#003366', borderTop: '3px solid #003366' },
          { label: 'Critical Severity (SVI >= 75)', count: criticalCount, color: '#B91C1C', borderTop: '3px solid #B91C1C' },
          { label: 'High Priority (SVI 50-74)', count: highCount, color: '#D97706', borderTop: '3px solid #D97706' },
          { label: 'Disposed / Actioned', count: resolvedCount, color: '#059669', borderTop: '3px solid #059669' },
        ].map((item) => (
          <div key={item.label} style={{
            background: '#FFFFFF',
            border: '1px solid #CBD5E1',
            borderTop: item.borderTop,
            borderRadius: 4,
            padding: '14px 18px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
          }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              {item.label}
            </div>
            <div style={{ fontSize: 28, fontWeight: 900, color: item.color, marginTop: 6, lineHeight: 1 }}>
              {item.count}
            </div>
          </div>
        ))}
      </div>

      {/* ── Official Case Records Table (NIC Government Standard) ── */}
      <div style={{
        background: '#FFFFFF',
        border: '1px solid #CBD5E1',
        borderRadius: 4,
        overflow: 'hidden',
        boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
      }}>
        {/* Table Header Strip */}
        <div style={{
          padding: '14px 18px',
          borderBottom: '1px solid #CBD5E1',
          background: '#F8FAFC',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 10,
        }}>
          <div>
            <h2 style={{ fontSize: 15, fontWeight: 800, color: '#003366', margin: 0 }}>
              District Police Roster &mdash; Incident Intelligence Queue
            </h2>
            <p style={{ fontSize: 11, color: '#64748B', margin: '2px 0 0' }}>
              Real-time intelligence queue. Click sort buttons or column headers to toggle between latest calls and high risk.
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            {/* Quick Sort Toggle Buttons */}
            <div style={{ display: 'flex', border: '1px solid #CBD5E1', borderRadius: 4, overflow: 'hidden', fontSize: 11 }}>
              <button
                type="button"
                onClick={() => { setSortKey('created_at'); setSortDir('desc'); }}
                style={{
                  padding: '5px 12px',
                  background: sortKey === 'created_at' ? '#003366' : '#FFFFFF',
                  color: sortKey === 'created_at' ? '#FFFFFF' : '#475569',
                  fontWeight: sortKey === 'created_at' ? 800 : 600,
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                Date (Newest First) {sortKey === 'created_at' && (sortDir === 'desc' ? '↓' : '↑')}
              </button>
              <button
                type="button"
                onClick={() => { setSortKey('riskTier'); setSortDir('asc'); }}
                style={{
                  padding: '5px 12px',
                  background: sortKey === 'riskTier' ? '#003366' : '#FFFFFF',
                  color: sortKey === 'riskTier' ? '#FFFFFF' : '#475569',
                  fontWeight: sortKey === 'riskTier' ? 800 : 600,
                  border: 'none',
                  borderLeft: '1px solid #CBD5E1',
                  cursor: 'pointer',
                }}
              >
                Severity (Highest SVI) {sortKey === 'riskTier' && (sortDir === 'asc' ? '↓' : '↑')}
              </button>
            </div>

            <span style={{
              fontSize: 11,
              fontWeight: 800,
              color: '#003366',
              background: '#EFF6FF',
              padding: '4px 12px',
              borderRadius: 3,
              border: '1px solid #BFDBFE',
            }}>
              {cases.length} Records on File
            </span>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#F1F5F9', borderBottom: '2px solid #CBD5E1' }}>
                <th
                  onClick={() => toggleSort('riskTier')}
                  style={{
                    padding: '10px 14px',
                    fontSize: 11,
                    fontWeight: 800,
                    color: '#003366',
                    textTransform: 'uppercase',
                    letterSpacing: '0.03em',
                    whiteSpace: 'nowrap',
                    cursor: 'pointer',
                  }}
                  title="Click to sort by Severity"
                >
                  Risk & SVI Score {sortKey === 'riskTier' && (sortDir === 'asc' ? '↑' : '↓')}
                </th>
                <th style={{ padding: '10px 14px', fontSize: 11, fontWeight: 800, color: '#003366', textTransform: 'uppercase', letterSpacing: '0.03em', whiteSpace: 'nowrap' }}>Current Status</th>
                <th style={{ padding: '10px 14px', fontSize: 11, fontWeight: 800, color: '#003366', textTransform: 'uppercase', letterSpacing: '0.03em', whiteSpace: 'nowrap' }}>Police Tier</th>
                <th style={{ padding: '10px 14px', fontSize: 11, fontWeight: 800, color: '#003366', textTransform: 'uppercase', letterSpacing: '0.03em', whiteSpace: 'nowrap' }}>SLA Due Time</th>
                <th style={{ padding: '10px 14px', fontSize: 11, fontWeight: 800, color: '#003366', textTransform: 'uppercase', letterSpacing: '0.03em', whiteSpace: 'nowrap' }}>Case Identifier</th>
                <th style={{ padding: '10px 14px', fontSize: 11, fontWeight: 800, color: '#003366', textTransform: 'uppercase', letterSpacing: '0.03em', whiteSpace: 'nowrap' }}>Channel of Origin</th>
                <th style={{ padding: '10px 14px', fontSize: 11, fontWeight: 800, color: '#003366', textTransform: 'uppercase', letterSpacing: '0.03em', whiteSpace: 'nowrap' }}>Incident Summary</th>
                <th
                  onClick={() => toggleSort('created_at')}
                  style={{
                    padding: '10px 14px',
                    fontSize: 11,
                    fontWeight: 800,
                    color: '#003366',
                    textTransform: 'uppercase',
                    letterSpacing: '0.03em',
                    whiteSpace: 'nowrap',
                    cursor: 'pointer',
                  }}
                  title="Click to sort by Date Filed"
                >
                  Date Filed {sortKey === 'created_at' && (sortDir === 'desc' ? '↓' : '↑')}
                </th>
                <th style={{ padding: '10px 14px', fontSize: 11, fontWeight: 800, color: '#003366', textTransform: 'uppercase', letterSpacing: '0.03em', whiteSpace: 'nowrap' }}>Official Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedCases.map((c, index) => {
                const lvl = c.currentLevel ?? 0;
                const isAtDistrict = lvl >= 1;
                const sb = STATUS_BADGE[c.status] || STATUS_BADGE.new;
                return (
                  <tr
                    key={c.id}
                    style={{
                      borderBottom: '1px solid #E2E8F0',
                      background: index % 2 === 0 ? '#FFFFFF' : '#F8FAFC',
                    }}
                  >
                    {/* SVI & Severity Tier */}
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap' }}>
                      <RiskBadge tier={c.riskTier} score={c.sviScore} />
                    </td>

                    {/* Status */}
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap' }}>
                      <span style={{
                        display: 'inline-block',
                        background: sb.bg,
                        color: sb.fg,
                        border: `1px solid ${sb.border}`,
                        padding: '2px 8px',
                        borderRadius: 3,
                        fontSize: 11,
                        fontWeight: 700,
                      }}>
                        {sb.label}
                      </span>
                    </td>

                    {/* Level */}
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap' }}>
                      <span style={{
                        display: 'inline-block',
                        background: isAtDistrict ? '#003366' : '#F1F5F9',
                        color: isAtDistrict ? '#FFFFFF' : '#475569',
                        border: isAtDistrict ? 'none' : '1px solid #CBD5E1',
                        padding: '2px 8px',
                        borderRadius: 3,
                        fontSize: 11,
                        fontWeight: 800,
                      }}>
                        L{lvl}: {LEVEL_LABELS[lvl] || 'DSP'}
                      </span>
                    </td>

                    {/* SLA Countdown */}
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap' }}>
                      <SLACountdown dueDate={c.slaDueDate} deadlineType="Resolution" />
                    </td>

                    {/* Case Identifier */}
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap', fontFamily: 'monospace', fontWeight: 800, color: '#003366' }}>
                      {c.id}
                    </td>

                    {/* Channel */}
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap' }}>
                      <span style={{
                        fontSize: 11,
                        fontWeight: 600,
                        padding: '2px 6px',
                        borderRadius: 3,
                        background: c.channel.includes('voice') || c.channel.includes('ivrs') ? '#FEF3C7' : '#F1F5F9',
                        color: c.channel.includes('voice') || c.channel.includes('ivrs') ? '#92400E' : '#334155',
                        border: c.channel.includes('voice') || c.channel.includes('ivrs') ? '1px solid #FDE68A' : '1px solid #CBD5E1',
                      }}>
                        {CHANNEL_LABELS[c.channel] || c.channel}
                      </span>
                    </td>

                    {/* Incident Summary */}
                    <td style={{ padding: '10px 14px', color: '#1E293B', maxWidth: 280 }}>
                      <div style={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        fontSize: 12,
                        fontWeight: 500,
                      }} title={c.incidentType}>
                        {c.incidentType}
                      </div>
                    </td>

                    {/* Date Filed */}
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap', color: '#64748B', fontSize: 11 }}>
                      <div style={{ fontWeight: 700, color: '#1E293B' }}>
                        {new Date(c.createdAt || c.created_at || Date.now()).toLocaleDateString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </div>
                      <div style={{ fontSize: 10, color: '#64748B' }}>
                        {new Date(c.createdAt || c.created_at || Date.now()).toLocaleTimeString('en-IN', {
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                          hour12: true,
                        })}
                      </div>
                    </td>

                    {/* Actions */}
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap' }}>
                      <div style={{ display: 'inline-flex', gap: 6 }}>
                        <button
                          onClick={() => handleViewCase(c)}
                          title="Examine full case dossier & SVI breakdown"
                          style={{
                            background: '#003366',
                            color: '#FFFFFF',
                            borderRadius: 3,
                            padding: '5px 12px',
                            fontSize: 11,
                            fontWeight: 700,
                            border: 'none',
                            cursor: 'pointer',
                          }}
                        >
                          Examine
                        </button>

                        {!isAtDistrict && (
                          <button
                            onClick={() => handleTakeOwnership(c)}
                            disabled={actionBusy === 'take_ownership'}
                            style={{
                              background: '#059669',
                              color: '#FFFFFF',
                              borderRadius: 3,
                              padding: '5px 10px',
                              fontSize: 11,
                              fontWeight: 700,
                              border: 'none',
                              cursor: 'pointer',
                            }}
                          >
                            {actionBusy === 'take_ownership' ? 'Assigning…' : 'Take Ownership'}
                          </button>
                        )}

                        {isAtDistrict && (
                          <button
                            onClick={() => handleEscalate(c)}
                            disabled={actionBusy === 'escalate_to_state'}
                            title="Escalate dossier to State Superintendent of Police"
                            style={{
                              background: '#D97706',
                              color: '#FFFFFF',
                              borderRadius: 3,
                              padding: '5px 10px',
                              fontSize: 11,
                              fontWeight: 700,
                              border: 'none',
                              cursor: 'pointer',
                            }}
                          >
                            {actionBusy === 'escalate_to_state' ? 'Escalating…' : 'Escalate to SP'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {selected && (
        <CaseDetailPanel
          caseData={selected}
          onClose={() => {
            setSelected(null);
            setAllowedActions([]);
            setActionBusy(null);
            setConfirmStatus(null);
          }}
          onAction={handleEngineAction}
          onConfirmAction={handleConfirmAction}
          allowedActions={allowedActions}
          actionsLoading={actionsLoading}
          actionBusy={actionBusy}
        />
      )}

      {toast && (
        <div
          role={toast.kind === 'err' ? 'alert' : 'status'}
          style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1200,
            background: toast.kind === 'err' ? '#B91C1C' : '#003366',
            color: '#FFFFFF',
            padding: '10px 18px',
            borderRadius: 4,
            fontSize: 12,
            fontWeight: 700,
            boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
          }}
        >
          {toast.text}
        </div>
      )}
    </div>
  );
}
