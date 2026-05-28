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

      <!-- Left: main form -->
      <div class="flex-1 bg-white rounded-2xl shadow-sm p-6">
        <h2 class="text-base font-bold text-gray-700 mb-5">Event Details</h2>
        <form class="flex flex-col space-y-4" @submit.prevent="editEvent">

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Event Title <span class="text-red-500">*</span></label>
            <input type="text" v-model="eventData.event"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Event title" required />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Theme</label>
            <input type="text" v-model="eventData.theme"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Event theme" />
          </div>

          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Organiser <span class="text-red-500">*</span></label>
              <select v-model="eventData.org_unit_id"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
                required>
                <option value="" disabled>-- Select organiser --</option>
                <option v-for="ou in orgUnits" :key="ou.id" :value="ou.id">{{ ou.name }}</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Country <span class="text-red-500">*</span></label>
              <select v-model="eventData.country_id"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
                required>
                <option value="" disabled>-- Select country --</option>
                <option v-for="c in countries" :key="c.id" :value="c.id">{{ c.country }}</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Location <span class="text-red-500">*</span></label>
            <input type="text" v-model="eventData.location"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Venue / city" required />
          </div>

          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Start Date <span class="text-red-500">*</span></label>
              <flat-pickr v-model="eventData.start_date"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
                placeholder="Start date" required />
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">End Date <span class="text-red-500">*</span></label>
              <flat-pickr v-model="eventData.end_date"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
                placeholder="End date" required />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="eventData.description" rows="3"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Event description"></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Organizers Info</label>
            <textarea v-model="eventData.organizers" rows="2"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Names / departments organizing the event"></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Participation Info</label>
            <textarea v-model="eventData.participation_info" rows="2"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Who can participate, fees, etc."></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Logistics Info</label>
            <textarea v-model="eventData.logistics_info" rows="2"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Accommodation, transport, etc."></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sponsors Info</label>
            <textarea v-model="eventData.sponsors_info" rows="2"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400"
              placeholder="Sponsors and partners"></textarea>
          </div>

          <div v-if="errorMsg" class="p-3 rounded-xl text-white text-sm" style="background-color: rgb(239,68,68);">{{ errorMsg }}</div>

          <div class="flex gap-3 pt-2">
            <button type="submit"
              class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90"
              style="background-color: rgb(254,80,103);">
              Save Changes
            </button>
            <router-link :to="{ name: 'Events' }"
              class="px-6 py-2.5 border border-gray-200 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 transition">
              Cancel
            </router-link>
          </div>
        </form>
      </div>

      <!-- Right: Banner panel -->
      <div class="lg:w-80 flex flex-col gap-4">
        <div class="bg-white rounded-2xl shadow-sm p-6">
          <h2 class="text-base font-bold text-gray-700 mb-4">Event Banner</h2>

          <!-- Current banner preview -->
          <div v-if="currentBanner" class="mb-4 rounded-xl overflow-hidden border border-gray-100">
            <img :src="bannerUrl" alt="Event Banner" class="w-full h-44 object-cover" />
          </div>
          <div v-else
            class="mb-4 h-44 rounded-xl border-2 border-dashed border-gray-200 flex flex-col items-center justify-center text-gray-400">
            <svg class="w-10 h-10 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-xs">No banner uploaded</span>
          </div>

          <!-- Upload area -->
          <label class="block cursor-pointer">
            <div class="border-2 border-dashed rounded-xl p-4 text-center transition hover:border-pink-300"
              :class="bannerFile ? 'border-pink-400 bg-pink-50' : 'border-gray-200'">
              <svg class="w-6 h-6 mx-auto mb-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="text-xs text-gray-500" v-if="!bannerFile">Click to select an image</p>
              <p class="text-xs font-semibold truncate" style="color: rgb(254,80,103);" v-else>{{ bannerFile.name }}</p>
            </div>
            <input type="file" accept="image/*" @change="onBannerSelected" ref="bannerInput" class="hidden" />
          </label>

          <button v-if="bannerFile" @click="uploadBanner" :disabled="uploadingBanner" type="button"
            class="mt-3 w-full py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ uploadingBanner ? 'Uploading...' : 'Upload Banner' }}
          </button>
          <button v-if="bannerFile && !uploadingBanner" @click="clearBannerSelection" type="button"
            class="mt-2 w-full py-2 rounded-xl text-xs font-medium text-gray-500 border border-gray-200 hover:bg-gray-50 transition">
            Clear selection
          </button>

          <div v-if="bannerMsg" class="mt-3 p-2.5 rounded-xl text-xs font-semibold text-center text-green-700 bg-green-50">
            {{ bannerMsg }}
          </div>
          <div v-if="bannerError" class="mt-3 p-2.5 rounded-xl text-xs text-center text-red-600 bg-red-50">
            {{ bannerError }}
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { fetchData, updateItem, fetchItem } from "@/services/apiService";
import axios from "axios";
import { useAuthStore } from "@/store/authStore";
import HeaderView from '@/includes/Header.vue';
import SpinnerComponent from "@/components/Spinner.vue";
import router from "@/router";
import flatPickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';

export default {
  name: "EditEventView",
  components: { HeaderView, SpinnerComponent, flatPickr },
  data() {
    return {
      headerTitle: "Edit Event",
      id: this.$route.params.id,
      eventData: {
        event: "",
        theme: "",
        org_unit_id: "",
        country_id: "",
        location: "",
        description: "",
        start_date: "",
        end_date: "",
        organizers: "",
        participation_info: "",
        logistics_info: "",
        sponsors_info: "",
      },
      isLoading: true,
      errorMsg: "",
      countries: [],
      orgUnits: [],
      currentBanner: "",
      bannerFile: null,
      uploadingBanner: false,
      bannerMsg: "",
      bannerError: "",
    };
  },
  mounted() {
    this.loadAll();
  },
  computed: {
    bannerUrl() {
      if (!this.currentBanner) return '';
      const base = import.meta.env.VITE_API_URL || '';
      return base.replace(/\/api\/?$/, '') + '/' + this.currentBanner;
    },
  },
  methods: {
    async loadAll() {
      this.isLoading = true;
      try {
        const [eventRes, countriesRes, orgUnitsRes] = await Promise.all([
          fetchItem("events", this.id),
          fetchData("countries", 0, 500, ""),
          fetchData("org_units", 0, 500, ""),
        ]);
        const e = eventRes.event;
        this.eventData.event = e.event || "";
        this.eventData.theme = e.theme || "";
        this.eventData.org_unit_id = e.org_unit_id || "";
        this.eventData.country_id = e.country_id || "";
        this.eventData.location = e.location || "";
        this.eventData.description = e.description || "";
        this.eventData.start_date = e.start_date || "";
        this.eventData.end_date = e.end_date || "";
        this.eventData.organizers = e.organizers || "";
        this.eventData.participation_info = e.participation_info || "";
        this.eventData.logistics_info = e.logistics_info || "";
        this.eventData.sponsors_info = e.sponsors_info || "";
        this.currentBanner = e.banner_image || "";
        this.countries = countriesRes.data || [];
        this.orgUnits = orgUnitsRes.data || [];
      } catch (error) {
        console.error("Error loading event:", error);
      } finally {
        this.isLoading = false;
      }
    },
    async editEvent() {
      this.isLoading = true;
      this.errorMsg = "";
      try {
        await updateItem("events", this.id, this.eventData);
        this.isLoading = false;
        router.push({ name: "Events" });
      } catch (error) {
        this.errorMsg = error.response?.data?.detail || "Failed to save changes.";
        this.isLoading = false;
      }
    },
    onBannerSelected(e) {
      this.bannerFile = e.target.files[0] || null;
      this.bannerMsg = "";
      this.bannerError = "";
    },
    clearBannerSelection() {
      this.bannerFile = null;
      if (this.$refs.bannerInput) this.$refs.bannerInput.value = "";
      this.bannerMsg = "";
      this.bannerError = "";
    },
    async uploadBanner() {
      if (!this.bannerFile) return;
      this.uploadingBanner = true;
      this.bannerMsg = "";
      this.bannerError = "";
      try {
        const fd = new FormData();
        fd.append("file", this.bannerFile);
        const authStore = useAuthStore();
        const base = import.meta.env.VITE_API_URL;
        const res = await axios.post(`${base}/events/upload_banner/${this.id}`, fd, {
          headers: { Authorization: `Bearer ${authStore.accessToken}` },
        });
        this.currentBanner = res.data.banner_image;
        this.clearBannerSelection();
        this.bannerMsg = "Banner uploaded successfully!";
      } catch (error) {
        this.bannerError = error.response?.data?.detail || "Upload failed.";
      } finally {
        this.uploadingBanner = false;
      }
    },
  },
};
</script>
