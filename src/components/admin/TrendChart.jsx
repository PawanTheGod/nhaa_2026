import React from 'react';
import PropTypes from 'prop-types';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const COLORS = {
  cases: '#0052CC',
  sviAvg: '#F96302',
  critical: '#DC2626',
  low: '#10B981',
  moderate: '#F59E0B',
  high: '#EF4444',
  critical_tier: '#7F1D1D',
};

export default function TrendChart({ data, dataKey = 'cases', type = 'line', height = 220, title }) {
  const strokeColor = COLORS[dataKey] || COLORS.cases;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      {title && <div className="mb-3 text-sm font-bold text-slate-700">{title}</div>}
      <ResponsiveContainer width="100%" height={height}>
        {type === 'bar' ? (
          <BarChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="week" stroke="#94A3B8" fontSize={11} />
            <YAxis stroke="#94A3B8" fontSize={11} />
            <Tooltip
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #E2E8F0' }}
              labelStyle={{ fontSize: 12 }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey={dataKey} fill={strokeColor} name={dataKey} radius={[4, 4, 0, 0]} />
          </BarChart>
        ) : (
          <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="week" stroke="#94A3B8" fontSize={11} />
            <YAxis stroke="#94A3B8" fontSize={11} />
            <Tooltip
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #E2E8F0' }}
              labelStyle={{ fontSize: 12 }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={strokeColor}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 6 }}
              name={dataKey}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

TrendChart.propTypes = {
  data: PropTypes.array.isRequired,
  dataKey: PropTypes.string,
  type: PropTypes.oneOf(['line', 'bar']),
  height: PropTypes.number,
  title: PropTypes.string,
};