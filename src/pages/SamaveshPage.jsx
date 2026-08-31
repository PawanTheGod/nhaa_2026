import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ASSETS } from '../assets';

const PORTALS = [
  {
    code: 'SCW',
    title: 'Senior Citizens Welfare',
    logo: ASSETS.nationalEmblem,
    url: 'https://seniorcitizen-admin.dosje.gov.in/',
  },
  {
    code: 'SMILE - Transgender',
    title: 'National Portal for Transgender Persons',
    logo: ASSETS.samavesh,
    url: 'https://tg-admin.dosje.gov.in/',
  },
  {
    code: 'NOS',
    title: 'National Overseas Scholarship',
    logo: ASSETS.favicon,
    url: 'https://nos-admin.dosje.gov.in/',
  },
  {
    code: 'NMBA',
    title: 'Nasha Mukt Bharat Abhiyaan',
    logo: ASSETS.favicon,
    url: 'https://nashamukt-admin.dosje.gov.in/',
  },
  {
    code: 'NHAA',
    title: 'National Helpline Against Atrocities',
    logo: ASSETS.favicon,
    url: '/nhaa',
    isInternal: true,
  },
];

export default function SamaveshPage() {
  return (
    <div style={{ background: '#FFF9F5', minHeight: '85vh', paddingBottom: 80 }}>
      {/* Breadcrumb */}
      <div style={{ background: '#fff', borderBottom: '1px solid #E5E7EB', padding: '12px 0' }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', fontSize: 13, color: '#6B7280' }}>
          <Link to="/" style={{ color: '#4B5563', textDecoration: 'none' }}>Home</Link>
          <span style={{ margin: '0 8px' }}>/</span>
          <span style={{ color: '#111827', fontWeight: 600 }}>Samavesh Citizen Portals</span>
        </div>
      </div>

      {/* Main Container */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '48px 24px', textAlign: 'center' }}>
        {/* Subtitle */}
        <p style={{ fontSize: 14, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>
          SAMAVESH - Citizen Login
        </p>

        {/* Heading */}
        <h1 style={{ fontSize: 32, fontWeight: 800, color: '#1B8738', margin: '0 0 40px' }}>
          Choose a portal to visit
        </h1>

        {/* Cards Grid matching Screenshot 1 & 2 */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20, justifyContent: 'center' }}>
          {PORTALS.map((p) => {
            const CardComponent = p.isInternal ? Link : 'a';
            const linkProps = p.isInternal ? { to: p.url } : { href: p.url, target: '_blank', rel: 'noreferrer' };

            return (
              <CardComponent
                key={p.code}
                {...linkProps}
                style={{
                  background: '#fff',
                  border: '1px solid #FF6200',
                  borderRadius: 16,
                  padding: '20px 24px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  textDecoration: 'none',
                  boxShadow: '0 2px 8px rgba(255, 98, 0, 0.06)',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
              >
                {/* Logo icon */}
                <div style={{ width: 44, height: 44, borderRadius: '50%', background: '#F8FAFC', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #E2E8F0', flexShrink: 0 }}>
                  <img src={p.logo} alt="" style={{ width: 30, height: 30, objectFit: 'contain' }} onError={(e) => { e.target.style.display = 'none'; }} />
                </div>

                {/* Text */}
                <div>
                  <h4 style={{ fontSize: 15, fontWeight: 800, color: '#FF6200', margin: '0 0 2px' }}>
                    {p.code}
                  </h4>
                  <p style={{ fontSize: 13, fontWeight: 600, color: '#334155', margin: 0, lineHeight: 1.3 }}>
                    {p.title}
                  </p>
                </div>
              </CardComponent>
            );
          })}
        </div>
      </div>
    </div>
  );
}
