import React from 'react';
import PropTypes from 'prop-types';

export default function StatsCard({ label, value, icon: Icon, trend, trendUp, sublabel }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="text-xs font-extrabold text-slate-500 uppercase" style={{ letterSpacing: '0.05em' }}>
            {label}
          </div>
          <div className="mt-1 text-3xl font-extrabold text-slate-900">{value}</div>
          {sublabel && <div className="mt-0.5 text-xs text-slate-500">{sublabel}</div>}
        </div>
        {Icon && (
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-50">
            <Icon className="h-5 w-5 text-slate-600" />
          </div>
        )}
      </div>
      {trend != null && (
        <div className="mt-3 flex items-center gap-1 text-xs">
          <span className={trendUp ? 'text-green-600' : 'text-red-600'}>
            {trendUp ? 'up' : 'down'} {Math.abs(trend)}%
          </span>
          <span className="text-slate-400">from last week</span>
        </div>
      )}
    </div>
  );
}

StatsCard.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  icon: PropTypes.elementType,
  trend: PropTypes.number,
  trendUp: PropTypes.bool,
  sublabel: PropTypes.string,
};