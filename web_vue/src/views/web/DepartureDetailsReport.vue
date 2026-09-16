<template>
  <div class="min-h-screen py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-center gap-3 mb-6">
        <img src="@/assets/images/logo.png" alt="ECSACONM" class="h-10 object-contain" />
        <div>
          <h1 class="text-lg font-bold text-gray-800">Travel &amp; Hotel Details</h1>
          <p class="text-xs text-gray-400">{{ report.event_name || 'ECSACONM Event' }} — live, updates automatically</p>
        </div>
        <button @click="load" :disabled="isLoading"
          class="ml-auto inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-white disabled:opacity-50"
          style="background-color: rgb(254,80,103);">
          Refresh
        </button>
      </div>

      <div v-if="errorMsg" class="p-4 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">{{ errorMsg }}</div>

      <template v-else>
        <div class="grid grid-cols-2 gap-3 mb-5">
          <div class="rounded-xl bg-white border border-gray-100 p-4 text-center shadow-sm">
            <div class="text-2xl font-bold" style="color: rgb(220,50,75);">{{ report.total_submitted || 0 }}</div>
            <div class="text-[11px] text-gray-500 mt-0.5">submitted</div>
          </div>
          <div class="rounded-xl bg-white border border-gray-100 p-4 text-center shadow-sm">
            <div class="text-2xl font-bold text-gray-700">{{ report.total_recipients || 0 }}</div>
            <div class="text-[11px] text-gray-500 mt-0.5">forms sent</div>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-left text-xs text-gray-500 bg-gray-50">
                  <th class="px-4 py-2.5 font-semibold">Name</th>
                  <th class="px-4 py-2.5 font-semibold">Email</th>
                  <th class="px-4 py-2.5 font-semibold">Hotel</th>
                  <th class="px-4 py-2.5 font-semibold">Departure date</th>
                  <th class="px-4 py-2.5 font-semibold">Departure time</th>
                  <th class="px-4 py-2.5 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="r in report.data" :key="r.id">
                  <td class="px-4 py-2.5">{{ r.name || '—' }}</td>
                  <td class="px-4 py-2.5 text-gray-500">{{ r.email }}</td>
                  <td class="px-4 py-2.5">{{ r.hotel || '—' }}</td>
                  <td class="px-4 py-2.5">{{ r.departure_date || '—' }}</td>
                  <td class="px-4 py-2.5">{{ r.departure_time || '—' }}</td>
                  <td class="px-4 py-2.5">
                    <span v-if="r.submitted" class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-green-100 text-green-700">submitted</span>
                    <span v-else class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">pending</span>
                  </td>
                </tr>
                <tr v-if="!isLoading && (!report.data || report.data.length === 0)">
                  <td colspan="6" class="px-4 py-8 text-center text-sm text-gray-400 italic">No submissions yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DepartureDetailsReportView',
  data() {
    return {
      isLoading: true,
      errorMsg: '',
      report: {},
      apiUrl: import.meta.env.VITE_API_URL,
      poll: null,
    }
  },
  mounted() {
    this.load()
    // Live-ish: refresh every 60s so a viewer watching this page over time
    // sees new submissions without manually reloading.
    this.poll = setInterval(this.load, 60000)
  },
  beforeUnmount() {
    if (this.poll) clearInterval(this.poll)
  },
  methods: {
    async load() {
      this.isLoading = true
      try {
        const token = this.$route.params.token
        const params = this.$route.query.event_id ? { event_id: this.$route.query.event_id } : {}
        const res = await axios.get(`${this.apiUrl}/departure-details/public-view/${token}`, { params })
        this.report = res.data || {}
        this.errorMsg = ''
      } catch (error) {
        this.errorMsg = error.response?.data?.detail || 'This link is invalid.'
      } finally {
        this.isLoading = false
      }
    },
  },
}
</script>
