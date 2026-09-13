<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle" />

    <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start gap-3">
      <search-component @search="handleSearch" />
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-500">
          {{ total }} presentation{{ total !== 1 ? 's' : '' }} uploaded
        </span>
        <!-- Batch download toolbar -->
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Batch</span>
          <button @click="downloadPresentationsZip(null)" :disabled="zipDownloading"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition disabled:opacity-40"
            style="border-color: rgb(0,150,180); color: rgb(0,150,180);">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            All ({{ total }})
          </button>
          <button @click="downloadPresentationsZip('oral')" :disabled="zipDownloading"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition disabled:opacity-40">
            Oral ({{ oralCount }})
          </button>
          <button @click="downloadPresentationsZip('poster')" :disabled="zipDownloading"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition disabled:opacity-40">
            Poster ({{ posterCount }})
          </button>
          <span v-if="zipDownloading" class="text-xs text-gray-400 italic">Preparing ZIP…</span>
          <span v-if="zipError" class="text-xs text-red-500">{{ zipError }}</span>
        </div>
      </div>
    </div>

    <div v-if="replaceMsg"
      class="px-3 py-2 rounded-md text-sm"
      :class="replaceErr ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'">
      {{ replaceMsg }}
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
          <div class="flex items-center gap-1.5">
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
            <button @click="replacePresentation(row)" :disabled="replacingId === row.id"
              title="Replace the uploaded file"
              class="inline-flex items-center gap-1 px-3 py-1 text-xs rounded-full font-semibold border transition hover:opacity-90 disabled:opacity-40"
              style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ replacingId === row.id ? 'Replacing…' : 'Replace' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <pagination-component
      :currentPage="currentPage"
      :totalPages="totalPages"
      @page-change="handlePageChange" />

    <input type="file" ref="replaceFileInput" class="hidden"
      :accept="acceptedExtensions" @change="onReplaceFileChange" />
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import { useAuthStore } from '@/store/authStore'
import { saveAs } from 'file-saver'
import axios from 'axios'

export default {
  name: 'UploadedPresentationsView',
  components: { HeaderView, SpinnerComponent, PaginationComponent, SearchComponent },

  data() {
    return {
      headerTitle: 'Uploaded Presentations',
      rows: [],
      total: 0,
      oralCount: 0,
      posterCount: 0,
      isLoading: true,
      currentPage: 1,
      pageSize: 20,
      searchPhrase: '',
      apiUrl: import.meta.env.VITE_API_URL,
      zipDownloading: false, zipError: '',
      replacingId: null,
      replaceTarget: null,
      replaceMsg: '', replaceErr: false,
      acceptedExtensions: '.pdf,.pptx,.jpg,.jpeg,.png,.gif,.bmp,.webp',
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
        this.oralCount = res.data.oral_count || 0
        this.posterCount = res.data.poster_count || 0
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

    async downloadPresentationsZip(presentationType) {
      this.zipDownloading = true
      this.zipError = ''
      try {
        const params = {}
        if (presentationType) params.presentation_type = presentationType
        const res = await axios.get(`${this.apiUrl}/abstracts/download-presentations-zip`, {
          params,
          headers: { Authorization: `Bearer ${this.accessToken}` },
          responseType: 'blob',
        })
        saveAs(res.data, `presentations_${presentationType || 'all'}.zip`)
      } catch (e) {
        const blob = e.response?.data
        if (blob instanceof Blob) {
          try { this.zipError = JSON.parse(await blob.text())?.detail || 'No matching presentations found to download.' }
          catch { this.zipError = 'No matching presentations found to download.' }
        } else {
          this.zipError = e.response?.data?.detail || 'No matching presentations found to download.'
        }
      } finally {
        this.zipDownloading = false
      }
    },

    presenterName(row) {
      return row.presenting_author?.name || row.submitter_name || '—'
    },

    replacePresentation(row) {
      this.replaceTarget = row
      this.replaceMsg = ''
      this.replaceErr = false
      this.$refs.replaceFileInput.value = ''
      this.$refs.replaceFileInput.click()
    },
    async onReplaceFileChange(e) {
      const file = e.target.files && e.target.files[0]
      if (!file || !this.replaceTarget) return
      const id = this.replaceTarget.id
      this.replacingId = id
      this.replaceMsg = ''
      this.replaceErr = false
      try {
        const form = new FormData()
        form.append('file', file)
        const res = await axios.post(`${this.apiUrl}/abstracts/${id}/upload-presentation`, form, {
          headers: {
            Authorization: `Bearer ${this.accessToken}`,
            'Content-Type': 'multipart/form-data',
          },
        })
        this.replaceMsg = `Replaced "${this.replaceTarget.title.slice(0, 60)}" — upload successful.`
        this.replaceErr = false
        await this.load()
      } catch (err) {
        this.replaceMsg = err.response?.data?.detail || 'Replace failed.'
        this.replaceErr = true
      } finally {
        this.replacingId = null
        this.replaceTarget = null
      }
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
