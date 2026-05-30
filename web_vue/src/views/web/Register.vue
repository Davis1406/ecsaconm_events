<template>
  <div class="bg-gray-50 min-h-screen">

    <!-- Hero Banner -->
    <section class="relative w-full overflow-hidden" style="min-height: 220px;">
      <div class="absolute inset-0" style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(180,30,55) 100%);"></div>
      <div class="relative z-10 max-w-3xl mx-auto px-6 py-12 text-white text-center">
        <p class="text-white/70 text-sm font-semibold mb-2 uppercase tracking-widest">Event Registration</p>
        <h1 class="text-3xl sm:text-4xl font-bold tracking-tight mb-3">{{ eventName }}</h1>
        <p v-if="eventDates" class="text-white/85 text-base">{{ eventDates }}</p>
        <p v-if="eventLocation" class="text-white/75 text-sm mt-1">{{ eventLocation }}</p>
      </div>
    </section>

    <!-- Success screen -->
    <div v-if="submitted" class="max-w-xl mx-auto px-6 py-16 text-center">
      <div class="bg-white rounded-2xl shadow-sm p-10">
        <div class="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-6">
          <svg class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 mb-3">Registration Successful!</h2>
        <p class="text-gray-600 mb-2">
          You have been registered for <strong>{{ eventName }}</strong>.
        </p>
        <p class="text-gray-600 mb-5">
          Your login credentials have been sent to your email address.
        </p>
        <ol class="text-left text-gray-600 text-sm space-y-3 mb-7 bg-gray-50 rounded-xl p-5">
          <li class="flex items-start gap-3">
            <span class="flex-shrink-0 h-5 w-5 rounded-full text-white text-xs flex items-center justify-center font-bold mt-0.5"
              style="background-color: rgb(254,80,103);">1</span>
            <span>Go to the <a href="https://ecsaconm.org/online-payment/" target="_blank"
              class="font-semibold underline" style="color: rgb(254,80,103);">payment page</a> to complete your conference fee payment.</span>
          </li>
          <li class="flex items-start gap-3">
            <span class="flex-shrink-0 h-5 w-5 rounded-full text-white text-xs flex items-center justify-center font-bold mt-0.5"
              style="background-color: rgb(254,80,103);">2</span>
            <span>Log in to the portal using the credentials sent to your email.</span>
          </li>
          <li class="flex items-start gap-3">
            <span class="flex-shrink-0 h-5 w-5 rounded-full text-white text-xs flex items-center justify-center font-bold mt-0.5"
              style="background-color: rgb(254,80,103);">3</span>
            <span>Upload your proof of payment from your account dashboard.</span>
          </li>
        </ol>
        <div class="flex flex-wrap justify-center gap-3">
          <a href="https://ecsaconm.org/online-payment/" target="_blank"
            class="inline-flex items-center px-6 py-3 rounded-full text-white font-semibold transition hover:opacity-90"
            style="background-color: rgb(254,80,103);">
            Go to Payment Page &rarr;
          </a>
          <router-link :to="{ name: 'Login' }"
            class="inline-flex items-center px-6 py-3 rounded-full font-semibold border-2 transition hover:bg-gray-50"
            style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
            Login to Portal
          </router-link>
        </div>
      </div>
    </div>

    <!-- Multi-step form -->
    <div v-else class="max-w-2xl mx-auto px-4 py-10">

      <!-- Step indicator -->
      <div class="flex items-center justify-center mb-8 select-none">
        <template v-for="(stepLabel, idx) in stepLabels" :key="idx">
          <div class="flex flex-col items-center">
            <div class="h-9 w-9 rounded-full flex items-center justify-center font-bold text-sm transition-all"
              :style="idx <= currentStep
                ? 'background-color: rgb(254,80,103); color: #fff;'
                : 'background-color: #e5e7eb; color: #6b7280;'">
              {{ idx + 1 }}
            </div>
            <span class="mt-1 text-xs font-medium hidden sm:block"
              :style="idx <= currentStep ? 'color: rgb(254,80,103);' : 'color: #9ca3af;'">
              {{ stepLabel }}
            </span>
          </div>
          <div v-if="idx < stepLabels.length - 1" class="flex-1 h-0.5 mx-2 mb-5"
            :style="idx < currentStep ? 'background-color: rgb(254,80,103);' : 'background-color: #e5e7eb;'"></div>
        </template>
      </div>

      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <!-- Error banner -->
        <div v-if="formError" class="mx-6 mt-6 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
          {{ formError }}
        </div>

        <transition name="slide-fade" mode="out-in">

          <!-- Step 0: Personal -->
          <div v-if="currentStep === 0" key="step0" class="p-6 sm:p-8 space-y-5">
            <h2 class="text-lg font-bold text-gray-800 mb-1">Personal Details</h2>
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
                  <option value="Sr.">Sr.</option>
                </select>
              </div>
              <div>
                <label class="field-label">Gender</label>
                <select v-model="form.gender" class="field-input">
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>
              <div>
                <label class="field-label">First Name <span class="text-red-500">*</span></label>
                <input v-model="form.firstname" type="text" placeholder="e.g. Jane" class="field-input" />
              </div>
              <div>
                <label class="field-label">Middle Name</label>
                <input v-model="form.middlename" type="text" placeholder="Optional" class="field-input" />
              </div>
              <div class="sm:col-span-2">
                <label class="field-label">Last Name <span class="text-red-500">*</span></label>
                <input v-model="form.lastname" type="text" placeholder="e.g. Doe" class="field-input" />
              </div>
              <div class="sm:col-span-2">
                <label class="field-label">
                  Full Name as it should Appear in Conference Attendance Certificate <span class="text-red-500">*</span>
                </label>
                <input v-model="form.certificate_name" type="text"
                  placeholder="e.g. Dr. Jane A. Doe"
                  class="field-input" />
                <p class="text-xs text-gray-400 mt-1">This is how your name will be printed on your certificate.</p>
              </div>
            </div>
            <div class="flex justify-end pt-2">
              <button @click="nextStep" class="btn-primary">Next &rarr;</button>
            </div>
          </div>

          <!-- Step 1: Photo -->
          <div v-else-if="currentStep === 1" key="step1" class="p-6 sm:p-8 space-y-5">
            <h2 class="text-lg font-bold text-gray-800 mb-1">Passport Photo</h2>
            <p class="text-sm text-gray-500">A clear passport-style photo will be used on your conference badge.</p>

            <div class="flex flex-col items-center gap-5">
              <!-- Preview or placeholder -->
              <div class="relative">
                <div v-if="form.photoPreview"
                  class="h-36 w-36 rounded-full overflow-hidden border-4 flex-shrink-0"
                  style="border-color: rgb(254,80,103);">
                  <img :src="form.photoPreview" alt="Photo preview" class="h-full w-full object-cover" />
                </div>
                <div v-else
                  class="h-36 w-36 rounded-full flex items-center justify-center border-4 border-dashed flex-shrink-0"
                  style="border-color: rgba(254,80,103,0.4); background-color: rgba(254,80,103,0.04);">
                  <svg class="w-12 h-12" style="color: rgba(254,80,103,0.4);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>

              <!-- Upload control -->
              <div class="w-full max-w-sm">
                <label class="block cursor-pointer">
                  <div class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl border-2 border-dashed transition text-sm font-semibold"
                    style="border-color: rgba(254,80,103,0.5); color: rgb(254,80,103); background-color: rgba(254,80,103,0.04);">
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {{ form.photo ? 'Change Photo' : 'Upload Photo' }}
                  </div>
                  <input type="file" accept="image/*" class="hidden" @change="onPhotoChange" />
                </label>
                <p v-if="form.photo" class="text-xs text-gray-400 mt-2 text-center">{{ form.photo.name }}</p>
                <p class="text-xs text-gray-400 mt-2 text-center">Photo is optional. You can skip this step.</p>
              </div>
            </div>

            <div class="flex justify-between pt-2">
              <button @click="prevStep" class="btn-secondary">&larr; Back</button>
              <button @click="nextStep" class="btn-primary">Next &rarr;</button>
            </div>
          </div>

          <!-- Step 2: Contact -->
          <div v-else-if="currentStep === 2" key="step2c" class="p-6 sm:p-8 space-y-5">
            <h2 class="text-lg font-bold text-gray-800 mb-1">Contact Information</h2>
            <div class="grid sm:grid-cols-2 gap-4">
              <div class="sm:col-span-2">
                <label class="field-label">Email Address <span class="text-red-500">*</span></label>
                <input v-model="form.email" type="email" placeholder="you@example.com" class="field-input" />
              </div>
              <div>
                <label class="field-label">Phone Number <span class="text-red-500">*</span></label>
                <input v-model="form.phone" type="tel" placeholder="+255700000000" class="field-input" />
                <p class="text-xs text-gray-400 mt-1">Include country code, e.g. +255757618084</p>
              </div>
              <div>
                <label class="field-label">Country <span class="text-red-500">*</span></label>
                <select v-model="form.country_id" class="field-input">
                  <option value="">Select country</option>
                  <option v-for="c in countries" :key="c.id" :value="c.id">{{ c.country }}</option>
                </select>
              </div>
              <div class="sm:col-span-2">
                <label class="field-label">Address</label>
                <textarea v-model="form.address" rows="3" class="field-input"
                  placeholder="Street / PO Box, City, Region"></textarea>
              </div>
            </div>
            <div class="flex justify-between pt-2">
              <button @click="prevStep" class="btn-secondary">&larr; Back</button>
              <button @click="nextStep" class="btn-primary">Next &rarr;</button>
            </div>
          </div>

          <!-- Step 3: Professional -->
          <div v-else-if="currentStep === 3" key="step3p" class="p-6 sm:p-8 space-y-5">
            <h2 class="text-lg font-bold text-gray-800 mb-1">Professional Details</h2>
            <div class="grid sm:grid-cols-2 gap-4">
              <div class="sm:col-span-2">
                <label class="field-label">Designation <span class="text-red-500">*</span></label>
                <select v-model="form.designation" class="field-input">
                  <option value="">Select designation</option>
                  <option value="Chief Nursing Officer">Chief Nursing Officer</option>
                  <option value="Clinical Supervisor">Clinical Supervisor</option>
                  <option value="Communications Manager">Communications Manager</option>
                  <option value="Director Nursing Services">Director Nursing Services</option>
                  <option value="Educator">Educator</option>
                  <option value="Midwifery Specialist">Midwifery Specialist</option>
                  <option value="Nursing Midwifery Specialist">Nursing Midwifery Specialist</option>
                  <option value="Nursing Specialist">Nursing Specialist</option>
                  <option value="Nursing Superintendent">Nursing Superintendent</option>
                  <option value="Principal Nursing Officer">Principal Nursing Officer</option>
                  <option value="Project Manager">Project Manager</option>
                  <option value="Public Health Specialist">Public Health Specialist</option>
                  <option value="Registered Nurse">Registered Nurse</option>
                  <option value="Researcher">Researcher</option>
                  <option value="Student">Student</option>
                  <option value="Other">Other (specify below)</option>
                </select>
              </div>
              <!-- Show free-text if Other selected -->
              <div class="sm:col-span-2" v-if="form.designation === 'Other'">
                <label class="field-label">Please specify your designation <span class="text-red-500">*</span></label>
                <input v-model="form.designation_other" type="text" placeholder="Your designation" class="field-input" />
              </div>
              <div class="sm:col-span-2">
                <label class="field-label">Organisation / Institution <span class="text-red-500">*</span></label>
                <input v-model="form.organisation" type="text" placeholder="e.g. Ministry of Health" class="field-input" />
              </div>
            </div>

            <div>
              <label class="field-label">Participation Category <span class="text-red-500">*</span></label>
              <div class="grid sm:grid-cols-1 gap-3 mt-2">
                <label v-for="opt in participationOptions" :key="opt.value"
                  class="flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition"
                  :style="form.participation_role === opt.value
                    ? 'border-color: rgb(254,80,103); background-color: rgba(254,80,103,0.05);'
                    : 'border-color: #e5e7eb; background-color: #fff;'">
                  <input type="radio" :value="opt.value" v-model="form.participation_role" class="mt-0.5 accent-pink-500 flex-shrink-0" />
                  <div>
                    <span class="text-sm font-semibold text-gray-800">{{ opt.label }}</span>
                    <p v-if="opt.fee" class="text-xs text-gray-500 mt-0.5">{{ opt.fee }}</p>
                  </div>
                </label>
              </div>
            </div>

            <div class="flex justify-between pt-2">
              <button @click="prevStep" class="btn-secondary">&larr; Back</button>
              <button @click="nextStep" class="btn-primary">Next &rarr;</button>
            </div>
          </div>

          <!-- Step 4: Confirm -->
          <div v-else-if="currentStep === 4" key="step4" class="p-6 sm:p-8 space-y-5">
            <h2 class="text-lg font-bold text-gray-800 mb-1">Review &amp; Submit</h2>
            <div class="rounded-xl bg-gray-50 divide-y divide-gray-100 overflow-hidden text-sm">
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Name</span>
                <span class="font-medium text-gray-800">{{ form.title }} {{ form.firstname }} {{ form.middlename }} {{ form.lastname }}</span>
              </div>
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Certificate Name</span>
                <span class="font-medium text-gray-800">{{ form.certificate_name || '—' }}</span>
              </div>
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Gender</span>
                <span class="font-medium text-gray-800">{{ form.gender || '—' }}</span>
              </div>
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Email</span>
                <span class="font-medium text-gray-800">{{ form.email }}</span>
              </div>
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Phone</span>
                <span class="font-medium text-gray-800">{{ form.phone }}</span>
              </div>
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Country</span>
                <span class="font-medium text-gray-800">{{ countryName }}</span>
              </div>
              <div v-if="form.address" class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Address</span>
                <span class="font-medium text-gray-800">{{ form.address }}</span>
              </div>
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Designation</span>
                <span class="font-medium text-gray-800">{{ resolvedDesignation || '—' }}</span>
              </div>
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Organisation</span>
                <span class="font-medium text-gray-800">{{ form.organisation }}</span>
              </div>
              <div class="flex gap-3 px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 pt-0.5 flex-shrink-0">Category</span>
                <span class="font-medium text-gray-800">{{ participationLabel }}</span>
              </div>
              <div class="flex gap-3 items-center px-5 py-3">
                <span class="text-xs text-gray-400 uppercase tracking-wide w-40 flex-shrink-0">Photo</span>
                <span v-if="form.photoPreview">
                  <img :src="form.photoPreview" alt="Badge photo" class="h-12 w-12 rounded-full object-cover border-2"
                    style="border-color: rgb(254,80,103);" />
                </span>
                <span v-else class="font-medium text-gray-400 italic text-sm">No photo uploaded</span>
              </div>
            </div>

            <!-- Fee info box -->
            <div class="rounded-xl border border-pink-100 bg-pink-50 p-4">
              <p class="text-sm font-semibold text-gray-700 mb-1">Registration Fee</p>
              <p class="text-sm text-gray-600">{{ selectedParticipationFee }}</p>
              <p class="text-xs text-gray-400 mt-2">Payment details will be sent to your email after registration.</p>
            </div>

            <div class="flex flex-col sm:flex-row justify-between gap-3 pt-2">
              <button @click="prevStep" class="btn-secondary" :disabled="isSubmitting">&larr; Back</button>
              <div class="flex gap-3">
                <button @click="submitForm('later')" :disabled="isSubmitting"
                  class="px-5 py-2.5 rounded-xl font-semibold text-sm border-2 transition disabled:opacity-50"
                  style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
                  {{ isSubmitting ? 'Registering...' : 'Register &amp; Pay Later' }}
                </button>
                <button @click="submitForm('now')" :disabled="isSubmitting"
                  class="px-5 py-2.5 rounded-xl font-semibold text-sm text-white transition hover:opacity-90 disabled:opacity-50"
                  style="background-color: rgb(254,80,103);">
                  {{ isSubmitting ? 'Registering...' : 'Register &amp; Pay Now' }}
                </button>
              </div>
            </div>
          </div>

        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { createItem } from '@/services/apiService'

export default {
  name: 'RegisterView',
  data() {
    return {
      currentStep: 0,
      isSubmitting: false,
      submitted: false,
      formError: '',
      eventName: '',
      eventDates: '',
      eventLocation: '',
      eventId: null,
      countries: [],
      form: {
        title: '',
        gender: '',
        firstname: '',
        middlename: '',
        lastname: '',
        certificate_name: '',
        email: '',
        phone: '',
        country_id: '',
        address: '',
        designation: '',
        designation_other: '',
        organisation: '',
        participation_role: '',
        photo: null,
        photoPreview: '',
      },
      stepLabels: ['Personal', 'Photo', 'Contact', 'Professional', 'Confirm'],
      participationOptions: [
        {
          value: 'member_state',
          label: 'ECSACONM Member (no arrears)',
          fee: 'Early Bird: USD 200  |  Late Bird: USD 250',
        },
        {
          value: 'participant',
          label: 'Non-ECSACONM Member from the Region',
          fee: 'Early Bird: USD 300  |  Late Bird: USD 400',
        },
        {
          value: 'other_africa',
          label: 'Non-ECSACONM Member from Outside the Region',
          fee: 'Early Bird: USD 400  |  Late Bird: USD 600',
        },
        {
          value: 'student',
          label: 'Student',
          fee: 'Contact the secretariat for student rates.',
        },
        {
          value: 'exhibitor',
          label: 'Sponsor / Exhibitor',
          fee: 'Contact the secretariat for sponsorship packages.',
        },
        {
          value: 'secretariat',
          label: 'Secretariat / Staff',
          fee: 'Internal registration — no registration fee.',
        },
      ],
    }
  },
  computed: {
    countryName() {
      const found = this.countries.find(c => c.id === this.form.country_id)
      return found ? found.country : '—'
    },
    participationLabel() {
      const found = this.participationOptions.find(o => o.value === this.form.participation_role)
      return found ? found.label : '—'
    },
    selectedParticipationFee() {
      const found = this.participationOptions.find(o => o.value === this.form.participation_role)
      return found?.fee || ''
    },
    resolvedDesignation() {
      return this.form.designation === 'Other' ? this.form.designation_other : this.form.designation
    },
  },
  async mounted() {
    this.eventId = this.$route.params.id
    await Promise.all([this.loadEvent(), this.loadCountries()])
  },
  methods: {
    async loadEvent() {
      try {
        const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
        const res = await api.get(`/events/${this.eventId}`)
        const ev = res.data?.event || res.data || {}
        this.eventName = ev.event || ev.title || 'Event Registration'
        this.eventLocation = [ev.location, ev.country].filter(Boolean).join(', ')
        if (ev.start_date) {
          const start = new Date(ev.start_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
          const end = ev.end_date ? new Date(ev.end_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : ''
          this.eventDates = end ? `${start} – ${end}` : start
        }
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
    nextStep() {
      this.formError = ''
      if (!this.validateStep()) return
      if (this.currentStep < 4) this.currentStep++
    },
    prevStep() {
      this.formError = ''
      if (this.currentStep > 0) this.currentStep--
    },
    validateStep() {
      if (this.currentStep === 0) {
        if (!this.form.firstname.trim()) { this.formError = 'First name is required.'; return false }
        if (!this.form.lastname.trim()) { this.formError = 'Last name is required.'; return false }
        if (!this.form.certificate_name.trim()) { this.formError = 'Please enter the name for your certificate.'; return false }
      }
      // Step 1: Photo — optional, always passes
      if (this.currentStep === 2) {
        if (!this.form.email.trim()) { this.formError = 'Email address is required.'; return false }
        if (!this.form.phone.trim()) { this.formError = 'Phone number is required.'; return false }
        if (!this.form.country_id) { this.formError = 'Please select a country.'; return false }
      }
      if (this.currentStep === 3) {
        if (!this.form.designation) { this.formError = 'Please select a designation.'; return false }
        if (this.form.designation === 'Other' && !this.form.designation_other.trim()) {
          this.formError = 'Please specify your designation.'; return false
        }
        if (!this.form.organisation.trim()) { this.formError = 'Organisation is required.'; return false }
        if (!this.form.participation_role) { this.formError = 'Please select a participation category.'; return false }
      }
      return true
    },
    onPhotoChange(e) {
      const file = e.target.files && e.target.files[0]
      if (!file) return
      this.form.photo = file
      const reader = new FileReader()
      reader.onload = (evt) => { this.form.photoPreview = evt.target.result }
      reader.readAsDataURL(file)
    },
    async submitForm(mode) {
      this.formError = ''
      this.isSubmitting = true
      try {
        // Step 1: Register / get user
        const regData = {
          firstname: this.form.firstname,
          lastname: this.form.lastname,
          email: this.form.email,
          phone: this.form.phone,
          event_name: this.eventName,
        }
        const regRes = await createItem('auth/register', regData)
        const userId = regRes.user_id || regRes.id

        // Step 2: Save extended profile
        const profileData = {
          title: this.form.title,
          middle_name: this.form.middlename,
          country_id: this.form.country_id || null,
          gender: this.form.gender,
          organisation: this.form.organisation,
          position: '',
          profession: this.resolvedDesignation,
          designation: this.resolvedDesignation,
          certificate_name: this.form.certificate_name,
          address: this.form.address,
        }
        await createItem(`users/profile/${userId}`, profileData)

        // Step 3: Register for event
        const eventRegData = {
          event_id: parseInt(this.eventId),
          participation_role: this.form.participation_role,
        }
        await createItem(`events/registration/${userId}`, eventRegData)

        // Step 4: Upload passport photo (optional)
        if (this.form.photo) {
          try {
            const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
            const photoForm = new FormData()
            photoForm.append('file', this.form.photo)
            await api.post(`/users/${userId}/photo`, photoForm, {
              headers: { 'Content-Type': 'multipart/form-data' },
            })
          } catch (photoErr) {
            // Non-critical: log but don't block registration success
            console.warn('Photo upload failed (non-critical):', photoErr)
          }
        }

        if (mode === 'now') {
          this.submitted = true
          window.open('https://ecsaconm.org/online-payment/', '_blank')
        } else {
          this.submitted = true
        }
      } catch (e) {
        console.error('Registration error:', e)
        this.formError = e.response?.data?.detail
          || (Array.isArray(e.response?.data) ? e.response.data.map(x => x.msg).join(', ') : null)
          || 'Registration failed. Please try again.'
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
.btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 0.625rem 1.5rem;
  border-radius: 0.625rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  background-color: rgb(254,80,103);
  transition: opacity 0.15s;
  border: none;
  cursor: pointer;
}
.btn-primary:hover { opacity: 0.9; }
.btn-secondary {
  display: inline-flex;
  align-items: center;
  padding: 0.625rem 1.5rem;
  border-radius: 0.625rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  background-color: #f3f4f6;
  transition: background-color 0.15s;
  border: none;
  cursor: pointer;
}
.btn-secondary:hover { background-color: #e5e7eb; }

/* Slide-fade transition */
.slide-fade-enter-active { transition: all 0.22s ease-out; }
.slide-fade-leave-active { transition: all 0.18s ease-in; }
.slide-fade-enter-from { opacity: 0; transform: translateX(20px); }
.slide-fade-leave-to { opacity: 0; transform: translateX(-20px); }
</style>
