<template>
  <div class="flex h-screen overflow-hidden bg-surface font-sans antialiased">

    <!-- ── Sidebar ────────────────────────────────────────────────────────── -->
    <aside class="hidden md:flex flex-col w-[260px] flex-shrink-0 h-full bg-surface-container-lowest border-r border-outline-variant z-10">
      <!-- Brand -->
      <div class="flex items-center gap-3 px-5 py-5 flex-shrink-0">
        <router-link :to="{ name: 'Dashboard' }" class="flex items-center gap-3 group">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-sm flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <img src="@/assets/images/logo.png" class="w-9 h-9 object-contain rounded-lg" alt="" />
          </div>
          <div>
            <p class="text-sm font-bold text-on-surface leading-tight">ECSACONM</p>
            <p class="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant">Admin Console</p>
          </div>
        </router-link>
      </div>

      <!-- Nav -->
      <div class="flex-1 overflow-y-auto px-3 pb-3">
        <SidebarView />
      </div>

      <!-- Bottom links -->
      <div class="px-3 pb-4 pt-3 border-t border-surface-container-high flex-shrink-0 space-y-0.5">
        <router-link :to="{ name: 'Home' }"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-on-surface-variant hover:bg-surface-container transition-colors">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Back to Site
        </router-link>
      </div>
    </aside>

    <!-- ── Main column ────────────────────────────────────────────────────── -->
    <div class="flex flex-col flex-1 min-w-0 h-screen overflow-hidden bg-surface">
      <!-- scrollable canvas — header is sticky inside this -->
      <div class="flex-1 overflow-y-auto">
        <router-view />
      </div>
    </div>

  </div>
</template>

<script>
import SidebarView from '@/includes/Sidebar.vue'

export default {
  name: 'MainLayout',
  components: { SidebarView },
}
</script>
