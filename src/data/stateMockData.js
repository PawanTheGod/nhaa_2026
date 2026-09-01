/**
 * Mock data for the State admin screen.
 * Data shape (per data contract — Step 14):
 *   stats: { totalCases, tierBreakdown: {low, moderate, high, critical}, resolutionRate }
 *   trend: [{ week: string, cases: number, sviAvg: number }]
 *   districtTable: [{ district, cases, resolved, resolutionRate, highRisk }]
 */
export const stateMockData = {
  state: 'Delhi',
  stats: {
    totalCases: 2847,
    tierBreakdown: {
      low: 1542,
      moderate: 812,
      high: 326,
      critical: 167,
    },
    resolutionRate: 84.3,
    pendingSLA: 23,
  },
  trend: [
    { week: 'Aug 18', cases: 340, sviAvg: 42.3 },
    { week: 'Aug 25', cases: 318, sviAvg: 48.1 },
    { week: 'Sep 01', cases: 295, sviAvg: 52.7 },
  ],
  districtTable: [
    { district: 'Central Delhi', cases: 487, resolved: 412, resolutionRate: 84.6, highRisk: 23 },
    { district: 'East Delhi', cases: 356, resolved: 301, resolutionRate: 84.5, highRisk: 18 },
    { district: 'South Delhi', cases: 445, resolved: 378, resolutionRate: 85.0, highRisk: 31 },
    { district: 'North Delhi', cases: 289, resolved: 251, resolutionRate: 87.2, highRisk: 12 },
    { district: 'West Delhi', cases: 312, resolved: 276, resolutionRate: 88.5, highRisk: 15 },
    { district: 'South-East Delhi', cases: 267, resolved: 229, resolutionRate: 85.8, highRisk: 19 },
    { district: 'South-West Delhi', cases: 234, resolved: 200, resolutionRate: 85.5, highRisk: 11 },
    { district: 'North-East Delhi', cases: 198, resolved: 170, resolutionRate: 85.9, highRisk: 8 },
    { district: 'North-West Delhi', cases: 293, resolved: 254, resolutionRate: 86.7, highRisk: 14 },
    { district: 'Shahjahanpur', cases: 158, resolved: 135, resolutionRate: 85.4, highRisk: 9 },
  ],
};
