<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-10">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-800">Discover Upcoming Events</h1>
      <p class="text-sm text-gray-500 mt-1">Browse ECSACONM conferences, workshops, and scientific events</p>
    </div>

    <!-- Search bar -->
    <div class="bg-white rounded-2xl shadow-sm p-4 mb-8 flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <input v-model="search" type="text" placeholder="Search events..."
          class="w-full border border-gray-300 rounded-xl px-4 py-2.5 pl-10 text-sm focus:outline-none focus:ring-2 focus:ring-bondi-blue-500 transition"/>
        <svg class="h-5 w-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z"/>
        </svg>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-20">
      <svg class="animate-spin h-10 w-10 text-bondi-blue-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <!-- No events -->
    <div v-else-if="filteredEvents.length === 0" class="text-center py-20 text-gray-400">
      <svg class="mx-auto h-12 w-12 mb-4 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
      </svg>
      <p class="text-lg font-medium">No events found.</p>
    </div>

    <!-- Events grid -->
    <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <router-link v-for="event in paginatedEvents" :key="event.id"
        :to="{ name: 'WebEvent', params: { id: event.id } }"
        class="bg-white rounded-2xl shadow-sm overflow-hidden hover:shadow-md hover:-translate-y-1 transition-all duration-200 flex flex-col">
        <!-- Accent bar -->
        <div class="h-2 w-full" style="background-color: rgb(254,80,103);"></div>
        <!-- Banner or gradient -->
        <div v-if="event.banner_image" class="h-40 bg-center bg-cover"
          :style="{ backgroundImage: `url('${apiUrl}/${event.banner_image}')` }"></div>
        <div v-else class="h-24 flex items-center justify-center font-bold text-white text-lg opacity-80"
          style="background: linear-gradient(135deg, rgb(254,80,103), rgb(220,50,75));">ECSACONM</div>

        <div class="p-5 flex flex-col flex-1 space-y-2">
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full text-white w-fit" style="background-color:rgb(254,80,103);">ECSACONM</span>
          <h3 class="text-base font-bold text-gray-800 leading-snug">{{ event.event }}</h3>
          <p v-if="event.theme" class="text-sm text-gray-500 italic line-clamp-2">{{ event.theme }}</p>
          <div class="flex items-center gap-2 text-gray-600 text-sm mt-auto pt-2">
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
          <span class="mt-3 inline-block text-xs font-semibold px-4 py-1.5 rounded-full border-2 border-bondi-blue-500 text-bondi-blue-500 w-fit">
            View Details →
          </span>
        </div>
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-10 flex justify-center items-center gap-2">
      <button @click="currentPage--" :disabled="currentPage === 1"
        class="px-4 py-2 rounded-xl border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-40 transition text-sm">
        ← Prev
      </button>
      <button v-for="p in totalPages" :key="p" @click="currentPage = p"
        class="px-4 py-2 rounded-xl border text-sm font-medium transition"
        :class="currentPage === p ? 'bg-bondi-blue-500 text-white border-bondi-blue-500' : 'border-gray-300 text-gray-600 hover:bg-gray-100'">
        {{ p }}
      </button>
      <button @click="currentPage++" :disabled="currentPage === totalPages"
        class="px-4 py-2 rounded-xl border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-40 transition text-sm">
        Next →
      </button>
    </div>
  </div>
</template>

<script>
import { fetchData } from '@/services/apiService'

export default {
  name: 'WebEventsView',
  data() {
    return {
      isLoading: true,
      events: [],
      search: '',
      currentPage: 1,
      perPage: 9,
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },
  computed: {
    filteredEvents() {
      const q = this.search.toLowerCase()
      if (!q) return this.events
      return this.events.filter(e =>
        e.event?.toLowerCase().includes(q) ||
        e.theme?.toLowerCase().includes(q) ||
        e.location?.toLowerCase().includes(q)
      )
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredEvents.length / this.perPage))
    },
    paginatedEvents() {
      const start = (this.currentPage - 1) * this.perPage
      return this.filteredEvents.slice(start, start + this.perPage)
    }
  },
  watch: {
    search() { this.currentPage = 1 }
  },
  async mounted() {
    try {
      const res = await fetchData('events/active/', 0, 100, '')
      this.events = (res.data || []).sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
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
