import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { User, Lock, Eye, EyeOff, ShieldCheck, RefreshCw, ArrowRight } from 'lucide-react';

const CAPTCHA_POOL = ['7X9K2', 'N4M8P', '3R6W9', 'H5T2Y', '9K4B7', 'E8M3Q'];

export default function LoginForm({ onSubmit, error, busy = false, initialUsername = '' }) {
  const [username, setUsername] = useState(initialUsername || 'dsp');
  const [password, setPassword] = useState('Test@1234');
  const [showPassword, setShowPassword] = useState(false);
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaIndex, setCaptchaIndex] = useState(0);
  const [captchaError, setCaptchaError] = useState('');

  useEffect(() => {
    if (initialUsername) {
      setUsername(initialUsername);
      setPassword('Test@1234');
    }
  }, [initialUsername]);

  const currentCaptcha = CAPTCHA_POOL[captchaIndex];

  const refreshCaptcha = () => {
    setCaptchaIndex((prev) => (prev + 1) % CAPTCHA_POOL.length);
    setCaptchaInput('');
    setCaptchaError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (busy) return;
    setCaptchaError('');

    // Optional user-friendly captcha validation
    if (captchaInput && captchaInput.trim().toUpperCase() !== currentCaptcha) {
      setCaptchaError('Incorrect Security Captcha. Please enter the characters shown.');
      return;
    }

    onSubmit({ username, password });
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }} noValidate>
      {/* Officer Username */}
      <div>
        <label htmlFor="admin-username" style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12.5, fontWeight: 800, color: '#1E293B', marginBottom: 6 }}>
          <User size={14} color="rgb(0, 115, 230)" /> Officer Official Username / Gov ID
        </label>
        <div style={{ position: 'relative' }}>
          <input
            id="admin-username"
            type="text"
            autoComplete="username"
            required
            disabled={busy}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. dsp, sp, judiciary, swo, operator"
            style={{
              width: '100%',
              padding: '11px 14px',
              fontSize: 14,
              border: '1.5px solid #CBD5E1',
              borderRadius: 6,
              boxSizing: 'border-box',
              outline: 'none',
              background: '#FFFFFF',
              color: '#0F172A',
              fontWeight: 600,
              transition: 'border-color 0.15s ease',
            }}
            onFocus={(e) => (e.target.style.borderColor = 'rgb(0, 115, 230)')}
            onBlur={(e) => (e.target.style.borderColor = '#CBD5E1')}
          />
        </div>
      </div>

      {/* Officer Password */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
          <label htmlFor="admin-password" style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12.5, fontWeight: 800, color: '#1E293B' }}>
            <Lock size={14} color="rgb(0, 115, 230)" /> Encrypted Password
          </label>
          <span style={{ fontSize: 11, color: '#64748B', fontWeight: 600 }}>Default: <code style={{ color: '#0F172A', fontWeight: 700 }}>Test@1234</code></span>
        </div>
        <div style={{ position: 'relative' }}>
          <input
            id="admin-password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="current-password"
            required
            disabled={busy}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter secure password"
            style={{
              width: '100%',
              padding: '11px 40px 11px 14px',
              fontSize: 14,
              border: '1.5px solid #CBD5E1',
              borderRadius: 6,
              boxSizing: 'border-box',
              outline: 'none',
              background: '#FFFFFF',
              color: '#0F172A',
              fontWeight: 600,
              transition: 'border-color 0.15s ease',
            }}
            onFocus={(e) => (e.target.style.borderColor = 'rgb(0, 115, 230)')}
            onBlur={(e) => (e.target.style.borderColor = '#CBD5E1')}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            style={{
              position: 'absolute',
              right: 10,
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              color: '#64748B',
              cursor: 'pointer',
              padding: 4,
              display: 'flex',
              alignItems: 'center',
            }}
            tabIndex={-1}
            title={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
      </div>

      {/* Security Captcha (Gov Security Pattern) */}
      <div style={{ background: '#F8FAFC', padding: '12px 14px', borderRadius: 6, border: '1px solid #E2E8F0' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontSize: 11.5, fontWeight: 700, color: '#475569' }}>
            Government Security Verification
          </span>
          <button
            type="button"
            onClick={refreshCaptcha}
            style={{
              background: 'none',
              border: 'none',
              fontSize: 11,
              color: 'rgb(0, 115, 230)',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <RefreshCw size={12} /> Refresh
          </button>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div style={{
            background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
            color: '#38BDF8',
            fontFamily: 'monospace',
            fontSize: 18,
            fontWeight: 900,
            letterSpacing: '0.25em',
            padding: '7px 16px',
            borderRadius: 4,
            userSelect: 'none',
            border: '1px solid #334155',
            textShadow: '0 0 6px rgba(56, 189, 248, 0.4)',
          }}>
            {currentCaptcha}
          </div>

          <input
            type="text"
            placeholder="Enter Captcha (or leave blank for demo)"
            value={captchaInput}
            onChange={(e) => setCaptchaInput(e.target.value)}
            style={{
              flex: 1,
              padding: '9px 12px',
              fontSize: 13,
              border: '1px solid #CBD5E1',
              borderRadius: 4,
              outline: 'none',
              textTransform: 'uppercase',
            }}
          />
        </div>
      </div>

      {captchaError && (
        <p role="alert" style={{ margin: 0, fontSize: 12, color: '#B91C1C', fontWeight: 700 }}>
          {captchaError}
        </p>
      )}

      {error && (
        <div role="alert" style={{
          background: '#FEF2F2',
          border: '1px solid #FECACA',
          borderRadius: 6,
          padding: '10px 14px',
          fontSize: 12.5,
          color: '#991B1B',
          fontWeight: 700,
        }}>
          {error}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={busy}
        style={{
          background: 'linear-gradient(135deg, rgb(0, 115, 230) 0%, rgb(0, 85, 180) 100%)',
          color: '#FFFFFF',
          border: 'none',
          borderRadius: 6,
          padding: '13px 20px',
          fontSize: 14,
          fontWeight: 800,
          cursor: busy ? 'wait' : 'pointer',
          opacity: busy ? 0.75 : 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          boxShadow: '0 2px 8px rgba(0, 115, 230, 0.25)',
          transition: 'all 0.15s ease',
        }}
      >
        <ShieldCheck size={17} />
        {busy ? 'Authenticating Credentials…' : 'Authenticate & Secure Login'}
        <ArrowRight size={15} />
      </button>
    </form>
  );
}

LoginForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  error: PropTypes.string,
  busy: PropTypes.bool,
  initialUsername: PropTypes.string,
};
