<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <WebHeader />
    <main class="flex-1">
      <router-view />
    </main>
    <WebFooter />
  </div>
</template>

<script>
import WebHeader from '@/includes/WebHeader.vue'
import WebFooter from '@/includes/WebFooter.vue'
export default {
  name: 'WebLayout',
  components: { WebHeader, WebFooter }
}
</script>
