<template>
  <div class="flex flex-col sm:flex-row min-h-screen bg-gray-50">

    <!-- Mobile top bar -->
    <div class="sm:hidden flex items-center justify-between px-4 py-3 bg-white shadow-sm">
      <div class="flex items-center gap-3">
        <div class="h-9 w-9 rounded-full overflow-hidden flex-shrink-0">
          <img v-if="profilePictureUrl" :src="profilePictureUrl" class="h-full w-full object-cover" alt="Profile" />
          <div v-else class="h-full w-full flex items-center justify-center text-white font-bold text-sm"
            style="background-color: rgb(254,80,103);">
            {{ initials }}
          </div>
        </div>
        <div>
          <p class="text-sm font-semibold text-gray-800 leading-tight">{{ userName }}</p>
          <p class="text-xs text-gray-400">My Account</p>
        </div>
      </div>
      <button @click="sidebarOpen = !sidebarOpen"
        class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition">
        <svg v-if="!sidebarOpen" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Sidebar -->
    <aside
      class="sm:w-64 w-full flex-shrink-0 bg-white shadow-sm sm:min-h-screen sm:sticky sm:top-0 sm:block"
      :class="sidebarOpen ? 'block' : 'hidden sm:flex sm:flex-col'">

      <!-- Logo + user info (desktop) -->
      <div class="hidden sm:flex flex-col items-center py-8 px-6 border-b border-gray-100">
        <div class="h-16 w-16 rounded-full overflow-hidden ring-4 ring-white shadow-md mb-3 flex-shrink-0">
          <img v-if="profilePictureUrl" :src="profilePictureUrl" class="h-full w-full object-cover" alt="Profile" />
          <div v-else class="h-full w-full flex items-center justify-center text-white text-2xl font-bold"
            style="background-color: rgb(254,80,103);">
            {{ initials }}
          </div>
        </div>
        <p class="font-bold text-gray-800 text-base text-center leading-tight">{{ userName }}</p>
        <p class="text-xs text-gray-500 mt-0.5 text-center truncate max-w-full px-2">{{ userFullName }}</p>
        <p class="text-xs text-gray-400 mt-0.5 text-center truncate max-w-full px-2">{{ userEmail }}</p>
      </div>

      <!-- Nav links -->
      <nav class="py-4 px-3 space-y-0.5 flex-1">

        <router-link :to="{ name: 'MyDashboard' }"
          class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition"
          :class="$route.name === 'MyDashboard' ? 'text-white' : 'text-gray-600 hover:bg-gray-100'"
          :style="$route.name === 'MyDashboard' ? 'background-color: rgb(254,80,103);' : ''"
          @click="sidebarOpen = false">
          <HomeIcon class="h-5 w-5 flex-shrink-0" />
          <span>My Dashboard</span>
        </router-link>

        <router-link :to="{ name: 'MyEvents' }"
          class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition"
          :class="['MyEvents','MyEvent'].includes($route.name) ? 'text-white' : 'text-gray-600 hover:bg-gray-100'"
          :style="['MyEvents','MyEvent'].includes($route.name) ? 'background-color: rgb(254,80,103);' : ''"
          @click="sidebarOpen = false">
          <CalendarDaysIcon class="h-5 w-5 flex-shrink-0" />
          <span>My Events</span>
        </router-link>

        <router-link :to="{ name: 'MyAccountProfile' }"
          class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition"
          :class="$route.name === 'MyAccountProfile' ? 'text-white' : 'text-gray-600 hover:bg-gray-100'"
          :style="$route.name === 'MyAccountProfile' ? 'background-color: rgb(254,80,103);' : ''"
          @click="sidebarOpen = false">
          <UserIcon class="h-5 w-5 flex-shrink-0" />
          <span>My Profile</span>
        </router-link>

      </nav>

      <!-- Bottom links -->
      <div class="px-3 py-4 border-t border-gray-100 space-y-1">

        <!-- Events Admin button (only for admins) -->
        <router-link v-if="isAdmin" :to="{ name: 'Dashboard' }"
          class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          <svg class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <span>Events Admin</span>
        </router-link>

        <button @click="signOut"
          class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold text-red-500 hover:bg-red-50 transition">
          <svg class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Sign Out</span>
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 sm:p-8 p-4 space-y-6 min-w-0">
      <router-view></router-view>
    </main>

  </div>
</template>

<script>
import axios from 'axios'
import { HomeIcon, CalendarDaysIcon, UserIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'MyAccountLayout',
  components: {
    HomeIcon, CalendarDaysIcon, UserIcon,
  },
  data() {
    return {
      sidebarOpen: false,
      profilePictureUrl: null,
    }
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  computed: {
    user() {
      return this.authStore.loginUser || {}
    },
    userName() {
      const u = this.user
      return u.firstname || u.email?.split('@')[0] || 'User'
    },
    userFullName() {
      const u = this.user
      return `${u.firstname || ''} ${u.lastname || ''}`.trim() || u.email || 'User'
    },
    userEmail() {
      return this.user.email || ''
    },
    initials() {
      const f = (this.user.firstname || '').charAt(0).toUpperCase()
      const l = (this.user.lastname || '').charAt(0).toUpperCase()
      return f + l || '?'
    },
    isAdmin() {
      const raw = this.authStore.permissions || []
      const codes = raw.map(p => typeof p === 'string' ? p : p.permission_code)
      return codes.includes('ADMIN_DASHBOARD')
    },
  },
  mounted() {
    this.loadProfilePicture()
  },
  methods: {
    async loadProfilePicture() {
      try {
        const userId = this.authStore.loginUser?.id
        if (!userId) return
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const res = await api.get(`/users/${userId}`)
        const pic = res.data?.profile_picture?.profile_picture
        if (pic) {
          this.profilePictureUrl = `${API_URL}/${pic}`
        }
      } catch (e) {
        // Silently ignore — fall back to initials
      }
    },
    signOut() {
      this.authStore.reset()
      this.$router.push({ name: 'Home' })
    },
  },
}
</script>
