import React, { useState, useEffect } from 'react';
import { ASSETS } from '../assets';

const FONT_SIZES = [
  { label: 'A-', px: 12 },
  { label: 'A', px: 14 },
  { label: 'A+', px: 18 },
];

const TopBar = () => {
  const [fontSize, setFontSize] = useState(14);
  const [highContrast, setHighContrast] = useState(false);
  const [lang, setLang] = useState('en');

  // Apply font size globally
  useEffect(() => {
    document.documentElement.style.fontSize = `${fontSize}px`;
  }, [fontSize]);

  // Apply high contrast mode
  useEffect(() => {
    if (highContrast) {
      document.documentElement.classList.add('high-contrast');
      document.documentElement.style.filter = 'contrast(1.4) saturate(1.2)';
    } else {
      document.documentElement.classList.remove('high-contrast');
      document.documentElement.style.filter = '';
    }
  }, [highContrast]);

  // Apply language attribute for screen readers
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const toggleScreenReader = () => {
    const enabled = !document.body.classList.contains('sr-mode');
    document.body.classList.toggle('sr-mode', enabled);
    if (enabled) {
      // Announce page content via aria-live region
      const announce = document.createElement('div');
      announce.setAttribute('role', 'status');
      announce.setAttribute('aria-live', 'polite');
      announce.id = 'sr-announce';
      announce.style.position = 'absolute';
      announce.style.left = '-9999px';
      announce.textContent = 'Screen reader mode enabled. Page heading: NHAA Portal.';
      document.body.appendChild(announce);
    } else {
      const old = document.getElementById('sr-announce');
      if (old) old.remove();
    }
  };

  return (
    <div className="bg-[#003087] text-white text-xs">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between py-1.5">
        {/* Left: Skip links */}
        <div className="flex items-center gap-3">
          <a href="#content" className="hover:underline opacity-80 hover:opacity-100 transition-opacity">
            Skip to Main Content
          </a>
          <span className="opacity-40">|</span>
          <a href="https://india.gov.in/" target="_blank" rel="noreferrer"
            className="hover:underline opacity-80 hover:opacity-100 transition-opacity flex items-center gap-1">
            <img src={ASSETS.indianFlag} alt="India" className="h-3.5 w-auto" onError={e => e.target.style.display='none'} />
            Government of India
          </a>
          <span className="opacity-40">|</span>
          <a href="https://india.gov.in/" target="_blank" rel="noreferrer"
            className="hover:underline opacity-80 hover:opacity-100 transition-opacity">
            India.gov.in
          </a>
        </div>

        {/* Right: Accessibility + Language + Admin */}
        <div className="flex items-center gap-3">
          {/* Text resize */}
          <div className="flex items-center gap-1.5 mr-1" role="group" aria-label="Text size">
            {FONT_SIZES.map((opt) => (
              <button
                key={opt.label}
                type="button"
                aria-label={`Set text size ${opt.label}`}
                aria-pressed={fontSize === opt.px}
                onClick={() => setFontSize(opt.px)}
                style={{ fontSize: `${opt.px - 2}px` }}
                className={`hover:opacity-100 transition-opacity ${
                  fontSize === opt.px
                    ? 'opacity-100 font-bold underline underline-offset-2'
                    : 'opacity-80'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
          <span className="opacity-40">|</span>

          {/* High Contrast */}
          <button
            type="button"
            aria-label="Toggle high contrast mode"
            aria-pressed={highContrast}
            onClick={() => setHighContrast((v) => !v)}
            className={`hover:underline hover:opacity-100 transition-opacity ${
              highContrast ? 'opacity-100 font-bold underline' : 'opacity-80'
            }`}
          >
            High Contrast
          </button>
          <span className="opacity-40">|</span>

          {/* Screen Reader */}
          <button
            type="button"
            aria-label="Toggle screen reader announcements"
            onClick={toggleScreenReader}
            className="hover:underline opacity-80 hover:opacity-100 transition-opacity"
          >
            Screen Reader
          </button>
          <span className="opacity-40">|</span>

          {/* Language selector */}
          <label className="opacity-80 hover:opacity-100">
            <span className="sr-only">Select language</span>
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              aria-label="Select language"
              className="bg-[#003087] text-white text-[10px] border border-white/40 rounded px-1 py-0.5 cursor-pointer focus:outline-none focus:ring-2 focus:ring-white"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="ta">தமிழ்</option>
              <option value="te">తెలుగు</option>
              <option value="bn">বাংলা</option>
              <option value="mr">मराठी</option>
            </select>
          </label>
          <span className="opacity-40">|</span>

          {/* Admin Portal */}
          <a
            href="#/admin/district"
            className="bg-[#003366] hover:bg-[#002244] text-white px-3 py-0.5 rounded text-[10px] font-semibold tracking-wide transition-colors"
          >
            Admin Portal
          </a>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
