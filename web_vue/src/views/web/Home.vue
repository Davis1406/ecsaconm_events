<template>
  <div class="min-h-screen bg-gray-50">

    <!-- ── HERO: Featured Event ─────────────────────────────────────────────── -->
    <section v-if="featuredEvent" class="relative w-full overflow-hidden" style="min-height: 480px;">
      <!-- Background: banner image or ECSACONM gradient -->
      <div class="absolute inset-0 bg-center bg-cover" :style="heroBgStyle"></div>
      <!-- Dark overlay -->
      <div class="absolute inset-0" :style="heroOverlayStyle"></div>

      <div class="relative z-10 max-w-5xl mx-auto px-6 py-16 sm:py-28 text-white text-center">
        <!-- Org badge -->
        <div class="mb-4 inline-flex items-center gap-2">
          <span class="text-sm font-semibold px-3 py-1 rounded-full bg-white/20 backdrop-blur-sm">ECSACONM</span>
        </div>

        <!-- Event name with ordinal superscripts -->
        <h1 class="text-3xl sm:text-5xl font-black leading-tight mb-4 drop-shadow-lg"
          v-html="formatOrdinals(featuredEvent.event)"></h1>

        <!-- Theme -->
        <p v-if="featuredEvent.theme" class="text-base sm:text-xl text-white/90 font-medium mb-6 max-w-2xl mx-auto">
          {{ featuredEvent.theme }}
        </p>

        <!-- Date & Location -->
        <div class="flex flex-wrap justify-center gap-4 text-sm sm:text-base text-white/90 mb-8">
          <div class="flex items-center gap-2">
            <svg class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <span>{{ formatDate(featuredEvent.start_date) }} – {{ formatDate(featuredEvent.end_date) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <svg class="h-5 w-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5 8a5 5 0 1110 0c0 3-5 9-5 9S5 11 5 8zm5-2a2 2 0 100 4 2 2 0 000-4z" clip-rule="evenodd"/>
            </svg>
            <span>{{ featuredEvent.location }}</span>
          </div>
        </div>

        <!-- CTA Buttons -->
        <div class="flex flex-wrap justify-center gap-3">
          <router-link v-if="isRegistrationOpen"
            :to="{ name: 'Register' }"
            class="inline-block px-8 py-3 rounded-full font-semibold text-sm sm:text-base shadow-lg transition hover:opacity-90 hover:-translate-y-0.5"
            style="background-color: rgb(254,80,103); color: #fff;">
            Register for conference →
          </router-link>
          <span v-else
            class="inline-block px-8 py-3 rounded-full font-semibold text-sm sm:text-base bg-white/20 text-white/60 cursor-not-allowed">
            Registration Closed
          </span>

        </div>

        <!-- View details -->
        <div class="mt-5">
          <router-link :to="{ name: 'WebEvent', params: { id: featuredEvent.id } }"
            class="text-sm text-white/80 underline hover:text-white">
            View event details
          </router-link>
        </div>
      </div>
    </section>

    <!-- Spinner while loading -->
    <div v-if="isLoading && !featuredEvent" class="flex justify-center py-24">
      <svg class="animate-spin h-10 w-10 text-bondi-blue-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <!-- ── MORE UPCOMING EVENTS ──────────────────────────────────────────────── -->
    <section v-if="otherEvents.length > 0" class="max-w-7xl mx-auto px-4 sm:px-6 py-12">
      <h2 class="text-2xl sm:text-3xl font-bold text-gray-800 mb-8">Upcoming Events</h2>
      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="event in otherEvents" :key="event.id"
          class="bg-white rounded-2xl shadow-sm overflow-hidden hover:shadow-md transition-shadow">
          <!-- Top accent bar -->
          <div class="h-2 w-full" style="background-color: rgb(254,80,103);"></div>
          <!-- Banner or gradient fallback -->
          <div v-if="event.banner_image" class="h-40 w-full bg-center bg-cover"
            :style="{ backgroundImage: `url('${apiUrl}/${event.banner_image}')` }"></div>
          <div v-else class="h-20 w-full flex items-center justify-center"
            style="background: linear-gradient(135deg, rgb(254,80,103), rgb(220,50,75));">
            <span class="text-white font-bold text-lg opacity-70">ECSACONM</span>
          </div>
          <!-- Card body -->
          <div class="p-5 space-y-3">
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full text-white" style="background-color: rgb(254,80,103);">ECSACONM</span>
            <h3 class="text-base font-bold text-gray-800 leading-snug">{{ event.event }}</h3>
            <p v-if="event.theme" class="text-sm text-gray-500 italic line-clamp-2">{{ event.theme }}</p>
            <div class="flex items-center gap-2 text-gray-600 text-sm">
              <svg class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <span>{{ formatDate(event.start_date) }}</span>
            </div>
            <div class="flex items-center gap-2 text-gray-600 text-sm">
              <svg class="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5 8a5 5 0 1110 0c0 3-5 9-5 9S5 11 5 8zm5-2a2 2 0 100 4 2 2 0 000-4z" clip-rule="evenodd"/>
              </svg>
              <span>{{ event.location }}</span>
            </div>
            <router-link :to="{ name: 'WebEvent', params: { id: event.id } }"
              class="mt-2 inline-block text-sm font-semibold px-4 py-1.5 rounded-full border-2 border-bondi-blue-500 text-bondi-blue-500 hover:bg-bondi-blue-500 hover:text-white transition">
              View Details
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- No events state (when not loading and nothing featured) -->
    <div v-if="!isLoading && !featuredEvent" class="text-center py-24 text-gray-400">
      <svg class="mx-auto h-12 w-12 mb-4 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
      </svg>
      <p class="text-lg font-medium">No upcoming events at the moment.</p>
      <p class="text-sm mt-1">Check back soon!</p>
    </div>

    <!-- ── CONTACT CTA STRIP ──────────────────────────────────────────────── -->
    <section class="mt-12" style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(220,50,75) 100%);">
      <div class="max-w-5xl mx-auto px-6 py-10 flex flex-col sm:flex-row items-center justify-between gap-6 text-white">
        <div>
          <h2 class="text-xl sm:text-2xl font-bold mb-1">Have a question about an event?</h2>
          <p class="text-white/80 text-sm">Reach out to the ECSACONM Secretariat · info@ecsaconm.org</p>
        </div>
        <router-link :to="{ name: 'Contact' }"
          class="flex-shrink-0 px-7 py-3 rounded-full font-semibold text-sm bg-white text-bondi-blue-500 hover:bg-gray-100 transition shadow-lg">
          Contact Us →
        </router-link>
      </div>
    </section>

  </div>
</template>

<script>
import { fetchData } from '@/services/apiService'
import goldenTulip from '@/assets/images/golden-tulip.avif'

export default {
  name: 'HomeView',
  data() {
    return {
      isLoading: true,
      featuredEvent: null,
      otherEvents: [],
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },
  computed: {
    isRegistrationOpen() {
      if (!this.featuredEvent?.start_date) return false
      const diffDays = (new Date(this.featuredEvent.start_date) - new Date()) / (1000 * 60 * 60 * 24)
      return diffDays >= 0
    },
    heroBgStyle() {
      if (!this.featuredEvent) return {}
      if (this.featuredEvent.banner_image) {
        return { backgroundImage: `url('${this.apiUrl}/${this.featuredEvent.banner_image}')` }
      }
      return { backgroundImage: `url('${goldenTulip}')` }
    },
    heroOverlayStyle() {
      // always use a dark overlay so text stays readable over the photo
      const opacity = this.featuredEvent?.banner_image ? '0.55' : '0.60'
      return { backgroundColor: `rgba(0,0,0,${opacity})` }
    }
  },
  async mounted() {
    try {
      const response = await fetchData('events/active/', 0, 100, '')
      const all = (response.data || []).sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
      this.featuredEvent = all[0] || null
      this.otherEvents = all.slice(1)
    } catch (e) {
      console.error('Error fetching events:', e)
    } finally {
      this.isLoading = false
    }
  },
  methods: {
    formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    },
    formatOrdinals(text) {
      if (!text) return ''
      return text.replace(/(\d+)(st|nd|rd|th)\b/gi, (_, num, suffix) =>
        `${num}<sup style="font-size:0.55em;vertical-align:super;">${suffix}</sup>`)
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
