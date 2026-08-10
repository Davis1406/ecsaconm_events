<template>
  <div v-if="authStore.isImpersonating"
    class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 px-4 py-2.5 text-white text-sm shadow-md"
    style="background: linear-gradient(90deg, rgb(254,80,103), rgb(220,50,75));">
    <div class="flex items-center gap-2 min-w-0">
      <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
      </svg>
      <p class="truncate">
        You are viewing as
        <span class="font-bold">{{ impersonatedName }}</span>
        <span class="opacity-80">({{ authStore.loginUser?.email }})</span>
      </p>
    </div>
    <button @click="stopImpersonating"
      class="self-start sm:self-auto flex-shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white text-xs font-bold transition hover:opacity-90"
      style="color: rgb(220,50,75);">
      <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      Stop Impersonating
    </button>
  </div>
</template>

<script>
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'ImpersonationBanner',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  computed: {
    impersonatedName() {
      const u = this.authStore.loginUser || {}
      return `${u.firstname || ''} ${u.lastname || ''}`.trim() || u.email || 'this user'
    },
  },
  methods: {
    async stopImpersonating() {
      // Lazy-import: a static import of apiService here would execute its
      // module-scope setAuthToken() before pinia is installed (layouts are
      // eagerly imported by the router), crashing the app at boot.
      const { setAuthToken } = await import('@/services/apiService')
      this.authStore.stopImpersonation()
      setAuthToken()
      this.$router.push({ name: 'Dashboard' })
    },
  },
}
</script>
