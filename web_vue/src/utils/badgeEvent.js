// Shared badge date-range / event formatting — used by every badge preview
// (admin BadgeModal, My Badge on MyEvent/MyEvents) so the on-screen card and
// the downloaded PDF (api/routers/events.py::_render_badge_page) agree.
export function formatBadgeDateRange(startDate, endDate) {
  if (!startDate) return ''
  const opts = { day: '2-digit', month: 'short', year: 'numeric' }
  const start = new Date(startDate)
  const startStr = start.toLocaleDateString('en-GB', opts)
  if (!endDate) return startStr
  const end = new Date(endDate)
  if (start.toDateString() === end.toDateString()) return startStr
  if (start.getFullYear() === end.getFullYear() && start.getMonth() === end.getMonth()) {
    const dayStr = start.toLocaleDateString('en-GB', { day: '2-digit' })
    const endStr = end.toLocaleDateString('en-GB', opts)
    return `${dayStr} – ${endStr}`
  }
  const endStr = end.toLocaleDateString('en-GB', opts)
  return `${startStr} – ${endStr}`
}

// Builds the `event` prop BadgeCard expects, from a raw event API object.
export function buildBadgeEvent(event) {
  return {
    title: event?.event || event?.title || 'ECSACONM',
    theme: event?.theme || '',
    location: event?.location || '',
    dateRange: formatBadgeDateRange(event?.start_date, event?.end_date),
  }
}
