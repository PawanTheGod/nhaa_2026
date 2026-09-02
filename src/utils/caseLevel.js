/** Map API current_level (string or legacy int) to a display label. */
const LEVEL_BY_INT = {
  0: 'operator',
  1: 'district',
  2: 'state',
  3: 'ministry',
};

const LEVEL_LABELS = {
  operator: 'Operator',
  district: 'District',
  state: 'State',
  ministry: 'Ministry',
  police: 'Police',
};

/**
 * @param {string|number|null|undefined} level
 * @returns {string|null} human-readable level or null if unset
 */
export function formatCurrentLevel(level) {
  if (level == null || level === '') return null;
  if (typeof level === 'number' || /^\d+$/.test(String(level))) {
    const key = LEVEL_BY_INT[Number(level)];
    return key ? LEVEL_LABELS[key] || key : String(level);
  }
  const key = String(level).toLowerCase();
  return LEVEL_LABELS[key] || key.replace(/_/g, ' ');
}

/** Pretty label for engine action strings e.g. escalate_to_district */
export function formatActionLabel(action) {
  if (!action) return '';
  return String(action)
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

/** Offline / mock allowed actions when API is unavailable */
export function mockAllowedActions(caseData, role = 'operator') {
  const status = String(caseData?.status || 'new').toLowerCase();
  const level = caseData?.current_level;

  if (['police', 'dlsa', 'medical', 'counselor', 'witness_protection'].includes(role)) {
    return caseData?.actioned ? [] : ['mark_actioned'];
  }

  if (status === 'resolved' || status === 'closed') {
    return ['reopen'];
  }

  const actions = [];
  if (status === 'new' || status === 'in_progress') {
    actions.push('assign_operator', 'escalate_to_district', 'dispatch_police', 'resolve');
  }
  if (status === 'escalated') {
    const lvl = typeof level === 'number' ? LEVEL_BY_INT[level] : String(level || '').toLowerCase();
    if (lvl === 'district' || lvl === '1') actions.push('escalate_to_state', 'resolve');
    else if (lvl === 'state' || lvl === '2') actions.push('escalate_to_ministry', 'resolve');
    else if (lvl === 'ministry' || lvl === '3') actions.push('resolve', 'close');
    else actions.push('escalate_to_district', 'resolve');
  }
  if (actions.length === 0) actions.push('resolve', 'escalate_to_district');
  return actions;
}
