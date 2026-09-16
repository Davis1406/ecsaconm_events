<template>
  <div class="min-h-screen flex items-start justify-center py-10 px-4">
    <div class="w-full max-w-lg">
      <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>

        <div class="flex flex-col items-center pt-6 pb-4 px-6 border-b border-gray-100">
          <img src="@/assets/images/logo.png" alt="ECSACONM" class="h-14 object-contain mb-3" />
          <h1 class="text-base font-bold text-gray-800 text-center leading-snug">Travel &amp; Hotel Details</h1>
        </div>

        <div class="flex items-center justify-center gap-2 px-6 py-3 text-xs font-medium text-white"
          style="background-color: rgb(254,80,103);">
          <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
          Help us plan your departure
        </div>

        <div class="p-6 space-y-5">
          <div v-if="errorMsg"
            class="flex items-start gap-2 p-4 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">
            <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {{ errorMsg }}
          </div>

          <div v-else-if="submitted" class="text-center space-y-4">
            <div class="inline-flex items-center justify-center h-16 w-16 rounded-full mx-auto"
              style="background-color: rgba(34,197,94,0.12);">
              <svg class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
            <p class="text-sm font-semibold text-gray-800">Thank you! Your travel details have been recorded.</p>
            <p class="text-xs text-gray-500">A confirmation email is on its way to you. You can submit this form again any time if anything changes.</p>
          </div>

          <form v-else @submit.prevent="submit" class="space-y-4">
            <p class="text-sm text-gray-600 text-center leading-relaxed">
              Please use the email address you registered with — we use it to confirm your registration.
            </p>

            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Name</label>
              <input v-model.trim="fields.name" type="text" required
                class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                style="--tw-ring-color: rgb(254,80,103);" placeholder="Your full name" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Email</label>
              <input v-model.trim="fields.email" type="email" required
                class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                style="--tw-ring-color: rgb(254,80,103);" placeholder="you@example.com" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Hotel</label>
              <input v-model.trim="fields.hotel" type="text" required
                class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                style="--tw-ring-color: rgb(254,80,103);" placeholder="e.g. Golden Tulip" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Departure date</label>
              <input v-model="fields.departure_date" type="date" required
                class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                style="--tw-ring-color: rgb(254,80,103);" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Departure time</label>
              <input v-model="fields.departure_time" type="time" required
                class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                style="--tw-ring-color: rgb(254,80,103);" />
            </div>

            <button type="submit" :disabled="isSubmitting"
              class="w-full py-3.5 rounded-xl text-white font-bold text-sm transition hover:opacity-90 disabled:opacity-50"
              style="background-color: rgb(254,80,103);">
              {{ isSubmitting ? 'Submitting…' : 'Submit Travel Details' }}
            </button>
          </form>
        </div>

        <div class="h-2" style="background-color: rgb(254,80,103);"></div>
      </div>

      <p class="text-center text-xs text-gray-400 mt-4">www.ecsaconm.org</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DepartureDetailsFormView',
  data() {
    return {
      isSubmitting: false,
      errorMsg: '',
      submitted: false,
      fields: { name: '', email: '', hotel: '', departure_date: '', departure_time: '' },
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },
  methods: {
    async submit() {
      this.isSubmitting = true
      this.errorMsg = ''
      try {
        const eventId = this.$route.query.event_id || 1
        await axios.post(`${this.apiUrl}/departure-details/submit`, { ...this.fields, event_id: Number(eventId) })
        this.submitted = true
      } catch (error) {
        this.errorMsg = error.response?.data?.detail || 'Failed to submit. Please try again.'
      } finally {
        this.isSubmitting = false
      }
    },
  },
}
</script>
