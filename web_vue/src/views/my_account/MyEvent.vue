<template>
  <div class="flex flex-col space-y-6 flex-1">
    <!-- Spinner -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <template v-else>
      <!-- ── Header Card ─────────────────────────────────────────────────── -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col md:flex-row justify-between gap-6">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl md:text-3xl font-bold leading-tight"
            style="color: rgb(254,80,103);"
            v-html="formatOrdinals(event.event || '')"></h1>
          <p v-if="event.theme" class="text-sm text-gray-500 mt-1">{{ event.theme }}</p>
          <p v-if="event.description" class="text-sm text-gray-600 mt-3 italic leading-relaxed whitespace-pre-line">
            {{ event.description }}
          </p>
        </div>
        <div class="text-sm text-gray-700 md:text-right space-y-1.5 md:min-w-[240px]">
          <p>
            <span class="font-semibold text-gray-800">Location:</span>
            {{ event.location || '—' }}<span v-if="event.country">, {{ event.country }}</span>
          </p>
          <p>
            <span class="font-semibold text-gray-800">Dates:</span>
            {{ formatDate(event.start_date) }} <span v-if="event.end_date">– {{ formatDate(event.end_date) }}</span>
          </p>
          <p v-if="event.org_unit">
            <span class="font-semibold text-gray-800">Organised by:</span>
            {{ event.org_unit }}
          </p>
        </div>
      </div>

      <!-- ── Registration Status Card ────────────────────────────────────── -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <!-- Not Registered -->
        <div v-if="userAccess === 'none'" class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-start gap-3">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style="background-color: rgba(254,80,103,0.12);">
              <svg class="w-5 h-5" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 class="text-base font-bold text-gray-800">You are not registered for this event</h2>
              <p class="text-sm text-gray-500 mt-0.5">Register now to participate and access event materials.</p>
            </div>
          </div>
          <router-link :to="{ name: 'EventRegister', params: { id: id } }"
            class="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-full text-white font-semibold text-sm transition hover:opacity-90 flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 4v16m8-8H4" />
            </svg>
            Register
          </router-link>
        </div>

        <!-- Registered, Unpaid -->
        <div v-else-if="userAccess === 'unpaid'" class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-start gap-3">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-yellow-100">
              <svg class="w-5 h-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 class="text-base font-bold text-gray-800">You are registered but payment is pending</h2>
              <div class="flex items-center gap-2 mt-1.5">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                  Registered
                </span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
                  Payment Pending
                </span>
              </div>
            </div>
          </div>
          <a href="https://ecsaconm.org/online-payment/" target="_blank" rel="noopener"
            class="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-full text-white font-semibold text-sm transition hover:opacity-90 flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            Pay Now
          </a>
        </div>

        <!-- Registered, Paid -->
        <div v-else class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-start gap-3">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-green-100">
              <svg class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 class="text-base font-bold text-gray-800">You are registered</h2>
              <div class="flex items-center gap-2 mt-1.5">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                  Registered
                </span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                  Paid
                </span>
              </div>
            </div>
          </div>
          <router-link :to="{ name: 'AccessEvent', params: { id: id } }"
            class="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-full text-white font-semibold text-sm transition hover:opacity-90 flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0" />
            </svg>
            My Badge
          </router-link>
        </div>
      </div>

      <!-- ── Documents Card ─────────────────────────────────────────────── -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-4">
          <div class="h-9 w-9 rounded-xl flex items-center justify-center"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4.5 h-4.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 class="text-lg font-bold text-gray-800">Documents</h2>
        </div>

        <!-- Visible docs -->
        <ul v-if="visibleDocuments.length" class="space-y-2">
          <li v-for="file in visibleDocuments" :key="file.id"
            class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition">
            <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style="background-color: rgb(254,80,103);">
              <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
            <a :href="`${apiUrl}/${file.path}`" target="_blank"
              class="text-sm font-semibold hover:underline" style="color: rgb(254,80,103);">
              {{ file.name }}
            </a>
          </li>
        </ul>

        <!-- Locked: not registered and there are restricted docs -->
        <div v-else-if="userAccess === 'none' && hasRestrictedDocuments"
          class="flex items-start gap-4 rounded-xl p-4 border-2 border-gray-200 bg-gray-50">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 bg-gray-300">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div>
            <p class="font-semibold text-gray-700 text-sm">Members Only</p>
            <p class="text-gray-500 text-sm mt-0.5">Register and complete payment to access event documents.</p>
          </div>
        </div>

        <!-- Empty -->
        <p v-else class="text-sm text-gray-400 italic">No documents available yet.</p>
      </div>

      <!-- ── Useful Links Card ──────────────────────────────────────────── -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <div class="flex items-center gap-3 mb-4">
          <div class="h-9 w-9 rounded-xl flex items-center justify-center"
            style="background-color: rgb(220,50,75);">
            <svg class="w-4.5 h-4.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <h2 class="text-lg font-bold text-gray-800">Useful Links</h2>
        </div>

        <!-- Visible links -->
        <ul v-if="visibleLinks.length" class="space-y-2">
          <li v-for="link in visibleLinks" :key="link.id"
            class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition">
            <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style="background-color: rgb(220,50,75);">
              <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </div>
            <a :href="link.link" target="_blank"
              class="text-sm font-semibold hover:underline" style="color: rgb(220,50,75);">
              {{ link.link_name || link.name }}
            </a>
          </li>
        </ul>

        <!-- Locked -->
        <div v-else-if="userAccess === 'none' && hasRestrictedLinks"
          class="flex items-start gap-4 rounded-xl p-4 border-2 border-gray-200 bg-gray-50">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 bg-gray-300">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div>
            <p class="font-semibold text-gray-700 text-sm">Members Only</p>
            <p class="text-gray-500 text-sm mt-0.5">Register and complete payment to access event links.</p>
          </div>
        </div>

        <!-- Empty -->
        <p v-else class="text-sm text-gray-400 italic">No links available yet.</p>
      </div>
    </template>
  </div>
</template>

<script>
import { fetchItem } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'MyEventView',
  setup() {
    const authStore = useAuthStore()
    return { currentUser: authStore.loginUser }
  },
  data() {
    return {
      isLoading: true,
      event: {},
      documents: [],
      links: [],
      userAccess: 'none',
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },
  computed: {
    id() {
      return this.$route.params.id
    },
    visibleDocuments() {
      return this.documents.filter(d => {
        const level = d.access_level || 'public'
        if (level === 'admin') return false
        if (level === 'public') return true
        if (level === 'registered') return this.userAccess !== 'none'
        return true
      })
    },
    visibleLinks() {
      return this.links.filter(l => {
        const level = l.access_level || 'public'
        if (level === 'admin') return false
        if (level === 'public') return true
        if (level === 'registered') return this.userAccess !== 'none'
        return true
      })
    },
    hasRestrictedDocuments() {
      return this.documents.some(d => (d.access_level || 'public') === 'registered')
    },
    hasRestrictedLinks() {
      return this.links.some(l => (l.access_level || 'public') === 'registered')
    },
  },
  async mounted() {
    try {
      const res = await fetchItem('events', this.id)
      this.event = res.event || {}
      this.documents = res.documents || []
      this.links = res.links || []
      this.userAccess = res.event?.user_access || 'none'
    } catch (e) {
      console.error('Error fetching event:', e)
    } finally {
      this.isLoading = false
    }
  },
  methods: {
    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    },
    formatOrdinals(text) {
      if (!text) return ''
      return text.replace(/(\d+)(st|nd|rd|th)\b/gi, (_, num, suffix) =>
        `${num}<sup style="font-size:0.55em;vertical-align:super;">${suffix}</sup>`)
    },
  }
}
</script>
