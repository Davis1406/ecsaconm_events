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
            <button v-if="permissions.includes('VIEW_REGISTRATIONS') || permissions.includes('ADMIN_DASHBOARD')"
              @click="openEditParticipant"
              class="px-3 py-1.5 rounded-lg text-sm font-medium border transition hover:bg-pink-50"
              style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
              Edit Participant
            </button>
            <button v-if="canImpersonate"
              @click="impersonateUser"
              :disabled="impersonating"
              class="px-3 py-1.5 rounded-lg text-sm font-medium border transition hover:bg-pink-50 disabled:opacity-50"
              style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
              {{ impersonating ? 'Switching…' : 'Log in as User' }}
            </button>
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

    <!-- Edit participant modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h3 class="font-bold text-gray-800">Edit Participant</h3>
          <button @click="showEditModal = false" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-4">
          <label v-if="userEvents.length > 1" class="block">
            <span class="block text-xs font-semibold text-gray-500 mb-1">Event registration</span>
            <select v-model.number="editForm.registration_id" @change="onRegistrationChange"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400">
              <option v-for="e in userEvents" :key="e.registration_id" :value="e.registration_id">{{ e.event }}</option>
            </select>
          </label>

          <div class="grid sm:grid-cols-2 gap-4">
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Title</span>
              <input v-model="editForm.title" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">First name</span>
              <input v-model="editForm.firstname" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Last name</span>
              <input v-model="editForm.lastname" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Phone</span>
              <input v-model="editForm.phone" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Designation</span>
              <input v-model="editForm.designation" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Organisation</span>
              <input v-model="editForm.organisation" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Country</span>
              <select v-model.number="editForm.country_id"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400">
                <option :value="null">—</option>
                <option v-for="c in editCountries" :key="c.id" :value="c.id">{{ c.country }}</option>
              </select>
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Participation role</span>
              <select v-model="editForm.participation_role"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-400">
                <option v-for="r in roleOptions" :key="r.value" :value="r.value">{{ r.label }}</option>
              </select>
            </label>
            <label class="block sm:col-span-2">
              <span class="block text-xs font-semibold text-gray-500 mb-1">Badge photo</span>
              <div class="flex items-center gap-3">
                <div class="h-14 w-14 rounded-full overflow-hidden border border-gray-200 flex-shrink-0 bg-gray-50">
                  <img v-if="editPhotoPreview" :src="editPhotoPreview" class="h-full w-full object-cover" alt="Badge photo" />
                  <div v-else class="h-full w-full flex items-center justify-center text-white text-lg font-semibold"
                    style="background-color: rgb(254,80,103);">
                    {{ initials }}
                  </div>
                </div>
                <div class="flex-1">
                  <input ref="editPhotoInput" type="file" accept="image/*" :disabled="editPhotoUploading"
                    class="block w-full text-sm text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:text-white file:bg-pink-500 file:cursor-pointer disabled:opacity-50"
                    @change="onEditPhotoChange" />
                  <p v-if="editPhotoError" class="text-xs text-red-600 mt-1">{{ editPhotoError }}</p>
                  <p v-if="editPhotoUploading" class="text-xs text-gray-500 mt-1">Uploading…</p>
                </div>
              </div>
            </label>
          </div>

          <p v-if="editError" class="text-sm px-3 py-2 rounded-lg bg-red-50 text-red-600">{{ editError }}</p>
        </div>

        <div class="px-5 py-4 border-t border-gray-100 flex justify-end gap-2">
          <button @click="showEditModal = false"
            class="px-4 py-2 rounded-lg text-sm font-medium border border-gray-300 text-gray-600 hover:bg-gray-50 transition">
            Cancel
          </button>
          <button @click="saveEditParticipant" :disabled="editSaving"
            class="px-4 py-2 rounded-lg text-sm font-medium text-white transition hover:opacity-90 disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ editSaving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import axios from 'axios'
import { fetchItem, createItem, fetchData, deleteItemWithBody, setAuthToken, updateItem } from '@/services/apiService'
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
      impersonating: false,
      // Edit participant
      userEvents: [],
      showEditModal: false,
      editSaving: false,
      editError: '',
      editPhotoPreview: null,
      editPhotoUploading: false,
      editPhotoError: '',
      editCountries: [],
      editForm: {
        registration_id: null,
        title: '',
        firstname: '',
        lastname: '',
        phone: '',
        designation: '',
        organisation: '',
        country_id: null,
        participation_role: '',
      },
      roleOptions: [
        { value: 'delegate', label: 'Delegate' },
        { value: 'secretariat', label: 'Secretariat' },
        { value: 'media', label: 'Media' },
        { value: 'exhibitor', label: 'Exhibitor' },
        { value: 'usher', label: 'Usher' },
      ],
    }
  },
  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissions = raw.map(p => typeof p === 'string' ? p : p.permission_code)
    return { permissions, authStore }
  },
  computed: {
    canImpersonate() {
      return this.permissions.includes('ADMIN_DASHBOARD')
        && !this.authStore.isImpersonating
        && parseInt(this.id) !== this.authStore.loginUser?.id
    },
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
        this.userEvents = response.events || []
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
    async impersonateUser() {
      this.impersonating = true
      try {
        const response = await createItem(`auth/impersonate/${this.id}`, {})
        this.authStore.startImpersonation(response)
        setAuthToken()
        const targetIsAdmin = (response.permissions || []).some(
          p => (typeof p === 'string' ? p : p.permission_code) === 'ADMIN_DASHBOARD'
        )
        this.$router.push({ name: targetIsAdmin ? 'Dashboard' : 'MyDashboard' })
      } catch (error) {
        this.showMessage('Failed to impersonate user.', 'error')
      } finally {
        this.impersonating = false
      }
    },
    async resetPassword() {
      try {
        await createItem(`users/${this.id}/reset-password`, {})
        this.showMessage('Password reset and sent to email.', 'success')
      } catch (error) {
        this.showMessage('Failed to reset password.', 'error')
      }
    },
    async openEditParticipant() {
      if (!this.userEvents.length) {
        this.showMessage('This user has no event registration to edit.', 'error')
        return
      }
      const first = this.userEvents[0]
      this.editForm = {
        registration_id: first.registration_id,
        title: this.profile.title || '',
        firstname: this.user.firstname || '',
        lastname: this.user.lastname || '',
        phone: this.user.phone || '',
        designation: this.profile.designation || '',
        organisation: this.profile.organisation || '',
        country_id: this.profile.country_id || null,
        participation_role: this.normalizeParticipationRole(first.participation_role),
      }
      this.editError = ''
      this.editPhotoError = ''
      this.editPhotoPreview = this.profilePictureUrl
      this.showEditModal = true
      await this.loadEditCountries()
    },
    onRegistrationChange() {
      const ev = this.userEvents.find(e => e.registration_id === this.editForm.registration_id)
      if (ev) this.editForm.participation_role = this.normalizeParticipationRole(ev.participation_role)
    },
    normalizeParticipationRole(role) {
      // The edit popup only offers the main roles; the fee-based delegate
      // categories (Member, Region, Outside-Region, Student) all read as
      // "Delegate", so normalise them to delegate.
      const legacyDelegate = ['member_state', 'participant', 'other_africa', 'student']
      if (!role) return 'delegate'
      const key = String(role).toLowerCase().replace(/\s+/g, '_')
      return legacyDelegate.includes(key) ? 'delegate' : key
    },
    async loadEditCountries() {
      if (this.editCountries.length) return
      try {
        const res = await fetchData('countries', 0, 500, '')
        this.editCountries = res.data || []
      } catch (error) {
        console.error('Error fetching countries:', error)
      }
    },
    async onEditPhotoChange(event) {
      const file = event.target.files[0]
      if (!file) return
      if (!file.type.startsWith('image/')) {
        this.editPhotoError = 'Please select an image file.'
        return
      }
      this.editPhotoError = ''
      this.editPhotoUploading = true
      try {
        const formData = new FormData()
        formData.append('file', file)
        const token = this.authStore.accessToken
        const res = await axios.post(`${API_URL}/users/${this.id}/photo`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`,
          },
        })
        this.editPhotoPreview = `${API_URL}/${res.data.file_path}`
        this.profilePictureUrl = this.editPhotoPreview
        this.showMessage('Photo uploaded.', 'success')
      } catch (e) {
        this.editPhotoError = e.response?.data?.detail || 'Failed to upload photo.'
      } finally {
        this.editPhotoUploading = false
        // Reset input so the same file can be re-selected
        this.$refs.editPhotoInput && (this.$refs.editPhotoInput.value = '')
      }
    },
    async saveEditParticipant() {
      if (!this.editForm.registration_id) return
      this.editSaving = true
      this.editError = ''
      try {
        await updateItem('registrations', this.editForm.registration_id, {
          title: this.editForm.title,
          firstname: this.editForm.firstname,
          lastname: this.editForm.lastname,
          phone: this.editForm.phone,
          designation: this.editForm.designation,
          organisation: this.editForm.organisation,
          country_id: this.editForm.country_id,
          participation_role: this.editForm.participation_role,
        })
        this.showEditModal = false
        await this.getUser()
        this.showMessage('Participant updated.', 'success')
      } catch (error) {
        this.editError = error.response?.data?.detail || 'Failed to update participant. Please try again.'
      } finally {
        this.editSaving = false
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
