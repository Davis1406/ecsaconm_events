<template>
  <div class="flex items-center justify-between bg-white border-b border-gray-100 px-6 py-4 shadow-sm">
    <!-- Page title -->
    <div class="flex items-center gap-3">
      <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8M4 18h16" />
      </svg>
      <h1 class="text-xl font-bold text-gray-800">{{ headerTitle }}</h1>
    </div>

    <!-- Right actions -->
    <div class="flex items-center gap-4">
      <router-link :to="{ name: 'Contacts' }" class="text-gray-400 hover:text-gray-600 transition">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </router-link>

      <!-- Profile dropdown -->
      <div class="relative">
        <button @click="dropdownOpen = !dropdownOpen"
          class="flex items-center gap-2 text-sm font-semibold text-gray-700 hover:text-gray-900 transition">
          <div class="h-8 w-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
            style="background-color: rgb(254,80,103);">
            {{ initials }}
          </div>
          <span class="hidden sm:block">{{ fullName }}</span>
          <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <transition name="fade">
          <div v-if="dropdownOpen"
            class="absolute right-0 mt-2 w-44 bg-white rounded-xl shadow-lg border border-gray-100 z-50 py-1">
            <router-link :to="{ name: 'MyProfile', params: { id: loginUser.id } }"
              @click="dropdownOpen = false"
              class="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition">
              <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              My Profile
            </router-link>
            <button @click="logout"
              class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Sign Out
            </button>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'HeaderView',
  props: {
    headerTitle: { type: String, default: '' },
  },
  data() {
    return { dropdownOpen: false }
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  computed: {
    loginUser() {
      return this.authStore.loginUser || {}
    },
    fullName() {
      return this.loginUser.firstname || this.loginUser.email?.split('@')[0] || 'Admin'
    },
    initials() {
      const f = (this.loginUser.firstname || '').charAt(0).toUpperCase()
      const l = (this.loginUser.lastname || '').charAt(0).toUpperCase()
      return (f + l) || 'A'
    },
  },
  methods: {
    logout() {
      this.authStore.reset()
      this.$router.push({ name: 'Login' })
    },
  },
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
