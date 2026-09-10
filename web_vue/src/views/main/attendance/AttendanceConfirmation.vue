<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'Attendance Confirmation'" />

    <!-- Event selector -->
    <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5">
      <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div class="flex-1">
          <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Select Event</label>
          <select v-model="selectedEventId" @change="loadAttendance"
            class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-700 focus:outline-none bg-white"
            style="border-color: #e5e7eb;">
            <option value="">— Choose an event —</option>
            <option v-for="event in events" :key="event.id" :value="event.id">{{ event.event }}</option>
          </select>
        </div>
        <div v-if="selectedEventId && hasAttendance" class="flex items-end gap-2 flex-wrap">
          <div class="bg-gray-50 rounded-xl px-4 py-2 text-center">
            <p class="text-xl font-bold text-gray-800">{{ stats.total }}</p>
            <p class="text-xs text-gray-400 uppercase tracking-wide">Registered</p>
          </div>
          <div class="rounded-xl px-4 py-2 text-center" style="background-color: rgba(254,80,103,0.08);">
            <p class="text-xl font-bold" style="color: rgb(254,80,103);">{{ stats.attended }}</p>
            <p class="text-xs uppercase tracking-wide" style="color: rgb(254,80,103);">Attended</p>
          </div>
          <div class="bg-yellow-50 rounded-xl px-4 py-2 text-center">
            <p class="text-xl font-bold text-yellow-700">{{ stats.total - stats.attended }}</p>
            <p class="text-xs text-yellow-600 uppercase tracking-wide">Absent</p>
          </div>
          <!-- Extract Excel -->
          <button @click="extractAttendance"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white transition hover:opacity-90"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export
          </button>
          <!-- Clear all attendance -->
          <button v-if="hasAttendance" @click="clearAllAttendance"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white transition hover:opacity-90"
            style="background-color: rgb(239,68,68);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Clear All
          </button>
        </div>
      </div>
    </div>

    <!-- No event selected -->
    <div v-if="!selectedEventId" class="bg-white rounded-2xl shadow-sm py-20 flex flex-col items-center justify-center text-center px-6">
      <div class="h-16 w-16 rounded-full flex items-center justify-center mb-4"
        style="background-color: rgba(254,80,103,0.08);">
        <svg class="w-8 h-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      </div>
      <p class="text-gray-500 text-base font-medium mb-1">Select an event to view attendance</p>
      <p class="text-gray-400 text-sm">Confirm attendance for each day of the event</p>
    </div>

    <!-- Spinner -->
    <div v-else-if="isLoading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <!-- Attendance table (only once someone has been scanned) -->
    <div v-else-if="hasAttendance" class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Search -->
      <div class="px-5 py-4 border-b border-gray-50 flex items-center gap-3">
        <input v-model="search" type="text" placeholder="Search participant…"
          class="flex-1 sm:max-w-xs border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
        <span class="text-xs text-gray-400 font-medium hidden sm:block">
          {{ filteredRegistrations.length }} of {{ scannedRegistrations.length }} scanned shown
        </span>
      </div>

      <!-- Day legend / select-all per day -->
      <div v-if="eventDays.length" class="px-5 pt-3 pb-2 flex flex-wrap gap-2 text-xs text-gray-500">
        <label v-for="d in eventDays" :key="d.date"
          class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-gray-50 cursor-pointer select-none">
          <input type="checkbox" :checked="dayAllSelected(d)" @change="toggleDayAll(d)" class="rounded border-gray-300" />
          {{ d.label }}
          <span class="text-gray-400">({{ dayCount(d) }})</span>
        </label>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead>
            <tr class="bg-gray-50 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
              <th class="px-3 py-3 text-left whitespace-nowrap">#</th>
              <th class="px-3 py-3 text-left whitespace-nowrap">Participant</th>
              <th class="px-3 py-3 text-left whitespace-nowrap">Category</th>
              <th v-for="d in eventDays" :key="d.date" class="px-3 py-3 text-center whitespace-nowrap">{{ d.label }}</th>
              <th class="px-3 py-3 text-center whitespace-nowrap">Days</th>
              <th class="px-3 py-3 text-center whitespace-nowrap"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(reg, idx) in filteredRegistrations" :key="reg.id"
              class="border-b border-gray-50 hover:bg-gray-50">
              <td class="px-3 py-3 text-gray-400 text-xs">{{ idx + 1 }}</td>
              <td class="px-3 py-3 font-semibold text-gray-800 whitespace-nowrap">
                {{ [reg.title, reg.firstname, reg.lastname].filter(Boolean).join(' ') || '—' }}
              </td>
              <td class="px-3 py-3 text-gray-600 text-xs whitespace-nowrap">{{ formatRole(reg.participation_role) }}</td>
              <td v-for="d in eventDays" :key="d.date" class="px-3 py-3 text-center">
                <input type="checkbox"
                  :checked="isPresent(reg, d.date)"
                  :disabled="toggling === reg.id + ':' + d.date"
                  @change="toggleDay(reg, d.date)"
                  class="rounded border-gray-300"
                  :title="d.label" />
              </td>
              <td class="px-3 py-3 text-center text-xs font-semibold text-gray-600">{{ daysAttended(reg) }}</td>
              <td class="px-3 py-3 text-center">
                <button v-if="daysAttended(reg) > 0" @click="clearParticipant(reg)"
                  title="Delete this participant's attendance records"
                  class="p-1.5 rounded-lg text-red-500 hover:bg-red-50 transition">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty -->
      <div v-if="filteredRegistrations.length === 0" class="py-16 text-center">
        <p class="text-gray-400 text-sm italic">No scanned participants match your search.</p>
      </div>
    </div>

    <!-- Blank until someone has been scanned -->
    <div v-else class="flex-1 min-h-[50vh]"></div>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast.show"
        class="fixed bottom-6 right-6 z-50 px-5 py-3 rounded-xl text-white text-sm font-semibold shadow-lg"
        :style="toast.type === 'success' ? 'background-color: rgb(34,197,94);' : 'background-color: rgb(239,68,68);'">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios'
import HeaderView from '@/includes/Header.vue'
import { fetchData } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'
import { exportToExcel } from '@/utils/exportToExcel'

const API_URL = import.meta.env.VITE_API_URL

const ROLE_MAP = {
  member_state: 'Member State', participant: 'Participant', other_africa: 'Other Africa',
  world: 'International', student: 'Student', exhibitor: 'Exhibitor', secretariat: 'Secretariat',
  delegate: 'Delegate', presenter: 'Presenter', speaker: 'Speaker',
  moh: 'Ministry of Health', moderator: 'Moderator', media: 'Media', usher: 'Usher',
}

export default {
  name: 'AttendanceConfirmationView',
  components: { HeaderView },
  data() {
    return {
      isLoading: false,
      events: [],
      selectedEventId: '',
      registrations: [],
      // registration_id -> { 'YYYY-MM-DD': attendanceId }
      attendanceMap: {},
      search: '',
      toggling: null,
      toast: { show: false, message: '', type: 'success' },
    }
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  computed: {
    selectedEvent() {
      return this.events.find(e => e.id == this.selectedEventId)
    },
    eventDays() {
      const ev = this.selectedEvent
      const days = []
      const seen = new Set()
      const pushDay = (dateStr) => {
        if (seen.has(dateStr)) return
        seen.add(dateStr)
        const d = new Date(dateStr + 'T00:00:00')
        days.push({
          date: dateStr,
          label: d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }),
        })
      }
      if (ev && ev.start_date && ev.end_date) {
        const start = new Date(String(ev.start_date).slice(0, 10) + 'T00:00:00')
        const end = new Date(String(ev.end_date).slice(0, 10) + 'T00:00:00')
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
          const y = d.getFullYear()
          const m = String(d.getMonth() + 1).padStart(2, '0')
          const dd = String(d.getDate()).padStart(2, '0')
          pushDay(`${y}-${m}-${dd}`)
        }
      }
      // Include any attendance dates outside the event range (e.g. pre-event
      // test scans) so their checkboxes are visible too.
      Object.values(this.attendanceMap).forEach(m => Object.keys(m).forEach(pushDay))
      return days.sort((a, b) => a.date.localeCompare(b.date))
    },
    scannedRegistrations() {
      return this.registrations.filter(r => this.daysAttended(r) > 0)
    },
    filteredRegistrations() {
      const base = this.scannedRegistrations
      if (!this.search.trim()) return base
      const term = this.search.toLowerCase()
      return base.filter(r => {
        const name = `${r.firstname || ''} ${r.lastname || ''}`.toLowerCase()
        return name.includes(term) || (r.email || '').toLowerCase().includes(term)
      })
    },
    stats() {
      return {
        total: this.registrations.length,
        attended: this.registrations.filter(r => this.daysAttended(r) > 0).length,
      }
    },
    hasAttendance() {
      return Object.keys(this.attendanceMap).some(regId =>
        Object.keys(this.attendanceMap[regId] || {}).length > 0)
    },
  },
  mounted() {
    this.loadEvents()
    this.pollTimer = setInterval(() => {
      // Keep the gate screen live: reload silently so QR scans appear without a
      // manual refresh and without flashing the loading spinner.
      if (this.selectedEventId && !this.isLoading && !this.toggling) {
        this.loadAttendance(true)
      }
    }, 10000)
  },
  beforeUnmount() {
    if (this.pollTimer) clearInterval(this.pollTimer)
  },
  methods: {
    async loadEvents() {
      try {
        const res = await fetchData('events', 0, 100, '')
        this.events = res.data || []
        if (this.events.length === 1) {
          this.selectedEventId = this.events[0].id
          this.loadAttendance()
        }
      } catch (e) {
        console.error('Error loading events:', e)
      }
    },

    async loadAttendance(silent = false) {
      if (!this.selectedEventId) { this.registrations = []; this.attendanceMap = {}; return }
      if (!silent) this.isLoading = true
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        const res = await api.get(`/registrations/?event_id=${this.selectedEventId}&skip=0&limit=1000`)
        const first = res.data
        let allRegs = first?.data || first || []
        const total = first?.total ?? allRegs.length
        // Fetch every page so the stats and scanned list cover ALL registrations,
        // not just the first page.
        for (let skip = 1000; skip < total; skip += 1000) {
          const page = await api.get(`/registrations/?event_id=${this.selectedEventId}&skip=${skip}&limit=1000`)
          allRegs = allRegs.concat(page.data?.data || [])
        }
        this.registrations = allRegs

        const map = {}
        try {
          const attRes = await api.get(`/events/${this.selectedEventId}/attendance`)
          const attList = attRes.data?.data || []
          attList.forEach(a => {
            const dateStr = String(a.attendance_date).slice(0, 10)
            if (!map[a.registration_id]) map[a.registration_id] = {}
            map[a.registration_id][dateStr] = a.id
          })
        } catch (e) { /* ignore */ }
        this.attendanceMap = map
      } catch (e) {
        console.error('Error loading attendance:', e)
        this.registrations = []
      } finally {
        if (!silent) this.isLoading = false
      }
    },

    isPresent(reg, dateStr) {
      return !!(this.attendanceMap[reg.id] && this.attendanceMap[reg.id][dateStr])
    },
    daysAttended(reg) {
      return Object.keys(this.attendanceMap[reg.id] || {}).length
    },
    dayCount(dateStr) {
      return this.registrations.filter(r => this.isPresent(r, dateStr)).length
    },
    dayAllSelected(dateStr) {
      const regs = this.filteredRegistrations
      return regs.length > 0 && regs.every(r => this.isPresent(r, dateStr))
    },
    async toggleDayAll(dateStr) {
      const regs = this.filteredRegistrations
      const target = this.dayAllSelected(dateStr)
        ? regs.filter(r => this.isPresent(r, dateStr))   // unmark all
        : regs.filter(r => !this.isPresent(r, dateStr))  // mark all
      for (const reg of target) {
        await this.toggleDay(reg, dateStr)
      }
    },
    async toggleDay(reg, dateStr) {
      const key = `${reg.id}:${dateStr}`
      if (this.toggling === key) return
      this.toggling = key
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        if (this.isPresent(reg, dateStr)) {
          const attId = this.attendanceMap[reg.id][dateStr]
          await api.delete(`/event_attendance/events/attendance/${attId}`)
          delete this.attendanceMap[reg.id][dateStr]
          this.attendanceMap = { ...this.attendanceMap }
          this.showToast(`${reg.firstname} removed from ${dateStr}`, 'success')
        } else {
          const res = await api.post(`/event_attendance/events/${this.selectedEventId}/attendance`, {
            registration_id: reg.id,
            event_id: parseInt(this.selectedEventId),
            attendance_date: dateStr,
          })
          if (!this.attendanceMap[reg.id]) this.attendanceMap[reg.id] = {}
          this.attendanceMap[reg.id][dateStr] = res.data?.id || Date.now()
          this.attendanceMap = { ...this.attendanceMap }
          this.showToast(`${reg.firstname} marked present for ${dateStr}`, 'success')
        }
      } catch (e) {
        this.showToast(e.response?.data?.detail || 'Failed to update attendance', 'error')
      } finally {
        this.toggling = null
      }
    },

    async clearParticipant(reg) {
      const name = [reg.firstname, reg.lastname].filter(Boolean).join(' ') || 'this participant'
      const dates = Object.keys(this.attendanceMap[reg.id] || {})
      if (!dates.length) return
      if (!window.confirm(`Delete all attendance records for ${name}?`)) return
      const token = this.authStore.accessToken
      const api = axios.create({ baseURL: API_URL })
      if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      this.toggling = 'clear'
      try {
        for (const dateStr of dates) {
          const attId = this.attendanceMap[reg.id][dateStr]
          await api.delete(`/event_attendance/events/attendance/${attId}`)
        }
        delete this.attendanceMap[reg.id]
        this.attendanceMap = { ...this.attendanceMap }
        this.showToast(`${name}'s attendance cleared`, 'success')
      } catch (e) {
        this.showToast(e.response?.data?.detail || 'Failed to clear attendance', 'error')
      } finally {
        this.toggling = null
      }
    },

    async clearAllAttendance() {
      if (!this.hasAttendance) return
      if (!window.confirm('Delete ALL attendance records for this event? This cannot be undone.')) return
      const token = this.authStore.accessToken
      const api = axios.create({ baseURL: API_URL })
      if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      this.toggling = 'clear-all'
      try {
        const res = await api.delete(`/event_attendance/events/${this.selectedEventId}/attendance`)
        this.attendanceMap = {}
        this.showToast(res.data?.detail || 'All attendance cleared', 'success')
      } catch (e) {
        this.showToast(e.response?.data?.detail || 'Failed to clear attendance', 'error')
      } finally {
        this.toggling = null
      }
    },

    extractAttendance() {
      const eventName = this.selectedEvent?.event || 'Event'
      const rows = this.registrations.map((r, i) => {
        const row = {
          '#': i + 1,
          'Title': r.title || '',
          'First Name': r.firstname || '',
          'Last Name': r.lastname || '',
          'Email': r.email || '',
          'Organisation': r.organisation || r.institution || '',
          'Country': r.country || '',
          'Category': this.formatRole(r.participation_role),
          'Paid': r.paid ? 'Yes' : 'No',
          'Days Attended': this.daysAttended(r),
        }
        this.eventDays.forEach(d => {
          row[`${d.label} (${d.date})`] = this.isPresent(r, d.date) ? 'Yes' : 'No'
        })
        return row
      })
      exportToExcel(rows, `Attendance_${eventName}`)
    },

    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => { this.toast.show = false }, 3500)
    },

    formatRole(role) {
      return ROLE_MAP[role] || role || '—'
    },
  },
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>