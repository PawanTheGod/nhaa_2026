/**
 * Presentation demo cases for SIH judges.
 * Nested flags + mixed status/level so Operator UI shows the full contract.
 */

export const DEMO_DISTRICT = 'Central Delhi';
export const DEMO_STATE = 'Delhi';

export const DEMO_CASES = [
  {
    channel_of_origin: 'ivrs',
    district: DEMO_DISTRICT,
    state: DEMO_STATE,
    language: 'en',
    is_silent_signal: true,
    incident_description:
      '[DEMO] Critical IVRS: ongoing intimidation; silent distress signal. Nested trauma/fear/suicidal_ideation flags.',
    ra: {
      svi_score: 94.5,
      risk_tier: 'critical',
      recommended_action: 'police_intervention',
      explanation_text:
        '[DEMO] Critical SVI with nested flags — show confidence % and signals in Case File.',
      model_version: 'demo-presentation-1.0',
      flags: {
        trauma: { present: true, confidence: 0.91, signals: ['voice tremor', 'high pitch variability'] },
        fear: { present: true, confidence: 0.88, signals: ['hesitation markers', 'whisper segments'] },
        suicidal_ideation: { present: true, confidence: 0.76, signals: ['keyword: end it', 'long pause: 4.2s'] },
        intimidation: { present: true, confidence: 0.84, signals: ['threat language'] },
        isolation: { present: false, confidence: 0.12, signals: [] },
      },
    },
    escalate_to: null, // keep new/operator for action buttons
  },
  {
    channel_of_origin: 'portal',
    district: DEMO_DISTRICT,
    state: DEMO_STATE,
    language: 'en',
    is_silent_signal: false,
    incident_description:
      '[DEMO] High portal grievance: social boycott alleged — will be escalated to district for status+level demo.',
    ra: {
      svi_score: 78.2,
      risk_tier: 'high',
      recommended_action: 'legal_aid',
      explanation_text: '[DEMO] High distress; escalate_to_district shows status=escalated + current_level=district.',
      model_version: 'demo-presentation-1.0',
      flags: {
        trauma: { present: true, confidence: 0.72, signals: ['narrative distress markers'] },
        fear: { present: true, confidence: 0.81, signals: ['avoidance language'] },
        suicidal_ideation: { present: false, confidence: 0.08, signals: [] },
        intimidation: { present: true, confidence: 0.79, signals: ['boycott threat', 'community pressure'] },
        isolation: { present: true, confidence: 0.68, signals: ['denied public access'] },
      },
    },
    escalate_to: 'escalate_to_district',
  },
  {
    channel_of_origin: 'chatbot',
    district: DEMO_DISTRICT,
    state: DEMO_STATE,
    language: 'en',
    is_silent_signal: false,
    incident_description:
      '[DEMO] Moderate chatbot: workplace discrimination — counselling referral.',
    ra: {
      svi_score: 52.0,
      risk_tier: 'moderate',
      recommended_action: 'counselling',
      explanation_text: '[DEMO] Moderate tier with trauma present for nested-flag rendering.',
      model_version: 'demo-presentation-1.0',
      flags: {
        trauma: { present: true, confidence: 0.61, signals: ['workplace discrimination narrative'] },
        fear: { present: false, confidence: 0.22, signals: [] },
        suicidal_ideation: { present: false, confidence: 0.05, signals: [] },
        intimidation: { present: false, confidence: 0.18, signals: [] },
        isolation: { present: false, confidence: 0.15, signals: [] },
      },
    },
    escalate_to: null,
  },
  {
    channel_of_origin: 'mobile_app',
    district: DEMO_DISTRICT,
    state: DEMO_STATE,
    language: 'en',
    is_silent_signal: false,
    incident_description:
      '[DEMO] High mobile report: physical assault — medical + police coordination.',
    ra: {
      svi_score: 81.0,
      risk_tier: 'high',
      recommended_action: 'medical_assistance',
      explanation_text: '[DEMO] High trauma/fear nested flags for medical pathway demo.',
      model_version: 'demo-presentation-1.0',
      flags: {
        trauma: { present: true, confidence: 0.89, signals: ['pain vocalisations', 'assault keywords'] },
        fear: { present: true, confidence: 0.85, signals: ['elevated pitch', 'rapid speech'] },
        suicidal_ideation: { present: false, confidence: 0.09, signals: [] },
        intimidation: { present: true, confidence: 0.74, signals: ['perpetrator nearby mention'] },
        isolation: { present: false, confidence: 0.2, signals: [] },
      },
    },
    escalate_to: null,
  },
];
