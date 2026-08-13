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
        <div v-if="failedCount" class="flex items-center gap-2">
          <button @click="confirmResendFailed" :disabled="resending"
            class="text-xs font-semibold text-white px-3 py-1.5 rounded-lg transition disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ resending ? 'Queuing…' : `Resend failed (${failedCount})` }}
          </button>
          <button @click="confirmClearFailed"
            class="text-xs font-semibold text-red-500 hover:text-red-700 border border-red-200 hover:border-red-400 px-3 py-1.5 rounded-lg transition">
            Clear failed logs ({{ failedCount }})
          </button>
        </div>
      </div>
    </div>

    <!-- Report -->
    <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-700">Email Report</h2>
        <p class="text-xs text-gray-400 mt-0.5">Breakdown across all logged emails</p>
      </div>
      <div v-if="statsLoading" class="flex justify-center py-10">
        <svg class="animate-spin h-6 w-6" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
      </div>
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6 p-5">
        <!-- By status -->
        <div>
          <h3 class="text-xs font-bold uppercase tracking-wide text-gray-400 mb-3">By Status</h3>
          <div v-if="!statusBars.length" class="text-xs text-gray-400 italic">No data yet.</div>
          <div v-for="row in statusBars" :key="row.key" class="mb-3 last:mb-0">
            <div class="flex justify-between text-xs mb-1">
              <span class="font-semibold text-gray-700 capitalize">{{ row.key }}</span>
              <span class="text-gray-500">{{ row.count }} ({{ row.pct }}%)</span>
            </div>
            <div class="h-2 rounded-full bg-gray-100 overflow-hidden">
              <div class="h-full rounded-full transition-all" :class="statusBarClass(row.key)" :style="{ width: row.barWidth + '%' }" />
            </div>
          </div>
        </div>

        <!-- By type -->
        <div>
          <h3 class="text-xs font-bold uppercase tracking-wide text-gray-400 mb-3">By Type</h3>
          <div v-if="!typeBars.length" class="text-xs text-gray-400 italic">No data yet.</div>
          <div v-for="row in typeBars" :key="row.key" class="mb-3 last:mb-0">
            <div class="flex justify-between text-xs mb-1">
              <span class="font-semibold text-gray-700">{{ typeLabel(row.key) }}</span>
              <span class="text-gray-500">{{ row.count }} ({{ row.pct }}%)</span>
            </div>
            <div class="h-2 rounded-full bg-gray-100 overflow-hidden">
              <div class="h-full rounded-full transition-all" :class="typeBarClass(row.key)" :style="{ width: row.barWidth + '%' }" />
            </div>
          </div>
        </div>

        <!-- Opened vs not opened -->
        <div>
          <h3 class="text-xs font-bold uppercase tracking-wide text-gray-400 mb-3">Opened (of Sent)</h3>
          <div v-if="!openedStats || openedStats.sent_total === 0" class="text-xs text-gray-400 italic">No sent emails yet.</div>
          <template v-else>
            <div class="flex items-baseline gap-2 mb-2">
              <span class="text-2xl font-bold" style="color: rgb(254,80,103);">{{ openedStats.openedPct }}%</span>
              <span class="text-xs text-gray-500">opened at least once</span>
            </div>
            <div class="h-2.5 rounded-full bg-gray-100 overflow-hidden flex">
              <div class="h-full" style="background-color: rgb(254,80,103);" :style="{ width: openedStats.openedPct + '%' }" />
            </div>
            <div class="flex justify-between text-xs text-gray-500 mt-2">
              <span><span class="font-semibold text-gray-700">{{ openedStats.opened }}</span> opened</span>
              <span><span class="font-semibold text-gray-700">{{ openedStats.not_opened }}</span> not opened</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Sent Emails table -->
    <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
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
              <th class="px-5 py-3 font-bold w-12">#</th>
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
            <tr v-for="(log, idx) in paginated" :key="log.id"
              class="border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition"
              :class="log.status === 'failed' ? 'bg-red-50 hover:bg-red-100' : ''"
              @click="openDetail(log)">
              <td class="px-5 py-3 text-gray-400 text-xs">{{ (currentPage - 1) * perPage + idx + 1 }}</td>
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
  test: 'Test',
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
  test: 'bg-pink-100 text-pink-700',
}

// Solid fill classes for report bars — same hue family as the badges above.
const TYPE_BAR_CLASSES = {
  general: 'bg-gray-400',
  new_account: 'bg-purple-500',
  password_reset_request: 'bg-yellow-500',
  password_reset: 'bg-yellow-500',
  account_verification: 'bg-blue-500',
  account_verification_request: 'bg-blue-500',
  organisation_verification_request: 'bg-indigo-500',
  organisation_approval_status: 'bg-indigo-500',
  reviewer_assignment: 'bg-teal-500',
  registration_reminder: 'bg-orange-500',
  payment_receipt: 'bg-green-500',
  test: 'bg-pink-500',
}

const STATUS_BAR_CLASSES = {
  sent: 'bg-green-500',
  failed: 'bg-red-500',
  pending: 'bg-yellow-500',
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
      stats: null,
      statsLoading: true,
      resending: false,
    }
  },
  computed: {
    typeOptions() {
      const present = new Set(this.logs.map(l => l.email_type))
      return Object.keys(TYPE_LABELS).filter(k => present.has(k))
    },
    failedCount() {
      return this.logs.filter(l => l.status === 'failed').length
    },
    statusBars() {
      if (!this.stats?.by_status?.length) return []
      const rows = [...this.stats.by_status].sort((a, b) => b.count - a.count)
      const total = rows.reduce((s, r) => s + r.count, 0)
      const max = Math.max(...rows.map(r => r.count), 1)
      return rows.map(r => ({
        key: r.status,
        count: r.count,
        pct: total ? Math.round((r.count / total) * 100) : 0,
        barWidth: Math.round((r.count / max) * 100),
      }))
    },
    typeBars() {
      if (!this.stats?.by_type?.length) return []
      const rows = [...this.stats.by_type].sort((a, b) => b.count - a.count)
      const total = rows.reduce((s, r) => s + r.count, 0)
      const max = Math.max(...rows.map(r => r.count), 1)
      return rows.map(r => ({
        key: r.email_type,
        count: r.count,
        pct: total ? Math.round((r.count / total) * 100) : 0,
        barWidth: Math.round((r.count / max) * 100),
      }))
    },
    openedStats() {
      const o = this.stats?.opened
      if (!o) return null
      return {
        ...o,
        openedPct: o.sent_total ? Math.round((o.opened / o.sent_total) * 100) : 0,
      }
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
    this.fetchStats()
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
    async fetchStats() {
      this.statsLoading = true
      try {
        const res = await axios.get(`${API_URL}/email-logs/stats/summary`, { headers: this.authHeaders() })
        this.stats = res.data
      } catch (e) {
        console.error('Failed to load email stats', e)
      } finally {
        this.statsLoading = false
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
    async confirmResendFailed() {
      const count = this.failedCount
      if (!count || !confirm(`Resend all ${count} failed email(s) now?`)) return
      this.resending = true
      try {
        const res = await axios.post(`${API_URL}/email-logs/failed/resend`, {}, { headers: this.authHeaders() })
        alert(res.data?.message || `Resending ${count} failed email(s).`)
        // Sends run in the background; refresh logs/stats shortly after so
        // new sent/failed entries show up once they land.
        setTimeout(() => { this.fetchLogs(); this.fetchStats() }, 4000)
      } catch (e) {
        console.error('Failed to resend failed logs', e)
        alert('Failed to queue resend. Please try again.')
      } finally {
        this.resending = false
      }
    },
    async confirmClearFailed() {
      const count = this.failedCount
      if (!count || !confirm(`Delete all ${count} failed log entr${count === 1 ? 'y' : 'ies'}? This cannot be undone.`)) return
      try {
        const res = await axios.delete(`${API_URL}/email-logs/failed/all`, { headers: this.authHeaders() })
        const deleted = res.data?.deleted ?? count
        this.logs = this.logs.filter(l => l.status !== 'failed')
        this.total = Math.max(0, this.total - deleted)
        this.closeDetail()
        this.fetchStats()
      } catch (e) {
        console.error('Failed to clear failed logs', e)
      }
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
    typeBarClass(t) { return TYPE_BAR_CLASSES[t] || 'bg-gray-400' },
    statusBarClass(s) { return STATUS_BAR_CLASSES[s] || 'bg-gray-400' },
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
