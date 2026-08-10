<template>
  <button
    type="button"
    :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    class="p-2 rounded-full transition-colors"
    :class="variant === 'dark' ? 'text-on-surface-variant hover:bg-surface-container' : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-white/10'"
    @click="themeStore.toggle()">
    <!-- Sun (shown in dark mode → switch to light) -->
    <svg v-if="isDark" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
      <circle cx="12" cy="12" r="4" />
      <path stroke-linecap="round" d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
    </svg>
    <!-- Moon (shown in light mode → switch to dark) -->
    <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
      <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
    </svg>
  </button>
</template>

<script>
import { useThemeStore } from '@/store/themeStore'

export default {
  name: 'ThemeToggle',
  props: {
    variant: { type: String, default: 'surface', validator: v => ['surface', 'dark'].includes(v) },
  },
  setup() {
    const themeStore = useThemeStore()
    return { themeStore }
  },
  computed: {
    isDark() { return this.themeStore.isDark },
  },
}
</script>
