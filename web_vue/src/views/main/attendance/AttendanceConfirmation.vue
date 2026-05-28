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
        <div v-if="selectedEventId" class="flex items-end gap-2 flex-wrap">
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
      <p class="text-gray-400 text-sm">Track confirmed attendance for each registered participant</p>
    </div>

    <!-- Spinner -->
    <div v-else-if="isLoading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <!-- Attendance table -->
    <div v-else class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Search -->
      <div class="px-5 py-4 border-b border-gray-50 flex items-center gap-3">
        <input v-model="search" type="text" placeholder="Search participant…"
          class="flex-1 sm:max-w-xs border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
        <span class="text-xs text-gray-400 font-medium hidden sm:block">
          {{ filteredRegistrations.length }} of {{ registrations.length }} shown
        </span>
      </div>

      <!-- Header -->
      <div class="hidden sm:grid grid-cols-12 gap-2 bg-gray-50 px-5 py-3 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
        <div class="col-span-1">#</div>
        <div class="col-span-3">Participant</div>
        <div class="col-span-3">Email</div>
        <div class="col-span-2">Category</div>
        <div class="col-span-2">Payment</div>
        <div class="col-span-1 text-right">Attended</div>
      </div>

      <!-- Empty -->
      <div v-if="filteredRegistrations.length === 0" class="py-16 text-center">
        <p class="text-gray-400 text-sm italic">No registrations found for this event.</p>
      </div>

      <!-- Rows -->
      <div v-for="(reg, idx) in filteredRegistrations" :key="reg.id"
        class="flex sm:grid sm:grid-cols-12 gap-2 items-center px-5 py-3.5 border-b border-gray-50 hover:bg-gray-50 transition text-sm"
        :class="reg.attended ? 'bg-green-50/30' : ''">
        <div class="col-span-1 text-gray-400 text-xs hidden sm:block">{{ idx + 1 }}</div>
        <div class="col-span-3 font-semibold text-gray-800">
          {{ [reg.title, reg.firstname, reg.lastname].filter(Boolean).join(' ') || '—' }}
        </div>
        <div class="col-span-3 text-gray-500 text-xs truncate">{{ reg.email || '—' }}</div>
        <div class="col-span-2 text-gray-600 text-xs">{{ formatRole(reg.participation_role) }}</div>
        <div class="col-span-2">
          <span v-if="reg.paid" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">Paid</span>
          <span v-else class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">Unpaid</span>
        </div>
        <div class="col-span-1 flex justify-end">
          <button @click="toggleAttendance(reg)"
            :disabled="toggling === reg.id"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none disabled:opacity-50"
            :style="reg.attended ? 'background-color: rgb(254,80,103);' : 'background-color: #d1d5db;'">
            <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform duration-200"
              :class="reg.attended ? 'translate-x-6' : 'translate-x-1'"></span>
          </button>
        </div>
      </div>
    </div>

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
  moh: 'Ministry of Health', moderator: 'Moderator',
}

export default {
  name: 'AttendanceConfirmationView',
  components: { HeaderView },
  data() {
    return {
      isLoading: false,
      events: [],
      selectedEventId: '',
      registrations: [],   // each reg has: ...fields, attended: bool, attendanceId: int|null
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
    filteredRegistrations() {
      if (!this.search.trim()) return this.registrations
      const term = this.search.toLowerCase()
      return this.registrations.filter(r => {
        const name = `${r.firstname || ''} ${r.lastname || ''}`.toLowerCase()
        return name.includes(term) || (r.email || '').toLowerCase().includes(term)
      })
    },
    stats() {
      return {
        total: this.registrations.length,
        attended: this.registrations.filter(r => r.attended).length,
      }
    },
  },
  mounted() {
    this.loadEvents()
  },
  methods: {
    async loadEvents() {
      try {
        const res = await fetchData('events', 0, 200, '')
        this.events = res.data || []
        // Auto-select if only one event exists
        if (this.events.length === 1) {
          this.selectedEventId = this.events[0].id
          this.loadAttendance()
        }
      } catch (e) {
        console.error('Error loading events:', e)
      }
    },

    async loadAttendance() {
      if (!this.selectedEventId) { this.registrations = []; return }
      this.isLoading = true
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        // Load registrations for this event
        const res = await api.get(`/registrations/?event_id=${this.selectedEventId}&skip=0&limit=500`)
        const rawRegs = res.data?.data || res.data || []

        // Load all attendance records; match by registration_id
        // Store both the boolean AND the attendance record ID (needed for delete/untoggle)
        let attendanceMap = {}   // registration_id → { attended: true, attendanceId: n }
        try {
          const regIds = new Set(rawRegs.map(r => r.id))
          const attRes = await api.get(`/event_attendance/events/attendance/?limit=10000`)
          const attList = attRes.data || []
          attList
            .filter(a => regIds.has(a.registration_id))
            .forEach(a => {
              // Keep the LATEST record per registration
              if (!attendanceMap[a.registration_id] || a.id > attendanceMap[a.registration_id].attendanceId) {
                attendanceMap[a.registration_id] = { attended: true, attendanceId: a.id }
              }
            })
        } catch (e) { /* ignore — attendance fetch failed */ }

        this.registrations = rawRegs.map(r => ({
          ...r,
          attended: !!attendanceMap[r.id]?.attended,
          attendanceId: attendanceMap[r.id]?.attendanceId || null,
        }))
      } catch (e) {
        console.error('Error loading attendance:', e)
        this.registrations = []
      } finally {
        this.isLoading = false
      }
    },

    async toggleAttendance(reg) {
      this.toggling = reg.id
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        if (!reg.attended) {
          // Mark as attended
          const res = await api.post(`/event_attendance/events/${this.selectedEventId}/attendance`, {
            registration_id: reg.id,
            event_id: parseInt(this.selectedEventId),
            attendance_date: new Date().toISOString(),
          })
          reg.attended = true
          reg.attendanceId = res.data?.id || null
          this.showToast(`${reg.firstname} marked as attended`, 'success')
        } else {
          // Remove attendance — DELETE the record
          if (reg.attendanceId) {
            await api.delete(`/event_attendance/events/attendance/${reg.attendanceId}`)
          }
          reg.attended = false
          reg.attendanceId = null
          this.showToast(`${reg.firstname} attendance removed`, 'success')
        }
      } catch (e) {
        this.showToast(e.response?.data?.detail || 'Failed to update attendance', 'error')
      } finally {
        this.toggling = null
      }
    },

    extractAttendance() {
      const eventName = this.events.find(e => e.id == this.selectedEventId)?.event || 'Event'
      const rows = this.registrations.map((r, i) => ({
        '#': i + 1,
        'Title': r.title || '',
        'First Name': r.firstname || '',
        'Last Name': r.lastname || '',
        'Email': r.email || '',
        'Organisation': r.organisation || r.institution || '',
        'Country': r.country || '',
        'Category': this.formatRole(r.participation_role),
        'Paid': r.paid ? 'Yes' : 'No',
        'Attended': r.attended ? 'Yes' : 'No',
      }))
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
