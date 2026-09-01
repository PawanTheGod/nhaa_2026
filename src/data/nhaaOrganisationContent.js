/**
 * Section-by-section content from the official DOSJE NHAA organisation page.
 * Source: https://www.dosje.gov.in/organisation/national-helpline-against-atrocities/
 */

import { ASSETS } from '../assets';

export const NHAA_ORG_BASE = '/organisation/national-helpline-against-atrocities';

export const SIDE_MENU = [
  { label: 'ABOUT US', type: 'heading' },
  { label: 'About the Scheme', href: '#aboutCommissionSec' },
  { label: 'Leadership & Organisation', href: '#leadershipOrganisationSec' },
  { label: 'OUR WORK & IMPACT', type: 'heading' },
  { label: 'Reports', href: '#reportsSec' },
  { label: 'Resources', href: '#resourcesSec' },
  { label: 'Latest Updates', href: '#LatestUpdatesSec' },
  { label: 'CONNECT & ENGAGE', type: 'heading' },
  { label: 'Contact', href: '#contactUsSec' },
  { label: 'Acts', href: '/about-us', internal: true },
  { label: 'Central Act', href: '/about-us', internal: true },
  { label: 'State-wise Stastics', href: '/schemes', internal: true },
  { label: 'IEC Material', href: '/tenders', internal: true },
  { label: 'FAQs', href: '/contact-us', internal: true },
];

export const LEADERSHIP = [
  {
    name: 'Mona K. Khandhar',
    title: 'IAS Additional Secretary D/O SJ&E (PCR-PoA & PM-AJAY)',
    image: ASSETS.monaIAS,
    profilePath: '/about-us',
  },
  {
    name: 'Mahender Singh',
    title: 'DS-(PCR-PoA) PCR-POA',
    image: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2025/11/Profile-Image-2.png',
    profilePath: '/about-us',
  },
  {
    name: 'Sunil Kumar Bhatia',
    title: 'Under Secretary PCR-POA, NSFDC, Vigilance',
    image: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2025/11/Profile-Image-2.png',
    profilePath: '/about-us',
  },
];

export const REPORTS = [
  {
    title: 'Annual Report English PoA 2023',
    date: '09 Mar 2026',
    type: 'Annual Reports',
    fileType: 'PDF',
    size: '0 MB',
    url: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/03/PoA-Act-Report-2023-English.pdf',
  },
  {
    title: 'Annual Report POA 2023',
    date: '09 Mar 2026',
    type: 'Annual Reports',
    fileType: 'PDF',
    size: '0 MB',
    url: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/03/PoA-Act-Report-2023-Hindi.pdf',
  },
  {
    title: 'Annual Report PoA 2022',
    date: '09 Mar 2026',
    type: 'Annual Reports',
    fileType: 'PDF',
    size: '0 MB',
    url: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/03/PoA-Act-Report-2022-English.pdf',
  },
];

export const RESOURCES = [
  {
    title: 'Press Release 08 Jan 2026',
    date: '09 Mar 2026',
    type: 'Publications',
    fileType: 'PDF',
    size: '0.78 MB',
    url: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/03/Press-Release-2.pdf',
  },
  {
    title: 'Press Release 23 May 2025',
    date: '09 Mar 2026',
    type: 'Publications',
    fileType: 'PDF',
    size: '0.15 MB',
    url: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/03/Press-Release_23May-2025.pdf',
  },
  {
    title: 'Booklet – Modernization and Strengthening',
    date: '09 Mar 2026',
    type: 'Publications',
    fileType: 'PDF',
    size: '0 MB',
    url: 'https://durwo6bhtjtqt.cloudfront.net/wp-content/uploads/2026/03/Modernisation-and-Strengthening-of-SPSs-and-ESCs.pdf',
  },
];

export const LATEST_UPDATES = {
  subtitle: 'Explore our schemes, career opportunities, and business partnerships',
  tabs: [
    {
      id: 'events',
      label: 'Events',
      viewAllPath: '/about-us',
      items: [
        {
          day: '08',
          month: 'Jan 2026',
          title: '29th Meeting of the Committee to Review the Implementation of the SC/ST (Prevention of Atrocities) Act, 1989, and the Protection of Civil Rights (PCR) Act, 1955.',
          link: '/about-us',
        },
        {
          day: '23',
          month: 'May 2025',
          title: 'DoSJE organizes 28th Coordination Committee Meeting to devise Ways and Means to curb Offences of Untouchability and Atrocities against SCs and STs',
          link: '/about-us',
        },
      ],
    },
    {
      id: 'press',
      label: 'Press Releases',
      viewAllPath: '/tenders',
      items: [
        {
          day: '08',
          month: 'Jan 2026',
          title: 'Press Release on NHAA Helpline 14566 awareness campaign',
          link: '/tenders',
        },
        {
          day: '23',
          month: 'May 2025',
          title: 'Press Release on coordination committee meeting outcomes',
          link: '/tenders',
        },
      ],
    },
    {
      id: 'circulars',
      label: 'Circulars',
      viewAllPath: '/tenders',
      items: [
        {
          day: '15',
          month: 'Feb 2026',
          title: 'Circular on implementation timelines under POA Act, 1989',
          link: '/tenders',
        },
        {
          day: '02',
          month: 'Dec 2025',
          title: 'Circular on grievance redressal monitoring for NHAA',
          link: '/tenders',
        },
      ],
    },
  ],
};

export const TAGS = [
  'atrocities',
  'Citizen Rights',
  'helpdesk',
  'NHAA',
  'POA',
  'Prevention of Atrocities Helpdesk',
  'protection of civil rights act',
  'sc st act 1989',
  'SC ST atrocity',
  'Victim Support',
];
