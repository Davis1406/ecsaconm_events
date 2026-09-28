<template>
  <div class="min-h-screen bg-gray-50 text-gray-800">
    <!-- Hero -->
    <div class="px-4 pt-12 pb-14" style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(180,30,55) 100%);">
      <div class="max-w-xl mx-auto text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 mb-4">
          <svg class="w-9 h-9 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 class="text-white text-2xl sm:text-3xl font-bold">Certificate Verification</h1>
        <p class="text-white/85 text-sm mt-1.5">
          This confirms the holder of this certificate attended the conference as stated below.
        </p>
      </div>
    </div>

    <div class="max-w-xl mx-auto px-4 -mt-6 pb-14">
      <div class="bg-white rounded-2xl shadow-lg shadow-black/5 border border-gray-100 p-6 sm:p-8">
        <!-- Green tick verification -->
        <div class="flex flex-col items-center text-center">
          <div class="w-14 h-14 rounded-full flex items-center justify-center bg-green-100">
            <svg class="w-7 h-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="mt-3 text-lg font-bold text-gray-900">Verified Certificate</h2>
          <p class="mt-1 text-sm text-gray-500">
            The certificate presented with this code has been issued by ECSACONM.
          </p>
        </div>

        <div class="mt-6 pt-6 border-t border-gray-100">
          <p class="text-sm text-gray-700 leading-relaxed">
            This is to confirm <span class="font-bold text-gray-900">{{ displayName }}</span>
            attended <span class="font-bold text-gray-900">{{ displayEvent }}</span>,
            from 14th to 18th September 2026 at Golden Tulip Airport Hotel, Zanzibar,
            and was awarded this certificate.
          </p>
        </div>

        <div class="mt-6 pt-6 border-t border-gray-100">
          <div class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">For further enquiries please contact</div>
          <div class="text-sm text-gray-600 space-y-1">
            <p><span class="font-semibold text-gray-500">Address:</span> Plot No. 157, Oloirien Njiro Road, P.O. Box 1009, Arusha, Tanzania</p>
            <p><span class="font-semibold text-gray-500">Tel:</span> +255-27-254 9362, +255-27-254 9365 / 9366</p>
            <p><span class="font-semibold text-gray-500">Fax:</span> +255-27-254 9392</p>
            <p><span class="font-semibold text-gray-500">Email:</span> info@ecsaconm.org (General enquiries)</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CertificateVerificationView',
  computed: {
    displayName() {
      const n = (this.$route.query.name || '').trim()
      return n || 'the certificate holder'
    },
    displayEvent() {
      const e = (this.$route.query.event || '').trim()
      return e || 'the ECSACONM conference'
    },
  },
}
</script>