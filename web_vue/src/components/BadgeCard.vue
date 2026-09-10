<template>
  <div class="badge-card-a5 relative bg-white rounded-3xl shadow-xl overflow-hidden mx-auto" style="border: 1px solid rgba(30,58,69,0.08);">

    <!-- Lanyard clip -->
    <div class="absolute left-1/2 -translate-x-1/2 -top-3 w-9 h-12 rounded-t-md flex items-start justify-center pt-1.5"
      style="background-color: rgb(220,50,75);">
      <span class="w-2.5 h-2.5 rounded-full bg-white/80"></span>
    </div>

    <div class="pt-9 px-6 flex flex-col items-center text-center">

      <!-- Logo row -->
      <div class="w-full flex items-center justify-between">
        <div class="w-14 h-14 rounded-full overflow-hidden flex items-center justify-center bg-white flex-shrink-0"
          style="border: 2px solid rgb(220,50,75);">
          <img src="@/assets/images/ecsalogo.png" class="w-full h-full object-contain p-1" alt="ECSA" />
        </div>
        <div class="w-14 h-14 rounded-full overflow-hidden flex items-center justify-center flex-shrink-0"
          style="background-color: rgb(220,50,75);">
          <img src="@/assets/images/logo.png" class="w-9 h-9 object-contain" alt="ECSACONM" />
        </div>
      </div>

      <!-- Event title -->
      <p class="mt-2 text-lg font-extrabold uppercase leading-tight" style="color: rgb(30,58,69);">
        {{ event.title || 'ECSACONM' }}
      </p>
      <span v-if="event.subtitle" class="mt-2 inline-block px-3 py-1 rounded-full text-[11px] font-semibold"
        style="background-color: rgba(220,50,75,0.08); color: rgb(220,50,75);">
        {{ event.subtitle }}
      </span>

      <!-- Name -->
      <p class="mt-5 text-2xl font-extrabold leading-tight" style="color: rgb(30,58,69);">
        {{ fullName || '—' }}
      </p>

      <!-- Category bar -->
      <div class="mt-3 w-full py-2 rounded-lg text-white font-extrabold text-base tracking-widest uppercase"
        style="background-color: rgb(30,58,69);">
        {{ categoryLabel }}
      </div>

      <!-- Designation pill -->
      <span v-if="designation" class="mt-3 inline-block px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wide"
        style="background-color: rgba(220,50,75,0.08); color: rgb(220,50,75); border: 1px solid rgba(220,50,75,0.35);">
        {{ designation }}
      </span>

      <!-- Institution & Country -->
      <p v-if="institution" class="mt-3 text-sm font-bold" style="color: rgb(30,58,69);">{{ institution }}</p>
      <p v-if="country" class="mt-1 flex items-center justify-center gap-1 text-xs font-semibold"
        style="color: rgb(220,50,75);">
        <MapPinIcon class="w-3.5 h-3.5" /> {{ country }}
      </p>

      <!-- QR code -->
      <div class="mt-5 relative p-3">
        <span class="absolute top-0 left-0 w-5 h-5 border-t-2 border-l-2 rounded-tl-md" style="border-color: rgb(220,50,75);"></span>
        <span class="absolute top-0 right-0 w-5 h-5 border-t-2 border-r-2 rounded-tr-md" style="border-color: rgb(220,50,75);"></span>
        <span class="absolute bottom-0 left-0 w-5 h-5 border-b-2 border-l-2 rounded-bl-md" style="border-color: rgb(220,50,75);"></span>
        <span class="absolute bottom-0 right-0 w-5 h-5 border-b-2 border-r-2 rounded-br-md" style="border-color: rgb(220,50,75);"></span>
        <QRCodeVue :value="qrValue" :size="qrSize" foreground="#000000" background="#ffffff" />
      </div>
      <p class="mt-1 text-sm font-extrabold" style="color: rgb(220,50,75);">ID #{{ registrationId ?? '—' }}</p>

      <p v-if="event.theme" class="mt-2 text-[11px] italic px-4 pb-5 leading-snug" style="color: rgb(220,50,75);">
        <span class="font-semibold not-italic">Theme:</span> "{{ event.theme }}"
      </p>
      <div v-else class="pb-5"></div>
    </div>

    <!-- Footer bar -->
    <div class="flex items-center justify-between gap-2 px-4 py-2 text-white text-[11px] font-semibold"
      style="background-color: rgb(30,58,69);">
      <span class="flex items-center gap-1">
        <CalendarIcon class="w-3.5 h-3.5 flex-shrink-0" /> {{ event.dateRange || '—' }}
      </span>
      <span class="uppercase">www.ecsaconm.org</span>
    </div>

    <!-- Sub footer -->
    <div v-if="event.location" class="flex items-center justify-center gap-1 px-4 py-1.5 text-[10px] font-semibold"
      style="background-color: rgba(220,50,75,0.08); color: rgb(220,50,75);">
      <MapPinIcon class="w-3 h-3 flex-shrink-0" /> {{ event.location }}
    </div>
  </div>
</template>

<script>
import QRCodeVue from 'qrcode.vue'
import { MapPinIcon, CalendarIcon } from '@heroicons/vue/24/solid'
import { formatBadgeCategory } from '@/utils/badgeCategory'

export default {
  name: 'BadgeCard',
  components: { QRCodeVue, MapPinIcon, CalendarIcon },
  props: {
    // { fullName, designation, category (raw role key), institution, country, registrationId }
    participant: { type: Object, required: true },
    // { title, subtitle, theme, dateRange, location }
    event: { type: Object, default: () => ({}) },
    qrValue: { type: String, required: true },
    qrSize: { type: Number, default: 120 },
  },
  computed: {
    fullName() { return this.participant.fullName || '' },
    designation() { return this.participant.designation || '' },
    institution() { return this.participant.institution || '' },
    country() { return this.participant.country || '' },
    registrationId() { return this.participant.registrationId },
    categoryLabel() { return formatBadgeCategory(this.participant.category) },
  },
}
</script>

<style scoped>
.badge-card-a5 {
  width: 100%;
  /* A5 proportions (148mm x 210mm) — the downloaded PDF is a true A5 page;
     this keeps the on-screen preview visually matching that ratio. */
  max-width: 380px;
}
</style>
