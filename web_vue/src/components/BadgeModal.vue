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
      <div class="p-5 pt-2 flex-1">
        <div class="badge-card rounded-2xl overflow-hidden shadow-lg border border-black/5">

          <!-- Gradient header band -->
          <div class="badge-header relative px-5 pt-5 pb-6">
            <!-- Subtle dot-grid watermark -->
            <div class="badge-watermark"></div>

            <!-- Logo row — pill container, divided by a vertical rule -->
            <div class="relative flex items-stretch justify-center gap-4 bg-white/95 backdrop-blur-sm rounded-xl px-4 py-3 shadow-sm">
              <div class="flex items-center justify-center flex-1">
                <img src="@/assets/images/ecsalogo.png" class="max-h-11 max-w-full object-contain" alt="ECSA" />
              </div>
              <div class="w-px bg-gray-200 self-stretch"></div>
              <div class="flex items-center justify-center flex-1">
                <img src="@/assets/images/logo.png" class="max-h-11 max-w-full object-contain" alt="ECSACONM" />
              </div>
            </div>
          </div>

          <!-- Body -->
          <div class="bg-white px-6 pt-5 pb-4 -mt-3 rounded-t-2xl relative">

            <!-- Name -->
            <div class="text-center">
              <p class="text-xl font-extrabold text-gray-900 leading-tight tracking-tight">
                {{ [participant.title, participant.firstname, participant.lastname].filter(Boolean).join(' ') || '—' }}
              </p>
            </div>

            <!-- Designation pill -->
            <div class="flex justify-center mt-3">
              <span class="badge-pill inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-white text-xs font-bold uppercase tracking-wide">
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {{ participant.designation || formatCategory(participant.participant_category || participant.participation_role) }}
              </span>
            </div>

            <!-- Institution & Country -->
            <div class="text-center mt-4 space-y-0.5">
              <p class="text-sm font-semibold text-gray-800 leading-snug">{{ participant.institution || participant.organisation || '—' }}</p>
              <p class="text-xs text-gray-400 flex items-center justify-center gap-1">
                <svg class="w-3 h-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {{ participant.country || '—' }}
              </p>
            </div>

            <!-- Divider -->
            <div class="badge-divider my-4"></div>

            <!-- QR Code -->
            <div class="flex flex-col items-center gap-1.5">
              <div class="p-2 rounded-xl bg-white border border-gray-100 shadow-sm">
                <QRCodeVue :value="qrValue" :size="96" foreground="#111827" background="#ffffff" />
              </div>
              <p class="text-[11px] font-semibold text-gray-400 tracking-wide mt-0.5">ID #{{ participant.id }}</p>
              <p v-if="eventTheme" class="text-[11px] text-gray-400 text-center px-6 leading-snug">
                <span class="font-semibold text-gray-500">Theme:</span>
                <span class="italic"> {{ eventTheme }}</span>
              </p>
            </div>

            <!-- Website -->
            <div class="text-center pt-4 pb-1">
              <p class="text-[11px] font-medium tracking-wide" style="color: rgb(220,50,75);">www.ecsaconm.org</p>
            </div>
          </div>

          <!-- Footer accent bar -->
          <div class="badge-footer h-2.5"></div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import QRCodeVue from 'qrcode.vue'

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
    return {}
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
  },
  watch: {
    show(val) {
      document.body.style.overflow = val ? 'hidden' : ''
    },
  },
}
</script>

<style scoped>
.badge-card {
  background: #fff;
}
.badge-header {
  background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(220,50,75) 100%);
}
.badge-watermark {
  position: absolute;
  inset: 0;
  opacity: 0.12;
  background-image: radial-gradient(rgba(255,255,255,0.9) 1px, transparent 1px);
  background-size: 14px 14px;
  pointer-events: none;
}
.badge-pill {
  background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(220,50,75) 100%);
  box-shadow: 0 2px 8px rgba(220,50,75,0.35);
}
.badge-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(220,50,75,0.25), transparent);
}
.badge-footer {
  background: linear-gradient(90deg, rgb(254,80,103) 0%, rgb(220,50,75) 100%);
}
</style>
