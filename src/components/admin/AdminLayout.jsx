import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ASSETS } from '../../assets';
import { getSession, clearSession, ROLE_LABELS } from '../../utils/adminAuth';
import { useLang } from '../../i18n/LangContext';
import { ADMIN_TRANSLATIONS } from '../../i18n/adminTranslations';

const RANK_CONFIG = {
  operator: { code: 'L-0', label: 'Call Centre Operator', jurisdiction: 'Triage Queue' },
  dsp:      { code: 'L-1', label: 'Deputy Superintendent of Police (DSP)', jurisdiction: 'District Operations' },
  sp:       { code: 'L-2', label: 'Superintendent of Police (SP)', jurisdiction: 'State Command' },
  ig:       { code: 'L-3', label: 'Inspector General of Police (IG)', jurisdiction: 'National Intelligence' },
};

const ADMIN_NAV = [
  { label: 'Operator Desk',  path: '/admin/operator', code: 'L-0', desc: 'Call Centre & AI Triage Queue', roles: ['operator'] },
  { label: 'DSP Command',    path: '/admin/dsp',      code: 'L-1', desc: 'District Field Operations & Inquiry', roles: ['dsp', 'operator'] },
  { label: 'SP Oversight',   path: '/admin/sp',       code: 'L-2', desc: 'State Supervisory & Escalation Command', roles: ['sp', 'dsp'] },
  { label: 'IG Intelligence',path: '/admin/ig',       code: 'L-3', desc: 'National Overview & Apex Review', roles: ['ig', 'sp'] },
];

function navVisible(item, role) {
  if (!role) return true;
  return item.roles.includes(role) || role === 'ig';
}

function Clock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t); }, []);
  return (
    <span style={{ fontFamily: 'monospace', fontSize: 12, color: '#FFFFFF', fontWeight: 600 }}>
      {time.toLocaleTimeString('en-IN', { hour12: false })} IST
    </span>
  );
}

export default function AdminLayout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const session = getSession();
  const role = session?.role;
  const { lang } = useLang();
  const at = ADMIN_TRANSLATIONS[lang] || ADMIN_TRANSLATIONS.en;
  const current = ADMIN_NAV.find((n) => n.path === location.pathname);
  const rank = RANK_CONFIG[role] || RANK_CONFIG.dsp;

  const handleLogout = () => {
    clearSession();
    navigate('/admin/login');
  };

  return (
    <div style={{
      background: '#F8FAFC',
      color: '#0F172A',
      fontFamily: "'Inter', 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* ── 1. Top Utility Bar (Matching Homepage) ── */}
      <div style={{
        background: '#003366',
        color: '#FFFFFF',
        fontSize: 12,
        padding: '6px 0',
        borderBottom: '2px solid #FF9933',
      }}>
        <div style={{
          maxWidth: 1440,
          margin: '0 auto',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12,
        }}>
          {/* Left: Indian Flag & Official Government Declaration */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <img
              src={ASSETS.indianFlag}
              alt="Government of India Flag"
              style={{ height: 13, width: 20, objectFit: 'cover', borderRadius: 2 }}
              onError={(e) => { e.target.style.display = 'none'; }}
            />
            <span style={{ fontWeight: 600, letterSpacing: '0.02em' }}>
              Government of India &nbsp;|&nbsp; Ministry of Social Justice &amp; Empowerment
            </span>
          </div>

          {/* Right: Telephony Status, Clock & Public Portal Link */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Clock />
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 11,
              fontWeight: 700,
              background: 'rgba(16, 185, 129, 0.2)',
              color: '#A7F3D0',
              padding: '2px 10px',
              borderRadius: 4,
              border: '1px solid rgba(16, 185, 129, 0.4)',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
              IVRS Telephony Active: 14566
            </span>
            <Link
              to="/"
              style={{
                color: '#93C5FD',
                textDecoration: 'none',
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              Public Portal
            </Link>
          </div>
        </div>
      </div>

      {/* ── 2. Official Main Header Bar (Matching Homepage Layout) ── */}
      <header style={{
        background: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '12px 0',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
      }}>
        <div style={{
          maxWidth: 1440,
          margin: '0 auto',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 20,
          flexWrap: 'wrap',
        }}>
          {/* Left: National Emblem + Ministry Header */}
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 14, textDecoration: 'none' }}>
            <img
              src={ASSETS.nationalEmblem}
              alt="National Emblem of India"
              style={{ height: 54, width: 'auto' }}
              onError={(e) => { e.target.src = `${import.meta.env.BASE_URL}ashoka_emblem.jpg`; }}
            />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                <span style={{
                  background: '#FF9900',
                  color: '#000000',
                  fontSize: 9,
                  fontWeight: 800,
                  padding: '1px 6px',
                  borderRadius: 3,
                  letterSpacing: '0.5px',
                }}>
                  OFFICIAL
                </span>
                <span style={{ fontSize: 11, color: '#64748B', fontWeight: 600 }}>
                  Government of India
                </span>
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#1E293B', lineHeight: 1.2 }}>
                Ministry of Social Justice &amp; Empowerment
              </div>
              <div style={{ fontSize: 17, fontWeight: 900, color: '#003366', letterSpacing: '-0.01em', lineHeight: 1.25 }}>
                National Helpline Against Atrocities (NHAA) &mdash; Law Enforcement Command
              </div>
            </div>
          </Link>

          {/* Right: Digital India Logo + Officer Profile Box */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <img
              src={ASSETS.digitalIndia}
              alt="Digital India"
              style={{ height: 38, width: 'auto' }}
              onError={(e) => { e.target.style.display = 'none'; }}
            />

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              background: '#F8FAFC',
              border: '1px solid #CBD5E1',
              padding: '6px 14px',
              borderRadius: 6,
            }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 13, fontWeight: 800, color: '#0F172A', lineHeight: 1.2 }}>
                  {session?.name || ROLE_LABELS[role] || 'Designated Officer'}
                </div>
                <div style={{ fontSize: 11, color: '#003366', fontWeight: 700, marginTop: 2 }}>
                  {rank.code}: {rank.label}
                  {session?.district ? ` | ${session.district}` : ''}
                </div>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                style={{
                  background: '#FFFFFF',
                  color: '#DC2626',
                  fontSize: 11,
                  fontWeight: 700,
                  padding: '6px 12px',
                  borderRadius: 4,
                  border: '1px solid #FECACA',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => { e.target.style.background = '#FEF2F2'; }}
                onMouseLeave={(e) => { e.target.style.background = '#FFFFFF'; }}
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ── 3. Government Hierarchy Navigation Tabs (Matching Home Navigation Bar) ── */}
      <nav style={{
        background: '#FFFFFF',
        borderBottom: '2px solid #003366',
        position: 'sticky',
        top: '78px',
        zIndex: 90,
        boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
      }} aria-label="Police Command Navigation">
        <div style={{ maxWidth: 1440, margin: '0 auto', padding: '0 24px', display: 'flex', gap: 2, overflowX: 'auto' }}>
          {ADMIN_NAV.filter((item) => navVisible(item, role)).map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '12px 18px',
                  fontSize: 13,
                  fontWeight: isActive ? 800 : 600,
                  color: isActive ? '#003366' : '#475569',
                  borderBottom: isActive ? '3px solid #003366' : '3px solid transparent',
                  background: isActive ? '#EFF6FF' : 'transparent',
                  textDecoration: 'none',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease',
                }}
              >
                <span style={{
                  fontSize: 10,
                  fontWeight: 800,
                  padding: '2px 6px',
                  borderRadius: 3,
                  background: isActive ? '#003366' : '#E2E8F0',
                  color: isActive ? '#FFFFFF' : '#475569',
                }}>
                  {item.code}
                </span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* ── 4. Main Desk Title Bar ── */}
      <div style={{ maxWidth: 1440, margin: '0 auto', width: '100%', padding: '20px 24px 0', boxSizing: 'border-box' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#003366', marginBottom: 2 }}>
              Police Command &amp; Supervisory Network &mdash; Ministry of Social Justice &amp; Empowerment
            </div>
            <h1 style={{ fontSize: 22, fontWeight: 900, color: '#0F172A', margin: 0, letterSpacing: '-0.01em' }}>
              {current?.label || 'Officer'} Desk
            </h1>
            {current?.desc && <p style={{ fontSize: 12, color: '#64748B', margin: '3px 0 0', fontWeight: 500 }}>{current.desc}</p>}
          </div>

          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: '#64748B' }}>Jurisdiction Status:</span>
            <span style={{
              fontSize: 11, fontWeight: 800, color: '#065F46', background: '#D1FAE5',
              padding: '3px 10px', borderRadius: 4, border: '1px solid #A7F3D0',
            }}>
              Connected to Central Repository
            </span>
          </div>
        </div>
      </div>

      {/* ── 5. Main Content Workspace ── */}
      <main style={{ flex: 1, maxWidth: 1440, margin: '0 auto', width: '100%', padding: '20px 24px 48px', boxSizing: 'border-box' }}>
        {children}
      </main>
    </div>
  );
}
