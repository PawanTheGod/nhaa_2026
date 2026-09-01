import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

const THRESHOLD_ORANGE_MS = 24 * 60 * 60 * 1000;
const THRESHOLD_RED_MS = 6 * 60 * 60 * 1000;

const fmtRemaining = (ms) => {
  if (ms <= 0) return 'OVERDUE';
  const h = Math.floor(ms / (60 * 60 * 1000));
  const m = Math.floor((ms % (60 * 60 * 1000)) / (60 * 1000));
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
};

const computeColor = (remaining) => {
  if (remaining <= 0) return { bg: '#FEE2E2', text: '#7F1D1D', border: '#F87171' };
  if (remaining < THRESHOLD_RED_MS) return { bg: '#FEE2E2', text: '#991B1B', border: '#FCA5A5' };
  if (remaining < THRESHOLD_ORANGE_MS) return { bg: '#FEF3C7', text: '#92400E', border: '#FCD34D' };
  return { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' };
};

export default function SLACountdown({ dueDate, deadlineType = 'Resolution' }) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 60000);
    return () => clearInterval(timer);
  }, []);

  const due = new Date(dueDate).getTime();
  const remaining = due - now;
  const color = computeColor(remaining);

  return (
    <div
      className="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-bold"
      style={{ background: color.bg, color: color.text, borderColor: color.border }}
      title={`${deadlineType} deadline: ${new Date(due).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: color.text, opacity: 0.5 }} />
      {fmtRemaining(remaining)}
    </div>
  );
}

SLACountdown.propTypes = {
  dueDate: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  deadlineType: PropTypes.string,
};