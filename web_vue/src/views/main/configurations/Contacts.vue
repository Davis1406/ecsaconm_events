<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'Contacts & Support'" />

    <div class="bg-white border border-gray-100 rounded-xl shadow-sm overflow-hidden">

      <!-- Card header -->
      <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div>
          <p class="font-semibold text-gray-800">ECSACONM Secretariat</p>
          <p class="text-xs text-gray-400 mt-0.5">East Central and Southern Africa College of Nursing and Midwifery</p>
        </div>
        <button v-if="!editing" @click="startEdit"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-white transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          Edit
        </button>
        <div v-else class="flex gap-2">
          <button @click="cancelEdit"
            class="px-4 py-2 rounded-lg text-sm font-semibold border border-gray-200 text-gray-600 hover:bg-gray-50 transition">
            Cancel
          </button>
          <button @click="saveContacts" :disabled="isSaving"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ isSaving ? 'Saving…' : 'Save Changes' }}
          </button>
        </div>
      </div>

      <!-- Success / Error -->
      <div v-if="successMsg" class="mx-6 mt-4 p-3 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm">
        {{ successMsg }}
      </div>
      <div v-if="errorMsg" class="mx-6 mt-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
        {{ errorMsg }}
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-center py-12">
        <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
      </div>

      <!-- View mode -->
      <div v-else-if="!editing" class="px-6 py-5 space-y-0 text-sm">

        <div class="flex items-start gap-4 py-3 border-b border-gray-50">
          <span class="text-xs font-semibold uppercase tracking-widest text-gray-400 w-28 flex-shrink-0 pt-0.5">Address</span>
          <div class="text-gray-700">
            <p>{{ form.address_line1 || '—' }}</p>
            <p v-if="form.address_line2">{{ form.address_line2 }}</p>
          </div>
        </div>

        <div class="flex items-start gap-4 py-3 border-b border-gray-50">
          <span class="text-xs font-semibold uppercase tracking-widest text-gray-400 w-28 flex-shrink-0 pt-0.5">Tel</span>
          <div class="text-gray-700">
            <p>{{ form.phone1 || '—' }}</p>
            <p v-if="form.phone2">{{ form.phone2 }}</p>
          </div>
        </div>

        <div class="flex items-start gap-4 py-3 border-b border-gray-50">
          <span class="text-xs font-semibold uppercase tracking-widest text-gray-400 w-28 flex-shrink-0 pt-0.5">Fax</span>
          <p class="text-gray-700">{{ form.fax || '—' }}</p>
        </div>

        <div class="flex items-start gap-4 py-3 border-b border-gray-50">
          <span class="text-xs font-semibold uppercase tracking-widest text-gray-400 w-28 flex-shrink-0 pt-0.5">Email</span>
          <div class="space-y-1">
            <div>
              <a :href="'mailto:' + form.email_general" class="hover:underline" style="color: rgb(254,80,103);">{{ form.email_general }}</a>
              <p class="text-xs text-gray-400">General enquiries</p>
            </div>
            <div class="mt-1">
              <a :href="'mailto:' + form.email_conference" class="hover:underline" style="color: rgb(254,80,103);">{{ form.email_conference }}</a>
              <p class="text-xs text-gray-400">Conference enquiries</p>
            </div>
          </div>
        </div>

        <div class="flex items-start gap-4 py-3">
          <span class="text-xs font-semibold uppercase tracking-widest text-gray-400 w-28 flex-shrink-0 pt-0.5">Website</span>
          <a :href="form.website" target="_blank" class="hover:underline" style="color: rgb(254,80,103);">{{ form.website }}</a>
        </div>

      </div>

      <!-- Edit mode -->
      <form v-else @submit.prevent="saveContacts" class="px-6 py-5 space-y-4 text-sm">

        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="field-label">Address Line 1</label>
            <input v-model="form.address_line1" type="text" class="field-input" placeholder="e.g. Plot No. 157, Njiro Road" />
          </div>
          <div>
            <label class="field-label">Address Line 2</label>
            <input v-model="form.address_line2" type="text" class="field-input" placeholder="e.g. P.O. Box 1009, Arusha, Tanzania" />
          </div>
          <div>
            <label class="field-label">Phone 1</label>
            <input v-model="form.phone1" type="text" class="field-input" placeholder="+255-27-254 9362" />
          </div>
          <div>
            <label class="field-label">Phone 2</label>
            <input v-model="form.phone2" type="text" class="field-input" placeholder="+255-27-254 9365 / 9366" />
          </div>
          <div>
            <label class="field-label">Fax</label>
            <input v-model="form.fax" type="text" class="field-input" placeholder="+255-27-254 9392" />
          </div>
          <div>
            <label class="field-label">General Email</label>
            <input v-model="form.email_general" type="email" class="field-input" placeholder="info@ecsaconm.org" />
          </div>
          <div>
            <label class="field-label">Conference Email</label>
            <input v-model="form.email_conference" type="email" class="field-input" placeholder="conference@ecsaconm.org" />
          </div>
          <div>
            <label class="field-label">Website</label>
            <input v-model="form.website" type="url" class="field-input" placeholder="https://ecsaconm.org" />
          </div>
        </div>

      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import HeaderView from '@/includes/Header.vue'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'ContactsView',
  components: { HeaderView },
  data() {
    return {
      isLoading: true,
      editing: false,
      isSaving: false,
      successMsg: '',
      errorMsg: '',
      form: {
        address_line1: '',
        address_line2: '',
        phone1: '',
        phone2: '',
        fax: '',
        email_general: '',
        email_conference: '',
        website: '',
      },
      savedForm: {},
    }
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  mounted() {
    this.loadContacts()
  },
  methods: {
    async loadContacts() {
      try {
        const api = axios.create({ baseURL: API_URL })
        const res = await api.get('/system/contacts')
        this.form = { ...this.form, ...res.data }
        this.savedForm = { ...this.form }
      } catch (e) {
        console.error('Error loading contacts:', e)
      } finally {
        this.isLoading = false
      }
    },
    startEdit() {
      this.savedForm = { ...this.form }
      this.editing = true
      this.successMsg = ''
      this.errorMsg = ''
    },
    cancelEdit() {
      this.form = { ...this.savedForm }
      this.editing = false
    },
    async saveContacts() {
      this.isSaving = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        await api.put('/system/contacts', this.form)
        this.savedForm = { ...this.form }
        this.editing = false
        this.successMsg = 'Contact information updated successfully.'
        setTimeout(() => { this.successMsg = '' }, 4000)
      } catch (e) {
        this.errorMsg = e.response?.data?.detail || 'Failed to save contacts.'
      } finally {
        this.isSaving = false
      }
    },
  },
}
</script>

<style scoped>
.field-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.field-input {
  display: block;
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #1f2937;
  background: #fff;
  outline: none;
  transition: border-color 0.15s;
}
.field-input:focus {
  border-color: rgb(254,80,103);
  box-shadow: 0 0 0 3px rgba(254,80,103,0.1);
}
</style>
