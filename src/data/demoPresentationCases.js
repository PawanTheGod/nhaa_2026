/**
 * Presentation demo cases for SIH judges.
 * Nested flags + mixed status/level so Operator UI shows the full contract.
 * Updated with Maharashtra & Pune District jurisdictions.
 */

export const DEMO_DISTRICT = 'Pune District';
export const DEMO_STATE = 'Maharashtra';

export const DEMO_CASES = [
  {
    person_name: 'Smt. Vandana Ashok Bhalerao',
    incident_location: 'Gali No. 4, Janwadi, Senapati Bapat Road, Chatuhshrungi, Pune City',
    channel_of_origin: 'ivrs',
    district: DEMO_DISTRICT,
    state: DEMO_STATE,
    language: 'en',
    is_silent_signal: true,
    incident_description:
      'Critical IVRS: Complainant Vandana Bhalerao reporting armed intimidation & physical assault in Janwadi; silent distress signal detected.',
    ra: {
      svi_score: 94.5,
      risk_tier: 'critical',
      recommended_action: 'police_intervention',
      explanation_text:
        'Critical SVI with nested flags: high tremor, fear markers, armed intimidation. Immediate Pune Police emergency squad dispatch recommended.',
      model_version: 'demo-presentation-1.0',
      flags: {
        trauma: { present: true, confidence: 0.91, signals: ['voice tremor', 'high pitch variability'] },
        fear: { present: true, confidence: 0.88, signals: ['hesitation markers', 'whisper segments'] },
        suicidal_ideation: { present: true, confidence: 0.76, signals: ['keyword: extreme fear', 'long pause: 4.2s'] },
        intimidation: { present: true, confidence: 0.84, signals: ['threat language', 'armed extortion'] },
        isolation: { present: false, confidence: 0.12, signals: [] },
      },
    },
    escalate_to: null,
  },
  {
    person_name: 'Shri Eknath Ganpat Thorat & Family',
    incident_location: 'Gat No. 124, Village Shikrapur, Shirur Taluka, Pune District',
    channel_of_origin: 'portal',
    district: DEMO_DISTRICT,
    state: DEMO_STATE,
    language: 'en',
    is_silent_signal: false,
    incident_description:
      'High portal grievance: Illegal land encroachment on Dalit farmland, destruction of crops, social boycott alleged.',
    ra: {
      svi_score: 78.2,
      risk_tier: 'high',
      recommended_action: 'legal_aid',
      explanation_text: 'High distress; escalate_to_district shows status=escalated + current_level=district.',
      model_version: 'demo-presentation-1.0',
      flags: {
        trauma: { present: true, confidence: 0.72, signals: ['narrative distress markers'] },
        fear: { present: true, confidence: 0.81, signals: ['avoidance language'] },
        suicidal_ideation: { present: false, confidence: 0.08, signals: [] },
        intimidation: { present: true, confidence: 0.79, signals: ['boycott threat', 'community pressure'] },
        isolation: { present: true, confidence: 0.68, signals: ['denied public road access'] },
      },
    },
    escalate_to: 'dsp',
  },
  {
    person_name: 'Dr. Virendra Tukaram Waghmare',
    incident_location: 'Sub-District Hospital, Shirur Taluka, Pune District',
    channel_of_origin: 'chatbot',
    district: DEMO_DISTRICT,
    state: DEMO_STATE,
    language: 'en',
    is_silent_signal: false,
    incident_description:
      'Moderate chatbot: Medical officer targeted with fabricated charges, abusive WhatsApp audio messages, casteist insults.',
    ra: {
      svi_score: 52.0,
      risk_tier: 'moderate',
      recommended_action: 'counseling',
      explanation_text: 'Moderate distress; institutional support & DLSA Pune legal counseling recommended.',
      model_version: 'demo-presentation-1.0',
      flags: {
        trauma: { present: false, confidence: 0.22, signals: [] },
        fear: { present: true, confidence: 0.64, signals: ['workplace vulnerability'] },
        suicidal_ideation: { present: false, confidence: 0.05, signals: [] },
        intimidation: { present: true, confidence: 0.71, signals: ['unlawful pressure'] },
        isolation: { present: false, confidence: 0.15, signals: [] },
      },
    },
    escalate_to: null,
  },
  {
    person_name: 'Kumari Pooja Vilas Salve',
    incident_location: 'Survey No. 48, Ghole Road, Shivajinagar, Pune City',
    channel_of_origin: 'mobile_app',
    district: DEMO_DISTRICT,
    state: DEMO_STATE,
    language: 'en',
    is_silent_signal: false,
    incident_description:
      'Low mobile app: Guidance requested for Dr. Babasaheb Ambedkar Swadhar Scheme & education hostel allowance in Pune.',
    ra: {
      svi_score: 18.0,
      risk_tier: 'low',
      recommended_action: 'general_info',
      explanation_text: 'Routine welfare scheme inquiry; zero distress markers detected.',
      model_version: 'demo-presentation-1.0',
      flags: {
        trauma: { present: false, confidence: 0.02, signals: [] },
        fear: { present: false, confidence: 0.04, signals: [] },
        suicidal_ideation: { present: false, confidence: 0.01, signals: [] },
        intimidation: { present: false, confidence: 0.03, signals: [] },
        isolation: { present: false, confidence: 0.02, signals: [] },
      },
    },
    escalate_to: null,
  },
];
