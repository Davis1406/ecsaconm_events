<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'User Profile'" />

    <SpinnerComponent v-if="isLoading" />

    <div v-else class="flex flex-col sm:flex-row gap-4">

      <!-- LEFT column -->
      <div class="sm:w-4/12 flex flex-col gap-4">

        <!-- Avatar card -->
        <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5 flex flex-col items-center text-center gap-3">
          <div class="h-20 w-20 rounded-full overflow-hidden flex-shrink-0 border border-gray-200">
            <img v-if="profilePictureUrl" :src="profilePictureUrl" class="h-full w-full object-cover" alt="Profile" />
            <div v-else class="h-full w-full flex items-center justify-center text-white text-2xl font-semibold"
              style="background-color: rgb(254,80,103);">
              {{ initials }}
            </div>
          </div>
          <div>
            <p class="font-semibold text-gray-800">
              {{ [profile.title, user.firstname, profile.middle_name, user.lastname].filter(Boolean).join(' ') }}
            </p>
            <p v-if="profile.designation" class="text-sm text-gray-500 mt-0.5">{{ profile.designation }}</p>
            <p v-if="profile.organisation" class="text-sm text-gray-400">{{ profile.organisation }}</p>
            <a :href="'mailto:' + user.email" class="text-sm hover:underline mt-1 block"
              style="color: rgb(254,80,103);">{{ user.email }}</a>
          </div>
          <div class="flex flex-wrap gap-2 justify-center w-full pt-1 border-t border-gray-100">
            <router-link v-if="permissions.includes('UPDATE_USER')"
              :to="{ name: 'EditUser', params: { id } }"
              class="px-3 py-1.5 rounded-lg text-sm font-medium text-white transition hover:opacity-90"
              style="background-color: rgb(254,80,103);">
              Edit
            </router-link>
            <button @click="resetPassword"
              class="px-3 py-1.5 rounded-lg text-sm font-medium border border-gray-300 text-gray-600 hover:bg-gray-50 transition">
              Reset Password
            </button>
          </div>
          <p v-if="message" class="w-full text-xs px-3 py-2 rounded-lg"
            :class="messageType === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'">
            {{ message }}
          </p>
        </div>

        <!-- Contact -->
        <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5">
          <p class="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-3">Contact</p>
          <div class="space-y-2 text-sm text-gray-700">
            <div v-if="user.phone"><span class="text-gray-400">Phone:</span> {{ user.phone }}</div>
            <div v-if="profile.country"><span class="text-gray-400">Country:</span> {{ profile.country }}</div>
            <div v-if="profile.address"><span class="text-gray-400">Address:</span> {{ profile.address }}</div>
          </div>
          <p v-if="!user.phone && !profile.country && !profile.address" class="text-sm text-gray-400 italic">No contact info.</p>
        </div>

      </div>

      <!-- RIGHT column -->
      <div class="sm:w-8/12 flex flex-col gap-4">

        <!-- Personal info -->
        <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5">
          <p class="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-3">Personal Information</p>
          <div class="grid sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
            <div v-if="profile.title">
              <span class="text-gray-400 block text-xs mb-0.5">Title</span>
              <span class="text-gray-800">{{ profile.title }}</span>
            </div>
            <div v-if="profile.gender">
              <span class="text-gray-400 block text-xs mb-0.5">Gender</span>
              <span class="text-gray-800">{{ profile.gender }}</span>
            </div>
            <div>
              <span class="text-gray-400 block text-xs mb-0.5">First Name</span>
              <span class="text-gray-800">{{ user.firstname || '—' }}</span>
            </div>
            <div v-if="profile.middle_name">
              <span class="text-gray-400 block text-xs mb-0.5">Middle Name</span>
              <span class="text-gray-800">{{ profile.middle_name }}</span>
            </div>
            <div>
              <span class="text-gray-400 block text-xs mb-0.5">Last Name</span>
              <span class="text-gray-800">{{ user.lastname || '—' }}</span>
            </div>
            <div>
              <span class="text-gray-400 block text-xs mb-0.5">Email</span>
              <span class="text-gray-800">{{ user.email || '—' }}</span>
            </div>
            <div v-if="user.phone">
              <span class="text-gray-400 block text-xs mb-0.5">Phone</span>
              <span class="text-gray-800">{{ user.phone }}</span>
            </div>
          </div>
        </div>

        <!-- Professional info -->
        <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5">
          <p class="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-3">Professional Information</p>
          <div class="grid sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
            <div v-if="profile.designation">
              <span class="text-gray-400 block text-xs mb-0.5">Designation</span>
              <span class="text-gray-800">{{ profile.designation }}</span>
            </div>
            <div v-if="profile.organisation">
              <span class="text-gray-400 block text-xs mb-0.5">Organisation</span>
              <span class="text-gray-800">{{ profile.organisation }}</span>
            </div>
            <div v-if="profile.profession">
              <span class="text-gray-400 block text-xs mb-0.5">Profession</span>
              <span class="text-gray-800">{{ profile.profession }}</span>
            </div>
            <div v-if="profile.position">
              <span class="text-gray-400 block text-xs mb-0.5">Position</span>
              <span class="text-gray-800">{{ profile.position }}</span>
            </div>
            <div v-if="profile.certificate_name" class="sm:col-span-2">
              <span class="text-gray-400 block text-xs mb-0.5">Certificate Name</span>
              <span class="text-gray-800">{{ profile.certificate_name }}</span>
            </div>
          </div>
          <p v-if="!profile.designation && !profile.organisation && !profile.profession && !profile.position"
            class="text-sm text-gray-400 italic">No professional information on file.</p>
        </div>

        <!-- Roles -->
        <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5">
          <p class="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-3">Roles</p>

          <div class="mb-4">
            <p class="text-xs text-gray-500 mb-2">Active roles <span class="text-gray-300">(click to remove)</span></p>
            <div class="flex flex-wrap gap-2">
              <button v-for="role in assignedRoles" :key="role.id"
                @click="removeRole(role.id)"
                class="px-3 py-1 rounded-lg text-sm text-white transition hover:opacity-80"
                style="background-color: rgb(254,80,103);">
                {{ role.role }} &times;
              </button>
              <span v-if="assignedRoles.length === 0" class="text-sm text-gray-400 italic">No roles assigned</span>
            </div>
          </div>

          <div>
            <p class="text-xs text-gray-500 mb-2">Available roles <span class="text-gray-300">(click to add)</span></p>
            <div class="flex flex-wrap gap-2">
              <button v-for="role in filteredRoles" :key="role.id"
                @click="assignRole(role.id)"
                class="px-3 py-1 rounded-lg text-sm border border-gray-300 text-gray-600 hover:bg-gray-50 transition">
                + {{ role.role }}
              </button>
              <span v-if="filteredRoles.length === 0" class="text-sm text-gray-400 italic">All roles assigned</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { fetchItem, createItem, fetchData, deleteItemWithBody, updateItem } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'UserView',
  components: { HeaderView, SpinnerComponent },
  data() {
    return {
      id: this.$route.params.id,
      isLoading: true,
      user: {},
      profile: {},
      profilePictureUrl: null,
      roles: [],
      assignedRoles: [],
      message: '',
      messageType: 'success',
    }
  },
  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissions = raw.map(p => typeof p === 'string' ? p : p.permission_code)
    return { permissions }
  },
  computed: {
    initials() {
      const f = (this.user.firstname || '').charAt(0).toUpperCase()
      const l = (this.user.lastname || '').charAt(0).toUpperCase()
      return f + l || '?'
    },
    filteredRoles() {
      return this.roles.filter(r => !this.assignedRoles.some(a => a.id === r.id))
    },
  },
  mounted() {
    this.getUser()
    this.getRoles()
  },
  methods: {
    async getUser() {
      try {
        const response = await fetchItem('users', this.id)
        this.user = response.user || {}
        this.profile = response.profile || {}
        this.assignedRoles = response.user?.roles || response.roles || []
        const pic = response.profile_picture?.profile_picture
        if (pic) this.profilePictureUrl = `${API_URL}/${pic}`
      } catch (error) {
        console.error('Error fetching user:', error)
      } finally {
        this.isLoading = false
      }
    },
    async getRoles() {
      try {
        const response = await fetchData('roles', 0, 100, '')
        this.roles = response.data || []
      } catch (error) {
        console.error('Error fetching roles:', error)
      }
    },
    async assignRole(role_id) {
      try {
        await createItem('users/roles/', { user_id: parseInt(this.id), role_id })
        await this.getUser()
        this.showMessage('Role assigned.', 'success')
      } catch (error) {
        this.showMessage('Failed to assign role.', 'error')
      }
    },
    async removeRole(role_id) {
      try {
        await deleteItemWithBody('users/roles/', { user_id: parseInt(this.id), role_id })
        this.assignedRoles = this.assignedRoles.filter(r => r.id !== role_id)
        this.showMessage('Role removed.', 'success')
      } catch (error) {
        this.showMessage('Failed to remove role.', 'error')
      }
    },
    async resetPassword() {
      try {
        await updateItem('users/password', this.id)
        this.showMessage('Password reset and sent to email.', 'success')
      } catch (error) {
        this.showMessage('Failed to reset password.', 'error')
      }
    },
    showMessage(msg, type = 'success') {
      this.message = msg
      this.messageType = type
      setTimeout(() => { this.message = '' }, 4000)
    },
  },
}
</script>
