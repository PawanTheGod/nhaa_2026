import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { ASSETS } from '../../assets';
import LoginForm from '../../components/admin/LoginForm';
import { authenticateMockUser } from '../../data/mockUsers';
import { loginOfficer } from '../../services/api';
import { getSession, setSession, getRedirectForRole } from '../../utils/adminAuth';

function sessionFromLoginResponse(data) {
  const role = data.role || data.officer?.role;
  return {
    token: data.token || data.access_token,
    role,
    name: data.name || data.officer?.name,
    district: data.district ?? data.officer?.district ?? null,
    state: data.state ?? data.officer?.state ?? null,
    officer_id: data.officer_id ?? data.officer?.id,
    username: data.username,
    authSource: 'api',
  };
}

const DEMO_CREDS = [
  { role: 'DSP', user: 'dsp', desc: 'Deputy Superintendent of Police (Level 1)' },
  { role: 'SP', user: 'sp', desc: 'Superintendent of Police (Level 2)' },
  { role: 'IG', user: 'ig', desc: 'Inspector General of Police (Level 3)' },
  { role: 'Operator', user: 'operator', desc: 'Call Centre Operator (Level 0)' },
];

export default function LoginScreen() {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const existing = getSession();

  if (existing?.role) {
    return <Navigate to={getRedirectForRole(existing.role)} replace />;
  }

  const handleSubmit = async ({ username, password }) => {
    setError('');
    setBusy(true);
    try {
      const data = await loginOfficer(username.trim(), password);
      const user = sessionFromLoginResponse(data);
      if (!user.token || !user.role) throw new Error('Login response missing token or role');
      setSession(user);
      navigate(getRedirectForRole(user.role));
      return;
    } catch (apiErr) {
      const user = authenticateMockUser(username, password);
      if (user) {
        setSession({ ...user, token: null, authSource: 'mock' });
        navigate(getRedirectForRole(user.role));
        return;
      }
      const msg = String(apiErr.message || '');
      const looksAuthReject = msg.includes('401') || msg.includes('403') || /invalid|incorrect|unauthorized/i.test(msg);
      if (looksAuthReject) {
        setError('Invalid credentials. Use: dsp / Test@1234');
      } else {
        setError('Server offline. Use credentials: dsp / Test@1234');
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#F1F5F9',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: "'Inter', 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    }}>
      {/* Top Government Ribbon */}
      <div style={{
        background: '#003366',
        color: '#FFFFFF',
        fontSize: 12,
        padding: '8px 24px',
        borderBottom: '2px solid #FF9933',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <img
            src={ASSETS.indianFlag}
            alt="Flag of India"
            style={{ height: 13, width: 20, objectFit: 'cover', borderRadius: 2 }}
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <span style={{ fontWeight: 600 }}>
            Government of India &nbsp;|&nbsp; Ministry of Social Justice &amp; Empowerment
          </span>
        </div>
        <span style={{ fontSize: 11, color: '#93C5FD', fontWeight: 600 }}>
          NHAA Helpline 14566 &mdash; Official Law Enforcement Portal
        </span>
      </div>

      <main id="login-main" style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '36px 24px',
        gap: 40,
        flexWrap: 'wrap',
      }}>
        {/* Left: Department Details & Hierarchy Matrix */}
        <div style={{
          width: '100%',
          maxWidth: 440,
          background: '#FFFFFF',
          borderRadius: 8,
          border: '1px solid #CBD5E1',
          padding: '32px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
            <img
              src={ASSETS.nationalEmblem}
              alt="National Emblem of India"
              style={{ height: 56, width: 'auto' }}
              onError={(e) => { e.target.src = `${import.meta.env.BASE_URL}ashoka_emblem.jpg`; }}
            />
            <div>
              <div style={{ fontSize: 11, color: '#64748B', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Government of India
              </div>
              <div style={{ fontSize: 13, color: '#1E293B', fontWeight: 700 }}>
                Ministry of Social Justice &amp; Empowerment
              </div>
              <div style={{ fontSize: 16, color: '#003366', fontWeight: 900 }}>
                NHAA 14566 Command Portal
              </div>
            </div>
          </div>

          <p style={{ fontSize: 13, color: '#475569', lineHeight: 1.6, margin: '0 0 20px' }}>
            Restricted-access monitoring dashboard for designated law enforcement officers investigating SC/ST atrocity reports under the PoA Act.
          </p>

          <div style={{ borderTop: '1px solid #E2E8F0', paddingTop: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 800, color: '#003366', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>
              Standard Operational Police Hierarchy
            </div>
            {[
              { code: 'LEVEL 3', role: 'Inspector General of Police (IG)', scope: 'National & Apex Supervisory Review', color: '#B91C1C' },
              { code: 'LEVEL 2', role: 'Superintendent of Police (SP)', scope: 'State Command & Escalated Investigation', color: '#D97706' },
              { code: 'LEVEL 1', role: 'Deputy Superintendent of Police (DSP)', scope: 'District Field Verification & Action', color: '#059669' },
              { code: 'LEVEL 0', role: 'Call Centre Operator', scope: 'Initial Intake & AI Triage Classification', color: '#0284C7' },
            ].map((item, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 12,
                padding: '8px 10px',
                borderRadius: 4,
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                marginBottom: 8,
              }}>
                <span style={{
                  fontSize: 10,
                  fontWeight: 800,
                  padding: '2px 6px',
                  borderRadius: 3,
                  background: item.color,
                  color: '#FFFFFF',
                  whiteSpace: 'nowrap',
                  marginTop: 2,
                }}>
                  {item.code}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, fontWeight: 800, color: '#0F172A' }}>{item.role}</div>
                  <div style={{ fontSize: 11, color: '#64748B', fontWeight: 500 }}>{item.scope}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Official Login Box */}
        <div style={{
          width: '100%',
          maxWidth: 420,
          background: '#FFFFFF',
          borderRadius: 8,
          border: '1px solid #CBD5E1',
          padding: '36px 32px',
          boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
        }}>
          <div style={{ marginBottom: 24 }}>
            <span style={{
              display: 'inline-block',
              fontSize: 11,
              fontWeight: 800,
              color: '#003366',
              background: '#EFF6FF',
              padding: '3px 10px',
              borderRadius: 3,
              marginBottom: 8,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              border: '1px solid #BFDBFE',
            }}>
              Official Law Enforcement Login
            </span>
            <h1 id="login-heading" style={{ margin: 0, fontSize: 22, fontWeight: 900, color: '#0F172A' }}>
              Officer Authentication
            </h1>
            <p style={{ margin: '6px 0 0', fontSize: 13, color: '#64748B' }}>
              Enter your assigned officer username and credentials
            </p>
          </div>

          <LoginForm onSubmit={handleSubmit} error={error} busy={busy} />

          {/* Test Credentials Box */}
          <div style={{
            marginTop: 24,
            padding: '14px 16px',
            background: '#F8FAFC',
            border: '1px solid #E2E8F0',
            borderRadius: 4,
          }}>
            <div style={{ fontSize: 11, fontWeight: 800, color: '#003366', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Designated Test Accounts (Password: <code style={{ background: '#E2E8F0', padding: '1px 5px', borderRadius: 3 }}>Test@1234</code>)
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 6 }}>
              {DEMO_CREDS.map(({ role, user }) => (
                <div key={user} style={{
                  fontSize: 11,
                  fontWeight: 600,
                  padding: '5px 8px',
                  borderRadius: 3,
                  background: '#FFFFFF',
                  border: '1px solid #CBD5E1',
                  color: '#334155',
                }}>
                  <strong style={{ color: '#003366' }}>{role}:</strong> {user}
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
