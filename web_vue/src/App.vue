<template>
  <div class="flex flex-col w-full min-h-screen font-roboto tracking-wide"
    style="color: var(--on-surface-variant); background-color: var(--surface);">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
}
</script>
