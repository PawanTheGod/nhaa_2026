import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { ASSETS } from '../../assets';
import LoginForm from '../../components/admin/LoginForm';
import { authenticateMockUser } from '../../data/mockUsers';
import { getSession, setSession, getRedirectForRole } from '../../utils/adminAuth';

export default function LoginScreen() {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const existing = getSession();

  if (existing?.role) {
    return <Navigate to={getRedirectForRole(existing.role)} replace />;
  }

  const handleSubmit = ({ username, password }) => {
    const user = authenticateMockUser(username, password);
    if (!user) {
      setError('Invalid username or password. Try operator / demo123');
      return;
    }
    setSession(user);
    navigate(getRedirectForRole(user.role));
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
          <LoginForm onSubmit={handleSubmit} error={error} />
        </div>
      </main>
    </div>
  );
}
