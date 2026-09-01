import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import RiskBadge from './RiskBadge';
import NotificationLog from './NotificationLog';

const ACTION_LABELS = {
  police_intervention: 'Police Intervention',
  legal_aid: 'Free Legal Aid (DLSA)',
  medical_assistance: 'Medical Assistance',
  counselling: 'Counselling Referral',
  emergency_escalation: 'Emergency Escalation',
  witness_protection: 'Witness Protection',
  standard_follow_up: 'Standard Follow-up',
  information_only: 'Information Only',
  fir_registration: 'FIR Registration',
  emergency_medical: 'Emergency Medical',
};

export default function CaseDetailPanel({ caseData, onClose, onConfirmAction }) {
  const dialogRef = useRef(null);
  const closeBtnRef = useRef(null);

  useEffect(() => {
    if (!caseData) return undefined;
    closeBtnRef.current?.focus();

    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [caseData, onClose]);

  if (!caseData) return null;

  const id = caseData.id ?? caseData.case_id;
  const isCritical = caseData.risk_tier === 'critical';

  return (
    <>
      <button
        type="button"
        aria-label="Close case detail panel"
        onClick={onClose}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.45)',
          border: 'none',
          zIndex: 200,
          cursor: 'pointer',
        }}
      />
      <aside
        ref={dialogRef}
        role="dialog"
        aria-labelledby="case-detail-title"
        aria-describedby="case-detail-desc"
        aria-modal="true"
        tabIndex={-1}
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          width: 'min(480px, 100vw)',
          height: '100vh',
          background: '#fff',
          boxShadow: '-8px 0 32px rgba(0,0,0,0.12)',
          zIndex: 201,
          overflowY: 'auto',
          padding: '24px 28px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, marginBottom: 20 }}>
          <div>
            <h2 id="case-detail-title" style={{ margin: 0, fontSize: 20, fontWeight: 800, color: '#0F172A' }}>
              Case NHAA-{id}
            </h2>
            <p id="case-detail-desc" style={{ margin: '6px 0 0', fontSize: 13, color: '#475569' }}>
              {caseData.incident_description}
            </p>
          </div>
          <button
            ref={closeBtnRef}
            type="button"
            onClick={onClose}
            aria-label="Close case details"
            style={{
              background: '#F1F5F9',
              border: 'none',
              borderRadius: 8,
              width: 36,
              height: 36,
              fontSize: 18,
              cursor: 'pointer',
              flexShrink: 0,
            }}
          >
            ×
          </button>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 20 }}>
          <RiskBadge tier={caseData.risk_tier || 'low'} score={caseData.svi_score} />
          {caseData.is_silent_signal && (
            <span style={{ fontSize: 11, fontWeight: 800, color: '#991B1B', background: '#FEE2E2', padding: '4px 10px', borderRadius: 999 }}>
              Silent Distress Signal
            </span>
          )}
        </div>

        <section aria-labelledby="svi-heading" style={{ marginBottom: 20 }}>
          <h3 id="svi-heading" style={{ fontSize: 14, fontWeight: 800, color: '#0073E6', marginBottom: 8 }}>SVI Score</h3>
          <p style={{ margin: 0, fontSize: 32, fontWeight: 800, color: '#0F172A' }}>
            {caseData.svi_score != null ? Number(caseData.svi_score).toFixed(1) : '—'}
            <span style={{ fontSize: 14, fontWeight: 500, color: '#475569', marginLeft: 6 }}>/ 100</span>
          </p>
        </section>

        <section aria-labelledby="ai-explanation-heading" style={{ marginBottom: 20 }}>
          <h3 id="ai-explanation-heading" style={{ fontSize: 14, fontWeight: 800, color: '#0073E6', marginBottom: 8 }}>AI Explanation</h3>
          <p style={{ margin: 0, fontSize: 14, color: '#334155', lineHeight: 1.7, background: '#F8FAFC', padding: 14, borderRadius: 10, border: '1px solid #E2E8F0' }}>
            {caseData.explanation_text || 'No explanation available.'}
          </p>
        </section>

        <section aria-labelledby="recommended-action-heading" style={{ marginBottom: 20 }}>
          <h3 id="recommended-action-heading" style={{ fontSize: 14, fontWeight: 800, color: '#0073E6', marginBottom: 8 }}>Recommended Action</h3>
          <p style={{ margin: 0, fontSize: 15, fontWeight: 700, color: '#0F172A' }}>
            {ACTION_LABELS[caseData.recommended_action] || caseData.recommended_action || '—'}
          </p>
        </section>

        {caseData.flags && (
          <section aria-labelledby="risk-flags-heading" style={{ marginBottom: 20 }}>
            <h3 id="risk-flags-heading" style={{ fontSize: 14, fontWeight: 800, color: '#0073E6', marginBottom: 8 }}>Risk Flags</h3>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {Object.entries(caseData.flags)
                .filter(([, v]) => v)
                .map(([k]) => (
                  <li
                    key={k}
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      background: '#FEE2E2',
                      color: '#991B1B',
                      padding: '4px 10px',
                      borderRadius: 999,
                      textTransform: 'capitalize',
                    }}
                  >
                    {k.replace(/_/g, ' ')}
                  </li>
                ))}
            </ul>
          </section>
        )}

        <NotificationLog notifications={caseData.notifications || []} />

        {isCritical && (
          <button
            type="button"
            onClick={() => onConfirmAction?.(caseData)}
            aria-describedby="case-detail-desc"
            style={{
              width: '100%',
              marginTop: 24,
              background: '#B91C1C',
              color: '#fff',
              border: 'none',
              borderRadius: 10,
              padding: '14px 20px',
              fontSize: 14,
              fontWeight: 800,
              cursor: 'pointer',
            }}
          >
            Confirm Action (Human-in-the-Loop)
          </button>
        )}
      </aside>
    </>
  );
}

CaseDetailPanel.propTypes = {
  caseData: PropTypes.object,
  onClose: PropTypes.func.isRequired,
  onConfirmAction: PropTypes.func,
};
