// ECSACONM conference certificates of participation — one entry per
// certificate variant from the designer's HTML source (Attendees 5 CPD,
// Presenters 10 CPD, Ushers 0 CPD). `body` lines are rendered with explicit
// line breaks, exactly as in the source design.
const EVENT_LINES = [
  'and 8th Quadrennial General Assembly, from 14th to 18th September 2026',
  'at Golden Tulip Airport Hotel, Zanzibar',
]

export const CERTIFICATE_TYPES = {
  attendee: {
    label: 'Attendees',
    cpd: 5,
    body: ['Having attended the 17th ECSACONM Biennial Scientific Conference', ...EVENT_LINES],
  },
  presenter: {
    label: 'Presenters',
    cpd: 10,
    body: ['Having presented in the 17th ECSACONM Biennial Scientific Conference', ...EVENT_LINES],
  },
  usher: {
    label: 'Ushers / Support Staff',
    cpd: 0,
    body: [
      'Having served as an usher/support staff at the 17th ECSACONM Biennial Scientific',
      'Conference and 8th Quadrennial General Assembly, from 14th to 18th September 2026',
      'at Golden Tulip Airport Hotel, Zanzibar',
    ],
  },
}

// localStorage key the admin page writes the print job to; the print tab reads it.
export const CERTIFICATE_JOB_KEY = 'certificatePrintJob'

// Names typed ALL CAPS or all lowercase at registration look wrong on a
// certificate — title-case those. Mixed-case names are left exactly as entered.
export function tidyName(name) {
  const n = String(name || '').replace(/\s+/g, ' ').trim()
  if (!n || (n !== n.toUpperCase() && n !== n.toLowerCase())) return n
  return n.toLowerCase().replace(/(^|[\s\-'.])(\p{L})/gu, (m, sep, ch) => sep + ch.toUpperCase())
}
