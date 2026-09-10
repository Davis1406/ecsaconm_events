// Shared badge "category bar" formatting — keep in sync with
// `format_badge_category()` in api/routers/events.py.
//
// Member States, Other Africa and general Participant registrations are all
// printed on the badge simply as "Delegate" (per design). Everything else
// keeps its own distinct label.
const DELEGATE_ROLE_KEYS = ['member_state', 'other_africa', 'participant']

const ROLE_LABELS = {
  world: 'International',
  student: 'Student',
  exhibitor: 'Exhibitor',
  exibitor: 'Exhibitor',
  secretariat: 'Secretariat',
  delegate: 'Delegate',
  presenter: 'Presenter',
  speaker: 'Speaker',
  sponsor: 'Sponsor',
  moderator: 'Moderator',
  moh: 'Ministry of Health',
  member: 'Member',
}

export function formatBadgeCategory(roleKey) {
  if (!roleKey) return 'Delegate'
  const key = String(roleKey).toLowerCase().trim()
  if (DELEGATE_ROLE_KEYS.includes(key)) return 'Delegate'
  if (ROLE_LABELS[key]) return ROLE_LABELS[key]
  return key
    .split(/[_\s]+/)
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}
