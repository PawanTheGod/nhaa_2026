import React from 'react';
import { ArrowRight, Calendar, Image as ImageIcon } from 'lucide-react';
import { ASSETS } from '../assets';

const events = [
  {
    title: 'NaMo Viksit Bharat Samvad "Har Ghar Tiranga: Inspiring Gen-Z to Uphold the Spirit of 80 Years of Independence."',
    date: 'Aug 2026',
    category: 'Event',
    href: 'https://www.dosje.gov.in/events/namo-viksit-bharat-samvad-har-ghar-tiranga-inspiring-gen-z-to-uphold-the-spirit-of-80-years-of-independence-constitutional-values-and-fundamental-duties/',
    img: null,
  },
  {
    title: 'test event – state officer',
    date: 'Aug 2026',
    category: 'Event',
    href: 'https://www.dosje.gov.in/events/test-event-state-officer/',
    img: null,
  },
];

const pressReleases = [
  {
    title: 'Memorial Lecture by Vice President: VP Radhakrishnan at DAIC',
    date: 'Aug 2026',
    href: 'https://www.dosje.gov.in/gallery/memorial-lecture-by-vice-president-vp-radhakrishnan-at-daic/',
    img: ASSETS.ddindia,
  },
  {
    title: 'Har Ghar Tiranga Campaign Seeks to Connect Gen-Z With Responsible Citizenship at CNMS Discussion',
    date: 'Aug 2026',
    href: 'https://www.dosje.gov.in/gallery/har-ghar-tiranga-campaign-seeks-to-connect-gen-z-with-responsible-citizenship-at-cnms-discussion/',
    img: ASSETS.harGharTiranga,
  },
  {
    title: "President Droupadi Murmu launches 'Ageing with Dignity' initiatives for Senior Citizens at Rashtrapati Bhavan",
    date: 'Jul 2026',
    href: 'https://www.dosje.gov.in/gallery/president-droupadi-murmu-launches-ageing-with-dignity-initiatives-for-senior-citizens-at-rashtrapati-bhavan-2/',
    img: null,
  },
];

const circulars = [
  { title: 'Submission of Annual Plan under GIA component of PM-AJAY for 2026–27 – reg.', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/08/pqRHCvMw26.pdf' },
  { title: "Tentative Notional Allocation for States/UTs under 'Grants-in-aid for District/State-level Projects' under PM-AJAY for 2026-27", pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/08/44synCnx0w.pdf' },
  { title: 'Committee formation DO to all State alongwith enclosure', pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/07/Committee-formation-DO-to-all-State-alongwith-enclosure.pdf' },
  { title: "Model Guidelines on Care, Rehabilitation, and Management of Beggar/Shelter Homes in compliance with Hon'ble Supreme Court directions", pdf: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/05/Model-guidelines-for-beggar_shelter-homes.pdf' },
];

const ActivityCorner = () => {
  return (
    <section className="bg-[#f8f9fa] py-12 border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4">

        <div className="flex items-center gap-3 mb-8">
          <div className="w-1 h-6 bg-[#FF6200] rounded-full"></div>
          <div>
            <h2 className="text-xl font-bold text-[#003087]">Activity Corner</h2>
            <p className="text-xs text-gray-400">Explore our affiliated bodies</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Events */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Calendar size={15} className="text-[#003087]" />
                <h3 className="text-sm font-bold text-[#003087]">Events</h3>
              </div>
              <a href="https://www.dosje.gov.in/events/" target="_blank" rel="noreferrer"
                className="text-[11px] text-[#FF6200] font-semibold hover:underline flex items-center gap-1">
                View All <ArrowRight size={11} />
              </a>
            </div>
            <div className="space-y-3">
              {events.map((item, i) => (
                <a key={i} href={item.href} target="_blank" rel="noreferrer"
                  className="card-hover flex items-start gap-3 p-3 bg-white border border-gray-100 rounded-xl hover:border-blue-200 group">
                  <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center shrink-0">
                    <Calendar size={17} className="text-[#003087]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">
                      {item.category}
                    </span>
                    <p className="text-[11px] text-gray-700 group-hover:text-[#003087] mt-1 leading-snug transition-colors line-clamp-2">
                      {item.title}
                    </p>
                    <span className="text-[10px] text-gray-400 mt-1 block">{item.date}</span>
                  </div>
                </a>
              ))}
            </div>
          </div>

          {/* Press Releases / Gallery with real thumbnails */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <ImageIcon size={15} className="text-[#003087]" />
                <h3 className="text-sm font-bold text-[#003087]">Press Releases &amp; Gallery</h3>
              </div>
              <a href="https://www.dosje.gov.in/gallery/" target="_blank" rel="noreferrer"
                className="text-[11px] text-[#FF6200] font-semibold hover:underline flex items-center gap-1">
                View All <ArrowRight size={11} />
              </a>
            </div>
            <div className="space-y-3">
              {pressReleases.map((item, i) => (
                <a key={i} href={item.href} target="_blank" rel="noreferrer"
                  className="card-hover flex items-start gap-3 p-3 bg-white border border-gray-100 rounded-xl hover:border-green-200 group">
                  {item.img ? (
                    <img
                      src={item.img}
                      alt={item.title}
                      className="w-14 h-10 rounded-lg object-cover shrink-0 border border-gray-100"
                      onError={e => {
                        e.target.outerHTML = '<div class="w-14 h-10 rounded-lg bg-green-50 flex items-center justify-center shrink-0"><svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg></div>';
                      }}
                    />
                  ) : (
                    <div className="w-14 h-10 rounded-lg bg-green-50 flex items-center justify-center shrink-0">
                      <ImageIcon size={17} className="text-green-400" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-green-100 text-green-700">Press Release</span>
                    <p className="text-[11px] text-gray-700 group-hover:text-[#003087] mt-1 leading-snug transition-colors line-clamp-2">
                      {item.title}
                    </p>
                    <span className="text-[10px] text-gray-400 mt-1 block">{item.date}</span>
                  </div>
                </a>
              ))}
            </div>
          </div>

          {/* Circulars & Notifications */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-[#003087]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-sm font-bold text-[#003087]">Circulars &amp; Notifications</h3>
              </div>
              <a href="https://www.dosje.gov.in/circulars-notifications/" target="_blank" rel="noreferrer"
                className="text-[11px] text-[#FF6200] font-semibold hover:underline flex items-center gap-1">
                View All <ArrowRight size={11} />
              </a>
            </div>
            <div className="space-y-2">
              {circulars.map((item, i) => (
                <a key={i} href={item.pdf} target="_blank" rel="noreferrer"
                  className="card-hover flex items-start gap-2.5 p-3 bg-white border border-gray-100 rounded-xl hover:border-amber-200 group">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#FF6200] shrink-0 mt-1.5"></div>
                  <p className="text-[11px] text-gray-700 group-hover:text-[#003087] transition-colors leading-snug line-clamp-2 flex-1">
                    {item.title}
                  </p>
                  <span className="text-[9px] text-red-500 font-bold shrink-0 bg-red-50 px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                    PDF
                  </span>
                </a>
              ))}
            </div>

            {/* Instagram CTA */}
            <div className="mt-5 p-4 rounded-xl border border-pink-200 bg-gradient-to-br from-pink-50 to-purple-50">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-5 h-5 text-pink-500" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
                </svg>
                <span className="text-xs font-bold text-pink-600">@our profile</span>
              </div>
              <p className="text-[11px] text-gray-500 mb-3">Follow us on Instagram to see our latest posts and reels.</p>
              <a
                href="https://www.instagram.com/msjegoi"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-[11px] font-bold text-white bg-gradient-to-r from-pink-500 to-purple-500 px-3 py-1.5 rounded-full hover:shadow-md transition-shadow"
              >
                Follow on Instagram <ArrowRight size={11} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ActivityCorner;
