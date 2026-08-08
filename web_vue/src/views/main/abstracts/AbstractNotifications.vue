<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle" />

    <div class="flex items-center space-x-2">
      <button @click="$router.push({ name: 'Abstracts' })"
        class="px-4 py-2 text-sm bg-mercury-500 hover:bg-mercury-600 text-abbey-500 rounded-md">
        &larr; Back to Abstracts
      </button>
    </div>

    <!-- Global messages -->
    <div class="p-3 px-4 rounded-2xl text-sm bg-green-100 border border-green-400 text-green-800"
      v-if="successMsg">{{ successMsg }}</div>
    <div class="p-3 px-4 rounded-2xl text-sm bg-red-100 border border-red-400 text-red-800"
      v-if="errorMsg">{{ errorMsg }}</div>

    <!-- ── IMPORT SECTION ───────────────────────────────────────────────── -->
    <div class="rounded-2xl border border-gray-100 shadow-sm bg-white p-6 space-y-5">
      <div class="flex sm:flex-row flex-col sm:justify-between sm:items-start gap-3">
        <div>
          <h2 class="text-lg font-bold text-gray-800">Import Abstracts</h2>
          <p class="text-sm text-gray-500 mt-1">
            Upload an ODS or XLSX file exported from your abstract management system.<br/>
            Accepted abstracts will be imported and linked to existing accounts where possible.
          </p>
        </div>
        <!-- Stats badges after preview -->
        <div v-if="importPreview" class="flex flex-wrap gap-2 text-xs font-semibold">
          <span class="px-3 py-1.5 rounded-full bg-blue-100 text-blue-700">
            {{ importPreview.to_import }} to import
          </span>
          <span class="px-3 py-1.5 rounded-full bg-gray-100 text-gray-500">
            {{ importPreview.duplicates }} duplicates
          </span>
          <span class="px-3 py-1.5 rounded-full bg-green-100 text-green-700">
            {{ importPreview.with_accounts }} have accounts
          </span>
          <span class="px-3 py-1.5 rounded-full bg-yellow-100 text-yellow-700">
            {{ importPreview.without_accounts }} no account
          </span>
        </div>
      </div>

      <!-- File input row -->
      <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-end">
        <div class="flex-1">
          <label class="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
            File (.xlsx or .ods)
          </label>
          <input type="file" accept=".xlsx,.ods,.xls"
            @change="onFileSelected"
            class="block w-full text-sm text-gray-700 border border-gray-200 rounded-xl px-3 py-2
                   file:mr-4 file:py-1.5 file:px-4 file:rounded-full file:border-0
                   file:text-xs file:font-semibold file:text-white cursor-pointer
                   focus:outline-none"
            style="--file-bg: rgb(254,80,103);"
            ref="fileInput" />
        </div>

        <button @click="runPreview" :disabled="!importFile || isPreviewLoading"
          class="px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40 whitespace-nowrap"
          style="background-color: rgb(254,80,103);">
          {{ isPreviewLoading ? 'Checking...' : 'Preview Import' }}
        </button>

        <button v-if="importPreview && importPreview.to_import > 0"
          @click="runImport" :disabled="isImporting"
          class="px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40 whitespace-nowrap"
          style="background-color: rgb(220,50,75);">
          {{ isImporting ? 'Importing...' : `Import ${importPreview.to_import} Abstract(s)` }}
        </button>
      </div>

      <!-- Import result banner -->
      <div v-if="importResult"
        class="p-4 rounded-xl border text-sm font-medium"
        :class="importResult.success ? 'bg-green-50 border-green-300 text-green-800' : 'bg-red-50 border-red-300 text-red-800'">
        <div class="font-bold mb-1">{{ importResult.message }}</div>
        <div v-if="importResult.errors && importResult.errors.length" class="mt-2 space-y-1">
          <div v-for="err in importResult.errors" :key="err.row" class="text-xs text-red-600">
            Row {{ err.row }}: {{ err.title }} — {{ err.error }}
          </div>
        </div>
      </div>

      <!-- Preview table -->
      <div v-if="isPreviewLoading" class="py-6 flex justify-center">
        <SpinnerComponent />
      </div>

      <div v-else-if="importPreview && importPreview.rows.length > 0" class="overflow-x-auto rounded-xl border border-gray-100">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-xs font-bold uppercase tracking-wider text-gray-500">
            <tr>
              <th class="px-4 py-3 text-left">#</th>
              <th class="px-4 py-3 text-left">Title</th>
              <th class="px-4 py-3 text-left">Presenter</th>
              <th class="px-4 py-3 text-left">Type</th>
              <th class="px-4 py-3 text-left">Account</th>
              <th class="px-4 py-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in importPreview.rows" :key="i"
              :class="row.is_duplicate ? 'bg-gray-50 opacity-50' : (i % 2 === 0 ? 'bg-white' : 'bg-gray-50/30')"
              class="border-t border-gray-100">
              <td class="px-4 py-2.5 text-gray-400 text-xs">{{ i + 1 }}</td>
              <td class="px-4 py-2.5 text-gray-800 font-medium max-w-xs">
                <div class="truncate" :title="row.title">{{ row.title }}</div>
                <div class="text-xs text-gray-400">{{ row.track }}</div>
              </td>
              <td class="px-4 py-2.5 text-gray-700">
                <div class="font-medium">{{ row.presenter_name }}</div>
                <div class="text-xs text-gray-400">{{ row.presenter_email }}</div>
              </td>
              <td class="px-4 py-2.5">
                <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                  :class="row.presentation_type === 'oral' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'">
                  {{ row.presentation_type }}
                </span>
              </td>
              <td class="px-4 py-2.5">
                <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                  :class="row.has_account ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
                  {{ row.has_account ? 'Has Account' : 'No Account' }}
                </span>
              </td>
              <td class="px-4 py-2.5">
                <span v-if="row.is_duplicate"
                  class="px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-200 text-gray-500">
                  Duplicate — skip
                </span>
                <span v-else
                  class="px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                  Will import
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── REGISTRATION REMINDERS SECTION ──────────────────────────────── -->
    <div class="rounded-2xl border border-gray-100 shadow-sm bg-white p-6 space-y-4">
      <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start gap-3">
        <div>
          <h2 class="text-lg font-bold text-gray-800">Registration Reminders</h2>
          <p class="text-sm text-gray-500 mt-1">
            Accepted abstract presenters who haven't registered for the event yet.
          </p>
        </div>
        <button @click="loadPreview" :disabled="isLoading"
          class="px-4 py-2 text-sm rounded-xl text-white font-semibold hover:opacity-90 disabled:opacity-50 transition"
          style="background-color: rgb(254,80,103);">
          {{ isLoading ? 'Loading...' : 'Refresh List' }}
        </button>
      </div>

      <SpinnerComponent v-if="isLoading" />

      <div v-else-if="presenters.length === 0"
        class="flex flex-col items-center justify-center py-12 text-center">
        <div class="h-14 w-14 rounded-full flex items-center justify-center mb-4"
          style="background-color: rgba(254,80,103,0.1);">
          <svg class="w-7 h-7" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-gray-400 text-sm italic">All presenters have registered — or no abstracts imported yet.</p>
      </div>

      <div v-else class="space-y-3">
        <!-- Summary pills -->
        <div class="flex flex-wrap gap-2 text-xs font-semibold">
          <span class="px-3 py-1.5 rounded-full bg-yellow-100 text-yellow-700">
            {{ presenters.filter(p => !p.has_account).length }} need to create account
          </span>
          <span class="px-3 py-1.5 rounded-full bg-blue-100 text-blue-700">
            {{ presenters.filter(p => p.has_account).length }} have account but not registered
          </span>
        </div>

        <div class="rounded-xl border border-gray-100 overflow-hidden">
          <div class="hidden sm:grid grid-cols-12 gap-2 bg-gray-50 px-5 py-3 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
            <div class="col-span-3">Presenter</div>
            <div class="col-span-3">Email</div>
            <div class="col-span-4">Abstract</div>
            <div class="col-span-2">Account</div>
          </div>

          <div v-for="(presenter, idx) in presenters" :key="presenter.email"
            class="flex sm:grid sm:grid-cols-12 gap-2 items-center px-5 py-3.5 border-b border-gray-50 hover:bg-gray-50 transition text-sm">
            <div class="sm:col-span-3 font-semibold text-gray-800">
              {{ presenter.firstname }} {{ presenter.lastname }}
            </div>
            <div class="sm:col-span-3 text-gray-500 text-xs truncate">{{ presenter.email }}</div>
            <div class="sm:col-span-4 text-gray-700 text-xs line-clamp-2">{{ presenter.abstract_title }}</div>
            <div class="sm:col-span-2">
              <span v-if="presenter.has_account"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                Has Account
              </span>
              <span v-else
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
                No Account
              </span>
            </div>
          </div>
        </div>

        <!-- Send Reminders Button -->
        <div class="flex justify-end gap-3">
          <div class="text-xs text-gray-400 self-center">
            {{ presenters.filter(p => !p.has_account).length }} will receive "create account" email ·
            {{ presenters.filter(p => p.has_account).length }} will receive "register now" email
          </div>
          <button @click="sendReminders" :disabled="isSending"
            class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white hover:opacity-90 disabled:opacity-50 transition"
            style="background-color: rgb(220,50,75);">
            {{ isSending ? 'Sending...' : `Send Reminders to ${presenters.length}` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { fetchDataWithParams, createItem } from '@/services/apiService'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'AbstractNotificationsView',
  components: {
    HeaderView, SpinnerComponent,
  },
  data() {
    return {
      headerTitle: 'Abstract Notifications',

      // ── Import state
      importFile: null,
      isPreviewLoading: false,
      importPreview: null,
      isImporting: false,
      importResult: null,

      // ── Reminder state
      presenters: [],
      isLoading: false,
      isSending: false,
      successMsg: '',
      errorMsg: '',
      eventId: null,
    }
  },
  mounted() {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      this.loadPreview()
    } else {
      // Token not yet hydrated — watch and trigger as soon as it's ready
      const unwatch = this.$watch(
        () => useAuthStore().accessToken,
        (token) => {
          if (token) {
            this.loadPreview()
            unwatch()
          }
        }
      )
    }
  },
  activated() {
    // Keep the list fresh when navigating back to this view via keep-alive
    this.loadPreview()
  },
  methods: {
    // ── Import ──────────────────────────────────────────────────────────

    onFileSelected(evt) {
      this.importFile = evt.target.files[0] || null
      this.importPreview = null
      this.importResult = null
    },

    async runPreview() {
      if (!this.importFile) return
      this.isPreviewLoading = true
      this.importPreview = null
      this.importResult = null
      this.errorMsg = ''
      try {
        const form = new FormData()
        form.append('file', this.importFile)
        const authStore = useAuthStore()
        const res = await axios.post(
          `${import.meta.env.VITE_API_URL}/abstracts/import-preview`,
          form,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        )
        this.importPreview = res.data
      } catch (err) {
        this.errorMsg = err.response?.data?.detail || 'Failed to preview file.'
      } finally {
        this.isPreviewLoading = false
      }
    },

    async runImport() {
      if (!this.importFile || !this.importPreview) return
      if (!confirm(`Import ${this.importPreview.to_import} abstract(s) into "${this.importPreview.event_name}"?`)) return
      this.isImporting = true
      this.importResult = null
      this.errorMsg = ''
      try {
        const form = new FormData()
        form.append('file', this.importFile)
        const authStore = useAuthStore()
        const res = await axios.post(
          `${import.meta.env.VITE_API_URL}/abstracts/import`,
          form,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        )
        this.importResult = res.data
        this.importPreview = null
        this.$refs.fileInput.value = ''
        this.importFile = null
        // Refresh the reminder list
        await this.loadPreview()
      } catch (err) {
        this.errorMsg = err.response?.data?.detail || 'Import failed.'
      } finally {
        this.isImporting = false
      }
    },

    // ── Registration Reminders ──────────────────────────────────────────

    async loadPreview() {
      this.isLoading = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const params = {}
        if (this.eventId) params.event_id = this.eventId
        const response = await fetchDataWithParams('abstracts/registration-reminder-preview', params)
        this.presenters = Array.isArray(response) ? response : (response.data || [])
      } catch (error) {
        console.error('Error loading reminder preview:', error)
        this.errorMsg = 'Failed to load presenter list.'
      } finally {
        this.isLoading = false
      }
    },

    async sendReminders() {
      if (!confirm(`Send registration reminder emails to ${this.presenters.length} presenter(s)?`)) return
      this.isSending = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const response = await createItem('abstracts/send-registration-reminders', {
          event_id: this.eventId ? parseInt(this.eventId) : null,
        })
        const msg = response.message || `${response.reminders_sent} reminder(s) sent.`
        this.successMsg = msg
        await this.loadPreview()
      } catch (error) {
        console.error('Error sending reminders:', error)
        this.errorMsg = error.response?.data?.detail || 'Failed to send reminders.'
      } finally {
        this.isSending = false
      }
    },
  },
}
</script>
