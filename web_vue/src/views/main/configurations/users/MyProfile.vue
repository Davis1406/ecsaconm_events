<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>
    <div v-else class="flex flex-col space-y-4">
      <div class="flex flex-row space-x-4">
        <div class="flex flex-col space-y-4 sm:w-8/12 w-full border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div class="flex flex-col space-y-3">
            <p class="text-xl font-semibold text-gray-800">
              {{ user.firstname }} {{ user.lastname }}
            </p>
            <a :href="'mailto:' + user.email" class="hover:underline text-sm" style="color: rgb(254,80,103);">
              {{ user.email }}
            </a>
            <p class="text-sm text-gray-600">{{ user.phone }}</p>
            <div class="flex sm:flex-row flex-col gap-2 pt-2">
              <router-link :to="{ name: 'EditProfile', params: { id: id } }"
                class="inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold text-white transition hover:opacity-90"
                style="background-color: rgb(254,80,103);">
                Update Profile
              </router-link>
              <button @click="showPassword()"
                class="inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold bg-gray-700 text-white hover:bg-gray-800 transition">
                Reset Password
              </button>
            </div>
            <div v-if="message" class="p-3 rounded-xl text-white text-sm" style="background-color: rgb(34,197,94);">
              {{ message }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <password-modal :show="showPasswordModal" @confirmed="confirmPassword" @closed="cancelPassword" :user_id="id">
    </password-modal>
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import { fetchItem } from "@/services/apiService";
import { useAuthStore } from "@/store/authStore";
import PasswordModal from "@/components/PasswordModal.vue";

export default {
  name: "MyProfileView",
  components: {
    HeaderView, PasswordModal
  },
  data() {
    return {
      headerTitle: "My Profile",
      id: this.$route.params.id,
      isLoading: true,
      user: {},
      message: "",
      showPasswordModal: false,
    };
  },
  mounted() {
    this.getUser();
  },
  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissions = raw.map(p => typeof p === 'string' ? p : p.permission_code)
    return { permissions }
  },
  methods: {
    async getUser() {
      try {
        const response = await fetchItem("users", this.id);
        this.user = response.user;
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching user:", error);
        this.isLoading = false;
      }
    },
    showPassword() {
      this.showPasswordModal = true;
    },
    confirmPassword() {
      this.message = "Password updated successfully";
      this.showPasswordModal = false;
    },
    cancelPassword() {
      this.showPasswordModal = false;
    },
  },
};
</script>
