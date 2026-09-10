<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50 bg-black/50 p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[95vh] overflow-y-auto flex flex-col">

      <!-- Minimal header — just close button -->
      <div class="flex items-center justify-end px-5 py-3 border-b border-gray-100">
        <button @click="close" class="text-gray-400 hover:text-gray-600 transition">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Badge card (A5) -->
      <div class="p-5 flex-1">
        <badge-card :participant="badgeParticipant" :event="badgeEvent" :qr-value="qrValue" />

        <!-- Actions -->
        <div class="mt-4 flex gap-2">
          <button @click="downloadPdf" :disabled="downloading"
            class="flex-1 inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-white text-gray-700 transition hover:opacity-80 disabled:opacity-50"
            style="border: 1px solid rgba(254,80,103,0.3);">
            <svg v-if="downloading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            <PrinterIcon v-else class="w-4 h-4" style="color: rgb(254,80,103);" />
            {{ downloading ? 'Preparing…' : 'Print A5 Pass' }}
          </button>
          <button @click="share"
            class="flex-1 inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold text-white transition hover:opacity-90"
            style="background-color: rgb(254,80,103);">
            <ShareIcon class="w-4 h-4" />
            Share ID #{{ participant.id }}
          </button>
        </div>
        <p v-if="shareMsg" class="mt-2 text-xs text-center text-gray-500">{{ shareMsg }}</p>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { PrinterIcon, ShareIcon } from '@heroicons/vue/24/solid'
import BadgeCard from '@/components/BadgeCard.vue'
import { useAuthStore } from '@/store/authStore'
import { buildBadgeEvent } from '@/utils/badgeEvent'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'BadgeModal',
  components: { BadgeCard, PrinterIcon, ShareIcon },
  props: {
    show: { type: Boolean, required: true },
    participant: { type: Object, required: true },
    event_id: { type: [Number, String] },
    event: { type: Object, default: () => ({}) },
  },
  data() {
    return {
      downloading: false,
      shareMsg: '',
    }
  },
  computed: {
    qrValue() {
      const base = import.meta.env.VITE_APP_URL || window.location.origin
      return `${base}/#/user-event-status/${this.participant.id}/${this.event_id}/`
    },
    badgeEvent() {
      return buildBadgeEvent(this.event)
    },
    badgeParticipant() {
      const p = this.participant
      return {
        fullName: [p.title, p.firstname, p.lastname].filter(Boolean).join(' '),
        designation: p.designation || '',
        category: p.participant_category || p.participation_role,
        institution: p.institution || p.organisation || '',
        country: p.country || '',
        registrationId: p.id,
        photo: p.photo || '',
      }
    },
  },
  methods: {
    close() { this.$emit('close') },
    async share() {
      try {
        await navigator.clipboard.writeText(this.qrValue)
        this.shareMsg = 'Badge link copied to clipboard.'
      } catch (e) {
        this.shareMsg = this.qrValue
      }
      setTimeout(() => { this.shareMsg = '' }, 4000)
    },
    async downloadPdf() {
      this.downloading = true
      try {
        const authStore = useAuthStore()
        const api = axios.create({ baseURL: API_URL })
        if (authStore.accessToken) api.defaults.headers.common['Authorization'] = `Bearer ${authStore.accessToken}`
        const res = await api.get(`/events/${this.event_id}/participants/${this.participant.id}/badge`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(res.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `badge_${String(this.participant.firstname || '').replace(/\s+/g, '_')}_${String(this.participant.lastname || '').replace(/\s+/g, '_')}.pdf`
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
      } catch (e) {
        console.error('Badge download failed:', e)
      } finally {
        this.downloading = false
      }
    },
  },
  watch: {
    show(val) {
      document.body.style.overflow = val ? 'hidden' : ''
    },
  },
}
</script>
