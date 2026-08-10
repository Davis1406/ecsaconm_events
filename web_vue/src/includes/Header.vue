<template>
  <header class="sticky top-0 z-20 flex items-center justify-between gap-4
                 px-8 h-16 bg-surface-container-lowest border-b border-outline-variant">

    <!-- Left: page title -->
    <div class="flex items-center gap-3 min-w-0">
      <!-- Mobile menu placeholder -->
      <button class="md:hidden p-1.5 -ml-1 rounded-lg text-on-surface-variant hover:bg-surface-container transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
      <svg class="hidden md:block w-5 h-5 text-on-surface-variant flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h8M4 18h16"/>
      </svg>
      <h1 class="text-lg font-bold text-on-surface truncate">{{ headerTitle }}</h1>
    </div>

    <!-- Right: actions + profile -->
    <div class="flex items-center gap-1.5">

      <!-- Theme toggle -->
      <ThemeToggle />

      <!-- Contacts icon -->
      <router-link :to="{ name: 'Contacts' }"
        class="p-2 rounded-full text-on-surface-variant hover:bg-surface-container transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      </router-link>

      <div class="w-px h-6 bg-outline-variant mx-1"></div>

      <!-- Profile dropdown -->
      <div class="relative">
        <button @click="dropdownOpen = !dropdownOpen"
          class="flex items-center gap-2.5 pl-2 pr-1.5 py-1.5 rounded-full hover:bg-surface-container transition-colors">
          <div class="flex flex-col items-end hidden sm:flex">
            <span class="text-sm font-semibold text-on-surface leading-tight">{{ fullName }}</span>
            <span class="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant">Admin</span>
          </div>
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            {{ initials }}
          </div>
          <svg class="w-4 h-4 text-on-surface-variant" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>

        <transition name="fade">
          <div v-if="dropdownOpen" v-click-outside="() => dropdownOpen = false"
            class="absolute right-0 mt-2 w-48 bg-surface-container-lowest rounded-xl shadow-lg border border-outline-variant z-50 py-1.5 overflow-hidden">
            <router-link :to="{ name: 'MyProfile', params: { id: loginUser.id } }"
              @click="dropdownOpen = false"
              class="flex items-center gap-3 px-4 py-2.5 text-sm text-on-surface hover:bg-surface-container transition-colors">
              <svg class="w-4 h-4 text-on-surface-variant" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              My Profile
            </router-link>
            <div class="h-px bg-outline-variant mx-3 my-1"></div>
            <button @click="logout"
              class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-cp-error hover:bg-error-container/20 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
              Sign Out
            </button>
          </div>
        </transition>
      </div>
    </div>
  </header>
</template>

<script>
import { useAuthStore } from '@/store/authStore'
import ThemeToggle from '@/components/ThemeToggle.vue'

export default {
  name: 'HeaderView',
  components: { ThemeToggle },
  props: {
    headerTitle: { type: String, default: '' },
  },
  data() {
    return { dropdownOpen: false }
  },
  directives: {
    clickOutside: {
      mounted(el, binding) {
        el._clickOutside = (e) => { if (!el.contains(e.target)) binding.value(e) }
        document.addEventListener('click', el._clickOutside, true)
      },
      unmounted(el) {
        document.removeEventListener('click', el._clickOutside, true)
      },
    },
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  computed: {
    loginUser() { return this.authStore.loginUser || {} },
    fullName()   { return this.loginUser.firstname || this.loginUser.email?.split('@')[0] || 'Admin' },
    initials() {
      const f = (this.loginUser.firstname || '').charAt(0).toUpperCase()
      const l = (this.loginUser.lastname  || '').charAt(0).toUpperCase()
      return (f + l) || 'AD'
    },
  },
  methods: {
    logout() {
      this.dropdownOpen = false
      this.authStore.reset()
      this.$router.push({ name: 'Login' })
    },
  },
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.12s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
