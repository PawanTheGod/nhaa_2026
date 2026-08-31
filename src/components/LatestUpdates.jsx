import React from 'react';
import { Bell, ArrowRight } from 'lucide-react';

const updates = [
  { type: 'Documents', title: 'Inviting Expression of Interest-cum-proposal from eligible organizations for setting up of District De-Addiction Centres under NAPDDR', date: 'Aug 2026', href: '#' },
  { type: 'Documents', title: 'Result of National Overseas Scholarship (NOS) for the Selection Year 2026-27', date: 'Aug 2026', href: '#' },
  { type: 'Updates', title: 'Pre Bid Meeting Tender id GEM/2026/B/7743923', date: 'Aug 2026', href: '#' },
  { type: 'Schemes', title: 'Dr. Ambedkar Medical Aid Scheme (Revised in 2026)', date: 'Jul 2026', href: '#' },
  { type: 'Vacancies', title: 'Extension of Application Submission Date for Financial Adviser (FA) Post at DAF and BJRNF', date: 'Jul 2026', href: '#' },
  { type: 'Documents', title: 'Annual Report 2025-26 (English)', date: 'Jun 2026', href: '#' },
  { type: 'Documents', title: 'Annual Report 2025-26 (Hindi)', date: 'Jun 2026', href: '#' },
  { type: 'Documents', title: 'Advertisement for new Regional Resource & Training Centres (RRTCs) under Sr Citizen Division', date: 'Jun 2026', href: '#' },
  { type: 'Documents', title: 'Result of National Overseas Scholarship (NOS) for SC etc. candidates for the Selection Year 2025-26 (2nd Round)', date: 'May 2026', href: '#' },
];

const typeColors = {
  Documents: 'bg-blue-100 text-blue-700',
  Updates: 'bg-orange-100 text-orange-700',
  Schemes: 'bg-green-100 text-green-700',
  Vacancies: 'bg-purple-100 text-purple-700',
};

const LatestUpdates = () => {
  return (
    <section className="bg-[#f8f9fa] border-b border-gray-200 py-0">
      {/* Section heading bar */}
      <div className="bg-[#003087] text-white px-5 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell size={14} className="text-[#FF6200]" />
          <h2 className="text-[13px] font-bold tracking-wide uppercase">Latest Updates</h2>
          <span className="pulse-dot w-2 h-2 bg-[#FF6200] rounded-full ml-1"></span>
        </div>
        <a href="#" className="text-xs text-blue-200 hover:text-white flex items-center gap-1 transition-colors">
          View All <ArrowRight size={12} />
        </a>
      </div>

      {/* Scrollable updates list */}
      <div className="divide-y divide-gray-100 max-h-72 overflow-y-auto">
        {updates.map((item, index) => (
          <a
            key={index}
            href={item.href}
            className="flex items-start gap-3 px-4 py-3 hover:bg-white transition-colors group"
          >
            <span className="mt-0.5 shrink-0">
              <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${typeColors[item.type] || 'bg-gray-100 text-gray-600'}`}>
                {item.type}
              </span>
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-[12px] text-gray-700 leading-snug group-hover:text-[#003087] transition-colors line-clamp-2">
                {item.title}
              </p>
              <span className="text-[10px] text-gray-400 mt-0.5 block">{item.date}</span>
            </div>
            <ArrowRight size={13} className="text-gray-300 group-hover:text-[#FF6200] shrink-0 mt-1 transition-colors" />
          </a>
        ))}
      </div>
    </section>
  );
};

export default LatestUpdates;
