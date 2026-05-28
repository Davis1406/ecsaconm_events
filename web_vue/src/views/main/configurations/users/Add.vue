<template>
  <div class="flex flex-col space-y-6 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>
    <div v-else class="flex flex-col lg:flex-row gap-6">

      <!-- Left: user form -->
      <div class="flex-1 bg-white rounded-2xl shadow-sm p-6">
        <h2 class="text-base font-bold text-gray-700 mb-5">User Information</h2>

        <div v-if="errorMsg" class="mb-4 p-3 rounded-xl text-white text-sm" style="background-color: rgb(239,68,68);">
          {{ errorMsg }}
        </div>

        <form class="flex flex-col space-y-4" @submit.prevent="addUser">
          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">First Name <span class="text-red-500">*</span></label>
              <input type="text" v-model="userData.firstname"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
                placeholder="First name" required />
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Name <span class="text-red-500">*</span></label>
              <input type="text" v-model="userData.lastname"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
                placeholder="Last name" required />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email Address <span class="text-red-500">*</span></label>
            <input type="email" v-model="userData.email"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="you@example.com" required />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Phone <span class="text-red-500">*</span></label>
            <input type="text" v-model="userData.phone"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="+265999000001" required />
          </div>

          <div class="flex gap-3 pt-2">
            <button type="submit"
              class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90"
              style="background-color: rgb(254,80,103);">
              Create User
            </button>
            <router-link :to="{ name: 'Users' }"
              class="px-6 py-2.5 border border-gray-200 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 transition">
              Cancel
            </router-link>
          </div>
        </form>
      </div>

      <!-- Right: roles panel -->
      <div class="lg:w-72 bg-white rounded-2xl shadow-sm p-6">
        <h2 class="text-base font-bold text-gray-700 mb-2">Assign Roles</h2>
        <p class="text-xs text-gray-400 mb-4">Select roles to assign when the user is created.</p>
        <div v-if="roles.length === 0" class="text-sm text-gray-400 italic">No roles available.</div>
        <div v-for="role in roles" :key="role.id" class="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
          <input type="checkbox" :id="'role-' + role.id" :value="role.id" v-model="selectedRoles"
            class="h-4 w-4 rounded border-gray-300 cursor-pointer"
            :style="selectedRoles.includes(role.id) ? 'accent-color: rgb(254,80,103);' : ''" />
          <label :for="'role-' + role.id" class="text-sm text-gray-700 cursor-pointer flex-1">
            {{ role.role }}
          </label>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { createItem, fetchData } from "@/services/apiService";
import HeaderView from '@/includes/Header.vue';
import router from "@/router";

export default {
  name: "AddUserView",
  components: { HeaderView },
  data() {
    return {
      headerTitle: "Add User",
      userData: {
        firstname: "",
        lastname: "",
        email: "",
        phone: "",
      },
      roles: [],
      selectedRoles: [],
      isLoading: true,
      errorMsg: "",
    };
  },
  mounted() {
    this.loadRoles();
  },
  methods: {
    async loadRoles() {
      try {
        const res = await fetchData("roles", 0, 200, "");
        this.roles = res.data || [];
      } catch (e) {
        console.error("Error loading roles:", e);
      } finally {
        this.isLoading = false;
      }
    },
    async addUser() {
      this.isLoading = true;
      this.errorMsg = "";
      try {
        const response = await createItem("users/", this.userData);
        const newUserId = response.id;

        if (newUserId && this.selectedRoles.length > 0) {
          await Promise.allSettled(
            this.selectedRoles.map(role_id =>
              createItem("users/roles/", { user_id: newUserId, role_id })
            )
          );
        }

        this.isLoading = false;
        if (newUserId) {
          router.push({ name: "User", params: { id: newUserId } });
        } else {
          router.push({ name: "Users" });
        }
      } catch (error) {
        this.errorMsg = error.response?.data?.detail || "Failed to create user.";
        this.isLoading = false;
      }
    },
  },
};
</script>
