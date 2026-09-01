import React from 'react';
import PropTypes from 'prop-types';
import { ROLE_LABELS } from '../../utils/adminAuth';

export default function NotificationLog({ notifications }) {
  if (!notifications?.length) {
    return (
      <section>
        <h3 style={{ fontSize: 14, fontWeight: 800, color: '#0073E6', marginBottom: 8 }}>Notifications</h3>
        <p style={{ margin: 0, fontSize: 13, color: '#64748B' }}>No agencies notified yet.</p>
      </section>
    );
  }

  return (
    <section>
      <h3 style={{ fontSize: 14, fontWeight: 800, color: '#0073E6', marginBottom: 8 }}>Notifications</h3>
      <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {notifications.map((n, i) => (
          <li
            key={`${n.recipient_role}-${n.sent_at}-${i}`}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: 12,
              padding: '10px 12px',
              background: '#F8FAFC',
              borderRadius: 8,
              border: '1px solid #E2E8F0',
              fontSize: 13,
            }}
          >
            <span style={{ fontWeight: 600, color: '#0F172A' }}>
              {ROLE_LABELS[n.recipient_role] || n.recipient_role}
            </span>
            <span style={{ color: '#64748B', fontSize: 12 }}>
              {n.channel?.toUpperCase()} · {new Date(n.sent_at).toLocaleString('en-IN')}
            </span>
            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                textTransform: 'uppercase',
                color: n.status === 'sent' || n.status === 'delivered' ? '#065F46' : '#92400E',
              }}
            >
              {n.status}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

NotificationLog.propTypes = {
  notifications: PropTypes.arrayOf(PropTypes.object),
};
