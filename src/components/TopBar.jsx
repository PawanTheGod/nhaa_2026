import React from 'react';
import { ASSETS } from '../assets';

const TopBar = () => {
  return (
    <div className="bg-[#003087] text-white text-xs">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between py-1.5">
        {/* Left: Skip links */}
        <div className="flex items-center gap-3">
          <a href="#content" className="hover:underline opacity-80 hover:opacity-100 transition-opacity">
            Skip to Main Content
          </a>
          <span className="opacity-40">|</span>
          <a href="https://india.gov.in/" target="_blank" rel="noreferrer"
            className="hover:underline opacity-80 hover:opacity-100 transition-opacity flex items-center gap-1">
            <img src={ASSETS.indianFlag} alt="India" className="h-3.5 w-auto" onError={e => e.target.style.display='none'} />
            Government of India
          </a>
          <span className="opacity-40">|</span>
          <a href="https://india.gov.in/" target="_blank" rel="noreferrer"
            className="hover:underline opacity-80 hover:opacity-100 transition-opacity">
            India.gov.in
          </a>
        </div>

        {/* Right: Accessibility + Admin */}
        <div className="flex items-center gap-3">
          {/* Text resize */}
          <div className="flex items-center gap-1.5 mr-1">
            <button className="opacity-60 text-[9px] hover:opacity-100 transition-opacity">A-</button>
            <button className="opacity-80 text-[11px] hover:opacity-100 transition-opacity">A</button>
            <button className="opacity-80 text-[13px] font-semibold hover:opacity-100 transition-opacity">A+</button>
          </div>
          <span className="opacity-40">|</span>
          {/* High Contrast */}
          <button className="hover:underline opacity-80 hover:opacity-100 transition-opacity text-[10px]">
            High Contrast
          </button>
          <span className="opacity-40">|</span>
          {/* Screen Reader */}
          <button className="hover:underline opacity-80 hover:opacity-100 transition-opacity text-[10px]">
            Screen Reader
          </button>
          <span className="opacity-40">|</span>
          {/* Admin Login */}
          <a
            href="#/admin/district"
            className="bg-[#003366] hover:bg-[#002244] text-white px-3 py-0.5 rounded text-[10px] font-semibold tracking-wide transition-colors"
          >
            Admin Portal
          </a>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
