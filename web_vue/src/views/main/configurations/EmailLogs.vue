<template>
  <div class="flex flex-col space-y-6 flex-1">
    <HeaderView :headerTitle="'Sent Emails'" />

    <!-- Toolbar -->
    <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
        <div class="flex-1 min-w-[160px]">
          <h2 class="text-sm font-bold text-gray-700">Sent Emails</h2>
          <p v-if="!isLoading" class="text-xs text-gray-400 mt-0.5">
            {{ total }} email{{ total !== 1 ? 's' : '' }} sent
          </p>
        </div>
        <button v-if="logs.length" @click="confirmClearAll"
          class="text-xs font-semibold text-red-500 hover:text-red-700 border border-red-200 hover:border-red-400 px-3 py-1.5 rounded-lg transition">
          Clear all logs
        </button>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
        <input v-model="search" type="text" placeholder="Search recipient or subject..."
          class="flex-1 min-w-[200px] px-4 py-2 bg-white border border-gray-200 shadow-sm placeholder-gray-400 focus:outline-none focus:border-pink-400 block rounded-xl text-sm" />
        <select v-model="filterType"
          class="px-3 py-2 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none">
          <option value="">All Types</option>
          <option v-for="t in typeOptions" :key="t" :value="t">{{ typeLabel(t) }}</option>
        </select>
        <select v-model="filterStatus"
          class="px-3 py-2 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none">
          <option value="">All Statuses</option>
          <option value="sent">Sent</option>
          <option value="failed">Failed</option>
          <option value="pending">Pending</option>
        </select>
      </div>

      <!-- Table -->
      <div v-if="isLoading" class="flex justify-center py-12">
        <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
      </div>
      <div v-else-if="filtered.length === 0" class="py-16 text-center text-sm text-gray-400">
        No emails found.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-gray-50 text-xs uppercase text-gray-500 border-b border-gray-100">
            <tr>
              <th class="px-5 py-3 font-bold">Sent At</th>
              <th class="px-5 py-3 font-bold">Recipient</th>
              <th class="px-5 py-3 font-bold">Subject</th>
              <th class="px-5 py-3 font-bold">Type</th>
              <th class="px-5 py-3 font-bold">Sent By</th>
              <th class="px-5 py-3 font-bold">Status</th>
              <th class="px-5 py-3 font-bold text-center">Opened</th>
              <th class="px-3 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in paginated" :key="log.id"
              class="border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition"
              :class="log.status === 'failed' ? 'bg-red-50 hover:bg-red-100' : ''"
              @click="openDetail(log)">
              <td class="px-5 py-3 whitespace-nowrap text-gray-500 text-xs">{{ fmtDate(log.sent_at) }}</td>
              <td class="px-5 py-3 font-medium text-gray-800">{{ log.recipient_email }}</td>
              <td class="px-5 py-3 max-w-xs truncate text-gray-700" :title="log.subject">{{ log.subject }}</td>
              <td class="px-5 py-3">
                <span class="px-2 py-0.5 rounded-full text-xs font-semibold" :class="typeClass(log.email_type)">
                  {{ typeLabel(log.email_type) }}
                </span>
              </td>
              <td class="px-5 py-3">
                <span v-if="log.sent_by" class="text-gray-700">{{ log.sent_by }}</span>
                <span v-else class="text-gray-400 italic">System</span>
              </td>
              <td class="px-5 py-3">
                <span class="px-2 py-0.5 rounded-full text-xs font-semibold" :class="statusClass(log.status)">
                  {{ log.status }}
                </span>
                <p v-if="log.error_message" class="text-xs text-red-500 mt-0.5 max-w-xs truncate" :title="log.error_message">
                  {{ log.error_message }}
                </p>
              </td>
              <td class="px-5 py-3 text-center">
                <span v-if="log.opened_count > 0" class="inline-flex items-center gap-1 text-xs font-semibold text-green-700">
                  <EyeIcon class="w-3.5 h-3.5" />
                  {{ log.opened_count }}×
                </span>
                <span v-else class="text-xs text-gray-300">—</span>
              </td>
              <td class="px-3 py-3" @click.stop>
                <button @click="deleteLog(log.id)" title="Delete log"
                  class="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition">
                  <TrashIcon class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="!isLoading && filtered.length > 0"
        class="flex items-center justify-between px-5 py-3.5 border-t border-gray-100 text-sm text-gray-600">
        <span>Page {{ currentPage }} of {{ totalPages }}</span>
        <div class="flex gap-2">
          <button :disabled="currentPage === 1" @click="currentPage--"
            class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 transition">
            Previous
          </button>
          <button :disabled="currentPage === totalPages" @click="currentPage++"
            class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 transition">
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Detail modal -->
    <Teleport to="body">
      <div v-if="selectedLog" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="closeDetail">
        <div class="absolute inset-0 bg-black/40" @click="closeDetail" />

        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
          <!-- Header -->
          <div class="flex items-start justify-between p-5 border-b border-gray-100 flex-shrink-0">
            <div class="min-w-0 flex-1 pr-4">
              <h2 class="text-base font-bold text-gray-800 truncate">{{ selectedLog.subject }}</h2>
              <p class="text-sm text-gray-500 mt-0.5">To: {{ selectedLog.recipient_email }}</p>
            </div>
            <button @click="closeDetail" class="flex-shrink-0 p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Meta strip -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 px-5 py-3 bg-gray-50 border-b border-gray-100 text-xs flex-shrink-0">
            <div>
              <p class="text-gray-400 uppercase font-bold tracking-wide mb-0.5">Sent at</p>
              <p class="text-gray-700">{{ fmtDate(selectedLog.sent_at) }}</p>
            </div>
            <div>
              <p class="text-gray-400 uppercase font-bold tracking-wide mb-0.5">Sent by</p>
              <p class="text-gray-700">{{ selectedLog.sent_by || 'System' }}</p>
            </div>
            <div>
              <p class="text-gray-400 uppercase font-bold tracking-wide mb-0.5">Status</p>
              <span class="px-2 py-0.5 rounded-full font-semibold" :class="statusClass(selectedLog.status)">{{ selectedLog.status }}</span>
            </div>
            <div>
              <p class="text-gray-400 uppercase font-bold tracking-wide mb-0.5">Opened</p>
              <div v-if="detailLoading" class="text-gray-400">…</div>
              <div v-else-if="detailLog && detailLog.opened_count > 0">
                <p class="text-green-700 font-semibold">{{ detailLog.opened_count }}× opened</p>
                <p class="text-gray-500">First: {{ fmtDate(detailLog.opened_at) }}</p>
              </div>
              <p v-else class="text-gray-400 italic">Not opened yet</p>
            </div>
          </div>

          <!-- Body -->
          <div class="flex-1 overflow-auto p-5">
            <div v-if="detailLoading" class="text-center text-gray-400 py-10">Loading email content…</div>
            <div v-else-if="detailLog && detailLog.body">
              <iframe ref="previewFrame" class="w-full border border-gray-200 rounded-xl bg-white" style="min-height: 480px;"
                sandbox="allow-same-origin" :srcdoc="detailLog.body" @load="resizeFrame" />
            </div>
            <div v-else-if="detailLog && !detailLog.body" class="text-center text-gray-400 py-10 italic">
              Email content not available for this log entry.
            </div>
            <div v-else-if="detailError" class="text-center text-red-500 py-10">Failed to load email content.</div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import axios from 'axios'
import HeaderView from '@/includes/Header.vue'
import { EyeIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL

const TYPE_LABELS = {
  general: 'General',
  new_account: 'New Account',
  password_reset_request: 'Password Reset Request',
  password_reset: 'Password Reset',
  account_verification: 'Account Verification',
  account_verification_request: 'Account Verification Request',
  organisation_verification_request: 'Organisation Verification Request',
  organisation_approval_status: 'Organisation Approval Status',
  reviewer_assignment: 'Reviewer Assignment',
  registration_reminder: 'Registration Reminder',
  payment_receipt: 'Payment Receipt',
}

const TYPE_CLASSES = {
  general: 'bg-gray-100 text-gray-600',
  new_account: 'bg-purple-100 text-purple-700',
  password_reset_request: 'bg-yellow-100 text-yellow-700',
  password_reset: 'bg-yellow-100 text-yellow-700',
  account_verification: 'bg-blue-100 text-blue-700',
  account_verification_request: 'bg-blue-100 text-blue-700',
  organisation_verification_request: 'bg-indigo-100 text-indigo-700',
  organisation_approval_status: 'bg-indigo-100 text-indigo-700',
  reviewer_assignment: 'bg-teal-100 text-teal-700',
  registration_reminder: 'bg-orange-100 text-orange-700',
  payment_receipt: 'bg-green-100 text-green-700',
}

export default {
  name: 'EmailLogsView',
  components: { HeaderView, EyeIcon, TrashIcon },
  setup() {
    const authStore = useAuthStore()
    return { accessToken: authStore.accessToken }
  },
  data() {
    return {
      logs: [],
      total: 0,
      isLoading: true,
      search: '',
      filterType: '',
      filterStatus: '',
      currentPage: 1,
      perPage: 50,
      selectedLog: null,
      detailLog: null,
      detailLoading: false,
      detailError: false,
    }
  },
  computed: {
    typeOptions() {
      const present = new Set(this.logs.map(l => l.email_type))
      return Object.keys(TYPE_LABELS).filter(k => present.has(k))
    },
    filtered() {
      const q = this.search.toLowerCase().trim()
      return this.logs.filter(l => {
        if (this.filterType && l.email_type !== this.filterType) return false
        if (this.filterStatus && l.status !== this.filterStatus) return false
        if (q && !`${l.recipient_email} ${l.subject} ${l.sent_by ?? ''}`.toLowerCase().includes(q)) return false
        return true
      })
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filtered.length / this.perPage))
    },
    paginated() {
      const start = (this.currentPage - 1) * this.perPage
      return this.filtered.slice(start, start + this.perPage)
    },
  },
  watch: {
    filtered() {
      if (this.currentPage > this.totalPages) this.currentPage = 1
    },
  },
  mounted() {
    this.fetchLogs()
  },
  methods: {
    authHeaders() {
      return { Authorization: `Bearer ${this.accessToken}` }
    },
    async fetchLogs() {
      this.isLoading = true
      try {
        const res = await axios.get(`${API_URL}/email-logs/?skip=0&limit=500`, { headers: this.authHeaders() })
        this.logs = res.data?.data || []
        this.total = res.data?.total || 0
      } catch (e) {
        console.error('Failed to load email logs', e)
      } finally {
        this.isLoading = false
      }
    },
    async deleteLog(id) {
      if (!confirm('Delete this log entry?')) return
      try {
        await axios.delete(`${API_URL}/email-logs/${id}`, { headers: this.authHeaders() })
        this.logs = this.logs.filter(l => l.id !== id)
        this.total = this.logs.length
        if (this.selectedLog?.id === id) this.closeDetail()
      } catch (e) {
        console.error('Failed to delete log', e)
      }
    },
    async confirmClearAll() {
      if (!confirm(`Delete all ${this.logs.length} log entries? This cannot be undone.`)) return
      const ids = [...this.logs.map(l => l.id)]
      for (const id of ids) {
        try { await axios.delete(`${API_URL}/email-logs/${id}`, { headers: this.authHeaders() }) } catch (_) { /* continue */ }
      }
      this.logs = []
      this.total = 0
      this.closeDetail()
    },
    async openDetail(log) {
      this.selectedLog = log
      this.detailLog = null
      this.detailError = false
      this.detailLoading = true
      try {
        const res = await axios.get(`${API_URL}/email-logs/${log.id}`, { headers: this.authHeaders() })
        this.detailLog = res.data
      } catch (e) {
        this.detailError = true
      } finally {
        this.detailLoading = false
        this.$nextTick(this.resizeFrame)
      }
    },
    closeDetail() {
      this.selectedLog = null
      this.detailLog = null
    },
    resizeFrame() {
      const frame = this.$refs.previewFrame
      if (!frame) return
      try {
        const h = frame.contentDocument?.body?.scrollHeight
        if (h) frame.style.height = `${h + 24}px`
      } catch (_) { /* cross-origin or not yet loaded */ }
    },
    fmtDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
      })
    },
    typeLabel(t) { return TYPE_LABELS[t] || t },
    typeClass(t) { return TYPE_CLASSES[t] || 'bg-gray-100 text-gray-600' },
    statusClass(s) {
      return {
        sent: 'bg-green-100 text-green-700',
        failed: 'bg-red-100 text-red-700',
        pending: 'bg-yellow-100 text-yellow-700',
      }[s] || 'bg-gray-100 text-gray-600'
    },
  },
}
</script>
