import React from 'react';
import PropTypes from 'prop-types';

const TIER_COLORS = {
  low: { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' },
  moderate: { bg: '#FEF3C7', text: '#92400E', border: '#FCD34D' },
  high: { bg: '#FEE2E2', text: '#991B1B', border: '#FCA5A5' },
  critical: { bg: '#FECACA', text: '#7F1D1D', border: '#F87171' },
};

const TIER_LABELS = {
  low: 'Low',
  moderate: 'Moderate',
  high: 'High',
  critical: 'Critical',
};

export default function RiskBadge({ tier = 'low', score }) {
  const cfg = TIER_COLORS[tier] || TIER_COLORS.low;
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-extrabold"
      style={{ background: cfg.bg, color: cfg.text, borderColor: cfg.border }}
      title={`Risk Tier: ${TIER_LABELS[tier]}${score != null ? ` | SVI: ${score}` : ''}`}
    >
      {TIER_LABELS[tier]}
      {score != null && <span className="font-normal opacity-60">({score})</span>}
    </span>
  );
}

RiskBadge.propTypes = {
  tier: PropTypes.oneOf(['low', 'moderate', 'high', 'critical']),
  score: PropTypes.number,
};
