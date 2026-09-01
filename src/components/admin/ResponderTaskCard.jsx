import React from 'react';
import PropTypes from 'prop-types';
import RiskBadge from './RiskBadge';
import { ROLE_LABELS } from '../../utils/adminAuth';

const ACTION_LABELS = {
  police_intervention: 'Police Intervention',
  legal_aid: 'Free Legal Aid',
  medical_assistance: 'Medical Assistance',
  counselling: 'Counselling',
  emergency_escalation: 'Emergency Escalation',
  witness_protection: 'Witness Protection',
  fir_registration: 'FIR Registration',
  emergency_medical: 'Emergency Medical',
};

export default function ResponderTaskCard({ task, onMarkActioned }) {
  return (
    <article
      style={{
        background: task.actioned ? '#F8FAFC' : '#fff',
        border: `1px solid ${task.actioned ? '#E2E8F0' : '#CBD5E1'}`,
        borderRadius: 14,
        padding: '18px 20px',
        opacity: task.actioned ? 0.75 : 1,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, marginBottom: 12 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: '#0F172A' }}>
            Case NHAA-{task.case_id}
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: 12, color: '#64748B' }}>
            {task.district} · {new Date(task.created_at).toLocaleString('en-IN')}
          </p>
        </div>
        <RiskBadge tier={task.risk_tier} score={task.svi_score} />
      </div>

      <p style={{ margin: '0 0 12px', fontSize: 14, color: '#334155', lineHeight: 1.6 }}>
        {task.incident_description}
      </p>

      <p style={{ margin: '0 0 16px', fontSize: 13 }}>
        <strong style={{ color: '#0073E6' }}>Recommended: </strong>
        {ACTION_LABELS[task.recommended_action] || task.recommended_action}
      </p>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 12, color: '#64748B' }}>
          Assigned to: {ROLE_LABELS[task.responder_type] || task.responder_type}
        </span>
        {task.actioned ? (
          <span style={{ fontSize: 12, fontWeight: 700, color: '#065F46' }} aria-live="polite">Actioned</span>
        ) : (
          <button
            type="button"
            onClick={() => onMarkActioned(task.case_id)}
            aria-label={`Mark case NHAA-${task.case_id} as actioned`}
            style={{
              background: '#0073E6',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '8px 16px',
              fontSize: 13,
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Mark Actioned
          </button>
        )}
      </div>
    </article>
  );
}

ResponderTaskCard.propTypes = {
  task: PropTypes.shape({
    case_id: PropTypes.number.isRequired,
    responder_type: PropTypes.string.isRequired,
    svi_score: PropTypes.number,
    risk_tier: PropTypes.string,
    recommended_action: PropTypes.string,
    incident_description: PropTypes.string,
    created_at: PropTypes.string,
    district: PropTypes.string,
    actioned: PropTypes.bool,
  }).isRequired,
  onMarkActioned: PropTypes.func.isRequired,
};
