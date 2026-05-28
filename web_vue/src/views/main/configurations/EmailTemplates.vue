<template>
  <div class="flex flex-col space-y-6 flex-1">
    <HeaderView :headerTitle="'Email Templates'" />

    <!-- Template list -->
    <div v-if="!editing" class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div>
          <h2 class="text-base font-bold text-gray-800">Email Templates</h2>
          <p class="text-sm text-gray-400 mt-0.5">Manage the email messages sent to users</p>
        </div>
      </div>

      <div v-if="isLoading" class="flex justify-center py-12">
        <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
      </div>

      <div v-else class="divide-y divide-gray-50">
        <div v-for="t in templates" :key="t.template_key"
          class="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition">
          <div class="flex items-start gap-4">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style="background-color: rgba(254,80,103,0.1);">
              <svg class="h-5 w-5" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-800">{{ t.name }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ t.subject }}</p>
              <p v-if="t.variables" class="text-xs text-gray-300 mt-1">
                Variables: <span class="font-mono">{{ t.variables }}</span>
              </p>
            </div>
          </div>
          <button @click="openEditor(t.template_key)"
            class="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition"
            style="background-color: rgba(254,80,103,0.08); color: rgb(254,80,103);">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            Edit
          </button>
        </div>
      </div>
    </div>

    <!-- Template editor -->
    <div v-else class="flex flex-col gap-6">
      <!-- Top bar -->
      <div class="flex items-center gap-3">
        <button @click="cancelEdit"
          class="flex items-center gap-1.5 text-sm font-semibold text-gray-500 hover:text-gray-700 transition">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          Back to Templates
        </button>
        <span class="text-gray-300">/</span>
        <span class="text-sm font-semibold text-gray-700">{{ editForm.name }}</span>
      </div>

      <div v-if="saveSuccess" class="p-3.5 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm">
        ✓ Template saved successfully.
      </div>
      <div v-if="saveError" class="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
        {{ saveError }}
      </div>

      <div class="bg-white rounded-2xl shadow-sm p-6 space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
          <input v-model="editForm.name" type="text"
            class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email Subject</label>
          <input v-model="editForm.subject" type="text"
            class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400" />
        </div>
        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="block text-sm font-medium text-gray-700">HTML Body</label>
            <div class="flex gap-2">
              <button @click="previewMode = !previewMode"
                class="text-xs px-3 py-1 rounded-lg border transition"
                :class="previewMode ? 'border-pink-400 text-pink-600 bg-pink-50' : 'border-gray-200 text-gray-500 hover:border-gray-300'">
                {{ previewMode ? 'Edit HTML' : 'Preview' }}
              </button>
            </div>
          </div>
          <div v-if="!previewMode">
            <textarea v-model="editForm.body_html" rows="28"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm font-mono focus:outline-none focus:border-pink-400"
              style="resize: vertical;"></textarea>
            <p class="text-xs text-gray-400 mt-1">
              Available variables:
              <span v-if="currentTemplate" class="font-mono">{{ currentTemplate.variables }}</span>
              — wrap them in double curly braces, e.g. <code class="bg-gray-100 px-1 rounded">&#123;&#123;firstname&#125;&#125;</code>
            </p>
          </div>
          <div v-else class="border border-gray-200 rounded-xl overflow-hidden bg-white">
            <iframe :srcdoc="editForm.body_html" style="width:100%; height:500px; border:none;"></iframe>
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-2 border-t border-gray-100">
          <button @click="cancelEdit"
            class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 transition">
            Cancel
          </button>
          <button @click="saveTemplate" :disabled="isSaving"
            class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ isSaving ? 'Saving...' : 'Save Template' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { fetchData, fetchItem, updateItem } from '@/services/apiService'
import HeaderView from '@/includes/Header.vue'

export default {
  name: 'EmailTemplatesView',
  components: { HeaderView },
  data() {
    return {
      isLoading: true,
      templates: [],
      editing: false,
      previewMode: false,
      isSaving: false,
      saveSuccess: false,
      saveError: '',
      currentTemplateKey: null,
      editForm: {
        name: '',
        subject: '',
        body_html: '',
      },
    }
  },
  computed: {
    currentTemplate() {
      return this.templates.find(t => t.template_key === this.currentTemplateKey) || null
    },
  },
  mounted() {
    this.loadTemplates()
  },
  methods: {
    async loadTemplates() {
      this.isLoading = true
      try {
        const res = await fetchData('email_templates', 0, 100, '')
        this.templates = res.data || []
      } catch (e) {
        console.error('Error loading templates:', e)
      } finally {
        this.isLoading = false
      }
    },
    async openEditor(key) {
      this.saveSuccess = false
      this.saveError = ''
      this.previewMode = false
      try {
        const res = await fetchItem('email_templates', key)
        this.editForm = {
          name: res.name || '',
          subject: res.subject || '',
          body_html: res.body_html || '',
        }
        this.currentTemplateKey = key
        this.editing = true
      } catch (e) {
        console.error('Error loading template:', e)
      }
    },
    cancelEdit() {
      this.editing = false
      this.currentTemplateKey = null
      this.previewMode = false
    },
    async saveTemplate() {
      this.isSaving = true
      this.saveSuccess = false
      this.saveError = ''
      try {
        await updateItem('email_templates', this.currentTemplateKey, this.editForm)
        this.saveSuccess = true
        // Refresh the list
        const idx = this.templates.findIndex(t => t.template_key === this.currentTemplateKey)
        if (idx !== -1) {
          this.templates[idx].name = this.editForm.name
          this.templates[idx].subject = this.editForm.subject
        }
      } catch (e) {
        this.saveError = e.response?.data?.detail || 'Failed to save template.'
      } finally {
        this.isSaving = false
      }
    },
  },
}
</script>
