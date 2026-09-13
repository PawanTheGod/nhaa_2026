import React, { useState } from 'react';
import { clearSession } from '../../utils/adminAuth';
import { useNavigate } from 'react-router-dom';

const ALL_DESKS = [
  { role: 'operator', label: 'Operator (L-0)', color: '#0284C7', cases: 14, active: 3, alerts: 1 },
  { role: 'io',       label: 'IO — Investigating Officer (L-0.5)', color: '#2563EB', cases: 9, active: 2, alerts: 0 },
  { role: 'dsp',      label: 'DSP / ACP (L-1)', color: '#059669', cases: 7, active: 1, alerts: 2 },
  { role: 'sp',       label: 'SP — Superintendent (L-2)', color: '#D97706', cases: 5, active: 1, alerts: 0 },
  { role: 'ig',       label: 'IG — Inspector General (L-3)', color: '#DC2626', cases: 3, active: 1, alerts: 1 },
  { role: 'director', label: 'Director — Apex Command (L-3+)', color: '#991B1B', cases: 2, active: 0, alerts: 0 },
  { role: 'judiciary',label: 'Judiciary — Special Court (L-4)', color: '#7C3AED', cases: 4, active: 1, alerts: 0 },
  { role: 'swo',      label: 'SWO — Social Welfare (L-5)', color: '#047857', cases: 6, active: 2, alerts: 0 },
];

const AUDIT_LOG = [
  { time: '14:31:05', user: 'DSP Rajesh Shinde', action: 'Escalated case #C-2026-0891 to SP desk', level: 'warn' },
  { time: '14:28:44', user: 'Operator Priya Kadam', action: 'New case intake — caller 98XXXXXXXX, risk tier: HIGH', level: 'critical' },
  { time: '14:25:12', user: 'IG Priya Kulkarni', action: 'Viewed aggregate heatmap for Pune District', level: 'info' },
  { time: '14:21:09', user: 'IO Vikram Shinde', action: 'Uploaded panchnama document for case #C-2026-0887', level: 'info' },
  { time: '14:18:33', user: 'SP Anand Patil', action: 'Case #C-2026-0884 locked with SHA-256 seal', level: 'success' },
  { time: '14:15:00', user: 'SWO Anita Pawar', action: 'DBT Stage 1 disbursed for victim ID V-2026-441', level: 'success' },
  { time: '14:11:22', user: 'Judiciary M. L. Gaikwad', action: 'Directive issued to SWO for Rule 12(4) relief', level: 'warn' },
  { time: '14:08:55', user: 'ACP Sanjay More', action: 'IO tasked for spot inspection — PS Bhosari MIDC', level: 'info' },
  { time: '14:02:17', user: 'Operator Priya Kadam', action: 'Silent distress signal received — auto-triaged as HIGH', level: 'critical' },
  { time: '13:58:41', user: 'Director K. S. Deshmukh', action: 'Viewed monthly KPI report — Maharashtra state', level: 'info' },
];

const LEVEL_STYLE = {
  info:     { bg: '#EFF6FF', color: '#1D4ED8', dot: '#3B82F6' },
  success:  { bg: '#F0FDF4', color: '#166534', dot: '#22C55E' },
  warn:     { bg: '#FFFBEB', color: '#92400E', dot: '#F59E0B' },
  critical: { bg: '#FEF2F2', color: '#991B1B', dot: '#EF4444' },
};

export default function SysAdminScreen() {
  const navigate = useNavigate();
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailTo, setEmailTo] = useState('monitoring@nhaa.gov.in');
  const [emailSent, setEmailSent] = useState(false);

  const handleLogout = () => {
    clearSession();
    navigate('/admin/login');
  };

  const handleSendEmail = () => {
    const subject = encodeURIComponent('NHAA System Report — ' + new Date().toLocaleDateString('en-IN'));
    const body = encodeURIComponent(
      `NHAA System Administrator Report\nGenerated: ${new Date().toLocaleString('en-IN')}\n\n` +
      `DESK SUMMARY:\n` +
      ALL_DESKS.map(d => `• ${d.label}: ${d.cases} cases, ${d.active} active, ${d.alerts} alerts`).join('\n') +
      `\n\nRECENT AUDIT LOG:\n` +
      AUDIT_LOG.slice(0, 5).map(l => `[${l.time}] ${l.user}: ${l.action}`).join('\n')
    );
    window.location.href = `mailto:${emailTo}?subject=${subject}&body=${body}`;
    setEmailSent(true);
    setTimeout(() => { setEmailSent(false); setShowEmailModal(false); }, 2000);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0F172A',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      color: '#E2E8F0',
    }}>
      {/* Header */}
      <div style={{
        background: '#7C2D12',
        borderBottom: '2px solid #F97316',
        padding: '14px 28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span style={{ fontSize: 20 }}>🛡️</span>
          <div>
            <div style={{ fontSize: 11, fontWeight: 800, color: '#FED7AA', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              RESTRICTED — SYSTEM ADMINISTRATOR ONLY
            </div>
            <div style={{ fontSize: 18, fontWeight: 900, color: '#FFF' }}>
              NHAA Full-Tier Monitoring Console
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={() => setShowEmailModal(true)}
            style={{
              background: '#1E3A5F',
              color: '#93C5FD',
              border: '1px solid #2563EB',
              borderRadius: 8,
              padding: '8px 18px',
              fontSize: 13,
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            📧 Email Report
          </button>
          <button
            onClick={handleLogout}
            style={{
              background: 'rgba(255,255,255,0.1)',
              color: '#FCA5A5',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: 8,
              padding: '8px 18px',
              fontSize: 13,
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div style={{ padding: '28px', maxWidth: 1280, margin: '0 auto' }}>

        {/* Desk Status Grid */}
        <h2 style={{ fontSize: 14, fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.06em', margin: '0 0 14px' }}>
          All Desk Status — Live Overview
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12, marginBottom: 32 }}>
          {ALL_DESKS.map((desk) => (
            <div key={desk.role} style={{
              background: '#1E293B',
              border: `1.5px solid ${desk.alerts > 0 ? '#EF4444' : '#334155'}`,
              borderRadius: 10,
              padding: '16px 18px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                <span style={{
                  fontSize: 10,
                  fontWeight: 900,
                  background: desk.color,
                  color: '#FFF',
                  padding: '2px 8px',
                  borderRadius: 3,
                }}>
                  {desk.role.toUpperCase()}
                </span>
                {desk.alerts > 0 && (
                  <span style={{
                    fontSize: 10,
                    fontWeight: 800,
                    background: '#7F1D1D',
                    color: '#FCA5A5',
                    padding: '2px 8px',
                    borderRadius: 3,
                  }}>
                    ⚠ {desk.alerts} ALERT{desk.alerts > 1 ? 'S' : ''}
                  </span>
                )}
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#E2E8F0', marginBottom: 8 }}>{desk.label}</div>
              <div style={{ display: 'flex', gap: 16 }}>
                <div>
                  <div style={{ fontSize: 22, fontWeight: 900, color: desk.color }}>{desk.cases}</div>
                  <div style={{ fontSize: 10, color: '#64748B', fontWeight: 600 }}>Total Cases</div>
                </div>
                <div>
                  <div style={{ fontSize: 22, fontWeight: 900, color: '#22C55E' }}>{desk.active}</div>
                  <div style={{ fontSize: 10, color: '#64748B', fontWeight: 600 }}>Active Now</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Audit Log */}
        <h2 style={{ fontSize: 14, fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.06em', margin: '0 0 14px' }}>
          System Audit Log — Last 10 Actions
        </h2>
        <div style={{ background: '#1E293B', borderRadius: 10, border: '1px solid #334155', overflow: 'hidden' }}>
          {AUDIT_LOG.map((entry, i) => {
            const s = LEVEL_STYLE[entry.level] || LEVEL_STYLE.info;
            return (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 14,
                padding: '12px 18px',
                borderBottom: i < AUDIT_LOG.length - 1 ? '1px solid #334155' : 'none',
                background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
              }}>
                <span style={{ fontSize: 11, color: '#475569', fontFamily: 'monospace', whiteSpace: 'nowrap' }}>{entry.time}</span>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: s.dot, flexShrink: 0 }} />
                <div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: '#CBD5E1' }}>{entry.user}</span>
                  <span style={{ fontSize: 12, color: '#64748B' }}> — {entry.action}</span>
                </div>
                <span style={{
                  marginLeft: 'auto',
                  fontSize: 10,
                  fontWeight: 700,
                  background: s.bg,
                  color: s.color,
                  padding: '2px 8px',
                  borderRadius: 3,
                  whiteSpace: 'nowrap',
                }}>
                  {entry.level.toUpperCase()}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Email Report Modal */}
      {showEmailModal && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999,
        }}>
          <div style={{
            background: '#1E293B', border: '1px solid #334155', borderRadius: 12,
            padding: '28px 32px', width: 420, boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
          }}>
            <h3 style={{ fontSize: 16, fontWeight: 800, color: '#E2E8F0', margin: '0 0 6px' }}>📧 Send System Report</h3>
            <p style={{ fontSize: 12, color: '#64748B', margin: '0 0 20px' }}>
              Sends a summary of all desk stats and the last 5 audit entries to the specified email.
            </p>
            <label style={{ fontSize: 12, fontWeight: 700, color: '#94A3B8', display: 'block', marginBottom: 6 }}>
              Recipient Email
            </label>
            <input
              type="email"
              value={emailTo}
              onChange={(e) => setEmailTo(e.target.value)}
              style={{
                width: '100%', boxSizing: 'border-box',
                background: '#0F172A', border: '1px solid #334155', borderRadius: 6,
                color: '#E2E8F0', fontSize: 13, padding: '10px 12px', marginBottom: 20, outline: 'none',
              }}
            />
            <div style={{ display: 'flex', gap: 10 }}>
              <button
                onClick={handleSendEmail}
                style={{
                  flex: 1, background: emailSent ? '#166534' : '#1D4ED8',
                  color: '#FFF', border: 'none', borderRadius: 8,
                  padding: '10px', fontSize: 13, fontWeight: 700, cursor: 'pointer',
                }}
              >
                {emailSent ? '✓ Opening Email Client...' : 'Send Report'}
              </button>
              <button
                onClick={() => setShowEmailModal(false)}
                style={{
                  background: '#334155', color: '#94A3B8', border: 'none',
                  borderRadius: 8, padding: '10px 18px', fontSize: 13, fontWeight: 700, cursor: 'pointer',
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
