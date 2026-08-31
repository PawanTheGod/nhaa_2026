import React from 'react';
import { ASSETS } from '../assets';

const Header = () => {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-2">
        <div className="flex items-center gap-4">

          {/* National Emblem */}
          <a href="/" className="shrink-0">
            <img
              src={ASSETS.nationalEmblem}
              alt="National Emblem of India"
              className="h-16 w-auto object-contain"
              onError={e => { e.target.src = '/ashoka_emblem.jpg'; }}
            />
          </a>

          {/* Ministry Name Block */}
          <div className="flex-1 border-l border-gray-200 pl-4">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="bg-[#FF6200] text-white text-[9px] font-bold px-2 py-0.5 rounded tracking-wider uppercase">
                BETA
              </span>
              <span className="text-[11px] text-gray-500">Government of India</span>
            </div>
            <h1 className="text-[18px] font-bold text-[#003087] leading-tight">
              Ministry of Social Justice &amp; Empowerment
            </h1>
            <p className="text-[13px] font-semibold text-[#FF6200]">
              Department of Social Justice &amp; Empowerment
            </p>
            <p className="text-[11px] text-gray-400 mt-0.5">
              सामाजिक न्याय और अधिकारिता विभाग
            </p>
          </div>

          {/* Samavesh Logo */}
          <div className="hidden md:block shrink-0">
            <img
              src={ASSETS.samavesh}
              alt="Samavesh Portal"
              className="h-14 w-auto object-contain"
              onError={e => e.target.style.display = 'none'}
            />
          </div>

          {/* Divider */}
          <div className="hidden lg:block h-14 w-px bg-gray-200 mx-2"></div>

          {/* India.gov.in */}
          <a href="https://india.gov.in/" target="_blank" rel="noreferrer" className="hidden lg:block shrink-0">
            <img
              src={ASSETS.indiaGov}
              alt="India.gov.in"
              className="h-10 w-auto object-contain"
              onError={e => e.target.style.display = 'none'}
            />
          </a>

          {/* Digital India */}
          <a href="https://digitalindia.gov.in/" target="_blank" rel="noreferrer" className="hidden lg:block shrink-0">
            <img
              src={ASSETS.digitalIndia}
              alt="Digital India"
              className="h-10 w-auto object-contain"
              onError={e => e.target.style.display = 'none'}
            />
          </a>
        </div>
      </div>

      {/* India Tricolor stripe */}
      <div className="flex h-1">
        <div className="flex-1 bg-[#FF9933]"></div>
        <div className="flex-1 bg-white border-y border-gray-200"></div>
        <div className="flex-1 bg-[#138808]"></div>
      </div>
    </header>
  );
};

export default Header;
