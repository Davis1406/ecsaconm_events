<template>
  <div class="badge-card-a5-wrap flex flex-col items-center mx-auto">

    <!-- Lanyard clip & punch hole (decorative, hidden when printed) -->
    <div class="no-print flex flex-col items-center -mb-2.5 z-20">
      <div class="w-10 h-8 rounded-t-md flex items-center justify-center relative overflow-hidden"
        style="background: linear-gradient(to bottom, rgb(220,50,75), rgb(254,80,103), rgb(220,50,75));">
        <div class="absolute inset-0 bg-white/10"></div>
      </div>
      <div class="w-5 h-5 rounded-sm -mt-0.5 z-20" style="background: linear-gradient(to right, #94a3b8, #f1f5f9, #94a3b8); border: 1px solid #94a3b8;"></div>
      <div class="w-3.5 h-3.5 rounded-full -mt-1 z-10" style="border: 2.5px solid #94a3b8;"></div>
    </div>

    <!-- Badge card (A5 proportions) -->
    <div class="badge-card-a5 relative bg-white rounded-3xl overflow-hidden flex flex-col"
      style="box-shadow: 0 20px 40px -15px rgba(220,50,75,0.18), 0 0 0 1px rgba(220,50,75,0.12), 0 8px 16px -4px rgba(15,23,42,0.08); border: 1px solid rgba(254,80,103,0.15);">

      <!-- Decorative background blobs -->
      <div class="absolute -top-12 -right-12 w-36 h-36 rounded-full pointer-events-none" style="background: rgba(254,80,103,0.08); filter: blur(28px);"></div>
      <div class="absolute top-1/3 -left-12 w-32 h-32 rounded-full pointer-events-none" style="background: rgba(254,80,103,0.06); filter: blur(24px);"></div>

      <!-- Header -->
      <header class="relative z-10 pt-4 px-4 pb-1 flex-shrink-0">
        <!-- Punch hole slot -->
        <div class="flex justify-center mb-3">
          <div class="w-14 h-3 rounded-full flex items-center justify-center" style="background: #0f172a; box-shadow: inset 0 2px 4px rgba(0,0,0,0.6);">
            <div class="w-10 h-0.5 rounded-full" style="background: #020617; opacity: 0.6;"></div>
          </div>
        </div>

        <div class="flex items-center justify-between gap-2">
          <!-- ECSA logo -->
          <div class="w-16 h-16 rounded-full bg-white flex-shrink-0 flex items-center justify-center overflow-hidden"
            style="border: 2px solid rgb(254,80,103);">
            <img src="@/assets/images/ecsalogo.png" class="w-full h-full object-contain p-1" alt="ECSA" />
          </div>

          <!-- Conference title -->
          <div class="flex-1 text-center px-1">
            <div class="inline-flex items-baseline justify-center gap-1 leading-none">
              <span class="text-lg font-extrabold text-gray-800 tracking-tight" v-html="titleOrdinalHtml"></span>
              <span class="text-xl font-extrabold tracking-tight" style="color: rgb(220,50,75);">{{ event.title.org }}</span>
            </div>
            <div v-if="event.title.subtitle" class="text-[10px] font-extrabold uppercase tracking-wide text-gray-600 leading-tight mt-1">
              {{ event.title.subtitle }}
            </div>
            <div v-if="event.title.pill" class="mt-1.5">
              <span class="text-[9px] font-bold tracking-tight px-2.5 py-0.5 rounded-full inline-block"
                style="color: rgb(220,50,75); background: rgba(254,80,103,0.08); border: 1px solid rgba(254,80,103,0.25);"
                v-html="titlePillHtml"></span>
            </div>
          </div>

          <!-- ECSACONM logo -->
          <div class="w-16 h-16 rounded-full flex-shrink-0 flex items-center justify-center overflow-hidden"
            style="background-color: rgb(220,50,75);">
            <img src="@/assets/images/logo.png" class="w-11 h-11 object-contain" alt="ECSACONM" />
          </div>
        </div>

        <div class="h-0.5 w-full mt-3" style="background: linear-gradient(to right, transparent, rgba(254,80,103,0.4), transparent);"></div>
      </header>

      <!-- Name & category -->
      <section class="relative z-10 px-5 pt-1 text-center flex-shrink-0">
        <h1 class="text-2xl font-extrabold text-gray-900 tracking-tight leading-tight mt-1">
          {{ fullName || '—' }}
        </h1>

        <div class="mt-2 py-2 rounded-lg flex items-center justify-center relative overflow-hidden"
          style="background: linear-gradient(to right, #173a4b, #1d4659, #173a4b); border: 1px solid rgba(43,93,115,0.4);">
          <span class="text-xl font-black tracking-[0.14em] text-white uppercase leading-none">{{ categoryLabel }}</span>
        </div>

        <div class="mt-3 space-y-1">
          <span v-if="designation" class="inline-block text-xs font-bold px-3 py-0.5 rounded-full uppercase tracking-wide"
            style="color: rgb(159,18,57); background: rgba(254,80,103,0.06); border: 1px solid rgba(254,80,103,0.3);">
            {{ designation }}
          </span>
          <p v-if="institution" class="text-sm font-bold text-gray-800 tracking-tight leading-snug pt-0.5">{{ institution }}</p>
          <p v-if="country" class="text-xs font-semibold text-gray-500 flex items-center justify-center gap-1">
            <MapPinIcon class="w-3.5 h-3.5 flex-shrink-0" style="color: rgb(254,80,103);" />
            {{ country }}
          </p>
        </div>
      </section>

      <!-- QR + theme -->
      <section class="relative z-10 px-5 py-2 flex flex-col items-center flex-shrink-0">
        <div class="bg-white p-3 rounded-xl flex flex-col items-center" style="border: 1px solid rgba(254,80,103,0.25);">
          <QRCodeVue :value="qrValue" :size="qrSize" foreground="#0f172a" background="#ffffff" />
          <span class="mt-1.5 text-xs font-extrabold tracking-wider uppercase" style="color: rgb(220,50,75);">
            ID #{{ registrationId ?? '—' }}
          </span>
        </div>

        <div v-if="event.theme" class="mt-2 px-3 text-center">
          <p class="text-[11px] italic text-gray-500 leading-tight">
            <span class="font-bold not-italic uppercase tracking-wide text-[10px]" style="color: rgb(220,50,75);">Theme:</span>
            "{{ event.theme }}"
          </p>
        </div>
      </section>

      <!-- Footer -->
      <footer class="relative text-white overflow-hidden flex-shrink-0 mt-auto">
        <div class="relative py-3 px-4 overflow-hidden"
          style="background: linear-gradient(to right, rgb(220,50,75), rgb(254,80,103), rgb(214,44,68)); border-top: 1px solid rgba(254,80,103,0.3);">
          <svg class="absolute inset-0 w-full h-full pointer-events-none" style="opacity: 0.15; color: #ffffff;" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="badge-african-motif" width="28" height="28" patternUnits="userSpaceOnUse">
                <polygon points="14,2 26,14 14,26 2,14" fill="none" stroke="currentColor" stroke-width="1.2" />
                <polygon points="14,6 22,14 14,22 6,14" fill="currentColor" opacity="0.25" />
                <line x1="14" y1="2" x2="14" y2="26" stroke="currentColor" stroke-width="0.8" stroke-dasharray="1 2" />
                <line x1="2" y1="14" x2="26" y2="14" stroke="currentColor" stroke-width="0.8" stroke-dasharray="1 2" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#badge-african-motif)" />
          </svg>
          <div class="relative z-10">
            <div class="flex items-center justify-between text-[10px] font-semibold pb-1.5 mb-1.5" style="border-bottom: 1px solid rgba(255,255,255,0.25);">
              <span class="flex items-center gap-1">
                <CalendarIcon class="w-3.5 h-3.5 flex-shrink-0" />
                <span v-html="event.dateRangeHtml"></span>
              </span>
              <span class="font-bold uppercase tracking-wider text-[9px]">www.ecsaconm.org</span>
            </div>
            <div v-if="event.location" class="flex items-center justify-center gap-1 text-center text-[10px] tracking-tight leading-tight">
              <MapPinIcon class="w-3 h-3 flex-shrink-0" />
              <span>{{ event.location }}</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
import QRCodeVue from 'qrcode.vue'
import { MapPinIcon, CalendarIcon } from '@heroicons/vue/24/solid'
import { formatBadgeCategory } from '@/utils/badgeCategory'
import { ordinalizeHtml } from '@/utils/badgeEvent'

export default {
  name: 'BadgeCard',
  components: { QRCodeVue, MapPinIcon, CalendarIcon },
  props: {
    // { fullName, designation, category (raw role key), institution, country, registrationId }
    participant: { type: Object, required: true },
    // { title: { ordinal, org, subtitle, pill }, theme, dateRangeHtml, location }
    event: {
      type: Object,
      default: () => ({ title: { ordinal: '', org: 'ECSACONM', subtitle: '', pill: '' } }),
    },
    qrValue: { type: String, required: true },
    qrSize: { type: Number, default: 108 },
  },
  computed: {
    fullName() { return this.participant.fullName || '' },
    designation() { return this.participant.designation || '' },
    institution() { return this.participant.institution || '' },
    country() { return this.participant.country || '' },
    registrationId() { return this.participant.registrationId },
    categoryLabel() { return formatBadgeCategory(this.participant.category) },
    titleOrdinalHtml() { return ordinalizeHtml(this.event.title?.ordinal || '') },
    titlePillHtml() { return ordinalizeHtml(this.event.title?.pill || '') },
  },
}
</script>

<style scoped>
.badge-card-a5-wrap {
  width: 100%;
  max-width: 380px;
}
.badge-card-a5 {
  width: 100%;
  /* A5 proportions (148mm x 210mm) — the downloaded PDF is a true A5 page.
     Height is intrinsic (not a forced aspect-ratio) so longer names,
     institutions or themes never get clipped by the card. */
}
</style>
