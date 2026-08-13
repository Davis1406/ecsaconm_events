<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle" />

    <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start gap-3">
      <search-component @search="handleSearch" />
      <div class="text-sm text-gray-500">
        {{ total }} presentation{{ total !== 1 ? 's' : '' }} uploaded
      </div>
    </div>

    <SpinnerComponent v-if="isLoading" />

    <div v-else class="rounded-md border-2 border-white-600 shadow-sm text-abbey-500">
      <!-- Header row -->
      <div class="flex bg-mercury-500 p-3 pt-2 pb-2 rounded-t-sm uppercase text-xs font-bold">
        <div class="w-1/12 p-1">#</div>
        <div class="w-3/12 p-1">Abstract Title</div>
        <div class="w-2/12 p-1">Presenter</div>
        <div class="w-2/12 p-1">Event</div>
        <div class="w-2/12 p-1">Uploaded</div>
        <div class="w-2/12 p-1">Download</div>
      </div>

      <div v-if="rows.length === 0" class="p-8 text-center text-sm text-gray-400 italic">
        No presentations uploaded yet.
      </div>

      <div v-for="(row, index) in rows" :key="row.id"
        class="flex sm:flex-row flex-col p-3 pt-2 pb-2 text-sm items-center border-t-2 border-mercury-500 hover:bg-ghost-300">
        <div class="sm:w-1/12 w-full p-1 text-gray-400">{{ (currentPage - 1) * pageSize + index + 1 }}</div>
        <div class="sm:w-3/12 w-full p-1 font-medium">
          <router-link :to="{ name: 'Abstract', params: { id: row.id } }"
            class="hover:underline" style="color: rgb(0,150,180);">
            {{ row.title }}
          </router-link>
        </div>
        <div class="sm:w-2/12 w-full p-1 text-xs">
          <div class="font-medium">{{ presenterName(row) }}</div>
          <div class="text-gray-400">{{ presenterEmail(row) }}</div>
        </div>
        <div class="sm:w-2/12 w-full p-1 text-xs text-gray-600">{{ row.event }}</div>
        <div class="sm:w-2/12 w-full p-1 text-xs text-gray-500">{{ formatDate(row.presentation_uploaded_at) }}</div>
        <div class="sm:w-2/12 w-full p-1">
          <a :href="`${apiUrl}/abstracts/${row.id}/download-presentation`"
            target="_blank"
            class="inline-flex items-center gap-1 px-3 py-1 text-xs rounded-full font-semibold text-white transition hover:opacity-90"
            style="background-color: rgb(0,150,180);">
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </a>
        </div>
      </div>
    </div>

    <pagination-component
      :currentPage="currentPage"
      :totalPages="totalPages"
      @page-change="handlePageChange" />
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import { useAuthStore } from '@/store/authStore'
import axios from 'axios'

export default {
  name: 'UploadedPresentationsView',
  components: { HeaderView, SpinnerComponent, PaginationComponent, SearchComponent },

  data() {
    return {
      headerTitle: 'Uploaded Presentations',
      rows: [],
      total: 0,
      isLoading: true,
      currentPage: 1,
      pageSize: 20,
      searchPhrase: '',
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },

  computed: {
    totalPages() {
      return Math.max(1, Math.ceil(this.total / this.pageSize))
    },
  },

  setup() {
    const authStore = useAuthStore()
    return { accessToken: authStore.accessToken }
  },

  mounted() {
    this.load()
  },

  methods: {
    async load() {
      this.isLoading = true
      try {
        const skip = (this.currentPage - 1) * this.pageSize
        const res = await axios.get(`${this.apiUrl}/abstracts/uploaded-presentations/list`, {
          params: { skip, limit: this.pageSize, search: this.searchPhrase },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.rows = res.data.data || []
        this.total = res.data.total || 0
      } catch (e) {
        console.error('Error loading uploaded presentations:', e)
      } finally {
        this.isLoading = false
      }
    },

    handleSearch(q) {
      this.searchPhrase = q
      this.currentPage = 1
      this.load()
    },

    handlePageChange(page) {
      this.currentPage = page
      this.load()
    },

    presenterName(row) {
      return row.presenting_author?.name || row.submitter_name || '—'
    },

    presenterEmail(row) {
      return row.presenting_author?.email || row.submitter_email || ''
    },

    formatDate(iso) {
      if (!iso) return '—'
      return new Date(iso).toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
      })
    },
  },
}
</script>
