import React, { useState, useEffect } from 'react';
import { ASSETS } from '../assets';
import { useLang } from '../i18n/LangContext';
import { SUPPORTED_LANGUAGES } from '../i18n/translations';

const FONT_SIZES = [
  { label: 'A-', px: 12 },
  { label: 'A', px: 14 },
  { label: 'A+', px: 18 },
];

const TopBar = () => {
  const [fontSize, setFontSize] = useState(14);
  const [highContrast, setHighContrast] = useState(false);
  const { lang, setLang, t } = useLang();

  useEffect(() => {
    // Use !important via setProperty to override Tailwind's text-* classes
    document.documentElement.style.setProperty('font-size', `${fontSize}px`, 'important');
  }, [fontSize]);

  useEffect(() => {
    if (highContrast) {
      document.documentElement.style.filter = 'contrast(1.4) saturate(1.2)';
    } else {
      document.documentElement.style.filter = '';
    }
  }, [highContrast]);

  return (
    <div style={{ background: '#0073E6', color: '#fff', fontSize: 13, padding: '7px 0' }}>
      <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Left: India flag + Government of India */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 500 }}>
          <img
            src={ASSETS.indianFlag}
            alt="India"
            style={{ height: 16, width: 'auto' }}
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <span>{t('governmentOfIndia')}</span>
          <span style={{ opacity: 0.6 }}>|</span>
          <a
            href="https://india.gov.in/"
            target="_blank"
            rel="noreferrer"
            style={{ color: '#fff', textDecoration: 'none' }}
          >
            {t('indiaGovIn')} ↗
          </a>
        </div>

        {/* Right: Accessibility controls + Skip link */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, fontSize: 13, fontWeight: 500 }}>
          <a href="#content" style={{ color: '#fff', textDecoration: 'none' }}>{t('skipToMain')}</a>
          <span style={{ opacity: 0.4 }}>|</span>

          {/* Text resize */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }} role="group" aria-label={t('aNormal')}>
            {FONT_SIZES.map((opt) => (
              <button
                key={opt.label}
                type="button"
                aria-label={`Set text size ${opt.label}`}
                aria-pressed={fontSize === opt.px}
                onClick={() => setFontSize(opt.px)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: `${opt.px - 2}px`,
                  fontWeight: fontSize === opt.px ? 700 : 500,
                  textDecoration: fontSize === opt.px ? 'underline' : 'none',
                  padding: 0,
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
          <span style={{ opacity: 0.4 }}>|</span>

          {/* High Contrast */}
          <button
            type="button"
            aria-label="Toggle high contrast mode"
            aria-pressed={highContrast}
            onClick={() => setHighContrast((v) => !v)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#fff',
              cursor: 'pointer',
              fontWeight: highContrast ? 700 : 500,
              textDecoration: highContrast ? 'underline' : 'none',
              padding: 0,
              fontSize: 13,
            }}
          >
            {t('highContrast')}
          </button>
          <span style={{ opacity: 0.4 }}>|</span>

          {/* Language selector */}
          <label>
            <span style={{ position: 'absolute', left: '-9999px' }}>{t('selectLanguage')}</span>
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              aria-label={t('selectLanguage')}
              style={{
                background: '#0073E6',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.5)',
                borderRadius: 3,
                fontSize: 12,
                padding: '1px 4px',
                cursor: 'pointer',
              }}
            >
              {SUPPORTED_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
