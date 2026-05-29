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

      <!-- Badge card -->
      <div class="p-5 flex-1">
        <div class="border border-gray-200 rounded-xl overflow-hidden">

          <!-- Top bar -->
          <div class="h-5" style="background-color: rgb(254,80,103);"></div>

          <!-- Logo row -->
          <div class="flex items-center justify-between px-5 py-4 bg-white">
            <div class="h-14 w-14 flex-shrink-0 flex items-center justify-center rounded-lg"
              :class="!leftLogoUrl ? 'border-2 border-dashed border-gray-100' : ''">
              <img v-if="leftLogoUrl" :src="leftLogoUrl" class="max-h-14 max-w-full object-contain" alt="Left Logo" />
              <span v-else class="text-gray-300 text-xs text-center leading-tight">Left<br/>Logo</span>
            </div>
            <div class="flex-1 flex justify-center px-3">
              <img src="@/assets/images/logo.png" class="h-14 object-contain" alt="ECSACONM" />
            </div>
            <div class="h-14 w-14 flex-shrink-0 flex items-center justify-center rounded-lg"
              :class="!rightLogoUrl ? 'border-2 border-dashed border-gray-100' : ''">
              <img v-if="rightLogoUrl" :src="rightLogoUrl" class="max-h-14 max-w-full object-contain" alt="Right Logo" />
              <span v-else class="text-gray-300 text-xs text-center leading-tight">Right<br/>Logo</span>
            </div>
          </div>

          <!-- Pink divider -->
          <div class="h-0.5 mx-5" style="background-color: rgb(254,80,103);"></div>

          <!-- Name -->
          <div class="px-6 pt-5 pb-3 text-center">
            <p class="text-2xl font-bold text-gray-900 leading-tight">
              {{ [participant.title, participant.firstname, participant.lastname].filter(Boolean).join(' ') || '—' }}
            </p>
          </div>

          <!-- Designation bar (replaces role) -->
          <div class="mx-5 py-2 text-center text-white font-bold text-sm rounded-lg"
            style="background-color: rgb(254,80,103);">
            {{ participant.designation || formatCategory(participant.participant_category || participant.participation_role) }}
          </div>

          <!-- Institution & Country -->
          <div class="px-6 py-4 text-center space-y-1">
            <p class="text-sm font-semibold text-gray-800">{{ participant.institution || participant.organisation || '—' }}</p>
            <p class="text-xs text-gray-500">{{ participant.country || '—' }}</p>
          </div>

          <!-- QR Code -->
          <div class="flex flex-col items-center pb-2 gap-1">
            <QRCodeVue :value="qrValue" :size="110" foreground="#000000" background="#ffffff" />
            <p class="text-xs text-gray-400 mt-1">ID #{{ participant.id }}</p>
            <!-- Theme below ID -->
            <p v-if="eventTheme" class="text-xs text-gray-500 text-center px-6 mt-0.5 leading-snug">
              <span class="font-semibold not-italic">Theme:</span>
              <span class="italic"> {{ eventTheme }}</span>
            </p>
          </div>

          <!-- Website -->
          <div class="text-center py-3">
            <p class="text-xs text-gray-400">www.ecsaconm.org</p>
          </div>

          <!-- Bottom bar -->
          <div class="h-5" style="background-color: rgb(254,80,103);"></div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import QRCodeVue from 'qrcode.vue'

const LOGO_LEFT_KEY = 'badge_logo_left'
const LOGO_RIGHT_KEY = 'badge_logo_right'

export default {
  name: 'BadgeModal',
  components: { QRCodeVue },
  props: {
    show: { type: Boolean, required: true },
    participant: { type: Object, required: true },
    event_id: { type: [Number, String] },
    event: { type: Object, default: () => ({}) },
  },
  data() {
    return {
      leftLogoUrl: null,
      rightLogoUrl: null,
    }
  },
  computed: {
    qrValue() {
      const base = import.meta.env.VITE_APP_URL || window.location.origin
      return `${base}/#/user-event-status/${this.participant.id}/${this.event_id}/`
    },
    eventTheme() {
      return this.event?.theme || ''
    },
  },
  mounted() {
    this.loadLogos()
  },
  methods: {
    close() { this.$emit('close') },
    formatCategory(cat) {
      const map = {
        member_state: 'Member State', participant: 'Participant', other_africa: 'Other Africa',
        world: 'International', student: 'Student', exhibitor: 'Exhibitor',
        secretariat: 'Secretariat', delegate: 'Delegate', presenter: 'Presenter',
        speaker: 'Speaker', sponsor: 'Sponsor', moderator: 'Moderator', moh: 'Ministry of Health',
      }
      return map[cat] || cat || 'Participant'
    },
    loadLogos() {
      this.leftLogoUrl = localStorage.getItem(LOGO_LEFT_KEY) || null
      this.rightLogoUrl = localStorage.getItem(LOGO_RIGHT_KEY) || null
    },
  },
  watch: {
    show(val) {
      document.body.style.overflow = val ? 'hidden' : ''
      if (val) this.loadLogos()
    },
  },
}
</script>
