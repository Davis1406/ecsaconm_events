<template>
  <div class="min-h-screen flex items-start justify-center py-10 px-4">
    <SpinnerComponent v-if="isLoading" />

    <div v-else class="w-full max-w-lg">

      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-xl overflow-hidden">

        <!-- Pink top bar -->
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>

        <!-- Logo header -->
        <div class="flex flex-col items-center pt-6 pb-4 px-6 border-b border-gray-100">
          <img src="@/assets/images/logo.png" alt="ECSACONM" class="h-14 object-contain mb-3" />
          <h1 class="text-base font-bold text-gray-800 text-center leading-snug">
            Attendance Confirmation
          </h1>
          <p v-if="form.event_name" class="text-xs text-gray-400 mt-1">{{ form.event_name }}</p>
        </div>

        <!-- Date strip -->
        <div class="flex items-center justify-center gap-2 px-6 py-3 text-xs font-medium text-white"
          style="background-color: rgb(254,80,103);">
          <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          Confirm your attendance
        </div>

        <!-- Form body -->
        <div class="p-6 space-y-5">

          <!-- Invalid / expired link -->
          <div v-if="errorMsg"
            class="flex items-start gap-2 p-4 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">
            <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {{ errorMsg }}
          </div>

          <!-- Already responded -->
          <div v-else-if="form.already_responded" class="text-center space-y-4">
            <div class="inline-flex items-center justify-center h-16 w-16 rounded-full mx-auto"
              :style="form.response === 'attending' ? 'background-color: rgba(34,197,94,0.12);' : 'background-color: rgba(239,68,68,0.12);'">
              <svg v-if="form.response === 'attending'" class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              <svg v-else class="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </div>
            <p class="text-sm font-semibold text-gray-800">
              {{ form.response === 'attending'
                ? 'Thank you! Please complete your registration and payment to confirm your availability for the event.'
                : 'Thank you for letting us know. We will plan the programme accordingly.' }}
            </p>
            <p v-if="form.response === 'attending'" class="text-xs text-gray-500">
              Register and pay at <a href="#/register" class="underline" style="color: rgb(254,80,103);">events.ecsaconm.org</a>.
              If you've already paid, email your proof of payment to info@ecsaconm.org and copy admission@cosecsa.org.
            </p>
            <p class="text-xs text-gray-400">Your response has already been recorded.</p>
          </div>

          <!-- Form -->
          <div v-else>
            <p class="text-sm text-gray-600 text-center leading-relaxed">
              Dear <strong>{{ form.firstname || 'Presenter' }}</strong>,
            </p>
            <p class="text-sm text-gray-600 text-center leading-relaxed mt-2">
              We noticed you haven't registered for abstract submission and presentation.
              Since you haven't registered, please confirm if you will not be able to attend,
              so that we can plan the programme accordingly.
            </p>

            <div class="space-y-3 mt-6">
              <button @click="submitResponse('not_attending')" :disabled="isSubmitting"
                class="w-full py-3.5 rounded-xl text-white font-bold text-sm transition hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                style="background-color: rgb(254,80,103);">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
                I will not be Attending
              </button>
              <button @click="submitResponse('attending')" :disabled="isSubmitting"
                class="w-full py-3.5 rounded-xl text-white font-bold text-sm transition hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                style="background-color: rgb(34,197,94);">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                I will still be attending
              </button>
            </div>
          </div>
        </div>

        <!-- Pink bottom bar -->
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>
      </div>

      <!-- Footer note -->
      <p class="text-center text-xs text-gray-400 mt-4">www.ecsaconm.org</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import SpinnerComponent from '@/components/Spinner.vue'

export default {
  name: 'AttendanceFormView',
  components: { SpinnerComponent },
  data() {
    return {
      isLoading: true,
      isSubmitting: false,
      errorMsg: '',
      form: {},
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },
  mounted() {
    this.loadForm()
  },
  methods: {
    async loadForm() {
      this.isLoading = true
      this.errorMsg = ''
      try {
        const token = this.$route.params.token
        const res = await axios.get(`${this.apiUrl}/attendance-form/form/${token}`)
        this.form = res.data || {}
      } catch (error) {
        this.errorMsg = error.response?.data?.detail || 'This link is invalid or has expired.'
      } finally {
        this.isLoading = false
      }
    },
    async submitResponse(response) {
      this.isSubmitting = true
      this.errorMsg = ''
      try {
        const token = this.$route.params.token
        const res = await axios.post(`${this.apiUrl}/attendance-form/form/${token}`, { response })
        this.form.already_responded = true
        this.form.response = res.data.response
      } catch (error) {
        this.errorMsg = error.response?.data?.detail || 'Failed to submit. Please try again.'
      } finally {
        this.isSubmitting = false
      }
    },
  },
}
</script>