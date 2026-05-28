<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <SpinnerComponent v-if="isLoading" />
    <div v-else class="rounded-2xl bg-catskill-white-100 shadow-sm p-4">
      <form class="flex flex-col w-5/12 w-full space-y-4" @submit.prevent="editUser" method="POST">
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Firtsname
          </span>
          <input type="input" name="firstname" v-model="userData.firstname"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            placeholder="Firstname" />
        </label>
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Lastname
          </span>
          <input type="input" name="lastname" v-model="userData.lastname"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            placeholder="Lastname" />
        </label>
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Email address
          </span>
          <input type="email" name="email" v-model="userData.email"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            placeholder="you@example.com" />
        </label>
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Phone
          </span>
          <input type="text" name="phone" v-model="userData.phone"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            title="Please enter a valid 10-digit phone number" placeholder="Phone number" required />
        </label>
        <div class="flex flex-row space-x-4">
          <button type="submit" class="mt-2 px-4 py-2 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
            Update user
          </button>
          <router-link :to="{ name: 'Users' }"
            class="mt-2 px-4 py-2 boder border-2 border-abbey-400 hover:border-abbey-200 rounded-2xl">Cancel</router-link>
        </div>
      </form>
    </div>
  </div>
</template>
<script>
import { updateItem, fetchItem } from "@/services/apiService";
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from "@/components/Spinner.vue";
import router from "@/router";

export default {
  name: "EditUserView",
  components: {
    HeaderView, SpinnerComponent
  },
  data() {
    return {
      headerTitle: "Edit users",
      id: this.$route.params.id,
      userData: {
        firstname: "",
        lastname: "",
        email: "",
        phone: "",
      },
      isLoading: false,
    };
  },
  mounted() {
    this.getUser();
  },
  methods: {
    async editUser() {
      this.isLoading = true;
      try {
        const response = await updateItem("users", this.id, this.userData);
        this.users = response.data;
        this.isLoading = false;
        router.push("/users");
      } catch (error) {
        console.error("Error fetching users:", error);
        this.isLoading = false;
      }
    },
    async getUser() {
      try {
        const response = await fetchItem("users", this.id);
        console.log(response)
        this.userData.firstname = response.user.firstname;
        this.userData.lastname = response.user.lastname;
        this.userData.email = response.user.email;
        this.userData.phone = response.user.phone;
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching role:", error);
        this.isLoading = false;
      }
    },
  },
};
</script>
