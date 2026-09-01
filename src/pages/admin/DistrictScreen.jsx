import React, { useEffect, useState } from 'react';
import { listCases, connectWebSocket } from '../../services/api';
import { districtMockData } from '../../data/districtCases';
import RiskBadge from '../../components/admin/RiskBadge';
import SLACountdown from '../../components/admin/SLACountdown';

const CHANNEL_LABELS = {
  portal: 'Portal',
  chatbot: 'Chatbot',
  ivrs: 'IVRS',
  mobile_app: 'Mobile App',
};

const TIER_ORDER = { critical: 0, high: 1, moderate: 2, low: 3 };

function apiToCase(apiCase) {
  return {
    id: `NHAA-${apiCase.id}`,
    riskTier: apiCase.risk_tier || 'low',
    sviScore: apiCase.svi_score || 0,
    slaDueDate: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
    district: apiCase.district || 'Unknown',
    state: apiCase.state || 'Unknown',
    channel: apiCase.channel_of_origin || 'portal',
    createdAt: apiCase.created_at,
    victimAgeGroup: '—',
    isSilentSignal: apiCase.is_silent_signal,
    incidentType: apiCase.incident_description || 'No description',
  };
}

export default function DistrictScreen() {
  const [cases, setCases] = useState([]);
  const [useMock, setUseMock] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    let ws;
    let cancelled = false;

    const fetchCases = async () => {
      try {
        const data = await listCases({ role: 'district', district: 'Central Delhi', state: 'Delhi', limit: 100 });
        if (!cancelled) {
          setCases(data.map(apiToCase));
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
            setCases((prev) => [apiToCase(msg.data), ...prev]);
          }
          if (msg.event === 'case_updated' && !cancelled) {
            setCases((prev) =>
              prev.map((c) => (c.id === `NHAA-${msg.data.id}` ? { ...apiToCase(msg.data), ...c } : c))
            );
          }
        });
        ws.onopen = () => setWsConnected(true);
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

  const sortedCases = [...cases].sort((a, b) => (TIER_ORDER[a.riskTier] || 99) - (TIER_ORDER[b.riskTier] || 99));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800, color: '#0F172A', margin: 0 }}>
            Central Delhi District
          </h2>
          <p style={{ fontSize: 13, color: '#64748B', marginTop: 4 }}>
            {useMock ? '(Mock data — API unreachable)' : '(Live data from Case API)'} | WebSocket: {wsConnected ? 'Connected' : 'Disconnected'}
          </p>
        </div>
        <button
          onClick={() => setCases(districtMockData)}
          style={{ fontSize: 12, padding: '6px 14px', borderRadius: 6, border: '1px solid #CBD5E1', background: 'white', cursor: 'pointer' }}
        >
          Restore Mock Data
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-extrabold text-slate-500 uppercase" style={{ letterSpacing: '0.05em' }}>Total Cases</div>
          <div className="mt-1 text-2xl font-extrabold text-slate-900">{cases.length}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-extrabold text-slate-500 uppercase" style={{ letterSpacing: '0.05em' }}>Critical</div>
          <div className="mt-1 text-2xl font-extrabold text-red-700">{cases.filter((c) => c.riskTier === 'critical').length}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-extrabold text-slate-500 uppercase" style={{ letterSpacing: '0.05em' }}>High</div>
          <div className="mt-1 text-2xl font-extrabold text-orange-600">{cases.filter((c) => c.riskTier === 'high').length}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-extrabold text-slate-500 uppercase" style={{ letterSpacing: '0.05em' }}>Pending SLA</div>
          <div className="mt-1 text-2xl font-extrabold text-slate-900">
            {cases.filter((c) => new Date(c.slaDueDate) > new Date()).length}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="border-b border-slate-200 px-5 py-3 bg-slate-50">
          <h2 className="text-lg font-bold text-slate-800">Active Case Queue</h2>
          <p className="text-xs text-slate-500 mt-0.5">Sorted by risk tier (highest first). Live updates via WebSocket.</p>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b-2 border-slate-200">
              <th className="px-4 py-2.5 text-left text-xs font-extrabold text-slate-600 uppercase">Risk</th>
              <th className="px-4 py-2.5 text-left text-xs font-extrabold text-slate-600 uppercase">SLA</th>
              <th className="px-4 py-2.5 text-left text-xs font-extrabold text-slate-600 uppercase">Case ID</th>
              <th className="px-4 py-2.5 text-left text-xs font-extrabold text-slate-600 uppercase">Channel</th>
              <th className="px-4 py-2.5 text-left text-xs font-extrabold text-slate-600 uppercase">Type</th>
              <th className="px-4 py-2.5 text-left text-xs font-extrabold text-slate-600 uppercase">Created</th>
              <th className="px-4 py-2.5 text-center text-xs font-extrabold text-slate-600 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedCases.map((c) => (
              <tr key={c.id} className="border-b border-slate-100 hover:bg-slate-25 transition-colors">
                <td className="px-4 py-3">
                  <RiskBadge tier={c.riskTier} score={c.sviScore} />
                  {c.isSilentSignal && (
                    <span title="Silent Distress Signal" className="ml-1.5 inline-block w-2 h-2 rounded-full bg-red-500" />
                  )}
                </td>
                <td className="px-4 py-3">
                  <SLACountdown dueDate={c.slaDueDate} deadlineType="Resolution" />
                </td>
                <td className="px-4 py-3 font-mono text-xs text-slate-800">{c.id}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {CHANNEL_LABELS[c.channel] || c.channel}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-600">{c.incidentType}</td>
                <td className="px-4 py-3 text-slate-500">{new Date(c.createdAt).toLocaleDateString('en-IN')}</td>
                <td className="px-4 py-3 text-center">
                  <button
                    onClick={() => alert(`Escalating case ${c.id} - notify District Nodal Officer + Police + DLSA`)}
                    className="rounded-md bg-[#F96302] px-3 py-1.5 text-xs font-bold text-white hover:bg-[#E05600] transition-colors"
                  >
                    Escalate
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="text-xs text-slate-400">
        Data shape contract (Step 14): District case queue expects - case id, risk tier, svi score, sla due date, district, channel, created at, incident type.
        Mock data shown when API is unreachable. Replace with live API calls once Aditya's auth layer is integrated.
      </div>
    </div>
  );
}
