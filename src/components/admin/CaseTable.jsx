import React, { useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import RiskBadge from './RiskBadge';

const CHANNEL_LABELS = {
  portal: 'Portal',
  chatbot: 'Chatbot',
  ivrs: 'IVRS',
  mobile_app: 'Mobile App',
};

const TIER_ORDER = { critical: 0, high: 1, moderate: 2, low: 3 };

export default function CaseTable({ cases, onViewCase }) {
  const [sortKey, setSortKey] = useState('created_at');
  const [sortDir, setSortDir] = useState('desc');

  const sorted = useMemo(() => {
    const list = [...cases];
    list.sort((a, b) => {
      let av;
      let bv;
      if (sortKey === 'risk_tier') {
        av = TIER_ORDER[a.risk_tier] ?? 9;
        bv = TIER_ORDER[b.risk_tier] ?? 9;
      } else if (sortKey === 'created_at') {
        av = new Date(a.created_at).getTime();
        bv = new Date(b.created_at).getTime();
      } else if (sortKey === 'id') {
        av = a.id ?? a.case_id;
        bv = b.id ?? b.case_id;
      } else {
        av = a[sortKey];
        bv = b[sortKey];
      }
      if (av < bv) return sortDir === 'asc' ? -1 : 1;
      if (av > bv) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    return list;
  }, [cases, sortKey, sortDir]);

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else {
      setSortKey(key);
      setSortDir(key === 'created_at' ? 'desc' : 'asc');
    }
  };

  const sortIndicator = (key) => (sortKey === key ? (sortDir === 'asc' ? ' ↑' : ' ↓') : '');

  return (
    <div style={{ overflowX: 'auto', border: '1px solid #E2E8F0', borderRadius: 12, background: '#fff' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <caption style={{ captionSide: 'top', textAlign: 'left', padding: '12px 16px', fontWeight: 700, color: '#0F172A' }}>
          Incoming cases — live triage queue
        </caption>
        <thead>
          <tr style={{ background: '#F1F5F9', borderBottom: '1px solid #E2E8F0' }}>
            <th scope="col" style={thStyle}>
              <button type="button" onClick={() => toggleSort('id')} style={sortBtnStyle} aria-label={`Sort by case ID${sortIndicator('id')}`}>
                Case ID{sortIndicator('id')}
              </button>
            </th>
            <th scope="col" style={thStyle}>Channel</th>
            <th scope="col" style={thStyle}>
              <button type="button" onClick={() => toggleSort('created_at')} style={sortBtnStyle} aria-label={`Sort by timestamp${sortIndicator('created_at')}`}>
                Timestamp{sortIndicator('created_at')}
              </button>
            </th>
            <th scope="col" style={thStyle}>
              <button type="button" onClick={() => toggleSort('risk_tier')} style={sortBtnStyle} aria-label={`Sort by risk tier${sortIndicator('risk_tier')}`}>
                Risk Tier{sortIndicator('risk_tier')}
              </button>
            </th>
            <th scope="col" style={thStyle}>Action</th>
          </tr>
        </thead>
        <tbody>
          {sorted.length === 0 ? (
            <tr>
              <td colSpan={5} style={{ padding: 24, textAlign: 'center', color: '#64748B' }}>
                No cases in queue.
              </td>
            </tr>
          ) : (
            sorted.map((c) => {
              const id = c.id ?? c.case_id;
              return (
                <tr key={id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                  <td style={tdStyle}>
                    <strong>NHAA-{id}</strong>
                    {c.is_silent_signal && (
                      <span style={{ marginLeft: 8, fontSize: 10, fontWeight: 800, color: '#991B1B' }} aria-label="Silent distress signal active">
                        SOS
                      </span>
                    )}
                  </td>
                  <td style={tdStyle}>{CHANNEL_LABELS[c.channel_of_origin] || c.channel_of_origin}</td>
                  <td style={tdStyle}>{new Date(c.created_at).toLocaleString('en-IN')}</td>
                  <td style={tdStyle}>
                    <RiskBadge tier={c.risk_tier || 'low'} score={c.svi_score} />
                  </td>
                  <td style={tdStyle}>
                    <button
                      type="button"
                      onClick={() => onViewCase(c)}
                      aria-label={`View details for case NHAA-${id}`}
                      style={{
                        background: '#EEF2FF',
                        color: '#003366',
                        border: '1px solid #CBD5E1',
                        borderRadius: 6,
                        padding: '6px 14px',
                        fontSize: 12,
                        fontWeight: 700,
                        cursor: 'pointer',
                      }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}

const thStyle = { textAlign: 'left', padding: '12px 16px', fontWeight: 700, color: '#334155' };
const tdStyle = { padding: '12px 16px', color: '#0F172A', verticalAlign: 'middle' };
const sortBtnStyle = {
  background: 'none',
  border: 'none',
  padding: 0,
  font: 'inherit',
  fontWeight: 700,
  color: '#334155',
  cursor: 'pointer',
};

CaseTable.propTypes = {
  cases: PropTypes.arrayOf(PropTypes.object).isRequired,
  onViewCase: PropTypes.func.isRequired,
};
