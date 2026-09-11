/**
 * Mock data for the State admin screen.
 * Data shape (per data contract — Step 14):
 *   stats: { totalCases, tierBreakdown: {low, moderate, high, critical}, resolutionRate }
 *   trend: [{ week: string, cases: number, sviAvg: number }]
 *   districtTable: [{ district, cases, resolved, resolutionRate, highRisk }]
 */
export const stateMockData = {
  state: 'Maharashtra',
  stats: {
    totalCases: 4892,
    tierBreakdown: {
      low: 2650,
      moderate: 1380,
      high: 580,
      critical: 282,
    },
    resolutionRate: 86.4,
    pendingSLA: 19,
  },
  trend: [
    { week: 'Aug 18', cases: 540, sviAvg: 41.2 },
    { week: 'Aug 25', cases: 512, sviAvg: 47.6 },
    { week: 'Sep 01', cases: 489, sviAvg: 51.4 },
    { week: 'Sep 08', cases: 465, sviAvg: 49.8 },
  ],
  districtTable: [
    { district: 'Pune District', cases: 684, resolved: 592, resolutionRate: 86.5, highRisk: 34 },
    { district: 'Nagpur', cases: 512, resolved: 442, resolutionRate: 86.3, highRisk: 28 },
    { district: 'Thane', cases: 495, resolved: 430, resolutionRate: 86.8, highRisk: 24 },
    { district: 'Chhatrapati Sambhajinagar', cases: 448, resolved: 382, resolutionRate: 85.2, highRisk: 32 },
    { district: 'Solapur', cases: 420, resolved: 368, resolutionRate: 87.6, highRisk: 21 },
    { district: 'Nashik', cases: 395, resolved: 344, resolutionRate: 87.1, highRisk: 19 },
    { district: 'Ahmednagar', cases: 382, resolved: 328, resolutionRate: 85.9, highRisk: 26 },
    { district: 'Nanded', cases: 360, resolved: 308, resolutionRate: 85.5, highRisk: 22 },
    { district: 'Satara', cases: 310, resolved: 275, resolutionRate: 88.7, highRisk: 14 },
    { district: 'Kolhapur', cases: 298, resolved: 264, resolutionRate: 88.6, highRisk: 12 },
  ],
};
