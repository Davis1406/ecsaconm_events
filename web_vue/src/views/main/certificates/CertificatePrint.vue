<template>
  <div class="cert-print" :style="{ '--s': scale }">
    <div class="cert-toolbar">
      <button type="button" @click="print" :disabled="!ready">Print / Save as PDF</button>
      <span v-if="type">
        {{ names.length }} {{ type.label }} certificate{{ names.length === 1 ? '' : 's' }} ·
        in the print dialog choose "Save as PDF" and turn on "Background graphics".
      </span>
      <span v-else>No certificates to print — generate them from the Certificates page.</span>
    </div>

    <template v-if="type">
      <div v-for="(name, i) in names" :key="i" class="cert-page">
        <CertificateSheet ref="sheets" :name="name" :type="type" :event-name="eventName" :uid="i" />
      </div>
    </template>
  </div>
</template>

<script>
import CertificateSheet from '@/components/CertificateSheet.vue'
import { CERTIFICATE_TYPES, CERTIFICATE_JOB_KEY, ensureCertificateFonts } from '@/utils/certificateTypes'

export default {
  name: 'CertificatePrintView',
  components: { CertificateSheet },
  data() {
    return { type: null, names: [], eventName: '', scale: 1, ready: false, autoPrint: false }
  },
  created() {
    // Written by Certificates.vue just before opening this tab. Left in place
    // so a refresh of this tab still works.
    try {
      const job = JSON.parse(localStorage.getItem(CERTIFICATE_JOB_KEY) || 'null')
      if (job && CERTIFICATE_TYPES[job.type] && Array.isArray(job.names)) {
        this.type = CERTIFICATE_TYPES[job.type]
        this.names = job.names
        this.eventName = job.eventName || ''
        this.autoPrint = !!job.autoPrint
      }
    } catch (e) { /* no job */ }
    document.title = this.type ? `ECSACONM Certificates - ${this.type.label}` : 'ECSACONM Certificates'
  },
  async mounted() {
    this.fit()
    window.addEventListener('resize', this.fit)
    // Load the certificate fonts explicitly — fonts.ready alone can resolve
    // before the @font-face requests are issued, which renders the preview
    // with fallback fonts and overlaps "Certificate" / "OF PARTICIPATION".
    await ensureCertificateFonts()
    ;(this.$refs.sheets || []).forEach(s => { s.fitName(); s.fitBody() })
    this.ready = true
    if (this.autoPrint && this.names.length) {
      // Only auto-open the dialog on the first load, not on refresh.
      try {
        const job = JSON.parse(localStorage.getItem(CERTIFICATE_JOB_KEY))
        localStorage.setItem(CERTIFICATE_JOB_KEY, JSON.stringify({ ...job, autoPrint: false }))
      } catch (e) { /* ignore */ }
      this.print()
    }
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.fit)
  },
  methods: {
    // Scale the on-screen preview to the window; print uses the real 1920x1080.
    fit() {
      this.scale = Math.min(1, (window.innerWidth - 48) / 1920)
    },
    print() {
      window.print()
    },
  },
}
</script>

<style>
/* Certificate @font-face rules live in CertificateSheet.vue so the email-preview
   render in Certificates.vue gets them too. */
.cert-print, .cert-print * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

@page { size: 1920px 1080px; margin: 0; }

@media screen {
  .cert-print { min-height: 100vh; background: #e9ecef; }
  .cert-toolbar { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: #fff; border-bottom: 1px solid #e5e7eb; font-size: 14px; color: #555; }
  .cert-toolbar button { background: rgb(254, 80, 103); color: #fff; border-radius: 12px; padding: 8px 16px; font-size: 13px; font-weight: 600; }
  .cert-toolbar button:disabled { opacity: .5; }
  .cert-page { width: calc(1920px * var(--s)); height: calc(1080px * var(--s)); margin: 16px auto; overflow: hidden; box-shadow: 0 2px 8px rgba(0, 0, 0, .15); }
  .cert-page > .cert { transform: scale(var(--s)); transform-origin: top left; }
}

@media print {
  html, body { margin: 0 !important; padding: 0 !important; background: #fff !important; }
  .cert-toolbar { display: none !important; }
  .cert-page { break-after: page; page-break-after: always; }
  .cert-page:last-child { break-after: auto; page-break-after: auto; }
}
</style>
