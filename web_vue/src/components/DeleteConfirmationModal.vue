<template>
  <div v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    @click.self="cancel">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-7 text-center">
      <!-- Icon -->
      <div class="h-14 w-14 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
        <svg class="w-7 h-7 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
      </div>
      <!-- Title -->
      <h3 class="text-lg font-bold text-gray-800 mb-2">Are you sure?</h3>
      <!-- Message -->
      <p class="text-sm text-gray-500 mb-6">{{ message }}</p>
      <!-- Buttons -->
      <div class="flex gap-3">
        <button @click="cancel"
          class="flex-1 py-2.5 rounded-xl font-semibold text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 transition">
          Cancel
        </button>
        <button @click="confirm"
          class="flex-1 py-2.5 rounded-xl font-semibold text-sm text-white bg-red-600 hover:bg-red-700 transition">
          Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    show: {
      type: Boolean,
      required: true,
    },
    message: {
      type: String,
      default: "Are you sure you want to delete this item?",
    },
  },
  methods: {
    confirm() { this.$emit("confirmed") },
    cancel() { this.$emit("canceled") },
  },
}
</script>
