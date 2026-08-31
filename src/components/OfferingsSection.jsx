import React, { useState } from 'react';
import { ArrowRight, FileText, Briefcase, Receipt } from 'lucide-react';
import { ASSETS } from '../assets';

const schemes = [
  { title: 'Pradhan Mantri Anusuchit Jaati Abhyuday Yojna (PM-AJAY)', category: 'Scheduled Castes', href: 'https://www.dosje.gov.in/schemes-and-services/pradhan-mantri-anusuchit-jaati-abhyuday-yojna-pm-ajay/' },
  { title: 'PM Young Achievers Scholarship Award Scheme for Vibrant India for OBCs and Others (PM-YASASVI)', category: 'OBC', href: 'https://www.dosje.gov.in/schemes-and-services/pm-young-achievers-scholarship-award-scheme-for-vibrant-india-for-obcs-and-others-pm-yasasvi/' },
  { title: 'Centrally Sponsored Scheme for implementation of the Protection of Civil Rights Act, 1955 and SC/ST Prevention of Atrocities Act, 1989', category: 'Civil Rights', href: 'https://www.dosje.gov.in/schemes-and-services/centrally-sponsored-scheme-for-implementation-of-the-protection-of-civil-rights-act-1955-and-the-scheduled-castes-and-the-scheduled-tribes-prevention-of-atrocities-act-1989/' },
  { title: 'Top Class Education in College for OBC, EBC and DNT Students', category: 'Education', href: 'https://www.dosje.gov.in/schemes-and-services/top-class-education-in-colllege-for-obc-ebc-and-dnt-students/' },
  { title: 'Pre-Matric Scholarships Scheme for Scheduled Castes & Others', category: 'Education', href: 'https://www.dosje.gov.in/schemes-and-services/pre-matric-scholarships-scheme-for-scheduled-castes-others/' },
  { title: 'Post-Matric Scholarship for SC Students', category: 'Education', href: 'https://www.dosje.gov.in/schemes-and-services/post-matric-scholarship-for-sc-students/' },
];

const vacancies = [
  { org: 'Dr. Ambedkar International Centre (DAIC)', title: 'Short Term Internship Programme at DAIC (September 2026)', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/08/Internship-Advertisment-September.pdf', href: 'https://www.dosje.gov.in/vacancies/short-term-internship-programme-at-daic-september-2026/' },
  { org: 'Dr. Ambedkar International Centre (DAIC)', title: 'Vacancy Circular for the post of Financial Advisor', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/08/FA-31-07-2026.pdf', href: 'https://www.dosje.gov.in/vacancies/vacancy-circular-for-the-post-of-financial-advisor/' },
  { org: 'NBCFDC', title: 'Recruitment Notification for Deputy General Manager (Finance) – E-5 Level', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/01/advertisement-E-5-10.12.2025_1.pdf', href: 'https://www.dosje.gov.in/vacancies/recruitment-notification-for-deputy-general-manager-finance-e-5-level/' },
  { org: 'National Institute of Social Defence (NISD)', title: 'Filling up the post of Junior Research Officer, Technical Assistant & Stenographer Grade-III on deputation basis', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2025/11/Application_for_the_post_of_JRO_TA_Steno_NISD.pdf', href: 'https://www.dosje.gov.in/vacancies/filling-up-the-post-of-junior-research-officer-technical-assistant-stenographer-grade-iii-in-national-institute-of-social-defence-nisd-on-deputation-basis/' },
  { org: 'National Institute of Social Defence (NISD)', title: 'Filling up the post of Deputy Director (Trg.) on deputation basis in NISD', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2025/11/Application_for_the_post_of_DD_TRG.pdf', href: 'https://www.dosje.gov.in/vacancies/filling-up-the-post-of-deputy-director-trg-on-deputation-basis-in-national-institute-of-social-defence-new-delhi-under-ministry-of-social-justice-empowerment-government-of-india/' },
];

const tenders = [
  { org: 'DAIC', title: 'Notice Inviting Expression of Interest', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/07/EOI.pdf' },
  { org: 'DAF', title: 'Invitation for Bids for providing the Manpower Outsourcing Services to office of Dr. Ambedkar Foundation through GeM', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/06/GeM-Bidding-9507171.pdf' },
  { org: 'NCSK', title: 'Hindi Pakhwada 14 September to 28 September 2024', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/05/Hindi-Pakhwada-14-September-to-28-September-2024.pdf' },
  { org: 'NCSK', title: 'Tender for Security Guards for parking arrangement in Lok Nayak Bhawan, Khan Market, New Delhi', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/05/Tender-for-Security-Guards-for-parking-arrangement-in-Lok-Nayak-Bhawan-Khan-Market-New-Delhi.pdf' },
  { org: 'NBCFDC', title: 'Proposals are invited for Annual Personal Contract of IT Associates', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/02/tender-document-55-0-1.pdf' },
];

const tabs = [
  { id: 'schemes', label: 'Schemes & Services', icon: FileText },
  { id: 'vacancies', label: 'Vacancies', icon: Briefcase },
  { id: 'tenders', label: 'Tenders', icon: Receipt },
];

const OfferingsSection = () => {
  const [active, setActive] = useState('schemes');

  const renderItems = () => {
    if (active === 'schemes') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* Schemes image */}
          <div className="md:col-span-2 mb-2">
            <img
              decoding="async"
              src={ASSETS.schemesThumbnail}
              alt="Schemes & Services"
              className="w-full h-36 object-cover rounded-xl shadow-sm"
              onError={e => e.target.style.display = 'none'}
            />
          </div>
          {schemes.map((item) => (
            <a
              key={item.title}
              href={item.href}
              target="_blank"
              rel="noreferrer"
              className="card-hover flex items-start gap-3 p-4 bg-white border border-gray-100 rounded-xl hover:border-[#FF6200] group"
            >
              <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center shrink-0 mt-0.5 group-hover:bg-[#003087] transition-colors">
                <FileText size={15} className="text-[#003087] group-hover:text-white transition-colors" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-gray-800 group-hover:text-[#003087] leading-snug transition-colors line-clamp-2">
                  {item.title}
                </p>
                <span className="inline-block text-[9px] font-semibold text-[#FF6200] bg-orange-50 px-2 py-0.5 rounded-full mt-1">
                  {item.category}
                </span>
              </div>
              <span className="text-[10px] text-[#FF6200] font-semibold shrink-0 opacity-0 group-hover:opacity-100 transition-opacity mt-1">
                Know More
              </span>
            </a>
          ))}
        </div>
      );
    }
    if (active === 'vacancies') {
      return (
        <div className="space-y-3">
          {vacancies.map((item) => (
            <div
              key={item.title}
              className="card-hover flex items-start gap-3 p-4 bg-white border border-gray-100 rounded-xl hover:border-purple-300"
            >
              <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center shrink-0 mt-0.5">
                <Briefcase size={15} className="text-purple-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[10px] font-semibold text-[#FF6200] mb-0.5">{item.org}</p>
                <a href={item.href} target="_blank" rel="noreferrer" className="text-xs text-gray-700 hover:text-[#003087] leading-snug block mb-2">
                  {item.title}
                </a>
                <a
                  href={item.pdf}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[9px] font-bold text-white bg-red-500 hover:bg-red-600 px-2 py-1 rounded transition-colors"
                >
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/></svg>
                  View PDF
                </a>
              </div>
            </div>
          ))}
        </div>
      );
    }
    if (active === 'tenders') {
      return (
        <div className="space-y-3">
          {tenders.map((item) => (
            <div
              key={item.title}
              className="card-hover flex items-start gap-3 p-4 bg-white border border-gray-100 rounded-xl hover:border-amber-300"
            >
              <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center shrink-0 mt-0.5">
                <Receipt size={15} className="text-amber-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[10px] font-semibold text-amber-600 mb-0.5">{item.org}</p>
                <p className="text-xs text-gray-700 leading-snug mb-2">{item.title}</p>
                <a
                  href={item.pdf}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[9px] font-bold text-white bg-red-500 hover:bg-red-600 px-2 py-1 rounded transition-colors"
                >
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/></svg>
                  View PDF
                </a>
              </div>
            </div>
          ))}
        </div>
      );
    }
  };

  const viewAllLinks = {
    schemes: 'https://www.dosje.gov.in/schemes-services/',
    vacancies: 'https://www.dosje.gov.in/vacancies/',
    tenders: 'https://www.dosje.gov.in/tenders/',
  };

  return (
    <section className="bg-[#f8f9fa] py-12 border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-1 h-6 bg-[#FF6200] rounded-full"></div>
            <div>
              <p className="text-[10px] text-gray-400 uppercase tracking-widest font-semibold">Discover our</p>
              <h2 className="text-xl font-bold text-[#003087]">Schemes, Careers &amp; Partnerships</h2>
            </div>
          </div>
          <a
            href={viewAllLinks[active]}
            target="_blank"
            rel="noreferrer"
            className="hidden md:flex items-center gap-1.5 text-xs font-semibold text-[#003087] border border-[#003087] px-3 py-1.5 rounded-full hover:bg-[#003087] hover:text-white transition-all duration-200"
          >
            View All <ArrowRight size={12} />
          </a>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-white rounded-xl p-1 border border-gray-200 mb-6 w-fit">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActive(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-200 ${
                  active === tab.id ? 'bg-[#003087] text-white shadow' : 'text-gray-600 hover:text-[#003087] hover:bg-gray-50'
                }`}
              >
                <Icon size={13} />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="transition-all duration-300">{renderItems()}</div>
      </div>
    </section>
  );
};

export default OfferingsSection;
