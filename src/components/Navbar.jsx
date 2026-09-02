import React, { useState } from 'react';
import { ChevronDown, Menu, X } from 'lucide-react';

const navItems = [
  { label: 'Home', href: '#' },
  {
    label: 'Department',
    children: [
      { label: 'About Us', href: '#' },
      { label: "Who's Who", href: '#' },
      { label: 'Directory', href: '#' },
    ],
  },
  {
    label: 'Associated Organisations',
    megaMenu: true,
    sections: [
      {
        title: 'COMMISSIONS',
        items: [
          { code: 'NCSC', label: 'National Commission for Scheduled Castes', href: '#' },
          { code: 'NCSK', label: 'National Commission for Safai Karamcharis', href: '#' },
          { code: 'NCBC', label: 'National Commission for Backward Classes', href: '#' },
        ],
      },
      {
        title: 'CORPORATIONS',
        items: [
          { code: 'NSFDC', label: 'National Scheduled Castes Finance and Development Corporation', href: '#' },
          { code: 'NSKFDC', label: 'National Safai Karamcharis Finance and Development Corporation', href: '#' },
          { code: 'NBCFDC', label: 'National Backward Classes Finance and Development Corporation', href: '#' },
        ],
      },
      {
        title: 'FOUNDATION / AUTONOMOUS BODIES',
        items: [
          { code: 'DAF', label: 'Dr. Ambedkar Foundation', href: '#' },
          { code: 'DAIC', label: 'Dr. Ambedkar International Centre', href: '#' },
          { code: 'BJRNF', label: 'Babu JagJivan Ram National Foundation', href: '#' },
          { code: 'DWBDNC', label: 'Development and Welfare Board for De-notified, Nomadic, and Semi-Nomadic Communities', href: '#' },
          { code: 'NISD', label: 'National Institute of Social Defence', href: '#' },
        ],
      },
      {
        title: 'SCHEME SPECIFIC THEMATIC PORTALS',
        items: [
          { code: 'SCW', label: 'Senior Citizens Welfare', href: '#' },
          { code: 'PM-AJAY', label: 'Pradhan Mantri Anusuchit Jaati Abhyuday Yojna', href: '#' },
          { code: 'SMILE', label: 'National Portal for Transgender Persons', href: '#' },
          { code: 'NOS', label: 'National Overseas Scholarship', href: '/schemes' },
          { code: 'NMBA', label: 'Nasha Mukt Bharat Abhiyaan', href: '/samavesh' },
          { code: 'NHAA / SAMBAL', label: 'National Helpline Against Atrocities', href: '/organisation/national-helpline-against-atrocities' },
        ],
      },
    ],
  },
  {
    label: 'Offerings',
    children: [
      { label: 'Schemes & Services', href: '#' },
      { label: 'Vacancies', href: '#' },
      { label: 'Tenders', href: '#' },
    ],
  },
  {
    label: 'Documents',
    children: [
      { label: 'Annual Reports', href: '#' },
      { label: 'Acts & Rules', href: '#' },
      { label: 'Policies', href: '#' },
      { label: 'Resources', href: '#' },
      { label: 'Circulars & Notifications', href: '#' },
      { label: 'Forms & Templates', href: '#' },
      { label: 'Publications', href: '#' },
      { label: 'Notices', href: '#' },
      { label: 'RTI', href: '#' },
      { label: 'MOU', href: '#' },
      { label: 'Advices', href: '#' },
      { label: 'Miscellaneous', href: '#' },
    ],
  },
  {
    label: 'Events & Gallery',
    children: [
      { label: 'Events', href: '#' },
      { label: 'Gallery', href: '#' },
    ],
  },
  {
    label: 'Connect',
    children: [
      { label: 'CPIO', href: '#' },
      { label: 'Directory', href: '#' },
      { label: 'Contact Us', href: '#' },
    ],
  },
];

const DropdownMenu = ({ items }) => (
  <div className="absolute top-full left-0 bg-white shadow-xl rounded-b-lg border-t-2 border-[#FF6200] min-w-[220px] z-50 dropdown-enter py-1">
    {items.map((item) => (
      <a
        key={item.label}
        href={item.href}
        className="flex items-center px-5 py-2.5 text-sm text-gray-700 hover:bg-[#f0f5ff] hover:text-[#003087] hover:pl-6 transition-all duration-150 border-b border-gray-50 last:border-b-0"
      >
        {item.label}
      </a>
    ))}
  </div>
);

const MegaMenu = ({ sections }) => (
  <div className="absolute top-full left-1/2 -translate-x-1/2 bg-white shadow-2xl rounded-b-lg border-t-2 border-[#FF6200] z-50 w-[900px] dropdown-enter">
    <div className="grid grid-cols-4 gap-0 p-6">
      {sections.map((section) => (
        <div key={section.title} className="pr-6 border-r border-gray-100 last:border-r-0 last:pr-0">
          <h4 className="text-[10px] font-bold tracking-widest text-[#FF6200] uppercase mb-3 pb-2 border-b border-orange-100">
            {section.title}
          </h4>
          <ul className="space-y-1.5">
            {section.items.map((item) => (
              <li key={item.code}>
                <a
                  href={item.href}
                  className="group flex items-start gap-2 text-xs text-gray-700 hover:text-[#003087] transition-colors"
                >
                  <span className="text-[9px] font-bold bg-[#003087] text-white px-1.5 py-0.5 rounded mt-0.5 shrink-0 group-hover:bg-[#FF6200] transition-colors">
                    {item.code}
                  </span>
                  <span className="leading-tight">{item.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  </div>
);

const Navbar = () => {
  const [activeMenu, setActiveMenu] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [mobileExpanded, setMobileExpanded] = useState(null);

  const handleMouseEnter = (label) => setActiveMenu(label);
  const handleMouseLeave = () => setActiveMenu(null);

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          {/* Desktop Nav */}
          <div className="hidden lg:flex items-center h-full gap-0.5">
            {navItems.map((item) => (
              <div
                key={item.label}
                className="relative h-full flex items-center"
                onMouseEnter={() => item.children || item.megaMenu ? handleMouseEnter(item.label) : null}
                onMouseLeave={handleMouseLeave}
              >
                <a
                  href={item.href || '#'}
                  className={`nav-link-hover flex items-center gap-1 px-3 py-2 text-[13px] font-medium transition-all duration-200 rounded
                    ${activeMenu === item.label
                      ? 'text-[#003087] bg-blue-50'
                      : 'text-gray-700 hover:text-[#003087] hover:bg-blue-50'
                    }`}
                >
                  {item.label}
                  {(item.children || item.megaMenu) && (
                    <ChevronDown
                      size={13}
                      className={`transition-transform duration-200 ${activeMenu === item.label ? 'rotate-180' : ''}`}
                    />
                  )}
                </a>

                {activeMenu === item.label && item.children && (
                  <DropdownMenu items={item.children} />
                )}
                {activeMenu === item.label && item.megaMenu && (
                  <MegaMenu sections={item.sections} />
                )}
              </div>
            ))}
          </div>

          {/* Right: Search */}
          <div className="hidden lg:flex items-center gap-3">
            <div className="flex items-center bg-gray-100 rounded-full px-3 py-1.5 gap-2">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search..."
                className="bg-transparent text-sm text-gray-600 outline-none w-32 placeholder-gray-400"
              />
            </div>
          </div>

          {/* Mobile hamburger */}
          <button
            className="lg:hidden text-gray-700 p-2"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="lg:hidden bg-white border-t border-gray-100 shadow-lg max-h-[80vh] overflow-y-auto">
          {navItems.map((item) => (
            <div key={item.label} className="border-b border-gray-50">
              <button
                className="w-full flex items-center justify-between px-5 py-3 text-sm font-medium text-gray-700 hover:bg-blue-50 hover:text-[#003087] transition-colors"
                onClick={() =>
                  (item.children || item.megaMenu)
                    ? setMobileExpanded(mobileExpanded === item.label ? null : item.label)
                    : null
                }
              >
                {item.label}
                {(item.children || item.megaMenu) && (
                  <ChevronDown
                    size={15}
                    className={`transition-transform ${mobileExpanded === item.label ? 'rotate-180' : ''}`}
                  />
                )}
              </button>
              {mobileExpanded === item.label && item.children && (
                <div className="bg-gray-50 pl-8 pb-2">
                  {item.children.map((child) => (
                    <a
                      key={child.label}
                      href={child.href}
                      className="block py-2 text-sm text-gray-600 hover:text-[#003087]"
                    >
                      {child.label}
                    </a>
                  ))}
                </div>
              )}
              {mobileExpanded === item.label && item.megaMenu && (
                <div className="bg-gray-50 pl-8 pb-2">
                  {item.sections.flatMap(s => s.items).map((child) => (
                    <a
                      key={child.code}
                      href={child.href}
                      className="block py-1.5 text-sm text-gray-600 hover:text-[#003087]"
                    >
                      <span className="text-[9px] font-bold bg-[#003087] text-white px-1 py-0.5 rounded mr-2">
                        {child.code}
                      </span>
                      {child.label}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
