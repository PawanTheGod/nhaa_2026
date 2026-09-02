import React, { useState } from 'react';
import PropTypes from 'prop-types';

export default function LoginForm({ onSubmit, error, busy = false }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (busy) return;
    onSubmit({ username, password });
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }} noValidate aria-describedby="login-demo-hint">
      <div>
        <label htmlFor="admin-username" style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#334155', marginBottom: 6 }}>
          Username
        </label>
        <input
          id="admin-username"
          type="text"
          autoComplete="username"
          required
          disabled={busy}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="e.g. operator, op_delhi_01"
          style={{
            width: '100%',
            padding: '12px 14px',
            fontSize: 14,
            border: '1px solid #CBD5E1',
            borderRadius: 8,
            boxSizing: 'border-box',
          }}
        />
      </div>
      <div>
        <label htmlFor="admin-password" style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#334155', marginBottom: 6 }}>
          Password
        </label>
        <input
          id="admin-password"
          type="password"
          autoComplete="current-password"
          required
          disabled={busy}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Test@1234"
          style={{
            width: '100%',
            padding: '12px 14px',
            fontSize: 14,
            border: '1px solid #CBD5E1',
            borderRadius: 8,
            boxSizing: 'border-box',
          }}
        />
      </div>
      {error && (
        <p role="alert" style={{ margin: 0, fontSize: 13, color: '#B91C1C', fontWeight: 600 }}>
          {error}
        </p>
      )}
      <button
        type="submit"
        disabled={busy}
        style={{
          background: '#0073E6',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          padding: '12px 20px',
          fontSize: 14,
          fontWeight: 700,
          cursor: busy ? 'wait' : 'pointer',
          opacity: busy ? 0.75 : 1,
        }}
      >
        {busy ? 'Signing in…' : 'Sign In'}
      </button>
      <p id="login-demo-hint" style={{ margin: 0, fontSize: 12, color: '#475569', lineHeight: 1.6 }}>
        Use <code>operator</code> / <code>Test@1234</code> (or <code>demo123</code>).
        Works offline with mock data; with backend running you get a live JWT.
      </p>
    </form>
  );
}

LoginForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  error: PropTypes.string,
  busy: PropTypes.bool,
};
