<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>
    <div v-else class="rounded-2xl bg-white shadow-sm p-6">
      <form class="flex flex-col sm:w-7/12 w-full space-y-4" @submit.prevent="saveProfile">
        <div class="flex gap-4">
          <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
            <input type="text" v-model="userData.firstname"
              class="w-full px-3 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="First name" required />
          </div>
          <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
            <input type="text" v-model="userData.lastname"
              class="w-full px-3 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Last name" required />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
          <input type="email" v-model="userData.email"
            class="w-full px-3 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:border-pink-400"
            placeholder="email@example.com" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
          <input type="text" v-model="userData.phone"
            class="w-full px-3 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:border-pink-400"
            placeholder="Phone number" />
        </div>

        <div v-if="errorMsg" class="p-3 rounded-xl text-white text-sm" style="background-color: rgb(239,68,68);">
          {{ errorMsg }}
        </div>

        <div class="flex gap-3 pt-2">
          <button type="submit"
            class="px-5 py-2 rounded-xl text-sm font-semibold text-white transition hover:opacity-90"
            style="background-color: rgb(254,80,103);">
            Save Changes
          </button>
          <router-link :to="{ name: 'MyProfile', params: { id: id } }"
            class="px-5 py-2 border border-gray-300 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 transition">
            Cancel
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { fetchItem, updateItem } from "@/services/apiService";
import HeaderView from '@/includes/Header.vue';
import router from "@/router";

export default {
  name: "EditProfileView",
  components: { HeaderView },
  data() {
    return {
      headerTitle: "Edit Profile",
      id: this.$route.params.id,
      userData: {
        firstname: "",
        lastname: "",
        email: "",
        phone: "",
      },
      isLoading: true,
      errorMsg: "",
    };
  },
  mounted() {
    this.loadUser();
  },
  methods: {
    async loadUser() {
      try {
        const response = await fetchItem("users", this.id);
        const u = response.user;
        this.userData.firstname = u.firstname || "";
        this.userData.lastname = u.lastname || "";
        this.userData.email = u.email || "";
        this.userData.phone = u.phone || "";
        this.isLoading = false;
      } catch (error) {
        console.error("Error loading user:", error);
        this.isLoading = false;
      }
    },
    async saveProfile() {
      this.isLoading = true;
      this.errorMsg = "";
      try {
        await updateItem("users", this.id, this.userData);
        this.isLoading = false;
        router.push({ name: "MyProfile", params: { id: this.id } });
      } catch (error) {
        console.error("Error updating profile:", error);
        this.errorMsg = error.response?.data?.detail || "Failed to update profile.";
        this.isLoading = false;
      }
    },
  },
};
</script>
