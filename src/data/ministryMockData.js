/**
 * Mock data for the Ministry admin screen.
 * Data shape (per data contract — Step 14):
 *   nationalTrend: [{ week: string, cases: number, sviAvg: number, critical: number }]
 *   stateTable: [{ state, cases, resolved, resolutionRate, highRisk, critical }]
 */
export const ministryMockData = {
  nationalStats: {
    totalCases: 184562,
    avgSvi: 58.3,
    activeSLA: 2847,
    statesReporting: 36,
  },
  nationalTrend: [
    { week: 'Aug 18', cases: 8420, sviAvg: 55.3, critical: 124 },
    { week: 'Aug 25', cases: 9156, sviAvg: 57.8, critical: 156 },
    { week: 'Sep 01', cases: 8942, sviAvg: 60.1, critical: 142 },
  ],
  stateTable: [
    { state: 'Uttar Pradesh', cases: 28500, resolved: 24125, resolutionRate: 84.6, highRisk: 1250, critical: 42 },
    { state: 'Bihar', cases: 19200, resolved: 16320, resolutionRate: 85.0, highRisk: 890, critical: 38 },
    { state: 'West Bengal', cases: 15600, resolved: 13260, resolutionRate: 85.0, highRisk: 740, critical: 31 },
    { state: 'Maharashtra', cases: 14800, resolved: 12580, resolutionRate: 85.0, highRisk: 680, critical: 29 },
    { state: 'Madhya Pradesh', cases: 12300, resolved: 10455, resolutionRate: 85.0, highRisk: 560, critical: 24 },
    { state: 'Rajasthan', cases: 11200, resolved: 9520, resolutionRate: 85.0, highRisk: 510, critical: 21 },
    { state: 'Tamil Nadu', cases: 9800, resolved: 8330, resolutionRate: 85.0, highRisk: 450, critical: 19 },
    { state: 'Karnataka', cases: 8500, resolved: 7225, resolutionRate: 85.0, highRisk: 390, critical: 17 },
    { state: 'Telangana', cases: 4600, resolved: 3910, resolutionRate: 85.0, highRisk: 210, critical: 9 },
    { state: 'Delhi', cases: 2847, resolved: 2400, resolutionRate: 84.3, highRisk: 126, critical: 6 },
  ],
};
