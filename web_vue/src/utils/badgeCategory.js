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
  media: 'Media',
  usher: 'Usher',
  member: 'Member',
}

// Category-bar colours per role — keep in sync with `badge_category_gradient()`
// in api/routers/events.py. Delegates (and everything without an override) keep
// the navy bar; staff/event teams get their own colour.
const CATEGORY_GRADIENTS = {
  secretariat: { background: 'linear-gradient(to right, #14532d, #166534, #14532d)', border: 'rgba(34,197,94,0.4)' },
  media: { background: 'linear-gradient(to right, #78350f, #92400e, #78350f)', border: 'rgba(245,158,11,0.4)' },
  exhibitor: { background: 'linear-gradient(to right, #134e4a, #0f766e, #134e4a)', border: 'rgba(20,184,166,0.4)' },
  usher: { background: 'linear-gradient(to right, #1e3a8a, #1d4ed8, #1e3a8a)', border: 'rgba(59,130,246,0.4)' },
}
const DEFAULT_CATEGORY_GRADIENT = {
  background: 'linear-gradient(to right, #173a4b, #1d4659, #173a4b)',
  border: 'rgba(43,93,115,0.4)',
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

export function badgeCategoryGradient(roleKey) {
  if (!roleKey) return DEFAULT_CATEGORY_GRADIENT
  const key = String(roleKey).toLowerCase().trim()
  if (DELEGATE_ROLE_KEYS.includes(key)) return DEFAULT_CATEGORY_GRADIENT
  return CATEGORY_GRADIENTS[key] || DEFAULT_CATEGORY_GRADIENT
}
