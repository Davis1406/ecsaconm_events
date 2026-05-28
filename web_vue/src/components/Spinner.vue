<template>
  <div class="spinner">
    <div class="w-16 h-16 border-t-4 border-bondi-blue-500 border-solid rounded-full animate-spin"></div>
  </div>
</template>

<script>
export default {
  name: "SpinnerComponent",
};
</script>

<style scoped>
.spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
