<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100">
        <h3 class="font-bold text-gray-800">Onsite Registration</h3>
        <p class="text-xs text-gray-400 mt-0.5">{{ eventName }} — for participants who have already paid</p>
      </div>

      <!-- Success -->
      <div v-if="submitted" class="p-6 text-center">
        <div class="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
          <svg class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <p class="font-semibold text-gray-800">{{ form.firstname }} {{ form.lastname }} registered</p>
        <p v-if="generatedEmail" class="text-xs text-gray-400 mt-2">
          No email given — placeholder login created: <span class="font-mono">{{ resultEmail }}</span>
        </p>
        <button @click="resetForm"
          class="mt-4 px-4 py-2 rounded-lg text-sm font-medium text-white transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          Register Another
        </button>
      </div>

      <!-- Form -->
      <template v-else>
        <div class="p-5 space-y-4">
          <div class="grid sm:grid-cols-2 gap-4">
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Title</span>
              <input v-model="form.title" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">First name <span class="text-red-500">*</span></span>
              <input v-model="form.firstname" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Last name <span class="text-red-500">*</span></span>
              <input v-model="form.lastname" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Phone <span class="text-red-500">*</span></span>
              <input v-model="form.phone" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Email <span class="text-gray-400 font-normal">(optional)</span></span>
              <input v-model="form.email" type="email"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Designation</span>
              <input v-model="form.designation" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Organisation</span>
              <input v-model="form.organisation" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Country</span>
              <select v-model.number="form.country_id"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400">
                <option :value="null">—</option>
                <option v-for="c in countries" :key="c.id" :value="c.id">{{ c.country }}</option>
              </select>
            </label>
            <label class="block sm:col-span-2">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Category</span>
              <select v-model="form.participation_role"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400">
                <option value="delegate">Delegate</option>
                <option value="secretariat">Secretariat</option>
                <option value="media">Media</option>
                <option value="exhibitor">Exhibitor</option>
                <option value="usher">Usher</option>
              </select>
            </label>
          </div>

          <p v-if="formError" class="text-sm px-3 py-2 rounded-lg bg-red-50 text-red-600">{{ formError }}</p>
        </div>

        <div class="px-5 py-4 border-t border-gray-100 flex justify-end">
          <button @click="submitForm" :disabled="isSubmitting"
            class="px-4 py-2 rounded-lg text-sm font-medium text-white transition hover:opacity-90 disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ isSubmitting ? 'Registering…' : 'Register Participant' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'OnsiteRegistrationView',
  data() {
    return {
      eventId: null,
      eventName: 'Event',
      countries: [],
      isSubmitting: false,
      submitted: false,
      generatedEmail: false,
      resultEmail: '',
      formError: '',
      form: {
        title: '',
        firstname: '',
        lastname: '',
        phone: '',
        email: '',
        organisation: '',
        designation: '',
        country_id: null,
        participation_role: 'delegate',
      },
    }
  },
  async mounted() {
    this.eventId = this.$route.params.eventId
    await Promise.all([this.loadEvent(), this.loadCountries()])
  },
  methods: {
    async loadEvent() {
      try {
        const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
        const res = await api.get(`/events/${this.eventId}`)
        const ev = res.data?.event || res.data || {}
        this.eventName = ev.event || ev.title || 'Event'
      } catch (e) {
        console.error('Error loading event:', e)
      }
    },
    async loadCountries() {
      try {
        const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
        const res = await api.get('/countries?skip=0&limit=500')
        this.countries = res.data?.data || res.data || []
      } catch (e) {
        console.error('Error loading countries:', e)
      }
    },
    resetForm() {
      this.submitted = false
      this.generatedEmail = false
      this.resultEmail = ''
      this.formError = ''
      this.form = {
        title: '', firstname: '', lastname: '', phone: '', email: '',
        organisation: '', designation: '', country_id: null, participation_role: 'delegate',
      }
    },
    async submitForm() {
      this.formError = ''
      if (!this.form.firstname.trim()) { this.formError = 'First name is required.'; return }
      if (!this.form.lastname.trim()) { this.formError = 'Last name is required.'; return }
      if (!this.form.phone.trim()) { this.formError = 'Phone number is required.'; return }

      this.isSubmitting = true
      try {
        const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
        const payload = {
          firstname: this.form.firstname.trim(),
          lastname: this.form.lastname.trim(),
          phone: this.form.phone.trim(),
          email: this.form.email.trim() || null,
          title: this.form.title || null,
          designation: this.form.designation || null,
          organisation: this.form.organisation || null,
          country_id: this.form.country_id || null,
          participation_role: this.form.participation_role,
        }
        const res = await api.post(`/events/${this.eventId}/onsite_registration`, payload)
        this.generatedEmail = !!res.data?.generated_email
        this.resultEmail = res.data?.email || ''
        this.submitted = true
      } catch (e) {
        this.formError = e.response?.data?.detail || 'Registration failed. Please try again.'
      } finally {
        this.isSubmitting = false
      }
    },
  },
}
</script>
