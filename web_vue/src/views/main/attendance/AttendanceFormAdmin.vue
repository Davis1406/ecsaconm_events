<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'Attendance Confirmation Form'" />

    <!-- Event selector -->
    <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5">
      <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div class="flex-1">
          <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Select Event</label>
          <select v-model="selectedEventId" @change="loadData"
            class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-700 focus:outline-none bg-white">
            <option value="">— Choose an event —</option>
            <option v-for="event in events" :key="event.id" :value="event.id">{{ event.event }}</option>
          </select>
        </div>
        <div v-if="selectedEventId" class="flex items-end gap-2 flex-wrap">
          <div class="bg-gray-50 rounded-xl px-4 py-2 text-center">
            <p class="text-xl font-bold text-gray-800">{{ recipients.length }}</p>
            <p class="text-xs text-gray-400 uppercase tracking-wide">Not Registered</p>
          </div>
          <div class="rounded-xl px-4 py-2 text-center" style="background-color: rgba(34,197,94,0.08);">
            <p class="text-xl font-bold text-green-600">{{ responseStats.attending }}</p>
            <p class="text-xs text-green-600 uppercase tracking-wide">Will Attend</p>
          </div>
          <div class="rounded-xl px-4 py-2 text-center" style="background-color: rgba(254,80,103,0.08);">
            <p class="text-xl font-bold" style="color: rgb(254,80,103);">{{ responseStats.notAttending }}</p>
            <p class="text-xs uppercase tracking-wide" style="color: rgb(254,80,103);">Won't Attend</p>
          </div>
          <div class="bg-yellow-50 rounded-xl px-4 py-2 text-center">
            <p class="text-xl font-bold text-yellow-700">{{ responseStats.pending }}</p>
            <p class="text-xs text-yellow-600 uppercase tracking-wide">No Response</p>
          </div>
          <button @click="exportResponses"
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
      <p v-if="selectedEventId" class="text-xs text-gray-400 mt-3">
        Email the attendance-confirmation form to presenters with accepted abstracts who haven't registered yet.
        Each presenter receives a personal link so we can plan the programme accordingly.
      </p>
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
      <p class="text-gray-500 text-base font-medium mb-1">Select an event to manage the form</p>
      <p class="text-gray-400 text-sm">Send the attendance confirmation form to unregistered presenters and track responses</p>
    </div>

    <!-- Spinner -->
    <div v-else-if="isLoading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <!-- Recipients -->
    <div v-else class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <div class="px-5 py-4 border-b border-gray-50 flex flex-wrap items-center gap-3">
        <input v-model="search" type="text" placeholder="Search presenter…"
          class="flex-1 sm:max-w-xs border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
        <button @click="sendForms('selected')"
          :disabled="isSending || recipients.length === 0 || selectedEmails.size === 0"
          class="px-4 py-2 text-white rounded-md text-sm font-medium disabled:opacity-50"
          style="background-color: rgb(254,80,103);">
          {{ sendStatus || `Send Form to Selected (${selectedEmails.size})` }}
        </button>
        <button @click="sendForms('all')"
          :disabled="isSending || recipients.length === 0"
          class="px-4 py-2 border rounded-md text-sm font-medium disabled:opacity-50"
          style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
          Send Form to All ({{ recipients.length }})
        </button>
        <button @click="loadData"
          :disabled="isLoading || isSending"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200 disabled:opacity-50">
          Refresh
        </button>
      </div>

      <div v-if="recipients.length === 0" class="py-16 text-center">
        <p class="text-gray-400 text-sm italic">All presenters have registered. No forms needed.</p>
      </div>

      <div v-else>
        <!-- Header -->
        <div class="hidden sm:grid grid-cols-12 gap-2 bg-gray-50 px-5 py-3 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
          <div class="col-span-1 flex items-center gap-2">
            <input type="checkbox" :checked="allSelected" @change="toggleSelectAll"
              class="w-4 h-4 rounded border-gray-300 cursor-pointer" style="accent-color: rgb(254,80,103);" />
          </div>
          <div class="col-span-3">Presenter</div>
          <div class="col-span-3">Email</div>
          <div class="col-span-3">Abstract</div>
          <div class="col-span-2 text-center">Response</div>
        </div>

        <!-- Rows -->
        <div v-for="(p, idx) in filteredRecipients" :key="p.email + idx"
          class="flex sm:grid sm:grid-cols-12 gap-2 items-center px-5 py-3.5 border-b border-gray-50 hover:bg-gray-50 transition text-sm">
          <div class="col-span-1 flex items-center gap-2">
            <input type="checkbox" :checked="selectedEmails.has(p.email)" @change="toggleSelect(p.email)"
              class="w-4 h-4 rounded border-gray-300 cursor-pointer" style="accent-color: rgb(254,80,103);" />
            <span class="text-gray-400 text-xs hidden sm:block">{{ idx + 1 }}</span>
          </div>
          <div class="col-span-3 font-semibold text-gray-800">
            {{ [p.firstname, p.lastname].filter(Boolean).join(' ') || '—' }}
          </div>
          <div class="col-span-3 text-gray-500 text-xs truncate">{{ p.email }}</div>
          <div class="col-span-3 text-gray-600 text-xs truncate">{{ p.abstract_title }}</div>
          <div class="col-span-2 flex justify-center">
            <span v-if="p.response === 'attending'"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M5 13l4 4L19 7"/></svg>
              Will attend
            </span>
            <span v-else-if="p.response === 'not_attending'"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-600">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M6 18L18 6M6 6l12 12"/></svg>
              Won't attend
            </span>
            <span v-else class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
              {{ p.sent ? 'Awaiting' : 'Not sent' }}
            </span>
          </div>
        </div>

        <div class="mt-3 px-5 py-3 flex justify-between items-center text-sm text-gray-500 border-t border-gray-50">
          <div>Total unregistered presenters: <strong>{{ recipients.length }}</strong></div>
          <div>Selected: <strong>{{ selectedEmails.size }}</strong></div>
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
import { useAuthStore } from '@/store/authStore'
import { exportToExcel } from '@/utils/exportToExcel'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'AttendanceFormAdminView',
  components: { HeaderView },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      isLoading: false,
      isSending: false,
      events: [],
      selectedEventId: '',
      recipients: [],
      search: '',
      selectedEmails: new Set(),
      sendStatus: '',
      toast: { show: false, message: '', type: 'success' },
    }
  },
  computed: {
    allSelected() {
      return this.recipients.length > 0 && this.recipients.every(p => this.selectedEmails.has(p.email))
    },
    filteredRecipients() {
      if (!this.search.trim()) return this.recipients
      const term = this.search.toLowerCase()
      return this.recipients.filter(p => {
        const name = `${p.firstname || ''} ${p.lastname || ''}`.toLowerCase()
        return name.includes(term) || (p.email || '').toLowerCase().includes(term)
      })
    },
    responseStats() {
      return {
        attending: this.recipients.filter(p => p.response === 'attending').length,
        notAttending: this.recipients.filter(p => p.response === 'not_attending').length,
        pending: this.recipients.filter(p => !p.response).length,
      }
    },
  },
  watch: {
    recipients() {
      this.selectedEmails = new Set()
    },
  },
  mounted() {
    this.loadEvents()
  },
  methods: {
    api() {
      const api = axios.create({ baseURL: API_URL })
      if (this.authStore.accessToken) {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.authStore.accessToken}`
      }
      return api
    },
    async loadEvents() {
      try {
        const res = await this.api().get('/events/?skip=0&limit=200')
        this.events = res.data?.data || res.data || []
        if (this.events.length === 1) {
          this.selectedEventId = this.events[0].id
          this.loadData()
        }
      } catch (e) {
        console.error('Error loading events:', e)
      }
    },
    async loadData() {
      if (!this.selectedEventId) { this.recipients = []; return }
      this.isLoading = true
      try {
        const res = await this.api().get(`/attendance-form/recipients`, {
          params: { event_id: this.selectedEventId },
        })
        this.recipients = res.data || []
      } catch (e) {
        this.showToast(e.response?.data?.detail || 'Failed to load recipients', 'error')
      } finally {
        this.isLoading = false
      }
    },
    toggleSelect(email) {
      if (this.selectedEmails.has(email)) {
        this.selectedEmails.delete(email)
      } else {
        this.selectedEmails.add(email)
      }
      this.selectedEmails = new Set(this.selectedEmails)
    },
    toggleSelectAll() {
      if (this.allSelected) {
        this.selectedEmails = new Set()
      } else {
        this.selectedEmails = new Set(this.recipients.map(p => p.email))
      }
    },
    async sendForms(mode) {
      const isAll = mode === 'all'
      const count = isAll ? this.recipients.length : this.selectedEmails.size
      if (count === 0) return

      this.isSending = true
      this.sendStatus = 'Sending...'
      try {
        const payload = { event_id: this.selectedEventId }
        if (!isAll) {
          payload.selected_emails = Array.from(this.selectedEmails)
        }
        const res = await this.api().post(`/attendance-form/send`, payload)
        const sent = res.data.sent || res.data.forms_sent || 0
        this.showToast(`Form emailed to ${sent} presenter(s)`, 'success')
        await this.loadData()
      } catch (e) {
        this.showToast(e.response?.data?.detail || 'Failed to send forms', 'error')
      } finally {
        this.isSending = false
        this.sendStatus = ''
      }
    },
    exportResponses() {
      const eventName = this.events.find(e => e.id == this.selectedEventId)?.event || 'Event'
      const rows = this.recipients.map((p, i) => ({
        '#': i + 1,
        'First Name': p.firstname || '',
        'Last Name': p.lastname || '',
        'Email': p.email || '',
        'Abstract': p.abstract_title || '',
        'Response': p.response === 'attending' ? 'Will attend'
          : p.response === 'not_attending' ? 'Will not attend'
          : (p.sent ? 'Awaiting response' : 'Not sent'),
        'Responded At': p.responded_at ? new Date(p.responded_at).toLocaleString() : '',
      }))
      exportToExcel(rows, `AttendanceForm_${eventName}`)
    },
    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => { this.toast.show = false }, 3500)
    },
  },
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>