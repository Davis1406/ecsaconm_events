<template>
  <div class="flex h-screen overflow-hidden bg-gray-50 font-roboto">

    <!-- Sidebar — fixed height, internally scrollable -->
    <aside class="w-56 flex-shrink-0 bg-white shadow-sm h-screen flex flex-col hidden sm:flex">

      <!-- Logo -->
      <div class="flex items-center justify-center py-6 border-b border-gray-100 flex-shrink-0">
        <router-link :to="{ name: 'Dashboard' }">
          <img src="@/assets/images/logo.png" class="h-16 w-16 object-contain" alt="ECSACONM" />
        </router-link>
      </div>

      <!-- Nav — scrollable if many items -->
      <div class="flex-1 overflow-y-auto py-3 px-2">
        <SidebarView />
      </div>

      <!-- Bottom user info -->
      <div class="border-t border-gray-100 p-3 space-y-2 flex-shrink-0">
        <router-link :to="{ name: 'Home' }"
          class="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium text-gray-500 hover:bg-gray-50 transition">
          <svg class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>Back to Site</span>
        </router-link>
      </div>
    </aside>

    <!-- Main area — scrolls independently of the sidebar -->
    <div class="flex flex-col flex-1 min-w-0 h-screen overflow-y-auto">
      <div class="flex-1 p-6 max-w-7xl w-full mx-auto">
        <router-view />
      </div>
      <FooterView />
    </div>

  </div>
</template>

<script>
import SidebarView from '@/includes/Sidebar.vue'
import FooterView from '@/includes/Footer.vue'

export default {
  name: 'MainLayout',
  components: { SidebarView, FooterView },
}
</script>
