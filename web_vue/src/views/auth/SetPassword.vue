<template>
  <div class="min-h-screen flex items-center justify-center px-4"
    style="background: linear-gradient(135deg, rgba(254,80,103,0.06) 0%, #f9fafb 100%);">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>
        <div class="p-8">
          <div class="flex justify-center mb-6">
            <img src="@/assets/images/logo.png" alt="ECSACONM" class="h-14 object-contain" />
          </div>

          <!-- Success -->
          <div v-if="success" class="text-center">
            <div class="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
            <h2 class="text-xl font-bold text-gray-800 mb-2">Password Set Successfully!</h2>
            <p class="text-gray-500 text-sm mb-6">You can now log in to the portal with your new password.</p>
            <router-link :to="{ name: 'Login' }"
              class="inline-block px-8 py-3 rounded-full text-white font-semibold transition hover:opacity-90"
              style="background-color: rgb(254,80,103);">
              Log In Now →
            </router-link>
          </div>

          <!-- Form -->
          <div v-else>
            <h2 class="text-2xl font-bold text-gray-800 mb-1 text-center">Set Your Password</h2>
            <p class="text-gray-500 text-sm text-center mb-6">Choose a strong password to secure your account.</p>

            <div v-if="error" class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              {{ error }}
            </div>

            <form @submit.prevent="submit" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                <input v-model="password" type="password" required placeholder="Minimum 8 characters"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none transition"
                  style="outline-color: rgb(254,80,103);" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                <input v-model="confirm" type="password" required placeholder="Re-enter your password"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none transition"
                  style="outline-color: rgb(254,80,103);" />
              </div>
              <button type="submit" :disabled="loading"
                class="w-full py-3 rounded-xl text-white font-semibold transition hover:opacity-90 disabled:opacity-60"
                style="background-color: rgb(254,80,103);">
                {{ loading ? 'Setting password…' : 'Set Password' }}
              </button>
            </form>
          </div>
        </div>
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'SetPasswordView',
  data() {
    return {
      token: this.$route.params.token,
      password: '',
      confirm: '',
      loading: false,
      error: '',
      success: false,
    }
  },
  methods: {
    async submit() {
      this.error = ''
      if (this.password.length < 8) {
        this.error = 'Password must be at least 8 characters.'; return
      }
      if (this.password !== this.confirm) {
        this.error = 'Passwords do not match.'; return
      }
      this.loading = true
      try {
        const api = axios.create({ baseURL: API_URL })
        await api.post('/auth/reset_password', {
          rest_token: this.token,
          password: this.password,
        })
        this.success = true
      } catch (e) {
        this.error = e.response?.data?.detail || 'Invalid or expired link. Please request a new one.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
