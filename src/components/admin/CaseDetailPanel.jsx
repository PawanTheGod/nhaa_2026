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

const CHANNEL_LABELS = {
  portal: 'Portal',
  chatbot: 'Chatbot',
  ivrs: 'IVRS',
  mobile_app: 'Mobile App',
};

/**
 * Normalise Aatmman/Vedika nested flags OR legacy flat booleans.
 * Nested: { trauma: { present, confidence, signals[] }, ... }
 */
function normalizeFlags(flags) {
  if (!flags || typeof flags !== 'object') return [];
  return Object.entries(flags)
    .map(([name, value]) => {
      if (value && typeof value === 'object' && 'present' in value) {
        return {
          name,
          present: Boolean(value.present),
          confidence: typeof value.confidence === 'number' ? value.confidence : null,
          signals: Array.isArray(value.signals) ? value.signals : [],
        };
      }
      return {
        name,
        present: Boolean(value),
        confidence: null,
        signals: [],
      };
    })
    .filter((f) => f.present);
}

export default function CaseDetailPanel({
  caseData,
  onClose,
  onConfirmAction,
  onMarkActioned,
  mode = 'operator',
}) {
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
  const activeFlags = normalizeFlags(caseData.flags);
  const isResponder = mode === 'responder';
  const alreadyActioned = Boolean(caseData.actioned);

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

        <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 20, flexWrap: 'wrap' }}>
          <RiskBadge tier={caseData.risk_tier || 'low'} score={caseData.svi_score} />
          {caseData.is_silent_signal && (
            <span style={{ fontSize: 11, fontWeight: 800, color: '#991B1B', background: '#FEE2E2', padding: '4px 10px', borderRadius: 999 }}>
              Silent Distress Signal
            </span>
          )}
          {caseData.channel_of_origin && (
            <span style={{ fontSize: 11, fontWeight: 700, color: '#334155', background: '#F1F5F9', padding: '4px 10px', borderRadius: 999 }}>
              {CHANNEL_LABELS[caseData.channel_of_origin] || caseData.channel_of_origin}
            </span>
          )}
          {caseData.status && (
            <span style={{ fontSize: 11, fontWeight: 700, color: '#334155', background: '#F1F5F9', padding: '4px 10px', borderRadius: 999, textTransform: 'capitalize' }}>
              {String(caseData.status).replace(/_/g, ' ')}
            </span>
          )}
        </div>

        {(caseData.district || caseData.state) && (
          <p style={{ margin: '0 0 16px', fontSize: 13, color: '#475569' }}>
            Location: {[caseData.district, caseData.state].filter(Boolean).join(', ')}
            {caseData.created_at ? ` · Logged ${new Date(caseData.created_at).toLocaleString('en-IN')}` : ''}
          </p>
        )}

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
            {activeFlags.length === 0 ? (
              <p style={{ margin: 0, fontSize: 13, color: '#64748B' }}>No active risk flags.</p>
            ) : (
              <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
                {activeFlags.map((flag) => (
                  <li
                    key={flag.name}
                    style={{
                      background: '#FEF2F2',
                      border: '1px solid #FECACA',
                      borderRadius: 10,
                      padding: '10px 12px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <span style={{ fontSize: 13, fontWeight: 800, color: '#991B1B', textTransform: 'capitalize' }}>
                        {flag.name.replace(/_/g, ' ')}
                      </span>
                      {flag.confidence != null && (
                        <span
                          style={{ fontSize: 12, fontWeight: 700, color: '#7F1D1D' }}
                          aria-label={`Confidence ${(flag.confidence * 100).toFixed(0)} percent`}
                        >
                          {(flag.confidence * 100).toFixed(0)}% confidence
                        </span>
                      )}
                    </div>
                    {flag.signals.length > 0 && (
                      <ul style={{ margin: '6px 0 0', paddingLeft: 18, color: '#7F1D1D', fontSize: 12, lineHeight: 1.5 }}>
                        {flag.signals.map((signal) => (
                          <li key={signal}>{signal}</li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        {Array.isArray(caseData.officer_checklist) && caseData.officer_checklist.length > 0 && (
          <section aria-labelledby="checklist-heading" style={{ marginBottom: 20 }}>
            <h3 id="checklist-heading" style={{ fontSize: 14, fontWeight: 800, color: '#0073E6', marginBottom: 8 }}>
              {isResponder ? 'Your action checklist' : 'Suggested checklist'}
            </h3>
            <ol style={{ margin: 0, paddingLeft: 20, color: '#334155', fontSize: 13, lineHeight: 1.7 }}>
              {caseData.officer_checklist.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ol>
          </section>
        )}

        <NotificationLog notifications={caseData.notifications || []} />

        {isResponder ? (
          alreadyActioned ? (
            <p
              role="status"
              aria-live="polite"
              style={{
                width: '100%',
                marginTop: 24,
                background: '#D1FAE5',
                color: '#065F46',
                borderRadius: 10,
                padding: '14px 20px',
                fontSize: 14,
                fontWeight: 800,
                textAlign: 'center',
              }}
            >
              Marked as actioned
            </p>
          ) : (
            <button
              type="button"
              onClick={() => onMarkActioned?.(caseData)}
              aria-describedby="case-detail-desc"
              style={{
                width: '100%',
                marginTop: 24,
                background: '#0073E6',
                color: '#fff',
                border: 'none',
                borderRadius: 10,
                padding: '14px 20px',
                fontSize: 14,
                fontWeight: 800,
                cursor: 'pointer',
              }}
            >
              Mark Actioned (after review)
            </button>
          )
        ) : (
          isCritical && (
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
          )
        )}
      </aside>
    </>
  );
}

CaseDetailPanel.propTypes = {
  caseData: PropTypes.object,
  onClose: PropTypes.func.isRequired,
  onConfirmAction: PropTypes.func,
  onMarkActioned: PropTypes.func,
  mode: PropTypes.oneOf(['operator', 'responder']),
};
