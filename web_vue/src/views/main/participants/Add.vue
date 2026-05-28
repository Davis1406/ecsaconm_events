<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <SpinnerComponent v-if="isLoading" />
    <div v-else class="rounded-2xl bg-catskill-white-100 shadow-sm p-4">
      <form class="flex flex-col sm:w-7/12 w-full space-y-4" @submit.prevent="addParticipant" method="POST">
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Title
          </span>
          <select name="country"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            v-model="participantData.title">
            <option value="" disabled selected>--Select title--</option>
            <option value="Mr." selected>Mr.</option>
            <option value="Mrs." selected>Mrs.</option>
            <option value="Ms." selected>Ms.</option>
            <option value="Miss." selected>Miss.</option>
            <option value="Dr." selected>Dr.</option>
            <option value="Prof." selected>Prof.</option>
          </select>
        </label>
        <label class="flex space-x-2">
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Firstname
            </span>
            <input type="input" name="firstname" v-model="participantData.firstname"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
              placeholder="Firstname" />
          </div>
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Lastname
            </span>
            <input type="input" name="lastname" v-model="participantData.lastname"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
              placeholder="Lastname" />
          </div>
        </label>
        <label class="flex space-x-2">
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              institution
            </span>
            <input name="Institution" v-model="participantData.institution"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
              placeholder="Institution" />
          </div>
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Country
            </span>
            <select name="country"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
              v-model="participantData.country_id">
              <option value="" disabled selected>--Select country--</option>
              <option v-for="country in countries" :key="country.id" :value="country.id">
                {{ country.country }}
              </option>
            </select>
          </div>
        </label>
        <label class="flex space-x-2">
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Email address
            </span>
            <input type="email" name="email" v-model="participantData.email"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
              placeholder="you@example.com" />
          </div>
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Phone
            </span>
            <input type="text" name="phone" v-model="participantData.phone"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
              title="Please enter a valid 10-digit phone number" placeholder="Phone number" required />
          </div>
        </label>
        <div class="flex flex-row space-x-4">
          <button type="submit" class="mt-2 px-4 py-2 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
            Add participant
          </button>
          <router-link :to="{ name: 'Participants' }"
            class="mt-2 px-4 py-2 boder border-2 border-abbey-400 hover:border-abbey-200 rounded-2xl">Cancel</router-link>
        </div>
      </form>
    </div>
  </div>
</template>
<script>
import { createItem, fetchData } from "@/services/apiService";
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from "@/components/Spinner.vue";
import router from "@/router";

export default {
  name: "AddParticipantView",
  components: {
    HeaderView, SpinnerComponent
  },
  data() {
    return {
      headerTitle: "Add participant",
      participantData: {
        title: "",
        firstname: "",
        lastname: "",
        institution: "",
        country: "",
        email: "",
        phone: "",
      },
      isLoading: false,
      countries: {},
      currentPage: 1,
      totalPages: "",
      pageSize: 500,
      searchPhrase: ""
    };
  },
  mounted() {
    this.getCountries();
  },
  methods: {
    async addParticipant() {
      this.isLoading = true;
      try {
        const response = await createItem("participants/", this.participantData);
        this.participants = response.data;
        this.isLoading = false;
        router.push("/participants");
      } catch (error) {
        console.error("Error fetching participants:", error);
        this.isLoading = false;
      }
    },
    async getCountries() {
      try {
        const response = await fetchData("countries", 0, this.pageSize, this.searchPhrase);
        this.countries = response.data;
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching countries:", error);
        this.isLoading = false;
      }
    },
  },
};
</script>
