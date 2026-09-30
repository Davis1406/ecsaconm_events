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
      'Having fully supported the',
      eventName || DEFAULT_EVENT_NAME,
      'from 14th to 18th September 2026 at Golden Tulip Airport Hotel, Zanzibar',
    ],
  },
}

// Certificate of Appreciation — sent one at a time to specific officials from
// the "Certificates of Appreciation" card, not from the list tabs (so it's
// deliberately not in CERTIFICATE_TYPES). Same sheet, different heading, a
// designation line under the name, and no CPD badge.
export const APPRECIATION_TYPE = {
  label: 'Appreciation',
  cpd: 0,
  heading: 'OF APPRECIATION',
  subtitle: 'IS PROUDLY PRESENTED TO',
  body: (eventName) => [
    'in recognition of outstanding dedication and invaluable support to the College',
    `in hosting the ${eventName || DEFAULT_EVENT_NAME}, September 2026`,
  ],
}

// Who gets one. `cc` is prefilled in the send dialog and can be edited there.
const APPRECIATION_CC = ['lemmym@ecsahc.org', 'info@ecsaconm.org']
export const APPRECIATION_RECIPIENTS = [
  {
    key: 'appreciation-ps-mohz',
    name: 'Dr. Mngereza Mzee Miraji',
    designation: 'Permanent Secretary, Ministry of Health Zanzibar',
    email: 'ps@mohz.go.tz',
    cc: APPRECIATION_CC,
  },
  {
    key: 'appreciation-dnm-mohz',
    name: 'Mwanaaisha Juma Fakih',
    designation: 'Director of Nursing and Midwifery, Ministry of Health Zanzibar',
    email: 'ayshajuly@gmail.com',
    cc: APPRECIATION_CC,
  },
]

// Certificates of Appreciation for the drivers and driver-officers of the
// Ministry of Health Zanzibar. They have no emails on file, so these are only
// ever generated/downloaded (never emailed) — a Generate button on the
// Certificates page opens the print tab with every name. `designation` is the
// group heading shown under each name, exactly as supplied.
export const APPRECIATION_DRIVER_GROUPS = [
  {
    key: 'appreciation-drivers-afisa',
    designation: 'AFISA MUUGUZI WIZARA YA AFYA',
    names: [
      'JAFFAR KHAMIS LUOGA',
      'HASNUU SAID NYANGA',
      'SHAABAN FAKI OMAR',
    ],
  },
  {
    key: 'appreciation-drivers-madereva',
    designation: 'DEREVA WIZARA YA AFYA',
    names: [
      'RASHID OMAR HAMAD',
      'HAROUN FAHMI ALAWI',
      'SULEIMAN ALI ISHAU',
      'OMAR ALI OMAR',
      'RAJAB SULEIMAN JABU',
      'HASSAN HAJI HASSAN',
      'SULTAN SALUM MBARAK',
      'KASSIM RASHID KHAMIS',
      'AHMED ABDALLA MAULID',
      "MOH'D HASSAN MAKAME",
    ],
  },
]

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

// Every webfont the certificate actually paints with, as CSS font shorthands
// covering the family/weight each element asks for (the px size in a load()
// descriptor is only a hint — matching is by family/weight/style).
const CERT_FONT_FACES = [
  "400 172px 'Alex Brush'",      // "Certificate"
  "800 35px 'Montserrat'",       // college name
  "700 50px 'Montserrat'",       // "OF PARTICIPATION"
  "600 32px 'Montserrat'",       // "THE FOLLOWING AWARD IS GIVEN TO"
  "400 29px 'Montserrat'",       // body copy
  "700 29px 'Montserrat'",       // signature name
  "600 21px 'Montserrat'",       // "PRESIDENT"
  "600 63px 'Playfair Display'", // the recipient's name
]

// Force the certificate webfonts to be applied before anything rasterizes or
// prints the sheet. The certificate is laid out in absolute px, so a fallback
// font is not a cosmetic difference: the 172px "Certificate" sits only 12px
// above "OF PARTICIPATION" in box terms, and a fallback with taller metrics
// paints straight through it.
//
// document.fonts.load() resolves with an EMPTY array — and no error — when the
// @font-face rule isn't in the document yet, so awaiting it blindly can
// silently rasterize with fallback fonts. Hence the explicit result check.
// Returns true when every face really loaded.
export async function ensureCertificateFonts() {
  const loaded = await Promise.all(
    CERT_FONT_FACES.map(face => document.fonts.load(face).catch(() => []))
  )
  await document.fonts.ready
  const missing = CERT_FONT_FACES.filter((face, i) => !loaded[i].length)
  if (missing.length) {
    console.warn(
      '[certificates] webfonts did not load — the certificate will render with ' +
      'fallback fonts and the headings may overlap. Missing:', missing
    )
    return false
  }
  return true
}
