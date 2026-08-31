import React from 'react';
import { ASSETS } from '../assets';

const LEADERSHIP = [
  { name: 'Dr. Virendra Kumar', title: 'Union Minister of Social Justice and Empowerment', img: ASSETS.drVirendraKumar, role: 'Cabinet Minister' },
  { name: 'Shri Ramdas Athawale', title: 'Minister of State of Social Justice and Empowerment', img: ASSETS.ramdas, role: 'Minister of State' },
  { name: 'Shri B. L. Verma', title: 'Minister of State of Social Justice and Empowerment', img: ASSETS.blVerma, role: 'Minister of State' },
];

export default function AboutUsPage() {
  return (
    <div style={{ background: '#F8FAFC', minHeight: '80vh', paddingBottom: 60 }}>
      {/* Header Banner */}
      <div style={{ background: '#0073E6', color: '#fff', padding: '36px 0' }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px' }}>
          <h1 style={{ fontSize: 30, fontWeight: 800, margin: 0 }}>About Us</h1>
          <p style={{ fontSize: 14, opacity: 0.9, marginTop: 6 }}>Department of Social Justice &amp; Empowerment — Government of India</p>
        </div>
      </div>

      <div style={{ maxWidth: 1380, margin: '0 auto', padding: '36px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 40 }}>
          {/* Mission & Vision */}
          <div>
            <div style={{ background: '#fff', padding: 28, borderRadius: 14, border: '1px solid #E2E8F0', marginBottom: 24 }}>
              <h2 style={{ fontSize: 20, fontWeight: 800, color: '#0073E6', marginBottom: 14 }}>Vision &amp; Mission</h2>
              <p style={{ fontSize: 14, color: '#334155', lineHeight: 1.8, marginBottom: 14 }}>
                The mandate of the Department of Social Justice and Empowerment is to work towards building an inclusive society where members of the target groups can lead active, secure and dignified lives with full growth and development.
              </p>
              <p style={{ fontSize: 14, color: '#334155', lineHeight: 1.8 }}>
                The target groups include Scheduled Castes (SCs), Other Backward Classes (OBCs), Senior Citizens, Victims of Substance Abuse, Transgender Persons, and De-notified, Nomadic and Semi-Nomadic Tribes.
              </p>
            </div>

            <div style={{ background: '#fff', padding: 28, borderRadius: 14, border: '1px solid #E2E8F0' }}>
              <h2 style={{ fontSize: 20, fontWeight: 800, color: '#0073E6', marginBottom: 14 }}>Key Objectives</h2>
              <ul style={{ paddingLeft: 20, fontSize: 14, color: '#334155', lineHeight: 1.8 }}>
                <li style={{ marginBottom: 10 }}>Educational empowerment through Pre-Matric, Post-Matric &amp; National Overseas Scholarships.</li>
                <li style={{ marginBottom: 10 }}>Economic development via concessional finance through National Finance Corporations (NSFDC, NBCFDC, NSKFDC).</li>
                <li style={{ marginBottom: 10 }}>Social defence &amp; rehabilitation via Nasha Mukt Bharat Abhiyaan and SMILE scheme.</li>
                <li style={{ marginBottom: 10 }}>Protection of Civil Rights and implementation of the SC/ST Prevention of Atrocities Act.</li>
              </ul>
            </div>
          </div>

          {/* Leadership */}
          <div>
            <div style={{ background: '#fff', padding: 28, borderRadius: 14, border: '1px solid #E2E8F0' }}>
              <h2 style={{ fontSize: 20, fontWeight: 800, color: '#0073E6', marginBottom: 20 }}>Leadership</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {LEADERSHIP.map((m) => (
                  <div key={m.name} style={{ display: 'flex', alignItems: 'center', gap: 16, padding: 12, borderRadius: 10, background: '#F8FAFC', border: '1px solid #F1F5F9' }}>
                    <img src={m.img} alt={m.name} style={{ width: 64, height: 64, borderRadius: '50%', objectFit: 'cover', border: '2px solid #0073E6' }} />
                    <div>
                      <span style={{ fontSize: 10, fontWeight: 800, color: '#F96302', uppercase: 'true' }}>{m.role}</span>
                      <h4 style={{ fontSize: 15, fontWeight: 700, color: '#0F172A', margin: '2px 0' }}>{m.name}</h4>
                      <p style={{ fontSize: 12, color: '#64748B', margin: 0 }}>{m.title}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
