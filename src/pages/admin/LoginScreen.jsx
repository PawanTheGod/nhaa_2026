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
      // Prefer live Supabase-backed auth
      const data = await loginOfficer(username.trim(), password);
      const user = sessionFromLoginResponse(data);
      if (!user.token || !user.role) {
        throw new Error('Login response missing token or role');
      }
      setSession(user);
      navigate(getRedirectForRole(user.role));
      return;
    } catch (apiErr) {
      // Backend down or wrong password — try local demo (accepts demo123 and Test@1234)
      const user = authenticateMockUser(username, password);
      if (user) {
        setSession({ ...user, token: null, authSource: 'mock' });
        navigate(getRedirectForRole(user.role));
        return;
      }
      const msg = String(apiErr.message || '');
      const looksAuthReject =
        msg.includes('401') ||
        msg.includes('403') ||
        /invalid|incorrect|unauthorized/i.test(msg);
      if (looksAuthReject) {
        setError('Invalid username or password. Try operator / Test@1234');
      } else {
        setError(
          'Auth server is offline (start backend on :8000). Offline demo: operator / Test@1234 or demo123'
        );
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #EEF2FF 0%, #F8FAFC 100%)',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: "'Inter', system-ui, sans-serif",
      }}
    >
      <a href="#login-main" className="skip-link">Skip to login form</a>
      <div style={{ background: '#003366', color: '#fff', fontSize: 12, padding: '8px 24px', textAlign: 'center' }}>
        Government of India | Ministry of Social Justice &amp; Empowerment | NHAA 14566 — Officer Login
      </div>

      <main
        id="login-main"
        aria-labelledby="login-heading"
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 24,
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: 420,
            background: '#fff',
            borderRadius: 16,
            border: '1px solid #E2E8F0',
            padding: '36px 32px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.06)',
          }}
        >
          <div style={{ textAlign: 'center', marginBottom: 28 }}>
            <img
              src={ASSETS.nationalEmblem}
              alt="National Emblem of India"
              style={{ height: 56, marginBottom: 12 }}
              onError={(e) => { e.target.src = `${import.meta.env.BASE_URL}ashoka_emblem.jpg`; }}
            />
            <h1 id="login-heading" style={{ margin: 0, fontSize: 22, fontWeight: 800, color: '#0F172A' }}>NHAA Officer Panel</h1>
            <p style={{ margin: '8px 0 0', fontSize: 13, color: '#475569' }}>
              Sign in to access your role-based dashboard
            </p>
          </div>
          <LoginForm onSubmit={handleSubmit} error={error} busy={busy} />
        </div>
      </main>
    </div>
  );
}
