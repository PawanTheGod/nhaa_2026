import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ASSETS } from './assets';

import SamaveshPage from './pages/SamaveshPage';
import AboutUsPage from './pages/AboutUsPage';
import SchemesPage from './pages/SchemesPage';
import VacanciesPage from './pages/VacanciesPage';
import TendersPage from './pages/TendersPage';
import ContactPage from './pages/ContactPage';
import NhaaPage from './pages/NhaaPage';

// ─── Professional SVG Icons (No Emojis) ────────────────────
const SearchIcon = () => (
  <svg width="18" height="18" fill="none" stroke="#64748B" strokeWidth="2" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const ExternalIcon = () => (
  <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
  </svg>
);

const AccessibilityIcon = () => (
  <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 2a2 2 0 100 4 2 2 0 000-4zm-1 6h2v6h-2V8zm-3 0h2v12H8V8zm8 0h2v12h-2V8z"/>
  </svg>
);

const MegaphoneIcon = () => (
  <svg width="18" height="18" fill="none" stroke="#fff" strokeWidth="2" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 8a3 3 0 010 6M11 5.882l-7.794 4.542a1 1 0 00-.456.86v1.432a1 1 0 00.456.86L11 18.118" />
  </svg>
);

const LocationPinIcon = () => (
  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" style={{ display: 'inline', marginRight: 4 }}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const FB  = () => <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>;
const TW  = () => <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>;
const IG  = () => <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>;
const YT  = () => <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>;
const WA  = () => <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>;

// ─── Data Constants ───────────────────────────────────────
const NAV_ITEMS = [
  { label: 'Home', path: '/' },
  { label: 'Department', children: [
    { label: 'About Us', path: '/about-us' },
    { label: "Who's Who", path: '/about-us' },
    { label: 'Directory', path: '/contact-us' },
  ]},
  { label: 'Associated Organisations', mega: true },
  { label: 'Offerings', children: [
    { label: 'Schemes & Services', path: '/schemes' },
    { label: 'Vacancies', path: '/vacancies' },
    { label: 'Tenders', path: '/tenders' },
  ]},
  { label: 'Documents', children: [
    { label: 'Annual Reports', path: '/about-us' },
    { label: 'Acts & Rules', path: '/about-us' },
    { label: 'Circulars & Notifications', path: '/tenders' },
  ]},
  { label: 'Events & Gallery', children: [
    { label: 'Events', path: '/about-us' },
    { label: 'Gallery', path: '/about-us' },
  ]},
  { label: 'Connect', children: [
    { label: 'Contact Us', path: '/contact-us' },
  ]},
];

// Mega Menu Data Matching Live Site
const MEGA_COLUMN_1 = {
  commissions: {
    title: 'COMMISSIONS',
    items: [
      { code: 'NCSC', label: 'National Commission for Scheduled Castes', logo: ASSETS.ncsc, path: '/samavesh' },
      { code: 'NCSK', label: 'National Commission for Safai Karamcharis', logo: ASSETS.ncsk, path: '/samavesh' },
      { code: 'NCBC', label: 'National Commission for Backward Classes', logo: ASSETS.ncbc, path: '/samavesh' },
    ]
  },
  corporations: {
    title: 'CORPORATIONS',
    items: [
      { code: 'NSFDC', label: 'National Scheduled Castes Finance and Development Corporation', logo: ASSETS.nsfdc, path: '/samavesh' },
      { code: 'NSKFDC', label: 'National Safai Karamcharis Finance and Development Corporation', logo: ASSETS.nskfdc, path: '/samavesh' },
      { code: 'NBCFDC', label: 'National Backward Classes Finance and Development Corporation', logo: ASSETS.nbcfdc, path: '/samavesh' },
    ]
  }
};

const MEGA_COLUMN_2 = {
  title: 'FOUNDATION / AUTONOMOUS BODIES',
  items: [
    { code: 'DAF', label: 'Dr. Ambedkar Foundation', logo: ASSETS.daf, path: '/samavesh' },
    { code: 'DAIC', label: 'Dr Ambedkar International Centre', logo: ASSETS.daic, path: '/samavesh' },
    { code: 'BJRNF', label: 'Babu Jagjivan Ram National Foundation', logo: ASSETS.bjrnf, path: '/samavesh' },
    { code: 'DWBDNC', label: 'Development and Welfare Board for De-notified, Nomadic, and Semi-Nomadic Communities', logo: ASSETS.dwbdnc, path: '/samavesh' },
    { code: 'NISD', label: 'National Institute of Social Defence', logo: ASSETS.nisd, path: '/samavesh' },
  ]
};

const MEGA_COLUMN_3 = {
  title: 'SCHEME SPECIFIC THEMATIC PORTALS',
  items: [
    { code: 'SCW', label: 'Senior Citizens Welfare', logo: ASSETS.scw, path: '/samavesh' },
    { code: 'PM-AJAY', label: 'Pradhan Mantri Anusuchit Jaati Abhyuday Yojna', logo: ASSETS.pmajay, path: '/schemes' },
    { code: 'SMILE - Transgender', label: 'National Portal for Transgender Persons', logo: ASSETS.transgender, path: '/samavesh' },
    { code: 'SMILE Beggary', label: 'Support for Marginalized Individuals for Livelihood and Enterprise', logo: ASSETS.smile, path: '/samavesh' },
    { code: 'NOS', label: 'National Overseas Scholarship', logo: ASSETS.nos, path: '/schemes' },
    { code: 'NMBA', label: 'Nasha Mukt Bharat Abhiyaan', logo: ASSETS.nmba, path: '/samavesh' },
  ]
};

const UPDATES = [
  { type: 'Documents', title: 'Extension of Application Submission Date for Financial Adviser (FA) Post at DAIC', date: '31 Aug 2026' },
  { type: 'Documents', title: 'Annual Report 2025-26 (Hindi)', date: '22 Apr 2026' },
  { type: 'Schemes And Services', title: 'Dr. Ambedkar Medical Aid Scheme (Revised in 2026)', date: '15 Mar 2026' },
];

const DOCUMENTS = [
  { title: 'Annual Report 2025-26 (English)', date: '22 Apr 2026', type: 'Annual Reports', size: '0 MB' },
  { title: 'Annual Report 2025-26 (Hindi)', date: '22 Apr 2026', type: 'Annual Reports', size: '89.2 MB' },
  { title: 'Annual Report 2024-25', date: '23 Dec 2025', type: 'Annual Reports', size: '195.41 MB' },
  { title: 'Annual Report 2023-24', date: '22 Dec 2025', type: 'Annual Reports', size: '6.52 MB' },
];

const SCHEMES = [
  { title: 'Pradhan Mantri Anusuchit Jaati Abhyuday Yojna (PM-AJAY)', cat: 'Scheduled Castes', path: '/schemes' },
  { title: 'PM Young Achievers Scholarship Award Scheme (PM-YASASVI)', cat: 'OBC', path: '/schemes' },
  { title: 'Centrally Sponsored Scheme for PCR Act 1955 & SC/ST Prevention of Atrocities Act', cat: 'Civil Rights', path: '/schemes' },
];

const VACANCIES = [
  { title: 'Short Term Internship Programme at DAIC (September 2026)', org: 'DAIC', path: '/vacancies' },
  { title: 'Vacancy Circular for the post of Financial Advisor', org: 'DAIC', path: '/vacancies' },
  { title: 'Recruitment Notification for Deputy General Manager (Finance)', org: 'NBCFDC', path: '/vacancies' },
];

const TENDERS = [
  { title: 'Notice Inviting Expression of Interest for District De-Addiction Centres', org: 'DAIC', path: '/tenders' },
  { title: 'Invitation for Bids for Manpower Outsourcing Services via GeM', org: 'DAF', path: '/tenders' },
  { title: 'Tender for Security Guards & Parking Management at Lok Nayak Bhawan', org: 'NCSK', path: '/tenders' },
];

const HOME_ORGS = [
  { code: 'NCSC', title: 'National Commission for Scheduled Castes', logo: ASSETS.ncsc },
  { code: 'NCSK', title: 'National Commission for Safai Karamcharis', logo: ASSETS.ncsk },
  { code: 'NCBC', title: 'National Commission for Backward Classes', logo: ASSETS.ncbc },
  { code: 'NSFDC', title: 'National Scheduled Castes Finance and Development Corporation', logo: ASSETS.nsfdc },
  { code: 'NSKFDC', title: 'National Safai Karamcharis Finance and Development Corporation', logo: ASSETS.nskfdc },
  { code: 'NBCFDC', title: 'National Backward Classes Finance and Development Corporation', logo: ASSETS.nbcfdc },
];

const FOOTER_LINKS = {
  Department: [
    { label: 'About Ministry', path: '/about-us' },
    { label: 'Vision & Mission', path: '/about-us' },
    { label: 'Organisational Chart', path: '/about-us' },
    { label: 'Ministers & Officials', path: '/about-us' },
  ],
  Services: [
    { label: 'Schemes & Benefits', path: '/schemes' },
    { label: 'Tenders', path: '/tenders' },
    { label: 'Vacancies', path: '/vacancies' },
  ],
  Support: [
    { label: 'Help & Support', path: '/contact-us' },
    { label: 'Contact Us', path: '/contact-us' },
    { label: 'RTI', path: '/about-us' },
    { label: 'Sitemap', path: '/' },
  ],
  Resources: [
    { label: 'Notices', path: '/tenders' },
    { label: 'Acts & Rules', path: '/about-us' },
    { label: 'Reports', path: '/about-us' },
    { label: 'Publications', path: '/about-us' },
    { label: 'Statistics', path: '/schemes' },
  ],
};

const BANNERS = [ASSETS.banner1, ASSETS.banner2, ASSETS.banner3, ASSETS.banner4, ASSETS.banner5];

// ─── TOP BAR ───────────────────────────────────────────────
function TopBar() {
  return (
    <div style={{ background: '#0073E6', color: '#fff', fontSize: 13, padding: '7px 0' }}>
      <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 500 }}>
          <img src={ASSETS.indianFlag} alt="India" style={{ height: 16, width: 'auto' }} onError={e => e.target.style.display = 'none'} />
          <span>Government of India</span>
          <ExternalIcon />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, fontSize: 13, fontWeight: 500 }}>
          <a href="#content" style={{ color: '#fff', textDecoration: 'none' }}>Skip to Main Content</a>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <AccessibilityIcon />
            <span style={{ fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>अA</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── HEADER ────────────────────────────────────────────────
function Header() {
  return (
    <header style={{ background: '#fff', padding: '16px 0', borderBottom: '1px solid #E5E7EB' }}>
      <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Link to="/" style={{ flexShrink: 0 }}>
            <img src={ASSETS.nationalEmblem} alt="Emblem" style={{ height: 68, width: 'auto' }} onError={e => { e.target.src = '/ashoka_emblem.jpg'; }} />
          </Link>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
              <span style={{ background: '#FF9900', color: '#000', fontSize: 10, fontWeight: 800, padding: '1px 6px', borderRadius: 3, letterSpacing: 0.5 }}>BETA</span>
            </div>
            <div style={{ fontSize: 12, color: '#4B5563', fontWeight: 500, lineHeight: 1.3 }}>Government of India</div>
            <div style={{ fontSize: 13, color: '#374151', fontWeight: 600, lineHeight: 1.3 }}>Ministry of Social Justice &amp; Empowerment</div>
            <h1 style={{ fontSize: 20, fontWeight: 800, color: '#111827', margin: '2px 0 0', lineHeight: 1.2 }}>
              <Link to="/" style={{ color: 'inherit', textDecoration: 'none' }}>Department of Social Justice &amp; Empowerment</Link>
            </h1>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ position: 'relative', width: 340 }}>
            <input
              type="text"
              placeholder="Search Schemes, Services, Documents"
              style={{
                width: '100%',
                padding: '9px 16px 9px 40px',
                fontSize: 13,
                border: '1px solid #E5E7EB',
                borderRadius: 8,
                background: '#FAFAFA',
                outline: 'none'
              }}
            />
            <div style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)' }}>
              <SearchIcon />
            </div>
          </div>

          <a href="https://digitalindia.gov.in/" target="_blank" rel="noreferrer" style={{ flexShrink: 0 }}>
            <img src={ASSETS.digitalIndia} alt="Digital India" style={{ height: 44, width: 'auto' }} onError={e => e.target.style.display = 'none'} />
          </a>

          <Link
            to="/samavesh"
            style={{
              background: '#0073E6',
              color: '#fff',
              fontSize: 14,
              fontWeight: 600,
              padding: '9px 20px',
              borderRadius: 8,
              textDecoration: 'none',
              whiteSpace: 'nowrap',
              boxShadow: '0 1px 3px rgba(0,115,230,0.3)',
              transition: 'background 0.2s'
            }}
          >
            Admin Login
          </Link>
        </div>
      </div>
    </header>
  );
}

// ─── NAVBAR WITH 3-COLUMN MEGA MENU ────────────────────────
function Navbar() {
  const location = useLocation();

  return (
    <nav style={{ background: '#fff', borderTop: '1px solid #E5E7EB', borderBottom: '1px solid #E5E7EB', position: 'sticky', top: 0, zIndex: 999 }}>
      <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }} className="desktop-nav">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            const isMega = item.mega;

            return (
              <div key={item.label} className="nav-item" style={{ position: 'relative' }}>
                <Link
                  to={item.path || '#'}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    padding: '14px 16px',
                    fontSize: 14,
                    fontWeight: isActive || isMega ? 700 : 500,
                    color: isActive ? '#0073E6' : '#374151',
                    background: isMega ? '#D9EAFD' : 'transparent',
                    borderRadius: isMega ? '8px 8px 0 0' : 0,
                    textDecoration: 'none',
                    borderBottom: isActive ? '3px solid #0073E6' : '3px solid transparent',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.15s'
                  }}
                >
                  {item.label}
                  {(item.children || item.mega) && <span style={{ fontSize: 9, opacity: 0.6, marginLeft: 2 }}>{isMega ? '▲' : '▼'}</span>}
                </Link>

                {item.children && (
                  <div className="nav-dropdown">
                    {item.children.map(c => <Link key={c.label} to={c.path}>{c.label}</Link>)}
                  </div>
                )}

                {item.mega && (
                  <div className="nav-mega">
                    <div>
                      <h5 className="mega-col-title">{MEGA_COLUMN_1.commissions.title}</h5>
                      {MEGA_COLUMN_1.commissions.items.map((i) => (
                        <Link key={i.code} to={i.path} className="mega-item">
                          <div className="mega-item-icon">
                            <img src={i.logo} alt="" onError={e => e.target.style.display = 'none'} />
                          </div>
                          <div className="mega-item-text">
                            <h6>{i.code}</h6>
                            <p>{i.label}</p>
                          </div>
                        </Link>
                      ))}

                      <div style={{ marginTop: 20 }}>
                        <h5 className="mega-col-title">{MEGA_COLUMN_1.corporations.title}</h5>
                        {MEGA_COLUMN_1.corporations.items.map((i) => (
                          <Link key={i.code} to={i.path} className="mega-item">
                            <div className="mega-item-icon">
                              <img src={i.logo} alt="" onError={e => e.target.style.display = 'none'} />
                            </div>
                            <div className="mega-item-text">
                              <h6>{i.code}</h6>
                              <p>{i.label}</p>
                            </div>
                          </Link>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h5 className="mega-col-title">{MEGA_COLUMN_2.title}</h5>
                      {MEGA_COLUMN_2.items.map((i) => (
                        <Link key={i.code} to={i.path} className="mega-item">
                          <div className="mega-item-icon">
                            <img src={i.logo} alt="" onError={e => e.target.style.display = 'none'} />
                          </div>
                          <div className="mega-item-text">
                            <h6>{i.code}</h6>
                            <p>{i.label}</p>
                          </div>
                        </Link>
                      ))}
                    </div>

                    <div>
                      <h5 className="mega-col-title">{MEGA_COLUMN_3.title}</h5>
                      {MEGA_COLUMN_3.items.map((i) => (
                        <Link key={i.code} to={i.path} className="mega-item">
                          <div className="mega-item-icon">
                            <img src={i.logo} alt="" onError={e => e.target.style.display = 'none'} />
                          </div>
                          <div className="mega-item-text">
                            <h6>{i.code}</h6>
                            <p>{i.label}</p>
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

// ─── SAMAVESH BANNER ───────────────────────────────────────
function SamaveshBanner() {
  return (
    <div style={{ background: '#F96302', padding: '14px 0', color: '#fff' }}>
      <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <img src={ASSETS.samavesh} alt="SAMAVESH" style={{ height: 44, width: 'auto', background: '#fff', borderRadius: '50%', padding: 2 }} onError={e => e.target.style.display = 'none'} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 22, fontWeight: 900, letterSpacing: 0.5, color: '#fff' }}>SAMAVESH</span>
            <span style={{ fontSize: 20, opacity: 0.6 }}>|</span>
            <span style={{ fontSize: 15, fontWeight: 500, color: '#fff' }}>Single Access Mechanism for All Verticals of Empowerment &amp; Social Harmony</span>
          </div>
        </div>
        <Link
          to="/samavesh"
          style={{
            background: '#198754',
            color: '#fff',
            fontSize: 14,
            fontWeight: 700,
            padding: '8px 22px',
            borderRadius: 8,
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            boxShadow: '0 2px 4px rgba(0,0,0,0.15)'
          }}
        >
          Explore ➔
        </Link>
      </div>
    </div>
  );
}

// ─── HERO CAROUSEL ─────────────────────────────────────────
function Hero() {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setIdx(p => (p + 1) % BANNERS.length), 5000);
    return () => clearInterval(t);
  }, []);

  return (
    <div style={{ position: 'relative', background: '#0f172a', overflow: 'hidden' }}>
      {BANNERS.map((src, i) => (
        <div key={i} style={{ position: i === 0 ? 'relative' : 'absolute', inset: 0, opacity: i === idx ? 1 : 0, transition: 'opacity 0.7s ease', zIndex: i === idx ? 1 : 0 }}>
          <img src={src} alt={`Banner ${i + 1}`} style={{ width: '100%', height: '520px', objectFit: 'cover', display: 'block' }} onError={e => e.target.style.display = 'none'} />
        </div>
      ))}

      <div style={{ position: 'absolute', bottom: 20, left: '50%', transform: 'translateX(-50%)', display: 'flex', gap: 8, zIndex: 10 }}>
        {BANNERS.map((_, i) => (
          <button key={i} onClick={() => setIdx(i)} style={{ width: i === idx ? 28 : 10, height: 10, borderRadius: 5, border: 'none', cursor: 'pointer', background: i === idx ? '#F96302' : 'rgba(255,255,255,0.6)', transition: 'all 0.3s' }} />
        ))}
      </div>

      {[{ dir: 'left', fn: () => setIdx(p => (p - 1 + BANNERS.length) % BANNERS.length) }, { dir: 'right', fn: () => setIdx(p => (p + 1) % BANNERS.length) }].map(({ dir, fn }) => (
        <button key={dir} onClick={fn} style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', zIndex: 10, [dir]: 16, width: 44, height: 44, borderRadius: '50%', border: 'none', background: 'rgba(0,0,0,0.4)', color: '#fff', cursor: 'pointer', fontSize: 24, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {dir === 'left' ? '‹' : '›'}
        </button>
      ))}

      <Link
        to="/samavesh"
        style={{
          position: 'fixed',
          right: 0,
          top: '50%',
          transform: 'translateY(-50%) rotate(-90deg)',
          transformOrigin: 'bottom right',
          background: '#0073E6',
          color: '#fff',
          fontSize: 12,
          fontWeight: 700,
          padding: '8px 16px',
          borderRadius: '8px 8px 0 0',
          textDecoration: 'none',
          zIndex: 9999,
          boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: 6
        }}
      >
        Important Links
      </Link>
    </div>
  );
}

// ─── LATEST UPDATES TOP BANNER ─────────────────────────────
function LatestUpdatesBar() {
  const [updateIdx, setUpdateIdx] = useState(0);

  const nextUpdate = () => setUpdateIdx(p => (p + 1) % UPDATES.length);
  const prevUpdate = () => setUpdateIdx(p => (p - 1 + UPDATES.length) % UPDATES.length);

  return (
    <div style={{ background: '#0073E6', color: '#fff', padding: '0', display: 'flex', alignItems: 'center' }}>
      <div style={{ maxWidth: 1380, margin: '0 auto', width: '100%', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ background: '#005BB5', padding: '14px 24px', display: 'flex', alignItems: 'center', gap: 10, fontWeight: 700, fontSize: 15, flexShrink: 0 }}>
          <MegaphoneIcon /> Latest Updates
        </div>

        <div style={{ flex: 1, padding: '0 24px', overflow: 'hidden' }}>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', opacity: 0.9 }}>
            {UPDATES[updateIdx].type}
          </div>
          <div style={{ fontSize: 13, fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {UPDATES[updateIdx].title}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
          <div style={{ display: 'flex', gap: 6 }}>
            <button onClick={prevUpdate} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: 16, padding: '4px 8px' }}>‹</button>
            <button onClick={nextUpdate} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: 16, padding: '4px 8px' }}>›</button>
          </div>

          <Link
            to="/tenders"
            style={{
              border: '1px solid rgba(255,255,255,0.8)',
              color: '#fff',
              fontSize: 12,
              fontWeight: 600,
              padding: '6px 14px',
              borderRadius: 6,
              textDecoration: 'none'
            }}
          >
            View All Updates
          </Link>
        </div>
      </div>
    </div>
  );
}

// ─── HOME PAGE COMPONENT ───────────────────────────────────
function HomePage() {
  const [personaIdx, setPersonaIdx] = useState(0);
  const [tab, setTab] = useState('schemes');

  const personas = [
    { title: 'Beneficiary', desc: 'Discover schemes, scholarships & financial assistance.', img: ASSETS.beneficiary },
    { title: 'Government Official', desc: 'Access administrative portals, reports & dashboards.', img: ASSETS.governmentOfficial },
  ];

  const offeringsData = tab === 'schemes' ? SCHEMES : tab === 'vacancies' ? VACANCIES : TENDERS;

  return (
    <>
      <SamaveshBanner />
      <Hero />
      <LatestUpdatesBar />

      <main id="content" style={{ background: '#F8FAFC' }}>
        
        {/* Stats Banner Section */}
        <div style={{ maxWidth: 1380, margin: '36px auto 0', padding: '0 24px' }}>
          <div style={{ background: '#0073E6', borderRadius: 16, padding: '28px 36px', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 24, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', flex: 1, justifyBetween: 'space-around', gap: 32 }}>
              
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', opacity: 0.8, letterSpacing: 0.5 }}>CUMULATIVE DISBURSEMENT</div>
                <div style={{ fontSize: 32, fontWeight: 900, margin: '2px 0' }}>₹67,977 <span style={{ fontSize: 16, fontWeight: 600 }}>Crore</span></div>
                <div style={{ fontSize: 12, opacity: 0.9 }}>Scholarships for Scheduled Castes</div>
              </div>

              <div style={{ width: 1, height: 48, background: 'rgba(255,255,255,0.2)' }} />

              <div>
                <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', opacity: 0.8, letterSpacing: 0.5 }}>BENEFICIARY COVERAGE</div>
                <div style={{ fontSize: 32, fontWeight: 900, margin: '2px 0' }}>19.82 <span style={{ fontSize: 16, fontWeight: 600 }}>Crore</span></div>
                <div style={{ fontSize: 12, opacity: 0.9 }}>Cumulative across all schemes</div>
              </div>

              <div style={{ width: 1, height: 48, background: 'rgba(255,255,255,0.2)' }} />

              <div>
                <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', opacity: 0.8, letterSpacing: 0.5 }}>RELEASE OF FUNDS, FY 2025–26</div>
                <div style={{ fontSize: 32, fontWeight: 900, margin: '2px 0' }}>₹8,731 <span style={{ fontSize: 16, fontWeight: 600 }}>Crore</span></div>
                <div style={{ fontSize: 12, opacity: 0.9 }}>Provisional · 14.3% above previous year</div>
              </div>
            </div>

            <a
              href="https://www.dosje.gov.in/dashboard"
              target="_blank"
              rel="noreferrer"
              style={{
                background: '#fff',
                color: '#0073E6',
                fontSize: 14,
                fontWeight: 700,
                padding: '10px 22px',
                borderRadius: 24,
                textDecoration: 'none',
                flexShrink: 0
              }}
            >
              View Dashboard ❯
            </a>
          </div>
        </div>

        {/* Recent Documents & User Personas Split Section */}
        <div style={{ maxWidth: 1380, margin: '40px auto', padding: '0 24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '3fr 1.6fr', gap: 32, alignItems: 'stretch' }}>
            
            {/* Left: Recent Documents Grid */}
            <div>
              <h2 style={{ fontSize: 24, fontWeight: 800, color: '#003366', marginBottom: 20 }}>Recent Documents</h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                {DOCUMENTS.map((doc, i) => (
                  <div key={i} style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: 16, padding: 20, display: 'flex', flexDirection: 'column', justifyBetween: 'space-between' }}>
                    <div>
                      <h4 style={{ fontSize: 15, fontWeight: 700, color: '#1E293B', margin: '0 0 4px' }}>{doc.title}</h4>
                      <div style={{ fontSize: 12, color: '#64748B', marginBottom: 12 }}>{doc.date}</div>
                      <div style={{ fontSize: 11, color: '#475569', marginBottom: 16 }}>
                        Type: {doc.type} • File: PDF ({doc.size})
                      </div>
                    </div>
                    
                    <a
                      href="https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/04/71441776233188.pdf"
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        alignSelf: 'flex-end',
                        border: '1px solid #0073E6',
                        color: '#0073E6',
                        fontSize: 12,
                        fontWeight: 600,
                        padding: '6px 16px',
                        borderRadius: 8,
                        textDecoration: 'none'
                      }}
                    >
                      View Online
                    </a>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Explore User Personas Container */}
            <div style={{ background: '#0073E6', borderRadius: 20, padding: 28, color: '#fff', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
              <h3 style={{ fontSize: 22, fontWeight: 800, margin: '0 0 6px' }}>Explore User Personas</h3>
              <p style={{ fontSize: 13, opacity: 0.9, margin: '0 0 20px' }}>Choose your role to discover services made for you.</p>

              <div style={{ background: '#005BB5', borderRadius: 16, padding: 20, width: '100%', flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                <img
                  src={personas[personaIdx].img}
                  alt=""
                  style={{ height: 180, width: 'auto', objectFit: 'contain', marginBottom: 12 }}
                  onError={e => e.target.style.display = 'none'}
                />
                <h4 style={{ fontSize: 18, fontWeight: 800, margin: 0 }}>{personas[personaIdx].title}</h4>

                <button onClick={() => setPersonaIdx(p => (p === 0 ? 1 : 0))} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#fff', fontSize: 24, cursor: 'pointer' }}>‹</button>
                <button onClick={() => setPersonaIdx(p => (p === 0 ? 1 : 0))} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#fff', fontSize: 24, cursor: 'pointer' }}>›</button>
              </div>
            </div>

          </div>
        </div>

        {/* Associated Organisations Section matching live site .home-org-items-sec */}
        <div style={{ maxWidth: 1380, margin: '48px auto', padding: '0 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
            <div>
              <h2 style={{ fontSize: 24, fontWeight: 800, color: '#003366', margin: '0 0 4px' }}>Associated Organisations</h2>
              <p style={{ fontSize: 14, color: '#64748B', margin: 0 }}>Autonomous commissions, foundations and corporations under the Ministry.</p>
            </div>
            <Link to="/samavesh" style={{ border: '1px solid #0073E6', color: '#0073E6', fontSize: 13, fontWeight: 600, padding: '8px 18px', borderRadius: 8, textDecoration: 'none' }}>
              View All Organisations
            </Link>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {HOME_ORGS.map((org) => (
              <Link
                key={org.code}
                to="/samavesh"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  padding: '20px 24px',
                  background: 'linear-gradient(90deg, #F2F9FF 0%, #DAEDFF 100%)',
                  border: '1px solid rgba(20, 137, 250, 0.4)',
                  borderRadius: 20,
                  textDecoration: 'none',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ width: 48, height: 48, borderRadius: '50%', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.12)', flexShrink: 0 }}>
                  <img src={org.logo} alt="" style={{ width: 32, height: 32, objectFit: 'contain' }} onError={e => e.target.style.display = 'none'} />
                </div>
                <div>
                  <strong style={{ fontSize: 16, color: '#0a4d8f', display: 'block', marginBottom: 2 }}>{org.code}</strong>
                  <span style={{ fontSize: 13, color: '#1E293B', lineHeight: 1.3 }}>{org.title}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Our Offerings Section */}
        <div style={{ maxWidth: 1380, margin: '48px auto', padding: '0 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <h2 style={{ fontSize: 24, fontWeight: 800, color: '#003366', margin: '0 0 4px' }}>Our Offerings</h2>
              <p style={{ fontSize: 14, color: '#64748B', margin: 0 }}>Discover our schemes, careers, and partnerships.</p>
            </div>
            
            <Link to="/schemes" style={{ border: '1px solid #0073E6', color: '#0073E6', fontSize: 13, fontWeight: 600, padding: '8px 18px', borderRadius: 8, textDecoration: 'none' }}>
              View all Schemes
            </Link>
          </div>

          <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
            <button onClick={() => setTab('schemes')} style={{ background: tab === 'schemes' ? '#0073E6' : '#E2E8F0', color: tab === 'schemes' ? '#fff' : '#475569', border: 'none', padding: '10px 24px', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>Schemes</button>
            <button onClick={() => setTab('vacancies')} style={{ background: tab === 'vacancies' ? '#0073E6' : '#E2E8F0', color: tab === 'vacancies' ? '#fff' : '#475569', border: 'none', padding: '10px 24px', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>Vacancies</button>
            <button onClick={() => setTab('tenders')} style={{ background: tab === 'tenders' ? '#0073E6' : '#E2E8F0', color: tab === 'tenders' ? '#fff' : '#475569', border: 'none', padding: '10px 24px', borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'pointer' }}>Tenders</button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 20 }}>
            {offeringsData.map((s, i) => (
              <div key={i} style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: 14, padding: 20 }}>
                <h4 style={{ fontSize: 15, fontWeight: 700, color: '#1E293B', marginBottom: 12 }}>{s.title}</h4>
                <Link to={s.path || '/schemes'} style={{ color: '#0073E6', fontSize: 13, fontWeight: 600, textDecoration: 'none' }}>Read More ➔</Link>
              </div>
            ))}
          </div>
        </div>

      </main>
    </>
  );
}

// ─── FOOTER COMPONENT ──────────────────────────────────────
function Footer() {
  return (
    <footer style={{ background: '#0078DB', color: '#fff' }}>
      <div style={{ background: '#F96302', padding: '18px 0' }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h3 style={{ fontSize: 18, fontWeight: 800, color: '#fff', margin: '0 0 2px' }}>Need Support?</h3>
            <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.9)', margin: 0 }}>Reach out to us and we will get back to you!</p>
          </div>
          <Link to="/contact-us" style={{ background: '#fff', color: '#0078DB', fontWeight: 700, padding: '8px 24px', borderRadius: 8, textDecoration: 'none', fontSize: 13, border: '1px solid #fff' }}>
            Get in Touch
          </Link>
        </div>
      </div>

      <div style={{ padding: '48px 0 32px' }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2.2fr 1fr 1fr 1fr 1fr 2fr', gap: 32, marginBottom: 40 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <img src={ASSETS.nationalEmblemWhite} alt="Emblem" style={{ height: 56, width: 'auto' }} onError={e => { e.target.src = ASSETS.nationalEmblem; }} />
                <div>
                  <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.8)' }}>Government of India</div>
                  <div style={{ fontSize: 14, fontWeight: 800, color: '#fff' }}>Ministry of Social Justice &amp; Empowerment</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#fff' }}>Department of Social Justice &amp; Empowerment</div>
                </div>
              </div>

              <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.85)', lineHeight: 1.6, marginBottom: 16 }}>
                <LocationPinIcon /> 8th Floor, GPOA-3, Netaji Nagar, New Delhi-110023
              </p>

              <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
                {[{ Icon: FB, href: 'https://www.facebook.com/goimsje' }, { Icon: TW, href: 'https://x.com/msjegoi' }, { Icon: IG, href: 'https://www.instagram.com/msjegoi' }, { Icon: YT, href: 'https://www.youtube.com/@ministryofsocialjustice511' }, { Icon: WA, href: 'https://whatsapp.com/channel/0029Vb7GfwH6mYPMHOvTd51W' }].map(({ Icon, href }, i) => (
                  <a key={i} href={href} target="_blank" rel="noreferrer" className="social-btn"><Icon /></a>
                ))}
              </div>

              <div style={{ fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.9)' }}>
                Total Visits: <span style={{ fontWeight: 800 }}>296,249</span>
              </div>
            </div>

            {Object.entries(FOOTER_LINKS).map(([sec, links]) => (
              <div key={sec}>
                <h4 style={{ fontSize: 14, fontWeight: 800, color: '#fff', marginBottom: 16 }}>{sec}</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {links.map(l => <Link key={l.label} to={l.path} style={{ color: 'rgba(255,255,255,0.85)', fontSize: 13, textDecoration: 'none' }}>{l.label}</Link>)}
                </div>
              </div>
            ))}

            <div>
              <img src={ASSETS.negd} alt="NeGD" style={{ height: 32, width: 'auto', marginBottom: 12 }} onError={e => e.target.style.display = 'none'} />
              <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.85)', lineHeight: 1.5, marginBottom: 16 }}>
                Digital India Corporation Ministry of Electronics &amp; IT (MeitY), Government of India
              </p>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.8)', marginBottom: 8 }}>Powered by Digital India</div>
              <img src={ASSETS.digitalIndiaWhite} alt="Digital India" style={{ height: 28, width: 'auto', marginBottom: 16 }} onError={e => e.target.style.display = 'none'} />
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.7)' }}>Last Updated: 31 Aug 2026</div>
            </div>

          </div>
        </div>
      </div>

      <div style={{ background: '#005BB5', padding: '14px 0', fontSize: 12, color: 'rgba(255,255,255,0.9)' }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            Contents of this website owned and managed by Department of Social Justice and Empowerment, Ministry of Social Justice and Empowerment, GOI
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            {['Copyright Policy', 'Hyperlinking Policy', 'Help', 'Terms & Conditions', 'Privacy Policy'].map(l => (
              <Link key={l} to="/about-us" style={{ color: '#fff', textDecoration: 'none' }}>{l}</Link>
            ))}
          </div>
        </div>
      </div>

      {/* Official Chatbot Button matching live site icon-v2.png */}
      <a
        href="https://www.dosje.gov.in/"
        target="_blank"
        rel="noreferrer"
        style={{
          position: 'fixed',
          right: '2vw',
          bottom: 20,
          width: 76,
          height: 80,
          borderRadius: '50%',
          backgroundImage: `url(${ASSETS.chatbotIcon})`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: '50% 50%',
          backgroundSize: '100% 100%',
          cursor: 'pointer',
          zIndex: 10001,
          display: 'block',
          boxShadow: '0 4px 16px rgba(0,0,0,0.15)'
        }}
        title="Samavesh Sahayak Chatbot"
      />

    </footer>
  );
}

// ─── ROUTER APP MAIN ───────────────────────────────────────
export default function App() {
  return (
    <Router>
      <TopBar />
      <Header />
      <Navbar />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/samavesh" element={<SamaveshPage />} />
        <Route path="/about-us" element={<AboutUsPage />} />
        <Route path="/schemes" element={<SchemesPage />} />
        <Route path="/vacancies" element={<VacanciesPage />} />
        <Route path="/tenders" element={<TendersPage />} />
        <Route path="/contact-us" element={<ContactPage />} />
        <Route path="/nhaa" element={<NhaaPage />} />
      </Routes>

      <Footer />
    </Router>
  );
}
