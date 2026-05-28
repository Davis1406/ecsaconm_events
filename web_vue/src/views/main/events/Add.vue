<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <SpinnerComponent v-if="isLoading" />
    <div v-else class="rounded-2xl bg-catskill-white-100 shadow-sm p-4">
      <form class="flex flex-col w-7/12 space-y-4" @submit.prevent="addEvent" method="POST">
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Event title
          </span>
          <input type="input" name="event" v-model="eventData.event"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
            placeholder="Event" />
        </label>
        <label class="flex space-x-2">
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Event Type
            </span>
            <select name="event_type"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              v-model="eventData.event_type_id">
              <option value="" disabled selected>--Select event type--</option>
              <option v-for="event_type in eventTypes" :key="event_type.id" :value="event_type.id">
                {{ event_type.event_type }}
              </option>
            </select>
          </div>
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Organiser
            </span>
            <select name="event_type"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              v-model="eventData.organiser_id">
              <option value="" disabled selected>--Select organisers--</option>
              <option v-for="organiser in organisers" :key="organiser.id" :value="organiser.id">
                {{ organiser.organiser }}
              </option>
            </select>
          </div>
        </label>
        <label class="flex space-x-2">
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Capacity
            </span>
            <input type="number" name="capacity" v-model="eventData.capacity"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              placeholder="Capacity" required />
          </div>
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Country
            </span>
            <select name="country"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              v-model="eventData.country_id">
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
              Location
            </span>
            <input type="text" name="location" v-model="eventData.location"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              placeholder="Location" />
          </div>
        </label>
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Description
          </span>
          <textarea name="description" v-model="eventData.description"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
            placeholder="Description"></textarea>
        </label>
        <label class="flex space-x-2">
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Start date
            </span>
            <flat-pickr
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              v-model="eventData.start_date" title="start_date" placeholder="Start_date" required />
          </div>
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              End date
            </span>
            <flat-pickr
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              v-model="eventData.end_date" title="end_date" placeholder="End date" required />
          </div>
        </label>

        <label class="flex space-x-2">
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Registration start date
            </span>
            <flat-pickr name="registration_start_date"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              v-model="eventData.registration_start_date" title="registration_start_date"
              placeholder="Registration start date" required />
          </div>
          <div class="flex-1">
            <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
              Registration end date
            </span>
            <flat-pickr name="registration_end_date"
              class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
              v-model="eventData.registration_end_date" title="registration_end_date"
              placeholder="Registration end date" required />
          </div>
        </label>

        <div class="flex flex-row space-x-4">
          <button type="submit" class="mt-2 px-4 py-2 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
            Add event
          </button>
          <router-link :to="{ name: 'Events' }"
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
import flatPickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';

export default {
  name: "AddEventView",
  components: {
    HeaderView, SpinnerComponent, flatPickr
  },
  data() {
    return {
      headerTitle: "Add event",
      eventData: {
        event: "",
        event_type_id: "",
        country_id: "",
        organiser_id: "",
        location: "",
        capacity: "",
        description: "",
        start_date: "",
        end_date: "",
        registration_start_date: "",
        registration_end_date: "",
      },
      isLoading: false,
      countries: {},
      eventTypes: {},
      organisers: {},
      currentPage: 1,
      totalPages: "",
      pageSize: 1000,
      searchPhrase: "",
      date: null,
    };
  },
  mounted() {
    this.getCountries();
    this.getEventTypes();
    this.getOrganisers();
  },
  methods: {
    async addEvent() {
      this.isLoading = true;
      try {
        const response = await createItem("events/", this.eventData);
        this.events = response.data;
        this.isLoading = false;
        router.push("/events");
      } catch (error) {
        console.error("Error fetching events:", error);
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
    async getEventTypes() {
      try {
        const response = await fetchData("event_types", 0, this.pageSize, this.searchPhrase);
        this.eventTypes = response.data;
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching event types:", error);
        this.isLoading = false;
      }
    },
    async getOrganisers() {
      try {
        const response = await fetchData("organisers", 0, this.pageSize, this.searchPhrase);
        this.organisers = response.data;
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching organisers:", error);
        this.isLoading = false;
      }
    },
  },
};
</script>
