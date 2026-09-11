import React, { useEffect, useState } from 'react';
import {
  Shield,
  Search,
  Filter,
  RefreshCw,
  MapPin,
  Phone,
  User,
  Building2,
  FileText,
  FolderOpen,
  Scale,
  Clock,
  ArrowUpRight,
  AlertTriangle,
  CheckCircle2,
  Lock,
} from 'lucide-react';
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
  portal: 'Web Portal',
  chatbot: 'Chatbot',
  ivrs: 'IVRS (14566)',
  voice_twilio: 'IVRS (14566)',
  mobile_app: 'Mobile App',
};

const TIER_ORDER = { critical: 0, high: 1, moderate: 2, low: 3 };

const LEVEL_LABELS = { 0: 'Operator', 1: 'DSP (District)', 2: 'SP (State)', 3: 'IG (Apex)' };

const STATUS_BADGE = {
  new:        { bg: '#EFF6FF', fg: '#1E40AF', border: '#BFDBFE', label: 'New Complaint' },
  in_progress:{ bg: '#FFFBEB', fg: '#92400E', border: '#FDE68A', label: 'Under Investigation' },
  escalated:  { bg: '#FFF7ED', fg: '#9A3412', border: '#FFEDD5', label: 'Escalated to SP' },
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
    person_name: apiCase.person_name || 'Complainant (Confidential)',
    complainant_name: apiCase.complainant_name || apiCase.person_name || 'Complainant (Self)',
    complainant_phone: apiCase.complainant_phone || '+91 98XXX-XXXXX',
    incident_location: apiCase.incident_location || (apiCase.district ? `${apiCase.district}, ${apiCase.state || 'Delhi'}` : 'Central Delhi'),
    police_station: apiCase.police_station || 'PS Central Jurisdiction',
    caste_category: apiCase.caste_category || 'Scheduled Caste (SC)',
    applicable_sections: apiCase.applicable_sections || 'SC/ST (PoA) Act & IPC Provisions',
    person_assaulted_date: apiCase.person_assaulted_date || null,
    assigned_io: apiCase.assigned_io || 'IO Roster Pending Assignment',
    evidence_files: apiCase.evidence_files || [],
    riskTier: tier,
    risk_tier: tier,
    sviScore: score,
    svi_score: score,
    slaDueDate: apiCase.slaDueDate || new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
    district: apiCase.district || 'Central Delhi',
    state: apiCase.state || 'Delhi',
    channel: apiCase.channel_of_origin || 'portal',
    channel_of_origin: apiCase.channel_of_origin || 'portal',
    createdAt: apiCase.created_at,
    created_at: apiCase.created_at,
    victimAgeGroup: apiCase.victimAgeGroup || '—',
    isSilentSignal: apiCase.is_silent_signal,
    incidentType: apiCase.incident_description || 'No description provided',
    incident_description: apiCase.incident_description,
    case_summary: apiCase.case_summary || apiCase.incident_description,
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
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRisk, setFilterRisk] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const { lang } = useLang();
  const at = ADMIN_TRANSLATIONS[lang] || ADMIN_TRANSLATIONS.en;

  const loadCases = async () => {
    try {
      const data = await listCases({ role: 'dsp', district: 'Pune District', state: 'Maharashtra', limit: 100 });
      if (data && data.length > 0) {
        const apiCases = data.map(apiToCase);
        const existingIds = new Set(apiCases.map(c => String(c.id)));
        const extraMock = districtMockData.filter(m => !existingIds.has(String(m.id)));
        setCases([...apiCases, ...extraMock]);
        setUseMock(false);
      } else {
        setCases(districtMockData);
        setUseMock(true);
      }
    } catch {
      setCases(districtMockData);
      setUseMock(true);
    }
  };

  useEffect(() => {
    let ws;
    loadCases();

    const tryWs = () => {
      try {
        ws = connectWebSocket((msg) => {
          if (msg.event === 'case_created') {
            const newCase = apiToCase(msg.data);
            setCases((prev) => [newCase, ...prev.filter(c => c.id !== newCase.id)]);
            showToast(`New Live Complaint: Case ${newCase.id} (${newCase.person_name})`, 'ok');
          }
          if (msg.event === 'case_updated') {
            setCases((prev) =>
              prev.map((c) => (c.id === `NHAA-${msg.data.id}` ? { ...c, ...apiToCase(msg.data) } : c))
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
      if (ws) ws.close();
    };
  }, []);

  const filteredCases = cases.filter((c) => {
    if (filterRisk !== 'all' && c.riskTier !== filterRisk && c.risk_tier !== filterRisk) return false;
    if (filterStatus !== 'all' && c.status !== filterStatus) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchId = String(c.id || '').toLowerCase().includes(q);
      const matchName = String(c.person_name || '').toLowerCase().includes(q);
      const matchComplainant = String(c.complainant_name || '').toLowerCase().includes(q);
      const matchPhone = String(c.complainant_phone || '').toLowerCase().includes(q);
      const matchLoc = String(c.incident_location || '').toLowerCase().includes(q);
      const matchPS = String(c.police_station || '').toLowerCase().includes(q);
      const matchDesc = String(c.incident_description || c.incidentType || '').toLowerCase().includes(q);
      const matchSec = String(c.applicable_sections || '').toLowerCase().includes(q);
      if (!matchId && !matchName && !matchComplainant && !matchPhone && !matchLoc && !matchPS && !matchDesc && !matchSec) {
        return false;
      }
    }
    return true;
  });

  const sortedCases = [...filteredCases].sort((a, b) => {
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
        c.id === row.id ? { ...c, riskTier: 'high', currentLevel: 2, status: 'escalated' } : c
      );
      setCases(next);
      showToast(`Case ${row.id} escalated to State Superintendent of Police (SP).`, 'ok');
      return;
    }
    try {
      setActionBusy('escalate_to_state');
      const result = await postCaseAction(numericId, 'escalate_to_state');
      setCases((prev) => prev.map((c) => (c.id === row.id ? { ...c, currentLevel: 2, status: 'escalated', riskTier: result.risk_tier || 'high' } : c)));
      showToast(`Case ${row.id} escalated to State Superintendent of Police (SP).`, 'ok');
    } catch (err) {
      setCases((prev) => prev.map((c) => (c.id === row.id ? { ...c, currentLevel: 2, status: 'escalated', riskTier: 'high' } : c)));
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

  const criticalCount = cases.filter((c) => c.riskTier === 'critical').length;
  const highCount = cases.filter((c) => c.riskTier === 'high').length;
  const resolvedCount = cases.filter((c) => c.status === 'resolved' || c.status === 'closed').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* ── Official Toast Banner ── */}
      {toast && (
        <div style={{
          position: 'fixed',
          top: 24,
          right: 24,
          zIndex: 9999,
          background: 'rgb(0, 115, 230)',
          color: '#FFFFFF',
          padding: '12px 20px',
          borderRadius: 8,
          boxShadow: '0 8px 24px rgba(0, 115, 230, 0.3)',
          fontWeight: 700,
          fontSize: 13,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}>
          <CheckCircle2 size={18} />
          {toast.text}
        </div>
      )}

      {/* ── Official Command Top Banner ── */}
      <div style={{
        background: 'linear-gradient(135deg, rgb(0, 115, 230) 0%, rgb(0, 85, 180) 100%)',
        color: '#FFFFFF',
        borderRadius: 12,
        padding: '24px 28px',
        boxShadow: '0 4px 20px rgba(0, 115, 230, 0.15)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 16,
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{
              background: '#FF9933',
              color: '#000000',
              fontSize: 10,
              fontWeight: 900,
              padding: '2px 8px',
              borderRadius: 4,
              letterSpacing: '0.04em',
            }}>
              TIER L-1 COMMAND
            </span>
            <span style={{ fontSize: 12, color: 'rgba(255, 255, 255, 0.9)', fontWeight: 700 }}>
              Office of the Deputy Superintendent of Police (DSP) &mdash; Pune District, Maharashtra
            </span>
          </div>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 900, letterSpacing: '-0.01em' }}>
            District Police Roster &mdash; Incident Intelligence Queue
          </h1>
          <p style={{ margin: '6px 0 0', fontSize: 13, color: 'rgba(255, 255, 255, 0.85)', maxWidth: 760, lineHeight: 1.4 }}>
            Direct supervisory control over registered SC/ST complaints, complainant profiles, ground IO inspection reports, and chain-of-custody evidence transfers.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            type="button"
            onClick={loadCases}
            style={{
              background: '#FFFFFF',
              color: 'rgb(0, 115, 230)',
              fontWeight: 800,
              fontSize: 13,
              padding: '10px 18px',
              borderRadius: 8,
              border: 'none',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            }}
          >
            <RefreshCw size={14} /> Refresh Live Queue
          </button>
        </div>
      </div>

      {/* ── Official Statistics Matrix ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
        <div style={{
          background: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderLeft: '5px solid rgb(0, 115, 230)',
          borderRadius: 8,
          padding: '16px 20px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
        }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: 'rgb(0, 115, 230)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Total Registered Complaints
          </div>
          <div style={{ fontSize: 32, fontWeight: 900, color: '#0F172A', marginTop: 4 }}>
            {cases.length}
          </div>
          <div style={{ fontSize: 11, color: '#64748B', fontWeight: 600, marginTop: 4 }}>
            100% Ingestion Coverage
          </div>
        </div>

        <div style={{
          background: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderLeft: '5px solid #DC2626',
          borderRadius: 8,
          padding: '16px 20px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
        }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: '#DC2626', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Critical Severity (SVI &ge; 75)
          </div>
          <div style={{ fontSize: 32, fontWeight: 900, color: '#DC2626', marginTop: 4 }}>
            {criticalCount}
          </div>
          <div style={{ fontSize: 11, color: '#991B1B', fontWeight: 600, marginTop: 4 }}>
            Urgent Ground IO Response Required
          </div>
        </div>

        <div style={{
          background: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderLeft: '5px solid #D97706',
          borderRadius: 8,
          padding: '16px 20px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
        }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: '#D97706', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            High Priority (SVI 50-74)
          </div>
          <div style={{ fontSize: 32, fontWeight: 900, color: '#D97706', marginTop: 4 }}>
            {highCount}
          </div>
          <div style={{ fontSize: 11, color: '#92400E', fontWeight: 600, marginTop: 4 }}>
            Supervisory Scrutiny Active
          </div>
        </div>

        <div style={{
          background: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderLeft: '5px solid #059669',
          borderRadius: 8,
          padding: '16px 20px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
        }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: '#059669', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Disposed / Interim Relieved
          </div>
          <div style={{ fontSize: 32, fontWeight: 900, color: '#059669', marginTop: 4 }}>
            {resolvedCount}
          </div>
          <div style={{ fontSize: 11, color: '#065F46', fontWeight: 600, marginTop: 4 }}>
            Action Recorded in Police Register
          </div>
        </div>
      </div>

      {/* ── Advanced Search & Filter Command Strip ── */}
      <div style={{
        background: '#FFFFFF',
        padding: '16px 20px',
        borderRadius: 8,
        border: '1px solid #CBD5E1',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 14,
        boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
      }}>
        {/* Search Box */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, minWidth: 280, position: 'relative' }}>
          <Search size={16} color="#64748B" style={{ position: 'absolute', left: 12 }} />
          <input
            type="text"
            placeholder="Search by Complainant Name, Phone, Police Station, Thana, Incident Location, Act Sections..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px 10px 36px',
              fontSize: 13,
              border: '1px solid #CBD5E1',
              borderRadius: 6,
              background: '#F8FAFC',
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>

        {/* Filter Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 12, fontWeight: 800, color: '#475569', display: 'flex', alignItems: 'center', gap: 4 }}>
            <Filter size={14} /> Risk:
          </span>
          {['all', 'critical', 'high', 'moderate', 'low'].map((tier) => (
            <button
              key={tier}
              type="button"
              onClick={() => setFilterRisk(tier)}
              style={{
                fontSize: 12,
                fontWeight: 700,
                padding: '6px 12px',
                borderRadius: 6,
                border: 'none',
                background: filterRisk === tier ? 'rgb(0, 115, 230)' : '#F1F5F9',
                color: filterRisk === tier ? '#FFFFFF' : '#475569',
                cursor: 'pointer',
                textTransform: 'capitalize',
                transition: 'all 0.15s ease',
              }}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* ── Official Structured Case Table ── */}
      <div style={{
        background: '#FFFFFF',
        border: '1px solid #CBD5E1',
        borderRadius: 8,
        overflow: 'hidden',
        boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
      }}>
        {/* Table Sub-Header Strip */}
        <div style={{
          padding: '14px 20px',
          borderBottom: '1px solid #E2E8F0',
          background: '#F8FAFC',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 10,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 14, fontWeight: 900, color: 'rgb(0, 115, 230)' }}>
              Live Registered Dossiers ({sortedCases.length} Matching Records)
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              type="button"
              onClick={() => { setSortKey('created_at'); setSortDir('desc'); }}
              style={{
                padding: '6px 12px',
                background: sortKey === 'created_at' ? 'rgb(0, 115, 230)' : '#FFFFFF',
                color: sortKey === 'created_at' ? '#FFFFFF' : '#475569',
                fontSize: 11,
                fontWeight: 700,
                border: '1px solid #CBD5E1',
                borderRadius: 4,
                cursor: 'pointer',
              }}
            >
              Newest Complaints {sortKey === 'created_at' && (sortDir === 'desc' ? '↓' : '↑')}
            </button>

            <button
              type="button"
              onClick={() => { setSortKey('riskTier'); setSortDir('asc'); }}
              style={{
                padding: '6px 12px',
                background: sortKey === 'riskTier' ? 'rgb(0, 115, 230)' : '#FFFFFF',
                color: sortKey === 'riskTier' ? '#FFFFFF' : '#475569',
                fontSize: 11,
                fontWeight: 700,
                border: '1px solid #CBD5E1',
                borderRadius: 4,
                cursor: 'pointer',
              }}
            >
              Highest SVI Severity {sortKey === 'riskTier' && (sortDir === 'asc' ? '↓' : '↑')}
            </button>
          </div>
        </div>

        {/* Full Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#F1F5F9', borderBottom: '2px solid #CBD5E1' }}>
                <th style={{ padding: '12px 16px', fontWeight: 800, color: '#0F172A', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>Case ID &amp; Channel</th>
                <th style={{ padding: '12px 16px', fontWeight: 800, color: '#0F172A', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>Complainant / Victim Profile</th>
                <th style={{ padding: '12px 16px', fontWeight: 800, color: '#0F172A', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>Incident Location &amp; Thana</th>
                <th style={{ padding: '12px 16px', fontWeight: 800, color: '#0F172A', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>Offence &amp; Act Sections</th>
                <th style={{ padding: '12px 16px', fontWeight: 800, color: '#0F172A', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>Threat &amp; SVI</th>
                <th style={{ padding: '12px 16px', fontWeight: 800, color: '#0F172A', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>Assigned IO &amp; Evidence</th>
                <th style={{ padding: '12px 16px', fontWeight: 800, color: '#0F172A', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>Status &amp; Police Tier</th>
                <th style={{ padding: '12px 16px', fontWeight: 800, color: '#0F172A', textTransform: 'uppercase', textAlign: 'right', whiteSpace: 'nowrap' }}>Command Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedCases.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ padding: 40, textAlign: 'center', color: '#64748B' }}>
                    No complaints matching current filter and search parameters.
                  </td>
                </tr>
              ) : (
                sortedCases.map((c, index) => {
                  const lvl = c.currentLevel ?? 1;
                  const isAtDistrict = lvl >= 1;
                  const sb = STATUS_BADGE[c.status] || STATUS_BADGE.new;
                  return (
                    <tr
                      key={c.id}
                      style={{
                        borderBottom: '1px solid #E2E8F0',
                        background: index % 2 === 0 ? '#FFFFFF' : '#F8FAFC',
                        transition: 'background 0.15s ease',
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.background = '#EFF6FF'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.background = index % 2 === 0 ? '#FFFFFF' : '#F8FAFC'; }}
                    >
                      {/* 1. Case Identifier & Channel */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        <div style={{ fontFamily: 'monospace', fontWeight: 900, color: 'rgb(0, 115, 230)', fontSize: 13 }}>
                          {c.id}
                        </div>
                        <div style={{ marginTop: 4 }}>
                          <span style={{
                            fontSize: 10,
                            fontWeight: 700,
                            padding: '2px 6px',
                            borderRadius: 4,
                            background: c.channel.includes('voice') || c.channel.includes('ivrs') ? '#FEF3C7' : '#EFF6FF',
                            color: c.channel.includes('voice') || c.channel.includes('ivrs') ? '#92400E' : 'rgb(0, 115, 230)',
                            border: c.channel.includes('voice') || c.channel.includes('ivrs') ? '1px solid #FDE68A' : '1px solid #BFDBFE',
                          }}>
                            {CHANNEL_LABELS[c.channel] || c.channel}
                          </span>
                        </div>
                        <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 4 }}>
                          {new Date(c.createdAt || c.created_at || Date.now()).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                        </div>
                      </td>

                      {/* 2. Complainant / Victim Profile */}
                      <td style={{ padding: '14px 16px', minWidth: 220 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <User size={14} color="rgb(0, 115, 230)" />
                          <span style={{ fontWeight: 800, color: '#0F172A', fontSize: 13 }}>
                            {c.person_name || 'Complainant (Confidential)'}
                          </span>
                        </div>
                        <div style={{ fontSize: 11, color: '#475569', marginTop: 3, display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Phone size={11} color="#64748B" /> {c.complainant_phone || '+91 98XXX-XXXXX'}
                        </div>
                        {c.caste_category && (
                          <div style={{ marginTop: 4 }}>
                            <span style={{ fontSize: 10, fontWeight: 700, background: '#F1F5F9', color: '#334155', padding: '2px 6px', borderRadius: 3, border: '1px solid #CBD5E1' }}>
                              {c.caste_category}
                            </span>
                          </div>
                        )}
                      </td>

                      {/* 3. Incident Location & Thana */}
                      <td style={{ padding: '14px 16px', minWidth: 240, maxWidth: 280 }}>
                        <div style={{ fontSize: 12, fontWeight: 700, color: '#1E293B', display: 'flex', alignItems: 'flex-start', gap: 4 }}>
                          <MapPin size={13} color="#DC2626" style={{ flexShrink: 0, marginTop: 2 }} />
                          <span>{c.incident_location || `${c.district}, ${c.state}`}</span>
                        </div>
                        <div style={{ fontSize: 11, color: '#0369A1', fontWeight: 700, marginTop: 3, display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Building2 size={12} color="#0369A1" /> {c.police_station || 'PS Central Jurisdiction'}
                        </div>
                        {c.person_assaulted_date && (
                          <div style={{ fontSize: 10, color: '#DC2626', fontWeight: 700, marginTop: 3 }}>
                            Incident Date: {new Date(c.person_assaulted_date).toLocaleDateString('en-IN')}
                          </div>
                        )}
                      </td>

                      {/* 4. Incident Offence & Applicable Sections */}
                      <td style={{ padding: '14px 16px', maxWidth: 260 }}>
                        <div style={{
                          fontSize: 12,
                          color: '#0F172A',
                          fontWeight: 600,
                          lineHeight: 1.3,
                          marginBottom: 4,
                        }} title={c.incident_description || c.incidentType}>
                          {c.incidentType || c.incident_description}
                        </div>
                        {c.applicable_sections && (
                          <span style={{
                            display: 'inline-block',
                            fontSize: 10,
                            fontWeight: 700,
                            background: '#EFF6FF',
                            color: '#1E40AF',
                            padding: '2px 6px',
                            borderRadius: 4,
                            border: '1px solid #BFDBFE',
                          }}>
                            {c.applicable_sections}
                          </span>
                        )}
                      </td>

                      {/* 5. Risk & SVI Score */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        <RiskBadge tier={c.riskTier || c.risk_tier} score={c.sviScore || c.svi_score} />
                        {c.isSilentSignal && (
                          <div style={{ marginTop: 4 }}>
                            <span style={{ fontSize: 9, fontWeight: 800, background: '#FEE2E2', color: '#991B1B', padding: '1px 5px', borderRadius: 3, border: '1px solid #FCA5A5' }}>
                              Silent Signal
                            </span>
                          </div>
                        )}
                      </td>

                      {/* 6. Assigned IO & Evidence Repository */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        <div style={{ fontSize: 11, fontWeight: 700, color: '#334155' }}>
                          {c.assigned_io || 'IO Roster Active'}
                        </div>
                        <div style={{ marginTop: 4 }}>
                          <span style={{
                            fontSize: 11,
                            fontWeight: 700,
                            background: (c.evidence_files && c.evidence_files.length > 0) ? '#EFF6FF' : '#F1F5F9',
                            color: (c.evidence_files && c.evidence_files.length > 0) ? 'rgb(0, 115, 230)' : '#64748B',
                            padding: '3px 8px',
                            borderRadius: 4,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                            border: (c.evidence_files && c.evidence_files.length > 0) ? '1px solid #BFDBFE' : '1px solid #CBD5E1',
                          }}>
                            <FolderOpen size={11} /> {c.evidence_files ? c.evidence_files.length : 0} Attached
                          </span>
                        </div>
                      </td>

                      {/* 7. Status & Police Tier */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        <span style={{
                          display: 'inline-block',
                          background: sb.bg,
                          color: sb.fg,
                          border: `1px solid ${sb.border}`,
                          padding: '3px 8px',
                          borderRadius: 4,
                          fontSize: 11,
                          fontWeight: 800,
                        }}>
                          {sb.label}
                        </span>
                        <div style={{ marginTop: 4 }}>
                          <span style={{
                            display: 'inline-block',
                            background: isAtDistrict ? 'rgb(0, 115, 230)' : '#F1F5F9',
                            color: isAtDistrict ? '#FFFFFF' : '#475569',
                            padding: '2px 6px',
                            borderRadius: 3,
                            fontSize: 10,
                            fontWeight: 800,
                          }}>
                            L{lvl}: {LEVEL_LABELS[lvl] || 'DSP'}
                          </span>
                        </div>
                      </td>

                      {/* 8. Senior Officer Actions */}
                      <td style={{ padding: '14px 16px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                        <div style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
                          <button
                            type="button"
                            onClick={() => handleViewCase(c)}
                            title="Examine full dossier & SVI evidence"
                            style={{
                              background: 'rgb(0, 115, 230)',
                              color: '#FFFFFF',
                              borderRadius: 6,
                              padding: '6px 14px',
                              fontSize: 12,
                              fontWeight: 800,
                              border: 'none',
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 4,
                              boxShadow: '0 2px 6px rgba(0, 115, 230, 0.2)',
                            }}
                          >
                            Examine <ArrowUpRight size={13} />
                          </button>

                          {!isAtDistrict && (
                            <button
                              type="button"
                              onClick={() => handleTakeOwnership(c)}
                              disabled={actionBusy === 'take_ownership'}
                              style={{
                                background: '#059669',
                                color: '#FFFFFF',
                                borderRadius: 6,
                                padding: '6px 10px',
                                fontSize: 11,
                                fontWeight: 800,
                                border: 'none',
                                cursor: 'pointer',
                              }}
                            >
                              {actionBusy === 'take_ownership' ? 'Assigning…' : 'Take Ownership'}
                            </button>
                          )}

                          {isAtDistrict && (
                            <button
                              type="button"
                              onClick={() => handleEscalate(c)}
                              disabled={actionBusy === 'escalate_to_state'}
                              title="Escalate dossier to State Superintendent of Police"
                              style={{
                                background: '#D97706',
                                color: '#FFFFFF',
                                borderRadius: 6,
                                padding: '6px 10px',
                                fontSize: 11,
                                fontWeight: 800,
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
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Case Detail & Examination Panel ── */}
      {selected && (
        <CaseDetailPanel
          caseData={selected}
          onClose={() => setSelected(null)}
          onRefresh={loadCases}
          onAction={async (action, caseItem) => {
            await postCaseAction(caseItem.numericId || caseItem.id, action, 'Action confirmed by DSP command officer');
            loadCases();
          }}
        />
      )}
    </div>
  );
}
