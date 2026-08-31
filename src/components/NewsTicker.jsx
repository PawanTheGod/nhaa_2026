import React from 'react';

const updates = [
  'Inviting Expression of Interest for setting up of District De-Addiction Centres under NAPDDR',
  'Result of National Overseas Scholarship (NOS) for Selection Year 2026-27',
  'Pre Bid Meeting Tender id GEM/2026/B/7743923',
  'Dr. Ambedkar Medical Aid Scheme (Revised in 2026)',
  'Annual Report 2025-26 (English) – Now Available',
  'Advertisement for new Regional Resource & Training Centres (RRTCs)',
  'Extension of Application Submission Date for Financial Adviser (FA) Post at DAIC',
];

const NewsTicker = () => {
  const repeated = [...updates, ...updates];

  return (
    <div className="bg-[#003087] text-white text-[11px] py-1.5 overflow-hidden">
      <div className="flex items-center max-w-7xl mx-auto px-4">
        {/* Label */}
        <div className="shrink-0 flex items-center gap-1.5 bg-[#FF6200] text-white text-[10px] font-bold px-3 py-0.5 rounded mr-4 uppercase tracking-wider">
          <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
          Latest
        </div>

        {/* Ticker */}
        <div className="ticker-container flex-1 relative">
          <div className="marquee-inner inline-flex gap-16">
            {repeated.map((item, i) => (
              <span key={i} className="cursor-pointer hover:text-[#FF9933] transition-colors">
                <span className="text-[#FF6200] mr-2">›</span>
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsTicker;
