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
            <p class="text-xs text-gray-500">A confirmation email is on its way to you. If anything changes, submit the form again with the same email — your details will be filled in for you.</p>
          </div>

          <form v-else @submit.prevent="submit" class="space-y-4">
            <p class="text-sm text-gray-600 text-center leading-relaxed">
              Find your name below — it'll fill in your registered email automatically.
            </p>

            <!-- Name search / picker -->
            <div v-if="!manualEntry">
              <label class="block text-xs font-semibold text-gray-600 mb-1">Name</label>

              <div v-if="fields.email" class="flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg border border-green-200 bg-green-50">
                <div class="min-w-0">
                  <div class="text-sm font-semibold text-gray-800 truncate">{{ fields.name }}</div>
                  <div class="text-xs text-gray-500 truncate">{{ fields.email }}</div>
                </div>
                <button type="button" @click="clearSelection" class="text-xs font-semibold flex-shrink-0" style="color: rgb(254,80,103);">Change</button>
              </div>

              <div v-else class="relative">
                <input v-model.trim="nameQuery" type="text" @focus="showDropdown = true"
                  class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                  style="--tw-ring-color: rgb(254,80,103);" placeholder="Start typing your name…" />
                <div v-if="showDropdown && nameQuery.length >= 2"
                  class="absolute z-10 mt-1 w-full max-h-52 overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg">
                  <button v-for="p in filteredPeople" :key="p.email" type="button" @click="pickPerson(p)"
                    class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 border-b border-gray-50 last:border-0">
                    <div class="font-medium text-gray-800">{{ p.name }}</div>
                    <div class="text-xs text-gray-400">{{ p.email }}</div>
                  </button>
                  <div v-if="filteredPeople.length === 0" class="px-3 py-3 text-xs text-gray-400 italic text-center">
                    No match. If you registered under a different name, try your email, or enter your details manually below.
                  </div>
                </div>
              </div>

              <button type="button" @click="manualEntry = true" class="text-xs font-medium mt-1.5 hover:underline" style="color: rgb(0,150,180);">
                Can't find your name? Enter manually
              </button>
            </div>

            <!-- Manual fallback -->
            <template v-else>
              <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Name</label>
                <input v-model.trim="fields.name" type="text" required
                  class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                  style="--tw-ring-color: rgb(254,80,103);" placeholder="Your full name" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Email</label>
                <input v-model.trim="fields.email" type="email" required @blur="prefillExisting(fields.email)"
                  class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                  style="--tw-ring-color: rgb(254,80,103);" placeholder="you@example.com" />
                <p class="text-xs text-gray-400 mt-1">Use the email address you registered with.</p>
              </div>
              <button type="button" @click="manualEntry = false; fields.name = ''; fields.email = ''" class="text-xs font-medium hover:underline" style="color: rgb(0,150,180);">
                Search by name instead
              </button>
            </template>

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
              <label class="block text-xs font-semibold text-gray-600 mb-1">Departure time (24hrs)</label>
              <input v-model="fields.departure_time" type="time" required
                class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                style="--tw-ring-color: rgb(254,80,103);" />
              <p class="text-xs text-gray-400 mt-1">24-hour format, e.g. 14:30</p>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Point of departure (Ferry / Airport)</label>
              <input v-model.trim="fields.departure_point" type="text" required
                class="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2"
                style="--tw-ring-color: rgb(254,80,103);" placeholder="e.g. Zanzibar Ferry Terminal or Abeid Amani Karume International Airport (ZNZ)" />
            </div>

            <button type="submit" :disabled="isSubmitting || !fields.email"
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
      manualEntry: false,
      nameQuery: '',
      showDropdown: false,
      people: [],
      fields: { name: '', email: '', hotel: '', departure_date: '', departure_time: '', departure_point: '' },
      prefilledEmail: '',
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },
  computed: {
    filteredPeople() {
      const q = this.nameQuery.toLowerCase()
      if (q.length < 2) return []
      return this.people
        .filter(p => p.name.toLowerCase().includes(q) || p.email.toLowerCase().includes(q))
        .slice(0, 8)
    },
  },
  mounted() {
    this.loadPeople()
    document.addEventListener('click', this.onDocClick)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.onDocClick)
  },
  methods: {
    onDocClick(e) {
      if (!this.$el.contains(e.target)) this.showDropdown = false
    },
    async loadPeople() {
      try {
        const eventId = this.$route.query.event_id || 1
        const res = await axios.get(`${this.apiUrl}/departure-details/eligible-names`, { params: { event_id: eventId } })
        this.people = res.data || []
      } catch (error) {
        // Non-fatal — the search box just won't find anyone; manual entry still works.
      }
    },
    pickPerson(p) {
      this.fields.name = p.name
      this.fields.email = p.email
      this.showDropdown = false
      this.nameQuery = ''
      this.prefillExisting(p.email)
    },
    clearSelection() {
      this.fields.name = ''
      this.fields.email = ''
      this.nameQuery = ''
      this.prefilledEmail = ''
    },
    async prefillExisting(email) {
      // Returning submitters get their saved details pre-filled so they only
      // need to edit the fields that changed (e.g. port of departure).
      const value = (email || '').trim().toLowerCase()
      if (!value || value === this.prefilledEmail) return
      const eventId = this.$route.query.event_id || 1
      try {
        const res = await axios.get(`${this.apiUrl}/departure-details/existing-details`, {
          params: { email: value, event_id: eventId },
        })
        const d = res.data || {}
        if (!d.email) return
        this.prefilledEmail = value
        this.fields.name = d.name || this.fields.name
        this.fields.hotel = d.hotel || ''
        this.fields.departure_date = d.departure_date || ''
        this.fields.departure_time = d.departure_time || ''
        this.fields.departure_point = d.departure_point || ''
      } catch (e) {
        // Non-fatal — the form still submits fine without prefill.
      }
    },
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
