<template>
  <div class="min-h-screen flex items-start justify-center py-8 px-4"
    style="background: linear-gradient(135deg, rgba(254,80,103,0.06) 0%, #f9fafb 100%);">

    <!-- Loading -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-24 gap-4">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
      <p class="text-sm text-gray-400">Loading…</p>
    </div>

    <!-- Not found -->
    <div v-else-if="notFound" class="w-full max-w-sm">
      <div class="bg-white rounded-2xl shadow-xl overflow-hidden text-center">
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>
        <div class="p-8">
          <img src="@/assets/images/logo.png" alt="ECSACONM" class="h-12 object-contain mx-auto mb-5" />
          <div class="h-16 w-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <p class="font-bold text-gray-800 mb-1">Registration Not Found</p>
          <p class="text-sm text-gray-400">This QR code does not match any registration.</p>
        </div>
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>
      </div>
    </div>

    <!-- Main card -->
    <div v-else class="w-full max-w-sm space-y-3">

      <div class="bg-white rounded-2xl shadow-xl overflow-hidden">

        <!-- Pink top bar -->
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>

        <!-- Logo + event header -->
        <div class="flex flex-col items-center pt-6 pb-4 px-6 border-b border-gray-100">
          <img src="@/assets/images/logo.png" alt="ECSACONM" class="h-12 object-contain mb-3" />
          <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">QR Code Scanned</p>
          <h2 class="text-sm font-bold text-gray-800 text-center leading-snug">
            {{ scanData.event?.event || 'Event' }}
          </h2>
          <p v-if="scanData.event?.location" class="text-xs text-gray-400 mt-0.5">
            {{ scanData.event.location }}
          </p>
        </div>

        <!-- Live clock strip -->
        <div class="flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-medium text-white"
          style="background-color: rgb(254,80,103);">
          <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          {{ currentTime }}
        </div>

        <!-- Participant details -->
        <div class="px-6 py-5 border-b border-gray-100 text-center">
          <!-- Avatar initials -->
          <div class="h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-3 text-white text-xl font-bold"
            style="background-color: rgb(254,80,103);">
            {{ initials }}
          </div>
          <p class="text-lg font-bold text-gray-900 leading-tight">
            {{ [scanData.participant?.title, scanData.participant?.firstname, scanData.participant?.lastname].filter(Boolean).join(' ') || '—' }}
          </p>
          <p v-if="scanData.participant?.designation"
            class="text-xs font-semibold mt-0.5" style="color: rgb(254,80,103);">
            {{ scanData.participant.designation }}
          </p>
          <p v-if="scanData.participant?.organisation" class="text-sm text-gray-500 mt-1">
            {{ scanData.participant.organisation }}
          </p>
          <p v-if="scanData.participant?.country" class="text-xs text-gray-400 mt-0.5">
            {{ scanData.participant.country }}
          </p>

          <!-- Category + Payment chips -->
          <div class="flex items-center justify-center gap-2 mt-3 flex-wrap">
            <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-600">
              {{ formatRole(scanData.registration?.participation_role) }}
            </span>
            <span v-if="scanData.registration?.paid"
              class="px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
              ✓ Paid
            </span>
            <span v-else
              class="px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
              Unpaid
            </span>
          </div>
        </div>

        <!-- Attendance action -->
        <div class="px-6 py-5">

          <!-- Already registered today -->
          <div v-if="registeredToday"
            class="flex flex-col items-center gap-3 py-4 rounded-2xl text-center"
            style="background-color: rgba(34,197,94,0.08);">
            <div class="h-14 w-14 rounded-full bg-green-100 flex items-center justify-center">
              <svg class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
            <div>
              <p class="font-bold text-green-700 text-base">Already Registered</p>
              <p class="text-xs text-green-600 mt-0.5">Attendance recorded for today</p>
            </div>
          </div>

          <!-- Confirm button -->
          <div v-else>
            <!-- Success state -->
            <div v-if="attendanceSuccess"
              class="flex flex-col items-center gap-3 py-4 rounded-2xl text-center"
              style="background-color: rgba(34,197,94,0.08);">
              <div class="h-14 w-14 rounded-full bg-green-100 flex items-center justify-center">
                <svg class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <div>
                <p class="font-bold text-green-700 text-base">Attendance Confirmed!</p>
                <p class="text-xs text-green-600 mt-0.5">{{ currentTime }}</p>
              </div>
            </div>

            <!-- Error -->
            <div v-if="attendanceError"
              class="mb-3 flex items-start gap-2 p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">
              <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              {{ attendanceError }}
            </div>

            <!-- Button -->
            <button v-if="!attendanceSuccess"
              @click="confirmAttendance"
              :disabled="confirming"
              class="w-full py-4 rounded-2xl text-white font-bold text-base transition hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
              style="background-color: rgb(254,80,103);">
              <svg v-if="confirming" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              {{ confirming ? 'Registering…' : 'Register Attendance' }}
            </button>
          </div>
        </div>

        <!-- Attendance history -->
        <div v-if="scanData.attendance?.records?.length > 0"
          class="px-6 pb-5 border-t border-gray-100 pt-4">
          <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">
            Attendance History
            <span class="ml-1 font-normal normal-case">({{ scanData.attendance.total_days }} day{{ scanData.attendance.total_days !== 1 ? 's' : '' }})</span>
          </p>
          <div class="space-y-1.5">
            <div v-for="rec in scanData.attendance.records" :key="rec.id"
              class="flex items-center justify-between px-3 py-2 rounded-xl bg-green-50">
              <span class="text-sm text-gray-700 font-medium">{{ formatDate(rec.date) }}</span>
              <svg class="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Bottom bar -->
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>
      </div>

      <p class="text-center text-xs text-gray-400">www.ecsaconm.org</p>
    </div>

  </div>
</template>

<script>
import axios from 'axios'

// Use network IP when available so scanned QR codes work from phones on the same WiFi
const API_URL = import.meta.env.VITE_API_URL_NETWORK || import.meta.env.VITE_API_URL

const ROLE_MAP = {
  member_state: 'Member State', participant: 'Participant', other_africa: 'Other Africa',
  world: 'International', student: 'Student', exhibitor: 'Exhibitor',
  secretariat: 'Secretariat', delegate: 'Delegate', presenter: 'Presenter',
  speaker: 'Speaker', sponsor: 'Sponsor', moderator: 'Moderator', moh: 'Ministry of Health',
}

export default {
  name: 'UserEventStatusView',
  data() {
    return {
      registrationId: this.$route.params.userId,  // named userId in route but holds registration_id
      eventId: this.$route.params.eventId,
      scanData: {},
      isLoading: true,
      notFound: false,
      currentTime: '',
      clockTimer: null,
      confirming: false,
      attendanceSuccess: false,
      attendanceError: '',
      registeredToday: false,
    }
  },
  computed: {
    initials() {
      const p = this.scanData.participant || {}
      const f = (p.firstname || '').charAt(0).toUpperCase()
      const l = (p.lastname || '').charAt(0).toUpperCase()
      return f + l || '?'
    },
  },
  mounted() {
    this.loadScanData()
    this.startClock()
  },
  beforeUnmount() {
    if (this.clockTimer) clearInterval(this.clockTimer)
  },
  methods: {
    startClock() {
      const tick = () => {
        this.currentTime = new Date().toLocaleString('en-GB', {
          weekday: 'short', day: '2-digit', month: 'short',
          year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit',
        })
      }
      tick()
      this.clockTimer = setInterval(tick, 1000)
    },

    async loadScanData() {
      try {
        const res = await axios.get(`${API_URL}/events/scan/${this.registrationId}`)
        this.scanData = res.data
        this.registeredToday = res.data.attendance?.registered_today || false
      } catch (e) {
        if (e.response?.status === 404) {
          this.notFound = true
        }
      } finally {
        this.isLoading = false
      }
    },

    async confirmAttendance() {
      this.confirming = true
      this.attendanceError = ''
      try {
        await axios.post(`${API_URL}/event_attendance/events/${this.scanData.event?.id}/attendance`, {
          registration_id: parseInt(this.registrationId),
          event_id: parseInt(this.scanData.event?.id),
          attendance_date: new Date().toISOString(),
        })
        this.attendanceSuccess = true
        this.registeredToday = true
        // Refresh to get updated history
        setTimeout(() => this.loadScanData(), 1200)
      } catch (e) {
        const detail = e.response?.data?.detail || 'Failed to register attendance.'
        if (detail.toLowerCase().includes('already')) {
          this.registeredToday = true
        } else {
          this.attendanceError = detail
        }
      } finally {
        this.confirming = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('en-GB', {
        weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
      })
    },

    formatRole(role) {
      return ROLE_MAP[role] || role || '—'
    },
  },
}
</script>
