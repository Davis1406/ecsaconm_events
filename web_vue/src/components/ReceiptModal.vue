<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50 bg-black/50 p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg flex flex-col max-h-[95vh] overflow-y-auto">

      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 flex-shrink-0">
        <div class="flex items-center gap-2">
          <div class="h-8 w-8 rounded-lg flex items-center justify-center" style="background-color: rgba(254,80,103,0.1);">
            <svg class="w-4 h-4" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <div>
            <p class="font-bold text-gray-800 text-sm">Send Receipt</p>
            <p class="text-xs text-gray-400">Generate & email official PDF receipt</p>
          </div>
        </div>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition p-1">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="p-5 space-y-5">

        <!-- Participant summary card -->
        <div class="p-4 rounded-xl bg-gray-50 border border-gray-100">
          <div class="flex items-start gap-3">
            <div class="h-10 w-10 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
              style="background-color: rgb(254,80,103);">
              {{ initials }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-bold text-gray-800 text-sm leading-tight">
                {{ [participant.title, participant.firstname, participant.lastname].filter(Boolean).join(' ') || '—' }}
              </p>
              <p class="text-xs text-gray-500 mt-0.5">{{ participant.email || '—' }}</p>
              <div class="flex flex-wrap gap-1.5 mt-2">
                <span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                  ✓ Paid
                </span>
                <span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-600">
                  {{ formatRole(participant.participation_role) }}
                </span>
              </div>
            </div>
            <div class="text-right flex-shrink-0">
              <p class="text-xs text-gray-400 uppercase tracking-widest">Amount</p>
              <p class="text-lg font-bold" style="color: rgb(254,80,103);">
                ${{ amountDisplay }}
              </p>
            </div>
          </div>
        </div>

        <!-- Proof of Payment -->
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">Proof of Payment</p>
          <div v-if="proofUrl" class="flex items-center gap-2 p-3 bg-blue-50 rounded-xl border border-blue-100">
            <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
            </svg>
            <a :href="proofUrl" target="_blank"
              class="text-xs text-blue-600 hover:underline truncate flex-1 font-medium">
              {{ proofUrl }}
            </a>
            <a :href="proofUrl" target="_blank"
              class="px-2.5 py-1 rounded-lg text-xs font-semibold border-2 flex-shrink-0"
              style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
              View
            </a>
          </div>
          <p v-else class="text-xs text-gray-400 italic">No payment proof on file.</p>
        </div>

        <!-- Badge / Passport Photo -->
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">Badge / Passport Photo</p>
          <div v-if="photoUrl" class="flex items-center gap-3 p-3 bg-green-50 rounded-xl border border-green-100">
            <img :src="photoUrl" class="h-10 w-10 rounded-full object-cover flex-shrink-0 border border-green-200"
              alt="Photo" @error="photoLoadError = true" v-if="!photoLoadError" />
            <div v-else class="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <a :href="photoUrl" target="_blank"
              class="text-xs text-green-700 hover:underline truncate flex-1 font-medium">
              {{ photoUrl }}
            </a>
            <a :href="photoUrl" target="_blank"
              class="px-2.5 py-1 rounded-lg text-xs font-semibold border-2 flex-shrink-0"
              style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
              View
            </a>
          </div>
          <p v-else class="text-xs text-gray-400 italic">No profile photo on file.</p>
        </div>

        <!-- ECSACONM Members section -->
        <div class="border border-gray-200 rounded-xl overflow-hidden">
          <div class="px-4 py-2.5 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
            <p class="text-xs font-bold uppercase tracking-widest text-gray-500">For ECSACONM Members</p>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="includeMembership" class="rounded" />
              <span class="text-xs text-gray-500">Include in receipt</span>
            </label>
          </div>
          <div class="p-4 space-y-3" :class="!includeMembership ? 'opacity-40 pointer-events-none' : ''">
            <div>
              <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">
                Membership Status
              </label>
              <input v-model="membershipStatus" type="text"
                placeholder="e.g. Unpaid for 3 years"
                class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">
                Membership Arrears (USD)
              </label>
              <input v-model.number="membershipArrears" type="number" min="0" step="1"
                placeholder="e.g. 60"
                class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
            </div>
            <p class="text-xs text-red-500 italic leading-relaxed">
              * Note: Membership arrears, if applicable, must be fully settled prior to issuance of a
              Proof of Conference Registration Letter.
            </p>
          </div>
        </div>

        <!-- Alerts -->
        <div v-if="errorMsg"
          class="flex items-start gap-2 p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">
          <svg class="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          {{ errorMsg }}
        </div>
        <div v-if="successMsg"
          class="flex items-start gap-2 p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">
          <svg class="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          {{ successMsg }}
        </div>

      </div>

      <!-- Actions -->
      <div class="flex items-center justify-end gap-3 px-5 py-4 border-t border-gray-100 flex-shrink-0">
        <button @click="$emit('close')"
          class="px-4 py-2 rounded-xl text-sm font-semibold border border-gray-200 text-gray-600 hover:bg-gray-50 transition">
          Cancel
        </button>
        <button @click="sendReceipt" :disabled="sending"
          class="inline-flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
          style="background-color: rgb(254,80,103);">
          <svg v-if="sending" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
          {{ sending ? 'Sending…' : 'Send Receipt' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL

const ROLE_MAP = {
  member_state: 'Member State', participant: 'Participant', other_africa: 'Other Africa',
  world: 'International', student: 'Student', exhibitor: 'Exhibitor',
  secretariat: 'Secretariat', delegate: 'Delegate', presenter: 'Presenter',
  speaker: 'Speaker', sponsor: 'Sponsor', moderator: 'Moderator', moh: 'Ministry of Health',
}

export default {
  name: 'ReceiptModal',
  props: {
    show:        { type: Boolean, required: true },
    participant: { type: Object,  required: true },  // row from participants list
    event:       { type: Object,  default: () => ({}) },
  },
  emits: ['close'],
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      membershipStatus:  '',
      membershipArrears: null,
      includeMembership: false,
      sending:           false,
      successMsg:        '',
      errorMsg:          '',
      photoLoadError:    false,
    }
  },
  computed: {
    initials() {
      const f = (this.participant?.firstname || '').charAt(0).toUpperCase()
      const l = (this.participant?.lastname  || '').charAt(0).toUpperCase()
      return (f + l) || '?'
    },
    amountDisplay() {
      const p = this.participant
      const amt = p?.payment_amount || p?.amount_paid || 0
      return Number(amt).toLocaleString()
    },
    proofUrl() {
      const proof = this.participant?.payment_proof
      if (!proof) return null
      if (proof.startsWith('http')) return proof
      return `${API_URL}/${proof}`
    },
    photoUrl() {
      const photo = this.participant?.photo  // now a string path from the API
      if (!photo) return null
      if (photo.startsWith('http')) return photo
      return `${API_URL}/${photo}`
    },
  },
  watch: {
    show(val) {
      if (val) {
        // Reset state when modal opens
        this.membershipStatus  = ''
        this.membershipArrears = null
        this.includeMembership = false
        this.successMsg        = ''
        this.errorMsg          = ''
        this.photoLoadError    = false
      }
      document.body.style.overflow = val ? 'hidden' : ''
    },
  },
  methods: {
    formatRole(role) {
      return ROLE_MAP[role] || role || '—'
    },
    async sendReceipt() {
      this.sending    = true
      this.errorMsg   = ''
      this.successMsg = ''
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        const payload = {
          membership_status:  this.includeMembership ? (this.membershipStatus || null) : null,
          membership_arrears: this.includeMembership ? (this.membershipArrears ?? null) : null,
        }

        const res = await api.post(`/events/send_receipt/${this.participant.id}`, payload)
        this.successMsg = `Receipt sent to ${res.data.email} (No. ${res.data.receipt_no})`
        setTimeout(() => { this.$emit('close') }, 3000)
      } catch (e) {
        this.errorMsg = e.response?.data?.detail || 'Failed to send receipt. Check SMTP settings.'
      } finally {
        this.sending = false
      }
    },
  },
}
</script>
