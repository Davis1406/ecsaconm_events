// Shared badge date/title formatting — used by every badge preview
// (admin BadgeModal, My Badge on MyEvent/MyEvents) so the on-screen card and
// the downloaded PDF (api/routers/events.py::_render_badge_page) agree.

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

function ordinalSuffix(n) {
  const v = n % 100
  if (v >= 11 && v <= 13) return 'th'
  switch (n % 10) {
    case 1: return 'st'
    case 2: return 'nd'
    case 3: return 'rd'
    default: return 'th'
  }
}

function ordinal(n) {
  return `${n}${ordinalSuffix(n)}`
}

function escapeHtml(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

// Wraps ordinal suffixes ("17th", "8th") in <sup> for display — input is
// escaped first, so this is safe to use with v-html.
export function ordinalizeHtml(text) {
  if (!text) return ''
  return escapeHtml(text).replace(/(\d+)(st|nd|rd|th)\b/gi, '$1<sup>$2</sup>')
}

export function formatBadgeDateRange(startDate, endDate) {
  if (!startDate) return ''
  const start = new Date(startDate)
  const startDay = ordinal(start.getDate())
  if (!endDate) return `${startDay} ${MONTHS[start.getMonth()]}, ${start.getFullYear()}`
  const end = new Date(endDate)
  const endDay = ordinal(end.getDate())
  if (start.toDateString() === end.toDateString()) {
    return `${startDay} ${MONTHS[start.getMonth()]}, ${start.getFullYear()}`
  }
  if (start.getFullYear() === end.getFullYear() && start.getMonth() === end.getMonth()) {
    return `${startDay} – ${endDay} ${MONTHS[end.getMonth()]}, ${end.getFullYear()}`
  }
  return `${startDay} ${MONTHS[start.getMonth()]} – ${endDay} ${MONTHS[end.getMonth()]}, ${end.getFullYear()}`
}

// Same as formatBadgeDateRange() but with <sup> around ordinal suffixes —
// safe to use with v-html since it's built entirely from digits/month names.
export function formatBadgeDateRangeHtml(startDate, endDate) {
  return ordinalizeHtml(formatBadgeDateRange(startDate, endDate))
}

// Splits an event title like "17th ECSACONM Biennial Scientific Conference
// & 8th Quadrennial General Assembly" into the header pieces the badge
// design uses: a leading ordinal + org name, a subtitle line, and an
// optional pill line. Falls back gracefully for titles that don't follow
// that "<ordinal> <ORG> <rest>" pattern.
export function parseBadgeTitle(eventName) {
  const name = (eventName || '').trim()
  if (!name) return { ordinal: '', org: 'ECSACONM', subtitle: '', pill: '' }
  const m = name.match(/^(\d+(?:st|nd|rd|th))\s+(\S+)\s*(.*)$/i)
  if (!m) return { ordinal: '', org: name, subtitle: '', pill: '' }
  const [, ord, org, rest] = m
  const parts = rest.split(/\s*&\s*|\s+and\s+/i).map((s) => s.trim()).filter(Boolean)
  return {
    ordinal: ord,
    org,
    subtitle: parts[0] || '',
    pill: parts[1] || '',
  }
}

// Builds the `event` prop BadgeCard expects, from a raw event API object.
export function buildBadgeEvent(event) {
  const title = parseBadgeTitle(event?.event || event?.title || '')
  return {
    title,
    theme: event?.theme || '',
    location: event?.location || '',
    dateRangeHtml: formatBadgeDateRangeHtml(event?.start_date, event?.end_date),
  }
}
