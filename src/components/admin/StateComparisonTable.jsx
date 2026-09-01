import React, { useState } from 'react';
import PropTypes from 'prop-types';

export default function StateComparisonTable({ columns, data, defaultSort = 'cases', title }) {
  const [sortKey, setSortKey] = useState(defaultSort);
  const [sortDir, setSortDir] = useState('desc');

  const sorted = [...data].sort((a, b) => {
    const av = a[sortKey] ?? 0;
    const bv = b[sortKey] ?? 0;
    if (typeof av === 'string') {
      return sortDir === 'asc'
        ? av.localeCompare(bv)
        : bv.localeCompare(av);
    }
    return sortDir === 'asc' ? av - bv : bv - av;
  });

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const renderCell = (row, col) => {
    const val = row[col.key];
    if (col.render) return col.render(val, row);
    if (typeof val === 'number' && col.suffix) return `${val}${col.suffix}`;
    if (typeof val === 'number' && col.decimal) return val.toFixed(col.decimal);
    return val ?? '—';
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      {title && (
        <div className="border-b border-slate-200 px-5 py-3 text-sm font-bold text-slate-700">
          {title}
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="cursor-pointer border-b border-slate-200 px-4 py-2.5 text-left font-extrabold text-slate-600"
                  onClick={() => col.sortable !== false && toggleSort(col.key)}
                  style={{ userSelect: 'none', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}
                >
                  {col.label}
                  {sortKey === col.key && col.sortable !== false && (
                    <span style={{ marginLeft: 4 }}>{sortDir === 'asc' ? '▲' : '▼'}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-slate-25'}>
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-2 border-b border-slate-100">
                    {renderCell(row, col)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

StateComparisonTable.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      sortable: PropTypes.bool,
      suffix: PropTypes.string,
      decimal: PropTypes.number,
      render: PropTypes.func,
    })
  ).isRequired,
  data: PropTypes.array.isRequired,
  defaultSort: PropTypes.string,
  title: PropTypes.string,
};