<template>
  <div class="min-h-screen bg-gray-50 font-roboto">

    <!-- ─── Hero ──────────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden text-white"
      style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(180,30,55) 60%, rgb(120,10,30) 100%);">
      <!-- Decorative rings -->
      <div class="absolute -top-20 -right-20 w-80 h-80 rounded-full opacity-10" style="background: #fff;"></div>
      <div class="absolute -bottom-12 -left-12 w-56 h-56 rounded-full opacity-10" style="background: #fff;"></div>

      <div class="relative z-10 max-w-5xl mx-auto px-6 py-16 sm:py-24 text-center">
        <div class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-medium mb-6">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          ECSACONM Secretariat
        </div>
        <h1 class="text-4xl sm:text-5xl font-black mb-4 drop-shadow-sm">Get In Touch</h1>
        <p class="text-lg text-white/80 max-w-xl mx-auto leading-relaxed">
          Reach out to the ECSACONM Secretariat for enquiries about events, registration, abstract submissions, or any other information.
        </p>
      </div>
    </section>

    <!-- ─── Contact Cards ─────────────────────────────────────────────────────── -->
    <section class="max-w-5xl mx-auto px-6 -mt-8 relative z-10">
      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">

        <!-- Address -->
        <div class="bg-white rounded-2xl shadow-md p-6 flex flex-col gap-4 hover:shadow-lg transition-shadow">
          <div class="h-12 w-12 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-sm uppercase tracking-wide mb-2" style="color: rgb(254,80,103);">Address</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              P.O. Box 30893<br />
              Lilongwe 3<br />
              Malawi
            </p>
          </div>
        </div>

        <!-- Phone -->
        <div class="bg-white rounded-2xl shadow-md p-6 flex flex-col gap-4 hover:shadow-lg transition-shadow">
          <div class="h-12 w-12 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(220,50,75);">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-sm uppercase tracking-wide mb-2" style="color: rgb(220,50,75);">Phone</h3>
            <a href="tel:+2651771541" class="text-gray-600 text-sm hover:underline block">+265 1 771 541</a>
            <p class="text-gray-400 text-xs mt-2">Mon – Fri · 08:00 – 17:00 (CAT)</p>
          </div>
        </div>

        <!-- Email -->
        <div class="bg-white rounded-2xl shadow-md p-6 flex flex-col gap-4 hover:shadow-lg transition-shadow">
          <div class="h-12 w-12 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-sm uppercase tracking-wide mb-2" style="color: rgb(254,80,103);">Email</h3>
            <a href="mailto:info@ecsaconm.org" class="text-gray-600 text-sm hover:underline break-all block">
              info@ecsaconm.org
            </a>
          </div>
        </div>

        <!-- Website -->
        <div class="bg-white rounded-2xl shadow-md p-6 flex flex-col gap-4 hover:shadow-lg transition-shadow">
          <div class="h-12 w-12 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(220,50,75);">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9" />
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-sm uppercase tracking-wide mb-2" style="color: rgb(220,50,75);">Website</h3>
            <a href="https://www.ecsaconm.org" target="_blank" class="text-gray-600 text-sm hover:underline block">
              www.ecsaconm.org
            </a>
          </div>
        </div>

      </div>
    </section>

    <!-- ─── About + Contact Form ───────────────────────────────────────────────── -->
    <section class="max-w-5xl mx-auto px-6 py-12 grid gap-8 md:grid-cols-5">

      <!-- About ECSACONM -->
      <div class="md:col-span-2 bg-white rounded-2xl shadow-md p-7 flex flex-col justify-between">
        <div>
          <h2 class="text-xl font-bold text-gray-800 mb-4" style="color: rgb(254,80,103);">About ECSACONM</h2>
          <p class="text-gray-600 text-sm leading-relaxed mb-4">
            The Eastern, Central and Southern Africa College of Nursing and Midwifery (ECSACONM) is a regional body that brings together nursing and midwifery professionals across the region.
          </p>
          <p class="text-gray-600 text-sm leading-relaxed mb-4">
            ECSACONM promotes the advancement of nursing and midwifery education, practice, and research through biennial scientific conferences and other regional programmes.
          </p>
          <div class="space-y-2 text-sm text-gray-600">
            <div class="flex items-center gap-2">
              <span class="h-1.5 w-1.5 rounded-full flex-shrink-0" style="background-color: rgb(254,80,103);"></span>
              Regional nursing &amp; midwifery body
            </div>
            <div class="flex items-center gap-2">
              <span class="h-1.5 w-1.5 rounded-full flex-shrink-0" style="background-color: rgb(220,50,75);"></span>
              Biennial scientific conferences
            </div>
            <div class="flex items-center gap-2">
              <span class="h-1.5 w-1.5 rounded-full flex-shrink-0" style="background-color: rgb(254,80,103);"></span>
              Secretariat: Lilongwe, Malawi
            </div>
          </div>
        </div>
        <a href="https://www.ecsaconm.org" target="_blank"
          class="mt-6 inline-block text-center text-sm font-semibold px-5 py-2.5 rounded-full text-white transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          Visit ECSACONM Website →
        </a>
      </div>

      <!-- Contact Form -->
      <div class="md:col-span-3 bg-white rounded-2xl shadow-md p-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-1">Send Us a Message</h2>
        <p class="text-gray-500 text-sm mb-6">Fill in the form below and the Secretariat will get back to you within 2 business days.</p>

        <form @submit.prevent="sendMessage" class="space-y-4">
          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input v-model="form.name" type="text" required placeholder="Jane Doe"
                class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 transition"
                style="--tw-ring-color: rgba(254,80,103,0.5);" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <input v-model="form.email" type="email" required placeholder="jane@example.org"
                class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 transition" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Organisation</label>
            <input v-model="form.organisation" type="text" placeholder="Ministry of Health, Tanzania"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 transition" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
            <select v-model="form.subject"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 transition">
              <option disabled value="">Select a subject</option>
              <option>Event Registration Enquiry</option>
              <option>Abstract Submission</option>
              <option>Sponsorship &amp; Exhibition</option>
              <option>Logistics &amp; Accommodation</option>
              <option>Scientific Programme</option>
              <option>General Enquiry</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
            <textarea v-model="form.message" rows="5" required placeholder="Write your message here..."
              class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 transition"></textarea>
          </div>

          <!-- Success feedback -->
          <div v-if="sent" class="flex items-center gap-2 text-green-600 bg-green-50 border border-green-200 rounded-xl px-4 py-3 text-sm">
            <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Thank you! Your message has been received. The Secretariat will be in touch shortly.
          </div>

          <button type="submit" :disabled="sending"
            class="w-full sm:w-auto px-8 py-3 rounded-full font-semibold text-white text-sm transition hover:opacity-90 disabled:opacity-60"
            style="background-color: rgb(254,80,103);">
            {{ sending ? 'Sending…' : 'Send Message' }}
          </button>
        </form>
      </div>

    </section>

  </div>
</template>

<script>
export default {
  name: 'ContactView',
  data() {
    return {
      sending: false,
      sent: false,
      form: {
        name: '',
        email: '',
        organisation: '',
        subject: '',
        message: '',
      }
    }
  },
  methods: {
    async sendMessage() {
      this.sending = true
      // Simulate sending — replace with real API call if a contact endpoint is added
      await new Promise(resolve => setTimeout(resolve, 1200))
      this.sent = true
      this.sending = false
      this.form = { name: '', email: '', organisation: '', subject: '', message: '' }
    }
  }
}
</script>
