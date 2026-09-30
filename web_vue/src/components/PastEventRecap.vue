<template>
  <div class="recap bg-[#0e0f13] text-white">

    <!-- ── Section navigator (desktop) ─────────────────────────────────────── -->
    <nav class="hidden lg:flex fixed right-5 top-1/2 -translate-y-1/2 z-40 flex-col gap-3" aria-label="Sections">
      <button v-for="s in sections" :key="s.id" type="button" @click="goTo(s.id)"
        class="group flex items-center justify-end gap-3" :aria-label="s.label">
        <span class="text-xs font-semibold px-2 py-1 rounded-full bg-black/60 backdrop-blur-sm transition-all duration-300 opacity-0 translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 group-focus-visible:opacity-100">
          {{ s.label }}
        </span>
        <span class="block rounded-full transition-all duration-300"
          :class="activeSection === s.id ? 'h-3 w-3 bg-[rgb(254,80,103)] ring-4 ring-[rgba(254,80,103,0.3)]' : 'h-2 w-2 bg-white/50 group-hover:bg-white'"></span>
      </button>
    </nav>

    <!-- ── HERO CAROUSEL ─────────────────────────────────────────────────────── -->
    <section id="recap-hero" ref="hero" data-section
      class="recap-section relative overflow-hidden bg-black h-[calc(100svh-4rem)] sm:h-[calc(100svh-5rem)] min-h-[520px]"
      @touchstart.passive="onTouchStart" @touchend.passive="onTouchEnd">

      <div v-for="(p, i) in slides" :key="p.id" class="absolute inset-0 transition-opacity duration-[1400ms] ease-in-out"
        :class="i === current ? 'opacity-100 z-[1]' : 'opacity-0 z-0'" :aria-hidden="i !== current">
        <img v-if="loaded[i]" :key="i === current ? `on-${kbCycle}` : 'off'" :src="p.full" :alt="p.caption"
          class="h-full w-full object-cover" :class="i === current ? (i % 2 ? 'kb-out' : 'kb-in') : ''"
          :style="{ objectPosition: 'center 35%' }" decoding="async" />
      </div>

      <!-- Overlays -->
      <div class="absolute inset-0 z-[2] bg-gradient-to-t from-black/85 via-black/25 to-black/40 pointer-events-none"></div>

      <!-- Progress bar -->
      <div class="absolute top-0 left-0 right-0 z-[3] h-1 bg-white/15">
        <div :key="`pb-${kbCycle}`" class="h-full bg-[rgb(254,80,103)] progress"
          :class="{ paused: isPaused }" :style="{ animationDuration: `${interval}ms` }"></div>
      </div>

      <!-- Back -->
      <button type="button" @click="$emit('back')"
        class="absolute top-5 left-4 sm:left-6 z-[4] inline-flex items-center gap-2 px-4 py-2 rounded-full bg-black/40 hover:bg-black/60 backdrop-blur-sm text-sm font-semibold transition">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        Home
      </button>

      <!-- Counter -->
      <div class="absolute top-6 right-4 sm:right-6 lg:right-24 z-[4] text-sm font-semibold tabular-nums text-white/80">
        {{ pad(current + 1) }} <span class="text-white/40">/ {{ pad(slides.length) }}</span>
      </div>

      <!-- Text -->
      <div class="absolute inset-x-0 bottom-0 z-[4] px-5 sm:px-10 lg:px-16 pb-28 sm:pb-36">
        <div class="max-w-4xl hero-intro">
          <span class="inline-block text-xs sm:text-sm font-semibold px-3 py-1 rounded-full bg-[rgb(254,80,103)] mb-4">
            Past Event · Photos &amp; Recap
          </span>
          <h1 class="text-2xl sm:text-4xl lg:text-5xl font-black leading-tight drop-shadow-lg mb-3"
            v-html="formatOrdinals(event.event)"></h1>
          <div class="flex flex-wrap gap-x-5 gap-y-1 text-sm sm:text-base text-white/85 mb-4">
            <span>{{ formatDate(event.start_date) }} – {{ formatDate(event.end_date) }}</span>
            <span v-if="event.location">{{ event.location }}</span>
          </div>
          <Transition name="caption" mode="out-in">
            <p :key="current" class="text-sm sm:text-base text-white/75 italic border-l-2 border-[rgb(254,80,103)] pl-3">
              {{ slides[current]?.caption }}
            </p>
          </Transition>
        </div>
      </div>

      <!-- Arrows -->
      <button type="button" @click="prev" aria-label="Previous photo"
        class="absolute left-3 sm:left-6 top-1/2 -translate-y-1/2 z-[4] h-11 w-11 sm:h-12 sm:w-12 rounded-full bg-black/35 hover:bg-[rgb(254,80,103)] backdrop-blur-sm flex items-center justify-center transition">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <button type="button" @click="next" aria-label="Next photo"
        class="absolute right-3 sm:right-6 lg:right-24 top-1/2 -translate-y-1/2 z-[4] h-11 w-11 sm:h-12 sm:w-12 rounded-full bg-black/35 hover:bg-[rgb(254,80,103)] backdrop-blur-sm flex items-center justify-center transition">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
      </button>

      <!-- Thumbnail strip -->
      <div class="absolute inset-x-0 bottom-4 sm:bottom-6 z-[4] px-5 sm:px-10 lg:px-16">
        <div ref="strip" class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
          <button v-for="(p, i) in slides" :key="`t-${p.id}`" type="button" @click="show(i)"
            :aria-label="`Show photo ${i + 1}`"
            class="flex-shrink-0 h-12 w-16 sm:h-16 sm:w-24 rounded-lg overflow-hidden transition-all duration-300"
            :class="i === current ? 'ring-2 ring-[rgb(254,80,103)] opacity-100 scale-105' : 'opacity-50 hover:opacity-90'">
            <img :src="p.thumb" alt="" loading="lazy" class="h-full w-full object-cover" />
          </button>
        </div>
      </div>

      <!-- Scroll cue -->
      <button type="button" @click="goTo(chapters[0]?.id)" aria-label="Scroll to the photo story"
        class="hidden sm:flex absolute bottom-28 right-6 lg:right-24 z-[4] flex-col items-center gap-1 text-xs text-white/70 hover:text-white">
        <span>Scroll</span>
        <svg class="w-5 h-5 bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
      </button>
    </section>

    <!-- ── THEME ─────────────────────────────────────────────────────────────── -->
    <section v-if="event.theme" id="recap-theme" data-section class="recap-section py-20 sm:py-28 px-6 text-center">
      <p data-reveal class="reveal text-xs uppercase tracking-[0.3em] text-[rgb(254,80,103)] font-bold mb-5">Conference theme</p>
      <p data-reveal class="reveal text-2xl sm:text-4xl font-black max-w-3xl mx-auto leading-snug" style="transition-delay: 120ms">
        “{{ event.theme }}”
      </p>
      <p data-reveal class="reveal mt-6 text-white/60 max-w-xl mx-auto" style="transition-delay: 240ms">
        Thank you to every delegate, speaker, partner and volunteer who made it happen. Here is the week in pictures.
      </p>
    </section>

    <!-- ── PHOTO STORY CHAPTERS ──────────────────────────────────────────────── -->
    <section v-for="(ch, ci) in chapters" :key="ch.id" :id="ch.id" data-section
      class="recap-section py-16 sm:py-24 px-4 sm:px-8 lg:px-16"
      :class="ci % 2 ? 'bg-[#15161c]' : 'bg-[#0e0f13]'">
      <div class="max-w-6xl mx-auto">
        <div class="mb-8 sm:mb-10 max-w-2xl" :class="ci % 2 ? 'ml-auto text-right' : ''">
          <p data-reveal class="reveal text-5xl sm:text-7xl font-black text-white/10 leading-none">{{ pad(ci + 1) }}</p>
          <h2 data-reveal class="reveal text-2xl sm:text-4xl font-black -mt-4 sm:-mt-7" style="transition-delay: 80ms">{{ ch.title }}</h2>
          <p data-reveal class="reveal mt-3 text-white/65 text-sm sm:text-base" style="transition-delay: 160ms">{{ ch.text }}</p>
        </div>

        <div class="grid grid-flow-row-dense grid-cols-2 md:grid-cols-4 auto-rows-[140px] sm:auto-rows-[190px] gap-3 sm:gap-4">
          <button v-for="(p, pi) in ch.photos" :key="p.id" type="button" data-reveal
            @click="openLightbox(indexOf(p))"
            class="reveal reveal-photo group relative overflow-hidden rounded-2xl bg-white/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[rgb(254,80,103)]"
            :class="tileClass(ch.photos.length, pi, ci)"
            :style="{ transitionDelay: `${pi * 90}ms` }">
            <img :src="p.thumb" :data-full="p.full" :alt="p.caption" loading="lazy"
              class="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-110"
              @load="upgrade($event, pi, ch.photos.length)" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/75 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <p class="absolute left-3 right-3 bottom-3 text-left text-xs sm:text-sm font-medium translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
              {{ p.caption }}
            </p>
          </button>
        </div>
      </div>
    </section>

    <!-- ── FULL GALLERIES & RESOURCES ────────────────────────────────────────── -->
    <section v-if="photoLinks.length || recapLinks.length || documents.length" id="recap-galleries" data-section
      class="recap-section py-16 sm:py-24 px-4 sm:px-8 lg:px-16 bg-gradient-to-b from-[#0e0f13] to-[#1b0f14]">
      <div class="max-w-5xl mx-auto">
        <div class="text-center mb-10">
          <h2 data-reveal class="reveal text-2xl sm:text-4xl font-black">See every moment</h2>
          <p data-reveal class="reveal mt-3 text-white/65" style="transition-delay: 100ms">
            Browse and download the full photo galleries, presentations and conference documents.
          </p>
        </div>

        <div v-if="photoLinks.length" class="grid gap-4 sm:grid-cols-2 mb-8">
          <a v-for="(link, li) in photoLinks" :key="link.id" :href="link.link" target="_blank" rel="noopener"
            data-reveal class="reveal group flex items-center gap-4 p-5 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-[rgb(254,80,103)] transition"
            :style="{ transitionDelay: `${li * 100}ms` }">
            <div class="h-14 w-14 rounded-2xl flex items-center justify-center flex-shrink-0 bg-[rgb(254,80,103)]">
              <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-bold">{{ link.link_name || link.name }}</p>
              <p class="text-xs text-white/50 truncate">{{ linkHost(link.link) }}</p>
            </div>
            <span class="text-sm font-semibold text-[rgb(254,80,103)] group-hover:translate-x-1 transition">Open →</span>
          </a>
        </div>

        <ul v-if="recapLinks.length || documents.length" class="space-y-3">
          <li v-for="link in recapLinks" :key="`l-${link.id}`" data-reveal
            class="reveal flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
            <p class="flex-1 min-w-0 text-sm font-bold truncate">{{ link.link_name || link.name }}</p>
            <a :href="link.link" target="_blank" rel="noopener"
              class="px-5 py-2 rounded-full text-sm font-semibold bg-[rgb(220,50,75)] hover:opacity-90 transition flex-shrink-0">Open</a>
          </li>
          <li v-for="file in documents" :key="`d-${file.id}`" data-reveal
            class="reveal flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold truncate">{{ file.name || file.file_name }}</p>
              <p class="text-xs text-white/50">{{ formatDocType(file.document_type) }}</p>
            </div>
            <a :href="`${apiUrl}/${file.path}`" target="_blank" rel="noopener"
              class="px-5 py-2 rounded-full text-sm font-semibold bg-[rgb(254,80,103)] hover:opacity-90 transition flex-shrink-0">Download</a>
          </li>
        </ul>

        <div class="text-center mt-12">
          <router-link :to="{ name: 'WebEvent', params: { id: event.id } }"
            class="inline-block px-7 py-3 rounded-full font-semibold text-sm border-2 border-white/30 hover:border-white transition">
            Event details
          </router-link>
        </div>
      </div>
    </section>

    <!-- ── LIGHTBOX ─────────────────────────────────────────────────────────── -->
    <Transition name="fade">
      <div v-if="lightbox !== null" class="fixed inset-0 z-[100] bg-black/95 flex items-center justify-center"
        role="dialog" aria-modal="true" @click.self="closeLightbox"
        @touchstart.passive="onTouchStart" @touchend.passive="onTouchEnd">
        <button type="button" @click="closeLightbox" aria-label="Close"
          class="absolute top-4 right-4 h-11 w-11 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
        <button type="button" @click="lbStep(-1)" aria-label="Previous photo"
          class="absolute left-2 sm:left-6 h-12 w-12 rounded-full bg-white/10 hover:bg-[rgb(254,80,103)] flex items-center justify-center transition">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <figure class="max-w-[92vw] max-h-[88vh] flex flex-col items-center">
          <Transition name="lb" mode="out-in">
            <img :key="lightbox" :src="slides[lightbox].full" :alt="slides[lightbox].caption"
              class="max-w-[92vw] max-h-[80vh] object-contain rounded-lg shadow-2xl" />
          </Transition>
          <figcaption class="mt-4 text-sm text-white/80 text-center px-12">
            {{ slides[lightbox].caption }}
            <span class="ml-2 text-white/40 tabular-nums">{{ lightbox + 1 }} / {{ slides.length }}</span>
          </figcaption>
        </figure>
        <button type="button" @click="lbStep(1)" aria-label="Next photo"
          class="absolute right-2 sm:right-6 h-12 w-12 rounded-full bg-white/10 hover:bg-[rgb(254,80,103)] flex items-center justify-center transition">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script>
export default {
  name: 'PastEventRecap',
  props: {
    event: { type: Object, required: true },
    story: { type: Object, required: true },
    links: { type: Array, default: () => [] },
    documents: { type: Array, default: () => [] },
  },
  emits: ['back'],
  data() {
    return {
      apiUrl: import.meta.env.VITE_API_URL,
      current: 0,
      kbCycle: 0,
      loaded: [],
      interval: 6000,
      timer: null,
      heroVisible: true,
      pageHidden: false,
      lightbox: null,
      activeSection: 'recap-hero',
      touchX: null,
      observers: [],
    }
  },
  computed: {
    chapters() {
      return this.story.chapters || []
    },
    slides() {
      return this.chapters.flatMap(c => c.photos)
    },
    sections() {
      const s = [{ id: 'recap-hero', label: 'Highlights' }]
      if (this.event.theme) s.push({ id: 'recap-theme', label: 'Theme' })
      this.chapters.forEach(c => s.push({ id: c.id, label: c.title }))
      if (this.photoLinks.length || this.recapLinks.length || this.documents.length) {
        s.push({ id: 'recap-galleries', label: 'Galleries' })
      }
      return s
    },
    photoLinks() {
      return this.links.filter(l => this.isPhotoLink(l))
    },
    recapLinks() {
      return this.links.filter(l => !this.isPhotoLink(l))
    },
    isPaused() {
      return !this.heroVisible || this.pageHidden || this.lightbox !== null
    },
  },
  watch: {
    isPaused(paused) {
      paused ? this.stop() : this.start()
    },
  },
  mounted() {
    this.loaded = this.slides.map((_, i) => i < 2 || i === this.slides.length - 1)
    document.documentElement.classList.add('recap-snap')
    document.addEventListener('keydown', this.onKey)
    document.addEventListener('visibilitychange', this.onVisibility)
    this.$nextTick(() => {
      this.observeReveals()
      this.observeSections()
      this.start()
    })
  },
  beforeUnmount() {
    this.stop()
    document.documentElement.classList.remove('recap-snap')
    document.removeEventListener('keydown', this.onKey)
    document.removeEventListener('visibilitychange', this.onVisibility)
    document.body.style.overflow = ''
    this.observers.forEach(o => o.disconnect())
  },
  methods: {
    // ── carousel ──
    start() {
      this.stop()
      if (this.isPaused) return
      this.timer = setTimeout(() => { this.next(); }, this.interval)
    },
    stop() {
      clearTimeout(this.timer)
      this.timer = null
    },
    show(i) {
      const n = this.slides.length
      this.current = (i + n) % n
      // load current + neighbours only, so the page doesn't pull every full-size photo up front
      ;[this.current, this.current + 1, this.current - 1].forEach(k => { this.loaded[(k + n) % n] = true })
      this.kbCycle++
      this.scrollStripToCurrent()
      this.start()
    },
    next() { this.show(this.current + 1) },
    prev() { this.show(this.current - 1) },
    scrollStripToCurrent() {
      const strip = this.$refs.strip
      const el = strip?.children[this.current]
      if (!el) return
      strip.scrollTo({ left: el.offsetLeft - strip.clientWidth / 2 + el.clientWidth / 2, behavior: 'smooth' })
    },
    onTouchStart(e) {
      this.touchX = e.changedTouches[0].clientX
    },
    onTouchEnd(e) {
      if (this.touchX === null) return
      const dx = e.changedTouches[0].clientX - this.touchX
      this.touchX = null
      if (Math.abs(dx) < 40) return
      const dir = dx < 0 ? 1 : -1
      this.lightbox !== null ? this.lbStep(dir) : this.show(this.current + dir)
    },
    onKey(e) {
      if (this.lightbox !== null) {
        if (e.key === 'Escape') this.closeLightbox()
        else if (e.key === 'ArrowRight') this.lbStep(1)
        else if (e.key === 'ArrowLeft') this.lbStep(-1)
      } else if (this.heroVisible) {
        if (e.key === 'ArrowRight') this.next()
        else if (e.key === 'ArrowLeft') this.prev()
      }
    },
    onVisibility() {
      this.pageHidden = document.hidden
    },

    // ── lightbox ──
    indexOf(p) {
      return this.slides.indexOf(p)
    },
    openLightbox(i) {
      this.lightbox = i
      document.body.style.overflow = 'hidden'
    },
    closeLightbox() {
      this.lightbox = null
      document.body.style.overflow = ''
    },
    lbStep(d) {
      const n = this.slides.length
      this.lightbox = (this.lightbox + d + n) % n
    },

    // ── scroll animation ──
    goTo(id) {
      const el = id && document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    },
    observeReveals() {
      const io = new IntersectionObserver((entries) => {
        entries.forEach(en => {
          if (en.isIntersecting) {
            en.target.classList.add('is-visible')
            io.unobserve(en.target)
          }
        })
      }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' })
      this.$el.querySelectorAll('[data-reveal]').forEach(el => io.observe(el))
      this.observers.push(io)
    },
    observeSections() {
      const io = new IntersectionObserver((entries) => {
        entries.forEach(en => {
          if (en.target.id === 'recap-hero') this.heroVisible = en.intersectionRatio > 0.35
          if (en.isIntersecting && en.intersectionRatio > 0.35) this.activeSection = en.target.id
        })
      }, { threshold: [0, 0.35, 0.6] })
      this.$el.querySelectorAll('[data-section]').forEach(el => io.observe(el))
      this.observers.push(io)
    },

    // ── mosaic ──
    tileClass(count, i, chapterIndex) {
      // the first photo of each chapter is the feature tile (alternating sides); the rest fill a 4-column grid
      if (count === 2) return 'col-span-2 row-span-2'
      if (i === 0) return ['col-span-2 row-span-2', chapterIndex % 2 ? 'md:col-start-3' : ''].join(' ')
      if (count === 3) return 'col-span-1 md:col-span-2'
      if (count === 6 && i === 5) return 'col-span-2 md:col-span-4 row-span-2'
      return ''
    },
    isLargeTile(count, i) {
      return count === 2 || i === 0 || count === 3 || (count === 6 && i === 5)
    },
    upgrade(e, i, count) {
      // large tiles swap the thumbnail for the full image once the thumb is shown
      if (!this.isLargeTile(count, i)) return
      const img = e.target
      const full = img.dataset.full
      if (!full) return
      img.dataset.full = ''
      const hi = new Image()
      hi.onload = () => { img.src = full }
      hi.src = full
    },

    // ── formatting ──
    pad(n) {
      return String(n).padStart(2, '0')
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
      const map = { ProgrammeBooklet: 'Programme Booklet', Presentation: 'Presentation', Photo: 'Photo', Advert: 'Advert', Guidelines: 'Guidelines' }
      return map[type] || 'Document'
    },
    isPhotoLink(link) {
      return /photo|gallery|album|picture/i.test(link.link_name || link.name || '')
    },
    linkHost(url) {
      try { return new URL(url).hostname.replace(/^www\./, '') } catch { return url }
    },
  },
}
</script>

<style>
/* Smooth, section-to-section scrolling while the recap is on screen */
html.recap-snap {
  overflow-anchor: none;
  scroll-behavior: smooth;
  scroll-snap-type: y proximity;
  scroll-padding-top: 4rem;
}
@media (min-width: 640px) {
  html.recap-snap { scroll-padding-top: 5rem; }
}
@media (prefers-reduced-motion: reduce) {
  html.recap-snap { scroll-behavior: auto; scroll-snap-type: none; }
}
</style>

<style scoped>
.recap-section { scroll-snap-align: start; }

/* Ken Burns */
.kb-in { animation: kbIn 9s ease-out both; }
.kb-out { animation: kbOut 9s ease-out both; }
@keyframes kbIn { from { transform: scale(1.02) translate(0, 0); } to { transform: scale(1.14) translate(-1.5%, -1%); } }
@keyframes kbOut { from { transform: scale(1.14) translate(1.5%, 1%); } to { transform: scale(1.03) translate(0, 0); } }

/* Autoplay progress */
.progress { width: 0; animation-name: grow; animation-timing-function: linear; animation-fill-mode: forwards; }
.progress.paused { animation-play-state: paused; }
@keyframes grow { to { width: 100%; } }

/* Hero text entrance */
.hero-intro { animation: rise 1s cubic-bezier(.2,.7,.2,1) both .2s; }
@keyframes rise { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: none; } }

.bounce { animation: bounce 1.8s infinite; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(6px); } }

/* Scroll reveal */
.reveal { opacity: 0; transform: translateY(36px); transition: opacity .8s ease, transform .8s cubic-bezier(.2,.7,.2,1); }
.reveal-photo { transform: translateY(40px) scale(.96); }
.reveal.is-visible { opacity: 1; transform: none; }

.caption-enter-active, .caption-leave-active { transition: opacity .5s ease, transform .5s ease; }
.caption-enter-from { opacity: 0; transform: translateY(8px); }
.caption-leave-to { opacity: 0; transform: translateY(-8px); }

.fade-enter-active, .fade-leave-active { transition: opacity .3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.lb-enter-active, .lb-leave-active { transition: opacity .25s ease, transform .25s ease; }
.lb-enter-from { opacity: 0; transform: scale(.97); }
.lb-leave-to { opacity: 0; transform: scale(1.02); }

.no-scrollbar { scrollbar-width: none; }
.no-scrollbar::-webkit-scrollbar { display: none; }

@media (prefers-reduced-motion: reduce) {
  .kb-in, .kb-out, .hero-intro, .bounce { animation: none; }
  .reveal, .reveal-photo { opacity: 1; transform: none; transition: none; }
}
</style>
