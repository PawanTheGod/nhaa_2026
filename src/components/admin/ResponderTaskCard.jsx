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

const CHANNEL_LABELS = {
  portal: 'Portal',
  chatbot: 'Chatbot',
  ivrs: 'IVRS',
  mobile_app: 'Mobile App',
};

export default function ResponderTaskCard({ task, onOpenCase }) {
  const assignedRole = task.role;

  return (
    <article
      style={{
        background: task.actioned ? '#F8FAFC' : '#fff',
        border: `1px solid ${task.actioned ? '#E2E8F0' : '#CBD5E1'}`,
        borderRadius: 14,
        padding: '18px 20px',
        opacity: task.actioned ? 0.85 : 1,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, marginBottom: 12 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: '#0F172A' }}>
            Case NHAA-{task.case_id}
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: 12, color: '#64748B' }}>
            {task.district}
            {task.state ? ` · ${task.state}` : ''} · {new Date(task.created_at).toLocaleString('en-IN')}
          </p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6 }}>
          <RiskBadge tier={task.risk_tier} score={task.svi_score} />
          {task.is_silent_signal && (
            <span style={{ fontSize: 10, fontWeight: 800, color: '#991B1B', background: '#FEE2E2', padding: '2px 8px', borderRadius: 999 }}>
              Silent SOS
            </span>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 12 }}>
        <span style={metaChip}>
          Channel: {CHANNEL_LABELS[task.channel_of_origin] || task.channel_of_origin || '—'}
        </span>
        {task.status && (
          <span style={metaChip}>Status: {task.status.replace(/_/g, ' ')}</span>
        )}
        {task.current_level != null && task.current_level !== '' && (
          <span style={{ ...metaChip, background: '#DBEAFE', color: '#1E3A8A', borderColor: '#93C5FD' }}>
            Level: {String(task.current_level).replace(/_/g, ' ')}
          </span>
        )}
        {task.actioned ? (
          <span style={{ ...metaChip, background: '#D1FAE5', color: '#065F46', borderColor: '#6EE7B7' }}>Actioned</span>
        ) : (
          <span style={{ ...metaChip, background: '#FEF3C7', color: '#92400E', borderColor: '#FCD34D' }}>Pending action</span>
        )}
      </div>

      <p style={{ margin: '0 0 12px', fontSize: 14, color: '#334155', lineHeight: 1.6 }}>
        {task.incident_description}
      </p>

      <p style={{ margin: '0 0 16px', fontSize: 13 }}>
        <strong style={{ color: '#0073E6' }}>Recommended: </strong>
        {ACTION_LABELS[task.recommended_action] || task.recommended_action}
      </p>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <span style={{ fontSize: 12, color: '#64748B' }}>
          Assigned to: {ROLE_LABELS[assignedRole] || assignedRole}
        </span>
        <button
          type="button"
          onClick={() => onOpenCase(task)}
          aria-label={`Open case file for NHAA-${task.case_id}`}
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
          Open Case File
        </button>
      </div>
    </article>
  );
}

const metaChip = {
  fontSize: 11,
  fontWeight: 600,
  color: '#334155',
  background: '#F1F5F9',
  border: '1px solid #E2E8F0',
  borderRadius: 999,
  padding: '3px 10px',
  textTransform: 'capitalize',
};

ResponderTaskCard.propTypes = {
  task: PropTypes.shape({
    case_id: PropTypes.number.isRequired,
    role: PropTypes.string.isRequired,
    svi_score: PropTypes.number,
    risk_tier: PropTypes.string,
    recommended_action: PropTypes.string,
    incident_description: PropTypes.string,
    created_at: PropTypes.string,
    district: PropTypes.string,
    state: PropTypes.string,
    status: PropTypes.string,
    channel_of_origin: PropTypes.string,
    is_silent_signal: PropTypes.bool,
    actioned: PropTypes.bool,
  }).isRequired,
  onOpenCase: PropTypes.func.isRequired,
};
