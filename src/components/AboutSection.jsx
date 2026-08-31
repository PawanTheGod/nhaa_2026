import React from 'react';
import { ArrowRight } from 'lucide-react';
import { ASSETS } from '../assets';

const ministers = [
  {
    name: 'Dr. Virendra Kumar',
    title: 'Union Minister of Social Justice and Empowerment',
    img: ASSETS.drVirendraKumar,
  },
  {
    name: 'Shri Ramdas Athawale',
    title: 'Minister of State of Social Justice and Empowerment',
    img: ASSETS.ramdas,
  },
  {
    name: 'Shri B. L. Verma',
    title: 'Minister of State of Social Justice and Empowerment',
    img: ASSETS.blVerma,
  },
];

const AboutSection = () => {
  return (
    <section id="about" className="bg-white py-12 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-10">

          {/* About Text — 3 cols */}
          <div className="lg:col-span-3">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-1 h-6 bg-[#FF6200] rounded-full"></div>
              <h2 className="text-xl font-bold text-[#003087]">About Us</h2>
            </div>

            <p className="text-sm text-gray-600 leading-relaxed mb-4">
              The <strong>Department of Social Justice &amp; Empowerment (DoSJE)</strong> is mandated to ensure the empowerment and welfare of India's most vulnerable groups, including Scheduled Castes, OBCs, Senior Citizens, Transgender Persons, and victims of substance abuse.
            </p>
            <p className="text-sm text-gray-600 leading-relaxed mb-6">
              The Ministry of Social Justice &amp; Empowerment works to uplift India's most vulnerable communities through targeted initiatives, inclusive growth, and compassionate governance.
            </p>

            {/* CTA Links */}
            <div className="flex flex-wrap gap-3 mb-8">
              {[
                { label: 'Our Team', href: 'https://www.dosje.gov.in/mosje-directory/' },
                { label: 'Our Ministry', href: 'https://www.dosje.gov.in/about-us/' },
                { label: 'Our Reports', href: 'https://www.dosje.gov.in/annual-reports/' },
              ].map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-[#003087] border border-[#003087]/20 rounded-full hover:bg-[#003087] hover:text-white transition-all duration-200"
                >
                  {link.label}
                  <ArrowRight size={11} />
                </a>
              ))}
            </div>

            {/* User Personas with real images */}
            <div className="bg-gradient-to-br from-[#f0f5ff] to-[#e8f0fe] rounded-2xl p-5 border border-blue-100">
              <h3 className="text-sm font-bold text-[#003087] mb-1">Explore User Personas</h3>
              <p className="text-xs text-gray-500 mb-4">Choose your role to discover services made for you.</p>
              <div className="grid grid-cols-2 gap-3">
                <a
                  href="https://www.dosje.gov.in/home-page/for-government-official/"
                  target="_blank"
                  rel="noreferrer"
                  className="card-hover bg-white rounded-xl overflow-hidden border border-blue-100 hover:border-[#FF6200] group"
                >
                  <img
                    src={ASSETS.governmentOfficial}
                    alt="Government Official"
                    className="w-full h-28 object-cover"
                    onError={e => { e.target.src = ''; e.target.className = 'hidden'; }}
                  />
                  <div className="p-3">
                    <h4 className="text-xs font-bold text-[#003087] group-hover:text-[#FF6200] transition-colors">
                      Government Official
                    </h4>
                    <p className="text-[10px] text-gray-500 mt-0.5">Access administrative tools &amp; reports</p>
                  </div>
                </a>
                <a
                  href="https://www.dosje.gov.in/home-page/for-beneficiary/"
                  target="_blank"
                  rel="noreferrer"
                  className="card-hover bg-white rounded-xl overflow-hidden border border-blue-100 hover:border-[#FF6200] group"
                >
                  <img
                    src={ASSETS.beneficiary}
                    alt="Beneficiary"
                    className="w-full h-28 object-cover"
                    onError={e => { e.target.src = ''; e.target.className = 'hidden'; }}
                  />
                  <div className="p-3">
                    <h4 className="text-xs font-bold text-[#003087] group-hover:text-[#FF6200] transition-colors">
                      Beneficiary
                    </h4>
                    <p className="text-[10px] text-gray-500 mt-0.5">Find schemes &amp; services for you</p>
                  </div>
                </a>
              </div>
            </div>
          </div>

          {/* Ministers — 2 cols */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-1 h-6 bg-[#003087] rounded-full"></div>
              <h2 className="text-xl font-bold text-[#003087]">Leadership</h2>
            </div>

            <div className="space-y-4">
              {ministers.map((m) => (
                <div
                  key={m.name}
                  className="card-hover flex items-center gap-4 p-3 bg-gray-50 rounded-xl border border-gray-100"
                >
                  <img
                    src={m.img}
                    alt={m.name}
                    className="w-16 h-16 rounded-full object-cover object-top border-2 border-[#003087]/20 shrink-0 shadow"
                    onError={e => {
                      e.target.outerHTML = `<div class="w-16 h-16 rounded-full bg-[#003087] flex items-center justify-center text-white font-bold text-xl shrink-0 shadow">${m.name.split(' ').map(w => w[0]).join('').slice(0,2)}</div>`;
                    }}
                  />
                  <div>
                    <h3 className="text-sm font-bold text-gray-800">{m.name}</h3>
                    <p className="text-[11px] text-gray-500 leading-tight">{m.title}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Documents */}
            <div className="mt-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-1 h-5 bg-[#FF6200] rounded-full"></div>
                <h3 className="text-sm font-bold text-[#003087]">Recent Documents</h3>
              </div>
              <div className="space-y-2">
                {[
                  { title: 'Annual Report 2025-26 (English)', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/04/71441776233188.pdf' },
                  { title: 'Annual Report 2025-26 (Hindi)', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/04/93691776234871.pdf' },
                  { title: 'Annual Report 2024-25', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2025/11/86481744793621.pdf' },
                  { title: 'Annual Report 2023-24', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2025/11/32691723633555.pdf' },
                ].map((doc) => (
                  <a
                    key={doc.title}
                    href={doc.pdf}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-2.5 p-2.5 bg-white border border-gray-100 rounded-lg hover:border-[#FF6200] hover:bg-orange-50 transition-all group"
                  >
                    <div className="w-7 h-7 bg-red-100 rounded flex items-center justify-center shrink-0">
                      <svg className="w-4 h-4 text-red-600" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                      </svg>
                    </div>
                    <span className="text-[11px] text-gray-600 group-hover:text-[#003087] transition-colors flex-1">
                      {doc.title}
                    </span>
                    <span className="text-[10px] text-[#FF6200] font-semibold opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                      PDF
                    </span>
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
