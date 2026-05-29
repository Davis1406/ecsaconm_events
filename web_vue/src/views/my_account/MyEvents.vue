<template>
  <div class="flex flex-col space-y-6 flex-1">
    <div class="text-2xl font-bold text-gray-800">My Events</div>

    <!-- Spinner -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <div v-else class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <!-- Empty state -->
      <div v-if="events.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-6">
        <div class="h-16 w-16 rounded-full flex items-center justify-center mb-4"
          style="background-color: rgba(254,80,103,0.1);">
          <svg class="w-8 h-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <p class="text-gray-500 text-base mb-4">You have not registered for any events yet.</p>
        <router-link :to="{ name: 'WebEvents' }"
          class="inline-flex items-center px-5 py-2.5 rounded-full text-white font-semibold text-sm transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          Browse Events &rarr;
        </router-link>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-100">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-5 py-3 text-left text-xs font-bold uppercase tracking-wider text-gray-500">Event</th>
              <th class="px-5 py-3 text-left text-xs font-bold uppercase tracking-wider text-gray-500">Dates</th>
              <th class="px-5 py-3 text-left text-xs font-bold uppercase tracking-wider text-gray-500">Location</th>
              <th class="px-5 py-3 text-left text-xs font-bold uppercase tracking-wider text-gray-500">Registration</th>
              <th class="px-5 py-3 text-left text-xs font-bold uppercase tracking-wider text-gray-500">Payment</th>
              <th class="px-5 py-3 text-left text-xs font-bold uppercase tracking-wider text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="item in registeredEvents" :key="item.event.id" class="hover:bg-gray-50 transition">
              <!-- Event name -->
              <td class="px-5 py-4 text-sm font-semibold text-gray-800 max-w-xs">
                {{ item.event.title || item.event.event || '—' }}
              </td>
              <!-- Dates -->
              <td class="px-5 py-4 text-sm text-gray-600 whitespace-nowrap">
                {{ formatDate(item.event.start_date) }}
                <span v-if="item.event.end_date" class="text-gray-400"> – {{ formatDate(item.event.end_date) }}</span>
              </td>
              <!-- Location -->
              <td class="px-5 py-4 text-sm text-gray-600">
                {{ item.event.location || '—' }}
              </td>
              <!-- Registration badge -->
              <td class="px-5 py-4">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                  Registered
                </span>
              </td>
              <!-- Payment badge -->
              <td class="px-5 py-4">
                <span v-if="item.registration_details && item.registration_details.paid"
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                  Paid
                </span>
                <span v-else
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
                  Unpaid
                </span>
              </td>
              <!-- Actions -->
              <td class="px-5 py-4">
                <div class="flex flex-wrap gap-2">
                  <router-link :to="{ name: 'MyEvent', params: { id: item.event.id } }"
                    class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border-2 transition"
                    style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
                    View Event
                  </router-link>

                  <!-- Unpaid: make payment + upload proof -->
                  <template v-if="item.registration_details && !item.registration_details.paid">
                    <button @click="openPaymentModal(item)"
                      class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition hover:opacity-90"
                      style="background-color: rgb(254,80,103);">
                      <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      Submit Payment
                    </button>
                  </template>

                  <!-- View submitted proof (any status) -->
                  <button
                    v-if="item.registration_details && item.registration_details.payment_proof"
                    @click="openProofViewer(item)"
                    class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold border-2 transition"
                    style="border-color: rgb(100,120,200); color: rgb(100,120,200);">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    View Proof
                  </button>

                  <!-- Paid: view badge -->
                  <button v-if="item.registration_details && item.registration_details.paid"
                    @click="openBadgeModal(item)"
                    class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition hover:opacity-90"
                    style="background-color: rgb(34,197,94);">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0" />
                    </svg>
                    My Badge
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ═══ PAYMENT MODAL ═══════════════════════════════════════════════════ -->
    <div v-if="showPaymentModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[95vh] overflow-y-auto flex flex-col">

        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h3 class="font-bold text-gray-800">Submit Payment</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ paymentEvent?.event?.title || paymentEvent?.event?.event }}</p>
          </div>
          <button @click="closePaymentModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Success state -->
        <div v-if="paymentSubmitted" class="flex flex-col items-center justify-center py-12 px-6 text-center">
          <div class="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h4 class="text-lg font-bold text-gray-800 mb-2">Payment Submitted!</h4>
          <p class="text-gray-500 text-sm mb-6">The secretariat will verify your payment shortly. You will be notified once confirmed.</p>
          <button @click="closePaymentModal"
            class="px-6 py-2.5 rounded-full text-white font-semibold text-sm transition hover:opacity-90"
            style="background-color: rgb(254,80,103);">
            Close
          </button>
        </div>

        <!-- Form -->
        <div v-else class="grid sm:grid-cols-2 gap-0 divide-y sm:divide-y-0 sm:divide-x divide-gray-100">

          <!-- Bank details -->
          <div class="p-6 space-y-3">
            <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-4">Bank Transfer Details</p>
            <div v-for="d in bankDetails" :key="d.label" class="p-3 rounded-xl bg-gray-50">
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-0.5">{{ d.label }}</p>
              <p class="text-sm font-semibold text-gray-800">{{ d.value }}</p>
            </div>
            <div class="p-3 rounded-xl bg-yellow-50 border border-yellow-100 text-xs text-gray-500">
              Use your full name and registration ID as payment reference.
            </div>
          </div>

          <!-- Upload form -->
          <div class="p-6">
            <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-4">Submit Proof</p>

            <div v-if="paymentError" class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              {{ paymentError }}
            </div>

            <div class="space-y-4">
              <!-- Payment method -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Payment Method <span class="text-red-500">*</span></label>
                <div class="grid grid-cols-3 gap-2">
                  <label v-for="m in paymentMethods" :key="m.value"
                    class="flex flex-col items-center p-2.5 rounded-xl border-2 cursor-pointer text-center text-xs font-semibold transition"
                    :style="paymentForm.payment_method === m.value
                      ? 'border-color: rgb(254,80,103); background-color: rgba(254,80,103,0.06); color: rgb(254,80,103);'
                      : 'border-color: #e5e7eb; color: #6b7280;'">
                    <input type="radio" :value="m.value" v-model="paymentForm.payment_method" class="sr-only" />
                    {{ m.label }}
                  </label>
                </div>
              </div>

              <!-- Amount -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Amount (USD) <span class="text-red-500">*</span></label>
                <input v-model="paymentForm.payment_amount" type="number" step="0.01" placeholder="0.00"
                  class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none"
                  style="focus:border-color: rgb(254,80,103);" />
              </div>

              <!-- File upload -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Proof of Payment <span class="text-gray-400 font-normal">(optional)</span></label>
                <label class="cursor-pointer flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 border-dashed text-sm font-medium transition"
                  style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
                  <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span class="truncate">{{ proofFileName || 'Choose file (image or PDF)' }}</span>
                  <input type="file" class="sr-only" accept="image/*,.pdf" @change="handleFileChange" />
                </label>
                <!-- Image preview -->
                <div v-if="proofPreviewUrl" class="mt-3 rounded-xl overflow-hidden border border-gray-200">
                  <img :src="proofPreviewUrl" class="max-h-40 w-full object-contain bg-gray-50" alt="Preview" />
                </div>
              </div>

              <button @click="submitPayment" :disabled="isSubmitting"
                class="w-full py-3 rounded-xl text-white font-bold text-sm transition hover:opacity-90 disabled:opacity-50"
                style="background-color: rgb(254,80,103);">
                {{ isSubmitting ? 'Submitting…' : 'Submit Payment' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ PROOF VIEWER MODAL ══════════════════════════════════════════════ -->
    <div v-if="showProofViewer" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <h3 class="font-bold text-gray-800">Payment Proof</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ proofViewerEvent }}</p>
          </div>
          <button @click="showProofViewer = false" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-5">
          <!-- Image -->
          <img v-if="proofViewerIsImage" :src="proofViewerUrl"
            class="max-w-full rounded-xl mx-auto border border-gray-100" alt="Payment Proof" />
          <!-- PDF inline -->
          <div v-else>
            <iframe :src="proofViewerUrl" class="w-full rounded-xl border border-gray-200"
              style="height: 480px;" title="Payment Proof PDF"></iframe>
            <a :href="proofViewerUrl" target="_blank"
              class="inline-flex items-center gap-1.5 mt-3 text-xs font-semibold hover:underline"
              style="color: rgb(254,80,103);">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Open in new tab
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ BADGE MODAL ══════════════════════════════════════════════════════ -->
    <div v-if="showBadgeModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm max-h-[95vh] overflow-y-auto flex flex-col">

        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-800">My Badge</h3>
          <div class="flex items-center gap-2">
            <button @click="downloadBadge"
              :disabled="badgeDownloading"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
              style="background-color: rgb(34,197,94);">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ badgeDownloading ? 'Downloading…' : 'Download PDF' }}
            </button>
            <button @click="showBadgeModal = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Badge preview -->
        <div class="p-5">
          <div class="border border-gray-200 rounded-xl overflow-hidden">
            <!-- Top bar -->
            <div class="h-5" style="background-color: rgb(254,80,103);"></div>

            <!-- Logo row -->
            <div class="flex items-center justify-center px-6 py-4 bg-white">
              <img src="@/assets/images/logo.png" class="h-14 object-contain" alt="ECSACONM" />
            </div>

            <!-- Divider -->
            <div class="h-0.5 mx-6" style="background-color: rgb(254,80,103);"></div>

            <!-- Name + Designation -->
            <div class="px-6 py-5 text-center">
              <p class="text-2xl font-bold text-gray-900">
                {{ badgeParticipant.fullName || '—' }}
              </p>
              <p v-if="badgeParticipant.designation" class="text-sm font-medium mt-1" style="color: rgb(254,80,103);">
                {{ badgeParticipant.designation }}
              </p>
            </div>

            <!-- Category bar -->
            <div class="mx-6 py-2 text-center text-white font-bold text-sm rounded-lg"
              style="background-color: rgb(254,80,103);">
              {{ formatRole(badgeParticipant.participation_role) }}
            </div>

            <!-- Institution & Country -->
            <div class="px-6 py-4 text-center space-y-1">
              <p class="text-base font-semibold text-gray-800">{{ badgeParticipant.organisation || '—' }}</p>
              <p class="text-sm text-gray-500">{{ badgeParticipant.country || '—' }}</p>
            </div>

            <!-- QR Code -->
            <div class="flex flex-col items-center pb-4 gap-1">
              <QRCodeVue
                :value="badgeQrValue"
                :size="100"
                foreground="#000000"
                background="#ffffff" />
              <p class="text-xs text-gray-400">ID #{{ badgeParticipant.registration_id }}</p>
              <p v-if="badgeParticipant.eventTheme" class="text-xs text-gray-500 text-center px-6 mt-0.5 leading-snug">
                <span class="font-semibold not-italic">Theme:</span>
                <span class="italic"> {{ badgeParticipant.eventTheme }}</span>
              </p>
            </div>

            <!-- Website -->
            <div class="text-center pb-3">
              <p class="text-xs text-gray-400">www.ecsaconm.org</p>
            </div>

            <!-- Bottom bar -->
            <div class="h-5" style="background-color: rgb(254,80,103);"></div>
          </div>

          <p v-if="badgeError" class="mt-3 text-xs text-red-500 text-center">{{ badgeError }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'
import QRCodeVue from 'qrcode.vue'
import { fetchData } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'MyEvents',
  components: { QRCodeVue },
  data() {
    return {
      isLoading: true,
      events: [],

      // Payment modal
      showPaymentModal: false,
      paymentEvent: null,
      paymentSubmitted: false,
      paymentError: '',
      isSubmitting: false,
      proofFile: null,
      proofFileName: '',
      proofPreviewUrl: null,
      paymentForm: {
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

      // Proof viewer
      showProofViewer: false,
      proofViewerUrl: '',
      proofViewerEvent: '',

      // Badge modal
      showBadgeModal: false,
      badgeParticipant: {},
      badgeEventId: null,
      badgeDownloading: false,
      badgeError: '',
    }
  },
  setup() {
    const authStore = useAuthStore()
    const user = authStore.loginUser
    return { user, authStore }
  },
  computed: {
    registeredEvents() {
      return this.events.filter(e => e.registered)
    },
    proofViewerIsImage() {
      return /\.(jpg|jpeg|png|gif|webp)(\?|$)/i.test(this.proofViewerUrl)
    },
    badgeQrValue() {
      const base = import.meta.env.VITE_APP_URL || window.location.origin
      return `${base}/#/user-event-status/${this.badgeParticipant.registration_id}/${this.badgeEventId}/`
    },
  },
  mounted() {
    this.loadMyEvents()
  },
  methods: {
    async loadMyEvents() {
      try {
        const userId = this.user?.id
        const response = await fetchData('events/with-registration/' + userId, 0, 100, '')
        const raw = response.data || response || []
        this.events = Array.isArray(raw) ? raw : []
      } catch (error) {
        console.error('Error fetching my events:', error)
        this.events = []
      } finally {
        this.isLoading = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
      })
    },

    formatRole(role) {
      const map = {
        member_state: 'Member State', participant: 'Participant', other_africa: 'Other Africa',
        world: 'International', student: 'Student', exhibitor: 'Exhibitor',
        secretariat: 'Secretariat', delegate: 'Delegate', presenter: 'Presenter',
        speaker: 'Speaker', sponsor: 'Sponsor', moderator: 'Moderator', moh: 'Ministry of Health',
      }
      return map[role] || role || 'Participant'
    },

    // ── Proof viewer ─────────────────────────────────────────────────────────
    openProofViewer(item) {
      const proof = item.registration_details?.payment_proof
      this.proofViewerUrl = proof ? `${API_URL}/${proof}` : ''
      this.proofViewerEvent = item.event?.title || item.event?.event || ''
      this.showProofViewer = true
    },

    // ── Payment modal ────────────────────────────────────────────────────────
    openPaymentModal(item) {
      this.paymentEvent = item
      this.paymentSubmitted = false
      this.paymentError = ''
      this.paymentForm = { payment_method: 'bank_transfer', payment_amount: '' }
      this.proofFile = null
      this.proofFileName = ''
      this.proofPreviewUrl = null
      this.showPaymentModal = true
    },
    closePaymentModal() {
      this.showPaymentModal = false
      this.paymentEvent = null
      if (this.paymentSubmitted) this.loadMyEvents()
    },
    handleFileChange(e) {
      const file = e.target.files[0]
      if (!file) return
      this.proofFile = file
      this.proofFileName = file.name
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = ev => { this.proofPreviewUrl = ev.target.result }
        reader.readAsDataURL(file)
      } else {
        this.proofPreviewUrl = null
      }
    },
    async submitPayment() {
      if (!this.paymentForm.payment_method) { this.paymentError = 'Please select a payment method.'; return }
      if (!this.paymentForm.payment_amount) { this.paymentError = 'Please enter the amount paid.'; return }
      this.isSubmitting = true
      this.paymentError = ''
      try {
        const fd = new FormData()
        fd.append('registration_id', this.paymentEvent.registration_details.registration_id)
        fd.append('payment_method', this.paymentForm.payment_method)
        fd.append('payment_amount', this.paymentForm.payment_amount)
        if (this.proofFile) fd.append('file', this.proofFile)

        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        await api.post(`/events/upload_payment_proof/${this.paymentEvent.event.id}`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        this.paymentSubmitted = true
      } catch (e) {
        this.paymentError = e.response?.data?.detail || e.response?.data?.message || 'Failed to submit payment.'
      } finally {
        this.isSubmitting = false
      }
    },

    // ── Badge modal ──────────────────────────────────────────────────────────
    async openBadgeModal(item) {
      this.badgeEventId = item.event.id
      this.badgeError = ''
      // Build participant info from auth store + registration details
      const u = this.user || {}
      this.badgeParticipant = {
        fullName: [u.title, u.firstname, u.lastname].filter(Boolean).join(' ') || `${u.firstname || ''} ${u.lastname || ''}`.trim(),
        organisation: u.organisation || '',
        country: u.country || '',
        participation_role: item.registration_details?.participation_role || 'participant',
        registration_id: item.registration_details?.registration_id,
        eventTheme: item.event?.theme || '',
      }
      // Try to enrich with profile data
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const res = await api.get(`/users/${u.id}?skip=0&limit=&search=`)
        const profile = res.data?.profile || {}
        const userData = res.data?.user || {}
        this.badgeParticipant.fullName = [profile.title, userData.firstname, userData.lastname].filter(Boolean).join(' ') || this.badgeParticipant.fullName
        this.badgeParticipant.organisation = profile.organisation || ''
        this.badgeParticipant.country = profile.country || ''
        this.badgeParticipant.designation = profile.designation || ''
      } catch (e) { /* use store data */ }
      this.showBadgeModal = true
    },
    async downloadBadge() {
      this.badgeDownloading = true
      this.badgeError = ''
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const response = await api.get(`/events/${this.badgeEventId}/my-badge`, { responseType: 'blob' })
        const url = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
        const a = document.createElement('a')
        a.href = url
        a.download = `badge_${this.badgeEventId}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } catch (e) {
        this.badgeError = e.response?.data?.detail || 'Failed to download badge. Ensure your payment is verified.'
      } finally {
        this.badgeDownloading = false
      }
    },
  },
}
</script>
