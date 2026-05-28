<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <SpinnerComponent v-if="isLoading" />
    <div v-else class="rounded-2xl bg-catskill-white-100 shadow-sm p-4">
      <form class="flex flex-col w-5/12 space-y-4" @submit.prevent="editOrganiser" method="POST">
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Organiser
          </span>
          <input type="input" name="organiser" v-model="organiserData.organiser"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            placeholder="Organiser" required />
        </label>
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Description
          </span>
          <textarea name="description" v-model="organiserData.description"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            placeholder="Description" required></textarea>
        </label>
        <div class="flex flex-row space-x-4">
          <button type="submit" class="mt-2 px-4 py-2 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
            Edit organiser
          </button>
          <router-link :to="{ name: 'Organisers' }"
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
  name: "EditOrganiserView",
  components: {
    HeaderView, SpinnerComponent
  },
  data() {
    return {
      headerTitle: "Edit organiser",
      id: this.$route.params.id,
      organiserData: {
        organiser: "",
        description: "",
      },
      isLoading: false,
      organiser: {},
    };
  },
  mounted() {
    this.getOrganiser();
  },
  methods: {
    async editOrganiser() {
      this.isLoading = true;
      try {
        const response = await updateItem(
          "organisers",
          this.id,
          this.organiserData
        );
        this.organiser = response.data;
        this.isLoading = false;
        router.push("/organisers");
      } catch (error) {
        console.error("Error adding organiser:", error);
        this.isLoading = false;
      }
    },
    async getOrganiser() {
      try {
        const response = await fetchItem("organisers", this.id);
        console.log(response)
        this.organiserData.organiser = response.organiser.organiser;
        this.organiserData.description = response.organiser.description;
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching organiser:", error);
        this.isLoading = false;
      }
    },
  },
};
</script>
