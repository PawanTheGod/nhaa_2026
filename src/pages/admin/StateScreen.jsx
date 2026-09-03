import React, { useEffect, useState } from 'react';
import {
  ScaleIcon, CheckCircleIcon, AlertTriangleIcon,
  ClockIcon, TrendingUpIcon, BarChart3Icon,
} from 'lucide-react';
import { stateMockData } from '../../data/stateMockData';
import { getCaseStats, getCaseTrend, getDistrictComparison } from '../../services/api';
import TrendChart from '../../components/admin/TrendChart';
import StateComparisonTable from '../../components/admin/StateComparisonTable';
import { useLang } from '../../i18n/LangContext';
import { ADMIN_TRANSLATIONS } from '../../i18n/adminTranslations';

export default function StateScreen() {
  const [stats, setStats] = useState(null);
  const [trend, setTrend] = useState([]);
  const [districtTable, setDistrictTable] = useState([]);
  const [useMock, setUseMock] = useState(false);
  const [selectedState] = useState('Delhi');
  const { lang } = useLang();
  const at = ADMIN_TRANSLATIONS[lang] || ADMIN_TRANSLATIONS.en;

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        const [statsRes, trendRes, districtRes] = await Promise.all([
          getCaseStats({ role: 'state', state: selectedState }),
          getCaseTrend({ role: 'state', state: selectedState, weeks: 4 }),
          getDistrictComparison({ role: 'state', state: selectedState }),
        ]);
        if (!cancelled) {
          setStats(statsRes);
          setTrend(trendRes);
          setDistrictTable(districtRes);
          setUseMock(false);
        }
      } catch {
        if (!cancelled) {
          setStats(stateMockData.stats);
          setTrend(stateMockData.trend);
          setDistrictTable(stateMockData.districtTable);
          setUseMock(true);
        }
      }
    };

    fetchData();
    return () => { cancelled = true; };
  }, [selectedState]);

  const tierColumns = [
    { key: 'district', label: 'District' },
    { key: 'cases', label: 'Total Cases' },
    { key: 'resolved', label: 'Resolved' },
    { key: 'resolutionRate', label: '% Resolution', suffix: '%', decimal: 1 },
    { key: 'highRisk', label: 'High Risk' },
  ];

  if (!stats) return null;

  const statCards = [
    { label: 'Total Cases', value: stats.total_cases?.toLocaleString('en-IN') || stats.totalCases?.toLocaleString('en-IN') || 0, Icon: BarChart3Icon },
    { label: 'Low Risk', value: stats.tier_breakdown?.low?.toLocaleString('en-IN') || stats.tierBreakdown?.low?.toLocaleString('en-IN') || 0, Icon: CheckCircleIcon, color: 'text-green-600' },
    { label: 'Moderate', value: stats.tier_breakdown?.moderate?.toLocaleString('en-IN') || stats.tierBreakdown?.moderate?.toLocaleString('en-IN') || 0, Icon: ClockIcon, color: 'text-amber-600' },
    { label: 'High Risk', value: stats.tier_breakdown?.high?.toLocaleString('en-IN') || stats.tierBreakdown?.high?.toLocaleString('en-IN') || 0, Icon: AlertTriangleIcon, color: 'text-orange-600' },
    { label: 'Critical', value: stats.tier_breakdown?.critical?.toLocaleString('en-IN') || stats.tierBreakdown?.critical?.toLocaleString('en-IN') || 0, Icon: ScaleIcon, color: 'text-red-700' },
    { label: 'Resolution Rate', value: `${stats.resolution_rate ?? stats.resolutionRate ?? 0}%`, Icon: TrendingUpIcon, color: 'text-blue-600' },
  ];

  const displayTrend = trend.length > 0 ? trend : stateMockData.trend;
  const displayDistricts = districtTable.length > 0 ? districtTable : stateMockData.districtTable;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800, color: '#0F172A', margin: 0 }}>{selectedState} {at.state} {at.dashboardTitle.replace('NHAA – ', '').replace('अधिकारी ', '').replace('அதிகாரி ', '').replace('అధికారి ', '').replace('কর্মকর্তা ', '').replace('अधिकारी ', '') || 'Dashboard'}</h2>
          <p style={{ fontSize: 13, color: '#64748B', marginTop: 4 }}>
            {useMock ? '(Mock data -- API unreachable)' : '(Live data from Case API)'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <label style={{ fontSize: 12, color: '#64748B' }}>Select Period:</label>
          <select style={{ fontSize: 13, padding: '6px 10px', borderRadius: 6, border: '1px solid #CBD5E1', background: 'white' }}>
            <option>Last 30 days</option>
            <option>Last 7 days</option>
            <option>This quarter</option>
          </select>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
        {statCards.map((card) => (
          <div key={card.label} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs font-extrabold text-slate-500 uppercase" style={{ letterSpacing: '0.05em' }}>{card.label}</div>
                <div className={`mt-1 text-2xl font-extrabold ${card.color || 'text-slate-900'}`}>{card.value}</div>
              </div>
              {card.Icon && (
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-50">
                  <card.Icon className={`h-5 w-5 ${card.color || 'text-slate-600'}`} />
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <TrendChart data={displayTrend} dataKey="cases" type="line" height={220} title="Case Volume (weekly)" />
        <TrendChart data={displayTrend} dataKey="sviAvg" type="bar" height={220} title="Avg SVI Score (weekly)" />
      </div>

      <StateComparisonTable
        title={`${selectedState} -- District Comparison`}
        columns={tierColumns}
        data={displayDistricts}
        defaultSort="cases"
      />

      <div className="text-xs text-slate-400">
        Data shape contract (Step 14): State stats expects -- total cases, tier breakdown, resolution rate, weekly trend[{displayTrend.length} points].
        District row expects -- district name, cases, resolved, resolution rate, high-risk count.
      </div>
    </div>
  );
}
