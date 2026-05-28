<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'System Configurations'" />

    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">

      <router-link v-if="permissions.includes('VIEW_USER')"
        :to="{ name: 'Users' }"
        class="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:bg-gray-50 transition">
        <div class="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style="background-color: rgba(254,80,103,0.1);">
          <UsersIcon class="h-5 w-5" style="color: rgb(254,80,103);" />
        </div>
        <div>
          <p class="font-semibold text-gray-800 text-sm">Users</p>
          <p class="text-xs text-gray-400 mt-0.5">Manage system user accounts</p>
        </div>
      </router-link>

      <router-link v-if="permissions.includes('VIEW_ROLE')"
        :to="{ name: 'Roles' }"
        class="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:bg-gray-50 transition">
        <div class="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style="background-color: rgba(254,80,103,0.1);">
          <UserGroupIcon class="h-5 w-5" style="color: rgb(254,80,103);" />
        </div>
        <div>
          <p class="font-semibold text-gray-800 text-sm">Roles</p>
          <p class="text-xs text-gray-400 mt-0.5">Configure roles and permissions</p>
        </div>
      </router-link>

      <router-link v-if="permissions.includes('VIEW_EVENT_TYPE')"
        :to="{ name: 'EventTypes' }"
        class="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:bg-gray-50 transition">
        <div class="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style="background-color: rgba(254,80,103,0.1);">
          <CalendarDaysIcon class="h-5 w-5" style="color: rgb(254,80,103);" />
        </div>
        <div>
          <p class="font-semibold text-gray-800 text-sm">Event Types</p>
          <p class="text-xs text-gray-400 mt-0.5">Define event categories</p>
        </div>
      </router-link>

      <router-link v-if="permissions.includes('VIEW_ORGANISER')"
        :to="{ name: 'Organisers' }"
        class="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:bg-gray-50 transition">
        <div class="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style="background-color: rgba(254,80,103,0.1);">
          <BriefcaseIcon class="h-5 w-5" style="color: rgb(254,80,103);" />
        </div>
        <div>
          <p class="font-semibold text-gray-800 text-sm">Organisers</p>
          <p class="text-xs text-gray-400 mt-0.5">Manage event partners</p>
        </div>
      </router-link>

      <router-link v-if="permissions.includes('ADMIN_DASHBOARD')"
        :to="{ name: 'EmailTemplates' }"
        class="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:bg-gray-50 transition">
        <div class="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style="background-color: rgba(254,80,103,0.1);">
          <EnvelopeIcon class="h-5 w-5" style="color: rgb(254,80,103);" />
        </div>
        <div>
          <p class="font-semibold text-gray-800 text-sm">Email Templates</p>
          <p class="text-xs text-gray-400 mt-0.5">Customise email messages</p>
        </div>
      </router-link>

      <router-link v-if="permissions.includes('ADMIN_DASHBOARD')"
        :to="{ name: 'Contacts' }"
        class="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:bg-gray-50 transition">
        <div class="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style="background-color: rgba(254,80,103,0.1);">
          <PhoneIcon class="h-5 w-5" style="color: rgb(254,80,103);" />
        </div>
        <div>
          <p class="font-semibold text-gray-800 text-sm">Contacts</p>
          <p class="text-xs text-gray-400 mt-0.5">Organisation contact info</p>
        </div>
      </router-link>

    </div>

    <!-- Badge Logos -->
    <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5">
      <p class="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-4">Badge Logos</p>
      <p class="text-sm text-gray-500 mb-4">Upload the left and right logos that appear on participant badges. Logos are saved in the browser and applied to all badge previews.</p>
      <div class="grid sm:grid-cols-2 gap-6">

        <!-- Left logo -->
        <div>
          <p class="text-sm font-medium text-gray-700 mb-2">Left Logo</p>
          <div class="flex items-center gap-3">
            <div class="h-16 w-16 flex-shrink-0 rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center overflow-hidden bg-gray-50">
              <img v-if="leftLogoUrl" :src="leftLogoUrl" class="h-full w-full object-contain" alt="Left Logo" />
              <svg v-else class="w-6 h-6 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="space-y-2">
              <label class="cursor-pointer inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-white transition hover:opacity-90"
                style="background-color: rgb(254,80,103);">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Upload
                <input type="file" accept="image/*" class="sr-only" @change="uploadLeft" />
              </label>
              <button v-if="leftLogoUrl" @click="clearLeft"
                class="block text-xs text-gray-400 hover:text-red-500 transition">Remove</button>
            </div>
          </div>
        </div>

        <!-- Right logo -->
        <div>
          <p class="text-sm font-medium text-gray-700 mb-2">Right Logo</p>
          <div class="flex items-center gap-3">
            <div class="h-16 w-16 flex-shrink-0 rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center overflow-hidden bg-gray-50">
              <img v-if="rightLogoUrl" :src="rightLogoUrl" class="h-full w-full object-contain" alt="Right Logo" />
              <svg v-else class="w-6 h-6 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="space-y-2">
              <label class="cursor-pointer inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-white transition hover:opacity-90"
                style="background-color: rgb(254,80,103);">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Upload
                <input type="file" accept="image/*" class="sr-only" @change="uploadRight" />
              </label>
              <button v-if="rightLogoUrl" @click="clearRight"
                class="block text-xs text-gray-400 hover:text-red-500 transition">Remove</button>
            </div>
          </div>
        </div>

      </div>
      <p v-if="logoSaved" class="mt-4 text-xs text-green-600 font-medium">✓ Logo saved — will appear on all badge previews.</p>
    </div>

  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import { useAuthStore } from '@/store/authStore'
import { UsersIcon, UserGroupIcon, CalendarDaysIcon, BriefcaseIcon } from '@heroicons/vue/24/solid'
import { EnvelopeIcon, PhoneIcon } from '@heroicons/vue/24/outline'

const LOGO_LEFT_KEY = 'badge_logo_left'
const LOGO_RIGHT_KEY = 'badge_logo_right'

export default {
  name: 'ConfigurationsView',
  components: {
    HeaderView,
    UsersIcon, UserGroupIcon, CalendarDaysIcon, BriefcaseIcon, EnvelopeIcon, PhoneIcon,
  },
  data() {
    return {
      leftLogoUrl: null,
      rightLogoUrl: null,
      logoSaved: false,
    }
  },
  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissions = raw.map(p => typeof p === 'string' ? p : p.permission_code)
    return { permissions }
  },
  mounted() {
    this.leftLogoUrl = localStorage.getItem(LOGO_LEFT_KEY) || null
    this.rightLogoUrl = localStorage.getItem(LOGO_RIGHT_KEY) || null
  },
  methods: {
    uploadLeft(e) {
      const file = e.target.files[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = ev => {
        this.leftLogoUrl = ev.target.result
        localStorage.setItem(LOGO_LEFT_KEY, ev.target.result)
        this.flashSaved()
      }
      reader.readAsDataURL(file)
    },
    uploadRight(e) {
      const file = e.target.files[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = ev => {
        this.rightLogoUrl = ev.target.result
        localStorage.setItem(LOGO_RIGHT_KEY, ev.target.result)
        this.flashSaved()
      }
      reader.readAsDataURL(file)
    },
    clearLeft() {
      this.leftLogoUrl = null
      localStorage.removeItem(LOGO_LEFT_KEY)
    },
    clearRight() {
      this.rightLogoUrl = null
      localStorage.removeItem(LOGO_RIGHT_KEY)
    },
    flashSaved() {
      this.logoSaved = true
      setTimeout(() => { this.logoSaved = false }, 3000)
    },
  },
}
</script>
