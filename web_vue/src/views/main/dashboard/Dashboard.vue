<template>
  <div class="flex flex-col space-y-6 flex-1">
    <HeaderView :headerTitle="headerTitle" />

    <!-- Spinner -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <div v-else>
      <!-- Stat cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">

        <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3">
          <div class="h-11 w-11 rounded-xl flex items-center justify-center"
            style="background-color: rgba(254,80,103,0.12);">
            <svg class="w-6 h-6" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-gray-800">{{ stats.events }}</p>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mt-0.5">Total Events</p>
          </div>
          <router-link :to="{ name: 'Events' }" class="text-xs font-semibold hover:underline"
            style="color: rgb(254,80,103);">Manage &rarr;</router-link>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3">
          <div class="h-11 w-11 rounded-xl flex items-center justify-center bg-blue-50">
            <svg class="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-gray-800">{{ stats.registrations }}</p>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mt-0.5">Registrations</p>
          </div>
          <router-link :to="{ name: 'Registrations' }" class="text-xs font-semibold text-blue-500 hover:underline">View all &rarr;</router-link>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3">
          <div class="h-11 w-11 rounded-xl flex items-center justify-center bg-green-50">
            <svg class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-gray-800">{{ stats.paid }}</p>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mt-0.5">Paid</p>
          </div>
          <span class="text-xs text-green-600 font-semibold">Payment verified</span>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3">
          <div class="h-11 w-11 rounded-xl flex items-center justify-center bg-yellow-50">
            <svg class="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-gray-800">{{ stats.unpaid }}</p>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mt-0.5">Pending Payment</p>
          </div>
          <span class="text-xs text-yellow-600 font-semibold" v-if="stats.unpaid > 0">Action needed</span>
          <span class="text-xs text-gray-400" v-else>All clear</span>
        </div>

      </div>

      <!-- Events table -->
      <div class="mt-6 bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="text-sm font-bold text-gray-700">Active Events</h2>
          <router-link :to="{ name: 'Events' }"
            class="text-xs font-semibold px-4 py-1.5 rounded-full text-white transition hover:opacity-90"
            style="background-color: rgb(254,80,103);">
            Manage Events
          </router-link>
        </div>

        <div v-if="events.length === 0" class="py-12 text-center text-gray-400 text-sm">
          No events found.
        </div>

        <div v-else>
          <div class="hidden sm:grid grid-cols-12 gap-2 bg-gray-50 px-5 py-3 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
            <div class="col-span-5">Event</div>
            <div class="col-span-2">Dates</div>
            <div class="col-span-2">Location</div>
            <div class="col-span-1">Status</div>
            <div class="col-span-2 text-right">Actions</div>
          </div>
          <div v-for="event in events" :key="event.id"
            class="grid sm:grid-cols-12 gap-2 items-center px-5 py-3.5 border-b border-gray-50 hover:bg-gray-50 transition text-sm">
            <div class="col-span-5">
              <p class="font-semibold text-gray-800 truncate">{{ event.event }}</p>
              <p class="text-xs text-gray-400 truncate">{{ event.theme }}</p>
            </div>
            <div class="col-span-2 text-gray-500 text-xs">
              <div>{{ formatDate(event.start_date) }}</div>
              <div v-if="event.end_date" class="text-gray-400">{{ formatDate(event.end_date) }}</div>
            </div>
            <div class="col-span-2 text-gray-500 text-xs truncate">{{ event.location || '—' }}</div>
            <div class="col-span-1">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
                :class="isUpcoming(event.start_date) ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                {{ isUpcoming(event.start_date) ? 'Upcoming' : 'Past' }}
              </span>
            </div>
            <div class="col-span-2 flex justify-end gap-2">
              <router-link :to="{ name: 'Event', params: { id: event.id } }"
                class="px-3 py-1 rounded-lg text-xs font-semibold border"
                style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
                View
              </router-link>
              <router-link :to="{ name: 'EditEvent', params: { id: event.id } }"
                class="px-3 py-1 rounded-lg text-xs font-semibold text-white"
                style="background-color: rgb(254,80,103);">
                Edit
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import { fetchData } from '@/services/apiService'

export default {
  name: 'DashboardView',
  components: { HeaderView },
  data() {
    return {
      headerTitle: 'Dashboard',
      isLoading: true,
      events: [],
      stats: {
        events: 0,
        registrations: 0,
        paid: 0,
        unpaid: 0,
      },
    }
  },
  mounted() {
    this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      try {
        const [eventsRes, regsRes] = await Promise.allSettled([
          fetchData('events', 0, 100, ''),
          fetchData('registrations', 0, 500, ''),
        ])

        if (eventsRes.status === 'fulfilled') {
          const data = eventsRes.value?.data || eventsRes.value || []
          this.events = Array.isArray(data) ? data : []
          this.stats.events = this.events.length
        }

        if (regsRes.status === 'fulfilled') {
          const regs = regsRes.value?.data || regsRes.value || []
          const list = Array.isArray(regs) ? regs : []
          this.stats.registrations = regsRes.value?.total || list.length
          this.stats.paid = list.filter(r => r.paid).length
          this.stats.unpaid = list.filter(r => !r.paid).length
        }
      } catch (e) {
        console.error('Dashboard load error:', e)
      } finally {
        this.isLoading = false
      }
    },
    formatDate(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
      })
    },
    isUpcoming(dateString) {
      if (!dateString) return false
      return new Date(dateString) >= new Date()
    },
  },
}
</script>
