<template>
  <div class="bg-gray-50 min-h-screen">

    <!-- Page header -->
    <div class="max-w-4xl mx-auto px-4 pt-8 pb-2">
      <p class="text-xs font-semibold uppercase tracking-widest mb-1" style="color: rgb(254,80,103);">Event Payment</p>
      <h1 class="text-2xl font-bold text-gray-800">{{ eventName }}</h1>
      <p v-if="eventDates" class="text-sm text-gray-500 mt-0.5">{{ eventDates }}</p>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <!-- Already Paid -->
    <div v-else-if="alreadyPaid" class="max-w-xl mx-auto px-6 py-16 text-center">
      <div class="bg-white rounded-2xl shadow-sm p-10">
        <div class="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-6">
          <svg class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 mb-3">Payment Complete</h2>
        <p class="text-gray-500 mb-8">Your payment for this event has already been recorded and verified.</p>
        <router-link :to="{ name: 'MyDashboard' }"
          class="inline-flex items-center px-6 py-3 rounded-full text-white font-semibold transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          Go to My Account &rarr;
        </router-link>
      </div>
    </div>

    <!-- Payment Submitted success -->
    <div v-else-if="paymentSubmitted" class="max-w-xl mx-auto px-6 py-16 text-center">
      <div class="bg-white rounded-2xl shadow-sm p-10">
        <div class="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-6">
          <svg class="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 mb-3">Payment Submitted!</h2>
        <p class="text-gray-500 mb-8">The secretariat will verify your payment shortly. You will be notified once confirmed.</p>
        <router-link :to="{ name: 'MyDashboard' }"
          class="inline-flex items-center px-6 py-3 rounded-full text-white font-semibold transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          Go to My Account &rarr;
        </router-link>
      </div>
    </div>

    <!-- Payment form -->
    <div v-else class="max-w-4xl mx-auto px-4 py-10">
      <!-- Error banner -->
      <div v-if="formError" class="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
        {{ formError }}
      </div>

      <div class="grid sm:grid-cols-2 gap-6">

        <!-- Bank Details Card -->
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center gap-3"
            style="background-color: rgba(254,80,103,0.05);">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style="background-color: rgb(254,80,103);">
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <h2 class="text-base font-bold text-gray-800">Bank Transfer Details</h2>
          </div>
          <div class="px-6 py-5 space-y-3">
            <div v-for="detail in bankDetails" :key="detail.label"
              class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-0.5">{{ detail.label }}</p>
                <p class="text-sm font-semibold text-gray-800">{{ detail.value }}</p>
              </div>
            </div>
            <div class="mt-2 p-3 rounded-xl text-xs text-gray-500 bg-yellow-50 border border-yellow-100">
              Please use your full name and registration ID as the payment reference.
            </div>
          </div>
        </div>

        <!-- Payment Form Card -->
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style="background-color: rgb(220,50,75);">
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h2 class="text-base font-bold text-gray-800">Submit Payment Proof</h2>
          </div>
          <form @submit.prevent="submitPayment" class="px-6 py-5 space-y-4">
            <!-- Payment Method -->
            <div>
              <label class="field-label">Payment Method <span class="text-red-500">*</span></label>
              <div class="grid grid-cols-3 gap-2 mt-1">
                <label v-for="method in paymentMethods" :key="method.value"
                  class="flex flex-col items-center p-3 rounded-xl border-2 cursor-pointer text-center transition text-xs font-semibold"
                  :style="form.payment_method === method.value
                    ? 'border-color: rgb(254,80,103); background-color: rgba(254,80,103,0.06); color: rgb(254,80,103);'
                    : 'border-color: #e5e7eb; color: #6b7280;'">
                  <input type="radio" :value="method.value" v-model="form.payment_method" class="sr-only" />
                  <span>{{ method.label }}</span>
                </label>
              </div>
            </div>

            <!-- Amount -->
            <div>
              <label class="field-label">Amount (USD) <span class="text-red-500">*</span></label>
              <input v-model="form.payment_amount" type="number" step="0.01" placeholder="0.00" class="field-input" />
            </div>

            <!-- Proof upload -->
            <div>
              <label class="field-label">Upload Proof of Payment <span class="text-gray-400 font-normal">(optional)</span></label>
              <div class="mt-1 flex items-center gap-3">
                <label class="cursor-pointer flex items-center gap-2 px-4 py-2 rounded-xl border-2 border-dashed text-sm font-medium transition"
                  style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span>{{ proofFileName || 'Choose file' }}</span>
                  <input type="file" class="sr-only" @change="handleFileChange" accept="image/*,.pdf" />
                </label>
              </div>
            </div>

            <button type="submit" :disabled="isSubmitting"
              class="w-full py-3 rounded-xl text-white font-bold text-sm transition hover:opacity-90 disabled:opacity-50"
              style="background-color: rgb(254,80,103);">
              {{ isSubmitting ? 'Submitting...' : 'Submit Payment' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { fetchData } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'PaymentView',
  data() {
    return {
      isLoading: true,
      alreadyPaid: false,
      paymentSubmitted: false,
      formError: '',
      isSubmitting: false,
      eventName: '',
      eventDates: '',
      proofFile: null,
      proofFileName: '',
      form: {
        payment_method: 'bank_transfer',
        payment_amount: '',
      },
      paymentMethods: [
        { value: 'bank_transfer', label: 'Bank Transfer' },
        { value: 'mobile_money', label: 'Mobile Money' },
        { value: 'cash', label: 'Cash' },
      ],
      bankDetails: [
        { label: 'Bank', value: 'KCB Bank Tanzania Ltd – Arusha Branch' },
        { label: 'Account Name', value: 'ECSACONM' },
        { label: 'Account Number', value: '3391180919' },
        { label: 'SWIFT Code', value: 'KCBLTZTZ' },
        { label: 'Currency', value: 'USD' },
      ],
    }
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  async mounted() {
    this.eventId = this.$route.params.event_id
    this.registrationId = this.$route.params.registration_id
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
        // Load event (no auth)
        const eventRes = await api.get(`/events/${this.eventId}`)
        const ev = eventRes.data?.event || eventRes.data || {}
        this.eventName = ev.event || ev.title || 'Event'
        if (ev.start_date) {
          const start = new Date(ev.start_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
          const end = ev.end_date ? new Date(ev.end_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : ''
          this.eventDates = end ? `${start} – ${end}` : start
        }

        // Load registration (with auth)
        const token = this.authStore.accessToken
        const regRes = await api.get(`/events/registration/${this.registrationId}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        const reg = regRes.data?.registration || regRes.data || {}
        if (reg.paid) {
          this.alreadyPaid = true
        }
        if (reg.amount) {
          this.form.payment_amount = reg.amount
        }
      } catch (e) {
        console.error('Error loading payment data:', e)
      } finally {
        this.isLoading = false
      }
    },
    handleFileChange(e) {
      const file = e.target.files[0]
      if (file) {
        this.proofFile = file
        this.proofFileName = file.name
      }
    },
    async submitPayment() {
      this.formError = ''
      if (!this.form.payment_method) { this.formError = 'Please select a payment method.'; return }
      if (!this.form.payment_amount) { this.formError = 'Please enter the amount paid.'; return }

      this.isSubmitting = true
      try {
        const fd = new FormData()
        fd.append('registration_id', this.registrationId)
        fd.append('payment_method', this.form.payment_method)
        fd.append('payment_amount', this.form.payment_amount)
        if (this.proofFile) {
          fd.append('file', this.proofFile)
        }

        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        }
        await api.post(`/events/upload_payment_proof/${this.eventId}`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        this.paymentSubmitted = true
      } catch (e) {
        console.error('Payment submission error:', e)
        this.formError = e.response?.data?.detail || e.response?.data?.message || 'Failed to submit payment. Please try again.'
      } finally {
        this.isSubmitting = false
      }
    },
  },
}
</script>

<style scoped>
.field-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.375rem;
}
.field-input {
  display: block;
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #1f2937;
  background: #fff;
  outline: none;
  transition: border-color 0.15s;
}
.field-input:focus {
  border-color: rgb(254,80,103);
  box-shadow: 0 0 0 3px rgba(254,80,103,0.1);
}
</style>
