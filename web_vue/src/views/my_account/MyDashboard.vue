<template>
  <div class="flex flex-col space-y-6 flex-1">

    <!-- Welcome message -->
    <div>
      <h1 class="text-2xl font-bold text-gray-800">Welcome back, {{ firstName }}!</h1>
      <p class="text-sm text-gray-500 mt-1">Here's an overview of your account activity.</p>
    </div>

    <!-- Spinner -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <div v-else>
      <!-- Stat cards grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">

        <!-- Registered Events -->
        <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3">
          <div class="h-11 w-11 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgba(254,80,103,0.12);">
            <svg class="w-6 h-6" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-gray-800">{{ stats.registered }}</p>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mt-0.5">Registered Events</p>
          </div>
          <router-link :to="{ name: 'MyEvents' }" class="text-xs font-semibold hover:underline"
            style="color: rgb(254,80,103);">View all &rarr;</router-link>
        </div>

        <!-- Paid Events -->
        <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3">
          <div class="h-11 w-11 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgba(34,197,94,0.12);">
            <svg class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-gray-800">{{ stats.paid }}</p>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mt-0.5">Paid Events</p>
          </div>
          <span class="text-xs text-gray-400">Payment verified</span>
        </div>

        <!-- Unpaid Events -->
        <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3">
          <div class="h-11 w-11 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgba(234,179,8,0.12);">
            <svg class="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-gray-800">{{ stats.unpaid }}</p>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mt-0.5">Unpaid Events</p>
          </div>
          <span class="text-xs text-yellow-600 font-semibold" v-if="stats.unpaid > 0">Action needed</span>
          <span class="text-xs text-gray-400" v-else>All clear</span>
        </div>

        <!-- Profile completion -->
        <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3">
          <div class="h-11 w-11 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgba(220,50,75,0.12);">
            <svg class="w-6 h-6" style="color: rgb(220,50,75);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800 leading-tight">Your Profile</p>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mt-0.5">Keep it updated</p>
          </div>
          <router-link :to="{ name: 'MyAccountProfile' }" class="text-xs font-semibold hover:underline"
            style="color: rgb(220,50,75);">Update profile &rarr;</router-link>
        </div>

      </div>

      <!-- Quick Actions -->
      <div class="mt-6 bg-white rounded-2xl shadow-sm p-6">
        <h2 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-4">Quick Actions</h2>
        <div class="flex flex-wrap gap-3">
          <router-link :to="{ name: 'WebEvents' }"
            class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm text-white transition hover:opacity-90"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Browse Events
          </router-link>
          <router-link :to="{ name: 'MyAccountProfile' }"
            class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition border-2"
            style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Update My Profile
          </router-link>
          <router-link :to="{ name: 'MyEvents' }"
            class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 transition">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            View All My Events
          </router-link>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { fetchData } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'MyDashboard',
  data() {
    return {
      isLoading: true,
      stats: {
        registered: 0,
        paid: 0,
        unpaid: 0,
      },
    }
  },
  setup() {
    const authStore = useAuthStore()
    const user = authStore.loginUser
    return { user }
  },
  computed: {
    firstName() {
      return this.user?.firstname || 'there'
    },
  },
  mounted() {
    this.loadStats()
  },
  methods: {
    async loadStats() {
      try {
        const userId = this.user?.id
        const response = await fetchData('events/with-registration/' + userId, 0, 100, '')
        const raw = response?.data || response || []
        const list = Array.isArray(raw) ? raw : []
        const registered = list.filter(i => i.registered)
        this.stats.registered = registered.length
        this.stats.paid = registered.filter(i => i.registration_details?.paid).length
        this.stats.unpaid = registered.filter(i => !i.registration_details?.paid).length
      } catch (error) {
        console.error('Error loading stats:', error)
      } finally {
        this.isLoading = false
      }
    },
  },
}
</script>
