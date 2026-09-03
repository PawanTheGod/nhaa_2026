import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ASSETS } from '../../assets';
import { getSession, clearSession, ROLE_LABELS } from '../../utils/adminAuth';
import { useLang } from '../../i18n/LangContext';
import { ADMIN_TRANSLATIONS } from '../../i18n/adminTranslations';

const ADMIN_NAV = [
  { label: 'Operator', path: '/admin/operator', desc: 'Live case triage queue', roles: ['operator'] },
  { label: 'Responder', path: '/admin/responder', desc: 'Agency assigned tasks', roles: ['police', 'dlsa', 'medical', 'counselor', 'witness_protection'] },
  { label: 'District', path: '/admin/district', desc: 'District case queue', roles: ['district', 'operator'] },
  { label: 'State', path: '/admin/state', desc: 'State dashboard', roles: ['state', 'district'] },
  { label: 'Ministry', path: '/admin/ministry', desc: 'National overview', roles: ['ministry', 'state'] },
];

function navVisible(item, role) {
  if (!role) return true;
  return item.roles.includes(role) || role === 'ministry';
}

export default function AdminLayout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const session = getSession();
  const role = session?.role;
  const { lang, t } = useLang();
  const at = ADMIN_TRANSLATIONS[lang] || ADMIN_TRANSLATIONS.en;
  const current = ADMIN_NAV.find((n) => n.path === location.pathname);

  const handleLogout = () => {
    clearSession();
    navigate('/admin/login');
  };

  return (
    <div style={{ background: '#F8FAFC', color: '#0F172A', fontFamily: "'Inter', system-ui, sans-serif", minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ background: '#003366', color: '#fff', fontSize: 12, padding: '6px 0' }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 500 }}>
            <img src={ASSETS.indianFlag} alt="India" style={{ height: 14, width: 22, objectFit: 'cover', borderRadius: 2 }} onError={(e) => { e.target.style.display = 'none'; }} />
            Government of India | {at.dashboardSubtitle} | NHAA 14566
          </span>
          <Link to="/" style={{ color: '#fff', textDecoration: 'none', fontSize: 12, fontWeight: 500 }}>
            ← Public Portal
          </Link>
        </div>
      </div>

      <header style={{ background: '#fff', borderBottom: '1px solid #E2E8F0', padding: '14px 0', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 24 }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 14, textDecoration: 'none' }}>
            <img src={ASSETS.nationalEmblem} alt="National Emblem" style={{ height: 48, width: 'auto' }} onError={(e) => { e.target.src = `${import.meta.env.BASE_URL}ashoka_emblem.jpg`; }} />
            <div>
              <div style={{ fontSize: 11, color: '#647489', fontWeight: 500 }}>Government of India</div>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>Ministry of Social Justice &amp; Empowerment</div>
              <div style={{ fontSize: 16, fontWeight: 800, color: '#0F172A' }}>NHAA – Officer Dashboard</div>
            </div>
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 13, color: '#647489' }}>
              Signed in as: {session?.name || ROLE_LABELS[role] || 'Guest'}
            </span>
            <button
              type="button"
              onClick={handleLogout}
              aria-label="Sign out and return to login"
              style={{ background: '#0073E6', color: '#fff', fontSize: 13, fontWeight: 600, padding: '8px 18px', borderRadius: 8, border: 'none', cursor: 'pointer' }}
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <nav style={{ background: '#fff', borderBottom: '2px solid #0073E6', position: 'sticky', top: '58px', zIndex: 90 }} aria-label="Admin dashboard navigation">
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', gap: 4, overflowX: 'auto' }}>
          {ADMIN_NAV.filter((item) => navVisible(item, role)).map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '14px 20px',
                  fontSize: 13,
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? '#003366' : '#334155',
                  borderBottom: isActive ? '3px solid #F96302' : '3px solid transparent',
                  textDecoration: 'none',
                  background: isActive ? '#EEF2FF' : 'transparent',
                  whiteSpace: 'nowrap',
                }}
              >
                <span>{item.label}</span>
                <span style={{ fontSize: 11, color: isActive ? '#003366' : '#475569', marginTop: 2 }}>{item.desc}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', marginTop: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, color: '#0F172A', margin: 0 }}>
          {current?.label || 'Admin'} Dashboard
        </h1>
        {current?.desc && <p style={{ fontSize: 13, color: '#475569', marginTop: 4 }}>{current.desc}</p>}
      </div>

      <main style={{ flex: 1, maxWidth: 1380, margin: '0 auto', width: '100%', padding: '0 24px 48px' }}>
        {children}
      </main>
    </div>
  );
}
