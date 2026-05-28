<template>
  <header class="bg-white shadow font-roboto sticky top-0 z-50">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 flex items-center justify-between h-16 sm:h-20">
      <!-- Logo + Title -->
      <router-link :to="{ name: 'Home' }" class="flex items-center gap-3">
        <img src="@/assets/images/logo.png" alt="ECSACONM" class="h-12 sm:h-16 object-contain" />
        <span class="font-bold text-base sm:text-2xl uppercase text-abbey tracking-wide">Events Portal</span>
      </router-link>

      <!-- Mobile toggle -->
      <button class="sm:hidden text-abbey" @click="toggleMenu">
        <svg v-if="!isMenuOpen" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
        <svg v-else class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>

      <!-- Desktop nav -->
      <nav class="hidden sm:flex items-center gap-6">
        <router-link :to="{ name: 'Home' }"
          class="text-sm font-medium text-abbey hover:text-bondi-blue-500 transition-colors pb-0.5"
          exact-active-class="text-bondi-blue-500 font-semibold border-b-2 border-bondi-blue-500">Home</router-link>
        <router-link :to="{ name: 'WebEvents' }"
          class="text-sm font-medium text-abbey hover:text-bondi-blue-500 transition-colors pb-0.5"
          active-class="text-bondi-blue-500 font-semibold border-b-2 border-bondi-blue-500">All Events</router-link>
        <router-link :to="{ name: 'Contact' }"
          class="text-sm font-medium text-abbey hover:text-bondi-blue-500 transition-colors pb-0.5"
          active-class="text-bondi-blue-500 font-semibold border-b-2 border-bondi-blue-500">Contact Us</router-link>
        <router-link v-if="isLoggedIn" :to="accountRoute"
          class="text-sm font-semibold px-5 py-2 rounded-full border-2 border-bondi-blue-500 text-bondi-blue-500 hover:bg-bondi-blue-500 hover:text-white transition">
          Event Portal
        </router-link>
        <router-link v-else :to="{ name: 'Login' }"
          class="text-sm font-semibold px-5 py-2 rounded-full border-2 border-bondi-blue-500 text-bondi-blue-500 hover:bg-bondi-blue-500 hover:text-white transition">
          Event Portal
        </router-link>
      </nav>
    </div>

    <!-- Mobile menu -->
    <transition name="fade">
      <div v-if="isMenuOpen" class="sm:hidden border-t border-gray-100 bg-white px-4 py-4 space-y-3">
        <router-link :to="{ name: 'Home' }" class="block text-abbey font-medium py-1 hover:text-bondi-blue-500" @click="closeMenu">Home</router-link>
        <router-link :to="{ name: 'WebEvents' }" class="block text-abbey font-medium py-1 hover:text-bondi-blue-500" @click="closeMenu">All Events</router-link>
        <router-link :to="{ name: 'Contact' }" class="block text-abbey font-medium py-1 hover:text-bondi-blue-500" @click="closeMenu">Contact Us</router-link>
        <router-link v-if="isLoggedIn" :to="accountRoute"
          class="inline-block text-sm font-semibold px-5 py-2 rounded-full border-2 border-bondi-blue-500 text-bondi-blue-500 mt-1" @click="closeMenu">
          Event Portal
        </router-link>
        <router-link v-else :to="{ name: 'Login' }"
          class="inline-block text-sm font-semibold px-5 py-2 rounded-full border-2 border-bondi-blue-500 text-bondi-blue-500 mt-1" @click="closeMenu">
          Event Portal
        </router-link>
      </div>
    </transition>
  </header>
</template>

<script>
import { useAuthStore } from '@/store/authStore'
export default {
  name: 'WebHeader',
  data() { return { isMenuOpen: false } },
  computed: {
    isLoggedIn() { return !!useAuthStore().accessToken },
    isAdmin() {
      const perms = useAuthStore().permissions || []
      return perms.some(p => p.permission_code === 'ADMIN_DASHBOARD')
    },
    accountRoute() {
      return this.isAdmin ? { name: 'Dashboard' } : { name: 'MyDashboard' }
    }
  },
  methods: {
    toggleMenu() { this.isMenuOpen = !this.isMenuOpen },
    closeMenu() { this.isMenuOpen = false }
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
