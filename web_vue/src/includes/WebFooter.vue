<template>
  <footer class="bg-gray-900 text-gray-400 text-sm font-roboto">
    <!-- Gradient top border in ECSACONM red -->
    <div class="h-1" style="background: linear-gradient(90deg, rgb(254,80,103), rgb(220,50,75));"></div>
    <div class="max-w-7xl mx-auto px-6 py-5 flex flex-col sm:flex-row items-center justify-between gap-3">
      <span>&copy; {{ currentYear }} All Rights Reserved, ECSACONM</span>
      <span>Eastern, Central and Southern Africa College of Nursing and Midwifery</span>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'WebFooter',
  data() { return { currentYear: new Date().getFullYear() } }
}
</script>
