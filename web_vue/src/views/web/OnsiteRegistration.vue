<template>
  <div class="bg-gray-50 min-h-screen">

    <!-- Hero banner -->
    <section class="relative w-full overflow-hidden" style="min-height: 180px;">
      <div class="absolute inset-0" style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(180,30,55) 100%);"></div>
      <div class="relative z-10 max-w-2xl mx-auto px-6 py-10 text-white text-center">
        <p class="text-white/70 text-sm font-semibold mb-2 uppercase tracking-widest">Onsite Registration</p>
        <h1 class="text-2xl sm:text-3xl font-bold tracking-tight">{{ eventName }}</h1>
        <p class="text-white/85 text-sm mt-2">For Finance use — participants who have already paid at the venue</p>
      </div>
    </section>

    <!-- Success screen -->
    <div v-if="submitted" class="max-w-lg mx-auto px-6 py-14 text-center">
      <div class="bg-white rounded-2xl shadow-sm p-8">
        <div class="h-14 w-14 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-5">
          <svg class="w-7 h-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-800 mb-2">Registered</h2>
        <p class="text-gray-600 mb-1">{{ form.firstname }} {{ form.lastname }} has been registered and marked as paid.</p>
        <p v-if="generatedEmail" class="text-xs text-gray-400 mt-3">
          No email was given — a placeholder login (<span class="font-mono">{{ resultEmail }}</span>) was created.
        </p>
        <button @click="resetForm"
          class="mt-6 inline-flex items-center px-6 py-3 rounded-full text-white font-semibold transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          Register Another Participant
        </button>
      </div>
    </div>

    <!-- Form -->
    <div v-else class="max-w-lg mx-auto px-4 py-8">
      <div class="bg-white rounded-2xl shadow-sm p-6 sm:p-8 space-y-5">
        <div v-if="formError" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
          {{ formError }}
        </div>

        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="field-label">Title</label>
            <select v-model="form.title" class="field-input">
              <option value="">Select title</option>
              <option value="Mr.">Mr.</option>
              <option value="Mrs.">Mrs.</option>
              <option value="Ms.">Ms.</option>
              <option value="Dr.">Dr.</option>
              <option value="Prof.">Prof.</option>
            </select>
          </div>
          <div></div>
          <div>
            <label class="field-label">First Name <span class="text-red-500">*</span></label>
            <input v-model="form.firstname" type="text" placeholder="e.g. Jane" class="field-input" />
          </div>
          <div>
            <label class="field-label">Last Name <span class="text-red-500">*</span></label>
            <input v-model="form.lastname" type="text" placeholder="e.g. Doe" class="field-input" />
          </div>
          <div>
            <label class="field-label">Phone Number <span class="text-red-500">*</span></label>
            <input v-model="form.phone" type="tel" placeholder="+255700000000" class="field-input" />
          </div>
          <div>
            <label class="field-label">Email <span class="text-gray-400 font-normal">(optional)</span></label>
            <input v-model="form.email" type="email" placeholder="Leave blank if unavailable" class="field-input" />
          </div>
          <div class="sm:col-span-2">
            <label class="field-label">Organisation</label>
            <input v-model="form.organisation" type="text" placeholder="e.g. Ministry of Health" class="field-input" />
          </div>
          <div class="sm:col-span-2">
            <label class="field-label">Designation</label>
            <input v-model="form.designation" type="text" placeholder="e.g. Registered Nurse" class="field-input" />
          </div>
          <div class="sm:col-span-2">
            <label class="field-label">Country</label>
            <select v-model="form.country_id" class="field-input">
              <option value="">Select country</option>
              <option v-for="c in countries" :key="c.id" :value="c.id">{{ c.country }}</option>
            </select>
          </div>
        </div>

        <div>
          <label class="field-label">Category</label>
          <select v-model="form.participation_role" class="field-input">
            <option value="delegate">Delegate</option>
            <option value="secretariat">Secretariat</option>
            <option value="media">Media</option>
            <option value="exhibitor">Exhibitor</option>
            <option value="usher">Usher</option>
          </select>
        </div>

        <div class="rounded-xl border border-pink-100 bg-pink-50 p-3 text-xs text-gray-500">
          This registration is marked <strong>paid</strong> automatically — use only for participants Finance has
          confirmed payment for at the venue.
        </div>

        <button @click="submitForm" :disabled="isSubmitting"
          class="w-full inline-flex items-center justify-center px-6 py-3 rounded-xl text-white font-semibold transition hover:opacity-90 disabled:opacity-50"
          style="background-color: rgb(254,80,103);">
          {{ isSubmitting ? 'Registering…' : 'Register Participant' }}
        </button>
      </div>
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
        country_id: '',
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
        organisation: '', designation: '', country_id: '', participation_role: 'delegate',
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
