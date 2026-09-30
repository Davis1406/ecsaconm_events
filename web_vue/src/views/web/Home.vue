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
            :to="{ name: 'EventRegister', params: { id: featuredEvent.id } }"
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

    <!-- ── INFORMATION NOTE / DOWNLOADS ─────────────────────────────────── -->
    <section v-if="publicDocuments.length" class="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      <div class="bg-white rounded-2xl shadow-lg overflow-hidden border-t-4"
        style="border-color: rgb(254,80,103);">
        <div class="px-6 py-4 flex items-center gap-3 border-b border-gray-100">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-bold" style="color: rgb(254,80,103);">Information Note</h2>
            <p class="text-xs text-gray-400">Official conference documents &amp; resources</p>
          </div>
        </div>
        <div class="px-6 py-5">
          <ul class="space-y-3">
            <li v-for="file in publicDocuments" :key="file.id"
              class="group flex items-center gap-4 p-4 rounded-xl bg-gray-50 hover:bg-pink-50 transition border border-transparent hover:border-pink-200">
              <div class="h-11 w-11 rounded-xl flex items-center justify-center flex-shrink-0"
                style="background-color: rgb(254,80,103);">
                <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-bold text-gray-800 truncate">{{ file.name || file.file_name }}</p>
                <p class="text-xs text-gray-400 capitalize">{{ formatDocType(file.document_type) }}</p>
              </div>
              <a :href="`${apiUrl}/${file.path}`" target="_blank" rel="noopener"
                class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full text-sm font-semibold text-white transition hover:opacity-90 flex-shrink-0 shadow-sm"
                style="background-color: rgb(254,80,103);">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download
              </a>
            </li>
          </ul>
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

    <!-- ── NO CURRENT EVENT → PAST EVENT PHOTOS & RECAP ─────────────────── -->
    <div v-if="!isLoading && !featuredEvent && pastEvent" class="bg-[#fff7f8]">
    <Transition name="stage" mode="out-in" @before-enter="toTop" @after-enter="toTop">
      <section v-if="!isLoading && !featuredEvent && pastEvent && !showRecap" key="intro"
        class="relative overflow-hidden bg-black flex items-center justify-center min-h-[calc(100svh-4rem)] sm:min-h-[calc(100svh-5rem)]">
        <!-- Drifting photo wall -->
        <div v-if="introPhotos.length" class="absolute inset-0 photo-wall" aria-hidden="true">
          <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-3 photo-wall-inner">
            <div v-for="(p, i) in introPhotos" :key="`w-${i}`" class="aspect-[4/3] rounded-xl overflow-hidden">
              <img :src="p.thumb" alt="" class="h-full w-full object-cover" />
            </div>
          </div>
        </div>
        <div v-else class="absolute inset-0 bg-center bg-cover" :style="pastHeroBgStyle"></div>
        <div class="absolute inset-0 bg-gradient-to-b from-black/60 via-black/45 to-black/65"></div>

        <div class="relative z-10 max-w-3xl mx-auto px-6 py-16 text-center text-white intro-content">
          <span class="inline-flex items-center gap-2 text-sm font-semibold px-3 py-1 rounded-full bg-white/15 backdrop-blur-sm mb-6">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            ECSACONM Events
          </span>
          <h1 class="text-3xl sm:text-5xl font-black leading-tight mb-4 drop-shadow-lg">No current event for now</h1>
          <p class="text-base sm:text-lg text-white/80 mb-10">
            Our next event will be announced here soon. In the meantime, look back at our most recent conference.
          </p>

          <div class="rounded-2xl bg-black/35 backdrop-blur-md border border-white/20 px-6 py-6 sm:px-8 mb-8">
            <p class="text-xs uppercase tracking-[0.25em] font-bold mb-2" style="color: rgb(254,80,103);">Past event</p>
            <p class="text-lg sm:text-2xl font-bold leading-snug" v-html="formatOrdinals(pastEvent.event)"></p>
            <p class="text-sm text-white/70 mt-2">
              {{ formatDate(pastEvent.start_date) }} – {{ formatDate(pastEvent.end_date) }}
              <span v-if="pastEvent.location"> · {{ pastEvent.location }}</span>
            </p>
          </div>

          <button v-if="pastStory" type="button" @click="openRecap"
            class="cta-pulse inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-base shadow-lg transition hover:-translate-y-0.5"
            style="background-color: rgb(254,80,103); color: #fff;">
            Click here to view the past event
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
          </button>
          <router-link v-else :to="{ name: 'WebEvent', params: { id: pastEvent.id } }"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-base shadow-lg"
            style="background-color: rgb(254,80,103); color: #fff;">
            Click here to view the past event →
          </router-link>
        </div>
      </section>

      <PastEventRecap v-else-if="!isLoading && !featuredEvent && pastEvent && showRecap" key="recap"
        :event="pastEvent" :story="pastStory" :links="pastLinks" :documents="pastDocuments"
        @back="closeRecap" />
    </Transition>
    </div>

    <!-- No events state (when not loading and nothing featured or past) -->
    <div v-if="!isLoading && !featuredEvent && !pastEvent" class="text-center py-24 text-gray-400">
      <svg class="mx-auto h-12 w-12 mb-4 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
      </svg>
      <p class="text-lg font-medium">No upcoming events at the moment.</p>
      <p class="text-sm mt-1">Check back soon!</p>
    </div>

    <!-- ── CONTACT CTA STRIP ──────────────────────────────────────────────── -->
    <section :class="!featuredEvent && pastEvent ? '' : 'mt-12'" style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(220,50,75) 100%);">
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
import { fetchData, fetchItem } from '@/services/apiService'
import goldenTulip from '@/assets/images/golden-tulip.avif'
import PastEventRecap from '@/components/PastEventRecap.vue'
import { photosForEvent } from '@/data/pastEventPhotos'

export default {
  name: 'HomeView',
  components: { PastEventRecap },
  data() {
    return {
      isLoading: true,
      featuredEvent: null,
      otherEvents: [],
      documents: [],
      pastEvent: null,
      pastLinks: [],
      pastDocuments: [],
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
    },
    pastHeroBgStyle() {
      const img = this.pastEvent?.banner_image
      return { backgroundImage: img ? `url('${this.apiUrl}/${img}')` : `url('${goldenTulip}')` }
    },
    pastStory() {
      return this.pastEvent ? photosForEvent(this.pastEvent.id) : null
    },
    showRecap() {
      return !!this.pastStory && this.$route.query.view === 'past-event'
    },
    introPhotos() {
      // repeat the photo set so the drifting wall always covers the screen
      const all = (this.pastStory?.chapters || []).flatMap(c => c.photos)
      return all.length ? [...all, ...all].slice(0, 36) : []
    },
    publicDocuments() {
      return this.documents.filter(d => (d.access_level || 'public') === 'public')
    }
  },
  async mounted() {
    try {
      const response = await fetchData('events/active', 0, 100, '')
      const all = (response.data || []).sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
      this.featuredEvent = all[0] || null
      this.otherEvents = all.slice(1)
      if (this.featuredEvent) {
        try {
          const res = await fetchItem('events', this.featuredEvent.id)
          this.documents = res.documents || []
        } catch (e) {
          console.error('Error fetching event documents:', e)
        }
      } else {
        await this.loadPastEvent()
      }
    } catch (e) {
      console.error('Error fetching events:', e)
    } finally {
      this.isLoading = false
    }
  },
  methods: {
    // No upcoming event: show the most recent finished event's photos & recap
    async loadPastEvent() {
      try {
        const res = await fetchData('events', 0, 20, '')
        const now = new Date()
        const past = (res.data || [])
          .filter(e => e.end_date && new Date(e.end_date) < now)
          .sort((a, b) => new Date(b.end_date) - new Date(a.end_date))[0]
        if (!past) return
        const detail = await fetchItem('events', past.id)
        const isPublic = x => (x.access_level || 'public') === 'public'
        this.pastEvent = detail.event || past
        this.pastLinks = (detail.links || []).filter(isPublic)
        this.pastDocuments = (detail.documents || []).filter(isPublic)
      } catch (e) {
        console.error('Error fetching past event:', e)
      }
    },
    openRecap() {
      this.$router.push({ query: { ...this.$route.query, view: 'past-event' } })
    },
    closeRecap() {
      const { view, ...rest } = this.$route.query
      this.$router.push({ query: rest })
    },
    toTop() {
      window.scrollTo({ top: 0, behavior: 'instant' })
    },
    formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    },
    formatOrdinals(text) {
      if (!text) return ''
      return text.replace(/(\d+)(st|nd|rd|th)\b/gi, (_, num, suffix) =>
        `${num}<sup style="font-size:0.55em;vertical-align:super;">${suffix}</sup>`)
    },
    formatDocType(type) {
      const map = {
        ProgrammeBooklet: 'Programme Booklet',
        Presentation: 'Presentation',
        Photo: 'Photo',
        Advert: 'Advert',
        Guidelines: 'Guidelines',
        Other: 'Document',
      }
      return map[type] || 'Document'
    }
  }
}
</script>

<style scoped>
/* Intro ⇄ recap page change */
.stage-enter-active { transition: opacity .8s ease, transform .9s cubic-bezier(.2,.7,.2,1); }
.stage-leave-active { transition: opacity .6s ease, transform .6s ease, filter .6s ease; }
.stage-enter-from { opacity: 0; transform: translateY(48px) scale(.98); }
.stage-leave-to { opacity: 0; transform: scale(1.08); filter: blur(8px); }

.photo-wall { overflow: hidden; }
.photo-wall-inner {
  width: 130%;
  margin-left: -15%;
  transform: rotate(-6deg) translateY(-12%);
  animation: drift 40s linear infinite alternate;
}
@keyframes drift {
  from { transform: rotate(-6deg) translate(0, -12%); }
  to { transform: rotate(-6deg) translate(-6%, -30%); }
}
.intro-content { animation: introRise 1s cubic-bezier(.2,.7,.2,1) both; }
@keyframes introRise { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: none; } }
.cta-pulse { animation: pulse 2.4s ease-in-out infinite; }
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(254,80,103,.55); }
  50% { box-shadow: 0 0 0 14px rgba(254,80,103,0); }
}
@media (prefers-reduced-motion: reduce) {
  .photo-wall-inner, .intro-content, .cta-pulse { animation: none; }
  .stage-enter-active, .stage-leave-active { transition: none; }
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
