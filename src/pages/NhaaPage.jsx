import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ASSETS } from '../assets';

export default function NhaaPage() {
  const [activeModal, setActiveModal] = useState(null);
  const [trackId, setTrackId] = useState('');
  const [statusResult, setStatusResult] = useState(null);

  // Form handling
  const handleTrack = (e) => {
    e.preventDefault();
    setStatusResult({
      id: trackId,
      status: 'Under Investigation',
      stage: 'Step 3: Field verification & evidence collection by District Police Officer',
      updated: '30 Aug 2026',
      officer: 'SP Atrocities Cell, District HQ',
    });
  };

  return (
    <div style={{ background: '#F8FAFC', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Top Bar */}
      <div style={{ background: '#003366', color: '#fff', fontSize: 13, padding: '8px 0' }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <img src={ASSETS.indianFlag} alt="" style={{ height: 16 }} />
            <span>Government of India</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: 12 }}>
            <a href="#content" style={{ color: '#fff', textDecoration: 'none' }}>Skip to Main Content</a>
            <div style={{ display: 'flex', gap: 4 }}>
              <button style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: 11 }}>A-</button>
              <button style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: 12, fontWeight: 700 }}>A</button>
              <button style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: 13 }}>A+</button>
            </div>
            <span>English ▾</span>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header style={{ background: '#fff', padding: '14px 0', borderBottom: '1px solid #E2E8F0' }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
              <img src={ASSETS.nationalEmblem} alt="" style={{ height: 60 }} onError={e => e.target.src = '/ashoka_emblem.jpg'} />
              <div>
                <span style={{ background: '#FF9900', color: '#000', fontSize: 9, fontWeight: 800, padding: '1px 5px', borderRadius: 3 }}>BETA</span>
                <div style={{ fontSize: 11, color: '#64748B' }}>Government of India</div>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#334155' }}>Ministry of Social Justice &amp; Empowerment</div>
                <div style={{ fontSize: 17, fontWeight: 800, color: '#0F172A' }}>Department of Social Justice &amp; Empowerment</div>
              </div>
            </Link>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <img src={ASSETS.digitalIndia} alt="Digital India" style={{ height: 40 }} />
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <img src={ASSETS.samavesh} alt="SAMAVESH" style={{ height: 32 }} />
              <div style={{ fontSize: 11, fontWeight: 700, color: '#003366' }}>
                SAMAVESH
                <div style={{ fontSize: 9, color: '#64748B', fontWeight: 500 }}>Empowerment &amp; Harmony</div>
              </div>
            </div>
            <a href="https://nhapoa-admin.dosje.gov.in/login" target="_blank" rel="noreferrer" style={{ background: '#003366', color: '#fff', padding: '8px 18px', borderRadius: 8, fontSize: 13, fontWeight: 700, textDecoration: 'none' }}>
              Admin Login
            </a>
          </div>
        </div>
      </header>

      {/* Portal Body with Left Sidebar */}
      <div style={{ display: 'flex', flex: 1 }}>
        
        {/* Left Vertical Sidebar matching Screenshot */}
        <div style={{ width: 72, background: '#fff', borderRight: '1px solid #E2E8F0', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px 0', gap: 28 }}>
          {/* SAMBAL Badge */}
          <div style={{ width: 44, height: 44, borderRadius: '50%', background: '#EEF2FF', border: '1px solid #C7D7FD', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontSize: 9, fontWeight: 800, color: '#003366', textAlign: 'center' }}>
            <span>SAMBAL</span>
            <span style={{ fontSize: 7, color: '#F96302' }}>2021</span>
          </div>

          {/* Nav Icons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24, fontSize: 20, color: '#64748B', cursor: 'pointer' }}>
            <span title="Dashboard" style={{ color: '#003366' }}>🎛️</span>
            <span title="Register Grievance" onClick={() => setActiveModal('grievance')}>📝</span>
            <span title="Register Rescue" onClick={() => setActiveModal('rescue')}>🏃</span>
            <span title="Track Status" onClick={() => setActiveModal('track')}>🔍</span>
            <span title="Help">❓</span>
          </div>
        </div>

        {/* Center Main Content */}
        <div style={{ flex: 1, padding: '36px 48px' }}>
          
          {/* Toll-Free Helpline Banner */}
          <div style={{ background: 'linear-gradient(135deg, #003366 0%, #004B87 100%)', color: '#fff', padding: '16px 28px', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28, boxShadow: '0 4px 12px rgba(0,51,102,0.15)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{ fontSize: 24 }}>📞</span>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: '#FF9900', letterSpacing: 0.5 }}>NATIONAL HELPLINE AGAINST ATROCITIES (NHAA)</div>
                <div style={{ fontSize: 18, fontWeight: 900 }}>Toll-Free Helpline: <span style={{ color: '#FF9900' }}>14566</span> (24x7 Assistance)</div>
              </div>
            </div>
            <span style={{ background: 'rgba(255,255,255,0.15)', padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600 }}>
              PCR Act 1955 &amp; PoA Act 1989
            </span>
          </div>

          {/* Subtitle Banner */}
          <p style={{ textAlign: 'center', fontSize: 15, color: '#475569', marginBottom: 36, fontWeight: 500 }}>
            Submit, track, and resolve grievances through automated workflow. Transparent governance for all citizens.
          </p>

          {/* 3 Main Action Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 28, maxWidth: 1200, margin: '0 auto 56px' }}>
            
            {/* Card 1: Register Grievance */}
            <div
              style={{
                background: '#fff',
                borderRadius: 16,
                border: '1px solid #E2E8F0',
                padding: 32,
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 2px 10px rgba(0,0,0,0.03)',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ fontSize: 36, color: '#003366', marginBottom: 16 }}>📝</div>
              <h3 style={{ fontSize: 18, fontWeight: 800, color: '#0F172A', marginBottom: 8 }}>Register Grievance</h3>
              <p style={{ fontSize: 13, color: '#64748B', lineHeight: 1.6, flex: 1, marginBottom: 24 }}>
                Submit a new complaint regarding atrocities. You can register as a Victim, Informer, or on behalf of an NGO.
              </p>
              <button
                onClick={() => setActiveModal('grievance')}
                style={{ background: 'none', border: 'none', color: '#0073E6', fontSize: 14, fontWeight: 700, cursor: 'pointer', textAlign: 'left', padding: 0 }}
              >
                Start Registration ➔
              </button>
            </div>

            {/* Card 2: Register Rescue */}
            <div
              style={{
                background: '#fff',
                borderRadius: 16,
                border: '1px solid #E2E8F0',
                padding: 32,
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 2px 10px rgba(0,0,0,0.03)',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ fontSize: 36, color: '#003366', marginBottom: 16 }}>🧍‍♂️</div>
              <h3 style={{ fontSize: 18, fontWeight: 800, color: '#0F172A', marginBottom: 8 }}>Register Rescue</h3>
              <p style={{ fontSize: 13, color: '#64748B', lineHeight: 1.6, flex: 1, marginBottom: 24 }}>
                Quick distress report. Four short fields — Name, Mobile (OTP), Location and Problem. Routed straight to the responding Police officer.
              </p>
              <button
                onClick={() => setActiveModal('rescue')}
                style={{ background: 'none', border: 'none', color: '#0073E6', fontSize: 14, fontWeight: 700, cursor: 'pointer', textAlign: 'left', padding: 0 }}
              >
                Start Rescue ➔
              </button>
            </div>

            {/* Card 3: Track Status */}
            <div
              style={{
                background: '#fff',
                borderRadius: 16,
                border: '1px solid #E2E8F0',
                padding: 32,
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 2px 10px rgba(0,0,0,0.03)',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ fontSize: 36, color: '#003366', marginBottom: 16 }}>🔍</div>
              <h3 style={{ fontSize: 18, fontWeight: 800, color: '#0F172A', marginBottom: 8 }}>Track Status</h3>
              <p style={{ fontSize: 13, color: '#64748B', lineHeight: 1.6, flex: 1, marginBottom: 24 }}>
                Check the current progress, officer remarks, and closure status of an already registered grievance.
              </p>
              <button
                onClick={() => setActiveModal('track')}
                style={{ background: 'none', border: 'none', color: '#0073E6', fontSize: 14, fontWeight: 700, cursor: 'pointer', textAlign: 'left', padding: 0 }}
              >
                Track Application ➔
              </button>
            </div>

          </div>

          {/* Grievance Closure Process Workflow (Matching Screenshot) */}
          <div style={{ maxWidth: 1100, margin: '0 auto', textAlign: 'center' }}>
            <h2 style={{ fontSize: 22, fontWeight: 800, color: '#0F172A', marginBottom: 40 }}>
              Grievance Closure Process
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 16, position: 'relative' }}>
              {[
                { num: 1, title: 'Registration', desc: 'Submit incident details and required documentation securely.' },
                { num: 2, title: 'Review', desc: 'DM/DC Office reviews the grievance and documents.' },
                { num: 3, title: 'Investigation', desc: 'Field verification and evidence collection by authorities.' },
                { num: 4, title: 'Approval', desc: 'State Authority approves or returns for rework.' },
                { num: 5, title: 'Closure & Relief', desc: 'Case is closed and eligible financial relief is processed.' },
              ].map((step) => (
                <div key={step.num} style={{ background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #E2E8F0', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#EEF2FF', color: '#003366', fontWeight: 800, fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
                    {step.num}
                  </div>
                  <h4 style={{ fontSize: 14, fontWeight: 700, color: '#0F172A', margin: '0 0 6px' }}>{step.title}</h4>
                  <p style={{ fontSize: 12, color: '#64748B', lineHeight: 1.4, margin: 0 }}>{step.desc}</p>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

      {/* Interactive Modal Popups */}
      {activeModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 99999 }}>
          <div style={{ background: '#fff', borderRadius: 16, padding: 32, maxWidth: 500, width: '90%', position: 'relative' }}>
            <button onClick={() => { setActiveModal(null); setStatusResult(null); }} style={{ position: 'absolute', right: 16, top: 16, background: 'none', border: 'none', fontSize: 20, cursor: 'pointer' }}>✕</button>
            
            {activeModal === 'grievance' && (
              <div>
                <h3 style={{ fontSize: 20, fontWeight: 800, color: '#003366', marginBottom: 16 }}>Register New Grievance</h3>
                <form onSubmit={(e) => { e.preventDefault(); alert('Grievance registered successfully! Reference ID: NHAA-2026-8891'); setActiveModal(null); }}>
                  <div style={{ marginBottom: 12 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>COMPLAINANT ROLE</label>
                    <select style={{ width: '100%', padding: '9px 12px', fontSize: 13, border: '1px solid #CBD5E1', borderRadius: 6, marginTop: 4 }}>
                      <option>Victim</option>
                      <option>Informer / Witness</option>
                      <option>NGO Representative</option>
                    </select>
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>INCIDENT LOCATION (STATE / DISTRICT)</label>
                    <input required type="text" placeholder="State & District" style={{ width: '100%', padding: '9px 12px', fontSize: 13, border: '1px solid #CBD5E1', borderRadius: 6, marginTop: 4 }} />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>INCIDENT DETAILS</label>
                    <textarea required rows={3} placeholder="Describe the incident..." style={{ width: '100%', padding: '9px 12px', fontSize: 13, border: '1px solid #CBD5E1', borderRadius: 6, marginTop: 4 }}></textarea>
                  </div>
                  <button type="submit" style={{ width: '100%', background: '#003366', color: '#fff', border: 'none', padding: 12, borderRadius: 8, fontSize: 14, fontWeight: 700, cursor: 'pointer' }}>
                    Submit Complaint ➔
                  </button>
                </form>
              </div>
            )}

            {activeModal === 'rescue' && (
              <div>
                <h3 style={{ fontSize: 20, fontWeight: 800, color: '#DC2626', marginBottom: 16 }}>Quick Distress Rescue Report</h3>
                <form onSubmit={(e) => { e.preventDefault(); alert('Distress alert sent to Nearest Police Station! Dispatching Response Team.'); setActiveModal(null); }}>
                  <div style={{ marginBottom: 12 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>FULL NAME</label>
                    <input required type="text" placeholder="Your Name" style={{ width: '100%', padding: '9px 12px', fontSize: 13, border: '1px solid #CBD5E1', borderRadius: 6, marginTop: 4 }} />
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>MOBILE NUMBER (OTP VERIFIED)</label>
                    <input required type="tel" placeholder="10-digit mobile" style={{ width: '100%', padding: '9px 12px', fontSize: 13, border: '1px solid #CBD5E1', borderRadius: 6, marginTop: 4 }} />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>CURRENT GPS LOCATION / ADDRESS</label>
                    <input required type="text" placeholder="Location details..." style={{ width: '100%', padding: '9px 12px', fontSize: 13, border: '1px solid #CBD5E1', borderRadius: 6, marginTop: 4 }} />
                  </div>
                  <button type="submit" style={{ width: '100%', background: '#DC2626', color: '#fff', border: 'none', padding: 12, borderRadius: 8, fontSize: 14, fontWeight: 700, cursor: 'pointer' }}>
                    Send Emergency Rescue Alert 🚨
                  </button>
                </form>
              </div>
            )}

            {activeModal === 'track' && (
              <div>
                <h3 style={{ fontSize: 20, fontWeight: 800, color: '#003366', marginBottom: 16 }}>Track Grievance Status</h3>
                <form onSubmit={handleTrack} style={{ marginBottom: 20 }}>
                  <label style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>REFERENCE / APPLICATION NUMBER</label>
                  <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                    <input
                      required
                      type="text"
                      placeholder="e.g. NHAA-2026-8891"
                      value={trackId}
                      onChange={(e) => setTrackId(e.target.value)}
                      style={{ flex: 1, padding: '9px 12px', fontSize: 13, border: '1px solid #CBD5E1', borderRadius: 6 }}
                    />
                    <button type="submit" style={{ background: '#003366', color: '#fff', border: 'none', padding: '9px 16px', borderRadius: 6, fontWeight: 700, cursor: 'pointer' }}>
                      Search
                    </button>
                  </div>
                </form>

                {statusResult && (
                  <div style={{ background: '#F8FAFC', padding: 16, borderRadius: 8, border: '1px solid #E2E8F0' }}>
                    <div style={{ fontSize: 12, color: '#64748B' }}>Reference ID: <strong>{statusResult.id}</strong></div>
                    <div style={{ fontSize: 14, fontWeight: 800, color: '#0073E6', margin: '4px 0' }}>Status: {statusResult.status}</div>
                    <div style={{ fontSize: 12, color: '#334155', margin: '6px 0' }}>{statusResult.stage}</div>
                    <div style={{ fontSize: 11, color: '#94A3B8' }}>Assigned Officer: {statusResult.officer}</div>
                  </div>
                )}
              </div>
            )}

          </div>
        </div>
      )}

      {/* Dark Footer matching Screenshot */}
      <footer style={{ background: '#001F3F', color: '#fff', padding: '16px 0', fontSize: 12 }}>
        <div style={{ maxWidth: 1380, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            © 2026 - Copyright UX4G. All rights reserved. Powered by NeGD | MeitY Government of India®2026 UX4G
          </div>
          <div style={{ display: 'flex', gap: 20, color: 'rgba(255,255,255,0.8)' }}>
            <span style={{ cursor: 'pointer' }}>Terms &amp; Conditions</span>
            <span>|</span>
            <span style={{ cursor: 'pointer' }}>Privacy Policy</span>
            <span>|</span>
            <span style={{ cursor: 'pointer' }}>Feedback</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
