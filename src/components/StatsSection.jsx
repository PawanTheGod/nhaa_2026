import React from 'react';
import { BarChart3, Users, IndianRupee, TrendingUp, ArrowUpRight } from 'lucide-react';

const stats = [
  {
    icon: IndianRupee,
    label: 'CUMULATIVE DISBURSEMENT',
    value: '₹67,977 Crore',
    sub: 'Scholarships for Scheduled Castes',
    color: '#FF6200',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    iconBg: 'bg-orange-100',
  },
  {
    icon: Users,
    label: 'BENEFICIARY COVERAGE',
    value: '19.82 Crore',
    sub: 'Cumulative across all schemes',
    color: '#003087',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    iconBg: 'bg-blue-100',
  },
  {
    icon: TrendingUp,
    label: 'RELEASE OF FUNDS, FY 2025–26',
    value: '₹8,731 Crore',
    sub: 'Provisional · 14.3% above previous year',
    color: '#138808',
    bg: 'bg-green-50',
    border: 'border-green-200',
    iconBg: 'bg-green-100',
  },
];

const StatsSection = () => {
  return (
    <section id="dashboard" className="bg-white border-b border-gray-100 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-1 h-6 bg-[#FF6200] rounded-full"></div>
            <h2 className="text-lg font-bold text-[#003087]">Department at a Glance</h2>
          </div>
          <a
            href="#"
            className="flex items-center gap-1.5 text-xs font-semibold text-[#003087] border border-[#003087] px-3 py-1.5 rounded-full hover:bg-[#003087] hover:text-white transition-all duration-200"
          >
            <BarChart3 size={13} />
            View Dashboard
          </a>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.label}
                className={`card-hover relative flex items-center gap-4 p-5 rounded-xl border ${stat.bg} ${stat.border} overflow-hidden`}
              >
                {/* Icon */}
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${stat.iconBg}`}>
                  <Icon size={22} style={{ color: stat.color }} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className="text-[9px] font-bold tracking-widest text-gray-400 uppercase mb-1">
                    {stat.label}
                  </p>
                  <p className="text-2xl font-extrabold leading-tight" style={{ color: stat.color }}>
                    {stat.value}
                  </p>
                  <p className="text-[11px] text-gray-500 mt-0.5 leading-tight">{stat.sub}</p>
                </div>

                {/* Corner arrow */}
                <ArrowUpRight size={16} className="absolute top-3 right-3 opacity-20" style={{ color: stat.color }} />

                {/* Decorative corner */}
                <div
                  className="absolute -bottom-4 -right-4 w-16 h-16 rounded-full opacity-10"
                  style={{ background: stat.color }}
                ></div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default StatsSection;
