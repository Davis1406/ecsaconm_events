<template>
  <div class="flex flex-col space-y-6 flex-1">
    <div class="text-2xl font-bold text-gray-800">My Profile</div>

    <!-- Spinner -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <div v-else class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <!-- Header strip with profile picture -->
      <div class="px-6 py-5 border-b border-gray-100 flex items-center gap-5">
        <!-- Avatar + upload -->
        <div class="relative flex-shrink-0">
          <div class="h-20 w-20 rounded-full overflow-hidden ring-4 ring-white shadow-md cursor-pointer"
            @click="$refs.photoInput.click()" title="Click to change photo">
            <img v-if="profilePictureUrl" :src="profilePictureUrl"
              class="h-full w-full object-cover" alt="Profile" />
            <div v-else class="h-full w-full flex items-center justify-center text-white text-2xl font-bold"
              style="background-color: rgb(254,80,103);">
              {{ initials }}
            </div>
          </div>
          <!-- Camera overlay -->
          <button @click="$refs.photoInput.click()"
            class="absolute bottom-0 right-0 h-7 w-7 rounded-full flex items-center justify-center text-white shadow-md"
            style="background-color: rgb(254,80,103);" title="Change photo">
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
          <input ref="photoInput" type="file" accept="image/*" class="hidden" @change="uploadPhoto" />
        </div>
        <div>
          <p class="font-bold text-gray-800 text-lg">{{ form.firstname }} {{ form.lastname }}</p>
          <p class="text-sm text-gray-400">{{ form.email }}</p>
          <p v-if="photoUploading" class="text-xs mt-1" style="color: rgb(254,80,103);">Uploading photo…</p>
          <p v-if="photoError" class="text-xs mt-1 text-red-500">{{ photoError }}</p>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="successMsg" class="mx-6 mt-5 p-3.5 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm">
        {{ successMsg }}
      </div>
      <div v-if="errorMsg" class="mx-6 mt-5 p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
        {{ errorMsg }}
      </div>

      <form @submit.prevent="saveProfile" class="px-6 py-6 space-y-6">

        <!-- Personal info -->
        <div>
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4">Personal Information</h3>
          <div class="grid sm:grid-cols-2 gap-4">
            <div>
              <label class="field-label">Title</label>
              <select v-model="form.title" class="field-input">
                <option value="">Select title</option>
                <option value="Mr">Mr</option>
                <option value="Mrs">Mrs</option>
                <option value="Ms">Ms</option>
                <option value="Dr">Dr</option>
                <option value="Prof">Prof</option>
              </select>
            </div>
            <div>
              <label class="field-label">Gender</label>
              <select v-model="form.gender" class="field-input">
                <option value="">Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>
            <div>
              <label class="field-label">First Name <span class="text-red-500">*</span></label>
              <input v-model="form.firstname" type="text" required class="field-input" />
            </div>
            <div>
              <label class="field-label">Middle Name</label>
              <input v-model="form.middle_name" type="text" class="field-input" placeholder="Optional" />
            </div>
            <div class="sm:col-span-2">
              <label class="field-label">Last Name <span class="text-red-500">*</span></label>
              <input v-model="form.lastname" type="text" required class="field-input" />
            </div>
            <div>
              <label class="field-label">Email Address</label>
              <input v-model="form.email" type="email" readonly
                class="field-input opacity-60 cursor-not-allowed bg-gray-50" />
              <p class="text-xs text-gray-400 mt-1">Email cannot be changed here.</p>
            </div>
            <div>
              <label class="field-label">Phone Number</label>
              <input v-model="form.phone" type="tel" class="field-input" />
            </div>
          </div>
        </div>

        <!-- Certificate name -->
        <div>
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4">Certificate Information</h3>
          <div>
            <label class="field-label">Full Name as it should Appear on Attendance Certificate</label>
            <input v-model="form.certificate_name" type="text" class="field-input"
              placeholder="e.g. Dr. Jane A. Doe" />
            <p class="text-xs text-gray-400 mt-1">This name will be printed on your conference certificate.</p>
          </div>
        </div>

        <!-- Professional info -->
        <div>
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4">Professional Information</h3>
          <div class="grid sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <label class="field-label">Designation</label>
              <select v-model="form.designation" class="field-input">
                <option value="">Select designation</option>
                <option value="Chief Nursing Officer">Chief Nursing Officer</option>
                <option value="Clinical Supervisor">Clinical Supervisor</option>
                <option value="Communications Manager">Communications Manager</option>
                <option value="Director Nursing Services">Director Nursing Services</option>
                <option value="Educator">Educator</option>
                <option value="Midwifery Specialist">Midwifery Specialist</option>
                <option value="Nursing Midwifery Specialist">Nursing Midwifery Specialist</option>
                <option value="Nursing Specialist">Nursing Specialist</option>
                <option value="Nursing Superintendent">Nursing Superintendent</option>
                <option value="Principal Nursing Officer">Principal Nursing Officer</option>
                <option value="Project Manager">Project Manager</option>
                <option value="Public Health Specialist">Public Health Specialist</option>
                <option value="Registered Nurse">Registered Nurse</option>
                <option value="Researcher">Researcher</option>
                <option value="Student">Student</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div class="sm:col-span-2">
              <label class="field-label">Organisation / Institution</label>
              <input v-model="form.organisation" type="text" class="field-input" placeholder="e.g. Ministry of Health" />
            </div>
            <div class="sm:col-span-2">
              <label class="field-label">Address</label>
              <textarea v-model="form.address" rows="2" class="field-input" placeholder="Street / PO Box, City, Region"></textarea>
            </div>
            <div>
              <label class="field-label">Country</label>
              <select v-model="form.country_id" class="field-input">
                <option value="">Select country</option>
                <option v-for="c in countries" :key="c.id" :value="c.id">{{ c.country }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end pt-2 border-t border-gray-100">
          <button type="submit" :disabled="isSaving"
            class="px-7 py-2.5 rounded-xl text-white font-semibold text-sm transition hover:opacity-90 disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { fetchItem, updateItem, createItem } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'MyProfile',
  data() {
    return {
      isLoading: true,
      isSaving: false,
      successMsg: '',
      errorMsg: '',
      countries: [],
      profilePictureUrl: null,
      photoUploading: false,
      photoError: '',
      form: {
        title: '',
        gender: '',
        firstname: '',
        middle_name: '',
        lastname: '',
        email: '',
        phone: '',
        profession: '',
        position: '',
        organisation: '',
        country_id: '',
        designation: '',
        certificate_name: '',
        address: '',
      },
    }
  },
  setup() {
    const authStore = useAuthStore()
    const user = authStore.loginUser
    return { user, authStore }
  },
  computed: {
    initials() {
      const f = this.form.firstname?.charAt(0)?.toUpperCase() || ''
      const l = this.form.lastname?.charAt(0)?.toUpperCase() || ''
      return f + l || '?'
    },
  },
  mounted() {
    this.loadCountries()
    this.loadProfile()
  },
  methods: {
    async loadCountries() {
      try {
        const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
        const res = await api.get('/countries?skip=0&limit=300')
        this.countries = res.data?.data || res.data || []
      } catch (e) {
        console.error('Error loading countries:', e)
      }
    },
    async loadProfile() {
      try {
        const userId = this.user?.id
        const userRes = await fetchItem('users', userId)
        // GET /users/{id} returns { user, profile, ... }
        const userData = userRes.user || userRes || {}
        const profileData = userRes.profile || {}

        this.form.firstname = userData.firstname || this.user?.firstname || ''
        this.form.lastname = userData.lastname || this.user?.lastname || ''
        this.form.email = userData.email || this.user?.email || ''
        this.form.phone = userData.phone || this.user?.phone || ''

        this.form.title = profileData.title || ''
        this.form.middle_name = profileData.middle_name || ''
        this.form.gender = profileData.gender || ''
        this.form.profession = profileData.profession || ''
        this.form.position = profileData.position || ''
        this.form.organisation = profileData.organisation || ''
        this.form.country_id = profileData.country_id || ''
        this.form.designation = profileData.designation || ''
        this.form.certificate_name = profileData.certificate_name || ''
        this.form.address = profileData.address || ''

        // Profile picture
        const pic = userRes.profile_picture?.profile_picture
        if (pic) {
          this.profilePictureUrl = `${API_URL}/${pic}`
        }
      } catch (error) {
        console.error('Error loading profile:', error)
        this.form.firstname = this.user?.firstname || ''
        this.form.lastname = this.user?.lastname || ''
        this.form.email = this.user?.email || ''
        this.form.phone = this.user?.phone || ''
      } finally {
        this.isLoading = false
      }
    },
    async uploadPhoto(event) {
      const file = event.target.files[0]
      if (!file) return
      if (!file.type.startsWith('image/')) {
        this.photoError = 'Please select an image file.'
        return
      }
      this.photoUploading = true
      this.photoError = ''
      try {
        const formData = new FormData()
        formData.append('file', file)
        const token = this.authStore.accessToken
        const res = await axios.post(`${API_URL}/users/upload_user_photo/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`,
          },
        })
        // Show preview
        this.profilePictureUrl = `${API_URL}/${res.data.file_path}`
      } catch (e) {
        this.photoError = e.response?.data?.detail || 'Failed to upload photo.'
      } finally {
        this.photoUploading = false
        // Reset input so same file can be re-selected
        this.$refs.photoInput.value = ''
      }
    },
    async saveProfile() {
      this.isSaving = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const userId = this.user?.id

        // Step 1: Update base user fields (UserSchema requires email)
        await updateItem('users', userId, {
          firstname: this.form.firstname,
          lastname: this.form.lastname,
          phone: this.form.phone,
          email: this.form.email,
        })

        // Step 2: Update profile fields (ProfileSchema)
        await createItem(`users/profile/${userId}`, {
          title: this.form.title || '',
          middle_name: this.form.middle_name || '',
          gender: this.form.gender || '',
          country_id: this.form.country_id || null,
          organisation: this.form.organisation || '',
          position: this.form.position || '',
          profession: this.form.profession || '',
          designation: this.form.designation || '',
          certificate_name: this.form.certificate_name || '',
          address: this.form.address || '',
        })

        this.successMsg = 'Profile updated successfully!'
        // Update auth store name fields
        this.authStore.setUser({
          ...this.user,
          firstname: this.form.firstname,
          lastname: this.form.lastname,
          phone: this.form.phone,
        })
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } catch (error) {
        console.error('Error saving profile:', error)
        this.errorMsg = error.response?.data?.detail
          || (Array.isArray(error.response?.data) ? error.response.data.map(e => e.msg).join(', ') : null)
          || 'Failed to update profile. Please try again.'
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
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.375rem;
}
.field-input {
  display: block;
  width: 100%;
  border: 1px solid #d1d5db;
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
