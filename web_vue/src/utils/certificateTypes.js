// ECSACONM conference certificates of participation — one entry per
// certificate variant from the designer's HTML source (Attendees 5 CPD,
// Presenters 10 CPD, Ushers 0 CPD). `body` is a function of the event name and
// returns lines that are rendered with explicit line breaks, exactly as in the
// source design. The usher wording names the event it is supporting, so it
// needs the name the admin picked; the other two keep their fixed text.
const EVENT_LINES = [
  'and 8th Quadrennial General Assembly, from 14th to 18th September 2026',
  'at Golden Tulip Airport Hotel, Zanzibar',
]

// Used when no event is selected/known, so the sheet never renders "undefined".
export const DEFAULT_EVENT_NAME =
  '17th ECSACONM Biennial Scientific Conference & 8th General Assembly'

export const CERTIFICATE_TYPES = {
  attendee: {
    label: 'Delegates',
    cpd: 5,
    body: () => ['Having attended the 17th ECSACONM Biennial Scientific Conference', ...EVENT_LINES],
  },
  presenter: {
    label: 'Presenters',
    cpd: 10,
    body: () => ['Having presented in the 17th ECSACONM Biennial Scientific Conference', ...EVENT_LINES],
  },
  usher: {
    label: 'Ushers & Secretariat',
    cpd: 0,
    body: (eventName) => [
      'Having served as an usher/support staff, for supporting the',
      eventName || DEFAULT_EVENT_NAME,
      'from 14th to 18th September 2026 at Golden Tulip Airport Hotel, Zanzibar',
    ],
  },
}

// localStorage key the admin page writes the print job to; the print tab reads it.
export const CERTIFICATE_JOB_KEY = 'certificatePrintJob'

// Participation roles that all get the same "Delegates" certificate. These
// are the fee-based categories the registration form used to split delegates
// into (member state / other Africa / participant) plus exhibitors — on a
// certificate they're one group, matching how the badge prints them. Ushers
// and secretariat are NOT here: they have their own certificate type.
const DELEGATE_ROLE_KEYS = [
  'delegate',
  'member_state',
  'other_africa',
  'participant',
  'exhibitor',
]

const ROLE_LABELS = {
  secretariat: 'Secretariat',
  usher: 'Usher',
  media: 'Media',
  exhibitor: 'Exhibitor',
  student: 'Student',
  world: 'International',
  presenter: 'Presenter',
  speaker: 'Speaker',
  sponsor: 'Sponsor',
  moderator: 'Moderator',
}

// The certificate's "category" column for one registration — how the admin
// groups people on the page. Delegate-ish roles collapse to a single
// "Delegates" group; anything else keeps its own readable label.
export function certificateCategory(roleKey) {
  const key = String(roleKey || '').toLowerCase().trim()
  if (!key || DELEGATE_ROLE_KEYS.includes(key)) return 'Delegate'
  return ROLE_LABELS[key] || key.replace(/_/g, ' ')
}

// Names typed ALL CAPS or all lowercase at registration look wrong on a
// certificate — title-case those. Mixed-case names are left exactly as entered.
export function tidyName(name) {
  const n = String(name || '').replace(/\s+/g, ' ').trim()
  if (!n || (n !== n.toUpperCase() && n !== n.toLowerCase())) return n
  return n.toLowerCase().replace(/(^|[\s\-'.])(\p{L})/gu, (m, sep, ch) => sep + ch.toUpperCase())
}
